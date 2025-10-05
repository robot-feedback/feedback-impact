
import time
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QMessageBox,
                             QLabel, QTextEdit, QHBoxLayout, QComboBox, QLCDNumber, QApplication)
from PyQt6.QtCore import Qt, QTimer

from config.config import *
from utils.task_2_data_manager import DataManager
from utils.task_2_llm_handler import LLMHandler
from utils.robot_handler import RobotHandler
from utils.tts_handler import TTSHandler

class SimpleWindow(QWidget):
    """Main application window"""

    def __init__(self, set_number):
        super().__init__()
        self.set_number = set_number
        self.phase = 1  # Phase 1 = 4 minutes, Phase 2 = 2 minutes
        self.response_1_saved = False
        self.response_2_saved = False
        self.time_left = 0

        print(f"\n=== FEEDBACK STUDY STARTED ===")
        print(f"Set Number: {set_number}")
        print(f"Phase 1: 4 minutes (Error detection)")
        print(f"Phase 2: 2 minutes (Review time)")
        print(f"=============================\n")

        # Initialize handlers
        self.data_manager = DataManager()
        self.llm_handler = LLMHandler()
        self.robot_handler = RobotHandler()
        self.tts_handler = TTSHandler()

        # Store loaded content
        self.error = ""
        self.answer = ""

        self.initUI()

    def initUI(self):
        """Initialize the user interface"""
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Title
        self.title = QLabel('Feedback Study', self)
        self.title.setStyleSheet(TITLE_STYLE)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create dropdown controls
        self._create_dropdown_controls()

        # Create text elements
        self._create_text_elements()

        # Create submit button
        self._create_submit_button()

        # Set up layout
        self._setup_layout()

        self.setWindowTitle('Feedback Study')

    def _create_dropdown_controls(self):
        """Create all dropdown controls and timer"""
        # Agent dropdown
        self.agent_combo = QComboBox(self)
        self.agent_combo.addItems(AGENT_OPTIONS)
        self.agent_combo.setFixedSize(160, DROPDOWN_HEIGHT)
        self.agent_combo.setStyleSheet(COMBO_BOX_STYLE)

        # Subject ID dropdown
        self.sub_id_combo = QComboBox(self)
        self.sub_id_combo.addItems(SUBJECT_ID_OPTIONS)
        self.sub_id_combo.setFixedSize(DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
        self.sub_id_combo.setStyleSheet(COMBO_BOX_STYLE)

        # Task ID dropdown
        self.task_id_combo = QComboBox(self)
        self.task_id_combo.addItems(TASK_ID_OPTIONS)
        self.task_id_combo.setFixedSize(160, DROPDOWN_HEIGHT)
        self.task_id_combo.setStyleSheet(COMBO_BOX_STYLE)

        # Feedback level dropdown
        self.feedback_level_combo = QComboBox(self)
        self.feedback_level_combo.addItems(FEEDBACK_LEVEL_OPTIONS)
        self.feedback_level_combo.setFixedSize(DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
        self.feedback_level_combo.setStyleSheet(COMBO_BOX_STYLE)

        # Timer display
        self.timer_display = QLCDNumber(self)
        self.timer_display.setDigitCount(5)
        self.timer_display.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.timer_display.setFixedSize(DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
        self.timer_display.setStyleSheet(COMBO_BOX_STYLE)
        self.timer_display.display(DISPLAY_TIME_1)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Play button
        self.play_button = QPushButton('Play', self)
        self.play_button.setFixedSize(DROPDOWN_WIDTH, DROPDOWN_HEIGHT)
        self.play_button.setStyleSheet(BUTTON_STYLE)
        self.play_button.clicked.connect(self.start_phase_1)

    def _create_text_elements(self):
        """Create text elements (instruction, paragraph, input)"""
        # Instruction label
        self.instruction = QLabel(TASK_INSTRUCTION, self)
        self.instruction.setWordWrap(True)
        self.instruction.setStyleSheet(INSTRUCTION_STYLE)

        # Paragraph label
        self.paragraph = QLabel("", self)
        self.paragraph.setWordWrap(True)
        self.paragraph.setStyleSheet(PARAGRAPH_STYLE)

        # Text input
        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText('Write your response here...')
        self.text_input.setStyleSheet(TEXT_INPUT_STYLE)

    def _create_submit_button(self):
        """Create submit button"""
        self.button = QPushButton('Submit', self)
        self.button.setFixedSize(150, 50)
        self.button.setStyleSheet(BUTTON_STYLE)
        self.button.clicked.connect(self.submit_button_pressed)

    def _setup_layout(self):
        """Set up the main layout"""
        # Dropdown layout
        combo_timer_layout = QHBoxLayout()
        combo_timer_layout.addSpacing(20)

        # Add dropdown controls with labels
        self._add_dropdown_with_label(combo_timer_layout, 'Agent:', self.agent_combo)
        self._add_dropdown_with_label(combo_timer_layout, 'Sub ID:', self.sub_id_combo)
        self._add_dropdown_with_label(combo_timer_layout, 'Task ID:', self.task_id_combo)
        self._add_dropdown_with_label(combo_timer_layout, 'Feedback Level:', self.feedback_level_combo)

        combo_timer_layout.addStretch(1)
        combo_timer_layout.addWidget(self.timer_display)
        combo_timer_layout.addSpacing(20)
        combo_timer_layout.addWidget(self.play_button)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.button)

        # Main layout
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

    def _add_dropdown_with_label(self, layout, label_text, dropdown):
        """Add dropdown with label to layout"""
        label = QLabel(label_text)
        label.setStyleSheet(DROPDOWN_LABEL_STYLE)
        layout.addWidget(label)
        layout.addWidget(dropdown)
        layout.addSpacing(20)

    def update_timer(self):
        """Update timer display and handle time expiration"""
        if self.time_left > 0:
            self.time_left -= 1
            minutes, seconds = divmod(self.time_left, 60)
            time_display = f"{minutes:02}:{seconds:02}"
            self.timer_display.display(time_display)
        else:
            # Stop the timer when time_left reaches 0
            self.timer.stop()

            if self.phase == 1:
                self.send_response_to_llm(self.text_input.toPlainText(), time.time(), self.time_left)
                self.start_phase_2()
            elif self.phase == 2:
                print(f"\n=== TIME'S UP - PHASE 2 AUTO-SUBMIT ===")
                self._save_phase_2_data("", submission_time=time.time(), time_left=0)
                QMessageBox.information(self, 'Warning', 'Time\'s up!')

    def submit_button_pressed(self):
        """Handle submit button press"""
        current_timestamp = time.time()
        remaining_time = self.time_left

        if self.phase == 1 and not self.response_1_saved:
            self.send_response_to_llm(self.text_input.toPlainText(), current_timestamp, remaining_time)
            self.start_phase_2()
        elif self.phase == 2 and not self.response_2_saved:
            self._save_phase_2_data("", submission_time=current_timestamp, time_left=remaining_time)
            self.timer.stop()

    def start_phase_1(self):
        """Start Phase 1 of the task"""
        # Load paragraphs based on feedback level
        feedback_level = self.feedback_level_combo.currentText()
        task_id = self.task_id_combo.currentText()
        task_number = task_id[-1]

        # Load files
        question_file_path = get_question_file_path(task_number, self.set_number)
        error_file_path = get_error_file_path(task_number, self.set_number)
        answer_file_path = get_answer_file_path(task_number, self.set_number)

        self.error = self.data_manager.load_file(error_file_path)
        self.answer = self.data_manager.load_file(answer_file_path)
        self.paragraph.setText(self.data_manager.load_file(question_file_path))

        # Start the timer for Phase 1
        self.timer.start(1000)
        self.time_left = TIME_PHASE_1
        self.phase = 1

    def start_phase_2(self):
        """Start Phase 2 of the task"""
        self.phase = 2
        self.response_1_saved = True
        self.time_left = TIME_PHASE_2
        self.timer_display.display(DISPLAY_TIME_2)
        self.timer.start(1000)

    def send_response_to_llm(self, submitted_response, submission_time, time_left):
        """Send response to LLM and handle feedback"""
        try:
            feedback_level = self.feedback_level_combo.currentText()

            # Get LLM response
            openai_response = self.llm_handler.get_feedback_response(
                feedback_level, self.paragraph.text(), self.answer, self.error, submitted_response
            )

            print(f"OpenAI response: {openai_response}")

            # Send feedback to appropriate agent
            self._send_feedback_to_agent(openai_response)

            # Save data for phase 1
            self._save_phase_1_data(openai_response, submission_time, time_left)

        except Exception as e:
            print(f"Error: {e}")
            QMessageBox.warning(self, 'Error', 'Failed to get response from OpenAI API.')

    def _send_feedback_to_agent(self, feedback_text):
        """Send feedback to the appropriate agent"""
        agent_id = self.agent_combo.currentText()

        # Skip if no feedback (F_4 level)
        if not feedback_text:
            return

        if agent_id == 'agent_1':
            # Send feedback to NAO robot
            try:
                self.robot_handler.send_feedback_to_robot(feedback_text)
            except Exception as e:
                print(f"Robot communication failed: {e}")

        elif agent_id == 'agent_2':
            # Use TTS for agent_2
            try:
                self.tts_handler.speak(feedback_text, use_google_cloud=True)
            except Exception as e:
                print(f"TTS failed: {e}")

    def _save_phase_1_data(self, openai_response, submission_time, time_left):
        """Save Phase 1 data"""
        message = self.data_manager.collect_data(
            phase=1,
            sub_id=self.sub_id_combo.currentText(),
            task_id=self.task_id_combo.currentText(),
            agent_id=self.agent_combo.currentText(),
            feedback_level=self.feedback_level_combo.currentText(),
            set_number=self.set_number,
            user_response=self.text_input.toPlainText(),
            openai_response=openai_response,
            submission_time=submission_time,
            time_left=time_left
        )
        print(f"\n=== PHASE 1 COMPLETED ===")
        print(f"✓ Response 1 saved successfully")
        print(f"✓ Feedback sent to {self.agent_combo.currentText()}")
        print(f"✓ Moving to Phase 2...")
        QMessageBox.information(self, 'Status', message)

    def _save_phase_2_data(self, openai_response="", submission_time=None, time_left=None):
        """Save Phase 2 data"""
        self.response_2_saved = True
        message = self.data_manager.collect_data(
            phase=2,
            sub_id=self.sub_id_combo.currentText(),
            task_id=self.task_id_combo.currentText(),
            agent_id=self.agent_combo.currentText(),
            feedback_level=self.feedback_level_combo.currentText(),
            set_number=self.set_number,
            user_response=self.text_input.toPlainText(),
            openai_response=openai_response,
            submission_time=submission_time,
            time_left=time_left
        )
        print(f"\n=== PHASE 2 COMPLETED ===")
        print(f"✓ Response 2 saved successfully")
        print(f"✓ Study session completed!")
        print(f"✓ Closing application...")
        QMessageBox.information(self, 'Status', message)

        # Auto-close the application after Phase 2
        def close_application():
            print("Terminating application...")
            QApplication.quit()

        QTimer.singleShot(1000, close_application)  # Close after 1 second