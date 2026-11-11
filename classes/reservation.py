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

    def submit() -> None:
        pass

    def edit(start: datetime, end: datetime, room) -> None:  # room is gonna be of type Room once you guys implement that class
        pass

    def cancel(reason: str) -> None:
        pass

    def approve(approver, comment: str) -> None:
        pass

    def reject(approver, comment: str) -> None:  # similar to room above, approver will be of type Admin
        pass

    def is_valid() -> bool:
        pass

    def check_conflicts() -> bool:
        pass

    def _save_changes() -> None:
        pass

    def _notify(type) -> None:
        pass
