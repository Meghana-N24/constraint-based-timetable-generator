import json
from typing import Dict, List
from src.models.timeslot import generate_timeslots, DAYS
from src.models.room import Room
from src.models.teacher import Teacher
from src.models.course import Course
from src.models.session import Session


class InputParser:

    def __init__(self):
        self.timeslots = []
        self.rooms: Dict[str, Room] = {}
        self.teachers: Dict[str, Teacher] = {}
        self.courses: Dict[str, Course] = {}
        self.sessions: List[Session] = []
        self.university_name = ""

    def load_from_file(self, filepath: str) -> bool:
        print(f"\n📂 Loading data from: {filepath}")
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"  ❌ File not found: {filepath}")
            return False
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}")
            return False

        self._parse_university(data)
        self._parse_rooms(data)
        self._parse_teachers(data)
        self._parse_courses(data)
        self._build_sessions()
        self._print_summary()
        return True

    def _parse_university(self, data):
        u = data["university"]
        self.university_name = u["name"]
        days = u.get("days", DAYS)
        periods = u.get("periods_per_day", 8)
        start_hour = u.get("period_start_hour", 8)
        duration = u.get("period_duration_mins", 60)
        self.timeslots = generate_timeslots(days, periods, start_hour, duration)
        print(f"  ✅ University : {self.university_name}")
        print(f"  ✅ TimeSlots  : {len(self.timeslots)} slots "
              f"({len(days)} days x {periods} periods)")

    def _parse_rooms(self, data):
        errors = []
        for r in data.get("rooms", []):
            try:
                room = Room(
                    id=r["id"],
                    name=r["name"],
                    capacity=r["capacity"],
                    room_type=r["room_type"],
                    building=r.get("building", "Main"),
                    floor=r.get("floor", 0),
                    has_projector=r.get("has_projector", True),
                    has_lab_equipment=r.get("has_lab_equipment", False),
                )
                self.rooms[room.id] = room
            except (KeyError, ValueError) as e:
                errors.append(f"Room {r.get('id', '?')}: {e}")
        for e in errors:
            print(f"  WARNING: {e}")
        print(f"  ✅ Rooms      : {len(self.rooms)} loaded")

    def _parse_teachers(self, data):
        errors = []
        for t in data.get("teachers", []):
            try:
                unavailable = [
                    (s["day"], s["period"])
                    for s in t.get("unavailable_slots", [])
                ]
                teacher = Teacher(
                    id=t["id"],
                    name=t["name"],
                    department=t["department"],
                    subjects=t.get("subjects", []),
                    unavailable_slots=unavailable,
                    max_periods_per_day=t.get("max_periods_per_day", 4),
                    max_periods_per_week=t.get("max_periods_per_week", 20),
                )
                self.teachers[teacher.id] = teacher
            except (KeyError, ValueError) as e:
                errors.append(f"Teacher {t.get('id', '?')}: {e}")
        for e in errors:
            print(f"  WARNING: {e}")
        print(f"  ✅ Teachers   : {len(self.teachers)} loaded")

    def _parse_courses(self, data):
        errors = []
        for c in data.get("courses", []):
            try:
                tid = c["teacher_id"]
                if tid not in self.teachers:
                    errors.append(
                        f"Course {c['id']}: teacher_id '{tid}' not found"
                    )
                    continue
                course = Course(
                    id=c["id"],
                    name=c["name"],
                    department=c["department"],
                    teacher_id=tid,
                    student_group=c["student_group"],
                    num_students=c["num_students"],
                    sessions_per_week=c["sessions_per_week"],
                    requires_lab=c.get("requires_lab", False),
                    requires_projector=c.get("requires_projector", True),
                    priority=c.get("priority", 1),
                )
                self.courses[course.id] = course
            except (KeyError, ValueError) as e:
                errors.append(f"Course {c.get('id', '?')}: {e}")
        for e in errors:
            print(f"  WARNING: {e}")
        print(f"  ✅ Courses    : {len(self.courses)} loaded")

    def _build_sessions(self):
        for course in self.courses.values():
            teacher = self.teachers[course.teacher_id]
            for i in range(1, course.sessions_per_week + 1):
                session = Session(
                    id=f"{course.id}-{i}",
                    course=course,
                    teacher=teacher,
                )
                self.sessions.append(session)
        self.sessions.sort(
            key=lambda s: s.course.priority,
            reverse=True
        )
        print(f"  ✅ Sessions   : {len(self.sessions)} CSP variables created")

    def _print_summary(self):
        total_slots = len(self.timeslots)
        total_sessions = len(self.sessions)
        print(f"\n  Search space estimate:")
        print(f"     Sessions to schedule : {total_sessions}")
        print(f"     Available timeslots  : {total_slots}")
        print(f"     Available rooms      : {len(self.rooms)}")
        print(f"     Brute-force space    : "
              f"({total_slots}x{len(self.rooms)})^{total_sessions}")
        print(f"     Why we need CSP algorithms: confirmed")