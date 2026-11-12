from datetime import date
from reservation import ReservationStatus

class room:
    def __init__(self, roomid : int, roomNumber : int, capacity : int):
        self.roomid = roomid
        self.roomNumber = roomNumber
        self.capacity = capacity
        self.features = []
        self.reservations = []

    #Checks if room is already booked or in the booking process
    def isAvailable(self, start=None, end=None):
        if start is None or end is None:
            raise ValueError("Please Provide Valid Start And End Times To View Room Availability.")
        for res in self.reservations:
            if res._status in [ReservationStatus.PENDING_APPROVAL, ReservationStatus.APPROVED, ReservationStatus.IN_PROGRESS]:
                if start < res._end_time and end > res._start_time:
                    return False
        return True

    #Provides Daily Itinerary For Any Room On A Given Day 
    def getSchedule(self, day=date.today()):
        day_schedule = []
        for res in self.reservations:
            if res._start_time.date() == day or res._end_time.date() == day:
                day_schedule.append(res)
        return day_schedule


class facility:
    def __init__(self, facilityid : int, name : str, location : str, facilityType, isActive : bool):
        self.facilityid = facilityid
        self.name = name
        self.location = location
        self.facilityType = facilityType
        self.isActive = isActive
        self.rooms = []

    #Return number of rooms in Facility
    def getRoomCount(self):
        return len(self.rooms)

    #Allows Admin to Add Room From Facility
    def addRoom(self, room):
        self.rooms.append(room)
        room._facility = self
        print(f'Room {room.roomNumber} Successfully Added to {self.name}.')

    #Allows Admin to Remove Rooms From Facility
    def removeRoom(self, roomid):
        self.rooms = [room for room in self.rooms if room.roomid != roomid]
        print(f'Room {roomid} Successfully Removed From {self.name}')

    #Returns List of Rooms Available According to User Specifications
    def findAvailableRoom(self, start, end, minCapacity):
        avail_rooms = []
        for room in self.rooms:
            if room._capacity >= minCapacity and room.isAvailable(start, end):
                avail_rooms.append(room)
        return avail_rooms