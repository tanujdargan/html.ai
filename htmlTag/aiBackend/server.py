from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import random
from openai import OpenAI
import os
from datetime import datetime

from fastapi import BackgroundTasks


RERENDER_SCORE = 1
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
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
mongo_client = MongoClient("mongodb://mongo:27017/")  # works inside Docker
mongodb = mongo_client["html_ai"]

users_collection = mongodb["users"]  # collection



# ----------------------------------------
# Payload Models
# ----------------------------------------
class HtmlPayload(BaseModel):
    user_id: str
    changingHtml: str
    contextHtml: str
    component_id: str | None = None   # NEW FIELD


class RewardPayload(BaseModel):
    user_id: str
    reward: float
    contextHtml: str
    variantAttributed: str
    component_ids: list[str] = []   # ✅ ARRAY NOW


# ----------------------------------------
# Logic: aiTag
# ----------------------------------------
def aiTag(user_id: str, changingHtml: str, contextHtml: str, component_id: str):
    """
    1. Ensure user exists
    2. Store HTML snapshot
    3. Call ABai() and return its response

    """

    if not does_user_exists(user_id):

        users_collection.insert_one({
            "user_id": user_id,
            "components": {
                component_id: {
                    "A": {
                        "current_html": changingHtml,
                        "current_score": 3,
                        "number_of_trials": 10,
                        "history": []
                    },
                    "B": {
                        "current_html": changingHtml,
                        "current_score": 3,
                        "number_of_trials": 10,
                        "history": []
                    }
                }
            }
        })


        # 2. Now that user exists → generate variant B using RAG
        new_b_html = AIRags(user_id, contextHtml, "B", "A", component_id)

        # 3. Save the newly generated B HTML back to MongoDB (WITH COMPONENT SUPPORT)
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {f"components.{component_id}.B.current_html": new_b_html}}
        )



        return {
            "status": "ok:new-user",
            "changingHtml": changingHtml,
            "variant": "A"
        }

    user = mongodb["users"].find_one({"user_id": user_id})
    component = user["components"].get(component_id)

    # NEW: If user exists but this component doesn't → initialize it
    if not component:
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"components.{component_id}": {
                        "A": {
                            "current_html": changingHtml,
                            "current_score": 3,
                            "number_of_trials": 10,
                            "history": []
                        },
                        "B": {
                            "current_html": changingHtml,
                            "current_score": 3,
                            "number_of_trials": 10,
                            "history": []
                        }
                    }
                }
            }
        )

        # Generate B for this new component
        new_b_html = AIRags(user_id, contextHtml, "B", "A", component_id)

        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {f"components.{component_id}.B.current_html": new_b_html}}
        )

        return {
            "status": "ok:new-component",
            "changingHtml": changingHtml,
            "variant": "A"
        }

    # TODO: ensure user exists + store HTML (you will add this later)
    # Randomly choose A or B
    boolChoice: bool = bool(random.randint(0, 1))

    user = mongodb["users"].find_one({"user_id": user_id})
    component = user["components"].get(component_id)

    if not component:
        return {"status": "error", "msg": f"Component '{component_id}' not found"}

    if boolChoice:
        AHtml = component["A"]["current_html"]
        return {
            "status": "ok",
            "changingHtml": AHtml,
            "variant": "A"
        }
    else:
        BHtml = component["B"]["current_html"]
        return {
            "status": "ok",
            "changingHtml": BHtml,
            "variant": "B"
        }






def does_user_exists(user_id: str) -> bool:
    # Check if user exists
    existing = users_collection.find_one({"user_id": user_id})

    if existing:
        return True  # user already exists

    return False  # user was created now



# ----------------------------------------
# Logic: rewardTag
# ----------------------------------------
def rewardTag(user_id: str, reward: float, contextHtml: str, variantAttributed: str, component_id: str):
    """
    Store a reward value mapped to the given user.
    """
    ReRenderCheck(user_id, contextHtml,component_id)
    implementScore(user_id, variantAttributed, reward, component_id)



def implementScore(user_id: str, variant: str, reward: float, component_id: str):
    variant = variant.upper()

    # Fetch user
    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "User not found"

    # Ensure component exists
    component = user.get("components", {}).get(component_id)
    if not component:
        return f"Component '{component_id}' not found"

    # Ensure variant exists
    if variant not in component:
        return f"Variant '{variant}' not found in component '{component_id}'"

    variant_data = component[variant]

    old_score = variant_data["current_score"]
    old_trials = variant_data["number_of_trials"]

    # Compute new average score
    new_trials = old_trials + 1
    new_score = (old_score * old_trials + reward) / new_trials

    # Update MongoDB *inside that specific component path*
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"components.{component_id}.{variant}.current_score": new_score,
                f"components.{component_id}.{variant}.number_of_trials": new_trials
            }
        }
    )

    print(f"⭐ Updated score for user {user_id} → component {component_id} → variant {variant}: {new_score:.3f}")


def ReRenderCheck(user_id: str, contextHtml: str, component_id: str):

    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return False

    component = user.get("components", {}).get(component_id)
    if not component:
        print(f"⚠️ Component '{component_id}' not found for rerender check.")
        return False

    # Extract scores + html inside THIS component
    AScore = component["A"]["current_score"]
    BScore = component["B"]["current_score"]
    AHtml = component["A"]["current_html"]
    BHtml = component["B"]["current_html"]

    # If A is outperforming B by threshold → regenerate B
    if AScore >= BScore + RERENDER_SCORE:
        reRender(
            user_id,
            "B",
            "A",
            contextHtml=contextHtml,
            oldHtml=BHtml,
            component_id=component_id   # ✅ PASSED NOW
        )

    # If B is outperforming A by threshold → regenerate A
    if BScore >= AScore + RERENDER_SCORE:
        reRender(
            user_id,
            "A",
            "B",
            contextHtml=contextHtml,
            oldHtml=AHtml,
            component_id=component_id   # ✅ PASSED NOW
        )

    return True



def reRender(
    user_id: str,
    VariantLetter: str,
    opposingVariantLetter: str,
    contextHtml: str,
    oldHtml: str,
    component_id: str
):
    """
    Re-render a losing variant (A or B) inside a specific component.
    """

    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "User not found"

    VariantLetter = VariantLetter.upper()
    opposingVariantLetter = opposingVariantLetter.upper()

    if VariantLetter not in ["A", "B"]:
        raise Exception("VariantLetter must be 'A' or 'B'")

    # Component block
    component = user.get("components", {}).get(component_id)
    if not component:
        raise Exception( f"Component '{component_id}' not found")

    # 1️⃣ Push OLD HTML into this component's history with timestamp + score
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$push": {
                f"components.{component_id}.{VariantLetter}.history": {
                    "html": oldHtml,
                    "score_before_reset": component[VariantLetter]["current_score"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
        }
    )

    # 2️⃣ Generate NEW variant HTML via OpenAI RAG pipeline
    new_html = AIRags(
        user_id=user_id,
        contextHtml=contextHtml,
        varianceLetter=VariantLetter,
        opposingVariantLetter=opposingVariantLetter,
        component_id=component_id      # 🔥 YOU MUST PASS THIS
    )

    # 3️⃣ Store NEW HTML into this component's variant
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"components.{component_id}.{VariantLetter}.current_html": new_html
            }
        }
    )

    print(f"🔄 Re-rendered variant {VariantLetter} for component {component_id}")

    # 4️⃣ Reset that component's scores (not global)
    reset_scores_to_midpoint(user_id, component_id)
    return None


def reset_scores_to_midpoint(user_id: str, component_id: str):
    user = users_collection.find_one({"user_id": user_id})

    if not user:
        raise Exception ("⚠️ User not found for midpoint reset.")


    component = user.get("components", {}).get(component_id)
    if not component:
        raise Exception (f"⚠️ Component '{component_id}' not found for midpoint reset.")


    A_score = component["A"]["current_score"]
    B_score = component["B"]["current_score"]

    new_score = (A_score + B_score) / 2

    users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"components.{component_id}.A.current_score": new_score,
                f"components.{component_id}.B.current_score": new_score,
                f"components.{component_id}.A.number_of_trials": 0,
                f"components.{component_id}.B.number_of_trials": 0
            }
        }
    )

    print(f"🔄 Reset scores for component '{component_id}' → midpoint = {new_score:.4f}")



def AIRags(
    user_id: str,
    contextHtml: str,
    varianceLetter: str,
    opposingVariantLetter: str,
    component_id: str,
) -> str:
    """
    Regenerate the HTML for the losing variant using:
    - Current variant HTML that needs updating
    - Opposing variant's HTML (the winning one)
    - Context HTML (surrounding structure)
    """

    print("RAG RAN!!!")

    # Fetch user
    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "<div>Error: user not found</div>"

    # NEW: navigate into components → selected component → variants A/B
    component = user["components"].get(component_id)
    if not component:
        return f"<div>Error: component '{component_id}' not found</div>"

    # Losing variant HTML
    losing_html = component[varianceLetter]["current_html"]

    # Winning variant block
    winning_variant = component[opposingVariantLetter]
    winning_html = winning_variant["current_html"]
    winning_score = winning_variant["current_score"]

    # -------------------------
    # 🔥 Prompt for OpenAI
    # -------------------------
    prompt = f"""
You are updating variant {varianceLetter} for an A/B testing system.
The goal is to make **small improvements** based on the winning variant {opposingVariantLetter}.

### Winning Variant ({opposingVariantLetter})
HTML:
{winning_html}

### Losing Variant ({varianceLetter})
Current HTML:
{losing_html}

### Context HTML
This is the larger page structure:
{contextHtml}

### Your Task
Generate a improved HTML version for variant {varianceLetter}.
DO NOT drastically change layout. Make subtle UX / visual / clarity improvements to cause more clicks.
Return ONLY raw HTML — no explanations.
"""

    # -------------------------
    # 🔥 Call OpenAI
    # -------------------------
    response = client.responses.create(
        model="gpt-5.2",
        input=prompt
    )

    ai_changed_html = response.output_text.strip()

    # -------------------------
    # Return the new HTML
    # (DO NOT save score here — reRender() will handle saving)
    # -------------------------
    print("ai_changed_html: ", ai_changed_html)
    return ai_changed_html


# ----------------------------------------
# Routes
# ----------------------------------------
@app.post("/tagAi")
async def tag_ai(payload: HtmlPayload):
    return aiTag(
        payload.user_id,
        payload.changingHtml,
        payload.contextHtml,
        payload.component_id   # ✅ NEW
    )


@app.post("/rewardTag")
async def reward_tag(payload: RewardPayload, background_tasks: BackgroundTasks):
    # loop through component IDs and queue work
    for component_id in payload.component_ids:
        background_tasks.add_task(
            rewardTag,
            payload.user_id,
            payload.reward,
            payload.contextHtml,
            payload.variantAttributed,
            component_id
        )

    return {"status": "queued", "msg": "Reward processing started"}

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