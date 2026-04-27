"""
Robot Handler Module
Handles NAO robot communication via ZMQ
"""

import zmq
from config.config import ZMQ_ADDRESS

class RobotHandler:
    """Handles NAO robot communication"""

    def __init__(self):
        """Initialize ZMQ context and socket"""
        self.context = None
        self.socket = None

    def send_feedback_to_robot(self, feedback_text):
        """
        Send feedback to NAO robot via ZMQ

        Args:
            feedback_text (str): Feedback text to send to robot

        Returns:
            str: Acknowledgment message from robot

        Raises:
            Exception: If ZMQ communication fails
        """
        try:
            # Create ZMQ context and socket
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 second timeout
            self.socket.connect(ZMQ_ADDRESS)

            # Send feedback to robot
            self.socket.send_string(feedback_text)

            # Wait for acknowledgment
            acknowledgment = self.socket.recv_string()
            print(f"Received ack from NAO: {acknowledgment}")

            return acknowledgment

        except Exception as e:
            print(f"Robot communication error: {e}")
            raise e

        finally:
            # Clean up ZMQ resources
            self._cleanup()

    def _cleanup(self):
        """Clean up ZMQ resources"""
        try:
            if self.socket:
                self.socket.close()
            if self.context:
                self.context.term()
        except Exception as e:
            print(f"Error cleaning up ZMQ resources: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self._cleanup()