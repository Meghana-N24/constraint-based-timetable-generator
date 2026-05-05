import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.io.input_parser import InputParser
from src.io.exporter import TimetableExporter
from src.algorithms.backtracking import BacktrackingSolver
from src.utils.display import TimetableDisplay
from src.cli.interactive import InteractiveCLI
from src.models.timeslot import generate_timeslots


def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║       CONSTRAINT-BASED TIMETABLE GENERATOR          ║
║       University Scheduling System                  ║
╚══════════════════════════════════════════════════════╝
    """)


def choose_input_mode() -> str:
    print("  How would you like to provide data?\n")
    print("    [1] Load from JSON file  (recommended for large data)")
    print("    [2] Enter data interactively  (quick setup)")
    print("    [3] Exit\n")
    while True:
        choice = input("  Choice: ").strip()
        if choice in ("1", "2", "3"):
            return choice
        print("  ⚠️  Enter 1, 2, or 3.")


def run_solver(sessions, timeslots, rooms, university_name):
    print("\n  ⚙️  Choose solver mode:\n")
    print("    [1] Backtracking + MRV heuristic  (fast, recommended)")
    print("    [2] Backtracking only  (slower, for comparison)\n")
    mode = input("  Choice [1]: ").strip() or "1"
    use_mrv = (mode != "2")

    solver = BacktrackingSolver(
        sessions=sessions,
        timeslots=timeslots,
        rooms=rooms,
        use_mrv=use_mrv,
    )

    print(f"\n  🔍 Solving timetable for {university_name}...")
    print(f"     Sessions to schedule: {len(sessions)}")
    solved = solver.solve()

    if solved:
        print("  ✅ Solution FOUND!\n")
        solver.print_stats()

        display = TimetableDisplay()

        print("\n  📋 Choose display view:\n")
        print("    [1] By day (full timetable)")
        print("    [2] By teacher")
        print("    [3] By room")
        print("    [4] All views\n")
        view = input("  Choice [1]: ").strip() or "1"

        if view == "1":
            display.print_full(sessions, university_name)
        elif view == "2":
            display.print_by_teacher(sessions)
        elif view == "3":
            display.print_by_room(sessions)
        else:
            display.print_full(sessions, university_name)
            display.print_by_teacher(sessions)
            display.print_by_room(sessions)

        # Export
        print("\n  💾 Export timetable?\n")
        print("    [1] CSV + JSON + TXT  (all formats)")
        print("    [2] CSV only")
        print("    [3] JSON only")
        print("    [4] Skip export\n")
        exp = input("  Choice [1]: ").strip() or "1"

        if exp != "4":
            exporter = TimetableExporter(output_dir="output")
            print()
            if exp in ("1", "2"):
                exporter.export_csv(sessions)
            if exp in ("1", "3"):
                exporter.export_json(sessions)
            if exp == "1":
                exporter.export_text(sessions, university_name)
            print("\n  ✅ Export complete. Check the output/ folder.")

    else:
        print("  ❌ No solution found!")
        print("  Suggestions:")
        print("    - Add more rooms")
        print("    - Add more time periods")
        print("    - Reduce sessions per week")
        print("    - Check teacher availability constraints")
        solver.print_stats()


def main():
    print_banner()
    choice = choose_input_mode()

    if choice == "3":
        print("\n  Goodbye!\n")
        return

    if choice == "1":
        # JSON file mode
        filepath = input("\n  Enter path to JSON file "
                         "[data/samples/university_sample.json]: ").strip()
        if not filepath:
            filepath = "data/samples/university_sample.json"

        parser = InputParser()
        ok = parser.load_from_file(filepath)
        if not ok:
            print("  ❌ Failed to load file. Exiting.")
            return

        run_solver(
            sessions=parser.sessions,
            timeslots=parser.timeslots,
            rooms=parser.rooms,
            university_name=parser.university_name,
        )

    elif choice == "2":
        # Interactive mode
        cli = InteractiveCLI()
        ready = cli.run()

        if not ready:
            print("\n  Cancelled. Goodbye!\n")
            return

        timeslots = generate_timeslots(
            days=cli.days,
            periods_per_day=cli.periods_per_day,
            start_hour=cli.start_hour,
            period_duration_mins=cli.period_duration,
        )

        run_solver(
            sessions=cli.sessions,
            timeslots=timeslots,
            rooms=cli.rooms,
            university_name=cli.university_name,
        )


if __name__ == "__main__":
    main()