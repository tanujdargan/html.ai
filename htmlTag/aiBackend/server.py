from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import random
from openai import OpenAI
import os
import threading




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
        })
        # 2. Generate variant B in background thread (non-blocking)
        def generate_variant_b():
            new_b_html = AIRags(user_id, contextHtml, "B", "A")
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"variants.B.current_html": new_b_html}}
            )
            print(f"✅ Variant B generated for user {user_id}")

        thread = threading.Thread(target=generate_variant_b)
        thread.start()

        return {
            "status": "ok:new-user",
            "changingHtml": changingHtml,
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



# ----------------------------------------
# Logic: rewardTag
# ----------------------------------------
def rewardTag(user_id: str, reward: float, contextHtml: str, variantAttributed: str):
    """
    Store a reward value mapped to the given user.
    """
    ReRenderCheck(user_id, contextHtml)
    implementScore(user_id, variantAttributed, reward)


    return {
        "status": "reward_logged",
        "user_id": user_id,
        "reward": reward
    }



def implementScore(user_id: str, variant: str, reward: float):
    variant = variant.upper()

    # Get the current user entry
    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "User not found"

    variant_data = user["variants"][variant]

    old_score = variant_data["current_score"]
    old_trials = variant_data["number_of_trials"]

    # Compute new average score
    new_trials = old_trials + 1
    new_score = (old_score * old_trials + reward) / new_trials

    # Update MongoDB
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"variants.{variant}.current_score": new_score,
                f"variants.{variant}.number_of_trials": new_trials
            }
        }
    )



def ReRenderCheck(user_id: str, contextHtml: str):

    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return False

    AScore = user["variants"]["A"]["current_score"]
    BScore = user["variants"]["B"]["current_score"]
    AHtml = user["variants"]["A"]["current_html"]
    BHtml = user["variants"]["B"]["current_html"]

    # If A is outperforming B by threshold → regenerate B (in background)
    if AScore >= BScore + RERENDER_SCORE:
        thread = threading.Thread(target=reRender, args=(user_id, "B", "A", contextHtml, BHtml))
        thread.start()

    # If B is outperforming A by threshold → regenerate A (in background)
    if BScore >= AScore + RERENDER_SCORE:
        thread = threading.Thread(target=reRender, args=(user_id, "A", "B", contextHtml, AHtml))
        thread.start()

    return True



def reRender(user_id: str, VariantLetter: str, opposingVariantLetter:str, contextHtml: str, oldHtml: str):
    """
    testLetter: "A" or "B"
    oldHtml: the previous HTML before updating
    """

    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "User not found"

    # Make sure testLetter is uppercase
    VariantLetter = VariantLetter.upper()

    # Safety check
    if VariantLetter not in ["A", "B"]:
        raise Exception("testLetter must be 'A' or 'B'")

    # 1. Push oldHtml into the correct variant's history
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$push": {
                f"variants.{VariantLetter}.history": oldHtml
            }
        }
    )

    # 2. Now generate NEW HTML (stubbed for now)
    new_html = AIRags(user_id, contextHtml, VariantLetter, opposingVariantLetter)


    # 3. Store the new HTML in current_html
    mongodb["users"].update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"variants.{VariantLetter}.current_html": new_html
            }
        }
    )

    print(mongodb["users"].find_one({"user_id": user_id}))

    reset_scores_to_midpoint(user_id)


def reset_scores_to_midpoint(user_id: str):
    user = users_collection.find_one({"user_id": user_id})

    if not user:
        print("⚠️ User not found for midpoint reset.")
        return

    A_score = user["variants"]["A"]["current_score"]
    B_score = user["variants"]["B"]["current_score"]

    new_score = (A_score + B_score) / 2

    # Update scores & reset trials back to 0
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "variants.A.current_score": new_score,
                "variants.B.current_score": new_score,
                "variants.A.number_of_trials": 0,
                "variants.B.number_of_trials": 0
            }
        }
    )

    print(f"🔄 Reset scores → midpoint = {new_score:.4f}")

def AIRags(
    user_id: str,
    contextHtml: str,
    varianceLetter: str,
    opposingVariantLetter: str
) -> str:
    """
    Regenerate the HTML for the losing variant using:
    - Current variant HTML that needs updating
    - Opposing variant's HTML (the winning one)
    - Context HTML (surrounding structure)
    """

    print("RAG RAN!!!")
    # Fetch user + opposing HTML + score
    user = mongodb["users"].find_one({"user_id": user_id})
    if not user:
        return "<div>Error: user not found</div>"

    losing_html = user["variants"][varianceLetter]["current_html"]
    winning_variant = user["variants"][opposingVariantLetter]

    winning_html = user["variants"][opposingVariantLetter]["current_html"]
    winning_score = user["variants"][opposingVariantLetter]["current_score"]

    # -------------------------
    # 🔥 Prompt for OpenAI
    # -------------------------
    prompt = f"""
You are an A/B testing AI that optimizes HTML components for better conversion.
You are updating variant {varianceLetter} to compete with the winning variant {opposingVariantLetter}.

### Winning Variant ({opposingVariantLetter}) - Score: {winning_score}
```html
{winning_html}
```

### Losing Variant ({varianceLetter}) - Needs Improvement
```html
{losing_html}
```

### Page Context
```html
{contextHtml}
```

### WHAT YOU CAN MODIFY (be creative within these bounds):

**Text & Copy:**
- Headlines (h1, h2, h3) - try different emotional hooks, urgency, benefits
- Descriptions/paragraphs - shorter vs longer, feature-focused vs benefit-focused
- Button text (CTAs) - action verbs, urgency words, value propositions
- Badges/labels - "New", "Limited", "Best Seller", "Free Shipping", etc.

**Typography & Styling (inline styles):**
- Font sizes (larger headlines, smaller body, etc.)
- Font weights (bold, semibold, normal)
- Text colors (contrast, emphasis on key words)
- Letter spacing, line height

**Layout & Positioning (inline styles):**
- Flexbox direction (row vs column)
- Alignment (center, left, right)
- Spacing (padding, margin, gap)
- Element ordering (move CTA above/below text, reorder content)

**Visual Emphasis:**
- Background colors on sections
- Border styles, border-radius
- Box shadows for depth

**Image Positioning (DO NOT resize images):**
- Move image left/right of content (flex order)
- Change image placement in the layout
- DO NOT change image width, height, or src - keep original dimensions

**Element Visibility:**
- Show/hide secondary elements
- Add urgency elements (limited stock, timer placeholder)
- Add trust signals (ratings, reviews count)

### RULES:
1. Keep the same semantic structure (don't remove core elements)
2. Use inline styles for all CSS changes
3. Be bold - try something noticeably different from the losing variant
4. Learn from what made the winning variant successful
5. Return ONLY the raw HTML - no markdown, no explanations, no code blocks
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
    return aiTag(payload.user_id, payload.changingHtml, payload.contextHtml)


@app.post("/rewardTag")
async def reward_tag(payload: RewardPayload):
    return rewardTag(payload.user_id, payload.reward, payload.contextHtml, payload.variantAttributed)


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