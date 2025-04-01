# eag4/math_agent/config.py

class Config:
    # System configuration
    MAX_ITERATIONS = 3
    TIMEOUT_SECONDS = 10
    MODEL_NAME = 'gemini-2.0-flash'
    LOG_LEVEL = 'DEBUG'

    # Prompt templates
    SYSTEM_PROMPT = """You are a math agent solving problems in iterations. You have access to various mathematical tools.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [number]

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- Do not repeat function calls with the same parameters

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

    # Default queries
    DEFAULT_QUERIES = {
        "ascii_sum": "Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.",
        "calculator": "Calculate the sum of 5 and 3.",
        "paint": "Draw a rectangle at coordinates (100,100) to (300,300) and add text 'Hello' inside it."
    }
