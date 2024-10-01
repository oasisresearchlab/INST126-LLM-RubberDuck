import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os
import csv
from dotenv import load_dotenv



load_dotenv()
logging.basicConfig(
    filename='bot.log', 
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/umeshchandra/Downloads/inst126-discord-bot-8283627ced30.json', scope)
client = gspread.authorize(creds)

spreadsheet = client.open("INST126_DISCORD_BOT_LOGS")
worksheet = spreadsheet.sheet1

def get_column_index(column_name):
    try:
        return worksheet.row_values(1).index(column_name) + 1
    except ValueError:
        raise Exception(f"Column '{column_name}' not found in the sheet.")

def log_to_google_sheets(log_data: dict):
    try:
        row = [''] * len(worksheet.row_values(1))
        for key, value in log_data.items():
            col_index = get_column_index(key)
            row[col_index - 1] = value

        # Append the row to the worksheet
        worksheet.append_row(row)
        print("Logged to Google Sheets successfully.")
    except Exception as e:
        print(f"Failed to log to Google Sheets: {e}")


def log_to_csv(log_data: dict):
    try:
        # Define the log file path (same directory as the script)
        log_file_path = os.path.join(os.path.dirname(__file__), 'bot_logs.csv')
        
        # Check if the log file already exists
        file_exists = os.path.isfile(log_file_path)
        
        with open(log_file_path, 'a', newline='') as csvfile:
            fieldnames = [
                "ID", "Discord Handle", "User Query", "Bot Response", "Time Stamp", 
                "Message Type", "Image URL", "Thread ID", "User Id", "Message Id","Server Name"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header only if the file doesn't already exist
            if not file_exists:
                writer.writeheader()
            
            # Write the log data as a new row
            writer.writerow(log_data)
        
        print("Logged to CSV file successfully.")
    except Exception as e:
        print(f"Failed to log to CSV file: {e}")
