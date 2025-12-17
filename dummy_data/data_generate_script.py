import json
from datetime import datetime, timedelta
import random

USER_ID = "c2aef4919d844f45a02c25a0d342d984"
START_DATE = datetime(2025, 10, 1)
DAYS = 60

custom_trackers = [
  {
    "id": 1,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Reading",
    "data_type": "number",
    "unit": "pages",
    "enum_options": None,
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  },
  {
    "id": 2,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Journal Note",
    "data_type": "text",
    "unit": None,
    "enum_options": None,
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  },
  {
    "id": 3,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Listened to Music",
    "data_type": "boolean",
    "unit": None,
    "enum_options": None,
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  },
  {
    "id": 4,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Movie / Screen Time",
    "data_type": "time",
    "unit": "hh:mm",
    "enum_options": None,
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  },
  {
    "id": 5,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Job Prep",
    "data_type": "enum",
    "unit": None,
    "enum_options": "interview,OA,DSA,system design",
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  },
  {
    "id": 6,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Workout Minutes",
    "data_type": "number",
    "unit": "minutes",
    "enum_options": None,
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  },
  {
    "id": 7,
    "user_id": "c2aef4919d844f45a02c25a0d342d984",
    "name": "Meditated",
    "data_type": "boolean",
    "unit": None,
    "enum_options": None,
    "is_active": 1,
    "created_at": "2025-10-01 10:00:00",
    "modified_at": "2025-10-01 10:00:00"
  }
]


diary = []
personal = []
work = []
custom_data = []
user_day = []
custom_tracker_ids = [1, 2, 3]
job_prep_values = ["interview", "OA", "DSA", "system design"]

id_counter = 1

for i in range(DAYS):
    date = (START_DATE + timedelta(days=i)).strftime("%Y-%m-%d")
    ts = f"{date} 22:00:00"

    diary_id = i + 1
    personal_id = i + 1
    work_id = i + 1
    day_id = i+1

    diary.append({
        "id": diary_id,
        "user_id": USER_ID,
        "date": date,
        "short_note": random.choice(["Good day", "Okay day", "Tired", "Productive"]),
        "long_entry": "Auto generated entry.",
        "attachments": "()",
        "created_at": ts,
        "modified_at": ts
    })

    personal.append({
        "id": personal_id,
        "user_id": USER_ID,
        "date": date,
        "wakeup_time": f"07:{random.randint(10,59)}",
        "sleep_time": f"23:{random.randint(10,59)}",
        "screen_time": f"0{random.randint(3,8)}:{random.randint(0,59):02}",
        "water_intake": round(random.uniform(1.5, 3.5), 1),
        "exercise": random.randint(0,3),
        "outgoing": random.randint(0,3),
        "mood": random.randint(1,5),
        "created_at": ts,
        "modified_at": ts
    })

    work.append({
        "id": work_id,
        "user_id": USER_ID,
        "date": date,
        "commute_time": "09:00",
        "return_time": "18:00",
        "break_time": "00:30",
        "given_work": random.randint(5, 10),
        "completed_work": random.randint(3, 10),
        "is_off": 1 if random.random() < 0.15 else 0,
        "workload": random.randint(0, 5),
        "created_at": ts,
        "modified_at": ts
    })

    custom_ids_for_day = []
    
    for tracker in custom_trackers:
        custom_id = id_counter
        custom_ids_for_day.append(custom_id)
        t_id = tracker["id"]
        value = ""
        if tracker['data_type'] == "number":
            value = str(random.randint(1, 100))
        elif tracker['data_type'] == "text":
            value = random.choice(["kya maulm", "chalne do", "i have nbo idea what i m doing"])
        elif tracker['data_type'] == "boolean":
            value = random.choice(("True", "False"))
        elif tracker['data_type'] == "time":
            value = f"{random.randint(0,24)}:{random.randint(10,59)}"
        elif tracker["data_type"] == "enum":
            value = random.choice(tracker["enum_options"].split(","))
        
        custom_data.append({
            "id": custom_id,
            "user_id": USER_ID,
            "tracker_id": t_id,
            "date": date,
            "value": value,
            "created_at": ts,
            "modified_at": ts
        })
        id_counter += 1

     # ---- USER DAY (the missing piece) ----
    user_day.append({
        "id": day_id,
        "user_id": USER_ID,
        "date": date,
        "diary_entry_id": diary_id,
        "personal_trackers_id": personal_id,
        "work_trackers_id": work_id,
        "custom_tracker_data_list_ids": str(tuple(custom_ids_for_day)),
        "created_at": ts,
        "modified_at": ts
    })

with open("diary_entry.json", "w") as f:
    json.dump(diary, f, indent=2)

with open("personal_trackers_data.json", "w") as f:
    json.dump(personal, f, indent=2)

with open("work_trackers_data.json", "w") as f:
    json.dump(work, f, indent=2)

with open("custom_trackers_data.json", "w") as f:
    json.dump(custom_data, f, indent=2)

with open("user_day.json", "w") as f:
    json.dump(user_day, f, indent=2)


print("✅ Dummy data generated!")
