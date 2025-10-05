
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# SHARED SETTINGS (Used by both Task 1 and Task 2)
# =============================================================================

# API Keys and Credentials
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

GOOGLE_CREDENTIALS_PATH = "config/file_name.json"

# ZMQ Settings
ZMQ_ADDRESS = "tcp://localhost:5555"

# Google TTS Settings
TTS_LANGUAGE = "en-US"
TTS_VOICE_NAME = "en-US-Wavenet-C"

# Audio Files
TEMP_AUDIO_FILE = "temp_audio.mp3"
OUTPUT_AUDIO_FILE = "output.mp3"

# OpenAI Settings
OPENAI_MODEL = "gpt-4o-mini"  
OPENAI_VISION_MODEL = "gpt-4o-mini" 

# =============================================================================
# TASK 1 SETTINGS
# =============================================================================

# Task 1 Timer Settings
TASK_1_TIME_PHASE_1 = 240  # 4 minutes in seconds
TASK_1_TIME_PHASE_2 = 120  # 2 minutes in seconds
TASK_1_DISPLAY_TIME_1 = "4:00"
TASK_1_DISPLAY_TIME_2 = "2:00"

# Task 1 UI Settings
TASK_1_WINDOW_WIDTH = 2000
TASK_1_WINDOW_HEIGHT = 1200

# Task 1 Dropdown Options
TASK_1_AGENT_OPTIONS = ['agent_2', 'agent_1']
TASK_1_SUBJECT_ID_OPTIONS = [f'P_{i}' for i in range(33)]
TASK_1_TASK_ID_OPTIONS = ['task_1']
TASK_1_FEEDBACK_LEVEL_OPTIONS = [f'F_{i}' for i in range(1, 5)]

# Task 1 UI Styles
TASK_1_DROPDOWN_WIDTH = 120
TASK_1_DROPDOWN_HEIGHT = 50
TASK_1_COMBO_BOX_STYLE = "font-size: 24px; font-family:Courier; padding-left: 25px; padding-right: 20px"
TASK_1_DROPDOWN_LABEL_STYLE = "font-size: 24px; font-family: Helvetica;"
TASK_1_TITLE_STYLE = "font-size: 32px; font-weight: bold; font-family: Arial;"
TASK_1_INSTRUCTION_STYLE = "font-size: 28px; color:red; font-family: Palatino; padding:30px;"
TASK_1_PARAGRAPH_STYLE = "font-size: 28px; padding:30px; color: black; font-family: Palatino;"
TASK_1_BUTTON_STYLE = "font-size: 24px; font-family: Helvetica;"

# Task 1 Instruction
TASK_1_INSTRUCTION = (
    "In this task, you will be provided with a set of shapes in various sizes and colors. "
    "Your goal is to create unique object patterns using these shapes. Once you've completed a pattern, "
    "input the name of the object and press the Save Pattern button to save it. "
    "You have four minutes to create as many patterns as possible. If you finish before, press the Submit "
    "button to get feedback."
)

# =============================================================================
# TASK 2 SETTINGS
# =============================================================================

# Task 2 Timer Settings
TIME_PHASE_1 = 240
TIME_PHASE_2 = 120
DISPLAY_TIME_1 = "4:00"
DISPLAY_TIME_2 = "2:00"

# Task 2 UI Settings
WINDOW_WIDTH = 2000
WINDOW_HEIGHT = 1200

# Task 2 Font and Style Settings
TITLE_FONT_SIZE = 32
DROPDOWN_FONT_SIZE = 24
TEXT_FONT_SIZE = 28
BUTTON_FONT_SIZE = 24

DROPDOWN_WIDTH = 120
DROPDOWN_HEIGHT = 50

# Task 2 UI Styles
COMBO_BOX_STYLE = "font-size: 24px; font-family:Courier; padding-left: 25px; padding-right: 20px"
DROPDOWN_LABEL_STYLE = "font-size: 24px; font-family: Helvetica;"
TITLE_STYLE = "font-size: 32px; font-weight: bold; font-family: Arial;"
INSTRUCTION_STYLE = "font-size: 28px; color:red; font-family: Palatino; padding:30px;"
PARAGRAPH_STYLE = "font-size: 28px; padding:30px; color: black; font-family: Palatino;"
TEXT_INPUT_STYLE = "font-size: 28px; padding:30px; color: blue; font-family: Palatino;"
BUTTON_STYLE = "font-size: 24px;font-family: Helvetica;"

# Task 2 Dropdown Options
AGENT_OPTIONS = ['agent_2', 'agent_1']
SUBJECT_ID_OPTIONS = ['P_0']  # ['P_0'] + [f'P_{i}' for i in range(1, 33)]
TASK_ID_OPTIONS = ['task_2']
FEEDBACK_LEVEL_OPTIONS = [f'F_{i}' for i in range(1, 5)]

# Task 2 Instruction
TASK_INSTRUCTION = (
    "Read the following passage carefully. Identify and correct all grammatical errors, spelling mistakes, "
    "punctuation-capitalization issues, word-choice error and consistency error. Then rewrite the passage in the text box. You have 4 minutes to "
    "find and correct as many errors as you can."
)

# =============================================================================
# FILE PATH FUNCTIONS (Used by both tasks)
# =============================================================================

def get_question_file_path(task_number, set_number):
    """Get path to question file for Task 2"""
    return f"database/task_{task_number}/question/question_{set_number}.txt"

def get_error_file_path(task_number, set_number):
    """Get path to error file for Task 2"""
    return f"database/task_{task_number}/error/error_{set_number}.txt"

def get_answer_file_path(task_number, set_number):
    """Get path to answer file for Task 2"""
    return f"database/task_{task_number}/answer/answer_{set_number}.txt"

def get_data_directory_path(task_id, agent_id, sub_id, feedback_level):
    """Get data directory path (used by Task 2)"""
    return f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}"

def get_feedback_data_file_path(task_id, agent_id, sub_id, feedback_level):
    """Get feedback data file path (used by Task 2)"""
    directory = get_data_directory_path(task_id, agent_id, sub_id, feedback_level)
    return os.path.join(directory, "feedback_data.txt")
