from dataclasses import dataclass
from typing import Optional


@dataclass
class Session:
    id: str
    course: object
    teacher: object
    timeslot: Optional[object] = None
    room: Optional[object] = None

    @property
    def is_assigned(self):
        return self.timeslot is not None and self.room is not None

    @property
    def is_lab(self):
        return self.course.requires_lab

    @property
    def num_students(self):
        return self.course.num_students

    def assign(self, timeslot, room):
        self.timeslot = timeslot
        self.room = room

    def unassign(self):
        self.timeslot = None
        self.room = None

    def __str__(self):
        if self.is_assigned:
            return f"[{self.id}] {self.course.name} -> {self.timeslot} in {self.room}"
        return f"[{self.id}] {self.course.name} -> UNASSIGNED"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Session) and self.id == other.id