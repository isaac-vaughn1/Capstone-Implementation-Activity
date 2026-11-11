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
        pass

    def edit(self, start: datetime, end: datetime, room) -> None:  # room is gonna be of type Room once you guys implement that class
        pass

    def cancel(self, reason: str) -> None:
        pass

    def approve(self, approver, comment: str) -> None:
        pass

    def reject(self, approver, comment: str) -> None:  # similar to room above, approver will be of type Admin
        pass

    def is_valid(self) -> bool:
        pass

    def check_conflicts(self) -> bool:
        pass

    def _save_changes(self) -> None:
        pass

    def _notify(self, type) -> None:
        pass
