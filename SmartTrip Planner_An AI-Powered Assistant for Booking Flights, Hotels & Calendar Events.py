import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { format } from "date-fns";

export default function TripPlanner() {
  const [startDate, setStartDate] = useState("2025-07-20");
  const [tripDuration, setTripDuration] = useState(3);
  const [status, setStatus] = useState("");
  const [results, setResults] = useState(null);

  const bookTrip = async () => {
    setStatus("Booking your flight...");

    const flight = await FlightBookingAPI({
      origin: "New York",
      destination: "San Francisco",
      date: startDate,
      class: "economy",
      passengers: 1,
    });

    const checkin = startDate;
    const checkout = format(
      new Date(new Date(startDate).getTime() + (tripDuration - 1) * 24 * 60 * 60 * 1000),
      "yyyy-MM-dd"
    );

    setStatus("Booking your hotel...");
    const hotel = await HotelBookingAPI({
      city: "San Francisco",
      checkin,
      checkout,
      stars: 4,
      amenities: ["WiFi", "business center"],
    });

    setStatus("Creating calendar event...");
    const calendar = await GoogleCalendarAPI.create_event({
      title: "Business Trip to San Francisco",
      date_time_start: `${startDate}T08:00:00`,
      date_time_end: `${checkout}T20:00:00`,
      location: "San Francisco, CA",
      attendees: [],
    });

    setResults({ flight, hotel, calendar });
    setStatus("Trip booked successfully!");
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Card className="mb-4">
        <CardContent>
          <h2 className="text-xl font-bold mb-4">Book Business Trip</h2>
          <div className="mb-2">
            <Label>Start Date</Label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div className="mb-4">
            <Label>Trip Duration (days)</Label>
            <Input
              type="number"
              value={tripDuration}
              onChange={(e) => setTripDuration(Number(e.target.value))}
            />
          </div>
          <Button onClick={bookTrip}>Book My Trip</Button>
        </CardContent>
      </Card>

      {status && <p className="mb-4">{status}</p>}

      {results && (
        <Card>
          <CardContent>
            <h3 className="text-lg font-semibold">Booking Summary</h3>
            <ul className="list-disc list-inside mt-2">
              <li>Flight: {results.flight.details}</li>
              <li>Hotel: {results.hotel.details}</li>
              <li>Calendar: {results.calendar.status}</li>
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Dummy APIs
async function FlightBookingAPI({ origin, destination, date, class: cls, passengers }) {
  return new Promise((res) =>
    setTimeout(() =>
      res({
        details: `${cls} flight from ${origin} to ${destination} on ${date} for ${passengers} passenger(s)`
      }), 1000)
  );
}

async function HotelBookingAPI({ city, checkin, checkout, stars, amenities }) {
  return new Promise((res) =>
    setTimeout(() =>
      res({
        details: `${stars}-star hotel in ${city} from ${checkin} to ${checkout} with ${amenities.join(", ")}`
      }), 1000)
  );
}

const GoogleCalendarAPI = {
  create_event: async ({ title, date_time_start, date_time_end, location }) => {
    return new Promise((res) =>
      setTimeout(() =>
        res({ status: `Event '${title}' created from ${date_time_start} to ${date_time_end} at ${location}` }),
        1000
      )
    );
  },
};
