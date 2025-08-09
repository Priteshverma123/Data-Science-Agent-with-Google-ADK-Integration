import os
# import vertexai
from google.adk.agents import Agent
from data_science.utils.LLMManager import LLMManager
from data_science.sub_agents.report_agent.prompts import return_instructions_report_writer

from langchain_google_genai import ChatGoogleGenerativeAI
from data_science.utils.config import config, load_env_variables

# Load environment variables and get the API key for Google
env_name = load_env_variables()
api_key = getattr(config[env_name], 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))



root_agent=Agent(
            # model=os.getenv("ANALYTICS_AGENT_MODEL"),  # Use the LLM instance from manager
            model = "gemini-1.5-flash",
            name="Report_Writer",  # Agent's name/role
            instruction=return_instructions_report_writer(),
        )

# Initialize Vertex AI first
# vertexai.init(
#     project=os.getenv("GOOGLE_CLOUD_PROJECT"),
#     location="us-central1"
# )

# Get the LLM instance from the manager
# llm_manager = LLMManager.get_instance()

# class ReportWriterAgentFactory:
#     """Factory class for creating report writer agents"""

#     @staticmethod
#     def create_report_writer_agent(streaming_callback=None):
#         """
#         Creates and returns a report writer agent for summarizing data analysis.

#         Returns:
#             Agent: A Google ADK Agent for report writing
#         """
        
#         # Get appropriate LLM instance based on streaming requirement - IMPORTANT FIX
#         if streaming_callback:
#             llm_instance = llm_manager.get_streaming_llm(streaming_callback)
#         else:
#             llm_instance = llm_manager.get_llm()
        
#         # Create a Google ADK Agent with a specific role and goal
#         report_writer = Agent(
#             # model=os.getenv("ANALYTICS_AGENT_MODEL"),  # Use the LLM instance from manager
#             model = "gemini-1.5-flash",
#             name="Report_Writer",  # Agent's name/role
#             instruction=return_instructions_report_writer(),
#         )
        
#         return report_writer

# # Wrapper function to maintain compatibility with existing code
# def create_report_writer_agent(streaming_callback=None):
#     """Wrapper function to maintain compatibility with existing code"""
#     return ReportWriterAgentFactory.create_report_writer_agent(streaming_callback)