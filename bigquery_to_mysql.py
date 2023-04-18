import mysql.connector
from google.cloud import bigquery
from google.oauth2 import service_account
from config import GOOGLE_APPLICATION_CREDENTIALS, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def bigquery_to_mysql():
    # Set up BigQuery client

    # Create credentials using the service account key JSON file
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)

    # Create a BigQuery client using the service account credentials
    bigquery_client = bigquery.Client(credentials=credentials)

    #bigquery_client = bigquery.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

    # Define your BigQuery SQL query here
    query = "SELECT * FROM `annular-moon-361814.Quests.ALL_quests` limit 1"

    # Run the BigQuery query
    query_job = bigquery_client.query(query)
    results = query_job.result()
    print(results)

    # Set up MySQL connection
#     mysql_conn = mysql.connector.connect(
#         host=MYSQL_HOST,
#         user=MYSQL_USER,
#         password=MYSQL_PASSWORD,
#         database=MYSQL_DATABASE
#     )
#     mysql_cursor = mysql_conn.cursor()
#
#     # Insert BigQuery data into MySQL table
#     for row in results:
#         # Customize the INSERT statement based on your table structure
#         insert_query = f"INSERT INTO your_mysql_table (column1, column2) VALUES ({row.column1}, {row.column2})"
#         mysql_cursor.execute(insert_query)
#
#     # Commit and close the MySQL connection
#     mysql_conn.commit()
#     mysql_cursor.close()
#     mysql_conn.close()

if __name__ == "__main__":
    bigquery_to_mysql()
