"""Cleans the truck data into one file"""
import pandas as pd

INVALID_VALUES = ['blank', 'None', 'ERR', 'VOID', 'NULL', '0', '0.00', '']


def combine_transaction_data_files():
    """Loads and combines relevant files from the data/ folder.

    Produces a single combined file in the data/ folder."""

    file_path = "../data/TRUCK_DATA_HIST_"
    truck_files = []
    try:
        for i in range(1, 7):
            df = pd.read_parquet(f"{file_path}{i}.parquet")
            df["truck_id"] = i
            truck_files.append(df)

        combined_df = pd.concat(truck_files, ignore_index=True)

        clean_truck_data(combined_df)

        combined_csv_path = "../data/combined_truck_data_hist.csv"
        combined_df.to_csv(combined_csv_path, index=False)

        print("Data has been combined!")

    except Exception as e:
        print(e)


def clean_truck_data(trucks: pd.DataFrame):
    """Cleans the combined data frame"""

    trucks.dropna(inplace=True)

    for index in trucks.index:
        if trucks.loc[index, "total"] in INVALID_VALUES:
            trucks.drop(index, inplace=True)

    trucks['timestamp'] = pd.to_datetime(trucks['timestamp'])
    trucks['total'] = trucks['total'].astype(float)


if __name__ == "__main__":
    combine_transaction_data_files()
