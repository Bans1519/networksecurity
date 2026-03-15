import os
import sys
import numpy as np
import pandas as pd

"""
Defining common constant variable for training pipeline
"""
TARGET_COLUMN : str = "Churn"
PIPELINE_NAME : str = 'CustomerChurnModel'
ARTIFACT_DIR : str = 'Artifacts'
FILE_NAME : str = 'churndata.csv'

TRAIN_FILE_NAME : str = 'train.csv'
TEST_FILE_NAME : str = 'test.csv'


"""
Data Ingestion related constant start with DATA_INGESTION VAR NAME
"""

DATA_INGESTION_COLLECTION_NAME : str = 'CustomerChurn'
DATA_INGESTION_DATABASE_NAME : str = 'BMPROJECTS'
DATA_INGESTION_DIR_NAME : str = 'data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR : str = 'feature_store'
DATA_INGESTION_INGESTED_DIR : str = 'ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO : float = 0.3

