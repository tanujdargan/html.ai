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
# ----------------------------------------
# Payload Models
# ----------------------------------------
class HtmlPayload(BaseModel):
    user_id: str
    html: str


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

    if does_user_exists(user_id):
        return {
            "status": "ok",
            "user_id": user_id,
            "changingHtml": changingHtml,
        }

    # TODO: ensure user exists + store HTML (you will add this later)

    return ABai(user_id, changingHtml, contextHtml)


def ABai(user_id: str, changingHtml: str, contextHtml: str):
    """
    Temporary stub AI engine.
    For now: return a 200 response containing the inputs.
    """
    '''
    we need 
    
    '''





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




def does_user_exists(user_id: str):
    # Check if user exists
    existing = users_collection.find_one({"user_id": user_id})

    if existing:
        return True  # user already exists

    # Insert new user
    users_collection.insert_one({
        "user_id": user_id,
        "html_history": [],

    })

    return False  # user was created now


# ----------------------------------------
# Logic: rewardTag
# ----------------------------------------
def rewardTag(user_id: str, reward: float):
    """
    Store a reward value mapped to the given user.
    """
    scores.insert_one({
        "user_id": user_id,
        "reward": reward
    })

    return {
        "status": "reward_logged",
        "user_id": user_id,
        "reward": reward
    }


# ----------------------------------------
# Routes
# ----------------------------------------
@app.post("/tagAi")
async def tag_ai(payload: HtmlPayload):
    return aiTag(payload.user_id, payload.html)


@app.post("/rewardTag")
async def reward_tag(payload: RewardPayload):
    return rewardTag(payload.user_id, payload.reward)


# ----------------------------------------
# Run (for local debugging only)
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)