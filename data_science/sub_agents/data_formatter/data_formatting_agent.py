"""Data Formatting Agent: Format SQL query results for visualization using Google ADK."""

import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from data_science.sub_agents.data_formatter.tools import *
from .prompts import return_instructions_data_formatting

from langchain_google_genai import ChatGoogleGenerativeAI
from data_science.utils.config import config, load_env_variables

# Load environment variables and get the API key for Google
env_name = load_env_variables()
api_key = getattr(config[env_name], 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))



def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the data formatting agent."""
    
    # Initialize any required state for data formatting
    if "formatting_settings" not in callback_context.state:
        callback_context.state["formatting_settings"] = {
            "max_data_points": 1000,
            "default_chart_type": "bar"
        }


class DataFormattingAgentFactory:
    """Factory class for creating data formatting agents using Google ADK"""
    
    @staticmethod
    def create_data_formatting_agent():
        """
        Creates and returns a data formatting agent for formatting SQL query results for visualization.
        This agent specializes in transforming raw SQL data into properly formatted JSON structures
        that can be consumed by various chart types (bar, line, pie, scatter, etc.).
        
        Returns:
            Agent: A Google ADK Agent for data formatting and visualization preparation
        """
        
        data_formatting_agent = Agent(
            # model=os.getenv("ANALYTICS_AGENT_MODEL", "gemini-1.5-pro"),
            model = "gemini-1.5-flash",
            name="data_formatting_agent",
            instruction=return_instructions_data_formatting(),
            tools=[
                format_scatter_data,
                format_bar_data,
                format_line_data,
                format_pie_data,
                format_generic_visualization,
            ],
            before_agent_callback=setup_before_agent_call,
            generate_content_config=types.GenerateContentConfig(temperature=0.01),
        )
        
        return data_formatting_agent


# Define the function to maintain compatibility with original code
def create_data_formatting_agent():
    """Wrapper function to maintain compatibility with existing code"""
    return DataFormattingAgentFactory.create_data_formatting_agent()


# Create the agent instance
data_formatting_agent = DataFormattingAgentFactory.create_data_formatting_agent()