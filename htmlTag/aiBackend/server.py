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
# Analytics Dashboard Endpoint
# ----------------------------------------
@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    """
    Dashboard endpoint - shows variant performance and system status
    """
    try:
        # Get basic counts
        total_users = mongodb["users"].count_documents({})
        total_events = mongodb.get_collection("events", create=True) if "events" in mongodb.list_collection_names() else None
        total_variants = mongodb.get_collection("variants", create=True) if "variants" in mongodb.list_collection_names() else None
        
        total_events_count = total_events.count_documents({}) if total_events else 0
        total_variants_count = total_variants.count_documents({}) if total_variants else 0
        
        # Get variant stats (if available)
        variant_stats = []
        identity_distribution = {}
        
        if total_variants:
            try:
                # Aggregate variant performance
                pipeline = [
                    {
                        "$group": {
                            "_id": {
                                "variant_id": "$variant_id",
                                "identity_state": "$identity_state"
                            },
                            "total_shown": {"$sum": 1},
                            "conversions": {
                                "$sum": {"$cond": ["$converted", 1, 0]}
                            }
                        }
                    }
                ]
                
                results = list(total_variants.aggregate(pipeline))
                
                for result in results:
                    total = result["total_shown"]
                    conversions = result["conversions"]
                    conversion_rate = conversions / total if total > 0 else 0.0
                    
                    variant_stats.append({
                        "variant_id": result["_id"]["variant_id"],
                        "identity_state": result["_id"]["identity_state"],
                        "total_shown": total,
                        "conversions": conversions,
                        "conversion_rate": conversion_rate
                    })
                    
                    # Track identity distribution
                    identity = result["_id"]["identity_state"]
                    if identity:
                        identity_distribution[identity] = identity_distribution.get(identity, 0) + total
            except Exception as e:
                print(f"[Dashboard] Error aggregating variants: {e}")
        
        # Check if multi-agent system is available
        multi_agent_enabled = workflow is not None and AGENTS_AVAILABLE
        
        return {
            "status": "ok",
            "total_users": total_users,
            "total_events": total_events_count,
            "total_variants": total_variants_count,
            "multi_agent_enabled": multi_agent_enabled,
            "variant_stats": variant_stats,
            "identity_distribution": identity_distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[Dashboard] Error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "total_users": 0,
            "total_events": 0,
            "total_variants": 0,
            "multi_agent_enabled": False
        }


@app.get("/api/analytics/recent-logs")
async def get_recent_logs():
    """
    Get recent agent communication logs
    """
    try:
        # Get recent sessions with audit logs
        recent_users = list(mongodb["users"].find().sort("_id", -1).limit(10))
        
        logs = []
        for user in recent_users:
            if "last_session" in user and "audit_log" in user["last_session"]:
                audit_log = user["last_session"]["audit_log"]
                for entry in audit_log:
                    # Parse agent log entries
                    if ":" in entry:
                        agent, message = entry.split(":", 1)
                        logs.append({
                            "timestamp": user.get("last_updated", datetime.utcnow()).isoformat() if "last_updated" in user else datetime.utcnow().isoformat(),
                            "agent": agent.strip(),
                            "message": message.strip()
                        })
        
        return logs[:50]  # Return last 50 log entries
        
    except Exception as e:
        print(f"[Recent Logs] Error: {e}")
        return []


# ----------------------------------------
# Run (for local debugging only)
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)