"""
Analytics Dashboard Server for html.ai

Serves the dashboard and provides analytics endpoints.
Reads variant data from the same MongoDB as the A/B testing engine.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from typing import Dict, Any, List
from datetime import datetime
import os

# ----------------------------------------
# FastAPI App + CORS
# ----------------------------------------
app = FastAPI(
    title="html.ai - Analytics Dashboard",
    description="Analytics and variant visualization for A/B testing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# MongoDB - Same database as server.py (html_ai)
# ----------------------------------------
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["html_ai"]

users_collection = db["users"]

# ----------------------------------------
# Helper Functions
# ----------------------------------------
def serialize_doc(doc: Dict) -> Dict:
    """Serialize MongoDB document"""
    if doc is None:
        return None
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for key, value in doc.items():
        if hasattr(value, 'isoformat'):
            doc[key] = value.isoformat()
    return doc


# ----------------------------------------
# Analytics Endpoints
# ----------------------------------------
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "html.ai - Analytics Dashboard",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    try:
        # Test MongoDB connection
        mongo_client.admin.command('ping')
        return {"status": "healthy", "mongo": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "mongo": str(e)}


@app.get("/api/variants/all")
async def get_all_variants():
    """
    Get all users with their A/B variants for the carousel display.
    Returns variant HTML, scores, and history.
    """
    try:
        users = list(users_collection.find({}))

        variants_data = []
        for user in users:
            user_id = user.get("user_id", "unknown")
            components = user.get("components", {})

            # Loop through each component_id
            for component_id, component_data in components.items():
                for variant_letter in ["A", "B"]:
                    variant = component_data.get(variant_letter, {})
                    if variant.get("current_html"):
                        variants_data.append({
                            "user_id": user_id,
                            "component_id": component_id,
                            "variant": variant_letter,
                            "html": variant.get("current_html", ""),
                            "score": round(variant.get("current_score", 0), 2),
                            "trials": variant.get("number_of_trials", 0),
                            "history_count": len(variant.get("history", []))
                        })

        return {
            "status": "ok",
            "total_users": len(users),
            "total_variants": len(variants_data),
            "variants": variants_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/variants/user/{user_id}")
async def get_user_variants(user_id: str):
    """
    Get detailed variant data for a specific user.
    Includes current HTML, history, and scores.
    """
    try:
        user = users_collection.find_one({"user_id": user_id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        components = user.get("components", {})

        result = {
            "user_id": user_id,
            "components": {}
        }

        # Loop through each component
        for component_id, component_data in components.items():
            result["components"][component_id] = {
                "A": {
                    "current_html": component_data.get("A", {}).get("current_html", ""),
                    "current_score": round(component_data.get("A", {}).get("current_score", 0), 2),
                    "number_of_trials": component_data.get("A", {}).get("number_of_trials", 0),
                    "history": component_data.get("A", {}).get("history", [])
                },
                "B": {
                    "current_html": component_data.get("B", {}).get("current_html", ""),
                    "current_score": round(component_data.get("B", {}).get("current_score", 0), 2),
                    "number_of_trials": component_data.get("B", {}).get("number_of_trials", 0),
                    "history": component_data.get("B", {}).get("history", [])
                }
            }

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/overview")
async def get_stats_overview():
    """
    Get overview statistics for the dashboard.
    """
    try:
        users = list(users_collection.find({}))

        total_users = len(users)
        total_trials = 0
        a_wins = 0
        b_wins = 0
        total_a_score = 0
        total_b_score = 0
        total_components = 0

        for user in users:
            components = user.get("components", {})

            # Loop through each component
            for component_id, component_data in components.items():
                total_components += 1
                
                a_variant = component_data.get("A", {})
                b_variant = component_data.get("B", {})

                a_score = a_variant.get("current_score", 0)
                b_score = b_variant.get("current_score", 0)

                total_a_score += a_score
                total_b_score += b_score

                total_trials += a_variant.get("number_of_trials", 0)
                total_trials += b_variant.get("number_of_trials", 0)

                if a_score > b_score:
                    a_wins += 1
                elif b_score > a_score:
                    b_wins += 1

        avg_a_score = round(total_a_score / total_components, 2) if total_components > 0 else 0
        avg_b_score = round(total_b_score / total_components, 2) if total_components > 0 else 0

        return {
            "total_users": total_users,
            "total_trials": total_trials,
            "variant_a": {
                "wins": a_wins,
                "avg_score": avg_a_score
            },
            "variant_b": {
                "wins": b_wins,
                "avg_score": avg_b_score
            },
            "overall_leader": "A" if avg_a_score >= avg_b_score else "B"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/variants/history/{user_id}/{component_id}/{variant}")
async def get_variant_history(user_id: str, component_id: str, variant: str):
    """
    Get the full history of a specific variant for a user's component.
    Shows how the HTML evolved over time.
    """
    variant = variant.upper()
    if variant not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Variant must be A or B")

    try:
        user = users_collection.find_one({"user_id": user_id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        components = user.get("components", {})
        component_data = components.get(component_id, {})
        variant_data = component_data.get(variant, {})

        return {
            "user_id": user_id,
            "component_id": component_id,
            "variant": variant,
            "current_html": variant_data.get("current_html", ""),
            "current_score": variant_data.get("current_score", 0),
            "history": variant_data.get("history", []),
            "total_versions": len(variant_data.get("history", [])) + 1
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------
# Run Server
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
