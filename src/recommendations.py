from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

def generate_recommendations(df_info, api_key):
    """Generates smart recommendations for preprocessing based on dataframe info."""
    if not api_key:
        return "Please provide an OpenAI API Key to generate recommendations."

    llm = ChatOpenAI(temperature=0.3, openai_api_key=api_key, model="gpt-3.5-turbo")
    
    prompt = PromptTemplate(
        input_variables=["info"],
        template=(
            "You are an expert data science assistant. Based on the following dataset info "
            "(including Data Types and Missing Values), provide actionable recommendations "
            "for data preprocessing (e.g., how to handle missing values, potential feature "
            "engineering, outlier treatment). Format the response clearly with markdown.\n\n"
            "Dataset Info:\n{info}\n\n"
            "Recommendations:"
        )
    )
    
    chain = prompt | llm
    try:
        response = chain.invoke({"info": df_info})
        return response.content
    except Exception as e:
        return f"Error generating recommendations: {e}"
