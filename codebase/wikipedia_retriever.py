from langchain_community.document_loaders import WebBaseLoader
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# Set environment variables (replace with your actual keys or manage externally)
tavily_tool = TavilySearchResults()
def get_web_info(query: str):
    """Retrieves and prints information from the internet using a web-crawling agent."""
    print(f"\n--- Searching the internet for: '{query}' ---")
    try:
        # The agent executor will decide which tools to use
        result = agent_executor.invoke({"input": query})
        print("\nWeb Search Result:")
        print(result.get("output", "No output from agent."))
    except Exception as e:
        print(f"An error occurred while fetching information for '{query}': {e}")

web_content_tool = Tool(
    name="web_content_reader",
    func=_get_web_content,
    get_web_info("LangChain framework")
    get_web_info("latest news on AI models")
    get_web_info("history of space exploration")

    description="Useful for reading the content of a specific URL. Input should be a valid URL string.",
)

tools = [tavily_tool, web_content_tool]

# Get the prompt to use - you can modify this to your liking
prompt = hub.pull("hwchase17/react")

# Construct the agent
agent = create_react_agent(llm, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
# os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_API_KEY"

llm = ChatOpenAI(model="gpt-4o", temperature=0) # Using a modern model

def _get_web_content(url: str) -> str:
    """Loads content from a URL."""
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs[0].page_content if docs else "No content found."
    except Exception as e:
        return f"Error loading content from {url}: {e}"

)

def get_wikipedia_info(query: str):
    """Retrieves and prints information from Wikipedia for a given query."""
    print(f"\n--- Searching Wikipedia for: '{query}' ---")
    try:
        # The .run() method takes a string query and returns a string summary.
        result = wikipedia_wrapper.run(query)
        print("\nWikipedia Search Result:")
        print(result)
    except Exception as e:
        print(f"An error occurred while fetching information for '{query}': {e}")

if __name__ == "__main__":
    # Example 1: Retrieve information about LangChain
    get_wikipedia_info("LangChain")

    # Example 2: Retrieve information about Artificial Intelligence
    get_wikipedia_info("Artificial Intelligence")

    # Example 3: Retrieve information about a historical figure
    get_wikipedia_info("Marie Curie")