"""Terminal-only TCP service for the baccarat-like betting challenge."""

from __future__ import annotations

import itertools
import logging
import os
import random
import secrets
import socket
import threading
from dataclasses import dataclass

from game import (
    AgentSpec,
    DuelOutcome,
    Shoe,
    load_banker_agents,
    load_player_agents,
    play_until_resolved,
    seed_for,
)

HOST = "0.0.0.0"
DEFAULT_PORT = 1337
START_BANKROLL = 1000
TARGET_BANKROLL = 100000
ROUNDS_PER_TABLE = 12
CLIENT_TIMEOUT_SECONDS = 180
DEFAULT_FLAG = "flag{development_flag}"
RUNTIME_CHALLENGE_SEED = os.environ.get("CHALLENGE_SEED") or secrets.token_hex(32)

# Tables persist for several resolved bets so the names matter: challengers who
# identify the better side get time to exploit that knowledge before rotation.
TABLE_ROSTER = [
    ("omnicybr", "blackshard", 12),
    ("blackshard", "omnicybr", 12),
    ("northstar", "blackshard", 11),
    ("blackshard", "northstar", 11),
    ("nipcat", "blackshard", 9),
    ("blackshard", "nipcat", 9),
    ("voltaicai", "blackshard", 8),
    ("blackshard", "voltaicai", 8),
    ("omnicybr", "voltaicai", 6),
    ("voltaicai", "omnicybr", 6),
    ("northstar", "voltaicai", 5),
    ("voltaicai", "northstar", 5),
]


class ClientDisconnected(Exception):
    """Raised when a client cleanly disconnects mid-session."""


@dataclass(frozen=True)
class TableTemplate:
    player_module_name: str
    banker_module_name: str
    weight: int


@dataclass
class ActiveTable:
    serial: int
    player_agent: AgentSpec
    banker_agent: AgentSpec
    rounds_remaining: int
    shoe: Shoe
    player_rng: random.Random
    banker_rng: random.Random


@dataclass
class BetResolution:
    chosen_side: str
    amount: int
    winner: str
    tie_replays: int
    duel: DuelOutcome
    bankroll_after: int


class SessionIO:
    """Small ASCII line-oriented wrapper around a connected socket."""

    def __init__(self, conn: socket.socket) -> None:
        self._file = conn.makefile("rwb", buffering=0)

    def send_line(self, message: str = "") -> None:
        data = (message + "\n").encode("ascii", "replace")
        self._file.write(data)

    def read_line(self) -> str:
        raw = self._file.readline()
        if not raw:
            raise ClientDisconnected
        return raw.decode("ascii", "ignore").strip()

    def close(self) -> None:
        self._file.close()


class ChallengeSession:
    def __init__(self, session_serial: int) -> None:
        self._session_serial = session_serial
        self._flag = os.environ.get("FLAG", DEFAULT_FLAG)
        self._challenge_seed = RUNTIME_CHALLENGE_SEED
        self._selection_rng = random.Random(
            seed_for(self._challenge_seed, "selection", session_serial)
        )
        self._players = {agent.module_name: agent for agent in load_player_agents()}
        self._bankers = {agent.module_name: agent for agent in load_banker_agents()}
        self._templates = [TableTemplate(*row) for row in TABLE_ROSTER]
        self._current_table: ActiveTable | None = None
        self._table_serial = 0
        self.bankroll = START_BANKROLL
        self.total_resolved_bets = 0

    def _choose_next_table(self) -> ActiveTable:
        self._table_serial += 1
        weights = [template.weight for template in self._templates]
        template = self._selection_rng.choices(self._templates, weights=weights, k=1)[0]
        player_agent = self._players[template.player_module_name]
        banker_agent = self._bankers[template.banker_module_name]
        seed_prefix = (
            self._challenge_seed,
            "session",
            self._session_serial,
            "table",
            self._table_serial,
            player_agent.module_name,
            banker_agent.module_name,
        )
        return ActiveTable(
            serial=self._table_serial,
            player_agent=player_agent,
            banker_agent=banker_agent,
            rounds_remaining=ROUNDS_PER_TABLE,
            shoe=Shoe(random.Random(seed_for(*seed_prefix, "shoe"))),
            player_rng=random.Random(seed_for(*seed_prefix, "player")),
            banker_rng=random.Random(seed_for(*seed_prefix, "banker")),
        )

    def current_table(self) -> ActiveTable:
        if self._current_table is None or self._current_table.rounds_remaining <= 0:
            self._current_table = self._choose_next_table()
        return self._current_table

    def resolve_bet(self, chosen_side: str, amount: int) -> BetResolution:
        table = self.current_table()
        duel, tie_replays = play_until_resolved(
            table.player_agent,
            table.banker_agent,
            table.shoe,
            table.player_rng,
            table.banker_rng,
        )
        winner = duel.winner
        if winner == chosen_side:
            self.bankroll += amount
        else:
            self.bankroll -= amount

        table.rounds_remaining -= 1
        self.total_resolved_bets += 1
        return BetResolution(
            chosen_side=chosen_side,
            amount=amount,
            winner=winner,
            tie_replays=tie_replays,
            duel=duel,
            bankroll_after=self.bankroll,
        )

    def won(self) -> bool:
        return self.bankroll >= TARGET_BANKROLL

    def lost(self) -> bool:
        return self.bankroll <= 0

    def flag(self) -> str:
        return self._flag


def _normalize_side(raw: str) -> str | None:
    value = raw.strip().lower()
    if value in {"player", "p"}:
        return "player"
    if value in {"banker", "b"}:
        return "banker"
    return None


def _parse_amount(raw: str, bankroll: int) -> int | None:
    value = raw.strip().lower()
    if value in {"all", "max"}:
        return bankroll
    if not value.isdigit():
        return None
    amount = int(value)
    if amount <= 0 or amount > bankroll:
        return None
    return amount


def _prompt_side(io: SessionIO) -> str:
    while True:
        io.send_line("Bet side [player/banker]:")
        raw = io.read_line()
        if raw.lower() == "quit":
            raise ClientDisconnected
        side = _normalize_side(raw)
        if side is not None:
            return side
        io.send_line("Invalid side. Type player or banker.")


def _prompt_amount(io: SessionIO, bankroll: int) -> int:
    while True:
        io.send_line(f"Bet amount [1-{bankroll}] (or 'all'):")
        raw = io.read_line()
        if raw.lower() == "quit":
            raise ClientDisconnected
        amount = _parse_amount(raw, bankroll)
        if amount is not None:
            return amount
        io.send_line("Invalid bet size.")


def _winner_label(winner: str) -> str:
    return "Player" if winner == "player" else "Banker"


def _send_banner(io: SessionIO) -> None:
    io.send_line("Baccarat Duel Betting Challenge")
    io.send_line(f"Starting bankroll :: {START_BANKROLL}")
    io.send_line(f"Target bankroll   :: {TARGET_BANKROLL}")
    io.send_line("Payout            :: even money")
    io.send_line("Tie rule          :: ties are replayed internally until resolved")
    io.send_line(f"Table rule        :: each table persists for {ROUNDS_PER_TABLE} resolved bets")
    io.send_line("Info shown before each bet :: BankerAI name and PlayerAI name")
    io.send_line("Type 'quit' at any prompt to disconnect.")
    io.send_line()


def _send_round_header(io: SessionIO, session: ChallengeSession, table: ActiveTable) -> None:
    round_number = ROUNDS_PER_TABLE - table.rounds_remaining + 1
    io.send_line(
        f"=== Table {table.serial} | Round {round_number}/{ROUNDS_PER_TABLE} | "
        f"Resolved Bets {session.total_resolved_bets + 1} ==="
    )
    io.send_line(f"BankerAI :: {table.banker_agent.display_name}")
    io.send_line(f"PlayerAI :: {table.player_agent.display_name}")
    io.send_line(f"Bankroll :: {session.bankroll}")


def _send_resolution(io: SessionIO, resolution: BetResolution) -> None:
    io.send_line(
        "Result :: "
        f"{_winner_label(resolution.winner)} wins | "
        f"ties replayed={resolution.tie_replays} | "
        f"player={resolution.duel.player_total} banker={resolution.duel.banker_total}"
    )
    io.send_line(f"Bankroll :: {resolution.bankroll_after}")
    io.send_line()


def _run_session(conn: socket.socket, session_serial: int) -> None:
    conn.settimeout(CLIENT_TIMEOUT_SECONDS)
    io = SessionIO(conn)
    session = ChallengeSession(session_serial)
    try:
        _send_banner(io)
        while not session.won() and not session.lost():
            table = session.current_table()
            _send_round_header(io, session, table)
            chosen_side = _prompt_side(io)
            amount = _prompt_amount(io, session.bankroll)
            resolution = session.resolve_bet(chosen_side, amount)
            _send_resolution(io, resolution)

        if session.won():
            io.send_line("Session result :: bankroll target reached")
            io.send_line(f"FLAG :: {session.flag()}")
        else:
            io.send_line("Session result :: bankroll depleted")
            io.send_line("Better luck next time.")
    finally:
        io.close()


def _handle_client(conn: socket.socket, addr: tuple[str, int], session_serial: int) -> None:
    with conn:
        try:
            _run_session(conn, session_serial)
        except ClientDisconnected:
            logging.info("session %d disconnected", session_serial)
        except (TimeoutError, socket.timeout):
            logging.info("session %d timed out", session_serial)
        except Exception:
            logging.exception("session %d crashed", session_serial)


def serve_forever() -> None:
    port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    session_counter = itertools.count(1)
    session_counter_lock = threading.Lock()
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, port))
        server_sock.listen(16)
        logging.info("listening on %s:%d", HOST, port)

        while True:
            conn, addr = server_sock.accept()
            with session_counter_lock:
                session_serial = next(session_counter)
            logging.info("accepted connection from %s:%d as session %d", *addr, session_serial)
            thread = threading.Thread(
                target=_handle_client,
                args=(conn, addr, session_serial),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    serve_forever()
