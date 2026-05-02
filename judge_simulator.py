import os
import json
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

# --- INITIALIZATION ---
# This looks for your .env file in the current folder
load_dotenv(find_dotenv())

# Configuration - pulls from .env
BOT_URL = os.getenv("BOT_URL", "http://localhost:8000")
LLM_API_KEY = os.getenv("GOOGLE_API_KEY")
DATASET_PATH = "./dataset"

# Configure the LLM Judge
if LLM_API_KEY:
    genai.configure(api_key=LLM_API_KEY)
    judge_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    print("❌ CRITICAL ERROR: GOOGLE_API_KEY not found. Please check your .env file.")

def call_bot(endpoint, payload):
    """Sends requests to your FastAPI server."""
    try:
        response = requests.post(f"{BOT_URL}{endpoint}", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        print(f"⚠️ Bot error on {endpoint}: Status {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Connection error calling {endpoint}: {e}")
        return None

def score_response(bot_output, trigger_context):
    """The LLM-powered judge that evaluates your bot based on the rubric[cite: 1]."""
    prompt = f"""
    You are the Magicpin AI Judge. Evaluate this Vera response.
    
    RUBRIC (Score each 0-10):
    1. Decision Quality: Did the bot pick the best signal for this moment?[cite: 1]
    2. Specificity: Did the bot use real numbers and local facts?[cite: 1]
    3. Category Fit: Is the tone right for the merchant type?[cite: 1]
    4. Merchant Fit: Is it personalized to the merchant's metrics?[cite: 1]
    5. Engagement Compulsion: Is the CTA low-friction and clear?[cite: 1]

    TRIGGER CONTEXT: {json.dumps(trigger_context)}
    BOT RESPONSE: {json.dumps(bot_output)}

    Return ONLY a raw JSON object:
    {{
        "decision_quality": 0,
        "specificity": 0,
        "category_fit": 0,
        "merchant_fit": 0,
        "engagement": 0,
        "rationale": "short explanation"
    }}
    """
    try:
        res = judge_model.generate_content(prompt)
        # Fix for the syntax error you saw earlier[cite: 1]
        cleaned_text = res.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except Exception as e:
        return {"error": f"Scoring failed: {str(e)}"}

def run_simulation():
    print("🚀 Starting Vera Building Challenge: Simulation Initialized")
    
    # 1. Warmup: Push context to the bot[cite: 1]
    print("📂 Loading datasets into bot context...")

    def load_and_push(path, scope):
        if not os.path.exists(path):
            print(f"⚠️ Missing dataset file: {path}")
            return
            
        with open(path, 'r') as f:
            data = json.load(f)
            
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            found_list = False
            for key in ["merchants", "customers", "categories", "triggers"]:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    found_list = True
                    break
            if not found_list:
                items = [data]
                
        for item in items:
            context_id = item.get("id", item.get("merchant_id", item.get("customer_id", item.get("slug", "default_id"))))
            call_bot("/v1/context", {"scope": scope, "context_id": context_id, "data": item})

    # 1a. Load category contexts from the categories folder
    categories_dir = os.path.join(DATASET_PATH, "categories")
    if os.path.exists(categories_dir):
        for filename in os.listdir(categories_dir):
            if filename.endswith(".json"):
                load_and_push(os.path.join(categories_dir, filename), "category")
    else:
        print(f"⚠️ Missing categories directory: {categories_dir}")

    # 1b. Load merchants and customers
    load_and_push(os.path.join(DATASET_PATH, "merchants_seed.json"), "merchant")
    load_and_push(os.path.join(DATASET_PATH, "customers_seed.json"), "customer")

    # 2. Simulation Loop: 60 minutes, 5-minute ticks[cite: 1]
    trigger_file = os.path.join(DATASET_PATH, "triggers_seed.json")
    if not os.path.exists(trigger_file):
        print("❌ Error: triggers_seed.json not found. Stopping.")
        return

    with open(trigger_file, 'r') as f:
        triggers_data = json.load(f)
        triggers = triggers_data.get("triggers", []) if isinstance(triggers_data, dict) else triggers_data

    print("\n✅ Warmup Complete. Running 60-minute test window...\n" + "-"*50)

    for i in range(0, 60, 5):
        print(f"🕒 [T+{i} min] Calling /v1/tick...")
        # Get the next trigger for this 5-min interval[cite: 1]
        idx = min(i // 5, len(triggers) - 1)
        current_trigger = triggers[idx]

        bot_res = call_bot("/v1/tick", current_trigger)
        
        if bot_res and "message" in bot_res:
            print(f"🤖 VERA: \"{bot_res['message']}\"")
            print(f"👉 CTA: {bot_res.get('cta')}")
            
            # Score the response[cite: 1]
            score_report = score_response(bot_res, current_trigger)
            print(f"📊 SCORE REPORT: {json.dumps(score_report, indent=2)}")
        else:
            print("⚠️ Bot failed to return a valid message for this tick.")
        
        print("-" * 50)
        time.sleep(1) # Simulated time delay

    print("\n🏁 Simulation Finished. Review your scores above before submitting!")

if __name__ == "__main__":
    run_simulation()