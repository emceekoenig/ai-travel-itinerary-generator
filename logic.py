"""Web app for AI-generated travel itineraries"""

import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # this loads variables defined in .env into environment variables

API_KEY = os.getenv("SHECODES_API_KEY")


# City input validation
def is_valid_city(name):
    """
    Validates the city name input.
    Accepts letters (including accented), spaces, apostrophes, and hyphens.
    Requires at least 2 characters.
    Disallows single letters separated by spaces to prevent inputs like 'p aris'.
    """
    name = name.strip()
    # Check full string with allowed characters
    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]{2,}$", name):
        return False
    # Disallow single characters being separated by spaces (e.g., "p aris")
    # We check if any word in the name is a single letter
    words = name.split()
    if any(len(word) == 1 for word in words):
        return False
    return True


# Weather API Integration - display current weather data
def display_current_weather(location):
    """Get the current temperature and conditions in a location as a string"""
    api_key = API_KEY
    api_url = f"https://api.shecodes.io/weather/v1/current?query={location}&key={api_key}&units=imperial"

    # Make a request to the current weather API
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return "⏰ The request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"⛔️ Error fetching weather data: {str(e)}"

    response_data = response.json()

    # Check if 'city' key in API response to avoid KeyError
    if "city" not in response_data:
        return f"n⛔️Error: City '{location}' not found or API error on current weather."

    # Extract and display the current weather information
    city_name = response_data["city"]
    temperature = round(response_data["temperature"]["current"])
    conditions = response_data["condition"]["description"]

    return f"📍{city_name} forecast: {temperature}°F, {conditions}"


# AI API Integration - generate travel itinerary between 2 places using AI
def generate_itinerary(origin_city, destination_city, trip_length):
    """Generate a travel itinerary between 2 places using AI"""
    print(
        f"\n\n🗺️ Generating itinerary for a {trip_length}-day trip from {origin_city.capitalize()} to {destination_city.capitalize()}...\n"
    )

    api_key = API_KEY
    prompt = f"Generate a nicely formatted travel itinerary from {origin_city} to {destination_city} for {trip_length} days. Include an emoji for the Country the {destination_city} is in. Display 'Total Estimated Cost', 'Total Travel Time' and if 'Currency Exchange Needed' at the top of itinerary. Add emojis for each day to make it more readable. Include daily estimated cost. If traveling to a different country, call out if currency exchange needed and how to do this. Keep the itinerary concise."
    context = "You are a well-travelled expert Travel Agent who has 20 years of experience in vacation planning. You know the best tourist spots around the world."
    api_url = f"https://api.shecodes.io/ai/v1/generate?prompt={prompt}&context={context}&key={api_key}"

    # Make a request to the AI API
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return "⏰ The request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"⛔️ Error fetching itinerary data: {str(e)}"

    response_data = response.json()

    # SheCodes AI API: check for 'answer' or 'error' in response
    if "answer" not in response_data:
        error_message = response_data.get(
            "error",
            f"City '{origin_city}' or '{destination_city}' not found or API error.",
        )
        return f"⛔️ Error: {error_message}"

    return response_data["answer"]


# Welcome message
def welcome():
    """Welcome message"""
    return "Welcome to the AI Travel Itinerary Planner"


# Credit display
def credit():
    """Returns the credit for the app"""
    return "\n\n👩🏻‍💻 The AI Travel Itinerary Planner was built by Chelsea K. Thank you for using it 💛"


# CLI input validation and interaction loop (Run only when standalone)
if __name__ == "__main__":
    print(welcome())

    # Enhanced input validation loop with API call verification
    while True:
        # # User inputs
        # Prompt user input for 'origin' city and strip spaces
        origin = input("📍 What city does your trip start from? \n").strip()
        # Prompt user input for 'destination' city and strip spaces
        destination = input("📍 Where do you want to go? \n").strip()
        # Prompt user input for 'duration' of trip and strip spaces
        duration = input(
            "🗓️ How long is your trip? (enter number of days, e.g. 5) \n"
        ).strip()

        # Validate origin city
        if not origin:
            # Handle empty input with error message and re-prompt
            print("\n⛔️ Error: Origin city name cannot be empty. Please try again.👇\n")
            continue
        if not is_valid_city(origin):
            # Handle invalid characters in city name, and if error on current weather API, re-prompt
            print(
                "\n⛔️ Error: City names should only contain letters, spaces, apostrophes, or hyphens, and not single-letter words like 'p aris'.👇\n"
            )
            continue

        # Validate destination city
        if not destination:
            # Handle empty input with error message and re-prompt
            print(
                "\n⛔️ Error: Destination city name cannot be empty. Please try again.👇\n"
            )
            continue
        if not is_valid_city(destination):
            # Handle invalid characters in city name, and if error on current weather API, re-prompt
            print(
                "\n⛔️ Error: City names should only contain letters, spaces, apostrophes, or hyphens, and not single-letter words like 'p aris'.👇\n"
            )
            continue

        # Check that origin and destination are not the same (case-insensitive)
        if origin.lower() == destination.lower():
            print(
                "\n ⛔️ Error: Origin and Destination cities must be different. Please try again.👇\n"
            )
            continue

        # Validate duration input
        if not duration.isdigit() or not (1 <= int(duration) <= 30):
            print(
                "\n ⛔️ Error: Trip duration should be a number between 1 and 30 days.👇\n"
            )
            continue

        # Print weather fetch message only after all validation passes
        print("Trip Summary")
        print(
            f"Origin: {origin.capitalize()} → Destination: {destination.capitalize()}\nDuration: {duration} days\n"
        )

        print("Weather Forecast")
        print(
            f"\n\n☀️ Getting current weather for {origin.capitalize()} and {destination.capitalize()}..."
        )

        # Fetch weather for origin and destination
        if display_current_weather(origin) is False:
            continue
        if display_current_weather(destination) is False:
            continue

        # Generate itinerary and display credit
        print("Travel Itinerary")
        print(generate_itinerary(origin, destination, duration))
        print(credit())

        break
