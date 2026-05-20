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

def generate_insights(df_summary, column_names, dtypes, missing_values, correlations, task="General Analysis"):
    """
    # NEW FEATURE: Focused insights based on 'task'.
    Generates professional data analysis insights targeted to a specific objective.
    """
    llm = get_llm()
    if not llm:
        return "AI temporarily unavailable. Please check your GROQ_API_KEY in the .env file."

    prompt = ChatPromptTemplate.from_template("""
    You are a professional data analyst.
    Your specific objective is: {task}
    
    Based ONLY on the provided dataset summary, provide high-quality insights focused on this objective.
    
    Dataset Context:
    - Columns: {column_names}
    - Types: {dtypes}
    - Summary Stats: {summary_stats}
    - Missing Values: {missing_values}
    - Correlations: {correlations}

    Tasks for this response:
    1. Focus heavily on the requested objective: {task}.
    2. Give 3–5 key insights.
    3. Suggest 2 Actionable recommendations related to the results.

    Rules:
    - Use bullet points.
    - Reference specific column names.
    - No Hallucinations.
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({
            "task": task,
            "column_names": column_names,
            "dtypes": dtypes,
            "summary_stats": df_summary,
            "missing_values": missing_values,
            "correlations": correlations
        })
        return response.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# NEW FEATURE: Auto-generated executive summary
def generate_auto_summary(df_info_str):
    """Generates a 3-5 point executive summary from dataframe info."""
    llm = get_llm()
    if not llm:
        return "AI unavailable for summary."

    prompt = ChatPromptTemplate.from_template("""
    You are an expert data analyst. Based on this dataset summary, provide 3-5 concise, high-level executive insights as bullet points.
    Focus on data quality, distributions, and potential relationships.
    
    Data Summary:
    {info}
    
    Insights:
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({"info": df_info_str})
        return response.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def explain_chart(chart_info, data_context=None):
    """
    # NEW FEATURE: Smarter chart explanation with data-driven context.
    Generates a simple explanation for a given chart's metadata and optional context.
    """
    llm = get_llm()
    if not llm:
        return "AI unavailable for chart explanation."

    context_str = f"\nAdditional Data Context: {data_context}" if data_context else ""

    prompt = ChatPromptTemplate.from_template("""
    You are an AI data assistant. Explain this chart to a user in simple terms.
    
    Chart Metadata:
    - Type: {chart_type}
    - Columns: {columns}{context}
    
    If data context is provided, include specific insights like highest/lowest values.
    Keep it to 2-3 sentences max.
    """)

    chain = prompt | llm
    try:
        response = chain.invoke({
            "chart_type": chart_info['type'], 
            "columns": chart_info['columns'],
            "context": context_str
        })
        return response.content
    except Exception as e:
        return f"Could not explain chart: {str(e)}"
