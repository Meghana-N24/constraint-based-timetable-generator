import sys
import os

# This ensures Python finds the src/ folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.timeslot import generate_timeslots
from src.models.room import Room
from src.models.teacher import Teacher
from src.models.course import Course
from src.models.session import Session

# Build timeslots
slots = generate_timeslots(['Monday','Tuesday'], periods_per_day=3, start_hour=9)
print('--- TimeSlots ---')
for s in slots:
    print(' ', s)

# Build a room
lab = Room(id='LAB1', name='CS Lab 1', capacity=40,
           room_type='lab', has_lab_equipment=True)
print('\n--- Room ---')
print(' ', lab)
print('  Fits 35 students?', lab.can_accommodate(35))

# Build a teacher
t = Teacher(id='T001', name='Dr. Ahmed', department='CS',
            subjects=['Data Structures','Algorithms'],
            unavailable_slots=[('Monday',1)])
print('\n--- Teacher ---')
print(' ', t)
print('  Available Mon P1?', t.is_available('Monday', 1))
print('  Available Mon P2?', t.is_available('Monday', 2))

# Build a course
c = Course(id='CS301', name='Data Structures', department='CS',
           teacher_id='T001', student_group='CS-3A',
           num_students=35, sessions_per_week=3,
           requires_lab=True, priority=2)
print('\n--- Course ---')
print(' ', c)

# Build sessions
sessions = [Session(id=f'CS301-{i}', course=c, teacher=t) for i in range(1,4)]
print('\n--- Sessions (CSP Variables) ---')
for s in sessions:
    print(' ', s)

# Assign one
sessions[0].assign(slots[1], lab)
print('\n--- After Assignment ---')
print(' ', sessions[0])
print('  Is assigned?', sessions[0].is_assigned)

print('\n✅ All models working correctly!')
