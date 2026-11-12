from __future__ import annotations
from enum import Enum
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import itertools
from admin import Admin

if TYPE_CHECKING:  # only needed for type hints, importing them for real causes circular imports
    from event import Event
    from RoomFacilityClasses import room as Room
    from user import User


_reservation_ids = itertools.count()  # so we can have auto-generated ids from 0-n
_all_reservations = []

_now = datetime.now().replace(microsecond=0)  # simulated clock, only moves with advance_time()

RETENTION_PERIOD = timedelta(days=30)
REMINDER_BEFORE_START = timedelta(hours=24)

class ReservationStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending approval"
    APPROVED = "approved"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

# the closed composite state from the diagram
CLOSED_STATES = {ReservationStatus.COMPLETED, ReservationStatus.REJECTED, ReservationStatus.CANCELLED, ReservationStatus.EXPIRED}

def get_now() -> datetime:
    return _now

def advance_time(hours: float) -> None:
    global _now
    _now += timedelta(hours=hours)

    # keep going until nothing changes so one big jump can go through several states
    changed = True
    while changed:
        changed = False
        for reservation in list(_all_reservations):
            if reservation._check_time():
                changed = True

class Reservation:

    def __init__(self, submitter: User, event: Event, room: Room, start_time, end_time, equipment_needed = None, support_needed = None) -> None:
        if end_time <= start_time:
            raise ValueError("End time must come after the start time")

        self._reservation_id = next(_reservation_ids)
        self._start_time = start_time
        self._end_time = end_time
        self._status = ReservationStatus.DRAFT
        self._submitted_at = None
        self._review_comment = ""
        self._cancel_reason = ""
        self._equipment_needed = list(equipment_needed or [])
        self._support_needed = list(support_needed or [])
        self._submitter = submitter
        self._event = event
        self._room = room
        self._reminder_sent = False
        self._closed_at = None

        _all_reservations.append(self)


    @property
    def event(self):
        return self._event

    @property
    def start_time(self):
        return self._start_time


    def get_all_reservations() -> list:
        return list(_all_reservations)


    def submit(self) -> None:
        if self._status != ReservationStatus.DRAFT:
            self._not_allowed("submit")
            return
        if not self.is_valid():
            print("Invalid reservation details")
            return
        if self.check_conflicts():
            self._notify("CONFLICT")
            return

        self._status = ReservationStatus.PENDING_APPROVAL
        self._submitted_at = _now
        self._notify("SUBMITTED")


    def edit(self, start: datetime, end: datetime, room: Room) -> None:
        if self._status not in {ReservationStatus.DRAFT, ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            self._not_allowed("edit")
            return

        if end <= start:
            raise ValueError("End time must be after start time")

        self._save_changes(start, end, room)

        # pending and approved reservations are sent back to draft stage during edits
        if self._status != ReservationStatus.DRAFT:
            self._status = ReservationStatus.DRAFT
            self._submitted_at = None
            self._review_comment = ""
            self._reminder_sent = False
            self._notify("WITHDRAWN")


    def cancel(self, reason: str = "") -> None:
        if self._status == ReservationStatus.DRAFT:
            self._remove()
            return
        if self._status not in {ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            self._not_allowed("cancel")
            return

        self._cancel_reason = reason
        self._close(ReservationStatus.CANCELLED)
        self._notify("CANCELLATION")


    def approve(self, approver: Admin, comment: str = "") -> None:
        if self._status != ReservationStatus.PENDING_APPROVAL:
            self._not_allowed("approve")
            return
        if not isinstance(approver, Admin):
            print("Only an admin can approve reservations")
            return

        self._status = ReservationStatus.APPROVED
        self._review_comment = comment
        self._notify("CONFIRMATION")


    def reject(self, approver: Admin, comment: str = "") -> None:
        if self._status != ReservationStatus.PENDING_APPROVAL:
            self._not_allowed("reject")
            return
        if not isinstance(approver, Admin):
            print("Only an admin can reject reservations")
            return

        self._review_comment = comment
        self._close(ReservationStatus.REJECTED)
        self._notify("REJECTION")


    def is_valid(self) -> bool:
        return self._room is not None and self._start_time < self._end_time and self._start_time > _now and self._room.capacity >= self._event.expectedAttendance


    def check_conflicts(self) -> bool:
        holding = {ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED, ReservationStatus.IN_PROGRESS}

        for other in _all_reservations:
            if (other is not self and other._room is self._room and other._status in holding
                and other._start_time < self._end_time and self._start_time < other._end_time):
                return True

        return False


    def _check_time(self) -> bool:
        # returns True if something changed
        if self._status == ReservationStatus.PENDING_APPROVAL and _now >= self._start_time:
            self._close(ReservationStatus.EXPIRED)
            self._notify("EXPIRED")
            return True

        if self._status == ReservationStatus.APPROVED:
            if not self._reminder_sent and _now >= self._start_time - REMINDER_BEFORE_START:
                self._reminder_sent = True
                self._notify("REMINDER")
                return True
            if _now >= self._start_time:
                self._status = ReservationStatus.IN_PROGRESS
                return True

        if self._status == ReservationStatus.IN_PROGRESS and _now >= self._end_time:
            self._close(ReservationStatus.COMPLETED)
            return True

        if self._status in CLOSED_STATES and _now - self._closed_at >= RETENTION_PERIOD:
            self._remove()
            return True

        return False


    def _close(self, status: ReservationStatus) -> None:
        self._status = status
        self._closed_at = _now


    def _remove(self) -> None:
        # also takes it out of the lists the user and room keep
        _all_reservations.remove(self)
        for owner in (self._submitter, self._room):
            for name in ("_reservations", "reservations"):
                if self in getattr(owner, name, []):
                    getattr(owner, name).remove(self)


    def _save_changes(self, start: datetime, end: datetime, room: Room) -> None:
        self._start_time = start
        self._end_time = end
        self._room = room


    def _not_allowed(self, event: str) -> None:
        print(f"{event} not allowed in {self._status.name}")


    def _notify(self, notification: str) -> None:
        print(f"[NOTIFY] {notification}: reservation {self._reservation_id}")
