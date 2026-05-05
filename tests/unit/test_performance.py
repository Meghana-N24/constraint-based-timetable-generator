import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.io.input_parser import InputParser
from src.algorithms.backtracking import BacktrackingSolver


def benchmark(use_mrv: bool, label: str) -> dict:
    parser = InputParser()
    parser.load_from_file("data/samples/university_sample.json")

    solver = BacktrackingSolver(
        sessions=parser.sessions,
        timeslots=parser.timeslots,
        rooms=parser.rooms,
        use_mrv=use_mrv,
    )

    start = time.time()
    solved = solver.solve()
    elapsed = time.time() - start

    return {
        "label": label,
        "solved": solved,
        "nodes": solver.nodes_explored,
        "backtracks": solver.backtracks,
        "time": solver.solve_time,
    }


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  PERFORMANCE BENCHMARK")
    print(f"  Backtracking WITH MRV  vs  WITHOUT MRV")
    print(f"{'='*60}\n")

    # Suppress parser output
    import io
    import contextlib

    results = []
    for use_mrv, label in [(True, "WITH MRV"), (False, "WITHOUT MRV")]:
        print(f"  Running {label}...", end=" ", flush=True)
        with contextlib.redirect_stdout(io.StringIO()):
            r = benchmark(use_mrv, label)
        print("done")
        results.append(r)

    print(f"\n  {'Metric':<25} {'WITH MRV':>15} {'WITHOUT MRV':>15}")
    print(f"  {'-'*55}")

    metrics = [
        ("Solved", "solved"),
        ("Nodes explored", "nodes"),
        ("Backtracks", "backtracks"),
        ("Time (seconds)", "time"),
    ]

    for metric_name, key in metrics:
        a = results[0][key]
        b = results[1][key]
        if key == "time":
            a_str = f"{a:.4f}s"
            b_str = f"{b:.4f}s"
        else:
            a_str = str(a)
            b_str = str(b)
        print(f"  {metric_name:<25} {a_str:>15} {b_str:>15}")

    print(f"\n  {'='*55}")
    if results[0]["nodes"] < results[1]["nodes"]:
        reduction = (1 - results[0]["nodes"] / max(results[1]["nodes"], 1)) * 100
        print(f"  MRV reduced nodes explored by {reduction:.1f}%")
    if results[0]["time"] < results[1]["time"]:
        speedup = results[1]["time"] / max(results[0]["time"], 0.0001)
        print(f"  MRV was {speedup:.1f}x faster")
    print()