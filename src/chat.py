import os
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource(show_spinner="Initializing AI Data Agent...")
def get_pandas_agent(df):
    """Initializes the Pandas DataFrame Agent using Groq with caching."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
        
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )
    
    # allow_dangerous_code=True is required for pandas agent to run python code
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        agent_type="tool-calling", # Updated for better compatibility with newer Llama models
        allow_dangerous_code=True
    )
    return agent

def query_agent(agent, query, df_context=""):
    """Queries the agent with a user prompt and extra context."""
    if agent is None:
        return "Agent not initialized. Please check your GROQ_API_KEY."
    
    # Refined prompt for more reliable performance
    prompt = f"""
    You are an expert data analyst. Use the provided dataframe to answer the question.
    Context: {df_context}
    
    Question: {query}
    
    If the question cannot be answered from the data, say "I don't have enough data to answer that."
    Always be concise.
    """
    
    try:
        # Simplest invocation is often most reliable
        response = agent.run(prompt)
        return response
    except Exception as e:
        # Fallback if run fails
        try:
             response = agent.invoke({"input": prompt})
             return response.get("output", "I couldn't find an answer.")
        except Exception as e2:
             return f"Error executing query: {e2}"

def get_suggested_questions():
    """Returns a list of suggested questions for the chat."""
    return [
        "Show key insights",
        "Find anomalies",
        "Summarize dataset",
        "Explain correlations"
    ]
