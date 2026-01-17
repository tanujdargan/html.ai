from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# The HTML your custom tag sends will match this model
class HtmlPayload(BaseModel):
    experiment: str
    html: str


@app.post("/log-html")
async def log_html(payload: HtmlPayload):
    print("\n==== RECEIVED HTML FROM CLIENT ====")
    print("Experiment:", payload.experiment)
    print("HTML Content:")
    print(payload.html)
    print("===================================\n")

    return {"status": "ok", "received": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)