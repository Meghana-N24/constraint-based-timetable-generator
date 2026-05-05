import json
import csv
import os
from typing import List
from src.models.session import Session
from src.models.timeslot import DAYS


class TimetableExporter:

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_csv(self, sessions: List[Session], filename: str = "timetable.csv"):
        filepath = os.path.join(self.output_dir, filename)
        assigned = [s for s in sessions if s.is_assigned]

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Session ID", "Course", "Department", "Group",
                "Day", "Period", "Start", "End",
                "Room", "Room Name", "Teacher"
            ])
            for s in sorted(assigned,
                            key=lambda x: (DAYS.index(x.timeslot.day),
                                           x.timeslot.period)):
                writer.writerow([
                    s.id,
                    s.course.name,
                    s.course.department,
                    s.course.student_group,
                    s.timeslot.day,
                    s.timeslot.period,
                    s.timeslot.start_time,
                    s.timeslot.end_time,
                    s.room.id,
                    s.room.name,
                    s.teacher.name,
                ])
        print(f"  ✅ CSV exported  : {filepath}")
        return filepath

    def export_json(self, sessions: List[Session], filename: str = "timetable.json"):
        filepath = os.path.join(self.output_dir, filename)
        assigned = [s for s in sessions if s.is_assigned]

        data = []
        for s in sorted(assigned,
                        key=lambda x: (DAYS.index(x.timeslot.day),
                                       x.timeslot.period)):
            data.append({
                "session_id": s.id,
                "course": s.course.name,
                "department": s.course.department,
                "student_group": s.course.student_group,
                "timeslot": {
                    "day": s.timeslot.day,
                    "period": s.timeslot.period,
                    "start": s.timeslot.start_time,
                    "end": s.timeslot.end_time,
                },
                "room": {
                    "id": s.room.id,
                    "name": s.room.name,
                    "capacity": s.room.capacity,
                },
                "teacher": s.teacher.name,
            })

        with open(filepath, "w") as f:
            json.dump({"timetable": data, "total_sessions": len(data)}, f, indent=2)

        print(f"  ✅ JSON exported : {filepath}")
        return filepath

    def export_text(self, sessions: List[Session],
                    university_name: str,
                    filename: str = "timetable.txt"):
        filepath = os.path.join(self.output_dir, filename)
        assigned = [s for s in sessions if s.is_assigned]

        by_day = {day: [] for day in DAYS}
        for s in assigned:
            by_day[s.timeslot.day].append(s)

        with open(filepath, "w") as f:
            f.write(f"TIMETABLE — {university_name}\n")
            f.write("=" * 70 + "\n\n")

            for day in DAYS:
                day_sessions = sorted(by_day[day],
                                      key=lambda s: s.timeslot.period)
                if not day_sessions:
                    continue
                f.write(f"{day}\n")
                f.write("-" * 70 + "\n")
                for s in day_sessions:
                    f.write(
                        f"  P{s.timeslot.period} "
                        f"{s.timeslot.start_time}-{s.timeslot.end_time}  "
                        f"{s.course.name:<26} "
                        f"{s.course.student_group:<10} "
                        f"{s.room.id:<8} "
                        f"{s.teacher.name}\n"
                    )
                f.write("\n")

        print(f"  ✅ TXT exported  : {filepath}")
        return filepath