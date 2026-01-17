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
# Run (for local debugging only)
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)