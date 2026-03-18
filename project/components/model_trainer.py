import os
import sys
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score

from project.utils.main_utils.utils import load_numpy_array_data, save_object
from project.entity.artifact_entity import ModelTrainerArtifact
from project.exception.exception import CustomException
from project.logging.logger import logging


class ModelTrainer:

    def __init__(self, data_transformation_artifact, model_trainer_config):
        self.data_transformation_artifact = data_transformation_artifact
        self.model_trainer_config = model_trainer_config


    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("Starting Model Training")
            
            # Loading transformed data
            
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            #  Computing imbalance ratio
            
            ratio = (len(y_train) - sum(y_train)) / sum(y_train)
            print("Imbalance ratio:", ratio)
            logging.info(f"Imbalance ratio: {ratio}")

            
            #  Defining models
            
            models = {
                "LogisticRegression": LogisticRegression(
                    max_iter=2000, class_weight="balanced", solver="liblinear"
                ),

                "RandomForest": RandomForestClassifier(
                    n_estimators=400, max_depth=12,
                    min_samples_split=5, min_samples_leaf=2,
                    class_weight="balanced", random_state=42
                ),

                "XGBoost": XGBClassifier(
                    n_estimators=500, learning_rate=0.03, max_depth=4,
                    subsample=0.9, colsample_bytree=0.9,
                    scale_pos_weight=ratio,
                    gamma=0.5, reg_lambda=5,reg_alpha=2,
                    random_state=42, eval_metric="logloss",
                    use_label_encoder=False
                )
            }

            
            #  Training & evaluating models
            
            best_model = None
            best_recall = 0
            best_threshold = 0.5
            best_model_name = None

            # Store only best result per model
            best_results = []

            for name, model in models.items():
                logging.info(f"Training {name}")
                model.fit(X_train, y_train)

                y_probs = model.predict_proba(X_test)[:, 1]
                roc_auc = roc_auc_score(y_test, y_probs)

                model_best_recall = 0
                model_best_threshold = 0
                model_best_precision = 0
                model_best_f1 = 0

                # Threshold sweep
                for threshold in np.arange(0.3, 0.8, 0.02):
                    y_pred = (y_probs >= threshold).astype(int)

                    recall = recall_score(y_test, y_pred)
                    precision = precision_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred)

                    # Track best threshold for THIS model
                    if recall > model_best_recall:
                        model_best_recall = recall
                        model_best_threshold = threshold
                        model_best_precision = precision
                        model_best_f1 = f1

                    # Track best model overall
                    if recall > best_recall:
                        best_recall = recall
                        best_model = model
                        best_threshold = threshold
                        best_model_name = name

                # Save only the best row for this model
                best_results.append({
                    "model": name,
                    "best_threshold": model_best_threshold,
                    "recall": model_best_recall,
                    "precision": model_best_precision,
                    "f1_score": model_best_f1,
                    "roc_auc": roc_auc
                })

            # Convert to DataFrame
            results_df = pd.DataFrame(best_results)
            print("\n BEST RESULTS PER MODEL")
            print(results_df)

            
            # Final evaluation of best model
            
            y_probs = best_model.predict_proba(X_test)[:, 1]
            y_pred = (y_probs >= best_threshold).astype(int)

            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_probs)

            print("\n FINAL BEST MODEL METRICS")
            print(f"Model: {best_model_name}")
            print(f"Recall: {recall}")
            print(f"Precision: {precision}")
            print(f"F1 Score: {f1}")
            print(f"ROC-AUC: {roc_auc}")
            print(f"Threshold: {best_threshold}")

            
            #  Save best model
            
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            
            #  Return artifact
            
            return ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                metric_artifact={
                    "model": best_model_name,
                    "recall": recall,
                    "precision": precision,
                    "f1_score": f1,
                    "roc_auc": roc_auc,
                    "threshold": best_threshold,
                    "results_dataframe": results_df
                },
                is_trained=True,
                message="Model training completed successfully"
            )

        except Exception as e:
            raise CustomException(e, sys)