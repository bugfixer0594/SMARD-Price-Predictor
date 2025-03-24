import pandas as pd
import numpy as np
import os

def refine_dataset(file_path):
    # Load data
    df = pd.read_csv(file_path, delimiter=",")

    # Identify numerical and categorical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns

    print(f"Processing {file_path}...")
    print(f"Detected numerical columns: {list(numerical_cols)}")
    print(f"Detected categorical columns: {list(categorical_cols)}")

    # Handle missing values
    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())  # Fill numerical with median

    for col in categorical_cols:
        if not df[col].mode().empty:  # Ensure mode is not empty
            df[col] = df[col].fillna(df[col].mode()[0])  # Fill categorical with mode
        else:
            print(f"Warning: No mode found for {col}, leaving NaN values.")

    # Normalize numerical data (Min-Max Scaling)
    for col in numerical_cols:
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    return df

# Directory paths
source_directory = "data/cleaned_files"
output_directory = "data/refined_files"
os.makedirs(output_directory, exist_ok=True)

# Process each cleaned dataset
for filename in os.listdir(source_directory):
    file_path = os.path.join(source_directory, filename)

    if filename.endswith(".csv"):
        try:
            refined_df = refine_dataset(file_path)
            output_file_path = os.path.join(output_directory, f"refined_{filename}")
            refined_df.to_csv(output_file_path, index=False, sep=",")
            print(f"Saved refined file: {output_file_path}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("All datasets refined and saved successfully.")
