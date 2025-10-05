

import os

class PromptHandler:
    """Handles loading and formatting of prompts from text files"""

    def __init__(self, task_id="task_2"):
        """
        Initialize PromptHandler

        Args:
            task_id (str): Task identifier (default: "task_2")
        """
        self.task_id = task_id
        self.prompts_dir = f"prompts/{task_id}"

    def load_prompt(self, prompt_name):
        """
        Load prompt from text file

        Args:
            prompt_name (str): Name of the prompt file (without .txt extension)

        Returns:
            str: Content of the prompt file

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        file_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")

        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

    def get_system_prompt(self):
        """
        Get the system prompt for the assistant

        Returns:
            str: System prompt content
        """
        return self.load_prompt("system")

    def get_f1_prompt(self, paragraph_text, answer, error_list, user_response):
        """
        Get F_1 feedback prompt with parameters filled in

        Args:
            paragraph_text (str): Original paragraph with errors
            answer (str): Corrected answer paragraph
            error_list (str): List of errors and their types
            user_response (str): User's submitted response

        Returns:
            str: Formatted F_1 prompt
        """
        template = self.load_prompt("F_1")
        return template.format(
            paragraph_text=paragraph_text,
            answer=answer,
            error_list=error_list,
            user_response=user_response
        )

    def get_f1_rewrite_prompt(self, initial_response):
        """
        Get F_1 rewrite prompt for conversational style

        Args:
            initial_response (str): Initial detailed response from first API call

        Returns:
            str: Formatted F_1 rewrite prompt
        """
        return f'''
<given response>
{initial_response}
</given response>

Rewrite this in a conversational style at maximum of two sentences.
'''

    def get_f2_prompt(self, paragraph_text, answer, error_list, user_response):
        """
        Get F_2 feedback prompt with parameters filled in

        Args:
            paragraph_text (str): Original paragraph with errors
            answer (str): Corrected answer paragraph
            error_list (str): List of errors and their types
            user_response (str): User's submitted response

        Returns:
            str: Formatted F_2 prompt
        """
        template = self.load_prompt("F_2")
        return template.format(
            paragraph_text=paragraph_text,
            answer=answer,
            error_list=error_list,
            user_response=user_response
        )

    def get_f3_prompt(self, paragraph_text, answer, error_list, user_response):
        """
        Get F_3 feedback prompt with parameters filled in

        Args:
            paragraph_text (str): Original paragraph with errors
            answer (str): Corrected answer paragraph
            error_list (str): List of errors and their types
            user_response (str): User's submitted response

        Returns:
            str: Formatted F_3 prompt
        """
        template = self.load_prompt("F_3")
        return template.format(
            paragraph_text=paragraph_text,
            answer=answer,
            error_list=error_list,
            user_response=user_response
        )

    def get_prompt_for_feedback_level(self, feedback_level, paragraph_text, answer, error_list, user_response):
        """
        Factory function to get the appropriate prompt based on feedback level

        Args:
            feedback_level (str): F_1, F_2, F_3, or F_4
            paragraph_text (str): The original paragraph with errors
            answer (str): The corrected answer paragraph
            error_list (str): List of errors and their types
            user_response (str): User's submitted response

        Returns:
            str: The appropriate prompt for the feedback level
            None: For F_4 (no feedback)

        Raises:
            ValueError: If feedback level is unknown
        """
        if feedback_level == "F_1":
            return self.get_f1_prompt(paragraph_text, answer, error_list, user_response)
        elif feedback_level == "F_2":
            return self.get_f2_prompt(paragraph_text, answer, error_list, user_response)
        elif feedback_level == "F_3":
            return self.get_f3_prompt(paragraph_text, answer, error_list, user_response)
        elif feedback_level == "F_4":
            return None  # No feedback for F_4
        else:
            raise ValueError(f"Unknown feedback level: {feedback_level}")
