from datetime import datetime, timedelta

# ✅ 1. Write events to Google Calendar
def write_to_calendar(schedule, start_date, service):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        for day_offset, day_events in enumerate(schedule):
            for event in day_events:
                event_date = start + timedelta(days=day_offset)

                # Use actual start and end time from event if available
                start_time_str = event.get("start_time", "10:00")
                end_time_str = event.get("end_time", "12:00")

                start_time = datetime.strptime(f"{event_date.date()} {start_time_str}", "%Y-%m-%d %H:%M")
                end_time = datetime.strptime(f"{event_date.date()} {end_time_str}", "%Y-%m-%d %H:%M")

                # Check if an event with same name and start time already exists
                existing = service.events().list(
                    calendarId="primary",
                    timeMin=start_time.isoformat() + "Z",
                    timeMax=end_time.isoformat() + "Z",
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()

                already_exists = any(
                    e.get("summary", "").strip().lower() == event["name"].strip().lower()
                    for e in existing.get("items", [])
                )

                if already_exists:
                    continue  # Skip duplicate

                event_body = {
                    "summary": event["name"],
                    "location": event["address"],
                    "start": {"dateTime": start_time.isoformat(),"timeZone": "Asia/Karachi"},
                    "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Karachi"},
                }

                service.events().insert(calendarId="primary", body=event_body).execute()

        return {"status": "✅ Events synced to calendar."}

    except Exception as e:
        print("Calendar Error:", e)
        return {"status": "❌ Calendar sync failed."}




def check_calendar_conflicts(schedule, start_date, service):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=len(schedule))

        # Fetch existing events in the calendar within the trip dates
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        existing_events = events_result.get("items", [])
        if not existing_events:
            return "✅ No calendar conflicts detected during your trip dates."

        # Extract all trip events to avoid marking them as conflicts
        trip_event_set = set()
        for day_offset, day_events in enumerate(schedule):
            for event in day_events:
                date = (start + timedelta(days=day_offset)).date()
                time = event.get("start_time", "10:00")
                key = f"{date} {time}|{event['name'].strip().lower()}"
                trip_event_set.add(key)

        # Now build conflict list
        seen = set()
        conflict_texts = []

        for event in existing_events:
            summary = event.get("summary", "No Title").strip().lower()
            start_time_raw = event["start"].get("dateTime", event["start"].get("date"))

            try:
                dt_obj = datetime.fromisoformat(start_time_raw)
                dt_str = dt_obj.strftime("%Y-%m-%d at %H:%M")
                date_key = f"{dt_obj.date()} {dt_obj.strftime('%H:%M')}|{summary}"
            except:
                dt_str = start_time_raw
                date_key = f"{dt_str}|{summary}"

            if date_key in trip_event_set or date_key in seen:
                continue  # Skip trip-generated or duplicate events

            seen.add(date_key)
            conflict_texts.append(f"📅 {dt_str} → {summary.title()}")

        if conflict_texts:
            bullet_list = "\n".join([f"- {line}" for line in conflict_texts])
            return f"⚠️ You already have other events scheduled:\n\n{bullet_list}"
        else:
            return "✅ No conflicting events in your calendar during the trip."


    except Exception as e:
        print("Calendar Conflict Check Error:", e)
        return "❌ Failed to check calendar conflicts."
