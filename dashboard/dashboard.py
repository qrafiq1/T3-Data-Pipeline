"""Creates streamlit dashboard"""
from os import environ
from datetime import datetime as dt
import redshift_connector
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv


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


def load_data(start_date, end_date):
    """Gets a dataframe of the desired data"""
    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute("SET search_path TO qasim_rafiq_schema")

    query = """
            SELECT tr.at, p.payment_method, tr.total, t.truck_name 
            FROM FACT_Transaction AS tr
            JOIN DIM_Truck AS t ON tr.truck_id = t.truck_id
            JOIN DIM_Payment_Method AS p ON tr.payment_method_id = p.payment_method_id
            WHERE tr.at BETWEEN %s AND %s;
            """

    cursor.execute(query, (start_date, end_date))
    rows = cursor.fetchall()

    columns = ['at', 'payment_method', 'total', 'truck_name']
    data = pd.DataFrame(rows, columns=columns)

    return data


def setup_page():
    """sets up Streamlit page"""
    st.set_page_config(page_title="Truck Revenue Dashboard", layout="wide")
    st.title("Truck Transaction Dashboard")

    date_range = get_dates()

    if date_range:
        start_date, end_date = date_range
        filtered_data = load_data(start_date, end_date)
        filtered_data['hour'] = filtered_data['at'].dt.hour

        col1, col2, col3 = st.columns(3)

        with col1:
            truck_payment_method(filtered_data)

        with col2:
            truck_revenue_time(filtered_data)

        with col3:
            truck_pie_chart(filtered_data)


def get_dates():
    """Filters the dataframe by date"""
    selected_date_range = st.date_input(
        "Select Date Range",
        value=(dt(2024, 10, 20), dt.today())
    )

    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        if start_date and end_date:
            return start_date, end_date
    else:
        st.warning("Please select both a start and an end date.")


def truck_pie_chart(data):
    """Creates a pie chart for transactions"""
    if 'truck_name' in data.columns:
        transaction_counts = data.groupby('truck_name').size(
        ).reset_index(name='Number of Transactions')

        st.subheader("Total Number of Transactions per Truck")
        fig = px.pie(transaction_counts, names='truck_name',
                     values='Number of Transactions', title="Transactions per Truck")
        st.plotly_chart(fig)
    else:
        st.error("Column 'truck_name' not found in the uploaded file.")


def truck_payment_method(data):
    """Creates a grouped bar chart for payment type"""
    if 'truck_name' in data.columns:
        truck_revenue = data.groupby(["truck_name", "payment_method"])[
            'total'].sum().reset_index()

        st.subheader("Total Revenue per Truck by Payment Type")
        fig = px.bar(
            truck_revenue,
            x='truck_name',
            y='total',
            color='payment_method',
            barmode='group',
            labels={'truck_name': 'Truck Name', 'total': 'Total Revenue'},
            title="Revenue per Truck (Cash vs Card)"
        )
        st.plotly_chart(fig)
    else:
        st.error("Column 'truck_name' not found in the uploaded file.")


def truck_revenue_time(data):
    """Creates a line chart for hourly revenue"""
    if 'truck_name' in data.columns:
        hourly_revenue = data.groupby(['truck_name', 'hour'])[
            'total'].sum().reset_index()

        st.subheader("Revenue Over Time for Each Truck")
        fig = px.line(
            hourly_revenue,
            x='hour',
            y='total',
            color='truck_name',
            labels={'hour': 'Hour of the Day', 'total': 'Total Revenue'},
            title="Hourly Revenue by Truck"
        )
        st.plotly_chart(fig)
    else:
        st.error("Column 'truck_name' not found in the uploaded file.")


if __name__ == "__main__":
    setup_page()
