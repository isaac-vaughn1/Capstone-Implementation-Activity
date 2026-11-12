class room:
    def __init__(self, roomid, roomNumber, capacity, features=None):
        self.roomid = roomid
        self.roomNumber = roomNumber
        self.capacity = capacity
        self.features = list(features) if features is not None else []

    def isAvailable(self, start, end):
        #if reserved  between start and end return 0
        #else return 1
        pass

    def getSchedule(self, day):
        #return all reservations for the day
        pass


class facility:
    def __init__(self, facilityid, name, location, facilityType, isActive):
        self.facilityid = facilityid
        self.name = name
        self.location = location
        self.facilityType = facilityType
        self.isActive = isActive

    def getRoomCount(self):
        #return number of rooms in facility
        pass

    def addRoom(self, room):
        #add room to facility
        #send confirmation message
        pass

    def removeRoom(self, roomid):
        #remove room
        #send confirmation message
        pass

    def findAvailableRoom(self, start, end, minCapacity):
        #return list of available rooms in facility between start and end and capacity >= minCapacity
        pass