"""Web app for AI-generated travel itineraries"""

import markdown
from flask import Flask, render_template, request
from logic import is_valid_city, display_current_weather, generate_itinerary


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    itinerary = None
    itinerary_html = None
    weather = []
    error = None
    origin = ""
    destination = ""
    duration = ""

    if request.method == "POST":
        origin = request.form.get("origin", "").strip()
        destination = request.form.get("destination", "").strip()
        duration = request.form.get("duration", "").strip()
        # ---- Enhanced input validation ----
        if not origin:
            error = "Origin city cannot be empty."
        elif not destination:
            error = "Destination city cannot be empty."
        elif not is_valid_city(origin):
            error = "Origin city name is invalid."
        elif not is_valid_city(destination):
            error = "Destination city name is invalid."
        elif origin.lower() == destination.lower():
            error = "Origin and destination must be different."
        elif not duration.isdigit() or not (1 <= int(duration) <= 30):
            error = "Trip duration must be a number between 1 and 30."
        else:
            # ---- Get weather for both cities ----
            weather.append(display_current_weather(origin))
            weather.append(display_current_weather(destination))

            # ---- Generate itinerary ----
            itinerary = generate_itinerary(origin, destination, int(duration))

    # Convert Markdown to HTML here, after POST logic, before rendering template
    if itinerary:
        itinerary_html = markdown.markdown(itinerary)
    else:
        itinerary_html = None

    # Join weather details for display
    weather_summary = "<br/>".join(weather) if weather else None
    # Render the HTML template. Pass any variables to be displayed in HTML.
    return render_template(
        "index.html",
        itinerary=itinerary_html,
        weather=weather_summary,
        error=error,
        origin=origin,
        destination=destination,
        duration=duration,
    )


if __name__ == "__main__":
    app.run(debug=True)
