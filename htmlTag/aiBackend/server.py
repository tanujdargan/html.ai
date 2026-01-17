from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import random

# ----------------------------------------
# FastAPI App + CORS
# ----------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all for now (hackathon)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# MongoDB
# ----------------------------------------
client = MongoClient("mongodb://mongo:27017/")  # works inside Docker
mongodb = client["html_ai"]

users_collection = mongodb["users"]  # collection


users_collection.insert_one({
            "user_id": "sultan",
            "variants": {
                "A": {
                    "current_html": "<div>A</div>",
                    "current_score": 4.3,
                    "history": []
                },

                "B": {
                    "current_html": "<div>B</div>",
                    "current_score": 3.0,
                    "history": []
                }
            }
        })
# ----------------------------------------
# Payload Models
# ----------------------------------------
class HtmlPayload(BaseModel):
    user_id: str
    changingHtml: str
    contextHtml: str


class RewardPayload(BaseModel):
    user_id: str
    reward: float


# ----------------------------------------
# Logic: aiTag
# ----------------------------------------
def aiTag(user_id: str, changingHtml: str, contextHtml: str):
    """
    1. Ensure user exists
    2. Store HTML snapshot
    3. Call ABai() and return its response

    """

    if not does_user_exists(user_id):


        users_collection.insert_one({
            "user_id": user_id,
            "variants": {
                "A": {
                    "current_html": changingHtml,
                    "current_score": 4.3,
                    "history": []
                },

                "B": {
                    "current_html": changingHtml, #TODO MUST BE DYNAMICs
                    "current_score": 3.0,
                    "history": []
                }
            }
        })
        print("insert")


        return {
            "status": "ok",
            "user_id": user_id,
            "changingHtml": changingHtml,
        }

    # TODO: ensure user exists + store HTML (you will add this later)
    boolChoice:bool = bool( random.randint(0,1))

    if boolChoice:
        return_html = mongodb["users"].find_one({"user_id": user_id})["variants"]["A"]["current_html"]


    else:
        return_html = mongodb["users"].find_one({"user_id": user_id})["variants"]["B"]["current_html"]


    return {
        "status": "ok",
        "changingHtml": return_html,
    }


    return ABai(user_id, changingHtml, contextHtml)


def ABai(user_id: str, changingHtml: str, contextHtml: str):
    """
    Temporary stub AI engine.
    For now: return a 200 response containing the inputs.
    """
    '''
    we need 
    
    '''

    boolChoice: bool = bool(random.randint(0, 1))

    return {
        "status": "ok",
        "user_id": user_id,
        "changingHtml": changingHtml,
        "contextHtml": contextHtml,
    }

def choseHtmltoUse(user_id: str, changingHtml: str, contextHtml: str) -> str:

    if users_collection.find_one({"user_id": user_id}) is None:

        aORb = random.randint(0, 2)
    return ""


def rederingNewHt():
    pass



def does_user_exists(user_id: str) -> bool:
    # Check if user exists
    existing = users_collection.find_one({"user_id": user_id})

    if existing:
        return True  # user already exists

    # Insert new user

    return False  # user was created now


# ----------------------------------------
# Logic: rewardTag
# ----------------------------------------

RERENDER_SCORE = 5
def rewardTag(user_id: str, reward: float):
    """
    Store a reward value mapped to the given user.
    """


    return {
        "status": "reward_logged",
        "user_id": user_id,
        "reward": reward
    }

def reRender(user_id, testLetter, contextHtml, oldHtml) -> str:
    mongodb["users"].insert_one({"user_id": user_id})







def ShouldWeReRender(user_id: str, changingHtml: str, contextHtml: str) -> bool:

    AScore = mongodb["users"].find_one({"user_id": user_id})["variants"]["A"]["current_html"]
    BScore = mongodb["users"].find_one({"user_id": user_id})["variants"]["B"]["current_html"]

    if AScore > BScore + RERENDER_SCORE:
        reRender(user_id, "A", contextHtml, AScore)






# ----------------------------------------
# Routes
# ----------------------------------------
@app.post("/tagAi")
async def tag_ai(payload: HtmlPayload):
    return aiTag(payload.user_id, payload.changingHtml, payload.contextHtml)


@app.post("/rewardTag")
async def reward_tag(payload: RewardPayload):
    return rewardTag(payload.user_id, payload.reward)


# ----------------------------------------
# Dashboard API Endpoints
# ----------------------------------------
@app.get("/")
def root():
    """Health check"""
    return {
        "status": "running",
        "service": "html.ai - A/B Testing Engine",
        "version": "1.0.0",
        "mongodb": "connected" if client else "disconnected"
    }


@app.get("/api/users/all")
async def get_all_users():
    """
    Get all users with their session data for dashboard
    """
    try:
        users = list(users_collection.find({}))
        
        # Get events and rewards (if collections exist)
        events = list(mongodb["events"].find({})) if "events" in mongodb.list_collection_names() else []
        rewards = list(mongodb["rewards"].find({})) if "rewards" in mongodb.list_collection_names() else []
        
        # Convert MongoDB _id to string
        for user in users:
            user["_id"] = str(user["_id"])
        for event in events:
            event["_id"] = str(event["_id"])
        for reward in rewards:
            reward["_id"] = str(reward["_id"])
        
        return {
            "users": users,
            "events": events,
            "rewards": rewards,
            "total_users": len(users),
            "total_events": len(events),
            "total_rewards": len(rewards)
        }
    except Exception as e:
        print(f"Error fetching users: {e}")
        return {
            "users": [],
            "events": [],
            "rewards": [],
            "total_users": 0,
            "total_events": 0,
            "total_rewards": 0,
            "error": str(e)
        }


@app.get("/api/user/{user_id}/journey")
async def get_user_journey(user_id: str):
    """
    Get detailed journey for a specific user
    Shows variants A/B with history and scores
    """
    try:
        user = users_collection.find_one({"user_id": user_id})
        
        if not user:
            return {
                "error": "User not found",
                "user_id": user_id
            }
        
        # Convert _id
        user["_id"] = str(user["_id"])
        
        # Extract variants
        variants = user.get("variants", {})
        variant_a = variants.get("A", {})
        variant_b = variants.get("B", {})
        
        # Build events from variant history
        events = []
        for variant_name in ["A", "B"]:
            variant = variants.get(variant_name, {})
            history = variant.get("history", [])
            for item in history:
                events.append({
                    "event_name": f"variant_{variant_name}_updated",
                    "variant": variant_name,
                    "html": item.get("html", ""),
                    "score": item.get("score", 0),
                    "timestamp": item.get("timestamp", "")
                })
        
        # Sort events by timestamp
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "user_id": user_id,
            "user": user,
            "variants": variants,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "events": events,
            "current_winner": "A" if variant_a.get("current_score", 0) > variant_b.get("current_score", 0) else "B"
        }
    except Exception as e:
        print(f"Error fetching user journey: {e}")
        return {
            "error": str(e),
            "user_id": user_id
        }


@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """
    Get aggregated analytics for the dashboard
    """
    try:
        users = list(users_collection.find({}))
        
        # Count active sessions
        active_sessions = sum(1 for u in users if u.get("last_session"))
        
        # Get variant statistics
        variant_a_users = sum(1 for u in users if u.get("variants", {}).get("A"))
        variant_b_users = sum(1 for u in users if u.get("variants", {}).get("B"))
        
        # Calculate average scores
        a_scores = [u.get("variants", {}).get("A", {}).get("current_score", 0) for u in users if u.get("variants", {}).get("A")]
        b_scores = [u.get("variants", {}).get("B", {}).get("current_score", 0) for u in users if u.get("variants", {}).get("B")]
        
        avg_a_score = sum(a_scores) / len(a_scores) if a_scores else 0
        avg_b_score = sum(b_scores) / len(b_scores) if b_scores else 0
        
        return {
            "total_users": len(users),
            "active_sessions": active_sessions,
            "variant_a": {
                "users": variant_a_users,
                "avg_score": round(avg_a_score, 2)
            },
            "variant_b": {
                "users": variant_b_users,
                "avg_score": round(avg_b_score, 2)
            },
            "winner": "A" if avg_a_score > avg_b_score else "B" if avg_b_score > avg_a_score else "Tie"
        }
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return {
            "error": str(e),
            "total_users": 0,
            "active_sessions": 0
        }


# ----------------------------------------
# Run (for local debugging only)
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)