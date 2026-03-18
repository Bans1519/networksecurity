import os
import sys
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from project.constant.training_pipeline import TARGET_COLUMN
from project.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from project.entity.config_entity import DataTransformationConfig
from project.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact    
)

from project.exception.exception import CustomException
from project.logging.logger import logging
from project.utils.main_utils.utils import save_numpy_array_data, save_object