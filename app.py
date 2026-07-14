"""
Financial Statement Analyzer - Pro Version
Live prices, valuation ratios, peer comparison, and comprehensive financial analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Financial Statement Analyzer Pro",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 0.3rem 0;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-top: 0.3rem;
    }
    .valuation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 0.3rem 0;
    }
    .profitability-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 0.3rem 0;
    }
    .growth-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin: 0.3rem 0;
    }
    .live-price-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .price-up {
        color: #00ff88;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .price-down {
        color: #ff4444;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .winner-card {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: #333;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        padding: 0.3rem;
        font-weight: bold;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Currency mapping
CURRENCY_SYMBOLS = {
    'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
    'CNY': '¥', 'AUD': 'A$', 'CAD': 'C$', 'CHF': 'CHF', 'HKD': 'HK$',
    'SGD': 'S$', 'KRW': '₩', 'BRL': 'R$',
}

INDIAN_SUFFIXES = {'NSE': '.NS', 'BSE': '.BO'}

# Indian stock database
INDIAN_STOCKS_DB = {
    'RELIANCE': 'Reliance Industries', 'TCS': 'Tata Consultancy',
    'HDFCBANK': 'HDFC Bank', 'INFY': 'Infosys', 'ICICIBANK': 'ICICI Bank',
    'ITC': 'ITC Ltd', 'WIPRO': 'Wipro', 'TATAMOTORS': 'Tata Motors',
    'SBIN': 'State Bank of India', 'BHARTIARTL': 'Bharti Airtel',
    'KOTAKBANK': 'Kotak Mahindra', 'LT': 'Larsen & Toubro',
    'AXISBANK': 'Axis Bank', 'MARUTI': 'Maruti Suzuki',
    'SUNPHARMA': 'Sun Pharma', 'TATASTEEL': 'Tata Steel',
    'BAJFINANCE': 'Bajaj Finance', 'ADANIENT': 'Adani Enterprises',
    'NTPC': 'NTPC Ltd', 'ONGC': 'ONGC', 'POWERGRID': 'Power Grid',
    'HCLTECH': 'HCL Technologies', 'ASIANPAINT': 'Asian Paints',
    'ULTRACEMCO': 'UltraTech Cement', 'TITAN': 'Titan Company',
    'NESTLEIND': 'Nestle India', 'DRREDDY': "Dr Reddy's",
    'CIPLA': 'Cipla', 'HINDUNILVR': 'Hindustan Unilever',
    'BRITANNIA': 'Britannia', 'EICHERMOT': 'Eicher Motors',
    'COALINDIA': 'Coal India', 'GRASIM': 'Grasim Industries',
    'HEROMOTOCO': 'Hero MotoCorp', 'DIVISLAB': 'Divi\'s Laboratories',
    'TECHM': 'Tech Mahindra', 'INDUSINDBK': 'IndusInd Bank',
    'BAJAJFINSV': 'Bajaj Finserv', 'JSWSTEEL': 'JSW Steel',
}

# Peer groups for comparison
PEER_GROUPS = {
    'Tech_US': ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NVDA'],
    'Tech_India': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
    'Banking_India': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
    'Auto_India': ['TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
    'Pharma_India': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
    'Oil_India': ['RELIANCE.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS'],
    'Finance_US': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    'EV_Auto': ['TSLA', 'RIVN', 'LCID', 'NIO'],
}

class ProFinancialAnalyzer:
    def __init__(self, ticker, exchange=None):
        self.original_ticker = ticker.upper().strip()
        self.ticker = self._format_ticker(ticker.upper().strip(), exchange)
        self.stock = None
        self.financials = {}
        self.metrics = {}
        self.ratios = {}
        self.live_price_data = {}
        self.currency = 'USD'
        self.currency_symbol = '$'
        self.company_name = ''
        
    def _format_ticker(self, ticker, exchange=None):
        if exchange and exchange in INDIAN_SUFFIXES:
            return ticker + INDIAN_SUFFIXES[exchange]
        
        if ticker in INDIAN_STOCKS_DB:
            return ticker + '.NS'
        
        return ticker
    
    def get_live_price(self):
        """Get real-time stock price data"""
        try:
            self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            
            self.live_price_data = {
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose') or info.get('regularMarketPreviousClose'),
                'open': info.get('open') or info.get('regularMarketOpen'),
                'day_high': info.get('dayHigh') or info.get('regularMarketDayHigh'),
                'day_low': info.get('dayLow') or info.get('regularMarketDayLow'),
                'volume': info.get('volume') or info.get('regularMarketVolume'),
                'avg_volume': info.get('averageVolume') or info.get('averageDailyVolume10Day'),
                'market_cap': info.get('marketCap'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'beta': info.get('beta'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSales'),
                'dividend_yield': info.get('dividendYield'),
                'target_mean_price': info.get('targetMeanPrice'),
                'recommendation': info.get('recommendationKey'),
                'number_of_analysts': info.get('numberOfAnalystOpinions'),
            }
            
            self.live_price_data = {k: v for k, v in self.live_price_data.items() if v is not None}
            return True
        except Exception as e:
            st.error(f"Error fetching live price: {str(e)}")
            return False
    
    def fetch_financial_data(self):
        """Fetch all financial data"""
        try:
            if not self.stock:
                self.stock = yf.Ticker(self.ticker)
            
            info = self.stock.info
            
            if not info or len(info) < 5:
                if not self.ticker.endswith('.NS'):
                    alt_ticker = self.ticker + '.NS'
                    self.stock = yf.Ticker(alt_ticker)
                    self.ticker = alt_ticker
                    info = self.stock.info
            
            self.financials['info'] = info
            self.company_name = info.get('longName', self.original_ticker)
            self.financials['sector'] = info.get('sector', 'Unknown')
            self.financials['industry'] = info.get('industry', 'Unknown')
            
            self.financials['income'] = self.stock.financials
            self.financials['balance'] = self.stock.balance_sheet
            self.financials['cashflow'] = self.stock.cashflow
            
            end = datetime.now()
            start = end - timedelta(days=365*3)
            self.financials['prices'] = self.stock.history(start=start, end=end)
            
            self._detect_currency()
            return True
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return False
    
    def _detect_currency(self):
        info = self.financials.get('info', {})
        currency = info.get('currency', info.get('financialCurrency', 'USD'))
        
        if self.ticker.endswith('.NS') or self.ticker.endswith('.BO'):
            currency = 'INR'
        
        self.currency = currency
        self.currency_symbol = CURRENCY_SYMBOLS.get(currency, currency + ' ')
        return currency
    
    def _format_amount(self, value):
        if value is None or pd.isna(value):
            return 'N/A'
        
        if self.currency == 'INR':
            crores = value / 1e7
            if abs(crores) >= 10000:
                return f"{self.currency_symbol}{crores/100:.0f}K Cr"
            elif abs(crores) >= 100:
                return f"{self.currency_symbol}{crores:.0f} Cr"
            else:
                return f"{self.currency_symbol}{crores:.1f} Cr"
        else:
            billions = value / 1e9
            millions = value / 1e6
            if abs(billions) >= 1:
                return f"{self.currency_symbol}{billions:.2f}B"
            else:
                return f"{self.currency_symbol}{millions:.1f}M"
    
    def _safe_get(self, df, keys, col=0):
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if key in df.index and len(df.columns) > col:
                val = df.loc[key].iloc[col]
                if pd.notna(val):
                    return val
        return None
    
    def calculate_all_ratios(self):
        try:
            income = self.financials['income']
            balance = self.financials['balance']
            cashflow = self.financials['cashflow']
            prices = self.financials.get('prices')
            
            current_price = self.live_price_data.get('current_price')
            
            revenue = self._safe_get(income, ['Total Revenue', 'Revenue'])
            revenue_prev = self._safe_get(income, ['Total Revenue', 'Revenue'], 1)
            net_income = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'])
            gross_profit = self._safe_get(income, ['Gross Profit'])
            op_income = self._safe_get(income, ['Operating Income', 'EBIT'])
            
            if revenue:
                if net_income:
                    self.ratios['Net Profit Margin'] = (net_income / revenue) * 100
                if gross_profit:
                    self.ratios['Gross Profit Margin'] = (gross_profit / revenue) * 100
                if op_income:
                    self.ratios['Operating Margin'] = (op_income / revenue) * 100
                if revenue_prev and revenue_prev != 0:
                    self.ratios['Revenue Growth (YoY)'] = ((revenue - revenue_prev) / revenue_prev) * 100
            
            net_income_prev = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'], 1)
            if net_income and net_income_prev and net_income_prev != 0:
                self.ratios['Net Income Growth (YoY)'] = ((net_income - net_income_prev) / net_income_prev) * 100
            
            equity = self._safe_get(balance, ['Stockholders Equity', 'Total Stockholder Equity', 'Total Equity'])
            assets = self._safe_get(balance, ['Total Assets'])
            curr_assets = self._safe_get(balance, ['Current Assets'])
            curr_liab = self._safe_get(balance, ['Current Liabilities'])
            total_debt = self._safe_get(balance, ['Total Debt'])
            long_term_debt = self._safe_get(balance, ['Long Term Debt', 'Long-Term Debt'])
            
            if equity:
                if net_income:
                    self.ratios['ROE'] = (net_income / equity) * 100
                if total_debt:
                    self.ratios['Debt to Equity'] = total_debt / equity
                elif long_term_debt:
                    self.ratios['Debt to Equity'] = long_term_debt / equity
            
            if assets:
                if net_income:
                    self.ratios['ROA'] = (net_income / assets) * 100
            
            if curr_assets and curr_liab:
                self.ratios['Current Ratio'] = curr_assets / curr_liab
                inventory = self._safe_get(balance, ['Inventory', 'Inventories'])
                if inventory:
                    self.ratios['Quick Ratio'] = (curr_assets - inventory) / curr_liab
            
            free_cashflow = self._safe_get(cashflow, ['Free Cash Flow'])
            if free_cashflow and net_income:
                self.ratios['FCF to Net Income'] = free_cashflow / net_income
            
            if current_price:
                diluted_shares = self._safe_get(income, ['Diluted Average Shares', 'Diluted Shares Outstanding'])
                basic_shares = self._safe_get(income, ['Basic Average Shares', 'Basic Shares Outstanding'])
                shares = diluted_shares or basic_shares
                
                if shares:
                    if net_income:
                        eps = net_income / shares
                        self.ratios['EPS'] = eps
                        if eps > 0:
                            self.ratios['P/E Ratio'] = current_price / eps
                    
                    if equity:
                        bvps = equity / shares
                        self.ratios['Book Value per Share'] = bvps
                        if bvps > 0:
                            self.ratios['P/B Ratio'] = current_price / bvps
                    
                    if revenue:
                        sps = revenue / shares
                        if sps > 0:
                            self.ratios['P/S Ratio'] = current_price / sps
                    
                    if free_cashflow:
                        fcfps = free_cashflow / shares
                        if fcfps > 0:
                            self.ratios['P/FCF Ratio'] = current_price / fcfps
                    
                    dividends = self._safe_get(cashflow, ['Dividends Paid'])
                    if dividends:
                        dps = abs(dividends) / shares
                        if current_price > 0:
                            self.ratios['Dividend Yield'] = (dps / current_price) * 100
                
                earnings_growth = self.ratios.get('Net Income Growth (YoY)')
                pe = self.ratios.get('P/E Ratio')
                if earnings_growth and pe and earnings_growth > 0:
                    self.ratios['PEG Ratio'] = pe / earnings_growth
            
            if prices is not None and not prices.empty:
                if len(prices) >= 252:
                    price_52w_ago = prices['Close'].iloc[-252]
                    current = prices['Close'].iloc[-1]
                    self.ratios['52-Week Return'] = ((current - price_52w_ago) / price_52w_ago) * 100
            
            if revenue:
                if assets:
                    self.ratios['Asset Turnover'] = revenue / assets
                if equity:
                    self.ratios['Equity Turnover'] = revenue / equity
            
            self.metrics = self.ratios.copy()
            return True
        except Exception as e:
            st.error(f"Error calculating ratios: {str(e)}")
            return False


def get_peer_comparison(main_ticker, peer_tickers):
    """Fetch and compare metrics for peer companies"""
    peer_data = []
    
    for ticker in peer_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            peer_data.append({
                'Ticker': ticker.replace('.NS', '').replace('.BO', ''),
                'Company': info.get('longName', ticker)[:25],
                'Market Cap (B)': round(info.get('marketCap', 0) / 1e9, 2),
                'P/E Ratio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
                'Forward P/E': round(info.get('forwardPE', 0), 2) if info.get('forwardPE') else None,
                'P/B Ratio': round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else None,
                'Revenue Growth': round(info.get('revenueGrowth', 0) * 100, 2) if info.get('revenueGrowth') else None,
                'Profit Margin': round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else None,
                'ROE': round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else None,
                'Debt/Equity': round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else None,
                'Dividend Yield': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else None,
                'Current Price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'Recommendation': info.get('recommendationKey', 'N/A'),
            })
        except:
            continue
    
    return pd.DataFrame(peer_data)


def create_peer_comparison_charts(peer_df, main_ticker_name, currency_symbol):
    """Create peer comparison visualizations"""
    
    st.markdown("---")
    st.markdown("## 🏢 Peer Comparison")
    
    if peer_df.empty or len(peer_df) < 2:
        st.warning("Not enough peer data available for comparison.")
        return
    
    # Clean ticker name
    main_ticker_clean = main_ticker_name.replace('.NS', '').replace('.BO', '')
    
    # === 1. Market Cap Comparison ===
    st.markdown("### 📊 Market Capitalization Comparison")
    
    fig = go.Figure()
    
    # Sort by market cap
    sorted_df = peer_df.sort_values('Market Cap (B)', ascending=True)
    
    colors = ['#ff4444' if ticker == main_ticker_clean else '#1f77b4' for ticker in sorted_df['Ticker']]
    
    fig.add_trace(go.Bar(
        y=sorted_df['Ticker'],
        x=sorted_df['Market Cap (B)'],
        orientation='h',
        marker_color=colors,
        text=[f"${v:.1f}B" if v > 0 else 'N/A' for v in sorted_df['Market Cap (B)']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'Market Cap Comparison ({currency_symbol}B)',
        height=400,
        template='plotly_white',
        xaxis_title='Market Cap (Billions)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # === 2. Valuation Metrics Comparison ===
    st.markdown("### 📈 Valuation Metrics Comparison")
    
    metrics_to_plot = ['P/E Ratio', 'P/B Ratio', 'Revenue Growth', 'ROE']
    available_metrics = [m for m in metrics_to_plot if m in peer_df.columns and peer_df[m].notna().any()]
    
    if available_metrics:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=available_metrics[:4],
            vertical_spacing=0.15
        )
        
        positions = [(1,1), (1,2), (2,1), (2,2)]
        
        for i, metric in enumerate(available_metrics[:4]):
            row, col = positions[i]
            
            # Filter out None values
            valid_data = peer_df[peer_df[metric].notna()]
            
            colors = ['#ff4444' if ticker == main_ticker_clean else '#1f77b4' for ticker in valid_data['Ticker']]
            
            fig.add_trace(
                go.Bar(
                    x=valid_data['Ticker'],
                    y=valid_data[metric],
                    name=metric,
                    marker_color=colors,
                    text=[f"{v:.1f}" if v else 'N/A' for v in valid_data[metric]],
                    textposition='outside'
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            height=600,
            template='plotly_white',
            showlegend=False,
            title_text="Peer Comparison - Key Metrics"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # === 3. Detailed Comparison Table ===
    st.markdown("### 📋 Detailed Peer Comparison Table")
    
    # Highlight the main company
    def highlight_main(row):
        if row['Ticker'] == main_ticker_clean:
            return ['background-color: #fff3cd'] * len(row)
        return [''] * len(row)
    
    # Format the dataframe
    display_df = peer_df.copy()
    
    # Round numeric columns
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'int64']:
            display_df[col] = display_df[col].round(2)
    
    # Style the dataframe
    styled_df = display_df.style.apply(highlight_main, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # === 4. Peer Summary Statistics ===
    st.markdown("### 📊 Peer Group Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate averages (excluding the main company)
    other_peers = peer_df[peer_df['Ticker'] != main_ticker_clean]
    
    with col1:
        avg_pe = other_peers['P/E Ratio'].mean()
        main_pe = peer_df[peer_df['Ticker'] == main_ticker_clean]['P/E Ratio'].values
        main_pe_val = main_pe[0] if len(main_pe) > 0 else None
        
        st.metric(
            "Avg Peer P/E",
            f"{avg_pe:.1f}" if pd.notna(avg_pe) else "N/A",
            delta=f"{main_pe_val:.1f} (Yours)" if main_pe_val and pd.notna(avg_pe) else None
        )
    
    with col2:
        avg_roe = other_peers['ROE'].mean()
        main_roe = peer_df[peer_df['Ticker'] == main_ticker_clean]['ROE'].values
        main_roe_val = main_roe[0] if len(main_roe) > 0 else None
        
        st.metric(
            "Avg Peer ROE",
            f"{avg_roe:.1f}%" if pd.notna(avg_roe) else "N/A",
            delta=f"{main_roe_val:.1f}% (Yours)" if main_roe_val and pd.notna(avg_roe) else None
        )
    
    with col3:
        avg_growth = other_peers['Revenue Growth'].mean()
        main_growth = peer_df[peer_df['Ticker'] == main_ticker_clean]['Revenue Growth'].values
        main_growth_val = main_growth[0] if len(main_growth) > 0 else None
        
        st.metric(
            "Avg Peer Growth",
            f"{avg_growth:.1f}%" if pd.notna(avg_growth) else "N/A",
            delta=f"{main_growth_val:.1f}% (Yours)" if main_growth_val and pd.notna(avg_growth) else None
        )
    
    with col4:
        avg_de = other_peers['Debt/Equity'].mean()
        main_de = peer_df[peer_df['Ticker'] == main_ticker_clean]['Debt/Equity'].values
        main_de_val = main_de[0] if len(main_de) > 0 else None
        
        st.metric(
            "Avg Peer D/E",
            f"{avg_de:.1f}" if pd.notna(avg_de) else "N/A",
            delta=f"{main_de_val:.1f} (Yours)" if main_de_val and pd.notna(avg_de) else None,
            delta_color="inverse"
        )
    
    # === 5. Recommendation Summary ===
    st.markdown("### 🎯 Analyst Recommendations")
    
    rec_counts = peer_df['Recommendation'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=rec_counts.index,
        values=rec_counts.values,
        hole=0.4,
        marker_colors=['#00ff88', '#88ff00', '#ffa500', '#ff4444', '#ff0000']
    )])
    
    fig.update_layout(
        title='Peer Group - Analyst Consensus Distribution',
        height=350,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_live_price_dashboard(analyzer):
    price_data = analyzer.live_price_data
    currency = analyzer.currency_symbol
    
    st.markdown("### 🟢 Live Market Data")
    
    current_price = price_data.get('current_price')
    prev_close = price_data.get('previous_close')
    
    if current_price and prev_close:
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        color = "price-up" if change >= 0 else "price-down"
        arrow = "▲" if change >= 0 else "▼"
        
        st.markdown(f"""
        <div class="live-price-box">
            <h3>{analyzer.company_name}</h3>
            <div class="{color}">
                {currency}{current_price:.2f} {arrow}
            </div>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                {currency}{abs(change):.2f} ({change_pct:+.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("Open", f"{currency}{price_data.get('open', 0):.2f}"),
        ("Day High", f"{currency}{price_data.get('day_high', 0):.2f}"),
        ("Day Low", f"{currency}{price_data.get('day_low', 0):.2f}"),
        ("Volume", f"{price_data.get('volume', 0):,.0f}"),
    ]
    for col, (label, value) in zip([col1, col2, col3, col4], stats):
        col.metric(label, value)
    
    col1, col2, col3, col4 = st.columns(4)
    stats2 = [
        ("52-Week High", f"{currency}{price_data.get('fifty_two_week_high', 0):.2f}"),
        ("52-Week Low", f"{currency}{price_data.get('fifty_two_week_low', 0):.2f}"),
        ("Market Cap", analyzer._format_amount(price_data.get('market_cap', 0))),
        ("Beta", f"{price_data.get('beta', 0):.2f}"),
    ]
    for col, (label, value) in zip([col1, col2, col3, col4], stats2):
        col.metric(label, value)


def create_ratio_dashboard(ratios, currency_symbol):
    st.markdown("### 📊 Financial Ratios Dashboard")
    
    categories = {
        '📈 Valuation Ratios': {
            'P/E Ratio': 'Price to Earnings',
            'P/B Ratio': 'Price to Book',
            'P/S Ratio': 'Price to Sales',
            'P/FCF Ratio': 'Price to Free Cash Flow',
            'PEG Ratio': 'Price/Earnings to Growth',
            'Dividend Yield': 'Dividend Yield %',
        },
        '💰 Profitability Ratios': {
            'Net Profit Margin': 'Net Margin %',
            'Gross Profit Margin': 'Gross Margin %',
            'Operating Margin': 'Operating Margin %',
            'ROE': 'Return on Equity %',
            'ROA': 'Return on Assets %',
        },
        '📊 Growth Metrics': {
            'Revenue Growth (YoY)': 'Revenue Growth %',
            'Net Income Growth (YoY)': 'Earnings Growth %',
            '52-Week Return': '52-Week Return %',
            'EPS': 'Earnings Per Share',
        },
        '🏦 Financial Health': {
            'Current Ratio': 'Liquidity Ratio',
            'Quick Ratio': 'Quick Ratio',
            'Debt to Equity': 'Leverage Ratio',
            'Asset Turnover': 'Asset Efficiency',
        },
    }
    
    for category, metrics in categories.items():
        available_metrics = {k: v for k, v in ratios.items() if k in metrics}
        
        if available_metrics:
            st.markdown(f"#### {category}")
            cols = st.columns(min(len(available_metrics), 4))
            
            for i, (name, value) in enumerate(available_metrics.items()):
                col_idx = i % 4
                with cols[col_idx]:
                    if isinstance(value, (int, float)):
                        if 'Ratio' in name and 'P/E' not in name and 'PEG' not in name:
                            display = f"{value:.2f}"
                        elif 'Margin' in name or 'Growth' in name or 'Yield' in name or 'ROE' in name or 'ROA' in name or 'Return' in name:
                            display = f"{value:.2f}%"
                        elif 'per Share' in name:
                            display = f"{currency_symbol}{value:.2f}"
                        else:
                            display = f"{value:.2f}"
                        
                        if 'Valuation' in category:
                            card_class = "valuation-card"
                        elif 'Profitability' in category:
                            card_class = "profitability-card"
                        elif 'Growth' in category:
                            card_class = "growth-card"
                        else:
                            card_class = "metric-card"
                        
                        st.markdown(f"""
                        <div class="{card_class}">
                            <div class="metric-value">{display}</div>
                            <div class="metric-label">{metrics[name]}</div>
                        </div>
                        """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)


def create_advanced_charts(analyzer):
    financials = analyzer.financials
    currency = analyzer.currency_symbol
    
    st.markdown("### 📉 Advanced Charts")
    
    prices = financials.get('prices')
    if prices is not None and not prices.empty:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('Price & Moving Averages', 'Volume')
        )
        
        fig.add_trace(go.Candlestick(
            x=prices.index, open=prices['Open'], high=prices['High'],
            low=prices['Low'], close=prices['Close'], name='Price'
        ), row=1, col=1)
        
        ma20 = prices['Close'].rolling(window=20).mean()
        ma50 = prices['Close'].rolling(window=50).mean()
        ma200 = prices['Close'].rolling(window=200).mean()
        
        fig.add_trace(go.Scatter(x=prices.index, y=ma20, name='20-day MA', line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=prices.index, y=ma50, name='50-day MA', line=dict(color='blue', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=prices.index, y=ma200, name='200-day MA', line=dict(color='red', width=1)), row=1, col=1)
        
        colors = ['green' if prices['Close'].iloc[i] >= prices['Open'].iloc[i] else 'red' for i in range(len(prices))]
        fig.add_trace(go.Bar(x=prices.index, y=prices['Volume'], name='Volume', marker_color=colors), row=2, col=1)
        
        fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False, hovermode='x unified')
        fig.update_yaxes(title_text=f"Price ({currency})", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Returns Distribution
    if prices is not None and not prices.empty:
        returns = prices['Close'].pct_change().dropna() * 100
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=returns, nbinsx=50, name='Daily Returns', marker_color='#1f77b4', opacity=0.7, histnorm='probability density'))
        
        if len(returns) > 1:
            mean_ret = returns.mean()
            std_ret = returns.std()
            x_range = np.linspace(returns.min(), returns.max(), 100)
            y_curve = (1/(std_ret * np.sqrt(2*np.pi))) * np.exp(-(x_range - mean_ret)**2 / (2*std_ret**2))
            fig.add_trace(go.Scatter(x=x_range, y=y_curve, name='Normal Distribution', line=dict(color='red', width=2)))
        
        fig.add_vline(x=returns.mean(), line_dash="dash", line_color="green", annotation_text=f"Mean: {returns.mean():.2f}%")
        fig.update_layout(title='Daily Returns Distribution', template='plotly_white', height=400, xaxis_title='Daily Return (%)', yaxis_title='Probability Density')
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean Return", f"{returns.mean():.3f}%")
        col2.metric("Std Deviation", f"{returns.std():.3f}%")
        col3.metric("Skewness", f"{returns.skew():.3f}")
        col4.metric("Kurtosis", f"{returns.kurtosis():.3f}")


def detect_peer_group(ticker):
    """Auto-detect which peer group a ticker belongs to"""
    for group_name, tickers in PEER_GROUPS.items():
        if ticker in tickers:
            return group_name, tickers
    return None, []


def main():
    st.markdown('<h1 class="main-header">📊 Financial Statement Analyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Live Prices • Peer Comparison • 20+ Ratios • Advanced Charts</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("🔍 Search & Settings")
        
        ticker = st.text_input("Enter Stock Ticker:", "AAPL", max_chars=50)
        
        exchange = st.selectbox(
            "Exchange:",
            ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"]
        )
        
        exchange_map = {
            "NSE India (.NS)": "NSE",
            "BSE India (.BO)": "BSE",
            "US Market": None,
            "Auto-detect": None
        }
        
        # === PEER COMPARISON OPTIONS ===
        st.divider()
        st.subheader("🏢 Peer Comparison")
        
        use_peer_comparison = st.checkbox("Enable Peer Comparison", value=True)
        
        # Custom peer input
        custom_peers = st.text_input(
            "Add custom peers (comma-separated):",
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Leave empty to auto-detect peers"
        )
        
        auto_refresh = st.checkbox("Auto-refresh price (30s)", value=False)
        analyze_btn = st.button("🔍 Analyze Company", type="primary", use_container_width=True)
        
        st.divider()
        
        tab1, tab2 = st.tabs(["Indian Stocks", "US Stocks"])
        
        with tab1:
            for tick, name in list(INDIAN_STOCKS_DB.items())[:15]:
                if st.button(f"{tick}", use_container_width=True, key=f"i_{tick}"):
                    st.session_state['ticker'] = tick
                    st.rerun()
        
        with tab2:
            for stock in ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM"]:
                if st.button(stock, use_container_width=True, key=f"u_{stock}"):
                    st.session_state['ticker'] = stock
                    st.rerun()
    
    if 'ticker' in st.session_state:
        ticker = st.session_state['ticker']
    
    if not analyze_btn and 'ticker' not in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 🚀 Pro Features
            
            - **Live Stock Prices** - Real-time market data
            - **Peer Comparison** - Compare against industry rivals
            - **20+ Financial Ratios** - Comprehensive analysis
            - **Valuation Metrics** - P/E, P/B, P/S, PEG
            - **Advanced Charts** - Moving averages, returns distribution
            - **Multi-Currency** - ₹, $, €, £, ¥ support
            - **Global Coverage** - Indian & International stocks
            
            👈 Enter a ticker and click Analyze to begin!
            """)
        return
    
    selected_exchange = exchange_map.get(exchange)
    analyzer = ProFinancialAnalyzer(ticker, exchange=selected_exchange)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Fetching live market data...")
    progress_bar.progress(25)
    analyzer.get_live_price()
    
    status_text.text("Downloading financial statements...")
    progress_bar.progress(50)
    if not analyzer.fetch_financial_data():
        st.error("Unable to fetch financial data.")
        progress_bar.empty()
        status_text.empty()
        return
    
    status_text.text("Calculating financial ratios...")
    progress_bar.progress(75)
    analyzer.calculate_all_ratios()
    
    status_text.text("Generating visualizations...")
    progress_bar.progress(100)
    time.sleep(0.3)
    progress_bar.empty()
    status_text.empty()
    
    # === DISPLAY RESULTS ===
    
    # 1. Live Price
    create_live_price_dashboard(analyzer)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # 2. Analyst Recommendation
    if analyzer.live_price_data.get('recommendation'):
        st.markdown("### 🎯 Analyst Consensus")
        rec = analyzer.live_price_data.get('recommendation', '').upper()
        analysts = analyzer.live_price_data.get('number_of_analysts', 'N/A')
        
        rec_color = {
            'BUY': '#00ff88', 'STRONG_BUY': '#00ff88',
            'HOLD': '#ffa500', 'SELL': '#ff4444',
            'STRONG_SELL': '#ff4444'
        }.get(rec, '#666')
        
        st.markdown(f"""
        <div style="background-color: {rec_color}; padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <h3>{rec.replace('_', ' ')}</h3>
            <p>Based on {analysts} analysts</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 3. Company Info
    info = analyzer.financials['info']
    st.markdown(f"""
    <div class="info-box">
        <strong>{analyzer.company_name}</strong> | 
        Sector: {analyzer.financials.get('sector', 'N/A')} | 
        Industry: {analyzer.financials.get('industry', 'N/A')} | 
        Currency: {analyzer.currency} ({analyzer.currency_symbol})
    </div>
    """, unsafe_allow_html=True)
    
    # 4. Financial Ratios
    create_ratio_dashboard(analyzer.ratios, analyzer.currency_symbol)
    
    # 5. Advanced Charts
    create_advanced_charts(analyzer)
    
    # 6. === PEER COMPARISON (NEW!) ===
    if use_peer_comparison:
        # Determine peers
        if custom_peers:
            peer_list = [p.strip().upper() for p in custom_peers.split(',') if p.strip()]
        else:
            group_name, peer_list = detect_peer_group(analyzer.ticker)
            
            if group_name:
                st.info(f"🔍 Auto-detected peer group: **{group_name.replace('_', ' ')}**")
            else:
                st.warning("No auto peer group found. Add custom peers in the sidebar.")
        
        # Remove main ticker from peers if present
        peer_list = [p for p in peer_list if p != analyzer.ticker]
        
        # Add main ticker to comparison
        all_tickers = [analyzer.ticker] + peer_list[:7]  # Max 8 companies
        
        if len(all_tickers) >= 2:
            with st.spinner("Fetching peer comparison data..."):
                peer_df = get_peer_comparison(analyzer.ticker, all_tickers)
                create_peer_comparison_charts(peer_df, analyzer.ticker, analyzer.currency_symbol)
    
    # 7. Financial Statements
    st.markdown("---")
    st.markdown("### 📋 Financial Statements")
    st.caption(f"All amounts in {analyzer.currency} ({analyzer.currency_symbol})")
    
    tab1, tab2, tab3 = st.tabs(["📊 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])
    
    with tab1:
        income_df = analyzer.financials.get('income')
        if income_df is not None and not income_df.empty:
            st.dataframe(income_df, use_container_width=True)
            csv = income_df.to_csv()
            st.download_button("📥 Download CSV", csv, f"{analyzer.original_ticker}_income.csv", "text/csv")
        else:
            st.warning("Income Statement not available.")
    
    with tab2:
        balance_df = analyzer.financials.get('balance')
        if balance_df is not None and not balance_df.empty:
            st.dataframe(balance_df, use_container_width=True)
            csv = balance_df.to_csv()
            st.download_button("📥 Download CSV", csv, f"{analyzer.original_ticker}_balance.csv", "text/csv")
        else:
            st.warning("Balance Sheet not available.")
    
    with tab3:
        cashflow_df = analyzer.financials.get('cashflow')
        if cashflow_df is not None and not cashflow_df.empty:
            st.dataframe(cashflow_df, use_container_width=True)
            csv = cashflow_df.to_csv()
            st.download_button("📥 Download CSV", csv, f"{analyzer.original_ticker}_cashflow.csv", "text/csv")
        else:
            st.warning("Cash Flow not available.")
    
    st.divider()
    st.caption(f"Data: Yahoo Finance | Currency: {analyzer.currency} | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()