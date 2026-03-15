from project.components.data_ingestion import DataIngestion
from project.logging.logger import logging
from project.exception.exception import CustomException
from project.entity.config_entity import DataIngestionConfig
from project.entity.config_entity import TrainingPipelineConfig
import sys

if __name__ == '__main__':
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Initiating the data ingestion...")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        print(dataingestionartifact)
        
    except Exception as e:
        raise CustomException(e, sys)