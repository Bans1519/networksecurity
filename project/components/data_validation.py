from project.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from project.entity.config_entity import DataValidationConfig
from project.exception.exception import CustomException
from project.logging.logger import logging
from project.constant.training_pipeline import SCHEMA_FILE_PATH
from project.utils.main_utils.utils import read_yaml_file, write_yaml_file
from scipy.stats import ks_2samp
import os
import sys
import pandas as pd


class DataValidation:

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise CustomException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            required_columns = len(self._schema_config["columns"])
            actual_columns = len(dataframe.columns)

            logging.info(f"Required columns: {required_columns}")
            logging.info(f"Actual columns: {actual_columns}")
            logging.info(f"Schema columns: {list(self._schema_config['columns'].keys())}")
            logging.info(f"Dataframe columns: {list(dataframe.columns)}")

            return required_columns == actual_columns

        except Exception as e:
            raise CustomException(e, sys)

    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:
            drift_report = {}
            drift_found = False

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]

                ks_result = ks_2samp(d1, d2)

                drift_status = ks_result.pvalue < threshold
                if drift_status:
                    drift_found = True

                drift_report[column] = {
                    "p_value": float(ks_result.pvalue),
                    "drift_detected": bool(drift_status)
                }

            # Save drift report
            drift_report_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_path, content=drift_report)

            return not drift_found  # True means no drift

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_path = self.data_ingestion_artifact.trained_file_path
            test_path = self.data_ingestion_artifact.test_file_path

            train_df = self.read_data(train_path)
            test_df = self.read_data(test_path)

            error_message = ""

            # Validate columns
            if not self.validate_number_of_columns(train_df):
                error_message += "Train dataset column mismatch. "

            if not self.validate_number_of_columns(test_df):
                error_message += "Test dataset column mismatch. "

            if error_message:
                raise CustomException(error_message, sys)

            # Detect drift
            validation_status = self.detect_dataset_drift(train_df, test_df)

            # Save validated data
            os.makedirs(self.data_validation_config.valid_data_dir, exist_ok=True)

            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            return DataValidationArtifact(
                validation_status=validation_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise CustomException(e, sys)