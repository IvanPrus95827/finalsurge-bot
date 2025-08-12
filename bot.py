import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz 
import random
import os
from dotenv import load_dotenv
from engine import generate_answer
import threading

load_dotenv()
if os.getenv('USER_EMAIL') is None or os.getenv('USER_PASSWORD') is None:
    print("Error: USER_EMAIL and USER_PASSWORD must be set in the .env file")
    exit()
date_format = "%Y-%m-%dT%H:%M:%S"

try:
    ireland_tz = pytz.timezone('Europe/Dublin') # For pytz
except pytz.UnknownTimeZoneError:
    print("Error: 'Europe/Dublin' timezone not found. Please ensure pytz is installed and up-to-date.")
    exit()

session = requests.Session()
session.timeout = 20

# Inbox listener configuration/state
INBOX_LISTENER_ENABLED = os.getenv('INBOX_LISTENER_ENABLED', 'true').lower() == 'true'
INBOX_POLL_INTERVAL_SECONDS = int(os.getenv('INBOX_POLL_INTERVAL_SECONDS', '120'))
TOKEN_TTL_SECONDS = int(os.getenv('TOKEN_TTL_SECONDS', '3300'))  # ~55 minutes

_auth_token = None
_token_acquired_at = None
_last_inbox_after_time = datetime.utcnow()
# _last_inbox_after_time = None

complete_messages = [
    {
        'subject': 'Well done on the training',
        'body': 'Well done $NAME on the training. How are you finding it all?'
    },
    {
        'subject': 'Nice work on Final Surge this week! 💪👏',
        'body': 'You’ve been super consistent, and it shows. Keep it up—every session adds up.\nRest up and get ready for another strong week ahead! 💪👏'
    },
    {
        'subject': 'Fantastic job this week in Final Surge!',
        'body': "Well done on your training in Final Surge this week! Great consistency and effort across the sessions. Keep it going — you're building strong momentum."
    }
]
incomplete_messages = [
    {
        'subject': 'Check in',
        'body': 'Hi $NAME, just checking last week wondering how you are finding training?'
    }
]
status_engine = False

def get_next_saturday():
    global ireland_tz
    """
    Calculates and returns the date of the next Saturday.
    """
    today = datetime.now(ireland_tz).date()  # Get today's date
    
    # Calculate days until next Saturday (Saturday is weekday 5, Monday is 0)
    # If today is Saturday (5), (5 - 5) % 7 = 0, so 7 days are added to get *next* Saturday.
    # If today is Sunday (6), (5 - 6) % 7 = -1 % 7 = 6, so 6 days are added.
    # If today is Friday (4), (5 - 4) % 7 = 1, so 1 day is added.
    days_until_saturday = (5 - today.weekday() + 7) % 7
    
    # If today is already Saturday, we want the *next* Saturday, so add 7 days.
    if days_until_saturday == 0:
        days_until_saturday = 7

    next_saturday = today + timedelta(days=days_until_saturday)
    return next_saturday

def get_access_token(email, password):
    try:
        url = "https://beta.finalsurge.com/api/login"  # Replace with the actual URL
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "deviceManufacturer": "",
            "deviceModel": "Netscape",
            "deviceOperatingSystem": "Win32",
            "deviceUniqueIdentifier": "",
            "email": email,
            "password": password
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("data").get("token")
        else:
            print(f"Failed to get access token: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out while getting access token.")
    except Exception as e:
        print(f"An error occurred while getting access token: {e}")
    return None

def get_athlete_data(token):
    try:
        url = "https://beta.finalsurge.com/api/TeamAthleteList"  # Replace with the actual URL
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=UTF-8"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            team_user_list = {}
            for team in response.json().get('data'):
                team_name = team['name']
                team_user_list[team_name] = []

                for member in team['athletes']:
                    team_user_list[team_name].append({
                        'user_key': member['user_key'], 
                        'first_name': member['first_name'], 
                        'email': member['email'], 
                        'last_name': member['last_name']
                    })
            return team_user_list
        else:
            print(f"Failed to get athlete data: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out while getting athlete data.")
    except Exception as e:
        print(f"An error occurred while getting athlete data: {e}")
    return None

def get_plan_data(token, userKey, startDate, endDate):
    try:
        url = f'https://beta.finalsurge.com/api/WorkoutList?scope=USER&scopekey={userKey}&startdate={startDate}&enddate={endDate}&ishistory=false&completedonly=false'
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=UTF-8"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data")
        else:
            print(f"Failed to get plan data: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out while getting the plan data.")
    except Exception as e:
        print(f"An error occurred while getting plan data: {e}")
    return None

def get_incomplete_workouts(workouts):
    try:
        workout_results = {}
        for workout in workouts:
            activities = workout.get("Activities")[0]
            if workout.get("workout_completion") == 0:
                if (activities.get('planned_duration') == None and
                    activities.get('planned_amount') == None and
                    activities.get('planned_amount_type') == None and
                    activities.get('planned_pace_low') == None and
                    activities.get('planned_pace_low_type') == None and
                    activities.get('planned_pace_high') == None and
                    activities.get('planned_pace_high_type') == None and
                    activities.get('planned_pace_display') == None and
                    activities.get('planned_pace_display_type') == None
                ):
                    continue
            
            workout_date_only = str(datetime.strptime(workout.get("workout_date"), date_format).date())
            workout_results[workout_date_only] = workout_results.get(workout_date_only, [])
            workout_results[workout_date_only].append({
                "activities_name": activities.get("activity_type_name"),
                "is_complete": workout.get("workout_completion"),
            })
            incomplete_workouts = []
            for date, activities in workout_results.items():
                is_complete = 0
                for activity in activities:
                    if activity['is_complete'] == 1:
                        is_complete = 1
                        break
                if is_complete == 0:
                    incomplete_workouts.append({
                        "date": date,
                        "activities": activities
                    })
        return incomplete_workouts
    except requests.exceptions.Timeout:
        print("Request timed out while getting incomplete workouts.")
    except Exception as e:
        print("An error occurred while getting incomplete workouts: ", e)
    return None

def send_message_to_athlete(token, user_key, subject, body):
    try:
        url = "https://beta.finalsurge.com/api/MailboxMessageSend"  # Replace with the actual URL
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=utf-8"
        }
        payload = {
            "body": body,
            "subject": subject,
            "to_club_keys": "",
            "to_user_keys": user_key
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            # print("Message sent successfully.")
            return True
        else:
            print(f"Failed to send message: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out while sending message to athlete.")
    except Exception as e:
        print(f"An error occurred while sending message to athlete: {e}")
    return False

def bot_engine(start_date, end_date):
    global ireland_tz, complete_messages, incomplete_messages
    index_complete = random.randint(0, len(complete_messages) - 1)
    index_incomplete = random.randint(0, len(incomplete_messages) - 1)

    print("-----------------------------------------------------------------------------------------------------------------")
    print(f"📅 Period Checked: {start_date.date():%B %d} to {end_date.date():%B %d} (as of {datetime.now(ireland_tz):%I:%M %p, %B %d})")
    total_athlete_cnt = no_plan_athlete_cnt = complete_athlete_cnt = incomplete_athlete_cnt = 0
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    email = os.getenv('USER_EMAIL')
    password = os.getenv('USER_PASSWORD')

    token = get_access_token(email, password)
    if token != None:
        athlete_data = get_athlete_data(token)

        if athlete_data != None:
            for team, members in athlete_data.items():
                # print(f"Team: {team}")
                for member in members:
                    total_athlete_cnt = total_athlete_cnt + 1
                    # print(f"  - {member['first_name']} {member['last_name']} ({member['email']})")
                    user_key = member['user_key']
                    workouts = get_plan_data(token, user_key, start_date, end_date)
                    if workouts != None and len(workouts) > 0:
                        incomplete_workouts = get_incomplete_workouts(workouts)
                        subject = ""
                        body = ""
                        if len(incomplete_workouts) > 0:
                            subject = incomplete_messages[index_incomplete]['subject']
                            body = incomplete_messages[index_incomplete]['body']
                            incomplete_athlete_cnt = incomplete_athlete_cnt + 1
                        else:
                            subject = complete_messages[index_complete]['subject']
                            complete_athlete_cnt = complete_athlete_cnt + 1
                            body = complete_messages[index_complete]['body']
                        body = body.replace('$NAME', member['first_name'])
                        send_message_to_athlete(token, user_key, subject, body)
                    else:
                        no_plan_athlete_cnt = no_plan_athlete_cnt + 1
            print(f'''
🏋️ Athlete Status:
    ✅ Completed Workouts: {complete_athlete_cnt}
    🔄 Incomplete Workouts: {incomplete_athlete_cnt}
    ⏳ No Workout Plan: {no_plan_athlete_cnt}
''')
            print(f"⏰ Next Check: 6 PM, Saturday, {get_next_saturday():%B %d}")
            return True
    print("❌ Failed to check the period.")
    return False
    
# ===== Inbox listener helpers =====

def _ensure_access_token() -> str:
    """
    Return a valid access token, caching it for TOKEN_TTL_SECONDS.
    """
    global _auth_token, _token_acquired_at
    try:
        now = time.time()
        if _auth_token and _token_acquired_at and (now - _token_acquired_at) < TOKEN_TTL_SECONDS:
            return _auth_token
        email = os.getenv('USER_EMAIL')
        password = os.getenv('USER_PASSWORD')
        token = get_access_token(email, password)
        if token:
            _auth_token = token
            _token_acquired_at = now
            return token
    except Exception as e:
        print(f"Error ensuring access token: {e}")
    return None


def fetch_inbox_messages(after_time_iso: str = None):
    """
    Call MailboxMessageList to fetch inbox messages.
    AfterTime should be ISO string (UTC). If None, API returns recent messages.
    """
    token = _ensure_access_token()
    if not token:
        return None
    base_url = "https://beta.finalsurge.com/api/MailboxMessageList"
    params = {
        "SentItems": "false"
    }
    if after_time_iso:
        params["BeforeTime"] = after_time_iso
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json;charset=UTF-8"
    }
    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=20)
        if resp.status_code == 200:
            return resp.json().get("data")
        else:
            print(f"Failed to fetch inbox messages: {resp.status_code} - {resp.text[:200]}")
    except requests.exceptions.Timeout:
        print("Request timed out while fetching inbox messages.")
    except Exception as e:
        print(f"Error fetching inbox messages: {e}")
    return None


def process_inbox_messages(messages):
    """
    Minimal processing: print and return latest message timestamp for cursor advancement.
    Expected each message to include fields like: id, subject, body, from_user_name, date_sent, etc.
    """
    global _auth_token
    if not messages:
        return None
    latest_ts = None
    for m in messages:
        try:
            sender = m['from'].get('name') or 'Unknown'
            subject = m.get('subject', '')
            user_key = m['from'].get('key')
            body_preview = m.get('text', '') or ''
            sent_at = m.get('timestamp')
            print("-----------------------------------------------------------------------------------------------------------------")
            print(f"📥 Inbox: {sender} | {subject} | {sent_at}\n   message: {body_preview}")
            result = generate_answer(subject, body_preview)
            if result is None:
                continue
            if result.get('status') == 'yes':
                print(f" 💬 Reply: {result.get('answer')}")
                send_message_to_athlete(_auth_token, user_key, 'RE: ' + subject, result.get('answer'))
            else:
                print(" 💬 No Reply!")
                
            # Track latest timestamp
            if sent_at:
                try:
                    # Keep as ISO string; compare lexicographically if ISO format
                    if (latest_ts is None) or (str(sent_at) > str(latest_ts)):
                        latest_ts = str(sent_at)
                except Exception:
                    pass
        except Exception as e:
            print(f"Error processing message: {e}")
            continue
    return latest_ts


def inbox_poll_tick():
    """
    One poll tick: fetch messages after the saved cursor and process them.
    Updates the global _last_inbox_after_time to the latest timestamp.
    """
    global _last_inbox_after_time
    try:
        messages = fetch_inbox_messages(_last_inbox_after_time)
        if messages is None:
            return
        latest = process_inbox_messages(messages)
        if latest:
            # Advance cursor slightly to avoid re-reading the last message
            _last_inbox_after_time = latest
    except Exception as e:
        print(f"Error during inbox poll tick: {e}")


def run_bot_engine():
    global status_engine, ireland_tz
    try:
        now_ireland = datetime.now(ireland_tz)
        start_of_week = now_ireland - timedelta(days=now_ireland.isoweekday())

        status_engine = not bot_engine(start_of_week, now_ireland)
    except Exception as e:
        status_engine = True

def check_time():
    global ireland_tz, status_engine
    now = datetime.now(ireland_tz)
    if now.weekday() == 5 and now.hour == 18 and now.minute == 0:  # Saturday 6:00 PM
        status_engine = True
    if status_engine == True:
        status_engine = False
        if now.weekday() == 5:
            threading.Thread(target=run_bot_engine).start()

# Schedule the check every minute
schedule.every(1).minutes.do(check_time)

# Inbox polling schedule
if INBOX_LISTENER_ENABLED:
    print('Inbox listener enabled')
    schedule.every(INBOX_POLL_INTERVAL_SECONDS).seconds.do(inbox_poll_tick)

print("Scheduler started. Waiting for Saturday 6 PM (Ireland time)...")
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        pass