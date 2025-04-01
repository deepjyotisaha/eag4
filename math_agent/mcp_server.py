# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32api  # Add this import
import win32con
import time
from win32api import GetSystemMetrics
import logging
from config import Config

# Configure logging at the start of your file
logging.basicConfig(
    #filename='mcp_server.log',
    #filemode='w',  # 'w' means write/overwrite (instead of 'a' for append)
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)20s() %(message)s',
        handlers=[
        logging.FileHandler('mcp_server.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> PILImage.Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint Canvas ready for drawing maximized on primary monitor with initialization verification"""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        
        # Get the Paint window with a timeout/retry mechanism
        max_retries = 10
        retry_count = 0
        paint_window = None
        
        while retry_count < max_retries:
            try:
                paint_window = paint_app.window(class_name='MSPaintApp')
                # Try to access window properties to verify it exists
                if paint_window.exists() and paint_window.is_visible():
                    break
            except Exception as e:
                logging.info(f"Attempt {retry_count + 1}: Waiting for Paint window to initialize...")
                time.sleep(0.5)
                retry_count += 1
        
        if not paint_window or not paint_window.exists():
            raise Exception("Failed to initialize Paint window")
        
        # Ensure window is active and visible
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
            
        logging.info("Paint window found, verifying UI elements...")
        
        # Verify canvas is accessible
        retry_count = 0
        canvas = None
        while retry_count < max_retries:
            try:
                canvas = paint_window.child_window(class_name='MSPaintView')
                time.sleep(0.5)
                if canvas.exists() and canvas.is_visible():
                    logging.info("Canvas element found and verified")
                    logging.info(f"Canvas dimensions: {canvas.rectangle()}")
                    break
            except Exception as e:
                logging.info(f"Attempt {retry_count + 1}: Waiting for canvas to initialize...")
                time.sleep(0.5)
                retry_count += 1
                
        if not canvas or not canvas.exists():
            raise Exception("Failed to verify Paint canvas")
            
        # Get monitor information
        monitor_count = win32api.GetSystemMetrics(win32con.SM_CMONITORS)
        primary_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        primary_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        logging.info(f"\n{'='*20} Display Configuration {'='*20}")
        logging.info(f"Total number of monitors: {monitor_count}")
        #logging.info(f"Primary Monitor Resolution: {primary_width}x{primary_height}")
        
        # Position window
        if monitor_count > 1:
            target_x = primary_width + 100
            target_y = 100
            
            logging.info(f"Positioning Paint window at: x={target_x}, y={target_y}")
            win32gui.SetWindowPos(
                paint_window.handle,
                win32con.HWND_TOP,
                target_x, target_y,
                0, 0,
                win32con.SWP_NOSIZE
            )
            
        # Maximize and verify window state
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.5)

        # Verify window is maximized
        retry_count = 0
        while retry_count < max_retries:
            try:
                window_placement = win32gui.GetWindowPlacement(paint_window.handle)
                if window_placement[1] == win32con.SW_SHOWMAXIMIZED:
                    logging.info("Window successfully maximized")
                    break
            except Exception as e:
                logging.info(f"Attempt {retry_count + 1}: Waiting for window to maximize...")
                time.sleep(0.5)
                retry_count += 1
                
        # Final verification - try to access key UI elements
        try:
            # Try to access the ribbon/toolbar area
            paint_window.click_input(coords=(532, 82))
            time.sleep(0.2)
            # Click back to canvas area
            canvas.click_input(coords=(100, 100))
            logging.info("UI elements verified and accessible")
        except Exception as e:
            logging.error(f"Failed to verify UI elements: {str(e)}")
            raise

        time.sleep(1)    
        logging.info("Paint initialization complete and verified")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Microsoft Paint Canvas opened and ready for drawing. All UI elements accessible. Detected {monitor_count} monitor(s)."
                )
            ]
        }
    except Exception as e:
        logging.error(f"Error in open_paint: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def get_canvas_resolution() -> dict:
    """Get the resolution of the Microsoft Paint canvas with proper verification"""
    try:
        # Get monitor information
        monitor_count = win32api.GetSystemMetrics(win32con.SM_CMONITORS)
        primary_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        primary_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        logging.info(f"\n{'='*20} Display Configuration {'='*20}")
        logging.info(f"Total number of monitors: {monitor_count}")
        logging.info(f"Primary Monitor Resolution: {primary_width}x{primary_height}")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Canvas resolution: Width={primary_width}, Height={primary_height}"
                )
            ]
        }
    except Exception as e:
        logging.error(f"Error getting canvas resolution: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error getting canvas resolution: {str(e)}"
                )
            ]
        }   

@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a black rectangle in Microsoft Paint Canvas from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        logging.info(f"Starting rectangle drawing operation from ({x1},{y1}) to ({x2},{y2})")
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active and wait for it to be fully ready
        if not paint_window.has_focus():
            logging.info("Setting Paint window focus")
            paint_window.set_focus()
            time.sleep(1)  # Increased wait time
        
        # Get window position and size
        window_rect = win32gui.GetWindowRect(paint_window.handle)
        logging.info(f"Paint window rectangle: {window_rect}")
        
        # Calculate toolbar position (relative to window)
        toolbar_x = 532  # Default x coordinate for rectangle tool
        toolbar_y = 82   # Default y coordinate for rectangle tool

        if Config.LAPTOP_MONITOR == True:
            toolbar_x = 805
            toolbar_y = 130
        
        logging.info(f"Clicking rectangle tool at ({toolbar_x}, {toolbar_y})")
        paint_window.click_input(coords=(toolbar_x, toolbar_y))
        time.sleep(0.5)  # Wait for tool selection
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        # Try drawing with mouse input
        try:
            # Move to start position first
            canvas.click_input(coords=(x1, y1))
            time.sleep(0.2)
      
            # Draw the rectangle
            canvas.press_mouse_input(coords=(x1, y1))
            time.sleep(0.2)
            canvas.move_mouse_input(coords=(x2, y2))
            time.sleep(0.2)
            canvas.release_mouse_input(coords=(x2, y2))
            time.sleep(0.2)
          
            logging.info("Rectangle drawing completed")
            
        except Exception as e:
            logging.error(f"Failed to draw rectangle: {str(e)}")
            raise
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Black Rectangle drawn on Microsoft Paint Canvas from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        logging.error(f"Error in draw_rectangle: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing black rectangle on Microsoft Paint Canvas: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str, x: int, y: int, width: int = 200, height: int = 100) -> dict:
    """
    Draw text in Microsoft Paint Canvas at specified coordinates starting from (x,y) within the box of size (width, height)
    
    """
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        logging.info(f"Expected: Starting text addition operation: '{text}' at ({x}, {y}) with box size ({width}, {height})")


        #temp_x = x
        #temp_y = y
        #temp_width = width
        #temp_height = height

        #x = 780
        #y = 380
        #width = 200
        #height = 100

        logging.info(f"Actual: Starting text addition operation: '{text}' at ({x}, {y}) with box size ({width}, {height})")
  
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(1)
        
        # Get window position and size
        window_rect = win32gui.GetWindowRect(paint_window.handle)
        logging.info(f"Paint window rectangle: {window_rect}")
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # First, switch to selection tool to ensure we're not in any other mode
        logging.info("Switching to selection tool")
        paint_window.type_keys('s')
        time.sleep(0.5)
        
        # Now select the Text tool using multiple methods to ensure it's activated
        logging.info("Selecting Text tool")
        
        # Method 1: Click the Text tool button
        paint_window.click_input(coords=(650, 82))  # Text tool coordinates
        time.sleep(1)
        
        # Method 2: Use keyboard shortcut
        paint_window.type_keys('t')
        time.sleep(1)
        
        logging.info("Creating text box")
        
        # Click and drag to create text box
        canvas.press_mouse_input(coords=(x, y))
        time.sleep(0.5)
        
        # Drag to create text box of specified size
        canvas.move_mouse_input(coords=(x + width, y + height))
        time.sleep(0.5)
        
        canvas.release_mouse_input(coords=(x + width, y + height))
        time.sleep(1)
        
        # Click inside the text box to ensure it's selected
        click_x = x + (width // 2)  # Click in the middle of the box
        click_y = y + (height // 2)
        canvas.click_input(coords=(click_x, click_y))
        time.sleep(0.5)
        
        # Clear any existing text
        paint_window.type_keys('^a')  # Select all
        time.sleep(0.2)
        paint_window.type_keys('{BACKSPACE}')
        time.sleep(0.2)
        
        # Type the text character by character
        logging.info(f"Typing text: {text}")
        for char in text:
            if char == ' ':
                paint_window.type_keys('{SPACE}')
            elif char == '\n':
                paint_window.type_keys('{ENTER}')
            else:
                paint_window.type_keys(char)
            time.sleep(0.1)
        
        # Finalize the text by clicking outside
        canvas.click_input(coords=(50, 50))
        time.sleep(0.5)
        
        # Switch back to selection tool
        paint_window.type_keys('s')
        time.sleep(0.5)
        
        logging.info("Text addition completed")

        #x = temp_x
        #y = temp_y
        #width = temp_width
        #height = temp_height
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text '{text}' added successfully at ({x}, {y}) on Microsoft Paint Canvas"
                )
            ]
        }
    except Exception as e:
        logging.error(f"Error adding text: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error adding text: {str(e)} on Microsoft Paint Canvas"
                )
            ]
        }

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

#if __name__ == "__main__":
#    # Check if running with mcp dev command
#    print("STARTING")
#    if len(sys.argv) > 1 and sys.argv[1] == "dev":
#        mcp.run()  # Run without transport for dev server
#    else:
#        mcp.run(transport="stdio")  # Run with stdio for direct execution


if __name__ == "__main__":
    print("Starting MCP Calculator server...")
    # Check if running with mcp dev command
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution