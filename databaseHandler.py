import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

connection=None

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

USER_LIST = [
    'Elias Gonzalez', 
    'Dr. Chan (Instructor)', 
    'Umesh (Grader)', 
    'Introduction to programming', 
    'Umesh'
]

def get_discord_handle(user: str) -> str:
    if user in USER_LIST:
        return user
    return ""

def redact_name_in_bot_response(discord_handle,bot_response):
    if discord_handle in bot_response:
        bot_response=bot_response.replace(discord_handle,"[redacted_name]")
    return bot_response



load_dotenv()
def connect_to_database():
    global connection
    if connection is None or not connection.is_connected():
        try:
            connection = mysql.connector.connect(
                host=MYSQL_HOST,  
                database=MYSQL_DATABASE,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD
            )
            if connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    return connection

def contains_code(bot_response):
    if "```" in bot_response:
        return True
    return False

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

        #Here add more code to insert data into annonymized_code_logs
        query = """
        INSERT INTO anonymized_bot_logs (id, user_query, bot_response, timestamp, message_type, image_url, thread_id, user_id, message_id,server_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """

        #Remove name in bot_response.
        bot_response_with_redacted_name=redact_name_in_bot_response(log_data["discord_handle"],log_data["bot_response"])

        values = (
            log_data['id'],
            log_data["user_query"],
            bot_response_with_redacted_name,
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
        print("Log inserted into MySQL database in anonymized_bot_logs.")

        if contains_code(log_data["bot_response"]):
            code_query = """
        INSERT INTO bot_code_logs (id,discord_handle, user_query, bot_response, timestamp, message_type, image_url, thread_id, user_id, message_id,server_name)
        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
            code_values = (
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
            cursor.execute(code_query, code_values)
            connection.commit()
            print("Code log inserted into bot_code_logs.")
            code_query = """
        INSERT INTO anonymized_bot_code_logs (id, user_query, bot_response, timestamp, message_type, image_url, thread_id, user_id, message_id,server_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
            code_values = (
            log_data['id'],
            log_data["user_query"],
            bot_response_with_redacted_name,
            log_data["timestamp"],
            log_data["message_type"],
            log_data["image_url"],
            log_data["thread_id"],
            log_data["user_id"],
            log_data["message_id"],
            log_data["server_name"]
        )
            cursor.execute(code_query, code_values)
            connection.commit()
            print("Code log inserted into annonymized_bot_code_logs.")
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