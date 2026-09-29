"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice teamwork and compete in soccer matches",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Improve shooting, dribbling, and game strategy",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and visual arts techniques",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ella@mergington.edu", "grace@mergington.edu"]
    },
    "Drama Workshop": {
        "description": "Develop acting skills and perform short scenes",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["zoe@mergington.edu", "lucas@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 12,
        "participants": ["ethan@mergington.edu", "isabella@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 16,
        "participants": ["james@mergington.edu", "harper@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


def _normalize_email(email: str) -> str:
    return email.strip().casefold()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    normalized_email = _normalize_email(email)

    # Validate student is not already signed up
    if any(_normalize_email(participant) == normalized_email for participant in activity["participants"]):
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student
    activity["participants"].append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def remove_from_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = _normalize_email(email)
    participant_email = next(
        (
            participant
            for participant in activity["participants"]
            if _normalize_email(participant) == normalized_email
        ),
        None,
    )
    if participant_email is None:
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    activity["participants"].remove(participant_email)
    return {"message": f"Removed {normalized_email} from {activity_name}"}
