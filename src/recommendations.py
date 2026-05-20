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
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

def generate_recommendations(df_info):
    """Generates smart recommendations for preprocessing based on dataframe info."""
    llm = get_llm()
    if not llm:
        return "AI temporarily unavailable for recommendations. Check GROQ_API_KEY."

    prompt = ChatPromptTemplate.from_template("""
    You are an expert data science assistant. Based on the following dataset info, 
    provide 3-5 high-priority actionable recommendations for data preprocessing 
    (handling missing values, feature engineering, outliers).
    
    Rules:
    - START DIRECTLY with the recommendations. No introductions or 'Introduction to Preprocessing'.
    - Use clear markdown subheadings for each point.
    - Be specific (e.g., "Use One-Hot Encoding for column X").
    
    Dataset Info:
    {info}
    """)
    
    chain = prompt | llm
    try:
        response = chain.invoke({"info": df_info})
        return response.content
    except Exception as e:
        return f"Error generating recommendations: {e}"
