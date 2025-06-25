import gradio as gr
from planner import authenticate_google_calendar, generate_gemini_itinerary
from weather_utils import (
    fetch_weather_forecast,
    format_weather_table,
    extract_trip_days,
    generate_weather_safety_advice
)
from calender_utils import write_to_calendar, check_calendar_conflicts

# 📅 Authenticate Google Calendar
calendar_service = authenticate_google_calendar()

# 🔧 Main logic
def generate_plan(user_input, start_date):
    if "islamabad" not in user_input.lower():
        return (
            "Only Islamabad is currently supported.",
            "", "", ""
        )

    num_days = extract_trip_days(user_input)

    # 🌦️ Weather Forecast
    forecast = fetch_weather_forecast()
    if not forecast:
        return (
            "⚠️ Weather API error",
            "❌ Weather unavailable",
            "Trip plan unavailable",
            "Calendar skipped"
        )

    weather_table = format_weather_table(forecast, num_days)
    safety_advice = generate_weather_safety_advice(forecast, num_days)

    # ✈️ AI Itinerary
    itinerary_text, raw_schedule = generate_gemini_itinerary(user_input, start_date)

    # 🧠 First check for conflicts BEFORE writing
    conflict_info = check_calendar_conflicts(raw_schedule, start_date, calendar_service)

    # ✅ Write to calendar if needed
    write_result = write_to_calendar(raw_schedule, start_date, calendar_service)

    # 🧾 Final result
    calendar_md = f"{conflict_info}\n\n{write_result['status']}"

    return (
        f"### Weather Table\n{weather_table}",
        f"### Safety Advisory\n{safety_advice}",
        itinerary_text,
        calendar_md
    )


# 🖼️ UI with Gradio
with gr.Blocks() as demo:
    gr.Markdown("## 🧳 Agentic AI Travel Planner – Islamabad")

    with gr.Row():
        user_input = gr.Textbox(label="✍️ Trip Query", placeholder="Plan a 3-day trip in Islamabad")
        start_date = gr.Textbox(label="📅 Start Date (YYYY-MM-DD)")

    gen_btn = gr.Button("🚀 Generate Plan")

    with gr.Tabs():
        with gr.Tab("📅 Weather Table"):
            weather_output = gr.Markdown()
        with gr.Tab("⚠️ Safety"):
            safety_output = gr.Markdown()
        with gr.Tab("📘 Itinerary"):
            itinerary_output = gr.Markdown()
        with gr.Tab("📆 Calendar"):
            calendar_output = gr.Markdown()

    gen_btn.click(
        generate_plan,
        inputs=[user_input, start_date],
        outputs=[weather_output, safety_output, itinerary_output, calendar_output]
    )

demo.launch()
