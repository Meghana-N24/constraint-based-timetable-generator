# Constraint-Based Timetable Generator

A university scheduling system that automatically generates
conflict-free timetables using Constraint Satisfaction Problem
(CSP) algorithms — backtracking, MRV heuristic, and least
constraining value ordering.

---

## Features

- No clashes — teachers, rooms, student groups
- Teacher availability constraints
- Room capacity and type matching (lab vs classroom)
- Priority-based scheduling (critical courses scheduled first)
- MRV heuristic for fast solving
- Interactive CLI + JSON file input
- Export to CSV, JSON, TXT
- Full validation report after solving
- 9-test automated test suite

---

## Project Structure
timetable-generator/
├── src/
│   ├── models/          # Core data classes
│   │   ├── timeslot.py
│   │   ├── room.py
│   │   ├── teacher.py
│   │   ├── course.py
│   │   └── session.py   # CSP variables
│   ├── algorithms/
│   │   └── backtracking.py  # CSP solver + MRV
│   ├── constraints/
│   │   └── constraint_checker.py
│   ├── io/
│   │   ├── input_parser.py  # JSON loader
│   │   └── exporter.py      # CSV/JSON/TXT output
│   ├── cli/
│   │   └── interactive.py   # Interactive input
│   └── utils/
│       ├── display.py       # Terminal tables
│       └── validator.py     # Solution verifier
├── tests/
│   └── unit/
│       ├── test_constraints.py
│       └── test_performance.py
├── data/
│   └── samples/
│       └── university_sample.json
├── output/              # Generated timetables
├── main.py              # Entry point
└── requirements.txt
---

## How It Works — The Algorithm

### Problem Modelling (CSP)

| CSP Concept | Timetable Meaning |
|-------------|-------------------|
| Variable | Each session to schedule (e.g. CS301-1) |
| Domain | All valid (timeslot, room) pairs |
| Constraint | No teacher/room/group clash |

### Algorithm: Backtracking + MRV
1.Sort sessions by priority (critical first)
2.Pick unassigned session with fewest valid options (MRV)
3.Try each (timeslot, room) pair:
-Check all 7 hard constraints in O(1)
-If valid → assign and recurse
-If no solution found → unassign and backtrack
4.Repeat until all sessions assigned
### Hard Constraints (never violated)

1. Teacher cannot teach two sessions at the same time
2. Room cannot host two sessions at the same time
3. Student group cannot have two classes at the same time
4. Teacher must be available at that timeslot
5. Room capacity must fit number of students
6. Lab courses must be assigned to lab rooms
7. Teacher daily workload limit respected

---

## Quick Start (Ubuntu)

### 1. Clone and setup

```bash
git clone https://github.com/YOUR_USERNAME/timetable-generator.git
cd timetable-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
