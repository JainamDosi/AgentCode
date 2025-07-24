import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def chat(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()
