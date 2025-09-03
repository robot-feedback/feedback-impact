import sys
import json
import os
import base64
import io
import requests
import threading
import zmq
import argparse
from gtts import gTTS
from playsound import playsound
import time

from openai import OpenAI
from PyQt6.QtWidgets import QFrame, QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel, QTextEdit, QHBoxLayout, QComboBox, QLCDNumber, QScrollArea, QGridLayout, QLineEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
import cv2
from PIL import Image
from unidecode import unidecode
from google.cloud import texttospeech

json_credentials_path = "<json_file_name>"
API_KEY = "<Your_API_KEY>"
client = OpenAI(api_key=API_KEY)

TIME_1 = 240
TIME_2 = 120
DP_1 = "4:00"
DP_2 = "2:00"


class PatternWidget(QWidget):
    def __init__(self, image, pattern_number, object_name):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Image
        self.image_label = QLabel()
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.image_label)

        # Pattern label
        self.label = QLabel(f"Pattern {pattern_number} - {object_name}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

class VideoCaptureApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Store reference to parent (SimpleWindow)
        self.api_key = "<your api key>"  # Replace with your actual API key
        # self.chatgpt_worker = ChatGPTWorker(self.api_key)
        # self.chatgpt_worker.finished.connect(self.on_chatgpt_finished)
        button_width, button_height = 240, 50

        main_layout = QHBoxLayout(self)

        video_feed_layout = QVBoxLayout()
        video_feed_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center-align

        # Video feed section (left)
        self.video_label = QLabel()
        main_layout.addWidget(self.video_label, 1)

        # Right section (captured images and buttons)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget, 1)

        # Scroll area for captured images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedWidth(1290)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_content)
        right_layout.addWidget(self.scroll_area, 1)

        # Grid layout for patterns
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(10)
        self.scroll_layout.addLayout(self.grid_layout)


        # Buttons and Object Name Field (Aligned in the same row)
        button_layout = QHBoxLayout()

        # Object Name Text Field with placeholder text
        self.object_name_field = QLineEdit()
        self.object_name_field.setFixedSize(button_width, button_height)
        self.object_name_field.setStyleSheet("font-size: 18px; font-family:Arial;")
        self.object_name_field.setPlaceholderText("Object Name")  # Placeholder with light text

        # Save Button
        self.save_button = QPushButton("Save Pattern")
        self.save_button.setFixedSize(button_width, button_height)
        self.save_button.setStyleSheet("font-size: 18px; font-family:Arial;")
        self.save_button.clicked.connect(self.save_pattern)

        # Submit Button
        self.get_feedback_button = QPushButton("Submit")
        self.get_feedback_button.setFixedSize(button_width, button_height)
        self.get_feedback_button.setStyleSheet("font-size: 18px; font-family:Arial;")
        self.get_feedback_button.clicked.connect(self.get_feedback)

        # Add widgets to the layout in the same row
        button_layout.addWidget(self.object_name_field)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.get_feedback_button)

        # Add the layout to the right_layout
        right_layout.addLayout(button_layout)



        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

        self.captured_images = []
        self.object_list = []
        self.chatgpt_results = {}

    def save_pattern(self):
        # Read a frame from the camera
        ret, frame = self.cap.read()
        if ret:
            object_name = self.object_name_field.text().strip()  # Get object name from text field
            print(object_name)
            if not object_name:
                QMessageBox.warning(self, 'Warning', 'Please enter a name for the object before saving.')
                return

            # Append the captured frame to the captured_images list
            self.captured_images.append((frame, object_name))  # Save both image and object name
            self.update_captured_images()

            # Access sub_id, task_id, agent_id, feedback_level from parent (SimpleWindow)
            sub_id = self.parent.sub_id_combo.currentText()
            task_id = self.parent.task_id_combo.currentText()
            agent_id = self.parent.agent_combo.currentText()
            feedback_level = self.parent.feedback_level_combo.currentText()

            # Define directory path based on selected options
            if self.parent.phase == 1:
                directory_path = f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}/images_before_feedback"
            else:
                directory_path = f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}/images_after_feedback"
                
            print(f'Directory Path: {directory_path}')
            os.makedirs(directory_path, exist_ok=True)  # Ensure the directory exists

            # Save the captured frame as an image file
            pattern_number = len(self.captured_images)  # Use pattern number based on the number of captured images
            image_file_path = os.path.join(directory_path, f"{object_name}.png")

            # Save the frame using OpenCV
            cv2.imwrite(image_file_path, frame)

            print(f"Pattern saved at {image_file_path}")
            self.object_list.append(object_name)  # Save object name to the object list

             # Reset the object name field to show the placeholder text
            self.object_name_field.clear()  # Clears the field and shows the placeholder text again


            # # Optionally, you can also start a new thread for ChatGPT processing here
            # thread = threading.Thread(target=self.process_image_in_background, args=(frame,))
            # thread.start()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                640, 480, Qt.AspectRatioMode.KeepAspectRatio))

    # def process_image_in_background(self, image):
    #     query = "A user is creating a pattern using the different blocks in the given image. Which object does it represent? Give the answer in one word."
    #     self.chatgpt_worker.process_image(image, query)

    # # def on_chatgpt_finished(self, query, result):
    # #     if query.startswith("A user is creating a pattern"):
    # #         self.object_list.append(result)
    # #         print(f"Object recognized: {result}")  # Debug print
    # #     else:
    # #         self.chatgpt_results['feedback'] = result

    def update_captured_images(self):
        # Clear existing items in the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Calculate number of columns based on scroll area width
        scroll_width = self.scroll_area.width() - 20  # Subtract 20 for scroll bar
        pattern_width = 160  # 150 for image + 10 for margins
        cols = max(1, scroll_width // pattern_width)

        # Add patterns to the grid layout
        for i, (image, object_name) in enumerate(self.captured_images):
            pattern_widget = PatternWidget(image, i + 1, object_name)
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(pattern_widget, row, col)

        # Add stretch to push all content to the top-left
        self.scroll_layout.addStretch()

    def get_feedback(self):

        current_timestamp = time.time()
        remaining_time = self.parent.time_left
        # if not self.captured_images:
        #     print("No patterns captured yet.")
        #     return

        self.get_feedback_button.setEnabled(False)

        if self.parent.phase == 1:
            self.parent.timer.stop()
            response = self.process_feedback()
            print(f"Feedback received: {response}")
            self.play_feedback_to_agent(feedback=response)
            
            self.collect_data(phase=self.parent.phase, object_list=self.object_list, openai_response=response, submission_time=current_timestamp, time_left=remaining_time)
            # self.parent.phase = 2
            self.object_list = []
            self.parent.start_phase_2()
            self.get_feedback_button.setEnabled(True)

        elif self.parent.phase == 2:
            self.parent.timer.stop()
            self.collect_data(phase=self.parent.phase, object_list=self.object_list, openai_response="", submission_time=current_timestamp, time_left=remaining_time)
            # self.timer.stop()

    def text_to_speech_gn(self, text):

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_credentials_path
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(language_code="en-US",name="en-US-Wavenet-C")
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            print("playing audio")

        playsound("output.mp3")


    def play_feedback_to_agent(self, feedback=""):

        agent_id = self.parent.agent_combo.currentText()
        feedback_level = self.parent.feedback_level_combo.currentText()

        if feedback_level!="F_4":
            if agent_id == 'agent_1':
                    # Send feedback to NAO robot
                    context = zmq.Context()
                    socket = context.socket(zmq.REQ)
                    socket.connect("tcp://localhost:5555")
                    socket.send_string(feedback)
                    message = socket.recv_string()
                    print(f"Received ack from NAO: {message}")

            elif agent_id == 'agent_2':
                self.text_to_speech_gn(feedback)


    def process_feedback(self):
        result = ""
        # Load the image from the parent class
        image_path = self.parent.question_file_path
        image = cv2.imread(image_path)  # Load the image from the file path

        # Ensure that the image was loaded correctly
        if image is None:
            print(f"Error: Failed to load image from {image_path}")
            return
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Prepare the required data for the prompt
        shape_list_str = self.parent.shape_list  # Already a formatted string from load_shapes_from_file
        object_list_str = ', '.join(self.object_list)  # Join object names
        example_objects_str = self.parent.example_object_list  # Already a formatted string from load_objects_from_file

        feedback_level = self.parent.feedback_level_combo.currentText()

        if feedback_level == "F_1":
            # Create the query for ChatGPT to guide the user in a robot-like response
            query = f"""
            You are a rhelpful assistant. 
            Here is the list of available shapes: {shape_list_str}. 
            The user has already made these objects: {object_list_str}. 
            Some examples of objects that can be made from the given shapes: {example_objects_str}.
            Suggest two new objects that the user can create from the example object list, mentioning the required shapes, colors, and quantities for those objects.
            For example, you can say: "Try making a house using one red trapezoid and one orange square" or "Let's try making a house using one red trapezoid and one orange square."
            If all the example shapes have been used, feel free to suggest something beyond the example list. Your response should be short and precise as you are directly guiding the user. Always suggest from 
            the example object list and shapes listed in the example list for the objects. Don't use formal linkers such as "additionally," etc. Instead, use friendly linkers like "How about making a house," or "Next, let's make," or "Another object could be."
            """
        elif feedback_level == "F_2":
            
            query = f'''
            You are a helpful assistant.
            <Given>:
            - available_shapes: {shape_list_str}
            - objects already made by the user: {object_list_str}
            - example objects that can be made from the given shapes: {example_objects_str}
            </Given>

            <Task> 
            Provide task-motivation level feedback that encourages the user to stay focused, acknowledges their effort, 
            and motivates them to improve based on the current state of their work. 
            Give your feedback in two short conversational style sentences.
            </Task> 

            '''
        elif feedback_level == "F_3":


            query = f'''
            You are a helpful assistant. 
            <Given>:
            - available_shapes: {shape_list_str}
            - objects already made by the user: {object_list_str}
            - example objects that can be made from the given shapes: {example_objects_str}
            </Given>

            <Task> 
            Provide meta-task level feedback.Focus the feedback on boosting their confidence and self-perception without mentioning shape suggestions. 
            Give positive, self-focused feedback. Give your feedback in two short conversational style sentences.
            </Task> 

            '''
        elif feedback_level == "F_4":
            return result
                

        # Set up the OpenAI API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 300
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            # Check if the response is successful
            if response.status_code == 200:
                data = response.json()
                result = data['choices'][0]['message']['content'].strip()
                result = unidecode(result)

            
                ####################sending feedback to agents######################

        except requests.exceptions.RequestException as e:
            print(f"Error with the API request: {e}")
            result = "Error: Unable to communicate with the OpenAI API."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            result = "Error: An unexpected issue occurred while processing feedback."

        return result

    

    def collect_data(self, phase=1, object_list=[], openai_response="", submission_time=None, time_left=None):
        sub_id = self.parent.sub_id_combo.currentText()
        task_id = self.parent.task_id_combo.currentText()
        agent_id = self.parent.agent_combo.currentText()
        feedback_level = self.parent.feedback_level_combo.currentText()

        if phase == 1:
            data = {
                "Sub__ID": sub_id,
                "Task_ID": task_id,
                "Agent_Type": agent_id,
                "Feedback_Level": feedback_level,
                f"Objects_{phase}": object_list,  # Save the object list here
                f"OpenAI_Response_{phase}": openai_response,    # Save the feedback result here
                f"Submission_timestamp{phase}": submission_time,
                f"Time_Left_{phase}": time_left
            }

            # Define directory path based on selected options
            directory_path = f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}"
            file_name = "objects_and_feedback.txt"
        else:
            data = {
                "Sub__ID": sub_id,
                "Task_ID": task_id,
                "Agent_Type": agent_id,
                "Feedback_Level": feedback_level,
                f"Objects_{phase}": object_list,  # Save the object list here
                f"OpenAI_Response_{phase}": "",    # Save the feedback result here
                f"Submission_timestamp{phase}": submission_time,
                f"Time_Left_{phase}": time_left
            }

            # Define directory path based on selected options
            directory_path = f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}"
            file_name = "objects_after_feedback.txt"

        os.makedirs(directory_path, exist_ok=True)  # Ensure the directory exists

        # Define the file path for feedback data
        file_path = os.path.join(directory_path, file_name)

        # Load existing file data (if any) and merge with new data
        file_data = {}
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                    if content:  
                        file_data = json.loads(content)

                

        except json.JSONDecodeError:
            file_data = {}

        # Add new phase data to the existing file data
        file_data[f"Phase_{phase}"] = data

        # Save the updated data to the file
        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=4)
        
        QMessageBox.information(self, 'Status', f'Response {phase} is saved!')
    def closeEvent(self, event):
        self.cap.release()

class SimpleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 1
        self.response_1_saved = False
        self.response_2_saved = False
        self.initUI()

    def initUI(self):
        self.setFixedSize(2000, 1200)  # Set window size

        self.title = QLabel('Feedback Study', self)
        self.title.setStyleSheet("font-size: 32px; font-weight: bold; font-family: Arial;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        combo_box_style = "font-size: 24px; font-family:Courier; padding-left: 25px; padding-right: 20px"
        drop_width, drop_height = 120, 50

        self.agent_combo = QComboBox(self)
        self.agent_combo.addItems(['agent_1'])
        self.agent_combo.setFixedSize(160, drop_height)
        self.agent_combo.setStyleSheet(combo_box_style)

        self.sub_id_combo = QComboBox(self)
        # self.sub_id_combo.addItems([f'P_{i}' for i in range(33)])
        self.sub_id_combo.addItems(['P_32','P_0'])
        self.sub_id_combo.setFixedSize(drop_width, drop_height)
        self.sub_id_combo.setStyleSheet(combo_box_style)

        self.task_id_combo = QComboBox(self)
        self.task_id_combo.addItems(['task_1'])
        self.task_id_combo.setFixedSize(160, drop_height)
        self.task_id_combo.setStyleSheet(combo_box_style)

        self.feedback_level_combo = QComboBox(self)
        self.feedback_level_combo.addItems([f'F_{i}' for i in range(1, 5)])
        self.feedback_level_combo.setFixedSize(drop_width, drop_height)
        self.feedback_level_combo.setStyleSheet(combo_box_style)

        self.set_combo = QComboBox(self)
        self.set_combo.addItems([f'{i}' for i in range(1, 9)])
        self.set_combo.setFixedSize(drop_width, drop_height)
        self.set_combo.setStyleSheet(combo_box_style)

        self.timer_display = QLCDNumber(self)
        self.timer_display.setDigitCount(5)
        self.timer_display.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.timer_display.setFixedSize(drop_width, drop_height)
        self.timer_display.setStyleSheet(combo_box_style)
        self.timer_display.display(DP_1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.play_button = QPushButton('Play', self)
        self.play_button.setFixedSize(drop_width, drop_height)
        self.play_button.setStyleSheet("font-size: 24px; font-family:Arial; padding-left: 25px; padding-right: 20px")
        self.play_button.clicked.connect(self.start_phase_1)

        drop_down_style = "font-size: 24px; font-family: Helvetica;"
        combo_timer_layout = QHBoxLayout()

        combo_timer_layout.addSpacing(20)
        agent_label = QLabel('Agent:')
        agent_label.setStyleSheet(drop_down_style)
        combo_timer_layout.addWidget(agent_label)
        combo_timer_layout.addWidget(self.agent_combo)

        combo_timer_layout.addSpacing(20)

        sub_id_label = QLabel('Sub ID:')
        sub_id_label.setStyleSheet(drop_down_style)
        combo_timer_layout.addWidget(sub_id_label)
        combo_timer_layout.addWidget(self.sub_id_combo)

        combo_timer_layout.addSpacing(20)

        task_id_label = QLabel('Task ID:')
        task_id_label.setStyleSheet(drop_down_style)
        combo_timer_layout.addWidget(task_id_label)
        combo_timer_layout.addWidget(self.task_id_combo)

        combo_timer_layout.addSpacing(20)

        feedback_level_label = QLabel('Feedback Level:')
        feedback_level_label.setStyleSheet(drop_down_style)
        combo_timer_layout.addWidget(feedback_level_label)
        combo_timer_layout.addWidget(self.feedback_level_combo)

        set_label = QLabel('Set:')
        set_label.setStyleSheet(drop_down_style)

        combo_timer_layout.addSpacing(20)
        combo_timer_layout.addWidget(set_label)
        combo_timer_layout.addWidget(self.set_combo)

        combo_timer_layout.addStretch(1)

        combo_timer_layout.addWidget(self.timer_display)
        combo_timer_layout.addSpacing(20)
        combo_timer_layout.addWidget(self.play_button)

        # Instruction label
        self.instruction = QLabel(
            "In this task, you will be provided with a set of shapes in various sizes and colors. "
            "Your goal is to create unique object patterns using these shapes. Once you've completed a pattern, "
            "input the name of the object and press the Save Pattern button to save it."
            "You have four minutes to create as many patterns as possible. If you finish before, press the Submit "
            "button to get feedback.", self
        )
        self.instruction.setWordWrap(True)
        self.instruction.setStyleSheet("font-size: 28px; color:red; font-family: Palatino;  padding:30px;")

        # Hidden elements: paragraph and video capture widget
        self.paragraph = QLabel("", self)
        self.paragraph.setWordWrap(True)
        self.paragraph.setStyleSheet("font-size: 28px;  padding:30px; color: black; font-family: Palatino;")
        self.paragraph.setVisible(False)  # Initially hidden

        # Hidden video capture widget
        self.video_capture_widget = VideoCaptureApp(self)
        self.video_capture_widget.setVisible(False)  # Initially hidden

        layout = QVBoxLayout()
        layout.addSpacing(20)
        layout.addWidget(self.title)
        layout.addSpacing(50)
        layout.addLayout(combo_timer_layout)
        layout.addSpacing(40)
        layout.addWidget(self.instruction)
        layout.addSpacing(10)  # Adjusted for padding
        layout.addWidget(self.paragraph)  # Add paragraph (initially hidden)
        layout.addWidget(self.video_capture_widget)  # Add video capture widget (initially hidden)

        self.setLayout(layout)
        self.setWindowTitle('Feedback and Video Capture Study')
    
    def load_shapes_from_file(self, file_path):
        shapes_str = ""  # A string to hold shape information

        try:
            with open(file_path, 'r') as file:
                shape_list = []
                for line in file:
                    # Split each line by comma and extract the shape properties
                    shape_data = line.strip().split(',')
                    if len(shape_data) == 3:
                        shape_name = shape_data[0]
                        shape_color = shape_data[1]
                        shape_quantity = shape_data[2]

                        # Add the shape in the "quantity color shape_name" format to the list
                        shape_list.append(f"{shape_quantity} {shape_color} {shape_name}")
                
                # Join all the shapes with a comma and a space
                shapes_str = ', '.join(shape_list)

        except FileNotFoundError:
            print("Error: File not found.")
        except ValueError:
            print("Error: Incorrect file format.")
        
        return shapes_str




    def load_objects_from_file(self, file_path):
        objects_str = ""  # A string to hold object information

        try:
            with open(file_path, 'r') as file:
                object_list = []
                for line in file:
                    # Split the line into object name and shapes
                    object_data = line.strip().split(':')
                    if len(object_data) == 2:
                        object_name = object_data[0].strip()  # Object name
                        shapes_str = object_data[1].strip()  # Shape list in string form

                        # Append the object in "object_name: shape_list" format
                        object_list.append(f"{object_name}: {shapes_str}")

                # Join all objects with a semicolon and space
                objects_str = '; '.join(object_list) + ';'

        except FileNotFoundError:
            print("Error: File not found.")
        except ValueError:
            print("Error: Incorrect file format.")
        
        return objects_str




    def start_phase_1(self):

        feedback_level = self.feedback_level_combo.currentText()
        task_id = self.task_id_combo.currentText()
        agent_id = self.agent_combo.currentText()
        set_id = self.set_combo.currentText()

        self.sub_id_combo.setEnabled(False)
        self.task_id_combo.setEnabled(False)
        self.agent_combo.setEnabled(False)
        self.feedback_level_combo.setEnabled(False)
        self.play_button.setEnabled(False)

        self.question_file_path = f"database/task_{task_id[-1]}/question/q_{set_id}.png"
        
        shape_file_path = f"database/task_{task_id[-1]}/shape_list/shape_{set_id}.txt"
        object_file_path = f"database/task_{task_id[-1]}/object_list/object_{set_id}.txt"

        self.shape_list = self.load_shapes_from_file(shape_file_path)

        print(self.shape_list)

        self.example_object_list = self.load_objects_from_file(object_file_path)

        print(self.example_object_list)

        pixmap = QPixmap(self.question_file_path)

        # Set the desired width for the image
        desired_width = 300  # Set the width you want

        # Scale the image while maintaining the aspect ratio
        scaled_pixmap = pixmap.scaledToWidth(desired_width, Qt.TransformationMode.SmoothTransformation)

        # Set the scaled image to the QLabel (self.paragraph)
        self.paragraph.setPixmap(scaled_pixmap)
        self.paragraph.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Show the hidden elements after pressing "Play"
        self.paragraph.setVisible(True)
        self.video_capture_widget.setVisible(True)  # Make video capture widget visible

        # Start the timer
        self.timer.start(1000)
        self.time_left = TIME_1
        self.phase = 1

    def update_timer(self):
        self.time_left -= 1
        minutes, seconds = divmod(self.time_left, 60)
        time_display = f"{minutes:02}:{seconds:02}"
        self.timer_display.display(time_display)

        if self.time_left == 0:
            if self.phase == 1:
                self.video_capture_widget.get_feedback()
                self.start_phase_2()

            elif self.phase == 2:
                self.video_capture_widget.get_feedback()
                self.timer.stop()
                QMessageBox.information(self,'Warning','Times up!')

    def start_phase_2(self):
        self.phase = 2
        self.time_left = TIME_2
        self.timer_display.display(DP_2)
        self.timer.start(1000)

    

def main():
    
    # parser = argparse.ArgumentParser(description="Feedback Study")
    # parser.add_argument('--mode', type=str, choices=['robot', 'speaker','dev'], required=True, help='Select mode: robot or speaker')
    # args = parser.parse_args()

    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
