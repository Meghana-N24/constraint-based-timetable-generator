import time
from typing import List, Dict
from src.models.session import Session
from src.models.timeslot import TimeSlot
from src.models.room import Room
from src.constraints.constraint_checker import ConstraintChecker


class BacktrackingSolver:

    def __init__(self, sessions, timeslots, rooms, use_mrv=True):
        self.sessions = list(sessions)
        self.timeslots = list(timeslots)
        self.rooms = list(rooms.values()) if isinstance(rooms, dict) else list(rooms)
        self.checker = ConstraintChecker()
        self.use_mrv = use_mrv
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = 0.0
        self.solve_time = 0.0

    def solve(self) -> bool:
        self.checker.reset()
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = time.time()
        for s in self.sessions:
            s.unassign()
        result = self._backtrack(0)
        self.solve_time = time.time() - self.start_time
        return result

    def _backtrack(self, index: int) -> bool:
        if index == len(self.sessions):
            return True

        if self.use_mrv:
            session = self._select_session_mrv(index)
        else:
            session = self.sessions[index]

        self.nodes_explored += 1

        for timeslot in self.timeslots:
            for room in self._order_rooms(session):
                ok, reason = self.checker.is_consistent(session, timeslot, room)
                if ok:
                    self.checker.assign(session, timeslot, room)
                    if self._backtrack(index + 1):
                        return True
                    self.checker.unassign(session)
                    self.backtracks += 1

        return False

    def _select_session_mrv(self, index: int) -> Session:
        unassigned = self.sessions[index:]
        if len(unassigned) == 1:
            return unassigned[0]

        def count_valid(session):
            count = 0
            for ts in self.timeslots:
                for room in self.rooms:
                    ok, _ = self.checker.is_consistent(session, ts, room)
                    if ok:
                        count += 1
            return count

        chosen = min(unassigned, key=count_valid)
        idx = self.sessions.index(chosen)
        self.sessions[index], self.sessions[idx] = (
            self.sessions[idx], self.sessions[index]
        )
        return chosen

    def _order_rooms(self, session: Session) -> List[Room]:
        suitable = [
            r for r in self.rooms
            if r.can_accommodate(session.num_students)
            and r.is_suitable_for(
                session.course.requires_lab,
                session.course.requires_projector
            )
        ]
        suitable.sort(key=lambda r: r.capacity)
        return suitable

    def print_stats(self):
        print(f"\n  Solver Statistics:")
        print(f"    Nodes explored : {self.nodes_explored}")
        print(f"    Backtracks     : {self.backtracks}")
        print(f"    Time taken     : {self.solve_time:.4f} seconds")
        print(f"    MRV heuristic  : {'ON' if self.use_mrv else 'OFF'}")