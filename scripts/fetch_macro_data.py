#!/usr/bin/env python3
"""
Fetch macroeconomic data (CPI, PMI, Interest Rates) from FRED
Using direct CSV download URLs
"""

import pandas as pd
import requests
from datetime import datetime
import os

# FRED series IDs for macroeconomic indicators
FRED_SERIES = {
    # CPI Data
    'CPIAUCSL': 'CPI All Urban Consumers (Seasonally Adjusted)',
    'CPILFESL': 'Core CPI (Less Food and Energy)',
    
    # Interest Rates
    'FEDFUNDS': 'Federal Funds Effective Rate',
    'DGS10': '10-Year Treasury Constant Maturity Rate',
    'DGS2': '2-Year Treasury Constant Maturity Rate',
    'DGS30': '30-Year Treasury Constant Maturity Rate',
    'MORTGAGE30US': '30-Year Fixed Rate Mortgage Average',
    
    # PMI Data (ISM Manufacturing)
    'MANEMP': 'Manufacturing Employment',
    'NAPM': 'ISM Manufacturing: PMI Composite Index',
    'NAPMNOI': 'ISM Manufacturing: New Orders Index',
    'NAPMPI': 'ISM Manufacturing: Production Index',
    
    # Additional Economic Indicators
    'UNRATE': 'Unemployment Rate',
    'GDPC1': 'Real GDP',
    'PCEPI': 'PCE Price Index',
    'T10Y2Y': '10-Year Treasury Minus 2-Year Treasury (Yield Curve)',
}

def download_fred_series(series_id, start_date='2020-01-01'):
    """
    Download FRED series data using direct CSV URL
    """
    # FRED CSV download URL format
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start_date}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Save to temp file and read
            temp_file = f'/tmp/{series_id}.csv'
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            df = pd.read_csv(temp_file)
            df.columns = ['Date', series_id]
            
            # Clean data - remove periods with missing data (marked as '.')
            df = df[df[series_id] != '.']
            df[series_id] = pd.to_numeric(df[series_id], errors='coerce')
            
            os.remove(temp_file)
            return df
        else:
            print(f"  Failed to download {series_id}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  Error downloading {series_id}: {str(e)}")
        return None

def main():
    print("Fetching macroeconomic data from FRED (2020-present)")
    print("=" * 70)
    
    all_data = {}
    
    for series_id, description in FRED_SERIES.items():
        print(f"Downloading {description} ({series_id})...")
        df = download_fred_series(series_id)
        if df is not None:
            all_data[series_id] = df
            print(f"  Retrieved {len(df)} data points")
        else:
            print(f"  Failed to retrieve data")
    
    # Merge all data into single DataFrame
    if all_data:
        print("\n" + "=" * 70)
        print("Merging data...")
        
        # Start with first series
        merged_df = None
        for series_id, df in all_data.items():
            if merged_df is None:
                merged_df = df
            else:
                merged_df = pd.merge(merged_df, df, on='Date', how='outer')
        
        # Sort by date
        merged_df['Date'] = pd.to_datetime(merged_df['Date'])
        merged_df = merged_df.sort_values('Date')
        merged_df['Date'] = merged_df['Date'].dt.strftime('%Y-%m-%d')
        
        # Save merged data
        merged_df.to_csv('/home/ubuntu/market_data_2020_2025/macro_data_all.csv', index=False)
        print(f"Saved merged data to macro_data_all.csv ({len(merged_df)} rows)")
        
        # Create separate files for each category
        
        # CPI Data
        cpi_cols = ['Date'] + [c for c in ['CPIAUCSL', 'CPILFESL', 'PCEPI'] if c in merged_df.columns]
        cpi_df = merged_df[cpi_cols].dropna(subset=cpi_cols[1:], how='all')
        cpi_df.to_csv('/home/ubuntu/market_data_2020_2025/cpi_data.csv', index=False)
        print(f"Saved CPI data to cpi_data.csv ({len(cpi_df)} rows)")
        
        # Interest Rate Data
        rate_cols = ['Date'] + [c for c in ['FEDFUNDS', 'DGS2', 'DGS10', 'DGS30', 'MORTGAGE30US', 'T10Y2Y'] if c in merged_df.columns]
        rate_df = merged_df[rate_cols].dropna(subset=rate_cols[1:], how='all')
        rate_df.to_csv('/home/ubuntu/market_data_2020_2025/interest_rate_data.csv', index=False)
        print(f"Saved interest rate data to interest_rate_data.csv ({len(rate_df)} rows)")
        
        # PMI Data
        pmi_cols = ['Date'] + [c for c in ['NAPM', 'NAPMNOI', 'NAPMPI', 'MANEMP'] if c in merged_df.columns]
        pmi_df = merged_df[pmi_cols].dropna(subset=pmi_cols[1:], how='all')
        pmi_df.to_csv('/home/ubuntu/market_data_2020_2025/pmi_data.csv', index=False)
        print(f"Saved PMI data to pmi_data.csv ({len(pmi_df)} rows)")
        
        # Print summary statistics
        print("\n" + "=" * 70)
        print("Summary Statistics:")
        print("=" * 70)
        
        for series_id, description in FRED_SERIES.items():
            if series_id in merged_df.columns:
                series_data = merged_df[series_id].dropna()
                if len(series_data) > 0:
                    print(f"\n{description} ({series_id}):")
                    print(f"  Data points: {len(series_data)}")
                    print(f"  Min: {series_data.min():.2f}")
                    print(f"  Max: {series_data.max():.2f}")
                    print(f"  Latest: {series_data.iloc[-1]:.2f}")
    else:
        print("No data was retrieved")

if __name__ == "__main__":
    main()
