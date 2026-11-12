import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "classes"))  

from datetime import datetime
from student import Student
from admin import Admin
from RoomFacilityClasses import room
import reservation
from reservation import Reservation, all_reservations

# a few things to start with
rooms = [room(1, "101", 30), room(2, "102", 50), room(3, "201", 100)]
users = [
    Student.register("Alice", "alice@umsystem.edu", "pass1"),
    Student.register("Bob", "bob@umsystem.edu", "pass2"),
    Admin.register("Admin", "admin@umsystem.edu", "admin"),
]
current_user = users[0]

HELP = """commands:
  user <id>
  create <room> <start> <end>      (times like 2026-11-20T09:00)
  edit <res_id> <field>=<value>    (fields: room, start, end)
  submit <res_id>
  approve <res_id> | reject <res_id>
  cancel <res_id>
  list
  advance <hours> | time
  quit"""

def find_room(number):
    for r in rooms:
        if r.roomNumber == number:
            return r
    return None

def find_reservation(res_id):
    for r in all_reservations:
        if r._reservation_id == int(res_id):
            return r
    return None

def show_list():
    if not all_reservations:
        print("no reservations")
    for r in all_reservations:
        print(f"{r._reservation_id}: room {r._room.roomNumber}, {r._start_time} to {r._end_time}, {r._status.name}")

def run_command(parts):
    global current_user
    cmd = parts[0]

    if cmd == "user":
        for u in users:
            if u._userId == int(parts[1]):
                current_user = u
        print(f"acting as {current_user._name} ({type(current_user).__name__})")
    elif cmd == "create":
        found = find_room(parts[1])
        if found is None:
            print("no such room")
            return
        r = Reservation(current_user, None, found, datetime.fromisoformat(parts[2]), datetime.fromisoformat(parts[3]))
        print(f"created reservation {r._reservation_id}, status {r._status.name}")
    elif cmd == "list":
        show_list()
    elif cmd == "time":
        print(reservation.get_now())
    elif cmd == "advance":
        before = {r: r._status for r in all_reservations}
        reservation.advance_time(float(parts[1]))
        print(f"time is now {reservation.get_now()}")
        for r, old in before.items():
            if r not in all_reservations:
                print(f"reservation {r._reservation_id}: {old.name} -> removed")
            elif r._status != old:
                print(f"reservation {r._reservation_id}: {old.name} -> {r._status.name}")
    elif cmd in ("edit", "submit", "approve", "reject", "cancel"):
        r = find_reservation(parts[1])
        if r is None:
            print("no such reservation")
            return
        old = r._status

        if cmd == "edit":
            field, value = parts[2].split("=")
            start, end, found = r._start_time, r._end_time, r._room
            if field == "start":
                start = datetime.fromisoformat(value)
            elif field == "end":
                end = datetime.fromisoformat(value)
            elif field == "room":
                found = find_room(value)
                if found is None:
                    print("no such room")
                    return
            else:
                print("unknown field")
                return
            r.edit(start, end, found)
        elif cmd == "submit":
            r.submit()
        elif cmd == "approve":
            r.approve(current_user)
        elif cmd == "reject":
            r.reject(current_user)
        elif cmd == "cancel":
            r.cancel()

        if r not in all_reservations:
            print(f"reservation {r._reservation_id}: {old.name} -> removed")
        else:
            print(f"reservation {r._reservation_id}: {old.name} -> {r._status.name}")
    else:
        print("unknown command, type help")

def main():
    print(f"simulated time: {reservation.get_now()}")
    print("users: 1 Alice (student), 2 Bob (student), 3 Admin")
    print("rooms: 101, 102, 201")
    print("type help for commands")

    while True:
        line = input(f"[{current_user._name}] > ").split()
        if not line:
            continue
        if line[0] == "quit":
            break
        if line[0] == "help":
            print(HELP)
            continue
        try:
            run_command(line)
        except (ValueError, IndexError) as e:
            print(f"bad input: {e}")

if __name__ == "__main__":
    main()
