from enum import Enum
from datetime import datetime
import itertools
from admin import Admin
# from event import Event
from RoomFacilityClasses import room as Room
from user import User


_reservation_ids = itertools.count()  # so we can have auto-generated ids from 0-n
_all_reservations = []

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

    def __init__(self, submitter: User, event, room: Room, start_time, end_time, equipment_needed = None, support_needed = None) -> None:
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

        _all_reservations.append(self)


    def submit(self) -> None:
        if self._status != ReservationStatus.DRAFT:
            raise ValueError("Only drafts may be submitted")
        
        if not self.is_valid():
            raise ValueError("Invalid reservation details")
        
        if self.check_conflicts():
            self._notify("Your reservation has conflicts")
            return

        self._status = ReservationStatus.PENDING_APPROVAL
        self._submitted_at = datetime.now()
        self._notify("Reservation submitted")


    def edit(self, start: datetime, end: datetime, room: Room) -> None:
        if self._status not in {ReservationStatus.DRAFT, ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            raise ValueError(f"{self._status.value} reservations cannot be edited")

        if end <= start:
            raise ValueError("End time must be after start time")

        self._start_time = start
        self._end_time = end
        self._room = room

        # pending and approved reservations are sent back to draft stage during edits
        if self._status != ReservationStatus.DRAFT:
            self._status = ReservationStatus.DRAFT
            self._submitted_at = None
            self._review_comment = ""
            self._notify("Reservation removed, please edit and resubmit")


    def cancel(self, reason: str) -> None:
        if self._status not in {ReservationStatus.DRAFT, ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED}:
            raise ValueError(f"{self._status.value} reservations may not be cancelled")
        
        self._cancel_reason = reason
        self._status = ReservationStatus.CANCELLED
        self._notify("REservation cancelled")


    def approve(self, approver: Admin, comment: str) -> None:
        if not isinstance(approver, Admin):
            raise ValueError("Only admins may approve reservations")
        
        if self._status != ReservationStatus.PENDING_APPROVAL:
            raise ValueError("Only pending reservatoins may be approved")
        
        if self.check_conflicts():
            raise ValueError("This room is already booked for that time :-(")
        
        self._status = ReservationStatus.APPROVED
        self._review_comment = comment
        self._notify("Reservation Approved")


    def reject(self, approver: Admin, comment: str) -> None:
        if not isinstance(approver, Admin):
            raise ValueError("Only admins may reject reservations")
        
        if self._status != ReservationStatus.PENDING_APPROVAL:
            raise ValueError("Only pending reservations may be rejected")
        
        self._status = ReservationStatus.REJECTED
        self._review_comment = comment
        self._notify(f"Reservation rejected: {comment}")


    def is_valid(self) -> bool:
        return self._start_time > datetime.now() and self._room.capacity >= self._event._expected_attendance  # TODO: replace that attendance check woth the real event attribute name once implemented


    def check_conflicts(self) -> bool:
        holding = {ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED, ReservationStatus.IN_PROGRESS}

        for other in _all_reservations:
            if (other is not self and other._room is self._room and other._status in holding 
                and other._start_time < self._end_time and self._start_time < other._end_time):
                return True 

        return False


    def _notify(self, notification: str) -> None:
        print(f"System notification to {self._submitter._name}: {notification}")
