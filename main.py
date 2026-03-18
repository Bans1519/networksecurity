from project.components.data_ingestion import DataIngestion
from project.components.data_validation import DataValidation
from project.components.data_transformation import DataTransformation
from project.entity.config_entity import DataTransformationConfig
from project.entity.artifact_entity import DataTransformationArtifact
from project.components.model_trainer import ModelTrainer
from project.logging.logger import logging
from project.exception.exception import CustomException
from project.entity.config_entity import DataIngestionConfig, DataValidationConfig, ModelTrainerConfig, TrainingPipelineConfig
from project.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
import sys

if __name__ == '__main__':
    try:
        trainingpipelineconfig = TrainingPipelineConfig()

        
        #  Data Ingestion
        
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)

        logging.info("Initiating the data ingestion...")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info('Data ingestion completed.')
        print(dataingestionartifact)

        
        #  Data Validation
        
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact, data_validation_config)

        logging.info('Initiating data validation...')
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info('Data validation completed.')
        print(data_validation_artifact)

        
        #  Data Transformation 
        
        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)

        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config
        )

        logging.info('Initiating data transformation...')
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info('Data transformation completed.')
        print(data_transformation_artifact)           
        
        #  Model Trainer
        
        model_trainer_config = ModelTrainerConfig(trainingpipelineconfig)

        model_trainer = ModelTrainer(
        data_transformation_artifact=data_transformation_artifact,
        model_trainer_config=model_trainer_config
        )

        logging.info("Initiating model training...")
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model training completed.")

        print(model_trainer_artifact)
        
    except Exception as e:
        logging.error(e)