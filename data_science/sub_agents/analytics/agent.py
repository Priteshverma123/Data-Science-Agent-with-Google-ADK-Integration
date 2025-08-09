#

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""
import os
import vertexai
from google.adk.code_executors import VertexAiCodeExecutor
# from google.adk.code_executors import LocalCodeExecutor
from google.adk.agents import Agent
from .prompts import return_instructions_ds
# from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Vertex AI with correct region FIRST
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1"
)

root_agent = Agent(
    # model=os.getenv("ANALYTICS_AGENT_MODEL"),
    model = "gemini-1.5-flash",
    # model=ChatGoogleGenerativeAI(model="gemini-2.0-flash-001"),
    name="data_science_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
)