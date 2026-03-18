import numpy as np
import yaml
import pickle
from project.exception.exception import CustomException
from project.logging.logger import logging
import os, sys

def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its content as a dictionary.
    """
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise CustomException(e, sys)


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """
    Writes content to a YAML file. Creates directories if needed.
    If replace=True, deletes existing file before writing.
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        if replace and os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'w') as file:
            yaml.dump(content, file)

    except Exception as e:
        raise CustomException(e, sys)
    
def save_numpy_array_data(file_path: str, array: np.array):
    """
    save numpy array data to file
    file_path : str location of the file to save
    array : np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise CustomException(e, sys)
    
def save_object(file_path: str, obj:object)-> None:
    try:
        logging.info("Entered the save_object method of MainUtils class")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise CustomException(e, sys)
    