import time
from typing import List, Dict, Optional, Tuple
from src.models.session import Session
from src.models.timeslot import TimeSlot
from src.models.room import Room
from src.constraints.constraint_checker import ConstraintChecker


class BacktrackingSolver:
    """
    Solves the timetable CSP using backtracking with:
      - MRV  (Minimum Remaining Values) heuristic
      - Least Constraining Value ordering
      - Forward checking (optional, Phase 3)

    How backtracking works:
      1. Pick an unassigned session
      2. Try every (timeslot, room) combination
      3. If consistent → assign it, move to next session
      4. If no combination works → undo last assignment, try next value
      5. Repeat until all sessions assigned OR no solution exists
    """

    def __init__(
        self,
        sessions: List[Session],
        timeslots: List[TimeSlot],
        rooms: Dict[str, Room],
        use_mrv: bool = True,
    ):
        self.sessions = sessions
        self.timeslots = timeslots
        self.rooms = list(rooms.values())
        self.checker = ConstraintChecker()
        self.use_mrv = use_mrv

        # Statistics
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = 0.0
        self.solve_time = 0.0

    def solve(self) -> bool:
        """
        Entry point. Returns True if solution found, False otherwise.
        """
        self.checker.reset()
        self.nodes_explored = 0
        self.backtracks = 0
        self.start_time = time.time()

        # Unassign everything first (clean state)
        for s in self.sessions:
            s.unassign()

        result = self._backtrack(0)
        self.solve_time = time.time() - self.start_time
        return result

    def _backtrack(self, index: int) -> bool:
        """
        Recursive backtracking.
        index = which session we are currently trying to assign.
        """

        # Base case: all sessions assigned = solution found
        if index == len(self.sessions):
            return True

        # Choose next session to assign
        if self.use_mrv:
            session = self._select_session_mrv(index)
        else:
            session = self.sessions[index]

        self.nodes_explored += 1

        # Try every (timeslot, room) pair in the domain
        for timeslot in self.timeslots:
            for room in self._order_rooms(session):

                ok, reason = self.checker.is_consistent(session, timeslot, room)

                if ok:
                    # Assign and recurse
                    self.checker.assign(session, timeslot, room)

                    if self._backtrack(index + 1):
                        return True  # Solution found up the chain

                    # Undo (backtrack)
                    self.checker.unassign(session)
                    self.backtracks += 1

        # No value worked for this session
        return False

    def _select_session_mrv(self, index: int) -> Session:
        """
        MRV = Minimum Remaining Values heuristic.

        Pick the session that has the FEWEST valid (timeslot, room)
        combinations remaining. This reduces the branching factor.

        Think of it as: solve the hardest constraint first.
        """
        unassigned = self.sessions[index:]
        if len(unassigned) == 1:
            return unassigned[0]

        def count_valid_values(session: Session) -> int:
            count = 0
            for ts in self.timeslots:
                for room in self.rooms:
                    ok, _ = self.checker.is_consistent(session, ts, room)
                    if ok:
                        count += 1
            return count

        # Pick session with minimum remaining values
        chosen = min(unassigned, key=count_valid_values)

        # Swap chosen into current position so backtrack stays correct
        idx = self.sessions.index(chosen)
        self.sessions[index], self.sessions[idx] = (
            self.sessions[idx], self.sessions[index]
        )
        return chosen

    def _order_rooms(self, session: Session) -> List[Room]:
        """
        Least Constraining Value: prefer rooms that leave more options
        for other sessions. Here we sort by how well-fitted the room is:
        smaller suitable room first (wastes less capacity).
        """
        suitable = [
            r for r in self.rooms
            if r.can_accommodate(session.num_students)
            and r.is_suitable_for(
                session.course.requires_lab,
                session.course.requires_projector
            )
        ]
        # Sort: smallest capacity that still fits (least wasteful)
        suitable.sort(key=lambda r: r.capacity)
        return suitable

    def print_stats(self):
        print(f"\n  Solver Statistics:")
        print(f"    Nodes explored : {self.nodes_explored}")
        print(f"    Backtracks     : {self.backtracks}")
        print(f"    Time taken     : {self.solve_time:.4f} seconds")
        print(f"    MRV heuristic  : {'ON' if self.use_mrv else 'OFF'}")