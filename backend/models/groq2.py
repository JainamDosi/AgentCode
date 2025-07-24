from langchain.chat_models import ChatGroq  # If available in your langchain version
# If not, you may need to use ChatOpenAI or a custom wrapper
from langchain.schema import HumanMessage

# Initialize the LangChain Groq chat model
chat = ChatGroq(
     
    model="meta-llama/llama-4-scout-17b-16e-instruct"
)

def chat_with_groq(message: str) -> str:
    response = chat([HumanMessage(content=message)])
    return response.content
