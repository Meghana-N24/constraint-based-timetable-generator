from dataclasses import dataclass
from typing import List

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


@dataclass(frozen=True)
class TimeSlot:
    day: str
    period: int
    start_time: str
    end_time: str

    def __post_init__(self):
        if self.day not in DAYS:
            raise ValueError(f"Invalid day: {self.day}")
        if self.period < 1:
            raise ValueError("Period must be >= 1")

    def __str__(self):
        return f"{self.day} P{self.period} ({self.start_time}-{self.end_time})"

    def __repr__(self):
        return self.__str__()


def generate_timeslots(days, periods_per_day, start_hour=8, period_duration_mins=60):
    slots = []
    for day in days:
        for p in range(1, periods_per_day + 1):
            total_start = start_hour * 60 + (p - 1) * period_duration_mins
            total_end = total_start + period_duration_mins
            start = f"{total_start // 60:02d}:{total_start % 60:02d}"
            end = f"{total_end // 60:02d}:{total_end % 60:02d}"
            slots.append(TimeSlot(day=day, period=p, start_time=start, end_time=end))
    return slots