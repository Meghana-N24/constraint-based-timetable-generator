import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.io.input_parser import InputParser
from src.algorithms.backtracking import BacktrackingSolver
from src.utils.display import TimetableDisplay
from src.io.exporter import TimetableExporter
from src.utils.validator import TimetableValidator

# Load
parser = InputParser()
ok = parser.load_from_file("data/samples/university_sample.json")
if not ok:
    exit(1)

# Solve
solver = BacktrackingSolver(
    sessions=parser.sessions,
    timeslots=parser.timeslots,
    rooms=parser.rooms,
    use_mrv=True,
)

print("\n🔍 Solving timetable...")
solved = solver.solve()

if solved:
    print("✅ Solution FOUND!")
    solver.print_stats()

    # Display
    display = TimetableDisplay()
    display.print_full(parser.sessions, parser.university_name)
    display.print_by_teacher(parser.sessions)
    display.print_by_room(parser.sessions)

    # Export
    print(f"\n📤 Exporting...")
    exporter = TimetableExporter(output_dir="output")
    exporter.export_csv(parser.sessions)
    exporter.export_json(parser.sessions)
    exporter.export_text(parser.sessions, parser.university_name)

    # Validate
    print(f"\n🔎 Validating solution...")
    validator = TimetableValidator()
    is_valid = validator.validate(parser.sessions)
    validator.print_report()

    print("\n✅ All done! Check the output/ folder.")

else:
    print("❌ No solution found!")
    solver.print_stats()