from rich.console import Console
from rich.table import Table

console = Console()


def print_analysis(solver):
    routes = solver.decode() or []

    console.rule("[bold]Solution[/bold]")
    _print_routes(routes)
    _print_usage(solver, routes)
    _print_skipped_jobs(solver, routes)
    console.rule("")


def _print_routes(routes):
    table = Table(title="Routes")
    table.add_column("Vehicle")
    table.add_column("Type")
    table.add_column("Route")
    table.add_column("Cost", justify="right")

    for r in routes:
        table.add_row(
            r["vehicle_id"],
            r["vehicle_type"],
            " → ".join(r["route"]),
            str(r["total_cost"]),
        )

    console.print(table)


def _print_usage(solver, routes):
    table = Table(title="Vehicle Usage")
    table.add_column("Vehicle")
    table.add_column("Type")
    table.add_column("Range Used")
    table.add_column("Payload")

    for i, r in enumerate(routes):
        v = solver.vehicles[i]

        payload_used = sum(
            loc.get("demand", 0)
            for loc in solver.locations
            if loc["id"] in r["route"]
        )

        range_pct = (
            r["total_cost"] / v["range_left"] * 100
            if v["range_left"] else 0
        )

        table.add_row(
            v["id"],
            v["type"],
            f"{range_pct:.1f}%",
            f"{payload_used} / {v['payload_left']}",
        )

    console.print(table)


def _print_skipped_jobs(solver, routes):
    visited = {node for r in routes for node in r["route"]}

    skipped = [
        loc for loc in solver.locations
        if loc["type"] == "job" and loc["id"] not in visited
    ]

    if not skipped:
        console.print("[green]All jobs served[/green]")
        return

    table = Table(title="Skipped Jobs")
    table.add_column("Job")
    table.add_column("Priority")
    table.add_column("Penalty")

    for j in skipped:
        table.add_row(
            j["id"],
            str(j.get("priority", "-")),
            str(j.get("penalty", "-")),
        )

    console.print(table)