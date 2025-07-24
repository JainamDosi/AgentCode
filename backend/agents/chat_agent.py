from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)
import os
from dotenv import load_dotenv

load_dotenv()


# --- LLM Setup ---
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# --- Memory Setup ---
memory = ConversationBufferMemory(return_messages=True)

# --- Prompt Template Setup ---
system_template = (
    "You are an expert AI coding assistant named Lucifer the Coder. "
    "You help users write, debug, and understand code in a wide variety of programming languages and frameworks. "
    "Always provide clear, concise, and well-documented code examples. "
    "If a user asks for an explanation, break down complex concepts into simple, easy-to-understand steps. "
    "If you are unsure about something, state your assumptions. "
    "Never provide code that is unsafe, malicious, or violates ethical guidelines. "
    "Be friendly, professional, and proactive in offering suggestions or improvements."
)
human_template = "{user_input}"

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])

# --- Standalone Question PromptTemplate ---
standalone_question_prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    template=(
        "Given the following conversation and a follow up question, "
        "rephrase the follow up question to be a standalone question.\n\n"
        "Chat History:\n{chat_history}\n"
        "Follow Up Input: {input}\n"
        "Standalone Question:"
    )
)

def get_chat_history_as_text():
    """Converts memory's chat history to a plain text format for the prompt."""
    history = memory.chat_memory.messages
    lines = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)

def rephrase_to_standalone(user_input: str) -> str:
    """Rephrases a follow-up question into a standalone question using chat history."""
    chat_history = get_chat_history_as_text()
    prompt = standalone_question_prompt.format(
        chat_history=chat_history,
        input=user_input
    )
    response = llm.invoke(prompt)
    return response.content.strip()

def is_code_action_request(user_message: str) -> bool:
    # Use the LLM to classify intent
    intent_prompt = (
        "Determine if the following user message is a request to perform a code change or coding task or to make a program or making any types of changes to file "
        "Reply only with 'yes' or 'no'.\n"
        f"User message: {user_message}\n"
        "Is this a code action request?"
    )
    response = llm.invoke(intent_prompt)
    return response.content.strip().lower().startswith("yes")

# --- Chat Function with Memory and Standalone Question Rephrasing ---
def chat_with_memory(user_message: str, custom_instructions: str = "", rephrase: bool = False):
    # Optionally rephrase the user message to a standalone question
    if rephrase and memory.chat_memory.messages:
        user_message = rephrase_to_standalone(user_message)

    # Build the prompt for this turn
    messages = chat_prompt.format_messages(
        custom_instructions=custom_instructions,
        user_input=user_message
    )
    # Add previous conversation history (excluding the current user message)
    history = memory.chat_memory.messages
    # Combine history and current prompt
    full_messages = history + messages

    # Get LLM response
    response = llm.invoke(full_messages)
    # Update memory with user and AI messages
    memory.chat_memory.add_message(HumanMessage(content=user_message))
    memory.chat_memory.add_message(AIMessage(content=response.content))
    return response.content

def chat_with_memory_with_confirmation(user_message: str, custom_instructions: str = "", rephrase: bool = False):
    response = chat_with_memory(user_message, custom_instructions, rephrase)
    if is_code_action_request(user_message):
        return {
            "reply": f"Do you want me to execute this task: \"{user_message}\"?",
            "task": user_message,
            "show_execute_button": True
        }
    return {"reply": response}

