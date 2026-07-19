import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from history import load_chat, save_chat
from memory import remember, recall

# -------------------------
# Load API Key
# -------------------------

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="Jerry AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = load_chat()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    global chat_history

    message = req.message

    chat_history.append({
        "role": "user",
        "content": message
    })

    memory = {
        "name": recall("name"),
        "city": recall("city"),
        "company": recall("company")
    }

    prompt = f"""
You are Jerry AI.

You have long-term memory.

Known information:

{json.dumps(memory, indent=2)}

Conversation:

{json.dumps(chat_history, indent=2)}

Latest user message:

{message}

Answer naturally.

At the end output

MEMORY:
{{}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text
        answer = text

        if "MEMORY:" in text:

            answer, memory_text = text.split("MEMORY:", 1)

            try:
                new_memory = json.loads(memory_text.strip())

                for k, v in new_memory.items():
                    remember(k, v)

            except:
                pass

        answer = answer.strip()

    except Exception as e:
        answer = str(e)

    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    save_chat(chat_history)

    return {
        "response": answer
    }


@app.get("/")
def root():
    return {
        "message": "Jerry AI Backend Running"
    }