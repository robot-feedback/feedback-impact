
from openai import OpenAI
from unidecode import unidecode
from config.config import OPENAI_API_KEY, OPENAI_MODEL
from utils.task_2_prompt_handler import PromptHandler

class LLMHandler:
    """Handles all OpenAI API interactions"""

    def __init__(self):
        """Initialize OpenAI client and prompt handler"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.prompt_handler = PromptHandler()

    def get_feedback_response(self, feedback_level, paragraph_text, answer, error_list, user_response):
        """
        Get feedback response from OpenAI based on feedback level

        Args:
            feedback_level (str): Feedback level (F_1, F_2, F_3, F_4)
            paragraph_text (str): Original paragraph with errors
            answer (str): Corrected answer paragraph
            error_list (str): List of errors and their types
            user_response (str): User's submitted response

        Returns:
            str: OpenAI generated feedback response
            str: Empty string for F_4 (no feedback)

        Raises:
            Exception: If OpenAI API call fails
        """
        # F_4 has no feedback
        if feedback_level == "F_4":
            return ""

        try:
            # Get appropriate prompt for feedback level
            user_prompt = self.prompt_handler.get_prompt_for_feedback_level(
                feedback_level, paragraph_text, answer, error_list, user_response
            )

            if user_prompt is None:
                return ""

            # Special handling for F_1 - requires two API calls
            if feedback_level == "F_1":
                return self._handle_f1_feedback(user_prompt)
            else:
                return self._make_api_call(user_prompt)

        except Exception as e:
            print(f"Error in LLM Handler: {e}")
            raise e

    def _handle_f1_feedback(self, initial_prompt):
        """
        Handle F_1 feedback which requires two API calls

        Args:
            initial_prompt (str): The initial F_1 prompt

        Returns:
            str: Processed conversational feedback
        """
        # First API call - get initial detailed response
        initial_response = self._make_api_call(initial_prompt)

        # Second API call - rewrite in conversational style
        rewrite_prompt = self.prompt_handler.get_f1_rewrite_prompt(initial_response)
        final_response = self._make_api_call(rewrite_prompt)

        return final_response

    def _make_api_call(self, user_prompt):
        """
        Make API call to OpenAI

        Args:
            user_prompt (str): The user prompt to send

        Returns:
            str: OpenAI response content

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompt_handler.get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ]
            )

            openai_response = response.choices[0].message.content
            # Convert to ASCII to handle special characters
            return unidecode(openai_response)

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            raise e