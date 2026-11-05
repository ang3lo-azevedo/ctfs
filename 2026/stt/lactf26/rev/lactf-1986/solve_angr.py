#!/usr/bin/env python3
import angr
import claripy
import archinfo
from pathlib import Path

BIN_PATH = "/home/ang3lo/Documents/ctfs/stt/26/lactf26/rev/lactf-1986/extracted/CHALL.EXE"

# Addresses from disassembly.asm (0x0000 base)
ENTRY_ADDR = 0x00B0
SUCCESS_ADDR = 0x01B0
FAIL_ADDR = 0x01AB

# Internal helper routine addresses to hook (avoid DOS/BIOS dependencies)
NOOP_PRINT_ADDR = 0x01FF
NOOP_SETUP_ADDR = 0x021F
READLINE_ADDR = 0x027E

BUF_MAX = 0x49

def parse_mz_header(path: str) -> tuple[int, int]:
    data = Path(path).read_bytes()
    if data[:2] != b"MZ":
        raise ValueError("Not an MZ executable")

    e_cparhdr = int.from_bytes(data[0x08:0x0A], "little")
    e_ip = int.from_bytes(data[0x14:0x16], "little")
    e_cs = int.from_bytes(data[0x16:0x18], "little")

    header_size = e_cparhdr * 16
    entry = e_cs * 16 + e_ip
    return header_size, entry


def _add16(a, b, carry=0):
    a = claripy.ZeroExt(1, a)
    b = claripy.ZeroExt(1, b)
    c = claripy.ZeroExt(16, carry) if isinstance(carry, claripy.ast.Base) else claripy.BVV(carry, 17)
    s = a + b + c
    res = claripy.Extract(15, 0, s)
    c_out = claripy.Extract(16, 16, s)
    return res, c_out


def _shl1(a):
    carry = claripy.Extract(15, 15, a)
    res = claripy.Extract(15, 0, a << 1)
    return res, carry


def _shr1(a):
    carry = claripy.Extract(0, 0, a)
    res = claripy.LShR(a, 1)
    return res, carry


def _rcl1(a, carry_in):
    carry_in = claripy.ZeroExt(15, carry_in)
    res = claripy.Extract(15, 0, (a << 1) | carry_in)
    carry_out = claripy.Extract(15, 15, a)
    return res, carry_out


def _rcr1(a, carry_in):
    carry_in = claripy.ZeroExt(15, carry_in)
    res = claripy.Extract(15, 0, claripy.LShR(a, 1) | (carry_in << 15))
    carry_out = claripy.Extract(0, 0, a)
    return res, carry_out


def implies(a, b):
    return claripy.Or(claripy.Not(a), b)


def hash_step(accum, si, byte):
    bx = accum
    di = si
    for _ in range(6):
        bx, carry = _shl1(bx)
        di, _ = _rcl1(di, carry)

    ax = accum
    dx = si
    ax, carry = _shl1(ax)
    dx, _ = _rcl1(dx, carry)

    ax, carry = _add16(ax, bx, 0)
    di, _ = _add16(di, dx, carry)

    dx = accum
    dx, carry = _add16(dx, ax, 0)
    di, _ = _add16(di, si, carry)

    ax = claripy.ZeroExt(8, byte)
    dx, carry = _add16(dx, ax, 0)
    accum = dx
    si, _ = _add16(claripy.BVV(0, 16), di, carry)
    si = si & claripy.BVV(0xF, 16)

    return accum, si


def prng_step(ax, dx):
    bx = ax
    si = dx
    for _ in range(3):
        dx, carry = _shr1(dx)
        ax, _ = _rcr1(ax, carry)

    di = ax ^ bx
    di = di & claripy.BVV(1, 16)

    ax = bx
    dx = si
    dx, carry = _shr1(dx)
    ax, _ = _rcr1(ax, carry)

    si = claripy.Extract(15, 0, di << 3)
    dx = dx | si
    dx = dx & claripy.BVV(0xF, 16)

    return ax, dx


def solve_with_claripy(table_bytes):
    solver = claripy.Solver()

    length = claripy.BVS("in_len", 16)
    prefix = b"lactf{"
    solver.add(length >= len(prefix))
    solver.add(length <= (BUF_MAX - 1))

    sym_bytes = [claripy.BVS(f"b{i}", 8) for i in range(BUF_MAX)]

    for i, b in enumerate(sym_bytes):
        solver.add(claripy.Or(b == 0, claripy.And(b >= 0x20, b <= 0x7e)))
        solver.add(implies(length == i, b == 0))
        if i < BUF_MAX - 1:
            solver.add(implies(length > i, b != 0))
            solver.add(implies(length < i, b == 0))

    for i, c in enumerate(prefix):
        solver.add(sym_bytes[i] == c)

    accum = claripy.BVV(0, 16)
    si = claripy.BVV(0, 16)
    for i in range(BUF_MAX):
        byte = sym_bytes[i]
        new_accum, new_si = hash_step(accum, si, byte)
        accum = claripy.If(length > i, new_accum, accum)
        si = claripy.If(length > i, new_si, si)

    ax = accum
    dx = si
    prng_ax = []
    for _ in range(BUF_MAX):
        ax, dx = prng_step(ax, dx)
        prng_ax.append(ax)

    for i in range(BUF_MAX - 1):
        expected = table_bytes[i]
        ax_byte = claripy.Extract(7, 0, prng_ax[i])
        solver.add(implies(length > i, ax_byte ^ sym_bytes[i] == claripy.BVV(expected, 8)))

    if solver.satisfiable():
        model_len = solver.eval(length)
        model_bytes = bytes(solver.eval(b) for b in sym_bytes[:model_len])
        return model_bytes
    return None

class NoOp(angr.SimProcedure):
    def run(self, *args, **kwargs):
        return claripy.BVV(0, self.state.arch.bits)

class ReadLine(angr.SimProcedure):
    def run(self):
        # In this binary, AX holds the buffer pointer. We ignore other args.
        buf_ptr = self.state.regs.ax
        length = claripy.BVS("in_len", 16)

        # Constrain length to [len(prefix), BUF_MAX-1]
        prefix = b"lactf{"
        self.state.solver.add(length >= len(prefix))
        self.state.solver.add(length <= (BUF_MAX - 1))

        # Build symbolic bytes (including terminator slot)
        sym_bytes = [claripy.BVS(f"b{i}", 8) for i in range(BUF_MAX)]

        for i, b in enumerate(sym_bytes):
            # Printable or NUL
            self.state.solver.add(
                claripy.Or(b == 0, claripy.And(b >= 0x20, b <= 0x7e))
            )
            # Enforce null-termination at index `length`
            self.state.solver.add(implies(length == i, b == 0))
            if i < BUF_MAX - 1:
                self.state.solver.add(implies(length > i, b != 0))
                self.state.solver.add(implies(length < i, b == 0))

        # Constrain prefix to "lactf{"
        for i, c in enumerate(prefix):
            self.state.solver.add(sym_bytes[i] == c)

        # Write bytes into buffer
        for i, b in enumerate(sym_bytes):
            self.state.memory.store(buf_ptr + i, b)

        # Keep for extraction in the found state
        self.state.globals["buf_ptr"] = buf_ptr
        self.state.globals["buf_len"] = length

        # Return length in AX
        self.state.regs.ax = length
        return length


def main():
    header_size, mz_entry = parse_mz_header(BIN_PATH)
    entry_addr = ENTRY_ADDR
    print(f"MZ header size: 0x{header_size:x}, entry: 0x{mz_entry:x} (using 0x{entry_addr:x})")

    data = Path(BIN_PATH).read_bytes()
    table_start = header_size + 0x146
    table_bytes = data[table_start:table_start + BUF_MAX]

    try:
        arch = archinfo.arch_from_id("x86_16")
    except Exception:
        arch = archinfo.arch_from_id("x86")

    proj = angr.Project(
        BIN_PATH,
        auto_load_libs=False,
        load_options={
            "main_opts": {
                "backend": "blob",
                "arch": arch,
                "base_addr": 0x0,
                "entry_point": entry_addr,
                "offset": header_size,
            }
        },
    )

    # Hook helper routines to simplify execution
    proj.hook(NOOP_PRINT_ADDR, NoOp())
    proj.hook(NOOP_SETUP_ADDR, NoOp())
    proj.hook(READLINE_ADDR, ReadLine())

    state = proj.factory.blank_state(
        addr=entry_addr,
        add_options={
            angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
            angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
        },
    )

    # Basic register setup for real-mode-like execution
    state.regs.eax = 0
    state.regs.ebx = 0
    state.regs.ecx = 0
    state.regs.edx = 0
    state.regs.esi = 0
    state.regs.edi = 0
    state.regs.ebp = 0
    state.regs.esp = 0x8000

    simgr = proj.factory.simulation_manager(state)
    simgr.stashes.setdefault("found", [])
    simgr.stashes.setdefault("avoid", [])

    step = 0
    max_steps = 20000
    while step < max_steps:
        simgr.step()
        step += 1

        # Move states that hit success/fail to their stashes
        simgr.move(from_stash="active", to_stash="found", filter_func=lambda s: s.addr == SUCCESS_ADDR)
        simgr.move(from_stash="active", to_stash="avoid", filter_func=lambda s: s.addr == FAIL_ADDR)

        if step % 200 == 0:
            cur_addr = simgr.active[0].addr if simgr.active else None
            addr_str = f"0x{cur_addr:x}" if cur_addr is not None else "None"
            print(
                f"step {step}: active={len(simgr.active)} deadended={len(simgr.deadended)} "
                f"avoid={len(simgr.avoid)} found={len(simgr.found)} addr={addr_str}"
            )

        if simgr.found:
            break

        if not simgr.active:
            if simgr.errored:
                err = simgr.errored[0].error
                print(f"Execution error: {err}")
                if "IR decoding error" in str(err):
                    print("Falling back to claripy-only solver...")
                    result = solve_with_claripy(table_bytes)
                    if result:
                        print("candidate:", result)
                    else:
                        print("No solution found in claripy fallback.")
            break

    if simgr.found:
        found = simgr.found[0]
        buf_ptr = found.globals.get("buf_ptr", claripy.BVV(0, 16))
        length = found.globals.get("buf_len", claripy.BVV(0, 16))
        length_val = found.solver.eval(length)
        data = found.solver.eval(found.memory.load(buf_ptr, length_val), cast_to=bytes)
        print("candidate:", data)
    else:
        print("No solution found within step limit.")


if __name__ == "__main__":
    main()
