import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
from pathlib import Path
import numpy as np

# Define stocks and their colors
stocks = {
    'NVDA': {'name': 'NVIDIA', 'color': '#00008B'},     # Dark blue
    'AAPL': {'name': 'Apple', 'color': '#FFA000'},       # Amber
    'MSFT': {'name': 'Microsoft', 'color': '#2E7D32'}   # Green
}

# Ensure Output directory exists
output_dir = Path('Output')
output_dir.mkdir(exist_ok=True)

# Step 1: Compute date range (last 10 business days)
# Go back ~14 calendar days to guarantee 10 business days
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=14)

# Fetch data for all stocks
print("Fetching stock data...")
data = {}
for ticker, info in stocks.items():
    print(f"  Downloading {ticker}...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    data[ticker] = df

# Trim to last 10 business days
for ticker in data:
    if len(data[ticker]) >= 10:
        data[ticker] = data[ticker].iloc[-10:]

# Extract closing prices and dates
closing_prices = {}
dates = None
for ticker in stocks.keys():
    # Convert to native Python floats using item() for each value
    closing_prices[ticker] = [v.item() for v in data[ticker]['Close'].values]
    if dates is None:
        dates = list(data[ticker].index)

print(f"Fetched data for {len(dates)} business days")

# Step 2: Create line chart
fig, ax = plt.subplots(figsize=(12, 7))

for ticker in stocks.keys():
    ax.plot(dates, closing_prices[ticker],
            label=stocks[ticker]['name'],
            color=stocks[ticker]['color'],
            linewidth=2,
            marker='o')

ax.set_title('Top 3 S&P 500 Stocks - Last 10 Business Days', fontsize=16, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Stock Price (USD)', fontsize=12)
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)

# Format x-axis labels as "Mon DD"
ax.set_xticks(range(len(dates)))
x_labels = [d.strftime('%a %d') for d in dates]
ax.set_xticklabels(x_labels, rotation=45, ha='right')

plt.tight_layout()

# Save PNG
png_path = output_dir / 'stock_chart.png'
plt.savefig(png_path, dpi=150, bbox_inches='tight')
print(f"Saved chart to {png_path}")

# Step 3: Create PDF with chart and table
pdf_path = output_dir / 'stock_report.pdf'
with PdfPages(pdf_path) as pdf:
    # Page 1: Chart
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    # Page 2: Data table
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('tight')
    ax.axis('off')

    # Prepare table data
    table_data = []
    table_data.append(['Company Name', 'Date', 'Stock Price (USD)'])

    # Sort by company then date
    for ticker in sorted(stocks.keys()):
        for i, date in enumerate(dates):
            price = closing_prices[ticker][i]
            date_str = date.strftime('%Y-%m-%d')
            table_data.append([stocks[ticker]['name'], date_str, f'${price:.2f}'])

    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                    colWidths=[0.3, 0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    # Style header row
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Alternating row colors
    for i in range(1, len(table_data)):
        for j in range(3):
            if (i - 1) % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            else:
                table[(i, j)].set_facecolor('#ffffff')

    ax.set_title('Stock Data - Last 10 Business Days', fontsize=16, fontweight='bold', pad=20)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

print(f"Saved PDF report to {pdf_path}")
print("\nScript completed successfully!")
print(f"Output files:")
print(f"  - {png_path}")
print(f"  - {pdf_path}")
