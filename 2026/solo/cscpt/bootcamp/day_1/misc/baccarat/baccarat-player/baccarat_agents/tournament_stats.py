"""Tournament runner for baccarat-like duel agents."""

from __future__ import annotations

from dataclasses import dataclass

from game import (
    AgentSpec,
    PairingStats,
    load_banker_agents,
    load_player_agents,
    simulate_pairing,
)

BASE_SEED = 20250311
RESOLVED_ROUNDS_PER_PAIRING = 10000


@dataclass
class AggregateStats:
    name: str
    wins: int = 0
    losses: int = 0
    ties: int = 0

    @property
    def resolved_rounds(self) -> int:
        return self.wins + self.losses

    @property
    def winrate(self) -> float:
        return self.wins / self.resolved_rounds if self.resolved_rounds else 0.0


def _run_pairing(player_agent: AgentSpec, banker_agent: AgentSpec) -> PairingStats:
    return simulate_pairing(
        player_agent,
        banker_agent,
        RESOLVED_ROUNDS_PER_PAIRING,
        BASE_SEED,
        "tournament",
    )


def _collect_tournament_stats(
    players: list[AgentSpec], bankers: list[AgentSpec]
) -> list[PairingStats]:
    results: list[PairingStats] = []
    for player_agent in players:
        for banker_agent in bankers:
            results.append(_run_pairing(player_agent, banker_agent))
    return results


def _build_aggregate_stats(
    pairings: list[PairingStats],
    players: list[AgentSpec],
    bankers: list[AgentSpec],
) -> tuple[list[AggregateStats], list[AggregateStats]]:
    player_totals = {agent.display_name: AggregateStats(agent.display_name) for agent in players}
    banker_totals = {agent.display_name: AggregateStats(agent.display_name) for agent in bankers}

    for pairing in pairings:
        player_record = player_totals[pairing.player.display_name]
        player_record.wins += pairing.player_wins
        player_record.losses += pairing.banker_wins
        player_record.ties += pairing.ties

        banker_record = banker_totals[pairing.banker.display_name]
        banker_record.wins += pairing.banker_wins
        banker_record.losses += pairing.player_wins
        banker_record.ties += pairing.ties

    ranked_players = sorted(
        player_totals.values(),
        key=lambda row: (-row.winrate, -row.wins, row.losses, row.name),
    )
    ranked_bankers = sorted(
        banker_totals.values(),
        key=lambda row: (-row.winrate, -row.wins, row.losses, row.name),
    )
    return ranked_players, ranked_bankers


def _print_pairing_results(pairings: list[PairingStats]) -> None:
    print("Pairing Results")
    print(
        f"{'Player':<12} {'Banker':<12} {'P Wins':>7} {'B Wins':>7} {'Ties':>7} "
        f"{'P Win%':>8} {'B Win%':>8}"
    )
    print("-" * 72)
    for pairing in pairings:
        print(
            f"{pairing.player.display_name:<12} {pairing.banker.display_name:<12} "
            f"{pairing.player_wins:>7} {pairing.banker_wins:>7} {pairing.ties:>7} "
            f"{pairing.player_resolved_winrate:>7.1%} {pairing.banker_resolved_winrate:>7.1%}"
        )
    print()


def _print_matrix(pairings: list[PairingStats], players: list[AgentSpec], bankers: list[AgentSpec]) -> None:
    matrix = {
        (pairing.player.display_name, pairing.banker.display_name): pairing
        for pairing in pairings
    }

    print("Player Resolved Winrate Matrix")
    row_label = "Player/Banker"
    header = f"{row_label:<14}" + "".join(
        f"{banker.display_name:>12}" for banker in bankers
    ) + f"{'Avg':>12}"
    print(header)
    print("-" * len(header))

    for player in players:
        row_values = []
        for banker in bankers:
            pairing = matrix[(player.display_name, banker.display_name)]
            row_values.append(pairing.player_resolved_winrate)
        average = sum(row_values) / len(row_values)
        print(
            f"{player.display_name:<14}"
            + "".join(f"{value:>11.1%} " for value in row_values)
            + f"{average:>11.1%} "
        )
    print()


def _print_aggregate_standings(
    title: str,
    standings: list[AggregateStats],
) -> None:
    print(title)
    print(
        f"{'Rank':<5} {'Name':<12} {'Wins':>7} {'Losses':>7} {'Ties':>7} {'Win%':>8}"
    )
    print("-" * 52)
    for index, record in enumerate(standings, start=1):
        print(
            f"{index:<5} {record.name:<12} {record.wins:>7} {record.losses:>7} "
            f"{record.ties:>7} {record.winrate:>7.1%}"
        )
    print()


def main() -> None:
    players = load_player_agents()
    bankers = load_banker_agents()
    if not players:
        raise RuntimeError("No player agents found in agents/players")
    if not bankers:
        raise RuntimeError("No banker agents found in agents/bankers")

    print("Baccarat Duel Tournament")
    print(f"Resolved rounds per pairing: {RESOLVED_ROUNDS_PER_PAIRING}")
    print(f"Base seed: {BASE_SEED}")
    print("Loaded players:", ", ".join(agent.display_name for agent in players))
    print("Loaded bankers:", ", ".join(agent.display_name for agent in bankers))
    print()

    pairings = _collect_tournament_stats(players, bankers)
    ranked_players, ranked_bankers = _build_aggregate_stats(pairings, players, bankers)

    _print_pairing_results(pairings)
    _print_matrix(pairings, players, bankers)
    _print_aggregate_standings("Best Players Overall", ranked_players)
    _print_aggregate_standings("Best Bankers Overall", ranked_bankers)


if __name__ == "__main__":
    main()
