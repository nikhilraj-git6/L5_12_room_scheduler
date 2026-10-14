"""Room scheduling system with safe input and file handling."""

import json
from datetime import datetime
from pathlib import Path

reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
reservation_counter = {"next": 1}


def schedule_room(room_id, time_slot, equipment_list=None):
    """Schedule a room and record any booking conflicts."""
    if equipment_list is None:
        equipment_list = []

    if not isinstance(time_slot, str):
        raise ValueError("Time slot must be a string, such as '09-11'.")

    try:
        start, end = map(int, time_slot.split("-"))
    except ValueError as exc:
        raise ValueError("Use a time slot such as '09-11'.") from exc

    if not 0 <= start < end <= 24:
        raise ValueError("Time slot must be within 00-24 and end after start.")

    for reservation in reservations.values():
        if (reservation["room"] == room_id
                and reservation["slot"] == time_slot):
            conflicts.append(
                f"{room_id} double-booked at {time_slot}"
            )

    for equipment in equipment_list:
        if equipment not in equipment_pool:
            raise ValueError(f"Unknown equipment: {equipment}")
        if equipment_pool[equipment] <= 0:
            raise ValueError(f"No {equipment} available.")

    for equipment in equipment_list:
        equipment_pool[equipment] -= 1

    reservation_id = reservation_counter["next"]
    reservations[reservation_id] = {
        "room": room_id,
        "slot": time_slot,
        "equipment": list(equipment_list),
    }
    reservation_counter["next"] += 1

    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and restore its equipment."""
    if reservation_id not in reservations:
        print(f"Reservation {reservation_id} not found.")
        return

    reservation = reservations.pop(reservation_id)
    for equipment in reservation["equipment"]:
        equipment_pool[equipment] += 1


def slot_hours(time_slot):
    """Return the duration of a valid time slot in hours."""
    try:
        start, end = map(int, time_slot.split("-"))
    except ValueError as exc:
        raise ValueError("Use a time slot such as '09-11'.") from exc

    if not 0 <= start < end <= 24:
        raise ValueError("Invalid time slot.")

    return end - start


def export_schedule(file="schedule.json"):
    """Save reservations to a JSON file."""
    with Path(file).open("w", encoding="utf-8") as output_file:
        json.dump(reservations, output_file, indent=2)


def log_conflicts(file="conflicts.log"):
    """Write conflicts to a log file and display them."""
    with Path(file).open("a", encoding="utf-8") as output_file:
        for conflict in conflicts:
            output_file.write(f"{datetime.now()} {conflict}\n")

    with Path(file).open("r", encoding="utf-8") as input_file:
        print(input_file.read())


def main():
    """Demonstrate room scheduling features."""
    schedule_room("Board-1", "09-11")
    schedule_room("Board-1", "09-11")
    second = schedule_room("Huddle-3", "14-16")

    print(
        "Slot length for second booking:",
        slot_hours(reservations[second]["slot"]),
    )

    cancel_reservation(77)

    slot = input(
        "Slot for Board-2, like 10-12 (Enter for 10-12): "
    ) or "10-12"

    try:
        schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as error:
        print(f"Booking failed: {error}")

    export_schedule()
    log_conflicts()
    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
