import sys
import json
import zmq
import os
import time
import io
import argparse
from openai import OpenAI
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel, QTextEdit, QHBoxLayout, QComboBox, QLCDNumber
from PyQt6.QtCore import Qt, QTimer
from gtts import gTTS
from playsound import playsound
from google.cloud import texttospeech
from unidecode import unidecode

json_credentials_path = "<json_file_name>"
API_KEY = "<Your_API_KEY>"
client = OpenAI(api_key=API_KEY)

TIME_1 = 240
TIME_2 = 120
DP_1 = "4:00"
DP_2 = "2:00"

class SimpleWindow(QWidget):
    def __init__(self,set_number):
        super().__init__()

        self.set_number = set_number
        self.phase = 1  # Phase 1 = 4 minutes, Phase 2 = 2 minutes
        self.response_1_saved = False
        self.response_2_saved = False
        self.initUI()

    def initUI(self):

        self.setFixedSize(2000, 1200)  # Set window size

        self.title = QLabel('Feedback Study', self)
        self.title.setStyleSheet("font-size: 32px; font-weight: bold; font-family: Arial;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

#########################      Drop Down Row Elements     #########################

        combo_box_style = "font-size: 24px; font-family:Courier; padding-left: 25px; padding-right: 20px"
        drop_width, drop_height = 120,50

        self.agent_combo = QComboBox(self)
        self.agent_combo.addItems(['agent_2', 'agent_1'])
        self.agent_combo.setFixedSize(160, drop_height)  # Set dropdown size
        self.agent_combo.setStyleSheet(combo_box_style)

        self.sub_id_combo = QComboBox(self)
        # self.sub_id_combo.addItems([f'P_{i}' for i in range(33)])
        self.sub_id_combo.addItems(['P_24','P_0'])
        self.sub_id_combo.setFixedSize(drop_width, drop_height)  # Set dropdown size
        self.sub_id_combo.setStyleSheet(combo_box_style)

        self.task_id_combo = QComboBox(self)
        self.task_id_combo.addItems(['task_2'])
        # self.task_id_combo.addItems(['task_2', 'task_1'])
        self.task_id_combo.setFixedSize(160, drop_height)  # Set dropdown size
        self.task_id_combo.setStyleSheet(combo_box_style)

        self.feedback_level_combo = QComboBox(self)
        self.feedback_level_combo.addItems([f'F_{i}' for i in range(1, 5)])
        self.feedback_level_combo.setFixedSize(drop_width, drop_height)  # Set dropdown size
        self.feedback_level_combo.setStyleSheet(combo_box_style)

        self.timer_display = QLCDNumber(self)
        self.timer_display.setDigitCount(5)
        self.timer_display.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.timer_display.setFixedSize(drop_width, drop_height)  # Set timer size
        self.timer_display.setStyleSheet(combo_box_style)
        self.timer_display.display(DP_1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.play_button = QPushButton('Play', self)
        self.play_button.setFixedSize(drop_width, drop_height)  # Set button size
        self.play_button.setStyleSheet("font-size: 24px; font-family:Arial; padding-left: 25px; padding-right: 20px")
        self.play_button.clicked.connect(self.start_phase_1)


#################### Drop Down Style #############################

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

        combo_timer_layout.addStretch(1)

        combo_timer_layout.addWidget(self.timer_display)
        combo_timer_layout.addSpacing(20)
        combo_timer_layout.addWidget(self.play_button)



#########################      Text Elements     #########################


        self.instruction = QLabel(
            "Read the following passage carefully. Identify and correct all grammatical errors, spelling mistakes, "
            "punctuation-capitalization issues, word-choice error and consistency error. Then rewrite the passage in the text box. You have 4 minutes to "
            "find and correct as many errors as you can.", self
        )
        self.instruction.setWordWrap(True)
        self.instruction.setStyleSheet("font-size: 28px; color:red; font-family: Palatino;  padding:30px;")

        self.paragraph = QLabel("", self)
        self.paragraph.setWordWrap(True)
        self.paragraph.setStyleSheet("font-size: 28px;  padding:30px; color: black; font-family: Palatino;")

        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText('Write your response here...')
        self.text_input.setStyleSheet("font-size: 28px;  padding:30px; color: blue; font-family: Palatino;")

        self.button = QPushButton('Submit', self)
        self.button.setFixedSize(150, 50)
        self.button.setStyleSheet("font-size: 24px;font-family: Helvetica;")
        self.button.clicked.connect(self.submit_button_pressed)

        # Set up the button layout (align to the right)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.button)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addSpacing(20) 
        layout.addWidget(self.title)
        layout.addSpacing(50) 
        layout.addLayout(combo_timer_layout)
        layout.addSpacing(40)
        layout.addWidget(self.instruction)
        layout.addSpacing(-40)
        layout.addWidget(self.paragraph)
        layout.addWidget(self.text_input)
        layout.addSpacing(20)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('Feedback Study')

    def load_paragraph_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                paragraph_text = file.read()
        except FileNotFoundError:
            paragraph_text = "Error: File not found."
        return paragraph_text

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            minutes, seconds = divmod(self.time_left, 60)
            time_display = f"{minutes:02}:{seconds:02}"
            self.timer_display.display(time_display)
        else:
            # Stop the timer when time_left reaches 0
            self.timer.stop()

            if self.phase == 1:
                self.send_response_to_openai(self.text_input.toPlainText(), time.time(), self.time_left)
                self.start_phase_2()

            elif self.phase == 2:
                self.collect_data(phase=2, openai_response="")
                QMessageBox.information(self, 'Warning', 'Time\'s up!')


    def submit_button_pressed(self):
        current_timestamp = time.time()
        remaining_time = self.time_left  # Get the remaining time from the timer

        if self.phase == 1 and not self.response_1_saved:
            self.send_response_to_openai(self.text_input.toPlainText(), current_timestamp, remaining_time)
            self.start_phase_2()
        elif self.phase == 2 and not self.response_2_saved:
            self.collect_data(phase=2, openai_response="", submission_time=current_timestamp, time_left=remaining_time)
            self.timer.stop()


    def start_phase_1(self):
        # Load paragraphs based on feedback level
        feedback_level = self.feedback_level_combo.currentText()
        task_id = self.task_id_combo.currentText()
        agent_id = self.agent_combo.currentText()

        question_file_path = f"database/task_{task_id[-1]}/question/question_{self.set_number}.txt"
        error_file_path = f"database/task_{task_id[-1]}/error/error_{self.set_number}.txt"
        answer_file_path = f"database/task_{task_id[-1]}/answer/answer_{self.set_number}.txt"


        self.error = self.load_paragraph_from_file(error_file_path)
        self.answer = self.load_paragraph_from_file(answer_file_path)
        self.paragraph.setText(self.load_paragraph_from_file(question_file_path))

        # Start the timer for Phase 1
        self.timer.start(1000)
        self.time_left = TIME_1 # Set to 4 minutes
        self.phase = 1

    def start_phase_2(self):
        # Start the second phase (2-minute timer)
        self.phase = 2
        self.response_1_saved = True
        self.time_left = TIME_2  # 2 minutes
        self.timer_display.display(DP_2)
        self.timer.start(1000)

    def collect_data(self, phase=1, openai_response="", submission_time=None, time_left=None):
        # Extract the values from the dropdowns
        sub_id = self.sub_id_combo.currentText()
        task_id = self.task_id_combo.currentText()
        agent_id = self.agent_combo.currentText()
        feedback_level = self.feedback_level_combo.currentText()
        submission_time = time.time()

        # Create the data dictionary
        data = {
            "Sub_ID": sub_id, 
            "Task_ID": task_id,
            "Agent_Type": agent_id,        
            "Feedback_Level": feedback_level,
            "Set_Number": self.set_number, 
            f"Response_{phase}": self.text_input.toPlainText(),
            f"OpenAI_Response_{phase}": openai_response,
            f"Submission_timestamp{phase}": submission_time,
            f"Time_Left_{phase}": time_left
        }

        directory_path = f"data/{task_id}/{agent_id}/{sub_id}/{feedback_level}"
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, "feedback_data.txt")

        file_data = {}
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                    if content:  # Check if file is not empty
                        file_data = json.loads(content)  # Load the existing data
        except json.JSONDecodeError:
            # Handle invalid JSON in the file
            file_data = {}

        # Update the existing data or create new
        file_data[f"Phase_{phase}"] = data

        # Save the updated data to the file
        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=4)

        QMessageBox.information(self, 'Status', f'Response {phase} is saved!')


    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        with open("temp_audio.mp3", "wb") as f:
            f.write(audio_buffer.read())

        playsound("temp_audio.mp3")

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

    def send_response_to_openai(self, submitted_response, submission_time, time_left):
        feedback_level = self.feedback_level_combo.currentText()

        assistant_behavior =f'''
            You are a helpful assistant.
            '''

        if feedback_level == "F_1":

            user_request_initial = f'''
            
            Context: User is proofreading a paragraph with 15 errors across 6 types: Grammar (5), Spelling (4), Word Choice (3), Punctuation (1), Capitalization (1), and Consistency (1).

            <Given>:
            - Question paragraph: {self.paragraph.text()}
            - Answer paragraph: {self.answer}
            - Error list and types: {self.error}
            - User's submitted response: {self.text_input.toPlainText()}

            </Given>

            <Task> 
            Compare user's submitted response to the error list and the answer paragraph. 
            Determine if the submitted response is complete and also check which errors are not corrected in the submitted response. 
            Only check the errors in the error list for whether they are corrected or not.

            Provide output based on the following scenarios:

            1. If user response is complete and no errors remain:
            Respond to user like this - It appears you've addressed all the errors. Consider reviewing once more to ensure nothing was missed.

            2. If user response is complete but errors remain:
            Find out maximum of two errors with the error type and sentence position from the error list that user didn’t correct.
            Do not include the solution of the error (e.g. what should be the correct version) in your response.

            3. If user response is incomplete and errors remain:
            First, instruct the user to complete the paragraph in a short one sentence. 
            Then, Find out maximum of two errors with the error type and sentence position from the error list that user didn’t correct.
            Do not include the solution of the error (e.g. what should be the correct version) in your response. 

            4. If user response is incomplete but no errors in the completed portion:
            Instruct the user to complete the rest of the paragraph.

            </Task> 

            '''

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": assistant_behavior},
                    {"role": "user", "content": user_request_initial}
                ]
            )

            # print(f"Initial pormpt: {user_request_initial}")
            initial_response = response.choices[0].message.content
            # print(f"Initial response: {initial_response}")

            user_request = f'''

            <given response> 
            {initial_response}
            </given response> 

            Rewrite this in a conversational style at maximum of two sentences.         

            '''

        elif feedback_level == "F_2":
            user_request = f'''
            
            Context: User is proofreading a paragraph with 15 errors across 6 types: Grammar (5), Spelling (4), Word Choice (3), Punctuation (1), Capitalization (1), and Consistency (1).

            <Given>:
            - Question paragraph: {self.paragraph.text()}
            - Answer paragraph: {self.answer}
            - Error list and types: {self.error}
            - User's submitted response: {self.text_input.toPlainText()}
            </Given>

            <Task> 
            Provide task-motivation level feedback that encourages the user to stay focused, acknowledges their effort.
            Encourage them to continue without pointing out specific errors. Motivates them to improve based on the current state of their work. 
            Give your feedback in two short conversational style sentences.
            </Task> 

            '''

        elif feedback_level == "F_3":
            user_request = f'''
            
            Context: User is proofreading a paragraph with 15 errors across 6 types: Grammar (5), Spelling (4), Word Choice (3), Punctuation (1), Capitalization (1), and Consistency (1).

            <Given>:
            - Question paragraph: {self.paragraph.text()}
            - Answer paragraph: {self.answer}
            - Error list and types: {self.error}
            - User's submitted response: {self.text_input.toPlainText()}

            </Given>

            <Task> 
            Provide meta-task level feedback.Focus the feedback on boosting their confidence and self-perception without mentioning specific errors or task details. 
            Give positive, self-focused feedback. Give your feedback in two short conversational style sentences.
            </Task>


            
            '''

        elif feedback_level == "F_4":
            openai_response = ""
            self.collect_data(self.phase, openai_response, submission_time=submission_time, time_left=time_left)
            return 

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": assistant_behavior},
                    {"role": "user", "content": user_request}
                ]
            )
            openai_response = response.choices[0].message.content
            agent_feedback = unidecode(openai_response)
            print(f"OpenAI response: {agent_feedback}")

    ############################### Sending feedback to Agents #################################
            agent_id = self.agent_combo.currentText()

            if agent_id == 'agent_1':
                # Send feedback to NAO robot
                context = zmq.Context()
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://localhost:5555")
                socket.send_string(agent_feedback)
                message = socket.recv_string()
                print(f"Received ack from NAO: {message}")

            elif agent_id == 'agent_2':
                self.text_to_speech_gn(agent_feedback)


    ########################## +++++++++++++++++++++++++ ####################################

            self.collect_data(self.phase, openai_response, submission_time=submission_time, time_left=time_left)
        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.warning(self, 'Error', 'Failed to get response from OpenAI API.')

def main():
    parser = argparse.ArgumentParser(description="Feedback Study")
    parser.add_argument('--set_number', type=str, required=True, help='Set number for study')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = SimpleWindow(args.set_number)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
