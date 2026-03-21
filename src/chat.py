from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

def get_pandas_agent(df, api_key):
    """Initializes the Pandas DataFrame Agent."""
    if not api_key:
        return None
    llm = ChatOpenAI(temperature=0, openai_api_key=api_key, model="gpt-3.5-turbo")
    
    # allow_dangerous_code=True is required for pandas agent to run python code
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        agent_type="openai-tools",
        allow_dangerous_code=True
    )
    return agent

def query_agent(agent, query):
    """Queries the agent with a user prompt."""
    if agent is None:
        return "Agent not initialized. Please provide an API Key."
    try:
        response = agent.invoke({"input": query})
        return response.get("output", "I couldn't find an answer.")
    except Exception as e:
        return f"Error executing query: {e}"
