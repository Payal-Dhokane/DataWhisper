import os
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_pandas_agent(df):
    """Initializes the Pandas DataFrame Agent using Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
        
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-70b-8192",
        temperature=0
    )
    
    # allow_dangerous_code=True is required for pandas agent to run python code
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        agent_type="tool-calling", # Generic tool calling for Llama3
        allow_dangerous_code=True
    )
    return agent

def query_agent(agent, query, df_context=""):
    """Queries the agent with a user prompt and extra context."""
    if agent is None:
        return "Agent not initialized. Please check your GROQ_API_KEY."
    
    system_message = f"""
    You are an AI data assistant.
    Answer ONLY using dataset context. If not possible -> say "Not enough data".
    Dataset Summary: {df_context}
    """
    
    try:
        # We can prepend the system message to the query or use a custom prompt
        full_query = f"{system_message}\n\nUser question: {query}"
        response = agent.invoke({"input": full_query})
        return response.get("output", "I couldn't find an answer.")
    except Exception as e:
        return f"Error executing query: {e}"

def get_suggested_questions():
    """Returns a list of suggested questions for the chat."""
    return [
        "Show key insights",
        "Find anomalies",
        "Summarize dataset",
        "Explain correlations"
    ]
