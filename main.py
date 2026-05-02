import uvicorn
from fastapi import FastAPI, Body, Request
from models import ContextPayload, TriggerPayload
from engine import VeraEngine

app = FastAPI(title="Vera Bot - Satyansh")
engine = VeraEngine()

# --- DATABASE ---
db = {
    "merchant": {},
    "category": {},
    "customer": {}
}

# --- NEW: ROOT ROUTE (To resolve "Not Found") ---
@app.get("/")
async def root():
    return {
        "message": "Vera AI is online and operational.",
        "status": "Ready for Magicpin Challenge",
        "developer": "Satyansh Srivastava",
        "endpoints": ["/v1/metadata", "/v1/healthz"]
    }

# --- REQUIRED SUBMISSION ENDPOINTS ---

@app.get("/v1/healthz")
async def health_check():
    return {"status": "ok"}

@app.get("/v1/metadata")
async def get_metadata():
    return {
        "bot_name": "Vera-Satyansh-Lucknow",
        "version": "1.2.0",
        "supported_scopes": ["merchant", "category", "customer"]
    }

@app.post("/v1/context")
async def update_context(payload: ContextPayload):
    db[payload.scope][payload.context_id] = payload.data
    return {"status": "success"}

@app.post("/v1/tick")
async def handle_tick(trigger: TriggerPayload):
    m_id = trigger.merchant_id
    merchant = db["merchant"].get(m_id, {})
    cat_id = merchant.get("category_id", "default")
    category = db["category"].get(cat_id, {})
    
    result = engine.compose(trigger.dict(), merchant, category)
    return result

@app.post("/v1/reply")
async def handle_reply(data: dict = Body(...)):
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)