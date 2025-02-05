from extract import download_truck_data_files
from transform import combine_transaction_data_files
from load import upload_transaction_data


def run_etl_process():
    """gets the data, cleans it, and uploads to redshift db."""
    download_truck_data_files()
    combine_transaction_data_files()
    upload_transaction_data()


if __name__ == "__main__":
    run_etl_process()
