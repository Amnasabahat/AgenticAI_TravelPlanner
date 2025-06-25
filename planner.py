import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# Google Calendar auth
def authenticate_google_calendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

# Gemini itinerary generator
def generate_gemini_itinerary(user_input, start_date):
    prompt = f"""
    I am planning a {user_input} trip starting from {start_date} only in Islamabad.
    Please generate a detailed itinerary for each day with timings and activities.
    Highlight each day with proper titles and make it visually appealing using markdown.and make the header bold and add day 1 and so on emojis along the header. 
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    itinerary_text = response.text

    # For now, return sample dummy schedule — replace with parser later
    sample_schedule = [
        [{"name": "Faisal Mosque", "address": "Faisal Ave"}],
        [{"name": "Daman-e-Koh", "address": "Margalla Hills"}],
        [{"name": "Lok Virsa Museum", "address": "Garden Ave"}],
    ]

    return itinerary_text, sample_schedule
