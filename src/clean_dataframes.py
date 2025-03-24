import pandas as pd
import os

def clean_dataframes(file_location, time_columns=None, sep=";" ):
    # Load dataset
    data = pd.read_csv(file_location, delimiter=sep, low_memory=False)

    # Detect datetime columns if not provided
    if time_columns is None:
        time_columns = [col for col in data.columns if "date" in col.lower() or "time" in col.lower()]

    # Convert datetime columns
    for col in time_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")

    # Display missing datetime values before cleaning
    missing_timestamps = data[time_columns].isna().sum()
    print(f"Missing datetime values before processing:\n{missing_timestamps}")

    # Drop rows only if all datetime columns are NaN
    if time_columns:
        data = data.dropna(subset=time_columns, how="all")

    # Warn if dataset becomes empty
    if data.empty:
        print(f"Warning: Processed dataset is empty after handling {file_location}.")

    # Sort dataset by first valid datetime column
    if time_columns and not data.empty:
        data = data.sort_values(by=time_columns[0]).reset_index(drop=True)

    return data

# Define directory paths
raw_data_dir = "data/raw_files"
processed_data_dir = "data/cleaned_files"
os.makedirs(processed_data_dir, exist_ok=True)

# Process all CSV files
for filename in os.listdir(raw_data_dir):
    if filename.endswith(".csv"):
        raw_file_path = os.path.join(raw_data_dir, filename)
        print(f"Cleaning {filename}...")

        # Clean and save
        processed_df = clean_dataframes(raw_file_path)
        
        if not processed_df.empty:
            processed_file_path = os.path.join(processed_data_dir, f"cleaned_{filename}")
            processed_df.to_csv(processed_file_path, index=False, sep=",")
            print(f"Saved cleaned file: {processed_file_path}")
        else:
            print(f"Skipped saving {filename} due to empty cleaned data.")

print("All datasets cleaned and saved successfully.")
