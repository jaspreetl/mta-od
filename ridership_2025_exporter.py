import pandas as pd
import duckdb
from datetime import datetime
import time

export_log = "export-log.txt"
api_base = "https://data.ny.gov/resource/5wq4-mkjj.csv"
db_file = "HourlyRidership2025.db"

limit = 1_000_000
offset = 0

# Function to log messages
def log_message(message: str) -> None:
    """Log messages with timestamp."""
    with open(export_log, 'a') as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{message}\n")

with duckdb.connect(db_file) as con:
    
    while True:
        
        api_path = f"{api_base}?$limit={limit}&$offset={offset}&$order=:id"
        log_message(f"Fetching data from: {api_path}")
        
        try:
            df = pd.read_csv(api_path, low_memory=False)

            rows = df.shape[0]
            
            if offset == 0:
                # Create the table if it's the first chunk
                con.execute("CREATE TABLE ridership AS SELECT * FROM df")
            else:
                # Insert data into the existing table
                con.execute("INSERT INTO ridership SELECT * FROM df")

            if rows < limit:
                # If fewer rows than limit, we are done
                log_message("Finished processing all data.")
                break

            # Update offset for the next batch
            offset += limit

            # Sleep to avoid hitting rate limits
            time.sleep(10)
            
        except Exception as e:
            log_message(f"Error reading data: {e}")
            break
con.close()
