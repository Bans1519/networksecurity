import sys
from project.logging import logger

class CustomException(Exception):
    def __init__(self, error_message, error_details: sys):
        super().__init__(error_message)
        self.error_message = error_message

        # Try to extract traceback info
        _, _, exc_tb = error_details.exc_info()

        if exc_tb is not None:
            self.line_number = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
        else:
            # When raised manually (no traceback available)
            self.line_number = "N/A"
            self.file_name = "N/A"

    def __str__(self):
        return (
            f"\n\n🔥 Custom Exception Occurred 🔥\n"
            f"--------------------------------------\n"
            f"📄 File: {self.file_name}\n"
            f"🔢 Line: {self.line_number}\n"
            f"💬 Message: {self.error_message}\n"
            f"--------------------------------------\n"
        )