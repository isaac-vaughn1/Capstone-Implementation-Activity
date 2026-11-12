from enum import Enum
from datetime import datetime, timedelta
import itertools
from admin import Admin

_reservation_ids = itertools.count()  # so we can have auto-generated ids from 0-n

_now = datetime.now().replace(microsecond=0)  # simulated clock, only moves with advance_time()
all_reservations = []

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

# the composite states from the diagram
CLOSED_STATES = {ReservationStatus.COMPLETED, ReservationStatus.REJECTED, ReservationStatus.CANCELLED, ReservationStatus.EXPIRED}
HOLDS_SLOT = {ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED, ReservationStatus.IN_PROGRESS}

def get_now() -> datetime:
    return _now

def advance_time(hours: float) -> None:
    global _now
    _now += timedelta(hours=hours)

    # keep going until nothing changes so one big jump can go through several states
    changed = True
    while changed:
        changed = False
        for reservation in list(all_reservations):
            if reservation._check_time():
                changed = True

class Reservation:

    def __init__(self, submitter, event, room, start_time, end_time, equipment_needed = None, support_needed = None) -> None:  # submitter will be a User, event will be an Event, and room will be a Room after those classes get made
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

        all_reservations.append(self)

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

    def edit(self, start: datetime, end: datetime, room) -> None:  # room is gonna be of type Room once you guys implement that class
        if self._status not in {ReservationStatus.DRAFT, ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            self._not_allowed("edit")
            return

        if end <= start:
            raise ValueError("End time must be after start time")

        self._save_changes(start, end, room)

        # editing after it was submitted pulls it back to a draft, which frees the time slot
        if self._status != ReservationStatus.DRAFT:
            self._status = ReservationStatus.DRAFT
            self._submitted_at = None
            self._reminder_sent = False
            self._notify("WITHDRAWN")

    def cancel(self, reason: str = "") -> None:
        if self._status == ReservationStatus.DRAFT:
            all_reservations.remove(self)
            return
        if self._status not in {ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            self._not_allowed("cancel")
            return

        self._cancel_reason = reason
        self._close(ReservationStatus.CANCELLED)
        self._notify("CANCELLATION")

    def approve(self, approver, comment: str = "") -> None:
        if self._status != ReservationStatus.PENDING_APPROVAL:
            self._not_allowed("approve")
            return
        if not isinstance(approver, Admin):
            print("Only an admin can approve reservations")
            return

        self._status = ReservationStatus.APPROVED
        self._review_comment = comment
        self._notify("CONFIRMATION")

    def reject(self, approver, comment: str = "") -> None:  # similar to room above, approver will be of type Admin
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
        # the room is the facility for now, will need to change this once the facility classes are linked up
        return self._room is not None and self._start_time < self._end_time and self._start_time > _now

    def check_conflicts(self) -> bool:
        for other in all_reservations:
            if other is self or other._status not in HOLDS_SLOT:
                continue
            if other._room is self._room and other._start_time < self._end_time and self._start_time < other._end_time:
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
            all_reservations.remove(self)
            return True

        return False

    def _close(self, status) -> None:
        self._status = status
        self._closed_at = _now

    def _save_changes(self, start, end, room) -> None:
        self._start_time = start
        self._end_time = end
        self._room = room

    def _not_allowed(self, event) -> None:
        print(f"{event} not allowed in {self._status.name}")

    def _notify(self, notification) -> None:
        print(f"[NOTIFY] {notification}: reservation {self._reservation_id}")
