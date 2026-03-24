import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Returns a ChatGroq instance, optionally fallback to Ollama if configured."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )

def generate_insights(df_summary, column_names, dtypes, missing_values, correlations):
    """Generates professional data analysis insights."""
    llm = get_llm()
    if not llm:
        return "AI temporarily unavailable. Please check your GROQ_API_KEY in the .env file."

    prompt = ChatPromptTemplate.from_template("""
    You are a professional data analyst.
    Analyze the dataset and generate insights.

    Dataset:
    Columns: {column_names}
    Types: {dtypes}
    Summary: {summary_stats}
    Missing: {missing_values}
    Correlations: {correlations}

    Tasks:
    1. Give 3–5 key insights.
    2. Highlight strong correlations (>0.7) or interesting patterns.
    3. Identify potential outliers or data quality issues.
    4. Suggest 2–3 actionable recommendations.

    Rules:
    - Use bullet points only.
    - Reference specific column names.
    - Avoid vague statements.
    - Base findings ONLY on the provided data.
    - No Hallucinations.
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({
            "column_names": column_names,
            "dtypes": dtypes,
            "summary_stats": df_summary,
            "missing_values": missing_values,
            "correlations": correlations
        })
        return response.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# NEW FEATURE
def generate_auto_summary(df_info):
    """Automatically generates 3-5 key insights for the dataset overview."""
    llm = get_llm()
    if not llm:
        return None

    prompt = ChatPromptTemplate.from_template("""
    You are a professional data analyst. 
    Quickly summarize this dataset in 3-5 bullet points.
    Focus on:
    - Overall size and complexity
    - Immediate data quality issues (missing values)
    - Interesting high-level patterns
    
    Dataset Info:
    {df_info}
    
    Format: Bullet points only. Max 5 points.
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({"df_info": str(df_info)})
        return response.content
    except Exception:
        return None

# IMPROVED FEATURE
def explain_chart(chart_info, data_context=None):
    """Generates a smarter explanation for a chart using optional data context."""
    llm = get_llm()
    if not llm:
        return "AI unavailable for chart explanation."

    context_str = f"\nData Context: {data_context}" if data_context else ""
    
    prompt = ChatPromptTemplate.from_template("""
    You are an AI data assistant. Explain this chart to a user using the provided metadata and data context.
    
    Chart Info:
    - Type: {chart_type}
    - Columns: {columns}
    {context_str}
    
    Task: 
    - Describe the visual (e.g., "This histogram shows...")
    - Include specific data points from the context (e.g., "The highest category is X with value Y")
    - Mention any obvious patterns or skewness.
    
    Keep it to 3-4 sentences max. Avoid generic buzzwords.
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({
            "chart_type": chart_info['type'], 
            "columns": chart_info['columns'],
            "context_str": context_str
        })
        return response.content
    except Exception as e:
        return f"Could not explain chart: {str(e)}"
