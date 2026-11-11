# need to import student class when it is made.
class StudentOrganization:
    def __init__(self, orgId: int, name: str, isRegistered: bool): 
        self._orgId = orgId
        self._name = name
        self._isRegistered = isRegistered
        self._reps = []

    def addRepresentative(self, student: Student):
        self._reps.append(student)

    def removeRepresentative(self, student: Student):
        if student in self._reps:
            self._reps.remove(student)
