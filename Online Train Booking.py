"""
Online Ticket Reservation System
Console-based mini project for Software Engineering course.

Features:
- View all available trips
- Search trips by source, destination and date
- Book tickets
- View all bookings
- Cancel a booking

Author: (your name)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# ====== DATA MODELS ======

@dataclass
class Trip:
    trip_id: int
    source: str
    destination: str
    date: str        # Simple string "YYYY-MM-DD" for demo
    time: str        # "HH:MM"
    total_seats: int
    seats_available: int
    price_per_seat: float


@dataclass
class Booking:
    booking_id: int
    passenger_name: str
    passenger_age: int
    trip_id: int
    num_seats: int
    total_fare: float
    status: str      # "CONFIRMED" or "CANCELLED"


# ====== CORE SYSTEM CLASS ======

class ReservationSystem:
    def __init__(self):
        self.trips: Dict[int, Trip] = {}
        self.bookings: Dict[int, Booking] = {}
        self.next_trip_id = 1
        self.next_booking_id = 1
        self._load_sample_data()

    # ---------- Trip management ----------

    def _add_trip(
        self,
        source: str,
        destination: str,
        date: str,
        time: str,
        total_seats: int,
        price_per_seat: float,
    ) -> Trip:
        trip = Trip(
            trip_id=self.next_trip_id,
            source=source,
            destination=destination,
            date=date,
            time=time,
            total_seats=total_seats,
            seats_available=total_seats,
            price_per_seat=price_per_seat,
        )
        self.trips[trip.trip_id] = trip
        self.next_trip_id += 1
        return trip

    def _load_sample_data(self):
        """
        Preload some trips so the system is usable immediately.
        In a real system, this would come from a database.
        """
        self._add_trip("Bhopal", "Indore", "2025-12-10", "09:00", 40, 450.0)
        self._add_trip("Bhopal", "Indore", "2025-12-10", "18:00", 40, 500.0)
        self._add_trip("Bhopal", "Delhi", "2025-12-11", "20:00", 50, 1200.0)
        self._add_trip("Indore", "Bhopal", "2025-12-11", "07:30", 40, 450.0)
        self._add_trip("Bhopal", "Mumbai", "2025-12-12", "21:00", 50, 1800.0)

    # ---------- Search operations ----------

    def list_all_trips(self) -> List[Trip]:
        return list(self.trips.values())

    def search_trips(self, source: str, destination: str, date: str) -> List[Trip]:
        result = []
        for trip in self.trips.values():
            if (
                trip.source.lower() == source.lower()
                and trip.destination.lower() == destination.lower()
                and trip.date == date
            ):
                result.append(trip)
        return result

    # ---------- Booking operations ----------

    def book_ticket(
        self,
        passenger_name: str,
        passenger_age: int,
        trip_id: int,
        num_seats: int,
    ) -> Optional[Booking]:
        trip = self.trips.get(trip_id)
        if trip is None:
            print("Invalid trip ID.")
            return None

        if num_seats <= 0:
            print("Number of seats must be at least 1.")
            return None

        if trip.seats_available < num_seats:
            print(
                f"Only {trip.seats_available} seats available on this trip. "
                f"Requested: {num_seats}"
            )
            return None

        total_fare = num_seats * trip.price_per_seat

        booking = Booking(
            booking_id=self.next_booking_id,
            passenger_name=passenger_name,
            passenger_age=passenger_age,
            trip_id=trip_id,
            num_seats=num_seats,
            total_fare=total_fare,
            status="CONFIRMED",
        )

        self.bookings[booking.booking_id] = booking
        self.next_booking_id += 1

        # Update seat availability
        trip.seats_available -= num_seats

        return booking

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        return self.bookings.get(booking_id)

    def cancel_booking(self, booking_id: int) -> bool:
        booking = self.bookings.get(booking_id)
        if booking is None:
            print("Invalid booking ID.")
            return False

        if booking.status == "CANCELLED":
            print("Booking is already cancelled.")
            return False

        # Free seats back to the trip
        trip = self.trips.get(booking.trip_id)
        if trip:
            trip.seats_available += booking.num_seats

        booking.status = "CANCELLED"
        return True

    def list_all_bookings(self) -> List[Booking]:
        return list(self.bookings.values())


# ====== HELPER DISPLAY FUNCTIONS ======

def print_trip(trip: Trip):
    print(
        f"Trip ID: {trip.trip_id} | {trip.source} -> {trip.destination} "
        f"| Date: {trip.date} Time: {trip.time} "
        f"| Price/seat: {trip.price_per_seat} "
        f"| Seats available: {trip.seats_available}/{trip.total_seats}"
    )


def print_booking(booking: Booking, system: ReservationSystem):
    trip = system.trips.get(booking.trip_id)
    trip_info = (
        f"{trip.source} -> {trip.destination} on {trip.date} at {trip.time}"
        if trip
        else "Unknown trip"
    )

    print(
        f"Booking ID: {booking.booking_id} | Passenger: {booking.passenger_name} "
        f"({booking.passenger_age}) | Trip: {trip_info} | Seats: {booking.num_seats} "
        f"| Total Fare: {booking.total_fare} | Status: {booking.status}"
    )


# ====== CONSOLE MENU INTERFACE ======

def main_menu():
    system = ReservationSystem()

    while True:
        print("\n========== ONLINE TICKET RESERVATION SYSTEM ==========")
        print("1. View all available trips")
        print("2. Search trips")
        print("3. Book ticket")
        print("4. View all bookings")
        print("5. Cancel booking")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            trips = system.list_all_trips()
            if not trips:
                print("No trips available.")
            else:
                print("\n---- Available Trips ----")
                for t in trips:
                    print_trip(t)

        elif choice == "2":
            print("\n---- Search Trips ----")
            src = input("Enter source city: ").strip()
            dest = input("Enter destination city: ").strip()
            date = input("Enter date (YYYY-MM-DD): ").strip()

            results = system.search_trips(src, dest, date)
            if not results:
                print("No matching trips found.")
            else:
                print("\nMatching trips:")
                for t in results:
                    print_trip(t)

        elif choice == "3":
            print("\n---- Book Ticket ----")
            name = input("Passenger name: ").strip()
            try:
                age = int(input("Passenger age: ").strip())
            except ValueError:
                print("Invalid age.")
                continue

            try:
                trip_id = int(input("Enter Trip ID to book: ").strip())
                num_seats = int(input("Number of seats: ").strip())
            except ValueError:
                print("Trip ID and number of seats must be integers.")
                continue

            booking = system.book_ticket(name, age, trip_id, num_seats)
            if booking:
                print("\nBooking successful! Your ticket details:")
                print_booking(booking, system)

        elif choice == "4":
            print("\n---- All Bookings ----")
            bookings = system.list_all_bookings()
            if not bookings:
                print("No bookings yet.")
            else:
                for b in bookings:
                    print_booking(b, system)

        elif choice == "5":
            print("\n---- Cancel Booking ----")
            try:
                booking_id = int(input("Enter Booking ID: ").strip())
            except ValueError:
                print("Booking ID must be an integer.")
                continue

            success = system.cancel_booking(booking_id)
            if success:
                print("Booking cancelled successfully.")

        elif choice == "6":
            print("Thank you for using the Online Ticket Reservation System.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main_menu()