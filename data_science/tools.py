"""Top level agent for data agent multi-agents.

-- it get data from database (e.g., BQ) using NL2SQL
-- then, it use data formatting, data analysis, and report generation agents for comprehensive data processing
"""

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import db_agent, ds_agent, da_agent, rs_agent



async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call database (nl2sql) agent."""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )

    agent_tool = AgentTool(agent=db_agent)

    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


async def call_ds_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data science (nl2py) agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    input_data = tool_context.state["query_result"]

    question_with_data = f"""
  Question to answer: {question}

  Actual data to analyze prevoius quesiton is already in the following:
  {input_data}

  """

    agent_tool = AgentTool(agent=ds_agent)

    ds_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["ana_agent_output"] = ds_agent_output
    return ds_agent_output


async def call_da_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call data analysis agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    # Use output from DB agent as input for data analysis
    input_data = tool_context.state["db_agent_output"]

    question_with_data = f"""
  Question to answer: {question}

  Data from database query to analyze:
  {input_data}

  """

    agent_tool = AgentTool(agent=da_agent)

    da_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["da_agent_output"] = da_agent_output
    return da_agent_output


async def call_rs_agent(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call report generation agent."""

    if question == "N/A":
        return tool_context.state["db_agent_output"]

    # Use output from DA agent as input for report generation
    input_data = tool_context.state["db_agent_output"]

    question_with_data = f"""
  Question to answer: {question}

  Analysis results to generate report from:
  {input_data}

  """

    agent_tool = AgentTool(agent=rs_agent)

    rs_agent_output = await agent_tool.run_async(
        args={"request": question_with_data}, tool_context=tool_context
    )
    tool_context.state["rs_agent_output"] = rs_agent_output
    return rs_agent_output


# Optional: Main orchestration function to chain all agents
async def process_data_pipeline(
    question: str,
    tool_context: ToolContext,
    use_ds_agent: bool = False,
    use_da_agent: bool = True,
    use_rs_agent: bool = True,
):
    """
    Orchestrate the complete data processing pipeline.
    
    Args:
        question: The user's question/request
        tool_context: Tool context containing state and settings
        use_ds_agent: Whether to use data science agent (alternative to DA agent)
        use_da_agent: Whether to use data analysis agent
        use_rs_agent: Whether to use report generation agent
    
    Returns:
        Final processed output from the pipeline
    """
    
    # Step 1: Get data from database
    db_output = await call_db_agent(question, tool_context)
    
    if use_ds_agent:
        # Alternative path: Use data science agent
        final_output = await call_ds_agent(question, tool_context)
    else:
        # Standard path: Use DA and RS agents
        final_output = db_output
        
        if use_da_agent:
            # Step 2: Analyze data
            da_output = await call_da_agent(question, tool_context)
            final_output = da_output
            
            if use_rs_agent:
                # Step 3: Generate report
                rs_output = await call_rs_agent(question, tool_context)
                final_output = rs_output
    
    return final_output

# async def call_data_analyst_agent(
#     question: str,
#     tool_context: ToolContext,
# ):
#     """Tool to call data analyst agent for data analysis."""
    
#     # Get the formatted data from the formatting agent or raw data from db agent
#     if "formatting_agent_output" in tool_context.state:
#         input_data = tool_context.state["db_agent_output"]
#         data_source = "formatted data from the data formatting agent"
#     elif "query_result" in tool_context.state:
#         input_data = tool_context.state["query_result"]
#         data_source = "raw data from the database query"
#     else:
#         return "No data available for analysis. Please run the database agent first."

#     question_with_data = f"""
#     Question to analyze: {question}

#     Data to analyze (from {data_source}):
#     {input_data}

#     Please provide detailed analysis, insights, and statistical observations about this data.
#     """

#     # Create streaming callback if available in tool context
#     streaming_callback = tool_context.state.get("streaming_callback", None)
    
#     # Create the agent using the factory
#     analyst_agent = DataAnalystAgentFactory.create_data_analyst_agent(streaming_callback)
#     agent_tool = AgentTool(agent=analyst_agent)

#     analyst_agent_output = await agent_tool.run_async(
#         args={"request": question_with_data}, tool_context=tool_context
#     )
#     tool_context.state["analyst_agent_output"] = analyst_agent_output
#     return analyst_agent_output


# async def call_report_writer_agent(
#     question: str,
#     tool_context: ToolContext,
# ):
#     """Tool to call report writer agent for generating comprehensive reports."""
    
#     # Collect all available outputs from previous agents
#     available_data = {}
    
#     if "db_agent_output" in tool_context.state:
#         available_data["database_results"] = tool_context.state["db_agent_output"]
    
#     if not available_data:
#         return "No data available for report generation. Please run the previous agents first."

#     question_with_data = f"""
#     Generate a comprehensive report for the following question: {question}

#     Available data and analysis results:
#     {available_data}

#     Please create a well-structured report that includes:
#     1. Executive summary
#     2. Key findings from the analysis
#     3. Data insights and trends
#     4. Visualizations recommendations (if applicable)
#     5. Conclusions and actionable recommendations
#     """

#     # Create streaming callback if available in tool context
#     streaming_callback = tool_context.state.get("streaming_callback", None)
    
#     # Create the agent using the factory
#     report_agent = ReportWriterAgentFactory.create_report_writer_agent(streaming_callback)
#     agent_tool = AgentTool(agent=report_agent)

#     report_agent_output = await agent_tool.run_async(
#         args={"request": question_with_data}, tool_context=tool_context
#     )
#     tool_context.state["report_agent_output"] = report_agent_output
#     return report_agent_output



# async def call_data_formatting_agent(
#     question: str,
#     tool_context: ToolContext,
# ):
#     """Tool to call data formatting agent for visualization preparation."""
    
#     # Get the raw SQL results from the database agent
#     if "query_result" not in tool_context.state:
#         return "No data available from database query. Please run the database agent first."
    
#     input_data = tool_context.state["query_result"]
    
#     question_with_data = f"""
#     Format the following SQL query results for visualization:
    
#     Original question: {question}
    
#     Raw data to format:
#     {input_data}
    
#     Please determine the most appropriate chart type and format the data accordingly.
#     """

#     # Create the agent using the factory
#     formatting_agent = DataFormattingAgentFactory.create_data_formatting_agent()
#     agent_tool = AgentTool(agent=formatting_agent)

#     formatting_agent_output = await agent_tool.run_async(
#         args={"request": question_with_data}, tool_context=tool_context
#     )
#     tool_context.state["formatting_agent_output"] = formatting_agent_output
#     return formatting_agent_output


# async def call_analysis_agent(
#     question: str,
#     tool_context: ToolContext,
# ):
#     """Tool to call the complete data science pipeline (formatting -> analysis -> reporting)."""

#     if question == "N/A":
#         return tool_context.state.get("db_agent_output", "No data available")

#     # Check if we have database results
#     if "query_result" not in tool_context.state:
#         return "No database results available. Please run the database agent first."

#     # Step 1: Format the data for visualization
#     # print("\n🔄 Step 1: Formatting data for visualization...")
#     # formatting_result = await call_data_formatting_agent(question, tool_context)
    
#     # Step 2: Analyze the data
#     print("\n🔍 Step 2: Analyzing the data...")
#     analysis_result = await call_data_analyst_agent(question, tool_context)
    
#     # Step 3: Generate comprehensive report
#     print("\n📊 Step 3: Generating comprehensive report...")
#     report_result = await call_report_writer_agent(question, tool_context)
    
#     # Store the final comprehensive output
#     comprehensive_output = {
#         # "formatting_results": formatting_result,
#         "analysis_results": analysis_result,
#         "final_report": report_result
#     }
    
#     tool_context.state["ds_agent_output"] = comprehensive_output
    
#     return report_result  # Return the final report as the main output