import mysql.connector
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
from driveHandler import upload_to_drive

load_dotenv()

# Function to export logs from any table
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')

def export_logs_to_csv(table_name):
    connection = mysql.connector.connect(
        host="34.205.204.68",
        database=MYSQL_DATABASE,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    
    filename = f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([i[0] for i in cursor.description]) 
        csv_writer.writerows(cursor.fetchall())
    cursor.close()
    connection.close()
    return filename

# Function to export both tables
def export_multiple_tables():
    logs_filename = export_logs_to_csv('anonymized_bot_logs')
    code_logs_filename = export_logs_to_csv('anonymized_bot_code_logs')
    return logs_filename, code_logs_filename

def export_and_upload_logs():
    # Export logs from both tables
    logs_filename, code_logs_filename = export_multiple_tables()
    print("fetched the csv files")
    
    # Upload both files to Google Drive
    upload_to_drive(logs_filename, code_logs_filename)

    # After upload, delete the local files
    try:
        if os.path.exists(logs_filename):
            os.remove(logs_filename)
            print(f"Deleted local file: {logs_filename}")
        if os.path.exists(code_logs_filename):
            os.remove(code_logs_filename)
            print(f"Deleted local file: {code_logs_filename}")
    except Exception as e:
        print(f"Error deleting files: {e}")

if __name__=="__main__":
    export_and_upload_logs()
