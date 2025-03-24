import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Email Configuration
SENDER_EMAIL = "quazifaraz508@gmail.com"  # Replace with your email
SENDER_PASSWORD = "noqg pzby jdct ugpa"  # Use an App Password for Gmail

# Get today's date
today_date = datetime.today().strftime("%Y-%m-%d")

# Function to fetch events scheduled for today
def get_todays_events(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT summary, description, start_date, start_time, location FROM events WHERE start_date = ?", (today_date,))
    events = c.fetchall()
    conn.close()
    return events

# Function to send email notification for today's events
def send_todays_event_notification(recipient_email, db_name):
    events = get_todays_events(db_name)
    if not events:
        return False  # No events for today

    subject = "🔔 Reminder: Your Scheduled Events Today"
    body = "Here are your scheduled events for today:\n\n"

    for event in events:
        summary, description, start_date, start_time, location = event
        body += f"📌 **{summary}**\n📅 Date: {start_date}\n⏰ Time: {start_time}\n📍 Location: {location}\n📝 {description}\n\n"

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {recipient_email} successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# Run automatically every day
if __name__ == "__main__":
    # Replace with actual user email & database
    recipient_email = "user@example.com"  # Replace with user's email
    db_name = "events_test_user.db"  # Replace with user's DB file

    send_todays_event_notification(recipient_email, db_name)
