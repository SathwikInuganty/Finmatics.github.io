import yfinance as yf
import pandas as pd
import plotly.express as px

# Step 1: Get the S&P 500 company list
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tables = pd.read_html(url)
sp500_table = tables[0]
sp500_tickers = sp500_table['Symbol'].tolist()
sp500_names = sp500_table['Security'].tolist()

# Step 2: Fetch market caps
def format_market_cap(value):
    """Convert market cap to human-readable format."""
    if value >= 1_000_000_000_000:  # Trillions
        return f"${value / 1_000_000_000_000:.1f}T"
    elif value >= 1_000_000_000:  # Billions
        return f"${value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:  # Millions
        return f"${value / 1_000_000:.1f}M"
    else:
        return f"${value:.1f}"

market_caps = {}
formatted_market_caps = {}
company_names = {}

for ticker, name in zip(sp500_tickers, sp500_names):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get('marketCap', 0)
        market_caps[ticker] = market_cap
        company_names[ticker] = name
        if market_cap > 0:
            formatted_market_caps[ticker] = format_market_cap(market_cap)
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

# Filter out companies with no market cap data
filtered_data = {k: v for k, v in market_caps.items() if v > 0}

# Prepare data for treemap
treemap_data = pd.DataFrame({
    'Ticker': filtered_data.keys(),
    'Market Cap': filtered_data.values(),
    'Company': [company_names[ticker] for ticker in filtered_data.keys()],
    'Formatted Market Cap': [formatted_market_caps[ticker] for ticker in filtered_data.keys()]
})

# Step 3: Create a treemap
fig = px.treemap(
    treemap_data,
    path=['Company', 'Ticker'],  # Hierarchy: Company name -> Ticker
    values='Market Cap',
    title="S&P 500 Companies by Market Capitalization",
    color='Market Cap',  # Optional: color by market cap
    color_continuous_scale='RdYlGn',
    hover_data={'Market Cap': False, 'Formatted Market Cap': True}
)
fig.update_traces(
    hovertemplate="<b>%{label}</b><br>Market Cap: %{customdata[0]}"
)
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

# Save the treemap as HTML
fig.write_html('sp500_treemap.html')

