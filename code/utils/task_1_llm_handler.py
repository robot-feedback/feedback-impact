
import base64
import io
import requests
import cv2
from PIL import Image
from unidecode import unidecode
from config.config import OPENAI_API_KEY, OPENAI_VISION_MODEL
from utils.task_1_prompt_handler import PromptHandler

class LLMHandler:
    """Handles all OpenAI API interactions for Task 1 (pattern recognition)"""

    def __init__(self):
        """Initialize OpenAI client and prompt handler"""
        self.api_key = OPENAI_API_KEY
        self.prompt_handler = PromptHandler()

    def get_feedback_response(self, feedback_level, image_path, shape_list_str, object_list_str, example_objects_str):
        """
        Get feedback response from OpenAI based on feedback level with image context

        Args:
            feedback_level (str): Feedback level (F_1, F_2, F_3, F_4)
            image_path (str): Path to the reference image
            shape_list_str (str): Available shapes and colors
            object_list_str (str): Objects already made by user
            example_objects_str (str): Example objects that can be built

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
                feedback_level, shape_list_str, object_list_str, example_objects_str
            )

            if user_prompt is None:
                return ""

            # Load and encode image
            base64_image = self._encode_image(image_path)

            # Make API call with vision
            return self._make_vision_api_call(user_prompt, base64_image)

        except Exception as e:
            print(f"Error in LLM Handler: {e}")
            raise e

    def _encode_image(self, image_path):
        """
        Encode image to base64 for API transmission

        Args:
            image_path (str): Path to the image file

        Returns:
            str: Base64 encoded image

        Raises:
            Exception: If image loading fails
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image from {image_path}")

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

            return base64_image

        except Exception as e:
            print(f"Image encoding error: {e}")
            raise e

    def _make_vision_api_call(self, user_prompt, base64_image):
        """
        Make API call to OpenAI Vision API

        Args:
            user_prompt (str): The user prompt to send
            base64_image (str): Base64 encoded image

        Returns:
            str: OpenAI response content

        Raises:
            Exception: If API call fails
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": OPENAI_VISION_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": self.prompt_handler.get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ],
                "max_tokens": 300
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                result = data['choices'][0]['message']['content'].strip()
                # Convert to ASCII to handle special characters
                return unidecode(result)
            else:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            raise e
