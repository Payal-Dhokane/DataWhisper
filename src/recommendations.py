import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Returns a ChatGroq instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-70b-8192",
        temperature=0.1
    )

def generate_recommendations(df_info):
    """Generates smart recommendations for preprocessing based on dataframe info."""
    llm = get_llm()
    if not llm:
        return "AI temporarily unavailable for recommendations. Check GROQ_API_KEY."

    prompt = ChatPromptTemplate.from_template("""
    You are an expert data science assistant. Based on the following dataset info 
    (including Data Types and Missing Values), provide actionable recommendations 
    for data preprocessing (e.g., how to handle missing values, potential feature 
    engineering, outlier treatment). 
    
    Dataset Info:
    {info}
    
    Rules:
    - Use clear markdown subheadings.
    - Be specific to the columns listed.
    - Suggest actual transformations (e.g., "Use One-Hot Encoding for column X").
    """)
    
    chain = prompt | llm
    try:
        response = chain.invoke({"info": df_info})
        return response.content
    except Exception as e:
        return f"Error generating recommendations: {e}"
