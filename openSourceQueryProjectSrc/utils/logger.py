"""
This file holds the implementation of a simple logging capabilities.
For more "versatility" of it, the print function at the end can be changed
according to some other "logic".
"""
import threading
import datetime
import inspect


class MyLogger:

    def __init__(self):
        print("MyLogger::__init__")

    @staticmethod
    def log_to_std(msg_to_log: str) -> None:
        current_thread_name = threading.current_thread().name
        current_time = datetime.datetime.now()
        current_log_format = str(current_time) + " " + current_thread_name + " "
        prev_frame = inspect.currentframe().f_back
        if "self" in prev_frame.f_locals:
            current_calling_class_name = str(prev_frame.f_locals["self"].__class__.__name__) + "::"
            current_calling_func_name = inspect.stack()[1][3]
        else:
            current_calling_class_name = ""
            current_calling_func_name = inspect.currentframe().f_back.f_code.co_name

        ret_str = current_log_format + current_calling_class_name + current_calling_func_name + " - "
        print(ret_str + msg_to_log)
