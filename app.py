import os
import json
import gradio as gr
from dotenv import load_dotenv
from google import genai

from history import load_chat, save_chat
from memory import remember, recall

# -------------------------
# Load API Key
# -------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

chat_history = load_chat()


def chat(message, history):
    global chat_history

    # Save user message
    chat_history.append({
        "role": "user",
        "content": message
    })

    # Load memory
    memory = {
        "name": recall("name"),
        "city": recall("city"),
        "company": recall("company")
    }

    # Prompt
    prompt = f"""
You are Jerry AI.

You have long-term memory.

Known information about the user:

{json.dumps(memory, indent=2)}

Conversation:

{json.dumps(chat_history, indent=2)}

Latest user message:

{message}

Instructions:

1. Answer naturally like ChatGPT.

2. If the user tells you new personal information
(name, city, company, college, age, skills,
favorite things, goals, etc.),
remember it.

3. If the answer already exists in memory,
use it.

4. At the END of your response output ONLY:

MEMORY:
{{}}

Example:

User:
My name is Narasimha.

Assistant:
Nice to meet you, Narasimha!

MEMORY:
{{"name":"Narasimha"}}

If nothing new:

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

        # Extract memory
        if "MEMORY:" in text:

            answer, memory_text = text.split("MEMORY:", 1)

            try:
                new_memory = json.loads(memory_text.strip())

                for key, value in new_memory.items():
                    remember(key, value)

            except Exception:
                pass

        answer = answer.strip()

    except Exception as e:
        answer = f"Error: {e}"

    # Save assistant reply
    chat_history.append({
        "role": "assistant",
        "content": answer
    })

    save_chat(chat_history)

    return answer


# -------------------------
# Gradio UI
# -------------------------

demo = gr.ChatInterface(
    fn=chat,
    title="🤖 Jerry AI",
    description="Powered by Google Gemini with Memory"
)

if __name__ == "__main__":
    demo.launch()