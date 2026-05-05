from typing import List, Tuple, Dict
from src.models.session import Session


class TimetableValidator:

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, sessions: List[Session]) -> bool:
        self.errors = []
        self.warnings = []

        assigned = [s for s in sessions if s.is_assigned]
        unassigned = [s for s in sessions if not s.is_assigned]

        for s in unassigned:
            self.errors.append(
                f"UNASSIGNED: {s.id} ({s.course.name}) never scheduled"
            )

        teacher_slots: Dict[Tuple, List[str]] = {}
        room_slots: Dict[Tuple, List[str]] = {}
        group_slots: Dict[Tuple, List[str]] = {}
        teacher_day: Dict[Tuple, List[str]] = {}

        for s in assigned:
            day = s.timeslot.day
            period = s.timeslot.period

            t_key = (s.teacher.id, day, period)
            teacher_slots.setdefault(t_key, []).append(s.id)

            r_key = (s.room.id, day, period)
            room_slots.setdefault(r_key, []).append(s.id)

            g_key = (s.course.student_group, day, period)
            group_slots.setdefault(g_key, []).append(s.id)

            if not s.teacher.is_available(day, period):
                self.errors.append(
                    f"AVAILABILITY: {s.teacher.name} unavailable "
                    f"on {day} P{period} but assigned {s.id}"
                )

            if not s.room.can_accommodate(s.num_students):
                self.errors.append(
                    f"CAPACITY: {s.room.id} holds {s.room.capacity} "
                    f"but {s.id} has {s.num_students} students"
                )

            if s.course.requires_lab and not s.room.has_lab_equipment:
                self.errors.append(
                    f"LAB: {s.id} needs lab but assigned to {s.room.id}"
                )

            d_key = (s.teacher.id, day)
            teacher_day.setdefault(d_key, []).append(s.id)

        for key, sids in teacher_slots.items():
            if len(sids) > 1:
                tid, day, period = key
                self.errors.append(
                    f"TEACHER CLASH: {tid} has {len(sids)} sessions "
                    f"on {day} P{period}: {sids}"
                )

        for key, sids in room_slots.items():
            if len(sids) > 1:
                rid, day, period = key
                self.errors.append(
                    f"ROOM CLASH: {rid} has {len(sids)} sessions "
                    f"on {day} P{period}: {sids}"
                )

        for key, sids in group_slots.items():
            if len(sids) > 1:
                gid, day, period = key
                self.errors.append(
                    f"GROUP CLASH: {gid} has {len(sids)} sessions "
                    f"on {day} P{period}: {sids}"
                )

        for (tid, day), sids in teacher_day.items():
            teacher = next(
                s.teacher for s in assigned if s.teacher.id == tid
            )
            if len(sids) > teacher.max_periods_per_day:
                self.warnings.append(
                    f"WORKLOAD: {teacher.name} has {len(sids)} periods "
                    f"on {day} (max {teacher.max_periods_per_day})"
                )

        return len(self.errors) == 0

    def print_report(self):
        print(f"\n{'='*55}")
        print(f"  VALIDATION REPORT")
        print(f"{'='*55}")

        if not self.errors and not self.warnings:
            print("  ✅ PERFECT — No errors or warnings found!")
            print("  All hard constraints satisfied.")
            return

        if self.errors:
            print(f"\n  ❌ ERRORS ({len(self.errors)}):")
            for e in self.errors:
                print(f"     {e}")

        if self.warnings:
            print(f"\n  ⚠️  WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"     {w}")

        if not self.errors:
            print("\n  ✅ Valid — no hard constraint violations.")