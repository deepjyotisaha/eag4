import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
#from google import genai
import google.generativeai as genai
from concurrent.futures import TimeoutError
from functools import partial
import logging
import sys
from datetime import datetime
from config import Config

# Configure logging at the start of your file, after the imports
logging.basicConfig(
    #filename='mcp_client.log',
    #filemode='a',  # append mode
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)20s() %(message)s',
    handlers=[
        logging.FileHandler('mcp_client.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

logging.info("Configuring Gemini API...")
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(Config.MODEL_NAME)
    logging.info("Gemini API configured successfully")
except Exception as e:
    logging.error(f"Error configuring Gemini API: {str(e)}")
    raise

max_iterations = Config.MAX_ITERATIONS
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(prompt, timeout=Config.TIMEOUT_SECONDS):
    """Generate content with a timeout"""
    logging.info("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: model.generate_content(
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        logging.info("LLM generation completed")
        return response
    except TimeoutError:
        logging.error("LLM generation timed out!")
        raise
    except Exception as e:
        logging.error(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

'''
async def init_gmail_server():
    logging.info("Starting Gmail server initialization...")
    gmail_server_params = StdioServerParameters(
        command="python",
        args=[
            "gmail-mcp-server/src/gmail/server.py",
            "--creds-file-path=.google/client_creds.json",
            "--token-path=.google/app_tokens.json"
        ]
    )
    try:
        logging.info("Creating Gmail server connection...")
        async with stdio_client(gmail_server_params) as (gmail_read, gmail_write):
            logging.info("Gmail server connection established, creating session...")
            async with ClientSession(gmail_read, gmail_write) as gmail_session:
                logging.info("Initializing Gmail session...")
                await gmail_session.initialize()
                logging.info("Getting Gmail tools...")
                tools_result = await gmail_session.list_tools()
                gmail_tools = tools_result.tools
                logging.info(f"Gmail server tools: {len(gmail_tools)}")
                for tool in gmail_tools:
                    tool.server_session = gmail_session
                return gmail_tools, gmail_session
    except Exception as e:
        logging.error(f"Error in Gmail server initialization: {str(e)}")
        logging.error("Stack trace:", exc_info=True)
        raise

async def init_math_server():
    logging.info("Starting math server initialization...")
    math_server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]  # Remove "stdio" argument - it's handled internally
    )
    try:
        logging.info("Creating math server connection...")
        async with stdio_client(math_server_params) as (math_read, math_write):
            logging.info("Math server connection established, creating session...")
            async with ClientSession(math_read, math_write) as math_session:
                logging.info("Initializing math session...")
                await math_session.initialize()
                logging.info("Getting math tools...")
                tools_result = await math_session.list_tools()
                math_tools = tools_result.tools
                logging.info(f"Math server tools: {len(math_tools)}")
                for tool in math_tools:
                    tool.server_session = math_session
                return math_tools, math_session
    except Exception as e:
        logging.error(f"Error in math server initialization: {str(e)}")
        logging.error("Stack trace:", exc_info=True)
        raise

async def initialize_servers():
    """Initialize both MCP and Gmail servers and combine their tools"""
    logging.info("Initializing both servers...")
    try:
        # Initialize both servers
        math_tools, math_session = await init_math_server()
        logging.info("Math server initialized successfully")
        
        gmail_tools, gmail_session = await init_gmail_server()
        logging.info("Gmail server initialized successfully")
        
        # Combine tools (extend the list instead of adding sessions)
        combined_tools = []
        combined_tools.extend(math_tools)
        combined_tools.extend(gmail_tools)
        
        logging.info(f"Combined tools: {len(combined_tools)}")
        
        return combined_tools, math_session, gmail_session
    except Exception as e:
        logging.error(f"Error in server initialization: {str(e)}")
        logging.error("Stack trace:", exc_info=True)
        raise

async def main():
    reset_state()
    logging.info("Starting main execution with multiple servers...")
    
    math_session = None
    gmail_session = None
    
    try:
        # Initialize servers
        tools, math_session, gmail_session = await initialize_servers()

        try:
            # Create tools description
            tools_description = []
            for i, tool in enumerate(tools):
                try:
                    params = tool.inputSchema
                    desc = getattr(tool, 'description', 'No description available')
                    name = getattr(tool, 'name', f'tool_{i}')
                
                    if 'properties' in params:
                        param_details = []
                        for param_name, param_info in params['properties'].items():
                            param_type = param_info.get('type', 'unknown')
                            param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                    else:
                        params_str = 'no parameters'

                    tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                    tools_description.append(tool_desc)
                
                except Exception as e:
                    logging.error(f"Error processing tool {i}: {e}")
                    tools_description.append(f"{i+1}. Error processing tool")
        
            tools_description = "\n".join(tools_description)
        
        except Exception as e:
            logging.error(f"Error creating tools description: {e}")

        logging.info(f"Number of tools: {len(tools)}")
        logging.info(f"Tools description: {tools_description}")
        logging.info(f"Successfully retrieved {len(tools)} tools")

        logging.info("Created system prompt...")
                
        system_prompt = Config.SYSTEM_PROMPT.format(tools_description=tools_description)
        query = Config.DEFAULT_QUERIES["ascii_sum"]

        logging.info("Starting iteration loop...")
        logging.debug(f"Query: {query}")
        logging.debug(f"System prompt: {system_prompt}")
                
        # Use global iteration variables
        global iteration, last_response
                
        while iteration < max_iterations:
            logging.info(f"\n--- Iteration {iteration + 1} ---")
            if last_response is None:
                current_query = query
            else:
                current_query = current_query + "\n\n" + " ".join(iteration_response)
                current_query = current_query + "  What should I do next?"

            # Get model's response with timeout
            logging.info("Preparing to generate LLM response...")
            prompt = f"{system_prompt}\n\nQuery: {current_query}"
            #logging.debug(f"Prompt: {prompt}")
            try:
                response = await generate_with_timeout(prompt)
                response_text = response.text.strip()
                logging.info(f"LLM Response: {response_text}")
                        
                # Find the FUNCTION_CALL line in the response
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith("FUNCTION_CALL:"):
                        response_text = line
                        break
                        
            except Exception as e:
                    logging.error(f"Failed to get LLM response: {e}")
                    break


            if response_text.startswith("FUNCTION_CALL:"):
                _, function_info = response_text.split(":", 1)
                parts = [p.strip() for p in function_info.split("|")]
                func_name, params = parts[0], parts[1:]
                        
                logging.info(f"\nDEBUG: Raw function info: {function_info}")
                logging.info(f"DEBUG: Split parts: {parts}")
                logging.info(f"DEBUG: Function name: {func_name}")
                logging.info(f"DEBUG: Raw parameters: {params}")
                        
                try:
                    # Find the matching tool to get its input schema
                    tool = next((t for t in tools if t.name == func_name), None)
                    if not tool:
                        logging.info(f"DEBUG: Available tools: {[t.name for t in tools]}")
                        raise ValueError(f"Unknown tool: {func_name}")

                    logging.info(f"DEBUG: Found tool: {tool.name}")
                    logging.info(f"DEBUG: Tool schema: {tool.inputSchema}")

                    # Get the correct session from the tool
                    session = tool.server_session
                    if not session:
                        raise ValueError(f"No session found for tool: {func_name}")

                    # Prepare arguments according to the tool's input schema
                    arguments = {}
                    schema_properties = tool.inputSchema.get('properties', {})
                    logging.info(f"DEBUG: Schema properties: {schema_properties}")
                    logging.info(f"DEBUG: Server Session: {session}")

                    for param_name, param_info in schema_properties.items():
                        if not params:  # Check if we have enough parameters
                            raise ValueError(f"Not enough parameters provided for {func_name}")
                            
                        value = params.pop(0)  # Get and remove the first parameter
                        param_type = param_info.get('type', 'string')
                        
                        logging.info(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
                        
                        # Convert the value to the correct type based on the schema
                        if param_type == 'integer':
                            arguments[param_name] = int(value)
                        elif param_type == 'number':
                            arguments[param_name] = float(value)
                        elif param_type == 'array':
                            # Handle array input
                            if isinstance(value, str):
                                value = value.strip('[]').split(',')
                            arguments[param_name] = [int(x.strip()) for x in value]
                        else:
                            arguments[param_name] = str(value)

                    logging.info(f"DEBUG: Final arguments: {arguments}")
                    logging.info(f"DEBUG: Calling tool {func_name}")
                    
                    result = await session.call_tool(func_name, arguments=arguments)
                    logging.info(f"DEBUG: Raw result: {result}")
                    
                    # Get the full result content
                    if hasattr(result, 'content'):
                        logging.info(f"DEBUG: Result has content attribute")
                        # Handle multiple content items
                        if isinstance(result.content, list):
                            iteration_result = [
                                item.text if hasattr(item, 'text') else str(item)
                                for item in result.content
                            ]
                        else:
                            iteration_result = str(result.content)
                    else:
                        logging.info(f"DEBUG: Result has no content attribute")
                        iteration_result = str(result)
                        
                    logging.info(f"DEBUG: Final iteration result: {iteration_result}")
                    
                    # Format the response based on result type
                    if isinstance(iteration_result, list):
                        result_str = f"[{', '.join(iteration_result)}]"
                    else:
                        result_str = str(iteration_result)
                    
                    iteration_response.append(
                        f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                        f"and the function returned {result_str}."
                    )
                    last_response = iteration_result

                except Exception as e:
                    logging.error(f"DEBUG: Error details: {str(e)}")
                    logging.error(f"DEBUG: Error type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                    break

                if response_text.startswith("FINAL_ANSWER:"):
                    logging.info("\n=== Agent Execution Complete ===")

                iteration += 1

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure proper cleanup
        if math_session:
            try:
                await math_session.close()
            except Exception as e:
                logging.error(f"Error closing math session: {e}")
        
        if gmail_session:
            try:
                await gmail_session.close()
            except Exception as e:
                logging.error(f"Error closing gmail session: {e}")
        reset_state()  # Reset at the end of main
'''

async def main():
    reset_state()  # Reset at the start of main
    logging.info("Starting main execution...")
    try:
        # Create a single MCP server connection
        logging.info("Establishing connection to MCP server...")
        
        math_server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )

        gmail_server_params = StdioServerParameters(
            command="python",
            args=[
                "gmail-mcp-server/src/gmail/server.py",
                "--creds-file-path=.google/client_creds.json",
                "--token-path=.google/app_tokens.json"
            ]
        )

        async with stdio_client(math_server_params) as (math_read, math_write), \
            stdio_client(gmail_server_params) as (gmail_read, gmail_write):
            logging.info("Connection established, creating session...")
            async with ClientSession(math_read, math_write) as math_session, \
                ClientSession(gmail_read, gmail_write) as gmail_session:
                logging.info("Session created, initializing...")
                await math_session.initialize()
                await gmail_session.initialize()
                
                # Get available tools
                logging.info("Requesting tool list...")
                tools_result = await math_session.list_tools()
                math_tools = tools_result.tools
                logging.info(f"Math server tools: {len(math_tools)}")
                for tool in math_tools:
                    tool.server_session = math_session
                logging.info(f"Successfully retrieved {len(math_tools)} math tools")
              

                tools_result = await gmail_session.list_tools()
                gmail_tools = tools_result.tools
                logging.info(f"Gmail server tools: {len(gmail_tools)}")
                for tool in gmail_tools:
                    tool.server_session = gmail_session
                logging.info(f"Successfully retrieved {len(gmail_tools)} gmail tools")

                # Combine tools (extend the list instead of adding sessions)
                tools = math_tools + gmail_tools
                #tools.extend(math_tools)
                #tools.extend(gmail_tools)
        
                logging.info(f"Combined tools: {len(tools)}")
               
                # Create system prompt with available tools
                logging.info("Creating system prompt...")
                logging.info(f"Number of tools: {len(tools)}")
                
                try:
                    # First, let's inspect what a tool object looks like
                    # if tools:
                    #     print(f"First tool properties: {dir(tools[0])}")
                    #     print(f"First tool example: {tools[0]}")
                    
                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            # Get tool properties
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            
                            # Format the input schema in a more readable way
                            if 'properties' in params:
                                param_details = []
                                for param_name, param_info in params['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            logging.info(f"Added description for tool: {tool_desc}")
                        except Exception as e:
                            logging.error(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                    
                    tools_description = "\n".join(tools_description)
                    logging.info("Successfully created tools description")
                except Exception as e:
                    logging.error(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"
                
                logging.info("Created system prompt...")
                
                system_prompt = Config.SYSTEM_PROMPT.format(tools_description=tools_description)
                query = Config.DEFAULT_QUERIES["ascii_sum"]

                logging.info("Starting iteration loop...")
                #logging.debug(f"Query: {query}")
                #logging.debug(f"System prompt: {system_prompt}")
                
                # Use global iteration variables
                global iteration, last_response
                
                while iteration < max_iterations:
                    logging.info(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    logging.info("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    #logging.debug(f"Prompt: {prompt}")
                    try:
                        response = await generate_with_timeout(prompt)
                        response_text = response.text.strip()
                        logging.info(f"LLM Response: {response_text}")
                        
                        # Find the FUNCTION_CALL line in the response
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:"):
                                response_text = line
                                break
                        
                    except Exception as e:
                        logging.error(f"Failed to get LLM response: {e}")
                        break


                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        
                        logging.info(f"\nDEBUG: Raw function info: {function_info}")
                        logging.info(f"DEBUG: Split parts: {parts}")
                        logging.info(f"DEBUG: Function name: {func_name}")
                        logging.info(f"DEBUG: Raw parameters: {params}")
                        
                        try:
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                logging.info(f"DEBUG: Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")

                            logging.info(f"DEBUG: Found tool: {tool.name}")
                            logging.info(f"DEBUG: Tool schema: {tool.inputSchema}")

                            # Get the correct session from the tool
                            session = tool.server_session
                            if not session:
                                raise ValueError(f"No session found for tool: {func_name}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            logging.info(f"DEBUG: Schema properties: {schema_properties}")

                            for param_name, param_info in schema_properties.items():
                                if not params:  # Check if we have enough parameters
                                    raise ValueError(f"Not enough parameters provided for {func_name}")
                                    
                                value = params.pop(0)  # Get and remove the first parameter
                                param_type = param_info.get('type', 'string')
                                
                                logging.info(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
                                
                                # Convert the value to the correct type based on the schema
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    # Handle array input
                                    if isinstance(value, str):
                                        value = value.strip('[]').split(',')
                                    arguments[param_name] = [int(x.strip()) for x in value]
                                else:
                                    arguments[param_name] = str(value)

                            logging.info(f"DEBUG: Final arguments: {arguments}")
                            logging.info(f"DEBUG: Calling tool {func_name}")
                            
                            #result = await tools.server_session.call_tool(func_name, arguments=arguments)
                            result = await session.call_tool(func_name, arguments=arguments)
                            logging.info(f"DEBUG: Raw result: {result}")
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                logging.info(f"DEBUG: Result has content attribute")
                                # Handle multiple content items
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                logging.info(f"DEBUG: Result has no content attribute")
                                iteration_result = str(result)
                                
                            logging.info(f"DEBUG: Final iteration result: {iteration_result}")
                            
                            # Format the response based on result type
                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)
                            
                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                f"and the function returned {result_str}."
                            )
                            last_response = iteration_result

                        except Exception as e:
                            logging.error(f"DEBUG: Error details: {str(e)}")
                            logging.error(f"DEBUG: Error type: {type(e)}")
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break

                    elif response_text.startswith("FINAL_ANSWER:"):
                        logging.info("\n=== Agent Execution Complete ===")

                    iteration += 1

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_state()  # Reset at the end of main



if __name__ == "__main__":
    asyncio.run(main())
    
    
