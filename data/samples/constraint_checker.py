from typing import List, Dict, Tuple, Optional
from src.models.session import Session
from src.models.timeslot import TimeSlot
from src.models.room import Room


class ConstraintChecker:
    """
    Checks ALL hard constraints before accepting any assignment.

    Hard constraints:
      1. No teacher teaches two sessions at the same timeslot
      2. No room hosts two sessions at the same timeslot
      3. No student group has two sessions at the same timeslot
      4. Teacher must be available at that timeslot
      5. Room must fit the number of students
      6. Room type must match course requirement (lab vs classroom)
      7. Teacher workload per day must not exceed limit
    """

    def __init__(self):
        # These track what is already assigned — updated live by solver
        # Key: (teacher_id, day, period) -> session_id
        self.teacher_schedule: Dict[Tuple, str] = {}
        # Key: (room_id, day, period) -> session_id
        self.room_schedule: Dict[Tuple, str] = {}
        # Key: (student_group, day, period) -> session_id
        self.group_schedule: Dict[Tuple, str] = {}
        # Key: (teacher_id, day) -> count of periods assigned
        self.teacher_day_load: Dict[Tuple, int] = {}

    def is_consistent(
        self,
        session: Session,
        timeslot: TimeSlot,
        room: Room
    ) -> Tuple[bool, str]:
        """
        Returns (True, "") if assignment is valid.
        Returns (False, reason) if any constraint is violated.
        """

        day = timeslot.day
        period = timeslot.period
        teacher = session.teacher

        # 1. Teacher availability
        if not teacher.is_available(day, period):
            return False, f"Teacher {teacher.name} unavailable on {day} P{period}"

        # 2. Teacher already teaching at this slot
        t_key = (teacher.id, day, period)
        if t_key in self.teacher_schedule:
            other = self.teacher_schedule[t_key]
            return False, f"Teacher {teacher.name} already teaching {other} at {day} P{period}"

        # 3. Room already occupied at this slot
        r_key = (room.id, day, period)
        if r_key in self.room_schedule:
            other = self.room_schedule[r_key]
            return False, f"Room {room.id} already occupied by {other} at {day} P{period}"

        # 4. Student group already has class at this slot
        g_key = (session.course.student_group, day, period)
        if g_key in self.group_schedule:
            other = self.group_schedule[g_key]
            return False, f"Group {session.course.student_group} already has {other} at {day} P{period}"

        # 5. Room capacity
        if not room.can_accommodate(session.num_students):
            return False, (f"Room {room.id} capacity {room.capacity} "
                           f"< {session.num_students} students")

        # 6. Lab requirement
        if session.course.requires_lab and not room.has_lab_equipment:
            return False, f"Course needs lab but {room.id} has no lab equipment"

        # 7. Teacher daily workload
        d_key = (teacher.id, day)
        current_load = self.teacher_day_load.get(d_key, 0)
        if current_load >= teacher.max_periods_per_day:
            return False, (f"Teacher {teacher.name} already at max "
                           f"{teacher.max_periods_per_day} periods on {day}")

        return True, ""

    def assign(self, session: Session, timeslot: TimeSlot, room: Room):
        """Register an assignment into all tracking dicts."""
        day = timeslot.day
        period = timeslot.period

        self.teacher_schedule[(session.teacher.id, day, period)] = session.id
        self.room_schedule[(room.id, day, period)] = session.id
        self.group_schedule[(session.course.student_group, day, period)] = session.id

        d_key = (session.teacher.id, day)
        self.teacher_day_load[d_key] = self.teacher_day_load.get(d_key, 0) + 1

        session.assign(timeslot, room)

    def unassign(self, session: Session):
        """Remove an assignment from all tracking dicts (for backtracking)."""
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
        """Clear all state."""
        self.teacher_schedule.clear()
        self.room_schedule.clear()
        self.group_schedule.clear()
        self.teacher_day_load.clear()