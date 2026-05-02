import uvicorn
from fastapi import FastAPI, Body, Request
from models import ContextPayload, TriggerPayload
from engine import VeraEngine

app = FastAPI(title="Vera Bot - Satyansh")
engine = VeraEngine()

# --- DATABASE ---
# In-memory store for simulation context
db = {
    "merchant": {},
    "category": {},
    "customer": {}
}

# --- MIDDLEWARE: BYPASS NGROK WARNING ---
@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    """
    This tells ngrok to skip the 'interstitial' warning page.
    It ensures Magicpin's automated judges get direct access to your JSON.
    """
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# --- REQUIRED SUBMISSION ENDPOINTS ---

@app.get("/v1/healthz")
async def health_check():
    """Confirms the bot is live."""
    return {"status": "ok"}

@app.get("/v1/metadata")
async def get_metadata():
    """Identifies the bot to the evaluator."""
    return {
        "bot_name": "Vera-Satyansh-Lucknow",
        "version": "1.1.0",
        "supported_scopes": ["merchant", "category", "customer"],
        "developer": "Satyansh Srivastava"
    }

@app.post("/v1/context")
async def update_context(payload: ContextPayload):
    """Stores training/seed data sent during the warmup phase."""
    db[payload.scope][payload.context_id] = payload.data
    return {"status": "success", "scope": payload.scope}

@app.post("/v1/tick")
async def handle_tick(trigger: TriggerPayload):
    """
    Core logic: Triggered every 5 minutes by the judge.
    Uses stored context to generate a high-impact response.
    """
    m_id = trigger.merchant_id
    merchant = db["merchant"].get(m_id, {})
    
    # Logic to find category based on the merchant's data
    cat_id = merchant.get("category_id", "default")
    category = db["category"].get(cat_id, {})
    
    # Call the LLM engine to compose the message
    result = engine.compose(trigger.dict(), merchant, category)
    return result

@app.post("/v1/reply")
async def handle_reply(data: dict = Body(...)):
    """Handles incoming customer messages."""
    return {
        "status": "success", 
        "message": "Vera has acknowledged your message."
    }

# --- SERVER START ---
if __name__ == "__main__":
    # Binding to 0.0.0.0 is critical for ngrok tunneling
    uvicorn.run(app, host="0.0.0.0", port=8000)