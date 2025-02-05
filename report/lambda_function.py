"""Returns a HTML string when the lambda is invoked"""
from os import environ
import json
from datetime import timedelta, datetime
from dotenv import load_dotenv
import redshift_connector
import redshift_connector.cursor


def lambda_handler(event, context):
    """Gets the html data when the lambda is invoked"""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        summary_data = load_data(cursor)
        html_data = convert_to_html(summary_data)
        return {"html_data": html_data}
    except Exception:
        print("Error retrieving the data.")
        return {"error": True, "message": "No data retrieved"}
    finally:
        cursor.close()
        conn.close()


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
        return conn
    except Exception as e:
        raise RuntimeError(f"Failed to connect to the database: {e}") from e


def get_cursor(conn):
    """Gets the cursor"""
    try:
        cursor = conn.cursor()
        cursor.execute("SET search_path TO qasim_rafiq_schema")
        return cursor
    except Exception as e:
        raise RuntimeError(f"Failed to connect to the database: {e}") from e


def save_to_json(data) -> None:
    """Saves the json data."""
    previous_day = datetime.now() - timedelta(days=1)
    file_name = f"report_data_{previous_day.strftime('%Y-%m-%d')}.json"
    with open(file_name, 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)


def get_previous_day() -> datetime:
    """Gets the start and end of the previous day"""
    today = datetime.now()
    yesterday_start = today - timedelta(days=1)
    yesterday_start = yesterday_start.replace(
        hour=0, minute=0, second=0)
    yesterday_end = yesterday_start + \
        timedelta(hours=23, minutes=59, seconds=59)
    return yesterday_start, yesterday_end


def load_data(cursor) -> dict:
    """Gets a dataframe of the desired data"""

    start_date, end_date = get_previous_day()

    query = """
            SELECT SUM(total) as Total_Transaction_Revenue
            FROM FACT_Transaction 
            WHERE at BETWEEN %s AND %s
            """

    cursor.execute(query, (start_date, end_date))
    total_transaction_value = cursor.fetchone()[0]

    query = """
            SELECT t.truck_id, t.truck_name, 
            COUNT(s.transaction_id) AS num_transactions, 
            SUM(s.total) AS total_value,
            SUM(CASE WHEN p.payment_method = 'cash' THEN 1 ELSE 0 END) AS cash_transactions,
            SUM(CASE WHEN p.payment_method = 'card' THEN 1 ELSE 0 END) AS card_transactions
            FROM FACT_Transaction AS s
            JOIN DIM_Truck t ON s.truck_id = t.truck_id
            JOIN DIM_Payment_Method p ON s.payment_method_id = p.payment_method_id
            WHERE s.at BETWEEN %s AND %s
            GROUP BY t.truck_id, t.truck_name
            ORDER BY t.truck_id
            """
    cursor.execute(query, (start_date, end_date))
    transactions_per_truck = cursor.fetchall()

    summary_data = {
        "date": start_date.strftime('%Y-%m-%d'),
        "total_transaction_value": round(total_transaction_value, 2),
        "trucks": []
    }

    for truck in transactions_per_truck:
        truck_id, truck_name, num_transactions, total_value, cash_transactions, card_transactions = truck
        total_transactions = round(cash_transactions + card_transactions, 2)
        avg_transaction = round(total_value / num_transactions, 2)
        cash_percentage = round((cash_transactions / total_transactions)
                                * 100, 2) if total_transactions > 0 else 0.00
        card_percentage = round((card_transactions / total_transactions)
                                * 100, 2) if total_transactions > 0 else 0.00
        summary_data["trucks"].append({
            "truck_id": truck_id,
            "truck_name": truck_name,
            "num_transactions": num_transactions,
            "total_transaction_value": round(total_value, 2),
            "cash_transactions": cash_percentage,
            "card_transactions": card_percentage,
            "Average_transaction": avg_transaction
        })

    return summary_data


def convert_to_html(data) -> str:
    """Creates a HTML table for the data"""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Transaction Summary</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333;
                margin: 20px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{
                color: #5b5b5b;
                text-align: center;
            }}
            .summary {{
                background-color: #f9f9f9;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            .summary p {{
                margin: 5px 0;
                font-size: 1.1em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            table, th, td {{
                border: 1px solid #ddd;
            }}
            th, td {{
                padding: 10px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Daily Transaction Report</h1>

            <div class="summary">
                <p><strong>Date:</strong> {data['date']}</p>
                <p><strong>Total Transaction Value:</strong> £{data['total_transaction_value']}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Truck ID</th>
                        <th>Truck Name</th>
                        <th>Number of Transactions</th>
                        <th>Total Transaction Value (£)</th>
                        <th>Cash Transactions (%)</th>
                        <th>Card Transactions (%)</th>
                        <th>Average Transaction Value (£)</th>
                    </tr>
                </thead>
                <tbody>
    """

    for truck in data['trucks']:
        html += f"""
            <tr>
                <td>{truck['truck_id']}</td>
                <td>{truck['truck_name']}</td>
                <td>{truck['num_transactions']}</td>
                <td>{truck['total_transaction_value']}</td>
                <td>{truck['cash_transactions']}</td>
                <td>{truck['card_transactions']}</td>
                <td>{truck['Average_transaction']}</td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    return html


def main():
    """Calls all functions in the correct order"""
    conn = get_connection()
    cursor = get_cursor(conn)

    try:
        data = load_data(cursor)
    except Exception as e:
        print("Error getting data")
        print(e)
        return

    save_to_json(data)
    html_content = convert_to_html(data)

    with open("html_eg.html", 'w') as f:
        f.write(html_content)


if __name__ == "__main__":
    main()
