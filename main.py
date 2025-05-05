import streamlit as st
from datetime import datetime, timedelta
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Load credentials from Streamlit secrets
client_config = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
REDIRECT_URI = st.secrets["REDIRECT_URI"]

def authenticate():
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return flow, auth_url

def get_calendar_service(flow, code):
    flow.fetch_token(code=code)
    creds = flow.credentials
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(service):
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=end,
        singleEvents=True, orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def parse_events(events):
    busy_times = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        busy_times.append((start, end))
    return busy_times

def find_free_slots(your_busy, bf_busy):
    full_day = [(datetime.now().replace(hour=9, minute=0), datetime.now().replace(hour=21, minute=0))]
    your_busy = [(datetime.fromisoformat(s), datetime.fromisoformat(e)) for s, e in your_busy]
    bf_busy = [(datetime.fromisoformat(s), datetime.fromisoformat(e)) for s, e in bf_busy]

    all_busy = sorted(your_busy + bf_busy, key=lambda x: x[0])
    free_slots = []
    current = full_day[0][0]

    for start, end in all_busy:
        if start > current:
            free_slots.append((current, start))
        current = max(current, end)

    if current < full_day[0][1]:
        free_slots.append((current, full_day[0][1]))

    return free_slots

# -------- Streamlit UI --------
st.title("💞 Schedule Syncer")
st.write("Find mutual free time between you and your boyfriend!")

query_params = st.query_params
code = query_params.get("code", [None])[0]

if code:
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)
    service = build("calendar", "v3", credentials=flow.credentials)

    events = get_events(service)
    your_busy = parse_events(events)

    # Dummy boyfriend calendar
    bf_busy = [
        ('2025-05-03T10:00:00', '2025-05-03T11:30:00'),
        ('2025-05-03T15:00:00', '2025-05-03T17:00:00')
    ]

    free_slots = find_free_slots(your_busy, bf_busy)

    st.subheader("💡 Mutual Free Time Today")
    for start, end in free_slots:
        st.write(f"🕒 {start.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')}")
else:
    flow, auth_url = authenticate()
    st.write("🔐 Click below to sign in and connect your Google Calendar:")
    st.markdown(f"[Authorize with Google]({auth_url})")
