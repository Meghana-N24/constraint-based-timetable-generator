import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.io.input_parser import InputParser

parser = InputParser()
ok = parser.load_from_file("data/samples/university_sample.json")

if ok:
    print()
    print("--- First 5 sessions (sorted by priority) ---")
    for s in parser.sessions[:5]:
        print(f"  {s.id:12} | {s.course.name:25} | "
              f"priority={s.course.priority} | "
              f"teacher={s.teacher.name}")