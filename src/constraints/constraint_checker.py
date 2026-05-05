from typing import Dict, Tuple
from src.models.session import Session
from src.models.timeslot import TimeSlot
from src.models.room import Room


class ConstraintChecker:

    def __init__(self):
        self.teacher_schedule: Dict[Tuple, str] = {}
        self.room_schedule: Dict[Tuple, str] = {}
        self.group_schedule: Dict[Tuple, str] = {}
        self.teacher_day_load: Dict[Tuple, int] = {}

    def is_consistent(self, session, timeslot, room):
        day = timeslot.day
        period = timeslot.period
        teacher = session.teacher

        if not teacher.is_available(day, period):
            return False, f"Teacher {teacher.name} unavailable on {day} P{period}"

        t_key = (teacher.id, day, period)
        if t_key in self.teacher_schedule:
            return False, f"Teacher clash at {day} P{period}"

        r_key = (room.id, day, period)
        if r_key in self.room_schedule:
            return False, f"Room clash at {day} P{period}"

        g_key = (session.course.student_group, day, period)
        if g_key in self.group_schedule:
            return False, f"Group clash at {day} P{period}"

        if not room.can_accommodate(session.num_students):
            return False, f"Room too small"

        if session.course.requires_lab and not room.has_lab_equipment:
            return False, f"Lab required but not available"

        d_key = (teacher.id, day)
        if self.teacher_day_load.get(d_key, 0) >= teacher.max_periods_per_day:
            return False, f"Teacher daily limit reached"

        return True, ""

    def assign(self, session, timeslot, room):
        day = timeslot.day
        period = timeslot.period
        self.teacher_schedule[(session.teacher.id, day, period)] = session.id
        self.room_schedule[(room.id, day, period)] = session.id
        self.group_schedule[(session.course.student_group, day, period)] = session.id
        d_key = (session.teacher.id, day)
        self.teacher_day_load[d_key] = self.teacher_day_load.get(d_key, 0) + 1
        session.assign(timeslot, room)

    def unassign(self, session):
        if not session.is_assigned:
            return
        day = session.timeslot.day
        period = session.timeslot.period
        self.teacher_schedule.pop((session.teacher.id, day, period), None)
        self.room_schedule.pop((session.room.id, day, period), None)
        self.group_schedule.pop((session.course.student_group, day, period), None)
        d_key = (session.teacher.id, day)
        if d_key in self.teacher_day_load:
            self.teacher_day_load[d_key] -= 1
            if self.teacher_day_load[d_key] <= 0:
                del self.teacher_day_load[d_key]
        session.unassign()

    def reset(self):
        self.teacher_schedule.clear()
        self.room_schedule.clear()
        self.group_schedule.clear()
        self.teacher_day_load.clear()