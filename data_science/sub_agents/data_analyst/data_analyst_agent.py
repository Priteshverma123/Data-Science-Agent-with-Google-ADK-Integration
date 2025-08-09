import os
# import vertexai
from google.adk.agents import Agent
from data_science.utils.LLMManager import LLMManager
from data_science.sub_agents.data_analyst.prompts import return_instructions_data_analyst

from langchain_google_genai import ChatGoogleGenerativeAI
from data_science.utils.config import config, load_env_variables

# Load environment variables and get the API key for Google
env_name = load_env_variables()
api_key = getattr(config[env_name], 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))



root_agent=Agent( 
            model = "gemini-1.5-flash",
            name="senior_data_analyst",  
            instruction=return_instructions_data_analyst(),
        )




# Initialize Vertex AI first
# vertexai.init(
#     project=os.getenv("GOOGLE_CLOUD_PROJECT"),
#     location="us-central1"
# )

# Get the LLM instance from the manager
# llm_manager = LLMManager.get_instance()

# class DataAnalystAgentFactory:
#     """Factory class for creating data analyst agents"""
    
#     @staticmethod
#     def create_data_analyst_agent(streaming_callback=None):
#         """
#         Creates and returns a data analyst agent for analyzing SQL query results.
        
#         Returns:
#             Agent: A Google ADK Agent for data analysis
#         """
        
#         # Get appropriate LLM instance based on streaming requirement - IMPORTANT FIX
#         if streaming_callback:
#             llm_instance = llm_manager.get_streaming_llm(streaming_callback)
#         else:
#             llm_instance = llm_manager.get_llm()
        
#         # Create a Google ADK Agent with specific role and goal
#         data_analyst = Agent(
#             # model=os.getenv("ANALYTICS_AGENT_MODEL"),  # Use the LLM instance from manager
#             model = "gemini-1.5-flash",
#             name="senior_data_analyst",  # Agent's name/role
#             instruction=return_instructions_data_analyst(),
#         )
        
#         return data_analyst


# # Define the function to maintain compatibility with original code
# def create_data_analyst_agent(streaming_callback=None):
#     """Wrapper function to maintain compatibility with existing code"""
#     return DataAnalystAgentFactory.create_data_analyst_agent(streaming_callback)