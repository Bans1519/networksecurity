import os
import sys
import json
import pandas as pd
import pymongo
import certifi

from dotenv import load_dotenv
from project.exception.exception import CustomException
from project.logging.logger import logging

# Load environment variables
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
ca = certifi.where()


class ChurnDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise CustomException(e, sys)

    def csv_to_json_convertor(self, file_path):
        """
        Reads a CSV file and converts it into a list of JSON-like dictionaries.
        """
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = data.to_dict(orient="records")
            return records

        except Exception as e:
            raise CustomException(e, sys)

    def insert_data_to_mongodb(self, records, database, collection):
        try:
            client = pymongo.MongoClient(
                MONGO_DB_URL,
                tlsCAFile=ca,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                retryWrites=True,
                w="majority"
            )

            # Force connection test
            client.admin.command("ping")

            db = client[database]
            col = db[collection]
            #clean old data
            col.delete_many({})

            # Insert in smaller batches to avoid connection drops
            batch_size = 500
            for i in range(0, len(records), batch_size):
                col.insert_many(records[i:i+batch_size])

            return len(records)

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    FILE_PATH = r"data/train_new.csv"  
    DATABASE = "BMPROJECTS"
    COLLECTION = "CustomerChurn"

    network_obj = ChurnDataExtract()

    # Convert CSV to JSON
    records = network_obj.csv_to_json_convertor(FILE_PATH)
    print(f"Sample record: {records[0]}")

    # Insert into MongoDB
    inserted_count = network_obj.insert_data_to_mongodb(records, DATABASE, COLLECTION)
    print(f"Inserted records: {inserted_count}")