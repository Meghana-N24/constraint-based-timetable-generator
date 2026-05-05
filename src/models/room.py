from dataclasses import dataclass
from enum import Enum


class RoomType(Enum):
    CLASSROOM = "classroom"
    LAB = "lab"
    AUDITORIUM = "auditorium"
    SEMINAR = "seminar"


@dataclass
class Room:
    id: str
    name: str
    capacity: int
    room_type: RoomType
    building: str = "Main"
    floor: int = 0
    has_projector: bool = True
    has_lab_equipment: bool = False

    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError(f"Room {self.id}: capacity must be > 0")
        if isinstance(self.room_type, str):
            self.room_type = RoomType(self.room_type.lower())

    def can_accommodate(self, num_students):
        return self.capacity >= num_students

    def is_suitable_for(self, requires_lab, requires_projector):
        if requires_lab and not self.has_lab_equipment:
            return False
        if requires_projector and not self.has_projector:
            return False
        return True

    def __str__(self):
        return f"{self.id} ({self.name}, cap={self.capacity}, {self.room_type.value})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Room) and self.id == other.id