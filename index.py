from flask import Flask, render_template, request
from dataclasses import dataclass
from typing import Dict, List, Optional

app = Flask(__name__)  # templates/ and static/ are in the same folder (api/)


# ---------------- DATA MODELS ---------------- #

@dataclass
class Trip:
    trip_id: int
    source: str
    destination: str
    date: str
    time: str
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
    status: str


# ---------------- CORE SYSTEM ---------------- #

class ReservationSystem:
    def __init__(self):
        self.trips: Dict[int, Trip] = {}
        self.bookings: Dict[int, Booking] = {}
        self.next_trip_id = 1
        self.next_booking_id = 1
        self._load_sample_data()

    def _add_trip(self, source, destination, date, time, seats, price):
        trip = Trip(
            trip_id=self.next_trip_id,
            source=source,
            destination=destination,
            date=date,
            time=time,
            total_seats=seats,
            seats_available=seats,
            price_per_seat=price,
        )
        self.trips[trip.trip_id] = trip
        self.next_trip_id += 1

    def _load_sample_data(self):
        self._add_trip("Bhopal", "Indore", "2025-12-10", "09:00", 40, 450)
        self._add_trip("Bhopal", "Indore", "2025-12-10", "18:00", 40, 500)
        self._add_trip("Bhopal", "Delhi", "2025-12-11", "20:00", 50, 1200)
        self._add_trip("Indore", "Bhopal", "2025-12-11", "07:30", 40, 450)
        self._add_trip("Bhopal", "Mumbai", "2025-12-12", "21:00", 50, 1800)

    def list_all_trips(self) -> List[Trip]:
        return list(self.trips.values())

    def book_ticket(self, name, age, trip_id, seats) -> Optional[Booking]:
        trip = self.trips.get(int(trip_id))
        if trip is None:
            return None
        seats = int(seats)
        if seats <= 0 or trip.seats_available < seats:
            return None

        fare = seats * trip.price_per_seat
        booking = Booking(
            booking_id=self.next_booking_id,
            passenger_name=name,
            passenger_age=int(age),
            trip_id=trip.trip_id,
            num_seats=seats,
            total_fare=fare,
            status="CONFIRMED",
        )
        self.bookings[booking.booking_id] = booking
        self.next_booking_id += 1
        trip.seats_available -= seats
        return booking

    def list_all_bookings(self) -> List[Booking]:
        return list(self.bookings.values())

    def cancel_booking(self, booking_id) -> bool:
        booking = self.bookings.get(int(booking_id))
        if not booking or booking.status == "CANCELLED":
            return False
        trip = self.trips.get(booking.trip_id)
        if trip:
            trip.seats_available += booking.num_seats
        booking.status = "CANCELLED"
        return True


system = ReservationSystem()


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/trips")
def trips():
    return render_template("trips.html", trips=system.list_all_trips())

@app.route("/book", methods=["GET", "POST"])
def book():
    booking = None
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        trip_id = request.form["trip_id"]
        seats = request.form["seats"]
        booking = system.book_ticket(name, age, trip_id, seats)

    return render_template("book.html", booking=booking, trips=system.list_all_trips())

@app.route("/bookings")
def bookings():
    return render_template("bookings.html", bookings=system.list_all_bookings())

@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    status = None
    if request.method == "POST":
        booking_id = request.form["booking_id"]
        status = system.cancel_booking(booking_id)
    return render_template("cancel.html", status=status)


# No handler() function needed – Vercel uses the `app` variable automatically.
