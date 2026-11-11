from enum import Enum
from datetime import datetime
import itertools

_reservation_ids = itertools.count()  # so we can have auto-generated ids from 0-n

class ReservationStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending approval"
    APPROVED = "approved"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

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

    def submit(self) -> None:
        if self._status != ReservationStatus.DRAFT:
            raise ValueError("Only drafts may be submitted")
        if not self.is_valid():
            raise ValueError("Invalid reservation details")
        if self.check_conflicts():
            self._notify("Your reservation has conflicts")
            return

        self._status = ReservationStatus.DRAFT
        self._submitted_at = datetime.now()
        self._notify("Reservation submitted")

    def edit(self, start: datetime, end: datetime, room) -> None:  # room is gonna be of type Room once you guys implement that class
        if self._status not in {ReservationStatus.DRAFT, ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            raise ValueError(f"{self._status.value} reservations cannot be edited")

        if end <= start:
            raise ValueError("End time must be after start time")

        self._start_time = start
        self._end_time = end

        # probably still need to add more functionality here but am going to wait until the other classes are made

    def cancel(self, reason: str) -> None:
        self._cancel_reason = reason
        self._status = ReservationStatus.CANCELLED
        self._notify("REservation cancelled")

    def approve(self, approver, comment: str) -> None:
        if self.check_conflicts():
            raise ValueError("This room is already booked for that time : (")
        
        self._status = ReservationStatus.APPROVED
        self._review_comment = comment
        self._save_changes()
        self._notify("Reservation Approved")

    def reject(self, approver, comment: str) -> None:  # similar to room above, approver will be of type Admin
        self._status = ReservationStatus.REJECTED
        self._review_comment = comment
        self._save_changes()
        self._notify(f"Reservation rejected: {comment}")

    def is_valid(self) -> bool:
        facility = self._room._facility

        # I can edit this check pretty easy after the other classes are implemented, since this depends on specific attributes of other classes
        return self._start_time > datetime.now() and facility is not None and facility._is_active and self._room._capacity >= self._event._expected_attendance

    def check_conflicts(self) -> bool:
        return not self._room.is_available()

    # not sure if we even need this since we have no database
    def _save_changes(self) -> None:
        pass

    def _notify(self, notification) -> None:
        print(f"System notification to {self._submitter._name}: {notification}")
