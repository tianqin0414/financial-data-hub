#!/usr/bin/env python3
"""
Fetch commodity futures historical data (Crude Oil, Gold, Copper) from 2020 to present
"""

import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import pandas as pd
from datetime import datetime
import time

def fetch_commodity_data(client, symbol, name, start_timestamp, end_timestamp):
    """
    Fetch historical data for a commodity futures contract
    """
    print(f"Fetching {name} ({symbol}) data...")
    
    try:
        response = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': 'US',
            'interval': '1d',
            'period1': str(start_timestamp),
            'period2': str(end_timestamp),
            'includeAdjustedClose': True
        })
        
        if response and 'chart' in response and 'result' in response['chart']:
            result = response['chart']['result'][0]
            meta = result['meta']
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Create DataFrame
            data = []
            for i in range(len(timestamps)):
                date = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
                data.append({
                    'Date': date,
                    'Open': quotes['open'][i] if quotes['open'][i] else None,
                    'High': quotes['high'][i] if quotes['high'][i] else None,
                    'Low': quotes['low'][i] if quotes['low'][i] else None,
                    'Close': quotes['close'][i] if quotes['close'][i] else None,
                    'Volume': quotes['volume'][i] if quotes['volume'][i] else None
                })
            
            df = pd.DataFrame(data)
            df['Commodity'] = name
            df['Symbol'] = symbol
            
            print(f"  Retrieved {len(df)} data points for {name}")
            print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
            
            return df
        else:
            print(f"  No data found for {name}")
            return None
            
    except Exception as e:
        print(f"  Error fetching {name}: {str(e)}")
        return None

def main():
    client = ApiClient()
    
    # Define time range: 2020-01-01 to now
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    print(f"Fetching commodity futures data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    # Commodity futures symbols
    commodities = [
        ('CL=F', 'Crude Oil (WTI)'),
        ('GC=F', 'Gold'),
        ('HG=F', 'Copper')
    ]
    
    all_data = []
    
    for symbol, name in commodities:
        df = fetch_commodity_data(client, symbol, name, start_timestamp, end_timestamp)
        if df is not None:
            all_data.append(df)
        time.sleep(1)  # Rate limiting
    
    if all_data:
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save combined data
        combined_df.to_csv('/home/ubuntu/market_data_2020_2025/commodity_futures_all.csv', index=False)
        print(f"\nSaved combined data to commodity_futures_all.csv ({len(combined_df)} rows)")
        
        # Save individual commodity files
        for symbol, name in commodities:
            commodity_df = combined_df[combined_df['Symbol'] == symbol]
            if len(commodity_df) > 0:
                filename = f"/home/ubuntu/market_data_2020_2025/{symbol.replace('=F', '').lower()}_futures.csv"
                commodity_df.to_csv(filename, index=False)
                print(f"Saved {name} data to {filename}")
        
        # Create summary statistics
        print("\n" + "=" * 60)
        print("Summary Statistics:")
        print("=" * 60)
        
        for symbol, name in commodities:
            commodity_df = combined_df[combined_df['Symbol'] == symbol]
            if len(commodity_df) > 0:
                print(f"\n{name} ({symbol}):")
                print(f"  Data points: {len(commodity_df)}")
                print(f"  Date range: {commodity_df['Date'].min()} to {commodity_df['Date'].max()}")
                print(f"  Price range: ${commodity_df['Close'].min():.2f} - ${commodity_df['Close'].max():.2f}")
                print(f"  Latest close: ${commodity_df['Close'].iloc[-1]:.2f}")
    else:
        print("No data was retrieved")

if __name__ == "__main__":
    main()
