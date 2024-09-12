import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

connection=None

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

load_dotenv()
def connect_to_database():
    global connection
    if connection is None or not connection.is_connected():
        try:
            connection = mysql.connector.connect(
                host='34.205.204.68',  
                database='INST126_BOT_LOGS',
                user='joel',
                password='oasislab@123O'
            )
            if connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    return connection

# Function to log data to the database
def log_to_database(log_data: dict):
    try:
        connection = connect_to_database()
        if connection is None:
            return

        cursor = connection.cursor()
        query = """
        INSERT INTO bot_logs (id,discord_handle, user_query, bot_response, timestamp, message_type, image_url, thread_id, user_id, message_id,server_name)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        values = (
            log_data['id'],
            log_data["discord_handle"],
            log_data["user_query"],
            log_data["bot_response"],
            log_data["timestamp"],
            log_data["message_type"],
            log_data["image_url"],
            log_data["thread_id"],
            log_data["user_id"],
            log_data["message_id"],
            log_data["server_name"]
        )
        cursor.execute(query, values)
        connection.commit()
        print("Log inserted into MySQL database.")
    except Error as e:
        print(f"Error inserting into MySQL: {e}")
    finally:
        if cursor:
            cursor.close()

# Function to close the database connection
def close_database_connection():
    global connection
    if connection and connection.is_connected():
        connection.close()
        connection = None
        print("MySQL connection closed.")