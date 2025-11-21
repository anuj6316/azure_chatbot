from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, RootModel
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
import os
import json
from dotenv import load_dotenv
from .logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

client = ChatOpenAI(
    api_key = os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
    model='mistralai/mixtral-8x7b-instruct'
)

query_decomposition_prompt = """
You are a Query Decomposition Engine designed to break a user's question into 
minimal, independent sub-queries for a Retrieval-Augmented Generation (RAG) system.

### STRICT RULES
1. Do NOT add any new information not present in the user's query.
2. Do NOT assume facts, names, places, or contexts.
3. If the query is already atomic, return only one sub-query (the same query).
4. If the user’s input is ambiguous, unclear, too short, or missing context,
   generate clarifying sub-queries — NOT assumptions.
5. Each sub-query MUST be self-contained, short, and focus on retrieving facts.
6. NEVER rewrite sub-queries with explanations. Only the queries themselves.
7. Output MUST be in VALID JSON array format:
   ["subquery1", "subquery2", ...]

### EDGE CASES TO HANDLE
- If query contains multiple questions → split them.
- If query contains reasoning steps → extract factual needs.
- If query references pronouns ("it", "they") → resolve using only explicit context.
- If query is too vague → generate clarifying questions as sub-queries.
- If query contains tasks (e.g., summarize, compare, explain) → break into required factual retrieval parts.
- If query involves steps or workflows → break into factual components only.
- If query contains data science problems → identify all needed knowledge pieces.

### IMPORTANT CONSTRAINTS
- Do NOT generate more than 7 sub-queries.
- Do NOT hallucinate domain knowledge.
- Sub-queries should focus only on what needs to be retrieved, NOT how to answer.
- If nothing can be decomposed → return the user’s query as a single-element array.

### OUTPUT FORMAT EXAMPLES
Input: "Explain how transformers work and compare them with RNNs."
Output:
[
  "What is the architecture of transformers?",
  "How do transformers process sequences?",
  "What is the architecture of RNNs?",
  "How do RNNs process sequences?",
  "What are the key differences between transformers and RNNs?"
]

Input: "Tell me what it means."
Output:
[
  "What is the referent of 'it' in the user's query?",
  "What meaning does the user intend for 'it'?"
]

Input: "GDP of India"
Output:
[
  "What is the GDP of India?"
]

---

### Now decompose the following user query into sub-queries following all rules:

User Query: {query}
"""



prompt_template = ChatPromptTemplate.from_template(
    query_decomposition_prompt,
)

def process_output(output: str):
    output = output.replace('[', '')
    output = output.replace(']', '')
    output = output.replace('\n',"")
    return output.strip().split(',')

def process_query_decomposition(query: str):
    logger.info(f"Decomposing query: {query}")
    query_decomposition_chain = prompt_template | client 
    response = query_decomposition_chain.invoke({"query": query})
    output = process_output(response.content)
    logger.info(f"Decomposed into {len(output)} sub-queries")
    return output

if __name__ == "__main__":
    result = process_query_decomposition('show me the types of machine learning concepts.')
    for i in result:
        print(i.strip())