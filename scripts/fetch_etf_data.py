#!/usr/bin/env python3
"""
Fetch ETF historical data (price and volume) from 2020 to present
Using volume and price changes as proxy for fund flow analysis
"""

import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import pandas as pd
from datetime import datetime
import time

def fetch_etf_data(client, symbol, name, start_timestamp, end_timestamp):
    """
    Fetch historical data for an ETF
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
                close = quotes['close'][i] if quotes['close'][i] else None
                volume = quotes['volume'][i] if quotes['volume'][i] else None
                
                data.append({
                    'Date': date,
                    'Open': quotes['open'][i] if quotes['open'][i] else None,
                    'High': quotes['high'][i] if quotes['high'][i] else None,
                    'Low': quotes['low'][i] if quotes['low'][i] else None,
                    'Close': close,
                    'Volume': volume
                })
            
            df = pd.DataFrame(data)
            df['ETF_Name'] = name
            df['Symbol'] = symbol
            
            # Calculate daily dollar volume (proxy for fund flow)
            df['Dollar_Volume'] = df['Close'] * df['Volume']
            
            # Calculate price change
            df['Price_Change'] = df['Close'].pct_change() * 100
            
            # Calculate volume change
            df['Volume_Change'] = df['Volume'].pct_change() * 100
            
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
    
    print(f"Fetching ETF data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 70)
    
    # Major ETFs covering different asset classes and sectors
    etfs = [
        # Major Index ETFs
        ('SPY', 'SPDR S&P 500 ETF'),
        ('QQQ', 'Invesco QQQ Trust (NASDAQ-100)'),
        ('IWM', 'iShares Russell 2000 ETF'),
        ('DIA', 'SPDR Dow Jones Industrial Average ETF'),
        
        # Sector ETFs
        ('XLF', 'Financial Select Sector SPDR'),
        ('XLK', 'Technology Select Sector SPDR'),
        ('XLE', 'Energy Select Sector SPDR'),
        ('XLV', 'Health Care Select Sector SPDR'),
        ('XLI', 'Industrial Select Sector SPDR'),
        ('XLU', 'Utilities Select Sector SPDR'),
        ('XLP', 'Consumer Staples Select Sector SPDR'),
        ('XLY', 'Consumer Discretionary Select Sector SPDR'),
        ('XLB', 'Materials Select Sector SPDR'),
        ('XLRE', 'Real Estate Select Sector SPDR'),
        
        # Bond ETFs
        ('TLT', 'iShares 20+ Year Treasury Bond ETF'),
        ('IEF', 'iShares 7-10 Year Treasury Bond ETF'),
        ('LQD', 'iShares iBoxx Investment Grade Corporate Bond ETF'),
        ('HYG', 'iShares iBoxx High Yield Corporate Bond ETF'),
        ('AGG', 'iShares Core U.S. Aggregate Bond ETF'),
        
        # Commodity ETFs
        ('GLD', 'SPDR Gold Shares'),
        ('SLV', 'iShares Silver Trust'),
        ('USO', 'United States Oil Fund'),
        
        # International ETFs
        ('EEM', 'iShares MSCI Emerging Markets ETF'),
        ('EFA', 'iShares MSCI EAFE ETF'),
        ('VWO', 'Vanguard FTSE Emerging Markets ETF'),
        ('FXI', 'iShares China Large-Cap ETF'),
        
        # Volatility ETFs
        ('VXX', 'iPath Series B S&P 500 VIX Short-Term Futures ETN'),
    ]
    
    all_data = []
    
    for symbol, name in etfs:
        df = fetch_etf_data(client, symbol, name, start_timestamp, end_timestamp)
        if df is not None:
            all_data.append(df)
        time.sleep(0.5)  # Rate limiting
    
    if all_data:
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save combined data
        combined_df.to_csv('/home/ubuntu/market_data_2020_2025/etf_data_all.csv', index=False)
        print(f"\nSaved combined data to etf_data_all.csv ({len(combined_df)} rows)")
        
        # Create pivot table for fund flow analysis (dollar volume by date and ETF)
        pivot_df = combined_df.pivot_table(
            index='Date', 
            columns='Symbol', 
            values=['Close', 'Volume', 'Dollar_Volume'],
            aggfunc='first'
        )
        pivot_df.columns = ['_'.join(col).strip() for col in pivot_df.columns.values]
        pivot_df.reset_index(inplace=True)
        pivot_df.to_csv('/home/ubuntu/market_data_2020_2025/etf_pivot_data.csv', index=False)
        print(f"Saved pivot data to etf_pivot_data.csv")
        
        # Create summary statistics
        print("\n" + "=" * 70)
        print("ETF Summary Statistics:")
        print("=" * 70)
        
        summary_data = []
        for symbol, name in etfs:
            etf_df = combined_df[combined_df['Symbol'] == symbol]
            if len(etf_df) > 0:
                first_close = etf_df['Close'].iloc[0]
                last_close = etf_df['Close'].iloc[-1]
                total_return = ((last_close / first_close) - 1) * 100 if first_close else None
                avg_volume = etf_df['Volume'].mean()
                avg_dollar_volume = etf_df['Dollar_Volume'].mean()
                
                summary_data.append({
                    'Symbol': symbol,
                    'Name': name,
                    'Data_Points': len(etf_df),
                    'Start_Date': etf_df['Date'].min(),
                    'End_Date': etf_df['Date'].max(),
                    'First_Close': first_close,
                    'Last_Close': last_close,
                    'Total_Return_Pct': total_return,
                    'Avg_Daily_Volume': avg_volume,
                    'Avg_Dollar_Volume': avg_dollar_volume
                })
                
                print(f"\n{name} ({symbol}):")
                print(f"  Data points: {len(etf_df)}")
                print(f"  Date range: {etf_df['Date'].min()} to {etf_df['Date'].max()}")
                if total_return:
                    print(f"  Total return: {total_return:.2f}%")
                if avg_dollar_volume:
                    print(f"  Avg daily dollar volume: ${avg_dollar_volume/1e9:.2f}B")
        
        # Save summary
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv('/home/ubuntu/market_data_2020_2025/etf_summary.csv', index=False)
        print(f"\nSaved summary to etf_summary.csv")
        
    else:
        print("No data was retrieved")

if __name__ == "__main__":
    main()
