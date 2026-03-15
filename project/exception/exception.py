import sys
from project.logging import logger

class CustomException(Exception):
    def __init__(self,error_message,error_details:sys):
        self.error_message = error_message
        _,_,exc_tb = error_details.exc_info()
        
        self.lineno = exc_tb.tb_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        
    def __str__(self):
         return (
            f"\n\n🔥 **Custom Exception Occurred** 🔥\n"
            f"--------------------------------------\n"
            f"📄 **File:** {self.file_name}\n"
            f"🔢 **Line:** {self.line_number}\n"
            f"💬 **Message:** {self.error_message}\n"
            f"--------------------------------------\n"
        )

        
if __name__ == '__main__':
    try:
        logger.logging.info('Enter the try block')
        a = 1/0
        print("This will not be printed",a)
    except Exception as e:
        raise CustomException(e,sys)