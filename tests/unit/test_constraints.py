import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.models.timeslot import TimeSlot
from src.models.room import Room
from src.models.teacher import Teacher
from src.models.course import Course
from src.models.session import Session
from src.constraints.constraint_checker import ConstraintChecker


# ── Shared test fixtures ──────────────────────────────────────────────

def make_slot(day="Monday", period=1):
    return TimeSlot(day=day, period=period,
                    start_time="08:00", end_time="09:00")

def make_room(rid="R1", capacity=50, lab=False):
    return Room(id=rid, name=f"Room {rid}", capacity=capacity,
                room_type="lab" if lab else "classroom",
                has_lab_equipment=lab, has_projector=True)

def make_teacher(tid="T1", unavailable=None):
    return Teacher(id=tid, name=f"Teacher {tid}",
                   department="CS", subjects=["Math"],
                   unavailable_slots=unavailable or [],
                   max_periods_per_day=4, max_periods_per_week=20)

def make_course(cid="C1", group="G1", students=30,
                lab=False, priority=1):
    return Course(id=cid, name=f"Course {cid}", department="CS",
                  teacher_id="T1", student_group=group,
                  num_students=students, sessions_per_week=1,
                  requires_lab=lab, priority=priority)

def make_session(sid="S1", course=None, teacher=None):
    course = course or make_course()
    teacher = teacher or make_teacher()
    return Session(id=sid, course=course, teacher=teacher)


# ── Tests ─────────────────────────────────────────────────────────────

def test_basic_assignment_is_valid():
    checker = ConstraintChecker()
    session = make_session()
    slot = make_slot()
    room = make_room()
    ok, reason = checker.is_consistent(session, slot, room)
    assert ok, f"Basic assignment should be valid. Got: {reason}"
    print("  ✅ test_basic_assignment_is_valid")


def test_teacher_clash_detected():
    checker = ConstraintChecker()
    t = make_teacher("T1")
    c1 = make_course("C1", group="G1")
    c2 = make_course("C2", group="G2")
    s1 = make_session("S1", course=c1, teacher=t)
    s2 = make_session("S2", course=c2, teacher=t)
    slot = make_slot("Monday", 1)
    room1 = make_room("R1")
    room2 = make_room("R2")

    checker.assign(s1, slot, room1)
    ok, reason = checker.is_consistent(s2, slot, room2)
    assert not ok, "Teacher clash should be detected"
    assert "clash" in reason.lower() or "teach" in reason.lower()
    print("  ✅ test_teacher_clash_detected")


def test_room_clash_detected():
    checker = ConstraintChecker()
    t1 = make_teacher("T1")
    t2 = make_teacher("T2")
    c1 = make_course("C1", group="G1")
    c2 = make_course("C2", group="G2")
    s1 = make_session("S1", course=c1, teacher=t1)
    s2 = make_session("S2", course=c2, teacher=t2)
    slot = make_slot("Monday", 1)
    room = make_room("R1")

    checker.assign(s1, slot, room)
    ok, reason = checker.is_consistent(s2, slot, room)
    assert not ok, "Room clash should be detected"
    print("  ✅ test_room_clash_detected")


def test_group_clash_detected():
    checker = ConstraintChecker()
    t1 = make_teacher("T1")
    t2 = make_teacher("T2")
    c1 = make_course("C1", group="G1")
    c2 = make_course("C2", group="G1")  # same group!
    s1 = make_session("S1", course=c1, teacher=t1)
    s2 = make_session("S2", course=c2, teacher=t2)
    slot = make_slot("Monday", 1)
    room1 = make_room("R1")
    room2 = make_room("R2")

    checker.assign(s1, slot, room1)
    ok, reason = checker.is_consistent(s2, slot, room2)
    assert not ok, "Group clash should be detected"
    print("  ✅ test_group_clash_detected")


def test_teacher_unavailability_respected():
    checker = ConstraintChecker()
    t = make_teacher("T1", unavailable=[("Monday", 1)])
    c = make_course("C1")
    s = make_session("S1", course=c, teacher=t)
    slot = make_slot("Monday", 1)
    room = make_room("R1")

    ok, reason = checker.is_consistent(s, slot, room)
    assert not ok, "Unavailable slot should be rejected"
    print("  ✅ test_teacher_unavailability_respected")


def test_room_capacity_enforced():
    checker = ConstraintChecker()
    t = make_teacher()
    c = make_course(students=60)     # 60 students
    s = make_session(course=c, teacher=t)
    slot = make_slot()
    room = make_room(capacity=40)   # only fits 40

    ok, reason = checker.is_consistent(s, slot, room)
    assert not ok, "Overcapacity should be rejected"
    print("  ✅ test_room_capacity_enforced")


def test_lab_requirement_enforced():
    checker = ConstraintChecker()
    t = make_teacher()
    c = make_course(lab=True)        # needs lab
    s = make_session(course=c, teacher=t)
    slot = make_slot()
    room = make_room(lab=False)      # no lab equipment

    ok, reason = checker.is_consistent(s, slot, room)
    assert not ok, "Lab requirement should be enforced"
    print("  ✅ test_lab_requirement_enforced")


def test_backtrack_unassign_works():
    checker = ConstraintChecker()
    t = make_teacher("T1")
    c = make_course("C1", group="G1")
    s = make_session("S1", course=c, teacher=t)
    slot = make_slot()
    room = make_room("R1")

    checker.assign(s, slot, room)
    assert s.is_assigned

    checker.unassign(s)
    assert not s.is_assigned

    # Should be assignable again after unassign
    ok, reason = checker.is_consistent(s, slot, room)
    assert ok, f"After unassign, should be valid again. Got: {reason}"
    print("  ✅ test_backtrack_unassign_works")


def test_different_slots_no_clash():
    checker = ConstraintChecker()
    t = make_teacher("T1")
    c1 = make_course("C1", group="G1")
    c2 = make_course("C2", group="G1")
    s1 = make_session("S1", course=c1, teacher=t)
    s2 = make_session("S2", course=c2, teacher=t)
    slot1 = make_slot("Monday", 1)
    slot2 = make_slot("Monday", 2)   # different period
    room = make_room("R1")

    checker.assign(s1, slot1, room)
    ok, reason = checker.is_consistent(s2, slot2, room)
    assert ok, f"Different slots should not clash. Got: {reason}"
    print("  ✅ test_different_slots_no_clash")


# ── Run all tests ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"  RUNNING CONSTRAINT TESTS")
    print(f"{'='*55}\n")

    tests = [
        test_basic_assignment_is_valid,
        test_teacher_clash_detected,
        test_room_clash_detected,
        test_group_clash_detected,
        test_teacher_unavailability_respected,
        test_room_capacity_enforced,
        test_lab_requirement_enforced,
        test_backtrack_unassign_works,
        test_different_slots_no_clash,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  💥 {test.__name__} CRASHED: {e}")
            failed += 1

    print(f"\n{'='*55}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*55}\n")