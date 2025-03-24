import streamlit as st
import pandas as pd
import sqlite3
from streamlit_calendar import calendar
from logiic import extract_event_details  
from email_not2 import send_todays_event_notification

# Ensure user is logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please log in to access the event calendar.")
    st.switch_page("pages/login")  # Redirects to login page
    st.stop()

username = st.session_state["username"]
db_name = f"events_{username}.db"

def init_db():
    """Initialize database and create events table if it doesn't exist."""
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        summary TEXT, 
                        description TEXT, 
                        start_date TEXT, 
                        end_date TEXT, 
                        start_time TEXT, 
                        end_time TEXT, 
                        location TEXT)''')
        conn.commit()

init_db()  # Ensure DB is ready

def insert_event(summary, description, start_date, end_date, start_time, end_time, location):
    """Insert an event into the database."""
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO events (summary, description, start_date, end_date, start_time, end_time, location) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (summary or "No title", description or "No description", 
                   start_date or "N/A", end_date or start_date, start_time or "00:00", end_time or "23:59", 
                   location or "Unknown"))
        conn.commit()

def delete_event(event_id):
    """Delete an event by its ID."""
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()

def get_events():
    """Fetch all events from the database as a DataFrame."""
    with sqlite3.connect(db_name) as conn:
        df = pd.read_sql_query("SELECT * FROM events", conn)
    return df

st.title(f"📅 Event Calendar - Welcome {username}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.success("Logged out successfully!")
    st.rerun()

with st.sidebar:
    st.header("➕ Add New Event")
    user_input = st.text_area("Describe your event (e.g., 'Meeting on March 25 at 9 AM at Hilton')")
    
    if st.button("Add Event"):
        event_details = extract_event_details(user_input) 
        insert_event(event_details["summary"], event_details["description"], 
                     str(event_details["start_date"]), str(event_details["end_date"]), 
                     str(event_details["start_time"]), str(event_details["end_time"]), 
                     event_details["location"])
        st.success("✅ Event added successfully!")
        st.rerun()

# Display events
events_df = get_events()
if not events_df.empty:
    events = []
    for _, row in events_df.iterrows():
        start_datetime = f"{row['start_date']}T{row['start_time']}:00" if row['start_time'] else row['start_date']
        end_datetime = f"{row['end_date']}T{row['end_time']}:00" if row['end_time'] else row['end_date']

        events.append({
            "id": row["id"],
            "title": row["summary"],
            "start": start_datetime,
            "end": end_datetime,
            "description": f"{row['description']}\nLocation: {row['location']}"
        })
    
    event_clicked = calendar(events=events, options={"editable": True})
    
    if event_clicked and "event" in event_clicked:
        event_id = event_clicked["event"]["id"]
        st.sidebar.write("### Event Details")
        st.sidebar.write(f"**Summary:** {event_clicked['event']['title']}")
        st.sidebar.write(f"**Description:** {event_clicked['event']['description']}")

        if st.sidebar.button("Delete Event"):
            delete_event(event_id)
            st.success("🗑 Event deleted successfully!")
            st.rerun()

# Email Notification
st.header("📩 Event Notifications")
recipient_email = st.text_input("Enter your email to receive event reminders")

if st.button("Send Notification for Today's Events"):
    if recipient_email:
        if send_todays_event_notification(recipient_email, db_name):
            st.success(f"✅ Email sent to {recipient_email} successfully!")
        else:
            st.warning("⚠ No events scheduled for today.")
    else:
        st.warning("⚠ Please enter your email before sending.")
