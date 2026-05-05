from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Teacher:
    id: str
    name: str
    department: str
    subjects: List[str] = field(default_factory=list)
    unavailable_slots: List[Tuple[str, int]] = field(default_factory=list)
    max_periods_per_day: int = 4
    max_periods_per_week: int = 20

    def __post_init__(self):
        self._unavailable_set = set(
            (day, period) for day, period in self.unavailable_slots
        )

    def is_available(self, day, period):
        return (day, period) not in self._unavailable_set

    def can_teach(self, subject):
        return subject in self.subjects

    def add_unavailable(self, day, period):
        self.unavailable_slots.append((day, period))
        self._unavailable_set.add((day, period))

    def __str__(self):
        return f"{self.id} - {self.name} ({self.department})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Teacher) and self.id == other.id