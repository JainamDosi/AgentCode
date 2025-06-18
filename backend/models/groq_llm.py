import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def chat(prompt: str, model="gemma2-9b-it") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "system", "content": "You are a AI SWE developer.",
            "role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()
