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
    contextHtml: str
    variantAttributed: str


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
                    "current_html": "<div>A</div>",
                    "current_score": 4.3,
                    "history": []
                },

                "B": {
                    "current_html": "<div>B</div>", #TODO MUST BE DYNAMICs
                    "current_score": 3.0,
                    "history": []
                }
            }
        })
        print("insert")

        return {
            "status": "ok",
            "changingHtml": "<div>A</div>",
            "variant": "A"
        }


    # TODO: ensure user exists + store HTML (you will add this later)
    boolChoice:bool = bool( random.randint(0,1))

    if boolChoice:
        BHtml = mongodb["users"].find_one({"user_id": user_id})["variants"]["A"]["current_html"]

        return {
            "status": "ok",
            "changingHtml": BHtml,
            "variant": "A"
        }

    else:
        AHtml = mongodb["users"].find_one({"user_id": user_id})["variants"]["B"]["current_html"]
        return {
            "status": "ok",
            "changingHtml": AHtml,
            "variant": "B"
        }






def does_user_exists(user_id: str) -> bool:
    # Check if user exists
    existing = users_collection.find_one({"user_id": user_id})

    if existing:
        return True  # user already exists

    return False  # user was created now


RERENDER_SCORE = 5
# ----------------------------------------
# Logic: rewardTag
# ----------------------------------------
def rewardTag(user_id: str, reward: float, contextHtml: str, variantAttributed: str):
    """
    Store a reward value mapped to the given user.
    """
    ReRenderCheck(user_id, contextHtml)

    return {
        "status": "reward_logged",
        "user_id": user_id,
        "reward": reward
    }




def ReRenderCheck(user_id: str, contextHtml: str):

    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return False

    AScore = user["variants"]["A"]["current_score"]
    BScore = user["variants"]["B"]["current_score"]
    AHtml = user["variants"]["A"]["current_html"]
    BHtml = user["variants"]["B"]["current_html"]

    # If A is outperforming B by threshold → regenerate B
    if AScore >= BScore + RERENDER_SCORE:
        reRender(user_id, "B", contextHtml, oldHtml=BHtml)

    # If B is outperforming A by threshold → regenerate A
    if BScore >= AScore + RERENDER_SCORE:
        reRender(user_id, "A", contextHtml, oldHtml=AHtml)

    return True



def reRender(user_id: str, varianceLetter: str, contextHtml: str, oldHtml: str):
    """
    testLetter: "A" or "B"
    oldHtml: the previous HTML before updating
    """

    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "User not found"

    # Make sure testLetter is uppercase
    varianceLetter = varianceLetter.upper()

    # Safety check
    if varianceLetter not in ["A", "B"]:
        raise Exception("testLetter must be 'A' or 'B'")

    # 1. Push oldHtml into the correct variant's history
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$push": {
                f"variants.{varianceLetter}.history": oldHtml
            }
        }
    )

    # 2. Now generate NEW HTML (stubbed for now)
    new_html = AIRags(user_id, contextHtml, varianceLetter)


    # 3. Store the new HTML in current_html
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"variants.{varianceLetter}.current_html": new_html
            }
        }
    )

    print(mongodb["users"].find_one({"user_id": user_id}))

def AIRags(user_id:str, changingHtml: str, contextHtml: str, varianceLetter: str) -> str:



    #TODO AI....  HUHH UHHH I LOVE AI AND BUILDING AND ALSO AI... (randomly screens) (mutters ai)
    return f"<div>New version for {varianceLetter}</div>"



# ----------------------------------------
# Routes
# ----------------------------------------
@app.post("/tagAi")
async def tag_ai(payload: HtmlPayload):
    return aiTag(payload.user_id, payload.changingHtml, payload.contextHtml)


@app.post("/rewardTag")
async def reward_tag(payload: RewardPayload):
    return rewardTag(payload.user_id, payload.reward, payload.contextHtml, payload.variantAttributed)


# ----------------------------------------
# Run (for local debugging only)
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)