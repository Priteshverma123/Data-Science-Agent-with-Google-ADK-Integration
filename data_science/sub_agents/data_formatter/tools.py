"""Data formatting tools for use with Google ADK agents."""

import json
import os
import re
from decimal import Decimal

from google.adk.tools import ToolContext
from google.genai import Client
from .graph_instructions import graph_instructions

# Initialize the LLM client
project = os.getenv("BQ_PROJECT_ID", None)
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
llm_client = Client(vertexai=True, project=project, location=location)


def safe_parse_results(results):
    """Safely parse results string into a list of tuples"""
    if isinstance(results, list):
        return results
    
    if not isinstance(results, str):
        return []
    
    try:
        # Try direct eval first
        parsed = eval(results)
        if isinstance(parsed, list):
            return parsed
    except:
        pass
    
    # Try to extract data from string patterns
    patterns = [
        r'\[([^\]]+)\]',  # Match [(...), (...)]
        r'\(([^)]+)\)',   # Match individual tuples
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, results)
        if matches:
            try:
                parsed_data = []
                for match in matches:
                    if ',' in match:
                        # Split and clean the match
                        parts = [part.strip().strip("'\"") for part in match.split(',')]
                        # Convert Decimal strings back to numbers
                        converted_parts = []
                        for part in parts:
                            if 'Decimal(' in part:
                                # Extract number from Decimal('number') format
                                num_match = re.search(r"Decimal\('([^']+)'\)", part)
                                if num_match:
                                    converted_parts.append(float(num_match.group(1)))
                                else:
                                    converted_parts.append(part)
                            elif part.replace('.', '').replace('-', '').isdigit():
                                converted_parts.append(float(part))
                            else:
                                converted_parts.append(part)
                        parsed_data.append(tuple(converted_parts))
                return parsed_data
            except:
                continue
    
    return []


def convert_decimal_values(data):
    """Convert Decimal objects to float values"""
    if isinstance(data, list):
        return [convert_decimal_values(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(convert_decimal_values(item) for item in data)
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data


def format_scatter_data(
    results: str,
    tool_context: ToolContext,
) -> str:
    """Format data for scatter plot visualization. Results should be a string representation of list of tuples."""
    try:
        parsed_results = safe_parse_results(results)
        parsed_results = convert_decimal_values(parsed_results)
        
        if not parsed_results:
            return json.dumps({"error": "No data available for visualization"})
        
        formatted_data = {"series": []}
        
        if len(parsed_results[0]) == 2:
            # Simple scatter with x,y pairs
            data_points = []
            for i, (x, y) in enumerate(parsed_results):
                try:
                    x_val = float(x) if (isinstance(x, (int, float)) or 
                              (isinstance(x, str) and x.replace('.', '', 1).replace('-', '').isdigit())) else i
                    y_val = float(y) if (isinstance(y, (int, float)) or 
                              (isinstance(y, str) and y.replace('.', '', 1).replace('-', '').isdigit())) else 0
                    data_points.append({"x": x_val, "y": y_val, "id": i+1})
                except (ValueError, TypeError):
                    continue
            
            if data_points:
                formatted_data["series"].append({
                    "data": data_points,
                    "label": "Data Points"
                })
            else:
                return json.dumps({"error": "No valid data points for scatter plot"})
                
        elif len(parsed_results[0]) == 3:
            # Group data by label
            entities = {}
            
            for row in parsed_results:
                label = str(row[0])  # First item as label
                try:
                    x_val = float(row[1]) if len(row) > 1 else 0
                    y_val = float(row[2]) if len(row) > 2 else 0
                except (ValueError, TypeError):
                    x_val = 0
                    y_val = 0
                
                if label not in entities:
                    entities[label] = []
                
                entities[label].append({
                    "x": x_val,
                    "y": y_val,
                    "id": len(entities[label])+1
                })
            
            for label, data in entities.items():
                if data:
                    formatted_data["series"].append({
                        "data": data,
                        "label": label
                    })
        
        # Store formatted data in tool context
        tool_context.state["formatted_data"] = formatted_data
        
        return json.dumps({"formatted_data_for_visualization": formatted_data})
        
    except Exception as e:
        return json.dumps({"error": f"Error formatting scatter data: {str(e)}"})


def format_bar_data(
    results: str,
    question: str,
    tool_context: ToolContext,
) -> str:
    """Format data for bar chart visualization. Results should be a string representation of list of tuples."""
    try:
        parsed_results = safe_parse_results(results)
        parsed_results = convert_decimal_values(parsed_results)
            
        if not parsed_results:
            return json.dumps({"error": "No data available for visualization"})
        
        if len(parsed_results[0]) == 2:
            # Simple bar chart
            labels = [str(row[0]) for row in parsed_results]
            data = []
            
            for row in parsed_results:
                try:
                    if isinstance(row[1], (int, float)):
                        data.append(float(row[1]))
                    elif isinstance(row[1], str) and row[1].replace('.', '', 1).replace('-', '').isdigit():
                        data.append(float(row[1]))
                    else:
                        data.append(0)
                except (ValueError, TypeError):
                    data.append(0)
            
            # Get label using LLM with error handling
            try:
                prompt = f"""You are a data labeling expert. Provide a concise label for the y-axis based on the question and data.
Question: {question}
Data sample: {str(parsed_results[:2])}
Provide a short label for the y-axis."""
                
                response = llm_client.models.generate_content(
                    model=os.getenv("DATA_FORMATTING_MODEL", "gemini-1.5-flash"),
                    contents=prompt,
                    config={"temperature": 0.1},
                )
                label = response.text.strip() if response.text else "Value"
            except Exception as llm_error:
                label = "Value"  # Default fallback
            
            values = [{"data": data, "label": label}]
            
        elif len(parsed_results[0]) == 3:
            # Multi-series bar chart
            categories = set()
            entities = set()
            
            for row in parsed_results:
                entities.add(str(row[0]))
                categories.add(str(row[1]))
            
            labels = list(categories)
            entities_list = list(entities)
            
            values = []
            for entity in entities_list:
                entity_data = []
                for category in labels:
                    matching_rows = [row for row in parsed_results 
                                   if str(row[0]) == str(entity) and str(row[1]) == str(category)]
                    if matching_rows:
                        try:
                            val = float(matching_rows[0][2]) if len(matching_rows[0]) > 2 else 0
                            entity_data.append(val)
                        except (ValueError, TypeError):
                            entity_data.append(0)
                    else:
                        entity_data.append(0)
                
                values.append({"data": entity_data, "label": str(entity)})
        
        formatted_data = {
            "labels": labels,
            "values": values
        }
        
        # Store formatted data in tool context
        tool_context.state["formatted_data"] = formatted_data
        
        return json.dumps({"formatted_data_for_visualization": formatted_data})
        
    except Exception as e:
        return json.dumps({"error": f"Error formatting bar data: {str(e)}"})


def format_line_data(
    results: str,
    question: str,
    tool_context: ToolContext,
) -> str:
    """Format data for line chart visualization. Results should be a string representation of list of tuples."""
    try:
        parsed_results = safe_parse_results(results)
        parsed_results = convert_decimal_values(parsed_results)
            
        if not parsed_results:
            return json.dumps({"error": "No data available for visualization"})
        
        if len(parsed_results[0]) == 2:
            # Simple line chart
            x_values = [str(row[0]) for row in parsed_results]
            y_values = []
            
            for row in parsed_results:
                try:
                    if isinstance(row[1], (int, float)):
                        y_values.append(float(row[1]))
                    elif isinstance(row[1], str) and row[1].replace('.', '', 1).replace('-', '').isdigit():
                        y_values.append(float(row[1]))
                    else:
                        y_values.append(0)
                except (ValueError, TypeError):
                    y_values.append(0)
            
            # Get label using LLM with error handling
            try:
                prompt = f"""You are a data labeling expert. Provide a concise label for the y-axis.
Question: {question}
Data sample: {str(parsed_results[:2])}
Provide a short label for the y-axis."""
                
                response = llm_client.models.generate_content(
                    model=os.getenv("DATA_FORMATTING_MODEL", "gemini-1.5-flash"),
                    contents=prompt,
                    config={"temperature": 0.1},
                )
                label = response.text.strip() if response.text else "Value"
            except Exception as llm_error:
                label = "Value"  # Default fallback
            
            formatted_data = {
                "xValues": x_values,
                "yValues": [{"data": y_values, "label": label}]
            }
            
        elif len(parsed_results[0]) == 3:
            # Multi-series line chart
            data_by_label = {}
            x_values = []
            
            for row in parsed_results:
                label = str(row[0])  # First column as label
                x_value = str(row[1])  # Second column as x-axis
                try:
                    y_value = float(row[2])  # Third column as y-axis
                except (ValueError, TypeError):
                    y_value = 0
                
                if x_value not in x_values:
                    x_values.append(x_value)
                
                if label not in data_by_label:
                    data_by_label[label] = []
                
                data_by_label[label].append(y_value)
            
            y_values = [{"data": data, "label": label} for label, data in data_by_label.items()]
            
            formatted_data = {
                "xValues": x_values,
                "yValues": y_values
            }
        
        # Store formatted data in tool context
        tool_context.state["formatted_data"] = formatted_data
        
        return json.dumps({"formatted_data_for_visualization": formatted_data})
        
    except Exception as e:
        return json.dumps({"error": f"Error formatting line data: {str(e)}"})


def format_pie_data(
    results: str,
    tool_context: ToolContext,
) -> str:
    """Format data for pie chart visualization. Results should be a string representation of list of tuples."""
    try:
        parsed_results = safe_parse_results(results)
        parsed_results = convert_decimal_values(parsed_results)
            
        if not parsed_results:
            return json.dumps({"error": "No data available for visualization"})
        
        formatted_data = []
        
        if len(parsed_results[0]) == 2:
            for i, (label, value) in enumerate(parsed_results):
                try:
                    if isinstance(value, (int, float)):
                        val = float(value)
                    elif isinstance(value, str) and value.replace('.', '', 1).replace('-', '').isdigit():
                        val = float(value)
                    else:
                        val = 0
                        
                    formatted_data.append({
                        "id": i,
                        "value": val,
                        "label": str(label)
                    })
                except (ValueError, TypeError):
                    continue
        else:
            return json.dumps({"error": "Pie chart requires exactly 2 columns (label, value)"})
        
        # Store formatted data in tool context
        tool_context.state["formatted_data"] = formatted_data
        
        return json.dumps({"formatted_data_for_visualization": formatted_data})
        
    except Exception as e:
        return json.dumps({"error": f"Error formatting pie data: {str(e)}"})


def format_generic_visualization(
    visualization_type: str,
    results: str,
    question: str,
    tool_context: ToolContext,
    sql_query: str = "",
) -> str:
    """Format data for any visualization type using LLM when specific formatters are not available."""
    try:
        if visualization_type not in graph_instructions:
            visualization_type = "bar"  # Default fallback
            
        instructions = graph_instructions[visualization_type]
        
        # Parse results first
        parsed_results = safe_parse_results(results)
        parsed_results = convert_decimal_values(parsed_results)
        
        if not parsed_results:
            return json.dumps({"error": "No data available for visualization"})
        
        prompt = f"""You are a Data expert who formats data according to the required needs. Format the provided data into valid JSON matching the format specification.

For the question: {question}

SQL query: {sql_query}

Result: {str(parsed_results)}

Use this format: {instructions}

Return only valid JSON with no additional text."""
        
        try:
            response = llm_client.models.generate_content(
                model=os.getenv("DATA_FORMATTING_MODEL", "gemini-1.5-flash"),
                contents=prompt,
                config={"temperature": 0.1},
            )
            response_text = response.text if response.text else ""
        except Exception as llm_error:
            # Fallback to simple formatting if LLM fails
            if visualization_type == "bar" and len(parsed_results[0]) == 2:
                fallback_data = {
                    "labels": [str(row[0]) for row in parsed_results],
                    "values": [{"data": [float(row[1]) for row in parsed_results], "label": "Values"}]
                }
                tool_context.state["formatted_data"] = fallback_data
                return json.dumps({"formatted_data_for_visualization": fallback_data})
            else:
                return json.dumps({"error": f"LLM formatting failed: {str(llm_error)}"})
        
        # Clean and extract JSON
        cleaned_response = response_text.strip()
        json_start = cleaned_response.find('{')
        json_end = cleaned_response.rfind('}')
        
        if json_start >= 0 and json_end > json_start:
            json_string = cleaned_response[json_start:json_end+1]
            try:
                formatted_data = json.loads(json_string)
                tool_context.state["formatted_data"] = formatted_data
                return json.dumps({"formatted_data_for_visualization": formatted_data})
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire response
        try:
            formatted_data = json.loads(cleaned_response)
            tool_context.state["formatted_data"] = formatted_data
            return json.dumps({"formatted_data_for_visualization": formatted_data})
        except json.JSONDecodeError:
            return json.dumps({"error": "Failed to format data for visualization", "raw_response": response_text})
            
    except Exception as e:
        return json.dumps({"error": f"Error in generic formatting: {str(e)}"})