

import json
import os
import time
from config.config import get_data_directory_path, get_feedback_data_file_path

class DataManager:
    """Handles all data operations for the feedback study"""

    def __init__(self):
        pass

    def load_file(self, file_path):
        """
        Load content from a text file

        Args:
            file_path (str): Path to the file to load

        Returns:
            str: File content or error message if file not found
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "Error: File not found."

    def collect_data(self, phase, sub_id, task_id, agent_id, feedback_level,
                     set_number, user_response, openai_response="",
                     submission_time=None, time_left=None):
        """
        Collect and save phase data to JSON file

        Args:
            phase (int): Phase number (1 or 2)
            sub_id (str): Subject ID
            task_id (str): Task ID
            agent_id (str): Agent ID
            feedback_level (str): Feedback level
            set_number (str): Set number
            user_response (str): User's text response
            openai_response (str): OpenAI generated response
            submission_time (float): Timestamp of submission
            time_left (int): Remaining time when submitted

        Returns:
            str: Success message
        """
        if submission_time is None:
            submission_time = time.time()

        # Create the data dictionary
        data = {
            "Sub_ID": sub_id,
            "Task_ID": task_id,
            "Agent_Type": agent_id,
            "Feedback_Level": feedback_level,
            "Set_Number": set_number,
            f"Response_{phase}": user_response,
            f"OpenAI_Response_{phase}": openai_response,
            f"Submission_timestamp{phase}": submission_time,
            f"Time_Left_{phase}": time_left
        }

        # Create directory if it doesn't exist
        directory_path = get_data_directory_path(task_id, agent_id, sub_id, feedback_level)
        os.makedirs(directory_path, exist_ok=True)

        # Get file path
        file_path = get_feedback_data_file_path(task_id, agent_id, sub_id, feedback_level)

        # Load existing data
        file_data = {}
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                    if content:  # Check if file is not empty
                        file_data = json.loads(content)
        except json.JSONDecodeError:
            # Handle invalid JSON in the file
            file_data = {}

        # Update the existing data or create new
        file_data[f"Phase_{phase}"] = data

        # Save the updated data to the file
        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=4)

        return f'Response {phase} is saved!'