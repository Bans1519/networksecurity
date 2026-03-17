from project.components.data_ingestion import DataIngestion
from project.components.data_validation import DataValidation
from project.logging.logger import logging
from project.exception.exception import CustomException
from project.entity.config_entity import DataIngestionConfig, DataValidationConfig
from project.entity.config_entity import TrainingPipelineConfig
from project.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
import sys

if __name__ == '__main__':
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Initiating the data ingestion...")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info('Data Initiation completed.')
        print(dataingestionartifact)
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact, data_validation_config)
        logging.info('Initiate the data validation')
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info('Data validation completed.')
        print(data_validation_artifact)
        
    except Exception as e:
        logging.error(e)