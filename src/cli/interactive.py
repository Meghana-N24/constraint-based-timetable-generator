from typing import List, Dict, Optional
from src.models.timeslot import DAYS
from src.models.room import Room, RoomType
from src.models.teacher import Teacher
from src.models.course import Course
from src.models.session import Session


def clear_line():
    print()


def print_header(title: str):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


def ask(prompt: str, default: str = "") -> str:
    """Ask user for input. If they press Enter, use default."""
    if default:
        result = input(f"  {prompt} [{default}]: ").strip()
        return result if result else default
    result = input(f"  {prompt}: ").strip()
    return result


def ask_int(prompt: str, default: int = 1, min_val: int = 1) -> int:
    """Ask for an integer with validation."""
    while True:
        raw = ask(prompt, str(default))
        try:
            val = int(raw)
            if val < min_val:
                print(f"  ⚠️  Must be at least {min_val}. Try again.")
                continue
            return val
        except ValueError:
            print(f"  ⚠️  Please enter a whole number.")


def ask_bool(prompt: str, default: bool = False) -> bool:
    """Ask yes/no question."""
    default_str = "y" if default else "n"
    raw = ask(f"{prompt} (y/n)", default_str).lower()
    return raw in ("y", "yes", "1", "true")


def ask_choice(prompt: str, choices: List[str]) -> str:
    """Show numbered menu, return chosen value."""
    print(f"\n  {prompt}")
    for i, c in enumerate(choices, 1):
        print(f"    [{i}] {c}")
    while True:
        raw = input("  Choice: ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
            print(f"  ⚠️  Enter a number between 1 and {len(choices)}")
        except ValueError:
            print("  ⚠️  Please enter a number.")


class InteractiveCLI:
    """
    Guides the user through entering all university data
    interactively in the terminal.
    """

    def __init__(self):
        self.university_name = ""
        self.days: List[str] = []
        self.periods_per_day: int = 8
        self.start_hour: int = 8
        self.period_duration: int = 60
        self.rooms: Dict[str, Room] = {}
        self.teachers: Dict[str, Teacher] = {}
        self.courses: Dict[str, Course] = {}
        self.sessions: List[Session] = []

    def run(self) -> bool:
        """
        Full interactive session.
        Returns True if data collected successfully.
        """
        print_header("TIMETABLE GENERATOR — Interactive Setup")

        self._collect_university_info()
        self._collect_rooms()
        self._collect_teachers()
        self._collect_courses()
        self._build_sessions()
        self._show_summary()

        print("\n  Proceed to solve timetable with this data?")
        return ask_bool("Continue?", default=True)

    # ── University ───────────────────────────────────────────────

    def _collect_university_info(self):
        print_header("Step 1 of 4 — University Info")

        self.university_name = ask("University name", "My University")

        print("\n  Which days does the university run?")
        print("  (Press Enter to use Mon–Fri, or type custom e.g. Mon,Tue,Wed)")
        raw = ask("Days", "Monday,Tuesday,Wednesday,Thursday,Friday")
        self.days = [d.strip() for d in raw.split(",")]

        self.periods_per_day = ask_int("Periods per day", default=8, min_val=1)
        self.start_hour = ask_int("Start hour (24h, e.g. 8 = 8am)", default=8)
        self.period_duration = ask_int("Period duration (minutes)", default=60)

        total = len(self.days) * self.periods_per_day
        print(f"\n  ✅ {total} total timeslots per week "
              f"({len(self.days)} days × {self.periods_per_day} periods)")

    # ── Rooms ────────────────────────────────────────────────────

    def _collect_rooms(self):
        print_header("Step 2 of 4 — Rooms")
        print("  Add all rooms available for scheduling.")
        print("  (Press Enter after each room. Type 'done' when finished.)\n")

        room_counter = 1
        while True:
            print(f"  --- Room #{room_counter} ---")
            room_id = ask("Room ID (e.g. R101, LAB1)", f"R{room_counter:03d}")

            if room_id.lower() == "done":
                if not self.rooms:
                    print("  ⚠️  You need at least one room!")
                    continue
                break

            if room_id in self.rooms:
                print(f"  ⚠️  Room ID '{room_id}' already exists. Use a different ID.")
                continue

            name = ask("Room name", f"Room {room_id}")
            capacity = ask_int("Capacity (max students)", default=40, min_val=1)

            room_type_str = ask_choice(
                "Room type:",
                ["classroom", "lab", "auditorium", "seminar"]
            )

            has_lab = room_type_str == "lab"
            if not has_lab:
                has_lab = ask_bool("Has lab equipment?", default=False)

            has_proj = ask_bool("Has projector?", default=True)
            building = ask("Building name", "Main")

            room = Room(
                id=room_id,
                name=name,
                capacity=capacity,
                room_type=room_type_str,
                building=building,
                has_projector=has_proj,
                has_lab_equipment=has_lab,
            )
            self.rooms[room_id] = room
            print(f"  ✅ Added: {room}")

            another = ask_bool(f"\n  Add another room?", default=True)
            if not another:
                break
            room_counter += 1

        print(f"\n  ✅ {len(self.rooms)} room(s) added.")

    # ── Teachers ─────────────────────────────────────────────────

    def _collect_teachers(self):
        print_header("Step 3 of 4 — Teachers")
        print("  Add all teachers.\n")

        teacher_counter = 1
        while True:
            print(f"  --- Teacher #{teacher_counter} ---")
            tid = ask("Teacher ID (e.g. T001)", f"T{teacher_counter:03d}")

            if tid.lower() == "done":
                if not self.teachers:
                    print("  ⚠️  You need at least one teacher!")
                    continue
                break

            if tid in self.teachers:
                print(f"  ⚠️  ID '{tid}' already exists.")
                continue

            name = ask("Full name", f"Teacher {teacher_counter}")
            dept = ask("Department", "General")

            raw_subjects = ask(
                "Subjects they can teach (comma separated)",
                "General Studies"
            )
            subjects = [s.strip() for s in raw_subjects.split(",")]

            max_day = ask_int("Max periods per day", default=4, min_val=1)
            max_week = ask_int("Max periods per week", default=20, min_val=1)

            # Unavailable slots
            unavailable = []
            if ask_bool("Add unavailable slots?", default=False):
                print("  Enter unavailable slots (e.g. Monday 3).")
                print("  Type 'done' when finished.")
                while True:
                    raw = ask("Day and period (e.g. Monday 3)", "done")
                    if raw.lower() == "done":
                        break
                    parts = raw.strip().split()
                    if len(parts) == 2:
                        try:
                            day_input = parts[0].capitalize()
                            period_input = int(parts[1])
                            if day_input in self.days:
                                unavailable.append((day_input, period_input))
                                print(f"    ✅ Marked unavailable: {day_input} P{period_input}")
                            else:
                                print(f"    ⚠️  '{day_input}' not in your days list.")
                        except ValueError:
                            print("    ⚠️  Format: DayName PeriodNumber (e.g. Monday 3)")
                    else:
                        print("    ⚠️  Format: DayName PeriodNumber (e.g. Monday 3)")

            teacher = Teacher(
                id=tid,
                name=name,
                department=dept,
                subjects=subjects,
                unavailable_slots=unavailable,
                max_periods_per_day=max_day,
                max_periods_per_week=max_week,
            )
            self.teachers[tid] = teacher
            print(f"  ✅ Added: {teacher}")

            another = ask_bool("\n  Add another teacher?", default=True)
            if not another:
                break
            teacher_counter += 1

        print(f"\n  ✅ {len(self.teachers)} teacher(s) added.")

    # ── Courses ──────────────────────────────────────────────────

    def _collect_courses(self):
        print_header("Step 4 of 4 — Courses")
        print("  Add all courses to schedule.\n")

        teacher_list = list(self.teachers.keys())
        teacher_display = [
            f"{t.id} — {t.name}" for t in self.teachers.values()
        ]

        course_counter = 1
        while True:
            print(f"  --- Course #{course_counter} ---")
            cid = ask("Course ID (e.g. CS301)", f"C{course_counter:03d}")

            if cid.lower() == "done":
                if not self.courses:
                    print("  ⚠️  You need at least one course!")
                    continue
                break

            if cid in self.courses:
                print(f"  ⚠️  Course ID '{cid}' already exists.")
                continue

            name = ask("Course name", f"Course {course_counter}")
            dept = ask("Department", "General")
            group = ask("Student group (e.g. CS-3A)", f"Group-{course_counter}")
            num_students = ask_int("Number of students enrolled", default=30)
            sessions_pw = ask_int("Sessions per week", default=3, min_val=1)

            # Pick teacher
            chosen = ask_choice(
                f"Assign teacher to {name}:",
                teacher_display
            )
            chosen_idx = teacher_display.index(chosen)
            teacher_id = teacher_list[chosen_idx]

            requires_lab = ask_bool("Requires lab?", default=False)
            requires_proj = ask_bool("Requires projector?", default=True)

            priority = ask_choice(
                "Priority level:",
                ["1 — Normal", "2 — High", "3 — Critical"]
            )
            priority_val = int(priority[0])

            course = Course(
                id=cid,
                name=name,
                department=dept,
                teacher_id=teacher_id,
                student_group=group,
                num_students=num_students,
                sessions_per_week=sessions_pw,
                requires_lab=requires_lab,
                requires_projector=requires_proj,
                priority=priority_val,
            )
            self.courses[cid] = course
            print(f"  ✅ Added: {course}")

            another = ask_bool("\n  Add another course?", default=True)
            if not another:
                break
            course_counter += 1

        print(f"\n  ✅ {len(self.courses)} course(s) added.")

    # ── Sessions ─────────────────────────────────────────────────

    def _build_sessions(self):
        for course in self.courses.values():
            teacher = self.teachers[course.teacher_id]
            for i in range(1, course.sessions_per_week + 1):
                self.sessions.append(Session(
                    id=f"{course.id}-{i}",
                    course=course,
                    teacher=teacher,
                ))
        self.sessions.sort(key=lambda s: s.course.priority, reverse=True)

    # ── Summary ──────────────────────────────────────────────────

    def _show_summary(self):
        print_header("Data Summary")
        print(f"  University : {self.university_name}")
        print(f"  Days       : {', '.join(self.days)}")
        print(f"  Periods/day: {self.periods_per_day}")
        print(f"  Rooms      : {len(self.rooms)}")
        print(f"  Teachers   : {len(self.teachers)}")
        print(f"  Courses    : {len(self.courses)}")
        print(f"  Sessions   : {len(self.sessions)} (CSP variables)")
        total_slots = len(self.days) * self.periods_per_day
        print(f"  Search space: ({total_slots}×{len(self.rooms)})"
              f"^{len(self.sessions)}")