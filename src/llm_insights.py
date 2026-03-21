from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

def generate_insights(df_summary, api_key):
    """Generates plain-English insights from dataset statistics using LLM."""
    if not api_key:
        return "Please provide an OpenAI API Key in the sidebar to generate insights."

    llm = ChatOpenAI(temperature=0.2, openai_api_key=api_key, model="gpt-3.5-turbo")
    
    prompt = PromptTemplate(
        input_variables=["summary"],
        template=(
            "You are an expert data science assistant. Based on the following dataset summary, "
            "provide concise, plain-English insights (e.g., strong correlations, outliers, "
            "data quality issues, trends). Format your response beautifully using markdown lists "
            "and highlighting.\n\n"
            "Dataset Summary:\n{summary}\n\n"
            "Insights:"
        )
    )
    
    chain = prompt | llm
    try:
        response = chain.invoke({"summary": df_summary})
        return response.content
    except Exception as e:
        return f"Error generating insights: {e}"
