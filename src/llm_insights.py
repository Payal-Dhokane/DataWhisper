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

def explain_chart(chart_info):
    """Generates a simple explanation for a given chart's metadata."""
    llm = get_llm()
    if not llm:
        return "AI unavailable for chart explanation."

    prompt = ChatPromptTemplate.from_template("""
    You are an AI data assistant. Explain this chart to a user in simple terms.
    
    Chart Metadata:
    - Type: {chart_type}
    - Columns: {columns}
    
    Example output: "This histogram shows right-skewed distribution of Income..."
    Keep it to 2-3 sentences max.
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({"chart_type": chart_info['type'], "columns": chart_info['columns']})
        return response.content
    except Exception as e:
        return f"Could not explain chart: {str(e)}"
