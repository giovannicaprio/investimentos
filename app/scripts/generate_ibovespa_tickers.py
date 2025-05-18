import yfinance as yf
import pandas as pd
import os

def generate_ibovespa_tickers():
    # Get IBOVESPA components
    ibov = yf.Ticker("^BVSP")
    components = ibov.info.get('components', [])
    
    # Create a list to store ticker data
    tickers_data = []
    
    # Process each component
    for ticker in components:
        try:
            # Add .SA suffix for Brazilian stocks
            full_ticker = f"{ticker}.SA"
            stock = yf.Ticker(full_ticker)
            info = stock.info
            
            # Determine if it's a FII
            is_fii = ticker.endswith('11') or ticker.endswith('12')
            
            tickers_data.append({
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'type': 'FII' if is_fii else 'Ação'
            })
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(tickers_data)
    
    # Ensure the data directory exists
    os.makedirs('app/static/data', exist_ok=True)
    
    # Save to CSV
    csv_path = 'app/static/data/ibovespa_tickers.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Saved {len(tickers_data)} tickers to {csv_path}")

if __name__ == "__main__":
    generate_ibovespa_tickers() 