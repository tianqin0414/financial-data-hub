#!/usr/bin/env python3
"""
Comprehensive data analysis and visualization for market data 2020-2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style first, then configure fonts
plt.style.use('seaborn-v0_8-whitegrid')

# Configure matplotlib for Chinese characters
plt.rcParams['font.family'] = 'Noto Sans CJK SC'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['figure.dpi'] = 100

# Output directory
OUTPUT_DIR = '/home/ubuntu/market_data_2020_2025/charts'

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    """Load all data files"""
    data = {}
    
    # Commodity futures
    data['commodities'] = pd.read_csv('/home/ubuntu/market_data_2020_2025/commodity_futures_all.csv')
    data['commodities']['Date'] = pd.to_datetime(data['commodities']['Date'])
    
    # ETF data
    data['etf'] = pd.read_csv('/home/ubuntu/market_data_2020_2025/etf_data_all.csv')
    data['etf']['Date'] = pd.to_datetime(data['etf']['Date'])
    
    # ETF summary
    data['etf_summary'] = pd.read_csv('/home/ubuntu/market_data_2020_2025/etf_summary.csv')
    
    # CPI data
    data['cpi'] = pd.read_csv('/home/ubuntu/market_data_2020_2025/cpi_data.csv')
    data['cpi']['Date'] = pd.to_datetime(data['cpi']['Date'])
    
    # Interest rate data
    data['rates'] = pd.read_csv('/home/ubuntu/market_data_2020_2025/interest_rate_data.csv')
    data['rates']['Date'] = pd.to_datetime(data['rates']['Date'])
    
    # PMI data
    data['pmi'] = pd.read_csv('/home/ubuntu/market_data_2020_2025/ism_pmi_data.csv')
    data['pmi']['Date'] = pd.to_datetime(data['pmi']['Date'])
    
    return data

def plot_commodity_prices(data):
    """Plot commodity futures prices"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    commodities = [
        ('CL=F', 'WTI原油期货 (美元/桶)', 'tab:brown'),
        ('GC=F', '黄金期货 (美元/盎司)', 'gold'),
        ('HG=F', '铜期货 (美元/磅)', 'tab:orange')
    ]
    
    for ax, (symbol, title, color) in zip(axes, commodities):
        df = data['commodities'][data['commodities']['Symbol'] == symbol]
        ax.plot(df['Date'], df['Close'], color=color, linewidth=1.5)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Add min/max annotations
        min_idx = df['Close'].idxmin()
        max_idx = df['Close'].idxmax()
        if pd.notna(min_idx) and pd.notna(max_idx):
            min_val = df.loc[min_idx, 'Close']
            max_val = df.loc[max_idx, 'Close']
            min_date = df.loc[min_idx, 'Date']
            max_date = df.loc[max_idx, 'Date']
            ax.annotate(f'最低: ${min_val:.2f}', xy=(min_date, min_val), 
                       xytext=(10, -20), textcoords='offset points', fontsize=9)
            ax.annotate(f'最高: ${max_val:.2f}', xy=(max_date, max_val), 
                       xytext=(10, 10), textcoords='offset points', fontsize=9)
    
    plt.suptitle('商品期货价格走势 (2020-2026)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/commodity_prices.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: commodity_prices.png")

def plot_etf_performance(data):
    """Plot major ETF performance"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Major index ETFs
    ax1 = axes[0, 0]
    for symbol, color in [('SPY', 'blue'), ('QQQ', 'green'), ('IWM', 'red'), ('DIA', 'purple')]:
        df = data['etf'][data['etf']['Symbol'] == symbol]
        # Normalize to 100 at start
        normalized = (df['Close'] / df['Close'].iloc[0]) * 100
        ax1.plot(df['Date'], normalized, label=symbol, linewidth=1.5)
    ax1.set_title('主要指数ETF表现 (标准化至100)', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Sector ETFs
    ax2 = axes[0, 1]
    for symbol, color in [('XLK', 'blue'), ('XLF', 'green'), ('XLE', 'brown'), ('XLV', 'red')]:
        df = data['etf'][data['etf']['Symbol'] == symbol]
        normalized = (df['Close'] / df['Close'].iloc[0]) * 100
        ax2.plot(df['Date'], normalized, label=symbol, linewidth=1.5)
    ax2.set_title('行业ETF表现 (标准化至100)', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Bond ETFs
    ax3 = axes[1, 0]
    for symbol, color in [('TLT', 'blue'), ('IEF', 'green'), ('LQD', 'orange'), ('HYG', 'red')]:
        df = data['etf'][data['etf']['Symbol'] == symbol]
        normalized = (df['Close'] / df['Close'].iloc[0]) * 100
        ax3.plot(df['Date'], normalized, label=symbol, linewidth=1.5)
    ax3.set_title('债券ETF表现 (标准化至100)', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Commodity & International ETFs
    ax4 = axes[1, 1]
    for symbol, color in [('GLD', 'gold'), ('SLV', 'silver'), ('EEM', 'green'), ('FXI', 'red')]:
        df = data['etf'][data['etf']['Symbol'] == symbol]
        normalized = (df['Close'] / df['Close'].iloc[0]) * 100
        ax4.plot(df['Date'], normalized, label=symbol, linewidth=1.5)
    ax4.set_title('商品与国际ETF表现 (标准化至100)', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('ETF表现对比 (2020-2026)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/etf_performance.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: etf_performance.png")

def plot_etf_volume(data):
    """Plot ETF trading volume (proxy for fund flows)"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Calculate monthly average dollar volume for SPY
    spy_df = data['etf'][data['etf']['Symbol'] == 'SPY'].copy()
    spy_df['YearMonth'] = spy_df['Date'].dt.to_period('M')
    monthly_volume = spy_df.groupby('YearMonth')['Dollar_Volume'].mean() / 1e9
    
    colors = ['green' if v > monthly_volume.mean() else 'red' for v in monthly_volume.values]
    
    ax.bar(range(len(monthly_volume)), monthly_volume.values, color=colors, alpha=0.7)
    ax.axhline(y=monthly_volume.mean(), color='blue', linestyle='--', label=f'平均: ${monthly_volume.mean():.1f}B')
    
    # Set x-axis labels
    tick_positions = range(0, len(monthly_volume), 6)
    tick_labels = [str(monthly_volume.index[i]) for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)
    
    ax.set_title('SPY ETF月均成交金额 (十亿美元)', fontsize=14, fontweight='bold')
    ax.set_xlabel('月份')
    ax.set_ylabel('成交金额 (十亿美元)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/etf_volume.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: etf_volume.png")

def plot_macro_indicators(data):
    """Plot macroeconomic indicators"""
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # CPI
    ax1 = axes[0]
    cpi = data['cpi'].dropna(subset=['CPIAUCSL'])
    ax1.plot(cpi['Date'], cpi['CPIAUCSL'], 'b-', linewidth=2, label='CPI (所有项目)')
    if 'CPILFESL' in cpi.columns:
        cpi_core = cpi.dropna(subset=['CPILFESL'])
        ax1.plot(cpi_core['Date'], cpi_core['CPILFESL'], 'r--', linewidth=1.5, label='核心CPI')
    ax1.set_title('消费者价格指数 (CPI)', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Interest Rates
    ax2 = axes[1]
    rates = data['rates'].dropna(subset=['FEDFUNDS'])
    # Resample to monthly for cleaner plot
    rates_monthly = rates.set_index('Date').resample('M').last().reset_index()
    ax2.plot(rates_monthly['Date'], rates_monthly['FEDFUNDS'], 'b-', linewidth=2, label='联邦基金利率')
    if 'DGS10' in rates_monthly.columns:
        ax2.plot(rates_monthly['Date'], rates_monthly['DGS10'], 'g--', linewidth=1.5, label='10年期国债收益率')
    if 'DGS2' in rates_monthly.columns:
        ax2.plot(rates_monthly['Date'], rates_monthly['DGS2'], 'r:', linewidth=1.5, label='2年期国债收益率')
    ax2.set_title('利率走势 (%)', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # PMI
    ax3 = axes[2]
    pmi = data['pmi']
    colors = ['green' if v >= 50 else 'red' for v in pmi['ISM_Manufacturing_PMI']]
    ax3.bar(pmi['Date'], pmi['ISM_Manufacturing_PMI'], color=colors, alpha=0.7, width=25)
    ax3.axhline(y=50, color='black', linestyle='-', linewidth=2, label='扩张/收缩分界线 (50)')
    ax3.set_title('ISM制造业PMI指数', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(35, 70)
    
    plt.suptitle('宏观经济指标 (2020-2026)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/macro_indicators.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: macro_indicators.png")

def plot_correlation_heatmap(data):
    """Plot correlation between different assets"""
    # Prepare monthly returns data
    etf_pivot = data['etf'].pivot_table(index='Date', columns='Symbol', values='Close')
    etf_returns = etf_pivot.pct_change().dropna()
    
    # Select key ETFs
    key_etfs = ['SPY', 'QQQ', 'TLT', 'GLD', 'EEM', 'XLE', 'XLK', 'XLF']
    available_etfs = [e for e in key_etfs if e in etf_returns.columns]
    
    corr_matrix = etf_returns[available_etfs].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr_matrix, cmap='RdYlGn', vmin=-1, vmax=1)
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('相关系数', rotation=-90, va="bottom")
    
    # Set ticks
    ax.set_xticks(np.arange(len(available_etfs)))
    ax.set_yticks(np.arange(len(available_etfs)))
    ax.set_xticklabels(available_etfs)
    ax.set_yticklabels(available_etfs)
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add correlation values
    for i in range(len(available_etfs)):
        for j in range(len(available_etfs)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)
    
    ax.set_title('主要ETF日收益率相关性矩阵 (2020-2026)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: correlation_heatmap.png")

def plot_etf_total_returns(data):
    """Plot ETF total returns bar chart"""
    summary = data['etf_summary'].copy()
    summary = summary.sort_values('Total_Return_Pct', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    colors = ['green' if r > 0 else 'red' for r in summary['Total_Return_Pct']]
    bars = ax.barh(summary['Symbol'], summary['Total_Return_Pct'], color=colors, alpha=0.7)
    
    ax.axvline(x=0, color='black', linewidth=1)
    ax.set_xlabel('累计收益率 (%)')
    ax.set_title('ETF累计收益率 (2020年1月至今)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for bar, val in zip(bars, summary['Total_Return_Pct']):
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
               ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/etf_total_returns.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: etf_total_returns.png")

def create_summary_report(data):
    """Create summary statistics report"""
    report = []
    report.append("=" * 80)
    report.append("市场数据综合分析报告 (2020年1月 - 2026年2月)")
    report.append("=" * 80)
    
    # Commodity summary
    report.append("\n一、商品期货数据摘要")
    report.append("-" * 40)
    for symbol, name in [('CL=F', 'WTI原油'), ('GC=F', '黄金'), ('HG=F', '铜')]:
        df = data['commodities'][data['commodities']['Symbol'] == symbol]
        report.append(f"\n{name} ({symbol}):")
        report.append(f"  数据点数: {len(df)}")
        report.append(f"  起始价格: ${df['Close'].iloc[0]:.2f}")
        report.append(f"  最新价格: ${df['Close'].iloc[-1]:.2f}")
        report.append(f"  最低价格: ${df['Close'].min():.2f}")
        report.append(f"  最高价格: ${df['Close'].max():.2f}")
        total_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
        report.append(f"  累计涨幅: {total_return:.2f}%")
    
    # ETF summary
    report.append("\n\n二、ETF数据摘要")
    report.append("-" * 40)
    summary = data['etf_summary']
    report.append(f"\n共追踪 {len(summary)} 只ETF")
    report.append(f"表现最佳: {summary.loc[summary['Total_Return_Pct'].idxmax(), 'Name']} ({summary['Total_Return_Pct'].max():.2f}%)")
    report.append(f"表现最差: {summary.loc[summary['Total_Return_Pct'].idxmin(), 'Name']} ({summary['Total_Return_Pct'].min():.2f}%)")
    
    # Top 5 performers
    report.append("\n表现最佳的5只ETF:")
    top5 = summary.nlargest(5, 'Total_Return_Pct')
    for _, row in top5.iterrows():
        report.append(f"  {row['Symbol']}: {row['Total_Return_Pct']:.2f}%")
    
    # Bottom 5 performers
    report.append("\n表现最差的5只ETF:")
    bottom5 = summary.nsmallest(5, 'Total_Return_Pct')
    for _, row in bottom5.iterrows():
        report.append(f"  {row['Symbol']}: {row['Total_Return_Pct']:.2f}%")
    
    # Macro indicators summary
    report.append("\n\n三、宏观经济指标摘要")
    report.append("-" * 40)
    
    # CPI
    cpi = data['cpi']
    report.append(f"\nCPI (消费者价格指数):")
    report.append(f"  起始值: {cpi['CPIAUCSL'].iloc[0]:.2f}")
    report.append(f"  最新值: {cpi['CPIAUCSL'].iloc[-1]:.2f}")
    cpi_change = ((cpi['CPIAUCSL'].iloc[-1] / cpi['CPIAUCSL'].iloc[0]) - 1) * 100
    report.append(f"  累计涨幅: {cpi_change:.2f}%")
    
    # Interest rates
    rates = data['rates'].dropna(subset=['FEDFUNDS'])
    report.append(f"\n联邦基金利率:")
    report.append(f"  起始值: {rates['FEDFUNDS'].iloc[0]:.2f}%")
    report.append(f"  最新值: {rates['FEDFUNDS'].iloc[-1]:.2f}%")
    report.append(f"  最低值: {rates['FEDFUNDS'].min():.2f}%")
    report.append(f"  最高值: {rates['FEDFUNDS'].max():.2f}%")
    
    # PMI
    pmi = data['pmi']
    report.append(f"\nISM制造业PMI:")
    report.append(f"  数据点数: {len(pmi)}")
    report.append(f"  最新值: {pmi['ISM_Manufacturing_PMI'].iloc[-1]:.1f}")
    expansion_months = len(pmi[pmi['ISM_Manufacturing_PMI'] >= 50])
    contraction_months = len(pmi[pmi['ISM_Manufacturing_PMI'] < 50])
    report.append(f"  扩张月份: {expansion_months}")
    report.append(f"  收缩月份: {contraction_months}")
    
    report.append("\n" + "=" * 80)
    report.append("报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report.append("=" * 80)
    
    # Save report
    with open('/home/ubuntu/market_data_2020_2025/analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print("Saved: analysis_report.txt")
    return '\n'.join(report)

def main():
    print("Loading data...")
    data = load_data()
    
    print("\nGenerating visualizations...")
    plot_commodity_prices(data)
    plot_etf_performance(data)
    plot_etf_volume(data)
    plot_macro_indicators(data)
    plot_correlation_heatmap(data)
    plot_etf_total_returns(data)
    
    print("\nGenerating summary report...")
    report = create_summary_report(data)
    
    print("\n" + report)
    print("\nAll visualizations and reports generated successfully!")

if __name__ == "__main__":
    main()
