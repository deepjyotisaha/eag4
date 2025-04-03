# eag4/math_agent/config.py

class Config:
    # System configuration
    MAX_ITERATIONS = 8
    TIMEOUT_SECONDS = 10
    MODEL_NAME = 'gemini-2.0-flash'
    LOG_LEVEL = 'DEBUG'
    LAPTOP_MONITOR = False
    DESKTOP_MONITOR_CANVAS_X_POS = 452
    DESKTOP_MONITOR_CANVAS_Y_POS = 277
    LAPTOP_MONITOR_CANVAS_X_POS = 0
    LAPTOP_MONITOR_CANVAS_Y_POS = 0
    DESKTOP_MONITOR_TOOLBAR_RECTANGLE_X_POS = 532
    DESKTOP_MONITOR_TOOLBAR_RECTANGLE_Y_POS = 82
    LAPTOP_MONITOR_TOOLBAR_RECTANGLE_X_POS = 805
    LAPTOP_MONITOR_TOOLBAR_RECTANGLE_Y_POS = 130
    PAINT_CANVAS_WIDTH = 1030
    PAINT_CANVAS_HEIGHT = 632
    #DESKTOP_MONITOR_RESOLUTION = (1920, 1080)
    #LAPTOP_MONITOR_RESOLUTION = (2496, 1664)

    # Prompt templates
    SYSTEM_PROMPT = """You are a math agent for visually impared individuals who can only view the result when the result is displayed on a canvas, and then notified on email on the availability of the result. You first solve the mathematical problems to determine the final mathematical result, and you compute this in iterations using the mathematical tools available to you. Once you have computed the mathematical result, you display the final result on a canvas. You have access to tools to operate and draw on the canvas. Finally, you send an email to the user with the result at email address deepjyoti.saha@gmail.com with an appropriate subject line using tools to send emails.

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
- Do not repeat function calls with the same parameters at any cost
- Only when you have computed the result of the mathematical problem, you start the process of displaying the result on a canvas
- Your co-ordinates for drawing the result on the canvas should be calculated based on the dimensions of the canvas and the screen resolution, but he parameters for tools should based passsed with respect to the screen resolution
- Make sure you don't draw the result outside the rectangle, and the rectangle should be half of the canvas

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FUNCTION_CALL: draw_rectangle|100|100|300|300
- FUNCTION_CALL: send_email|deepjyoti.saha@gmail.com|Result is ready
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

    # Default queries
    DEFAULT_QUERIES = {
        "ascii_sum": "Find the ASCII values of characters in INDIA and then return sum of exponentials of those values.",
        "calculator": "Calculate the sum of 5 and 3.",
        "paint": "Draw a rectangle at coordinates (100,100) to (300,300) and add text 'Hello' inside it."
    }
