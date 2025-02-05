"""Uploads clean data to redshift database"""
from os import environ
import redshift_connector
from dotenv import load_dotenv
import pandas as pd


def get_connection():
    """Connects to redshift database"""
    load_dotenv()
    try:
        conn = redshift_connector.connect(
            host=environ["DATABASE_IP"],
            port=environ["DATABASE_PORT"],
            database=environ["DATABASE_NAME"],
            user=environ["DATABASE_USERNAME"],
            password=environ["DATABASE_PASSWORD"]
        )
        print("Connection done")
        return conn
    except Exception as e:
        raise RuntimeError(f"Failed to connect to the database: {e}") from e


def get_cursor(conn):
    """Gets the cursor"""
    try:
        cursor = conn.cursor()
        print("Cursor done")
        return cursor
    except Exception as e:
        raise RuntimeError(f"Failed to connect to the database: {e}") from e


def get_payment_method_id(payment_method: str, conn, cursor) -> int:
    """Gets the ids of cash and card"""
    try:
        cursor.execute(
            """SELECT payment_method_id FROM DIM_Payment_Method 
            WHERE payment_method = %s""", (payment_method,))
        conn.commit()
        payment_method_id = cursor.fetchone()[0]
        return payment_method_id
    except Exception as e:
        raise Exception(e) from e


def get_sample_data():
    """Gets a sample from the clean csv file"""
    return pd.read_csv("../data/combined_truck_data_hist.csv").sample(50)


def upload_transaction_data():
    """Uploads transaction data to the database."""
    conn = get_connection()
    cursor_ = get_cursor(conn)
    cursor_.execute("SET search_path TO qasim_rafiq_schema")

    trucks_sample = get_sample_data()

    cash_id = get_payment_method_id('cash', conn, cursor_)
    card_id = get_payment_method_id('card', conn, cursor_)

    trucks_sample['type'] = trucks_sample['type'].replace('cash', cash_id)
    trucks_sample['type'] = trucks_sample['type'].replace('card', card_id)

    try:
        for _, row in trucks_sample.iterrows():
            cursor_.execute(
                """INSERT INTO FACT_Transaction (truck_id, payment_method_id, total, at) 
                VALUES (%s, %s, %s, %s)""",
                (row['truck_id'], row['type'], row['total'], row['timestamp'])
            )
            conn.commit()
        print("Imported transaction data")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    upload_transaction_data()
