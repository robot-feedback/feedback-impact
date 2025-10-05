

import time
import os
import cv2
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QMessageBox,
                             QLabel, QHBoxLayout, QComboBox, QLCDNumber, QApplication,
                             QScrollArea, QGridLayout, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

from config.config import *
from utils.task_1_data_manager import DataManager
from utils.task_1_llm_handler import LLMHandler
from utils.robot_handler import RobotHandler
from utils.tts_handler import TTSHandler


class PatternWidget(QWidget):
    """Widget to display a single pattern with image and label"""

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
    """Video capture widget for pattern recognition"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Store reference to parent (SimpleWindow)

        button_width, button_height = 240, 50

        main_layout = QHBoxLayout(self)

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
        self.object_name_field.setPlaceholderText("Object Name")

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

        # Add widgets to the layout
        button_layout.addWidget(self.object_name_field)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.get_feedback_button)

        right_layout.addLayout(button_layout)

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

        self.captured_images = []
        self.object_list = []

    def save_pattern(self):
        """Save captured pattern from camera"""
        ret, frame = self.cap.read()
        if ret:
            object_name = self.object_name_field.text().strip()
            if not object_name:
                QMessageBox.warning(self, 'Warning', 'Please enter a name for the object before saving.')
                return

            # Append the captured frame to the captured_images list
            self.captured_images.append((frame, object_name))
            self.update_captured_images()

            # Access configuration from parent
            sub_id = self.parent.sub_id_combo.currentText()
            task_id = self.parent.task_id_combo.currentText()
            agent_id = self.parent.agent_combo.currentText()
            feedback_level = self.parent.feedback_level_combo.currentText()

            # Define directory path based on phase
            directory_path = self.parent.data_manager.get_image_directory_path(
                task_id, agent_id, sub_id, feedback_level, self.parent.phase
            )

            print(f'Directory Path: {directory_path}')
            os.makedirs(directory_path, exist_ok=True)

            # Save the captured frame as an image file
            image_file_path = os.path.join(directory_path, f"{object_name}.png")
            cv2.imwrite(image_file_path, frame)

            print(f"Pattern saved at {image_file_path}")
            self.object_list.append(object_name)

            # Reset the object name field
            self.object_name_field.clear()

    def update_frame(self):
        """Update video feed frame"""
        ret, frame = self.cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                640, 480, Qt.AspectRatioMode.KeepAspectRatio))

    def update_captured_images(self):
        """Update the grid display of captured patterns"""
        # Clear existing items in the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Calculate number of columns based on scroll area width
        scroll_width = self.scroll_area.width() - 20
        pattern_width = 160
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
        """Handle feedback submission"""
        current_timestamp = time.time()
        remaining_time = self.parent.time_left

        self.get_feedback_button.setEnabled(False)

        if self.parent.phase == 1:
            self.parent.timer.stop()

            # Get feedback from LLM
            feedback_response = self._process_feedback()
            print(f"Feedback received: {feedback_response}")

            # Send feedback to agent
            self._send_feedback_to_agent(feedback_response)

            # Save phase 1 data
            self._save_phase_1_data(feedback_response, current_timestamp, remaining_time)

            # Reset and move to phase 2
            self.object_list = []
            self.parent.start_phase_2()
            self.get_feedback_button.setEnabled(True)

        elif self.parent.phase == 2:
            self.parent.timer.stop()
            self._save_phase_2_data(current_timestamp, remaining_time)

    def _process_feedback(self):
        """Process feedback using LLM handler"""
        try:
            feedback_level = self.parent.feedback_level_combo.currentText()

            # Prepare data for LLM
            image_path = self.parent.question_file_path
            shape_list_str = self.parent.shape_list
            object_list_str = ', '.join(self.object_list)
            example_objects_str = self.parent.example_object_list

            # Get feedback from LLM handler
            feedback = self.parent.llm_handler.get_feedback_response(
                feedback_level, image_path, shape_list_str, object_list_str, example_objects_str
            )

            return feedback

        except Exception as e:
            print(f"Error processing feedback: {e}")
            QMessageBox.warning(self, 'Error', 'Failed to get response from OpenAI API.')
            return ""

    def _send_feedback_to_agent(self, feedback_text):
        """Send feedback to the appropriate agent"""
        agent_id = self.parent.agent_combo.currentText()
        feedback_level = self.parent.feedback_level_combo.currentText()

        # Skip if no feedback (F_4 level)
        if feedback_level == "F_4" or not feedback_text:
            return

        if agent_id == 'agent_1':
            # Send feedback to NAO robot
            try:
                self.parent.robot_handler.send_feedback_to_robot(feedback_text)
            except Exception as e:
                print(f"Robot communication failed: {e}")

        elif agent_id == 'agent_2':
            # Use TTS for agent_2
            try:
                self.parent.tts_handler.speak(feedback_text, use_google_cloud=True)
            except Exception as e:
                print(f"TTS failed: {e}")

    def _save_phase_1_data(self, openai_response, submission_time, time_left):
        """Save Phase 1 data"""
        message = self.parent.data_manager.collect_data(
            phase=1,
            sub_id=self.parent.sub_id_combo.currentText(),
            task_id=self.parent.task_id_combo.currentText(),
            agent_id=self.parent.agent_combo.currentText(),
            feedback_level=self.parent.feedback_level_combo.currentText(),
            object_list=self.object_list,
            openai_response=openai_response,
            submission_time=submission_time,
            time_left=time_left
        )
        print(f"\n=== PHASE 1 COMPLETED ===")
        print(f"✓ Response 1 saved successfully")
        print(f"✓ Feedback sent to {self.parent.agent_combo.currentText()}")
        print(f"✓ Moving to Phase 2...")
        QMessageBox.information(self, 'Status', message)

    def _save_phase_2_data(self, submission_time, time_left):
        """Save Phase 2 data"""
        message = self.parent.data_manager.collect_data(
            phase=2,
            sub_id=self.parent.sub_id_combo.currentText(),
            task_id=self.parent.task_id_combo.currentText(),
            agent_id=self.parent.agent_combo.currentText(),
            feedback_level=self.parent.feedback_level_combo.currentText(),
            object_list=self.object_list,
            openai_response="",
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

        QTimer.singleShot(1000, close_application)

    def closeEvent(self, event):
        """Clean up video capture on close"""
        self.cap.release()


class SimpleWindow(QWidget):
    """Main application window for Task 1"""

    def __init__(self, set_number):
        super().__init__()
        self.set_number = set_number
        self.phase = 1
        self.response_1_saved = False
        self.response_2_saved = False
        self.time_left = 0

        print(f"\n=== PATTERN RECOGNITION STUDY STARTED ===")
        print(f"Set Number: {set_number}")
        print(f"Phase 1: 4 minutes (Pattern creation)")
        print(f"Phase 2: 2 minutes (Review time)")
        print(f"==========================================\n")

        # Initialize handlers
        self.data_manager = DataManager()
        self.llm_handler = LLMHandler()
        self.robot_handler = RobotHandler()
        self.tts_handler = TTSHandler()

        # Store loaded content
        self.question_file_path = ""
        self.shape_list = ""
        self.example_object_list = ""

        self.initUI()

    def initUI(self):
        """Initialize the user interface"""
        self.setFixedSize(TASK_1_WINDOW_WIDTH, TASK_1_WINDOW_HEIGHT)

        # Title
        self.title = QLabel('Pattern Recognition Study', self)
        self.title.setStyleSheet(TASK_1_TITLE_STYLE)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create dropdown controls
        self._create_dropdown_controls()

        # Create instruction and content elements
        self._create_content_elements()

        # Set up layout
        self._setup_layout()

        self.setWindowTitle('Pattern Recognition Study')

    def _create_dropdown_controls(self):
        """Create all dropdown controls and timer"""
        combo_box_style = TASK_1_COMBO_BOX_STYLE
        drop_width, drop_height = TASK_1_DROPDOWN_WIDTH, TASK_1_DROPDOWN_HEIGHT

        # Agent dropdown
        self.agent_combo = QComboBox(self)
        self.agent_combo.addItems(TASK_1_AGENT_OPTIONS)
        self.agent_combo.setFixedSize(160, drop_height)
        self.agent_combo.setStyleSheet(combo_box_style)

        # Subject ID dropdown
        self.sub_id_combo = QComboBox(self)
        self.sub_id_combo.addItems(TASK_1_SUBJECT_ID_OPTIONS)
        self.sub_id_combo.setFixedSize(drop_width, drop_height)
        self.sub_id_combo.setStyleSheet(combo_box_style)

        # Task ID dropdown
        self.task_id_combo = QComboBox(self)
        self.task_id_combo.addItems(TASK_1_TASK_ID_OPTIONS)
        self.task_id_combo.setFixedSize(160, drop_height)
        self.task_id_combo.setStyleSheet(combo_box_style)

        # Feedback level dropdown
        self.feedback_level_combo = QComboBox(self)
        self.feedback_level_combo.addItems(TASK_1_FEEDBACK_LEVEL_OPTIONS)
        self.feedback_level_combo.setFixedSize(drop_width, drop_height)
        self.feedback_level_combo.setStyleSheet(combo_box_style)

        # Timer display
        self.timer_display = QLCDNumber(self)
        self.timer_display.setDigitCount(5)
        self.timer_display.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)
        self.timer_display.setFixedSize(drop_width, drop_height)
        self.timer_display.setStyleSheet(combo_box_style)
        self.timer_display.display(TASK_1_DISPLAY_TIME_1)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Play button
        self.play_button = QPushButton('Play', self)
        self.play_button.setFixedSize(drop_width, drop_height)
        self.play_button.setStyleSheet(TASK_1_BUTTON_STYLE)
        self.play_button.clicked.connect(self.start_phase_1)

    def _create_content_elements(self):
        """Create instruction, paragraph, and video capture widget"""
        # Instruction label
        self.instruction = QLabel(TASK_1_INSTRUCTION, self)
        self.instruction.setWordWrap(True)
        self.instruction.setStyleSheet(TASK_1_INSTRUCTION_STYLE)

        # Hidden paragraph (for shapes image)
        self.paragraph = QLabel("", self)
        self.paragraph.setWordWrap(True)
        self.paragraph.setStyleSheet(TASK_1_PARAGRAPH_STYLE)
        self.paragraph.setVisible(False)

        # Hidden video capture widget
        self.video_capture_widget = VideoCaptureApp(self)
        self.video_capture_widget.setVisible(False)

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

        # Main layout
        layout = QVBoxLayout()
        layout.addSpacing(20)
        layout.addWidget(self.title)
        layout.addSpacing(50)
        layout.addLayout(combo_timer_layout)
        layout.addSpacing(40)
        layout.addWidget(self.instruction)
        layout.addSpacing(10)
        layout.addWidget(self.paragraph)
        layout.addWidget(self.video_capture_widget)

        self.setLayout(layout)

    def _add_dropdown_with_label(self, layout, label_text, dropdown):
        """Add dropdown with label to layout"""
        label = QLabel(label_text)
        label.setStyleSheet(TASK_1_DROPDOWN_LABEL_STYLE)
        layout.addWidget(label)
        layout.addWidget(dropdown)
        layout.addSpacing(20)

    def start_phase_1(self):
        """Start Phase 1 of the task"""
        set_id = self.set_number
        task_id = self.task_id_combo.currentText()

        # Disable configuration controls
        self.sub_id_combo.setEnabled(False)
        self.task_id_combo.setEnabled(False)
        self.agent_combo.setEnabled(False)
        self.feedback_level_combo.setEnabled(False)
        self.play_button.setEnabled(False)

        # Load task files
        task_number = task_id[-1]
        self.question_file_path = f"database/task_{task_number}/question/q_{set_id}.png"
        shape_file_path = f"database/task_{task_number}/shape_list/shape_{set_id}.txt"
        object_file_path = f"database/task_{task_number}/object_list/object_{set_id}.txt"

        # Load shapes and objects
        self.shape_list = self.data_manager.load_shapes_from_file(shape_file_path)
        self.example_object_list = self.data_manager.load_objects_from_file(object_file_path)

        print(f"Shapes: {self.shape_list}")
        print(f"Example objects: {self.example_object_list}")

        # Display shapes image
        pixmap = QPixmap(self.question_file_path)
        desired_width = 300
        scaled_pixmap = pixmap.scaledToWidth(desired_width, Qt.TransformationMode.SmoothTransformation)
        self.paragraph.setPixmap(scaled_pixmap)
        self.paragraph.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Show hidden elements
        self.paragraph.setVisible(True)
        self.video_capture_widget.setVisible(True)

        # Start the timer
        self.timer.start(1000)
        self.time_left = TASK_1_TIME_PHASE_1
        self.phase = 1

    def update_timer(self):
        """Update timer display and handle time expiration"""
        if self.time_left > 0:
            self.time_left -= 1
            minutes, seconds = divmod(self.time_left, 60)
            time_display = f"{minutes:02}:{seconds:02}"
            self.timer_display.display(time_display)
        else:
            self.timer.stop()

            if self.phase == 1:
                self.video_capture_widget.get_feedback()
                self.start_phase_2()
            elif self.phase == 2:
                self.video_capture_widget.get_feedback()
                QMessageBox.information(self, 'Warning', 'Time\'s up!')

    def start_phase_2(self):
        """Start Phase 2 of the task"""
        self.phase = 2
        self.response_1_saved = True
        self.time_left = TASK_1_TIME_PHASE_2
        self.timer_display.display(TASK_1_DISPLAY_TIME_2)
        self.timer.start(1000)
