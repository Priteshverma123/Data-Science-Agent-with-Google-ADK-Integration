"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use data formatting, analysis, and report generation agents for comprehensive data processing
"""
import os
from datetime import date

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts

from data_science.utils.config import config, load_env_variables

# Load environment variables and get the API key for Google
env_name = load_env_variables()
api_key = getattr(config[env_name], 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))


from .sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)
from .prompts import return_instructions_root
from .tools import (
    call_db_agent, 
    call_ds_agent, 
    call_da_agent,
    call_rs_agent
)

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent."""

    # setting up database settings in session.state
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # setting up schema in instruction
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_root()
            + f"""

    --------- The BigQuery schema of the relevant data with a few sample rows. ---------
    {schema}

    """
        )


root_agent = Agent(
    # model=os.getenv("ROOT_AGENT_MODEL"),
    model = "gemini-1.5-flash",
    name="db_ds_multiagent",
    instruction=return_instructions_root(),
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Todays date: {date_today}
        """
    ),
    tools=[
        call_db_agent,
        call_ds_agent,
        call_da_agent,
        call_rs_agent,
        load_artifacts,
    ],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)