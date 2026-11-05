import base64
import binascii
import os
import queue
import signal
import sys
import threading
import time
from dataclasses import dataclass

from frida_tools.application import Reactor

import frida
from pwnlib.tubes.tube import tube
from pwnlib.elf import ELF

PATH = os.getenv("TARGET_APP", default="app")
NAME = os.path.basename(PATH)


@dataclass
class Hook:
    address: int
    script: frida.core.Script


class Application:
    def __init__(self):
        self._reactor = Reactor(run_until_return=self._process_input)

        self._device = frida.get_device_manager().add_remote_device("127.0.0.1:27042")
        self._session = None
        self._paused = False

        self._elf = ELF(PATH)
        self._relevant_functions = {
            function.address: name for name, function in self._elf.functions.items()
        }

        self._process = self._elf.process(env={"LD_PRELOAD": "./libs/libgadget.so"})

        self._scripts: list[Hook] = []

    def run(self):
        if any(proc.name == NAME for proc in self._device.enumerate_processes()):
            self._session = self._device.attach(NAME)
        else:
            self._device.on(
                "spawn-added",
                lambda spawn: self._reactor.schedule(self._on_spawn(spawn)),
            )
            self._device.enable_spawn_gating()
            self._paused = True

        self._reactor.run()

    def _on_spawn(self, spawn: frida.core.Spawn):
        if spawn.identifier.endswith(NAME):
            self._session = self._device.attach(spawn.pid)

    def list_functions(self):
        print("[INFO] Functions:")
        for address, name in sorted(self._relevant_functions.items()):
            print(f"{hex(address)}: {name}")

    def _build_script(self, address: int):
        return f"""\
const offset = {hex(address)};

const mod = Process.getModuleByName('{NAME}');
const target = mod.base.add(offset);

Interceptor.attach(target, {{
    onEnter: function (args) {{
        console.log("Called function {hex(address)}");
    }}
}});
console.log("Attached hook to {hex(address)}");
    """

    def _print_help(self):
        print("[INFO] Usage:")
        print("help          - print this help message")
        print("resume        - resume paused target process (only once, upon startup)")
        print("send <msg>    - send message line to target process")
        print("sendb64 <msg> - decode base64 input and send message to target process")
        print("listing       - list relevant functions")
        print("add <addr>    - add function hook at given address")
        print("del           - delete hook from list")
        print("debug         - print debug information")
        print("exit          - terminate this process")

    def _process_input(self, reactor):
        if self._session is None:
            print("[INFO] Starting target process...")
            while self._session is None:
                time.sleep(0.1)

            print(
                "[INFO] Attached to target and paused execution during startup. "
                "Configure your hooks and start the process with `resume` once you are ready. "
                "Please use the `send`/`sendb64`-commands to interact with the process "
                "and refer to `help` for documentation of the inspector CLI."
            )

        self.list_functions()

        prompt = "> "

        def output(proc: tube, stopped: threading.Event):
            try:
                while not stopped.is_set():
                    process_data = proc.recv(timeout=0.1)
                    if len(process_data) > 0:
                        print(f"\n[TARGET] Received {hex(len(process_data))} bytes:")
                        sys.stdout.buffer.write(process_data)
                        print(prompt, end="")
                        sys.stdout.flush()
            except EOFError:
                os.kill(os.getpid(), signal.SIGINT)
                return

        stop_event = threading.Event()
        output_thread = threading.Thread(
            target=output,
            args=(
                self._process,
                stop_event,
            ),
        )
        output_thread.start()

        while True:
            try:
                command = input(prompt).strip()
            except KeyboardInterrupt:
                print()
                if not output_thread.is_alive():
                    print("[TARGET] Received EOF")
                self._reactor.cancel_io()
                break

            if len(command) == 0:
                continue
            match command:
                case "help":
                    self._print_help()
                case "resume":
                    if not self._paused:
                        print("[ERROR] Target process is already running")
                        continue

                    self._device.disable_spawn_gating()
                    self._paused = False
                case c if c.startswith("send ") or c.startswith("sendb64 "):
                    if command.startswith("send "):
                        msg = (command.removeprefix("send ") + "\n").encode()
                    elif command.startswith("sendb64 "):
                        try:
                            msg = base64.b64decode(command.removeprefix("sendb64 "))
                        except (ValueError, binascii.Error):
                            print("[ERROR] Invalid base64 input")
                            continue

                    self._process.send(msg)
                case "listing":
                    self.list_functions()
                case c if c.startswith("add "):
                    address = int(command.removeprefix("add "), base=0)

                    errors = queue.Queue()
                    init_event = threading.Event()

                    def msg_callback(msg: dict, data, init: threading.Event):
                        if "type" in msg and msg["type"] == "error":
                            if msg["description"].startswith("Error: access violation"):
                                errors.put("Access violation")
                            else:
                                errors.put("Unable to intercept function")
                            init.set()

                    def log_handler(level: str, msg: str, init: threading.Event):
                        if not msg.startswith("Attached"):
                            print()
                        print(f"[{level.upper()}] {msg}")
                        if not msg.startswith("Attached"):
                            print(prompt, end="")
                        sys.stdout.flush()
                        init.set()

                    script = self._session.create_script(self._build_script(address))
                    script.on(
                        "message", lambda msg, data: msg_callback(msg, data, init_event)
                    )
                    script.set_log_handler(
                        lambda level, msg: log_handler(level, msg, init_event)
                    )

                    assert not init_event.is_set()
                    script.load()
                    if not init_event.wait(0.5):
                        print("[ERROR] Timeout reached, could not add hook")
                        script.unload()
                        continue

                    if not errors.empty():
                        print(f"[ERROR] {errors.get()}, could not add hook")
                        script.unload()
                        continue

                    self._scripts.append(Hook(address, script))
                case "del":
                    if len(self._scripts) == 0:
                        print("[INFO] No hooks available, see `add`")
                        continue

                    for idx, script in enumerate(self._scripts):
                        print(f"{idx + 1}. {hex(script.address)}")

                    try:
                        choice = int(input("Delete hook: "), base=0)
                        choice -= 1
                    except ValueError:
                        choice = None

                    if choice is None or not (0 <= choice < len(self._scripts)):
                        print("[ERROR] Invalid choice")
                        continue

                    script: Hook = self._scripts.pop(choice)
                    script.script.unload()
                case "debug":
                    print("Processes:", self._device.enumerate_processes())
                case (
                    "exit"
                    | "stop"
                    | "terminate"
                    | "done"
                    | "cheerio"
                    | "fuck"
                    | "tschüss"
                ):
                    break
                case _:
                    self._print_help()

        print("[INFO] Terminating...")
        stop_event.set()
        output_thread.join()


if __name__ == "__main__":
    app = Application()
    app.run()
