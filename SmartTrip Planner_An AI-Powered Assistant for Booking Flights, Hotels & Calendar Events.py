import streamlit as st
import datetime
import json
import sqlite3
import os

# ---- Mock API Clients ----

def FlightBookingAPI(origin, destination, date, flight_class, passengers):
    return {
        "success": True,
        "flight": {
            "origin": origin,
            "destination": destination,
            "date": date,
            "class": flight_class,
            "passengers": passengers,
            "flight_number": "UA123",
            "departure_time": f"{date}T09:00:00",
            "arrival_time": f"{date}T12:00:00",
            "booking_reference": "FLIGHT-BOOKED-001"
        }
    }

def HotelBookingAPI(city, checkin, checkout, stars, amenities):
    return {
        "success": True,
        "hotel": {
            "name": "Grand San Francisco Hotel",
            "city": city,
            "checkin": checkin,
            "checkout": checkout,
            "stars": stars,
            "amenities": amenities,
            "booking_reference": "HOTEL-BOOKED-001"
        }
    }

def GoogleCalendarAPI_create_event(title, date_time_start, date_time_end, location, attendees):
    return {
        "success": True,
        "event": {
            "title": title,
            "start": date_time_start,
            "end": date_time_end,
            "location": location,
            "attendees": attendees,
            "calendar_event_id": "CAL-EVENT-001"
        }
    }

# ---- Core Workflow Function ----

def plan_business_trip(
    origin,
    destination,
    start_date,
    trip_days,
    flight_class="Economy",
    passengers=1,
    hotel_stars=4,
    hotel_amenities=None,
    calendar_attendees=None
):
    reasoning_steps = []
    output = {}

    # Step 1: Book Flight
    reasoning_steps.append("Step 1: Book a flight.")
    flight_result = FlightBookingAPI(origin, destination, start_date, flight_class, passengers)
    output['flight_booking'] = flight_result
    if not flight_result['success']:
        reasoning_steps.append("Flight booking failed.")
        return {"reasoning": reasoning_steps, "output": output}

    # Step 2: Book Hotel
    checkin_date = start_date
    checkout_date = (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=trip_days)).strftime("%Y-%m-%d")
    reasoning_steps.append("Step 2: Book hotel.")
    hotel_result = HotelBookingAPI(destination, checkin_date, checkout_date, hotel_stars, hotel_amenities or ["WiFi", "Breakfast"])
    output['hotel_booking'] = hotel_result
    if not hotel_result['success']:
        reasoning_steps.append("Hotel booking failed.")
        return {"reasoning": reasoning_steps, "output": output}

    # Step 3: Calendar Event
    reasoning_steps.append("Step 3: Create calendar event.")
    event_title = f"Trip: {origin} to {destination}"
    departure_time = flight_result['flight']['departure_time']
    return_time = checkout_date + "T23:59:00"
    location = hotel_result['hotel']['name'] + ", " + destination
    calendar_result = GoogleCalendarAPI_create_event(event_title, departure_time, return_time, location, calendar_attendees or [])
    output['calendar_event'] = calendar_result

    if not calendar_result['success']:
        reasoning_steps.append("Calendar event failed.")
        return {"reasoning": reasoning_steps, "output": output}

    reasoning_steps.append("All steps completed successfully.")
    return {"reasoning": reasoning_steps, "output": output}

# ---- Save to JSON file and SQLite ----

def save_to_file(data, filename="trip_booking.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def save_to_db(data):
    conn = sqlite3.connect("bookings.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (flight TEXT, hotel TEXT, calendar TEXT, timestamp TEXT)''')
    c.execute("INSERT INTO bookings VALUES (?, ?, ?, datetime('now'))",
              (json.dumps(data['output'].get('flight_booking')),
               json.dumps(data['output'].get('hotel_booking')),
               json.dumps(data['output'].get('calendar_event'))))
    conn.commit()
    conn.close()

# ---- Streamlit UI ----

st.set_page_config(page_title="SmartTrip Planner", layout="centered")

st.markdown(
    """
    <h1 style='text-align: center; font-size: 2.8em;'>✈️ SmartTrip Planner</h1>
    <h4 style='text-align: center; color: gray;'>An AI-Powered Travel Assistant for Flights, Hotels & Calendar</h4>
    """,
    unsafe_allow_html=True
)

st.caption("Plan your full trip with one click — from booking flights and hotels to blocking your calendar.")

with st.form("trip_form"):
    st.markdown("### 📝 Enter Your Trip Details")
    origin = st.text_input("From", "New York")
    destination = st.text_input("To", "San Francisco")
    start_date = st.date_input("Trip Start Date", datetime.date.today())
    days = st.slider("Trip Duration (days)", 1, 10, 3)
    submit = st.form_submit_button("🛫 Plan My Trip")

if submit:
    result = plan_business_trip(
        origin=origin,
        destination=destination,
        start_date=start_date.strftime("%Y-%m-%d"),
        trip_days=days
    )

    st.markdown("## 📋 Reasoning Trace")
    for step in result['reasoning']:
        st.success(step)

    st.markdown("## ✈️ Flight Details")
    flight = result['output']['flight_booking']['flight']
    st.write(f"**From:** {flight['origin']} → **To:** {flight['destination']}")
    st.write(f"**Date:** {flight['date']}")
    st.write(f"**Flight No:** {flight['flight_number']}")
    st.write(f"**Departure:** {flight['departure_time']} → **Arrival:** {flight['arrival_time']}")
    st.write(f"**Class:** {flight['class']} | **Passengers:** {flight['passengers']}")

    st.markdown("## 🏨 Hotel Details")
    hotel = result['output']['hotel_booking']['hotel']
    st.write(f"**Hotel:** {hotel['name']}, {hotel['city']}")
    st.write(f"**Check-in:** {hotel['checkin']} → **Check-out:** {hotel['checkout']}")
    st.write(f"**Stars:** {hotel['stars']} | **Amenities:** {', '.join(hotel['amenities'])}")

    st.markdown("## 📅 Calendar Event")
    event = result['output']['calendar_event']['event']
    st.write(f"**Event Title:** {event['title']}")
    st.write(f"**Start:** {event['start']} → **End:** {event['end']}")
    st.write(f"**Location:** {event['location']}")

    save_to_file(result)
    save_to_db(result)
    st.success("✅ Trip details saved to file and database.")
