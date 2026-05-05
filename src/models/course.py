from dataclasses import dataclass, field
from typing import List


@dataclass
class Course:
    id: str
    name: str
    department: str
    teacher_id: str
    student_group: str
    num_students: int
    sessions_per_week: int
    requires_lab: bool = False
    requires_projector: bool = True
    priority: int = 1
    preferred_slots: List = field(default_factory=list)

    def __post_init__(self):
        if self.sessions_per_week < 1:
            raise ValueError(f"Course {self.id}: sessions_per_week must be >= 1")
        if self.num_students < 1:
            raise ValueError(f"Course {self.id}: num_students must be >= 1")
        if self.priority not in (1, 2, 3):
            raise ValueError(f"Course {self.id}: priority must be 1, 2, or 3")

    def __str__(self):
        lab = "LAB" if self.requires_lab else "LEC"
        return (f"{self.id} - {self.name} "
                f"[{self.student_group}, {self.sessions_per_week}x/week, {lab}]")

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Course) and self.id == other.id