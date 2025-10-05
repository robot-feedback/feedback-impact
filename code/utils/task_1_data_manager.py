
import json
import os
import time

class DataManager:
    """Handles all data operations for the pattern recognition feedback study (Task 1)"""

    def __init__(self):
        pass

    def load_shapes_from_file(self, file_path):
        """
        Load shapes from file and format as string

        Args:
            file_path (str): Path to the shapes file

        Returns:
            str: Formatted string of shapes (e.g., "2 red squares, 3 blue triangles")
        """
        shapes_str = ""

        try:
            with open(file_path, 'r') as file:
                shape_list = []
                for line in file:
                    shape_data = line.strip().split(',')
                    if len(shape_data) == 3:
                        shape_name = shape_data[0]
                        shape_color = shape_data[1]
                        shape_quantity = shape_data[2]
                        shape_list.append(f"{shape_quantity} {shape_color} {shape_name}")

                shapes_str = ', '.join(shape_list)

        except FileNotFoundError:
            print(f"Error: Shapes file not found at {file_path}")
            return "Error: File not found."
        except ValueError:
            print("Error: Incorrect shapes file format.")
            return "Error: Incorrect file format."

        return shapes_str

    def load_objects_from_file(self, file_path):
        """
        Load example objects from file and format as string

        Args:
            file_path (str): Path to the objects file

        Returns:
            str: Formatted string of objects (e.g., "house: 1 red square, 2 blue triangles; ...")
        """
        objects_str = ""

        try:
            with open(file_path, 'r') as file:
                object_list = []
                for line in file:
                    object_data = line.strip().split(':')
                    if len(object_data) == 2:
                        object_name = object_data[0].strip()
                        shapes_str = object_data[1].strip()
                        object_list.append(f"{object_name}: {shapes_str}")

                objects_str = '; '.join(object_list) + ';'

        except FileNotFoundError:
            print(f"Error: Objects file not found at {file_path}")
            return "Error: File not found."
        except ValueError:
            print("Error: Incorrect objects file format.")
            return "Error: Incorrect file format."

        return objects_str

    def get_data_directory_path(self, task_id, agent_id, sub_id, feedback_level):
        """
        Get the directory path for storing data

        Args:
            task_id (str): Task ID
            agent_id (str): Agent ID
            sub_id (str): Subject ID
            feedback_level (str): Feedback level

        Returns:
            str: Directory path
        """
        return f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}"

    def get_image_directory_path(self, task_id, agent_id, sub_id, feedback_level, phase):
        """
        Get the directory path for storing images

        Args:
            task_id (str): Task ID
            agent_id (str): Agent ID
            sub_id (str): Subject ID
            feedback_level (str): Feedback level
            phase (int): Phase number (1 or 2)

        Returns:
            str: Image directory path
        """
        base_path = self.get_data_directory_path(task_id, agent_id, sub_id, feedback_level)
        if phase == 1:
            return os.path.join(base_path, "images_before_feedback")
        else:
            return os.path.join(base_path, "images_after_feedback")

    def collect_data(self, phase, sub_id, task_id, agent_id, feedback_level,
                     object_list, openai_response="", submission_time=None, time_left=None):
        """
        Collect and save phase data to JSON file

        Args:
            phase (int): Phase number (1 or 2)
            sub_id (str): Subject ID
            task_id (str): Task ID
            agent_id (str): Agent ID
            feedback_level (str): Feedback level
            object_list (list): List of object names created by user
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
            f"Objects_{phase}": object_list,
            f"OpenAI_Response_{phase}": openai_response,
            f"Submission_timestamp{phase}": submission_time,
            f"Time_Left_{phase}": time_left
        }

        # Create directory if it doesn't exist
        directory_path = self.get_data_directory_path(task_id, agent_id, sub_id, feedback_level)
        os.makedirs(directory_path, exist_ok=True)

        # Determine file name based on phase
        if phase == 1:
            file_name = "objects_and_feedback.txt"
        else:
            file_name = "objects_after_feedback.txt"

        # Get file path
        file_path = os.path.join(directory_path, file_name)

        # Load existing data
        file_data = {}
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                    if content:
                        file_data = json.loads(content)
        except json.JSONDecodeError:
            file_data = {}

        # Update the existing data or create new
        file_data[f"Phase_{phase}"] = data

        # Save the updated data to the file
        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=4)

        return f'Response {phase} is saved!'
