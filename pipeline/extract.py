"""Extracts truck history data from an s3 bucket"""
import os
from boto3 import client


def download_truck_data_files():
    """Downloads relevant files from S3 to a data/ folder."""
    client_s3 = client('s3')
    response = client_s3.list_objects_v2(
        Bucket='sigma-resources-truck', Prefix='historical/')

    truck_files = [obj['Key'] for obj in response['Contents']
                   if obj['Key'].endswith(".parquet")]

    output_file = "../data/"
    os.makedirs(output_file, exist_ok=True)

    if truck_files:
        for file_key in truck_files:
            file_path = os.path.join(output_file, os.path.basename(file_key))
            client_s3.download_file(
                'sigma-resources-truck', file_key, file_path)
        print("Files have been downloaded")
    else:
        print("No .parquet files found")

    response = client_s3.list_objects_v2(
        Bucket='sigma-resources-truck', Prefix='metadata/')

    file_key = [obj['Key'] for obj in response['Contents']
                if obj['Key'].endswith(".xlsx")]
    file_path = os.path.join(output_file, os.path.basename(file_key[0]))

    client_s3.download_file(
        'sigma-resources-truck', file_key[0], file_path)


if __name__ == "__main__":
    download_truck_data_files()
