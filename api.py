import os

from dotenv import load_dotenv
from fastapi import FastAPI
from google import genai  # Gemini (Google GenAI)
#from langchain_openai import AzureChatOpenAI  # Azure OpenAI (LangChain)
#from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini (LangChain)
from pydantic import BaseModel

from helper import DB_PATH, setup_database, text2sql

load_dotenv()

# Initialize Gemini client (Google GenAI direct SDK) — matches helper.py / main.py
genai_client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

if not os.path.exists(DB_PATH):
    setup_database()

app = FastAPI(title="Text-to-SQL API")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    sql: str
    results: list[dict]
    row_count: int


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/text2sql", response_model=QueryResponse)
def query(request: QueryRequest):
    sql, results_df = text2sql(genai_client, request.query)  # Gemini (Google GenAI)
    if results_df is not None:
        results = results_df.to_dict(orient='records')
        return QueryResponse(sql=sql, results=results, row_count=len(results))
    return QueryResponse(sql=sql, results=[], row_count=0)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
