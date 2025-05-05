import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="🗓️ Schedule Syncer")

st.title("💖 Schedule Syncer")
st.write("Find mutual free time between you and your boyfriend!")

# Dummy "busy" events: [(start_datetime, end_datetime)]
your_busy = [
    (datetime(2025, 5, 6, 9), datetime(2025, 5, 6, 10)),
    (datetime(2025, 5, 6, 12), datetime(2025, 5, 6, 13, 30)),
    (datetime(2025, 5, 6, 15), datetime(2025, 5, 6, 16)),
]

bf_busy = [
    (datetime(2025, 5, 6, 10), datetime(2025, 5, 6, 11)),
    (datetime(2025, 5, 6, 13), datetime(2025, 5, 6, 14)),
    (datetime(2025, 5, 6, 16), datetime(2025, 5, 6, 17)),
]

def find_free_slots(yours, his, start, end):
    all_busy = sorted(yours + his, key=lambda x: x[0])
    free_slots = []
    current = start

    for b_start, b_end in all_busy:
        if current < b_start:
            free_slots.append((current, b_start))
        current = max(current, b_end)

    if current < end:
        free_slots.append((current, end))

    return free_slots

day_start = datetime(2025, 5, 6, 9)
day_end = datetime(2025, 5, 6, 18)

free_slots = find_free_slots(your_busy, bf_busy, day_start, day_end)

st.subheader("✅ Common Free Time:")
if free_slots:
    for start, end in free_slots:
        st.write(f"🕒 {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
else:
    st.error("No common free time today! 😢")
