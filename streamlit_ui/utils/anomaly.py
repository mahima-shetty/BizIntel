# utils/anomaly.py
import pandas as pd
import numpy as np
import json

mock_kpi_history = {
    "AAPL": {
        "2025-07-10": {
            "Market Cap": 3000000000000,
            "PE Ratio": 28.5,
            "EPS": 6.10,
            "Dividend Yield": 0.52,
        },
        "2025-07-11": {
            "Market Cap": 3100000000000,
            "PE Ratio": 30.1,
            "EPS": 6.30,
            "Dividend Yield": 0.51,
        },
        "2025-07-12": {
            "Market Cap": 3050000000000,
            "PE Ratio": 29.8,
            "EPS": 6.25,
            "Dividend Yield": 0.50,
        },
        "2025-07-13": {
            "Market Cap": 3900000000000,  # 👈 Outlier
            "PE Ratio": 90.0,             # 👈 Outlier
            "EPS": 12.0,                  # 👈 Outlier
            "Dividend Yield": 1.2,        # 👈 Outlier
        },
        "2025-07-14": {
            "Market Cap": 3080000000000,
            "PE Ratio": 29.5,
            "EPS": 6.20,
            "Dividend Yield": 0.49,
        }
    }
}


import pandas as pd
import numpy as np

def detect_anomalies_for_ticker(kpi_history: dict) -> dict:
    anomalies = {}

    for ticker, date_data in kpi_history.items():
        df = pd.DataFrame.from_dict(date_data, orient="index")
        df.index.name = "Date"
        df.reset_index(inplace=True)

        # Ensure Date is sorted and metrics are numeric
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values("Date", inplace=True)

        numeric_cols = ['Market Cap', 'PE Ratio', 'EPS', 'Dividend Yield']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

        ticker_anomalies = {}

        for col in numeric_cols:
            clean_df = df[['Date', col]].dropna()
            if len(clean_df) < 4:
                print(f"⚠️ Not enough data points for {ticker} - {col}")
                continue

            mean = clean_df[col].mean()
            std = clean_df[col].std()
            if std == 0 or pd.isna(std):
                continue

            clean_df["z_score"] = (clean_df[col] - mean) / std
            outliers = clean_df[clean_df["z_score"].abs() > 1.5]

            if not outliers.empty:
                records = outliers[['Date', col]].copy()
                records["Date"] = records["Date"].astype(str)  # 👈 Convert Timestamp to str
                ticker_anomalies[col] = records.to_dict(orient="records")



        if ticker_anomalies:
            anomalies[ticker] = ticker_anomalies

    print("✅ Final anomalies dict:")
    print(json.dumps(anomalies, indent=2, default=str))  # for datetime-safe printing
    return anomalies

