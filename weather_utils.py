import os
import re
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Islamabad"

def extract_trip_days(user_input):
    match = re.search(r"(\d+)[\s-]*day", user_input.lower())
    days = int(match.group(1)) if match else 3
    return min(days, 5)


def fetch_weather_forecast():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if "list" not in data:
            print("❌ Weather API error:", data)
            return None
        return data
    except Exception as e:
        print("❌ Weather fetch failed:", e)
        return None

def format_weather_table(data, num_days):
    if not data or "list" not in data:
        return "⚠️ Unable to fetch weather data."

    rows, seen = [], set()
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date in seen:
            continue
        seen.add(date)
        day = pd.to_datetime(date).strftime("%A")
        desc = item["weather"][0]["description"].title()
        tmin = round(item["main"]["temp_min"])
        tmax = round(item["main"]["temp_max"])
        rows.append((date, day, desc, tmin, tmax))

        if len(seen) == num_days:  
            break

    df = pd.DataFrame(rows, columns=["📅 Date", "📆 Day", "🌤️ Condition", "🌡️ Min (°C)", "🌡️ Max (°C)"])
    return df.to_markdown(index=False)


def format_weather_summary(data, num_days=3):
    if not data or "list" not in data:
        return "⚠️ Weather summary not available."

    summary, seen = [], set()
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date in seen:
            continue
        seen.add(date)
        day = pd.to_datetime(date).strftime("%A")
        desc = item["weather"][0]["description"].title()
        tmin = round(item["main"]["temp_min"])
        tmax = round(item["main"]["temp_max"])
        summary.append(f"- **{day}**: {desc}, {tmin}°C / {tmax}°C")
        if len(seen) == num_days:
            break
    return "\n".join(summary)
def generate_weather_safety_advice(data, num_days):
    if not data or "list" not in data:
        return "⚠️ Safety info unavailable."

    risks = set()
    seen = set()

    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date in seen:
            continue
        seen.add(date)

        weather = item["weather"][0]["main"].lower()

        if "storm" in weather or "thunder" in weather:
            risks.add("⚠️ Thunderstorm expected — avoid outdoor travel and stay indoors when possible.")
        elif "rain" in weather:
            risks.add("☔ Light rain expected — carry an umbrella and wear waterproof shoes.")

        if len(seen) == num_days:
            break

    if not risks:
        return "✅ All clear — no weather-related risks expected."

    return "\n".join(f"- {tip}" for tip in risks)
