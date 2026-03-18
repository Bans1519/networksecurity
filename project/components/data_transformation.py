import sys
import os
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

from project.constant.training_pipeline import TARGET_COLUMN
from project.entity.config_entity import DataTransformationConfig
from project.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact

from project.exception.exception import CustomException
from project.logging.logger import logging
from project.utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationArtifact):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise CustomException(e, sys)
    
    @staticmethod
    def read_data(file_path)-> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CustomException(e, sys)
    
    #  Feature Engineering
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Fix datatype
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

            # New features
            df["AvgCharges"] = df["TotalCharges"] / (df["tenure"] + 1)

            df["tenure_group"] = pd.cut(
                df["tenure"],
                bins=[0, 12, 24, 48, 72],
                labels=["0-1yr", "1-2yr", "2-4yr", "4-6yr"]
            )

            df["is_long_term"] = np.where(df["tenure"] > 24, 1, 0)

            return df

        except Exception as e:
            raise CustomException(e, sys)

    #  Preprocessing Pipeline
    def get_data_transformer_object(self):
        try:
            numerical_columns = [
                "tenure", "MonthlyCharges", "TotalCharges",
                "AvgCharges", "is_long_term"
            ]

            categorical_columns = [
                "gender", "SeniorCitizen", "Partner", "Dependents",
                "PhoneService", "MultipleLines", "InternetService",
                "OnlineSecurity", "OnlineBackup", "DeviceProtection",
                "TechSupport", "StreamingTV", "StreamingMovies",
                "Contract", "PaperlessBilling", "PaymentMethod",
                "tenure_group"
            ]

            num_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])

            cat_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ])

            preprocessor = ColumnTransformer([
                ("num", num_pipeline, numerical_columns),
                ("cat", cat_pipeline, categorical_columns)
            ])

            return preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("Starting Data Transformation")

            # Load data
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

            #  Feature Engineering
            train_df = self.feature_engineering(train_df)
            test_df = self.feature_engineering(test_df)

            # Split input & target
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN].map({"Yes": 1, "No": 0})

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN].map({"Yes": 1, "No": 0})

            # Preprocessor
            preprocessor = self.get_data_transformer_object()

            #  SMOTE ONLY on train
            train_pipeline = ImbPipeline([
                ("preprocessor", preprocessor),
                ("smote", SMOTE(sampling_strategy=0.7, random_state=42))
            ])

            X_train, y_train = train_pipeline.fit_resample(
                input_feature_train_df,
                target_feature_train_df
            )

            #  transform test (NO SMOTE)
            X_test = preprocessor.transform(input_feature_test_df)

            # Save preprocessor
            save_object(
                file_path=self.data_transformation_config.transformed_object_file_path,
                obj=preprocessor
            )

            # Save transformed arrays
            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_train_file_path,
                array=np.c_[X_train, y_train]
            )

            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_test_file_path,
                array=np.c_[X_test, target_feature_test_df]
            )

            # Return artifact
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            logging.info("Data Transformation Completed")

            return data_transformation_artifact

        except Exception as e:
            raise CustomException(e, sys)