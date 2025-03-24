# import pandas as pd
# import numpy as np
# import os

# # =========================
# # Define Paths
# # =========================
# INPUT_DIR = "data/refined_files"
# OUTPUT_DIR = "data/finalized_files"
# VISUALS_DIR = "visuals"
# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(VISUALS_DIR, exist_ok=True)

# # =========================
# # Load Processed Data
# # =========================
# data_files = {
#     "market_price": "refined_cleaned_Day-ahead_prices_202301010000_202503050000_Hour.csv",
#     "actual_demand": "refined_cleaned_Actual_consumption_202301010000_202503050000_Quarterhour.csv",
#     "forecast_demand": "refined_cleaned_Forecasted_consumption_202301010000_202503050000_Quarterhour.csv",
#     "actual_supply": "refined_cleaned_Actual_generation_202301010000_202503050000_Quarterhour.csv",
#     "forecast_supply": "refined_cleaned_Forecasted_generation_Day-Ahead_202301010000_202503050000_Hour_Quarterhour.csv",
#     "grid_flows": "refined_cleaned_Cross-border_physical_flows_202301010000_202503050000_Quarterhour.csv",
#     "scheduled_trades": "refined_cleaned_Scheduled_commercial_exchanges_202301010000_202503050000_Quarterhour.csv",
# }

# # Load datasets
# df_price = pd.read_csv(os.path.join(INPUT_DIR, data_files["market_price"]), delimiter=",", low_memory=False)
# df_actual_demand = pd.read_csv(os.path.join(INPUT_DIR, data_files["actual_demand"]), delimiter=",", low_memory=False)
# df_forecast_demand = pd.read_csv(os.path.join(INPUT_DIR, data_files["forecast_demand"]), delimiter=",", low_memory=False)
# df_actual_supply = pd.read_csv(os.path.join(INPUT_DIR, data_files["actual_supply"]), delimiter=",", low_memory=False)
# df_forecast_supply = pd.read_csv(os.path.join(INPUT_DIR, data_files["forecast_supply"]), delimiter=",", low_memory=False)
# df_grid_flows = pd.read_csv(os.path.join(INPUT_DIR, data_files["grid_flows"]), delimiter=",", low_memory=False)
# df_scheduled_trades = pd.read_csv(os.path.join(INPUT_DIR, data_files["scheduled_trades"]), delimiter=",", low_memory=False)

# # =========================
# # Clean Column Names
# # =========================
# for df in [df_price, df_actual_demand, df_forecast_demand, df_actual_supply, df_forecast_supply, df_grid_flows, df_scheduled_trades]:
#     df.columns = df.columns.str.strip()
#     df.columns = df.columns.str.replace(r"[^\x00-\x7F]+", "", regex=True)

# # =========================
# # Convert "-" to NaN and Ensure Numeric Columns
# # =========================
# for df in [df_price, df_actual_demand, df_forecast_demand, df_actual_supply, df_forecast_supply, df_grid_flows, df_scheduled_trades]:
#     df.replace("-", np.nan, inplace=True)
#     df.infer_objects(copy=False)
    
#     for col in df.columns:
#         if col != "Start date":
#             df[col] = pd.to_numeric(df[col], errors="coerce")

# # =========================
# # Compute Market Average Price
# # =========================
# price_columns = [col for col in df_price.columns if "MWh" in col]

# if not price_columns:
#     raise KeyError("No valid price columns found for market data.")

# df_price["Market_Average_Price"] = df_price[price_columns].mean(axis=1)

# # =========================
# # Drop Redundant Columns Before Merge
# # =========================
# for df in [df_actual_demand, df_forecast_demand, df_actual_supply, df_forecast_supply, df_grid_flows, df_scheduled_trades]:
#     df.drop(columns=["End Timestamp"], errors="ignore", inplace=True)

# # =========================
# # Convert Time Columns
# # =========================
# for df in [df_price, df_actual_demand, df_forecast_demand, df_actual_supply, df_forecast_supply, df_grid_flows, df_scheduled_trades]:
#     df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

# # =========================
# # Merge Data with Unique Suffixes
# # =========================
# df_combined = df_price \
#     .merge(df_actual_demand, on="Timestamp", how="inner", suffixes=("", "_demand")) \
#     .merge(df_forecast_demand, on="Timestamp", how="inner", suffixes=("", "_forecast_demand")) \
#     .merge(df_actual_supply, on="Timestamp", how="inner", suffixes=("", "_supply")) \
#     .merge(df_forecast_supply, on="Timestamp", how="inner", suffixes=("", "_forecast_supply")) \
#     .merge(df_grid_flows, on="Timestamp", how="inner", suffixes=("", "_grid")) \
#     .merge(df_scheduled_trades, on="Timestamp", how="inner", suffixes=("", "_scheduled"))

# df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]

# # =========================
# # Compute Forecast Supply Total
# # =========================
# forecast_supply_columns = [col for col in df_combined.columns if "forecast_supply" in col]

# if not forecast_supply_columns:
#     raise KeyError("No forecast supply columns found in dataset.")

# df_combined["Total_Forecast_Supply"] = df_combined[forecast_supply_columns].sum(axis=1)

# # Compute Supply Imbalance
# if "Total_Supply_Recorded" in df_combined.columns:
#     df_combined["Supply_Imbalance"] = df_combined["Total_Supply_Recorded"] - df_combined["Total_Forecast_Supply"]
# else:
#     raise KeyError("Total_Supply_Recorded column missing in dataset.")

# # =========================
# # Handle Missing Values
# # =========================
# df_combined.fillna(df_combined.median(), inplace=True)

# # =========================
# # Feature Engineering
# # =========================
# df_combined["Rolling_Avg_24h"] = df_combined["Market_Average_Price"].rolling(window=24, min_periods=1).mean()
# df_combined["Rolling_Avg_7d"] = df_combined["Market_Average_Price"].rolling(window=24 * 7, min_periods=1).mean()
# df_combined["Price_Change_1h"] = df_combined["Market_Average_Price"].pct_change() * 100
# df_combined["Price_Change_24h"] = df_combined["Market_Average_Price"].pct_change(24) * 100

# df_combined.set_index("Timestamp", inplace=True)

# # =========================
# # Aggregate Data by Timeframe
# # =========================
# df_hourly = df_combined.resample("H").mean()
# df_daily = df_combined.resample("D").mean()
# df_weekly = df_combined.resample("W").mean()

# # =========================
# # Save Processed Data
# # =========================
# df_hourly.to_csv(os.path.join(OUTPUT_DIR, "final_hourly_data.csv"), sep=",")
# df_daily.to_csv(os.path.join(OUTPUT_DIR, "final_daily_data.csv"), sep=",")
# df_weekly.to_csv(os.path.join(OUTPUT_DIR, "final_weekly_data.csv"), sep=",")

# print("Data processing completed successfully.")

import pandas as pd
import numpy as np
import os

# =========================
# 📌 Define Paths
# =========================
DATA_DIR = "data/refined_files"
OUTPUT_DIR = "data/finalized_files"
PLOTS_DIR = "plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# =========================
# 📌 Load Preprocessed Data
# =========================
files = {
    "market_price": "refined_cleaned_Day-ahead_prices_202301010000_202503050000_Hour.csv",
    "actual_demand": "refined_cleaned_Actual_consumption_202301010000_202503050000_Quarterhour.csv",
    "forecast_demand": "refined_cleaned_Forecasted_consumption_202301010000_202503050000_Quarterhour.csv",
    "actual_supply": "refined_cleaned_Actual_generation_202301010000_202503050000_Quarterhour.csv",
    "forecast_supply": "refined_cleaned_Forecasted_generation_Day-Ahead_202301010000_202503050000_Hour_Quarterhour.csv",
    "grid_flows": "refined_cleaned_Cross-border_physical_flows_202301010000_202503050000_Quarterhour.csv",
    "scheduled_trades": "refined_cleaned_Scheduled_commercial_exchanges_202301010000_202503050000_Quarterhour.csv",
}

# Load datasets
df_price = pd.read_csv(os.path.join(DATA_DIR, files["market_price"]), delimiter=",", low_memory=False)
df_actual_consumption = pd.read_csv(os.path.join(DATA_DIR, files["actual_demand"]), delimiter=",", low_memory=False)
df_forecast_consumption = pd.read_csv(os.path.join(DATA_DIR, files["forecast_demand"]), delimiter=",", low_memory=False)
df_actual_generation = pd.read_csv(os.path.join(DATA_DIR, files["actual_supply"]), delimiter=",", low_memory=False)
df_forecast_generation = pd.read_csv(os.path.join(DATA_DIR, files["forecast_supply"]), delimiter=",", low_memory=False)
df_cross_border_flows = pd.read_csv(os.path.join(DATA_DIR, files["grid_flows"]), delimiter=",", low_memory=False)
df_scheduled_exchanges = pd.read_csv(os.path.join(DATA_DIR, files["scheduled_trades"]), delimiter=",", low_memory=False)

# =========================
# 📌 Fix Column Names (Strip Spaces & Special Characters)
# =========================
for df in [df_price, df_actual_consumption, df_forecast_consumption, df_actual_generation, 
           df_forecast_generation, df_cross_border_flows, df_scheduled_exchanges]:
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    df.columns = df.columns.str.replace(r"[^\x00-\x7F]+", "", regex=True)  # Remove non-ASCII chars

# =========================
# 📌 Convert "-" to NaN and Ensure Numeric Columns
# =========================
for df in [df_price, df_actual_consumption, df_forecast_consumption, df_actual_generation, 
           df_forecast_generation, df_cross_border_flows, df_scheduled_exchanges]:
    df.replace("-", np.nan, inplace=True)  # Convert "-" to NaN
    df.infer_objects(copy=False)  # Retain old behavior

    # Convert all columns (except "Start date") to numeric
    for col in df.columns:
        if col != "Start date":  
            df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 📌 Fix Average Price Calculation
# =========================
price_columns = [col for col in df_price.columns if "/MWh" in col]

if not price_columns:
    raise KeyError("⚠ No columns with '/MWh' found for price data!")

df_price["Average_Price_€/MWh"] = df_price[price_columns].mean(axis=1)

# =========================
# 📌 Drop Duplicate Columns Before Merge
# =========================
for df in [df_actual_consumption, df_forecast_consumption, df_actual_generation, 
           df_forecast_generation, df_cross_border_flows, df_scheduled_exchanges]:
    df.drop(columns=["End date"], errors="ignore", inplace=True)

# =========================
# 📌 Convert Time Columns
# =========================
for df in [df_price, df_actual_consumption, df_forecast_consumption, df_actual_generation, 
           df_forecast_generation, df_cross_border_flows, df_scheduled_exchanges]:
    df["Start date"] = pd.to_datetime(df["Start date"], errors="coerce")

# =========================
# 📌 Merge Datasets with Unique Suffixes
# =========================
df = df_price \
    .merge(df_actual_consumption, on="Start date", how="inner", suffixes=("", "_consumption")) \
    .merge(df_forecast_consumption, on="Start date", how="inner", suffixes=("", "_forecast_consumption")) \
    .merge(df_actual_generation, on="Start date", how="inner", suffixes=("", "_generation")) \
    .merge(df_forecast_generation, on="Start date", how="inner", suffixes=("", "_forecast_generation")) \
    .merge(df_cross_border_flows, on="Start date", how="inner", suffixes=("", "_cross_border")) \
    .merge(df_scheduled_exchanges, on="Start date", how="inner", suffixes=("", "_scheduled_exchanges"))

# Ensure unique column names
df = df.loc[:, ~df.columns.duplicated()]

# =========================
# 📌 Compute 'Total Forecast Generation' Dynamically
# =========================
forecast_gen_cols = [col for col in df.columns if "forecast_generation" in col]

if not forecast_gen_cols:
    raise KeyError("⚠ No forecast generation columns found in dataset!")

df["Total_Forecast_Generation"] = df[forecast_gen_cols].sum(axis=1)

# ✅ Compute Generation Imbalance
if "Total [MWh] Original resolutions" in df.columns:
    df["Generation_Imbalance"] = df["Total [MWh] Original resolutions"] - df["Total_Forecast_Generation"]
else:
    raise KeyError("⚠ 'Total [MWh] Original resolutions' column not found in dataset!")

# =========================
# 📌 Handle Missing Values
# =========================
df.fillna(df.median(), inplace=True)  # Fill missing values with column medians

# 📌 Recompute `Average_Price_€/MWh` After Merging (Ensure It Exists)
# =========================
df["Average_Price_€/MWh"] = df[price_columns].mean(axis=1)

# =========================
# 📌 Feature Engineering
# =========================
df["Rolling_Mean_24h"] = df["Average_Price_€/MWh"].rolling(window=24, min_periods=1).mean()
df["Rolling_Mean_7d"] = df["Average_Price_€/MWh"].rolling(window=24 * 7, min_periods=1).mean()
df["Price_Diff"] = df["Average_Price_€/MWh"].diff()
df["Lag_1h"] = df["Average_Price_€/MWh"].shift(1)
df["Lag_24h"] = df["Average_Price_€/MWh"].shift(24)
df["Volatility_24h"] = df["Average_Price_€/MWh"].rolling(window=24, min_periods=1).std()
df["Price_Change_1h"] = df["Average_Price_€/MWh"].pct_change() * 100
df["Price_Change_24h"] = df["Average_Price_€/MWh"].pct_change(24) * 100

# Compute imbalance between actual and forecast values
if "Total (grid load) [MWh] Original resolutions" in df.columns and "Total (grid load) [MWh] Original resolutions_forecast_consumption" in df.columns:
    df["Consumption_Imbalance"] = df["Total (grid load) [MWh] Original resolutions"] - df["Total (grid load) [MWh] Original resolutions_forecast_consumption"]

# =========================
# 📌 Aggregate Data to Different Timeframes
# =========================
df.set_index("Start date", inplace=True)
df_hourly = df.resample("H").mean()
df_daily = df.resample("D").mean()
df_weekly = df.resample("W").mean()

# =========================
# 📌 Save Processed Data
# =========================
df_hourly.to_csv(os.path.join(OUTPUT_DIR, "final_hourly_data.csv"), sep=",")
df_daily.to_csv(os.path.join(OUTPUT_DIR, "final_daily_data.csv"), sep=",")
df_weekly.to_csv(os.path.join(OUTPUT_DIR, "final_weekly_data.csv"), sep=",")

print("✅ Data finalization completed successfully!")
