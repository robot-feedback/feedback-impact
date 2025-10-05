"""
Main Application Entry Point
Feedback Study Application
Routes to Task 1 or Task 2 based on command line arguments
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication


def main():
    """Main function to run the application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Feedback Study Application")
    parser.add_argument('--task_id', type=str, required=True,
                       choices=['task_1', 'task_2'],
                       help='Task ID: task_1 (Pattern Recognition) or task_2 (Text Feedback)')
    parser.add_argument('--set_number', type=str, required=True,
                       help='Set number for the study')
    args = parser.parse_args()

    # Create the application
    app = QApplication(sys.argv)

    # Route to appropriate task based on task_id
    if args.task_id == 'task_1':
        from core.task_1_ui import SimpleWindow
        print(f"\n{'='*50}")
        print(f"Starting Task 1")
        print(f"Set Number: {args.set_number}")
        print(f"{'='*50}\n")
        window = SimpleWindow(args.set_number)

    elif args.task_id == 'task_2':
        from core.task_2_ui import SimpleWindow
        print(f"\n{'='*50}")
        print(f"Starting Task 2")
        print(f"Set Number: {args.set_number}")
        print(f"{'='*50}\n")
        window = SimpleWindow(args.set_number)

    else:
        print(f"Error: Unknown task_id '{args.task_id}'")
        print("Valid options are: task_1, task_2")
        sys.exit(1)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
