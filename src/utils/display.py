from typing import List, Dict
from src.models.session import Session
from src.models.timeslot import DAYS


class TimetableDisplay:

    def print_full(self, sessions: List[Session], university_name: str):
        print(f"\n{'='*70}")
        print(f"  TIMETABLE — {university_name}")
        print(f"{'='*70}")

        # Group by day
        by_day: Dict[str, List[Session]] = {day: [] for day in DAYS}
        for s in sessions:
            if s.is_assigned:
                by_day[s.timeslot.day].append(s)

        for day in DAYS:
            day_sessions = sorted(by_day[day], key=lambda s: s.timeslot.period)
            if not day_sessions:
                continue
            print(f"\n  📅 {day}")
            print(f"  {'Period':<8} {'Time':<14} {'Course':<26} "
                  f"{'Group':<10} {'Room':<8} {'Teacher'}")
            print(f"  {'-'*85}")
            for s in day_sessions:
                print(f"  P{s.timeslot.period:<7} "
                      f"{s.timeslot.start_time+'-'+s.timeslot.end_time:<14} "
                      f"{s.course.name:<26} "
                      f"{s.course.student_group:<10} "
                      f"{s.room.id:<8} "
                      f"{s.teacher.name}")

    def print_by_teacher(self, sessions: List[Session]):
        print(f"\n{'='*70}")
        print(f"  TIMETABLE BY TEACHER")
        print(f"{'='*70}")

        by_teacher: Dict[str, List[Session]] = {}
        for s in sessions:
            if s.is_assigned:
                tid = s.teacher.name
                by_teacher.setdefault(tid, []).append(s)

        for teacher_name, tsessions in sorted(by_teacher.items()):
            print(f"\n  👤 {teacher_name}")
            print(f"  {'Day':<12} {'Period':<8} {'Time':<14} {'Course':<26} {'Room'}")
            print(f"  {'-'*70}")
            for s in sorted(tsessions,
                            key=lambda x: (DAYS.index(x.timeslot.day),
                                           x.timeslot.period)):
                print(f"  {s.timeslot.day:<12} "
                      f"P{s.timeslot.period:<7} "
                      f"{s.timeslot.start_time+'-'+s.timeslot.end_time:<14} "
                      f"{s.course.name:<26} "
                      f"{s.room.id}")

    def print_by_room(self, sessions: List[Session]):
        print(f"\n{'='*70}")
        print(f"  TIMETABLE BY ROOM")
        print(f"{'='*70}")

        by_room: Dict[str, List[Session]] = {}
        for s in sessions:
            if s.is_assigned:
                by_room.setdefault(s.room.id, []).append(s)

        for room_id, rsessions in sorted(by_room.items()):
            room = rsessions[0].room
            print(f"\n  🏛️  {room_id} — {room.name} "
                  f"(cap={room.capacity}, {room.room_type.value})")
            print(f"  {'Day':<12} {'Period':<8} {'Course':<26} {'Group':<10} {'Teacher'}")
            print(f"  {'-'*70}")
            for s in sorted(rsessions,
                            key=lambda x: (DAYS.index(x.timeslot.day),
                                           x.timeslot.period)):
                print(f"  {s.timeslot.day:<12} "
                      f"P{s.timeslot.period:<7} "
                      f"{s.course.name:<26} "
                      f"{s.course.student_group:<10} "
                      f"{s.teacher.name}")