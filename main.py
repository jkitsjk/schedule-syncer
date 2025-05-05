import streamlit as st
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

st.set_page_config(page_title="Schedule Syncer")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

client_config = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
REDIRECT_URI = st.secrets["REDIRECT_URI"]

# Auth flow
query_params = st.query_params
code = query_params.get("code", [None])[0]

if code:
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=st.secrets["REDIRECT_URI"])
    flow.fetch_token(code=code)
    credentials = flow.credentials
    service = build('calendar', 'v3', credentials=credentials)

    now = datetime.utcnow().isoformat() + "Z"
    end = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    events = service.events().list(calendarId='primary', timeMin=now, timeMax=end, singleEvents=True, orderBy='startTime').execute()
    
    st.success("✅ Calendar connected!")
    st.write("Your events today:")
    for event in events.get('items', []):
        start = event['start'].get('dateTime', event['start'].get('date'))
        st.write(f"• {start}: {event['summary']}")
else:
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=st.secrets["REDIRECT_URI"])
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.write("🔐 Click below to connect your Google Calendar:")
    st.markdown(f"[Connect Google Calendar]({auth_url})")
