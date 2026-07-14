"""
Financial Statement Analyzer - Pro Version
Modern UI with Peer Comparison, Live Prices, and Advanced Analytics
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="FinAnalyzer Pro | Stock Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== MODERN UI CSS ==========
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Live Price Box */
    .live-price-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .live-price-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .price-up {
        color: #00ff88;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(0,255,136,0.3);
    }
    
    .price-down {
        color: #ff4757;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(255,71,87,0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: #e2e8f0;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102,126,234,0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .valuation-card {
        background: linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%);
        border: 1px solid rgba(240, 147, 251, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: #e2e8f0;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    
    .valuation-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(240,147,251,0.2);
        border-color: rgba(240, 147, 251, 0.5);
    }
    
    .profitability-card {
        background: linear-gradient(135deg, #4facfe15 0%, #00f2fe15 100%);
        border: 1px solid rgba(79, 172, 254, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: #e2e8f0;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    
    .profitability-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(79,172,254,0.2);
        border-color: rgba(79, 172, 254, 0.5);
    }
    
    .growth-card {
        background: linear-gradient(135deg, #43e97b15 0%, #38f9d715 100%);
        border: 1px solid rgba(67, 233, 123, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: #e2e8f0;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    
    .growth-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(67,233,123,0.2);
        border-color: rgba(67, 233, 123, 0.5);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        color: #e2e8f0;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102,126,234,0.4);
    }
    
    /* Analyst Card */
    .analyst-card {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-weight: 600;
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
    }
    
    .analyst-card:hover {
        transform: scale(1.02);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.2rem;
        color: #94a3b8;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea30 0%, #764ba230 100%);
        color: #667eea;
        border-bottom: 2px solid #667eea;
    }
    
    /* Metric Container */
    div[data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* DataFrame */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    /* Pulse animation for live indicator */
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff88;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0,255,136,0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0,255,136,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,255,136,0); }
    }
</style>
""", unsafe_allow_html=True)

# ========== CONSTANTS ==========
CURRENCY_SYMBOLS = {
    'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
    'CNY': '¥', 'AUD': 'A$', 'CAD': 'C$', 'CHF': 'CHF', 'HKD': 'HK$',
    'SGD': 'S$', 'KRW': '₩', 'BRL': 'R$',
}

INDIAN_SUFFIXES = {'NSE': '.NS', 'BSE': '.BO'}

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

PEER_GROUPS = {
    '🖥️ Tech Giants (US)': ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NVDA'],
    '💻 IT Services (India)': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
    '🏦 Banking (India)': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
    '🚗 Automobile (India)': ['TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
    '💊 Pharma (India)': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
    '🛢️ Energy (India)': ['RELIANCE.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS'],
    '🏦 Banking (US)': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    '🚀 EV & Auto Tech': ['TSLA', 'RIVN', 'LCID', 'NIO'],
}

# ========== ANALYZER CLASS ==========
class ProFinancialAnalyzer:
    def __init__(self, ticker, exchange=None):
        self.original_ticker = ticker.upper().strip()
        self.ticker = self._format_ticker(ticker.upper().strip(), exchange)
        self.stock = None
        self.financials = {}
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
                'market_cap': info.get('marketCap'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'beta': info.get('beta'),
                'target_mean_price': info.get('targetMeanPrice'),
                'recommendation': info.get('recommendationKey'),
                'number_of_analysts': info.get('numberOfAnalystOpinions'),
            }
            self.live_price_data = {k: v for k, v in self.live_price_data.items() if v is not None}
            return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False
    
    def fetch_financial_data(self):
        try:
            if not self.stock:
                self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            if not info or len(info) < 5:
                if not self.ticker.endswith('.NS'):
                    self.stock = yf.Ticker(self.ticker + '.NS')
                    self.ticker = self.ticker + '.NS'
                    info = self.stock.info
            self.financials['info'] = info
            self.company_name = info.get('longName', self.original_ticker)
            self.financials['sector'] = info.get('sector', 'Unknown')
            self.financials['industry'] = info.get('industry', 'Unknown')
            self.financials['income'] = self.stock.financials
            self.financials['balance'] = self.stock.balance_sheet
            self.financials['cashflow'] = self.stock.cashflow
            end = datetime.now()
            self.financials['prices'] = self.stock.history(start=end - timedelta(days=365*3), end=end)
            self._detect_currency()
            return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False
    
    def _detect_currency(self):
        info = self.financials.get('info', {})
        currency = info.get('currency', info.get('financialCurrency', 'USD'))
        if self.ticker.endswith('.NS') or self.ticker.endswith('.BO'):
            currency = 'INR'
        self.currency = currency
        self.currency_symbol = CURRENCY_SYMBOLS.get(currency, currency + ' ')
    
    def _format_amount(self, value):
        if value is None or pd.isna(value): return 'N/A'
        if self.currency == 'INR':
            cr = value / 1e7
            return f"{self.currency_symbol}{cr/100:.0f}K Cr" if abs(cr) >= 10000 else f"{self.currency_symbol}{cr:.0f} Cr" if abs(cr) >= 100 else f"{self.currency_symbol}{cr:.1f} Cr"
        b = value / 1e9
        return f"{self.currency_symbol}{b:.2f}B" if abs(b) >= 1 else f"{self.currency_symbol}{value/1e6:.1f}M"
    
    def _safe_get(self, df, keys, col=0):
        if isinstance(keys, str): keys = [keys]
        for key in keys:
            if key in df.index and len(df.columns) > col:
                val = df.loc[key].iloc[col]
                if pd.notna(val): return val
        return None
    
    def calculate_all_ratios(self):
        try:
            income = self.financials['income']
            balance = self.financials['balance']
            cashflow = self.financials['cashflow']
            prices = self.financials.get('prices')
            cp = self.live_price_data.get('current_price')
            
            rev = self._safe_get(income, ['Total Revenue', 'Revenue'])
            rev_p = self._safe_get(income, ['Total Revenue', 'Revenue'], 1)
            ni = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'])
            gp = self._safe_get(income, ['Gross Profit'])
            oi = self._safe_get(income, ['Operating Income', 'EBIT'])
            
            if rev:
                if ni: self.ratios['Net Profit Margin'] = (ni/rev)*100
                if gp: self.ratios['Gross Profit Margin'] = (gp/rev)*100
                if oi: self.ratios['Operating Margin'] = (oi/rev)*100
                if rev_p and rev_p != 0: self.ratios['Revenue Growth (YoY)'] = ((rev-rev_p)/rev_p)*100
            
            ni_p = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'], 1)
            if ni and ni_p and ni_p != 0: self.ratios['Net Income Growth (YoY)'] = ((ni-ni_p)/ni_p)*100
            
            eq = self._safe_get(balance, ['Stockholders Equity', 'Total Stockholder Equity', 'Total Equity'])
            ast = self._safe_get(balance, ['Total Assets'])
            ca = self._safe_get(balance, ['Current Assets'])
            cl = self._safe_get(balance, ['Current Liabilities'])
            td = self._safe_get(balance, ['Total Debt']) or self._safe_get(balance, ['Long Term Debt', 'Long-Term Debt'])
            
            if eq:
                if ni: self.ratios['ROE'] = (ni/eq)*100
                if td: self.ratios['Debt to Equity'] = td/eq
            if ast and ni: self.ratios['ROA'] = (ni/ast)*100
            if ca and cl:
                self.ratios['Current Ratio'] = ca/cl
                inv = self._safe_get(balance, ['Inventory', 'Inventories'])
                if inv: self.ratios['Quick Ratio'] = (ca-inv)/cl
            
            fcf = self._safe_get(cashflow, ['Free Cash Flow'])
            if fcf and ni: self.ratios['FCF to Net Income'] = fcf/ni
            
            if cp:
                shares = self._safe_get(income, ['Diluted Average Shares', 'Diluted Shares Outstanding']) or self._safe_get(income, ['Basic Average Shares', 'Basic Shares Outstanding'])
                if shares:
                    if ni:
                        eps = ni/shares
                        self.ratios['EPS'] = eps
                        if eps > 0: self.ratios['P/E Ratio'] = cp/eps
                    if eq:
                        bvps = eq/shares
                        if bvps > 0: self.ratios['P/B Ratio'] = cp/bvps
                    if rev and rev/shares > 0: self.ratios['P/S Ratio'] = cp/(rev/shares)
                    if fcf and fcf/shares > 0: self.ratios['P/FCF Ratio'] = cp/(fcf/shares)
                    div = self._safe_get(cashflow, ['Dividends Paid'])
                    if div and cp > 0: self.ratios['Dividend Yield'] = (abs(div)/shares/cp)*100
                
                eg = self.ratios.get('Net Income Growth (YoY)')
                pe = self.ratios.get('P/E Ratio')
                if eg and pe and eg > 0: self.ratios['PEG Ratio'] = pe/eg
            
            if prices is not None and not prices.empty and len(prices) >= 252:
                self.ratios['52-Week Return'] = ((prices['Close'].iloc[-1] - prices['Close'].iloc[-252])/prices['Close'].iloc[-252])*100
            
            if rev:
                if ast: self.ratios['Asset Turnover'] = rev/ast
                if eq: self.ratios['Equity Turnover'] = rev/eq
            
            return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False


# ========== PEER COMPARISON ==========
def get_peer_comparison(main_ticker, peer_tickers):
    peer_data = []
    for ticker in peer_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            peer_data.append({
                'Ticker': ticker.replace('.NS','').replace('.BO',''),
                'Company': info.get('longName', ticker)[:25],
                'Market Cap (B)': round(info.get('marketCap', 0)/1e9, 2),
                'P/E Ratio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
                'P/B Ratio': round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else None,
                'Revenue Growth': round(info.get('revenueGrowth', 0)*100, 2) if info.get('revenueGrowth') else None,
                'Profit Margin': round(info.get('profitMargins', 0)*100, 2) if info.get('profitMargins') else None,
                'ROE': round(info.get('returnOnEquity', 0)*100, 2) if info.get('returnOnEquity') else None,
                'Debt/Equity': round(info.get('debtToEquity', 0), 2) if info.get('debtToEquity') else None,
                'Dividend Yield': round(info.get('dividendYield', 0)*100, 2) if info.get('dividendYield') else None,
                'Current Price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'Recommendation': info.get('recommendationKey', 'N/A'),
            })
        except:
            continue
    return pd.DataFrame(peer_data)


def create_peer_comparison_charts(peer_df, main_ticker_name, currency_symbol):
    st.markdown("---")
    st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
    
    if peer_df.empty or len(peer_df) < 2:
        st.warning("Not enough peer data available.")
        return
    
    main_ticker_clean = main_ticker_name.replace('.NS','').replace('.BO','')
    
    # Market Cap
    st.markdown("#### 📊 Market Capitalization")
    sorted_df = peer_df.sort_values('Market Cap (B)', ascending=True)
    colors = ['#ff4757' if t == main_ticker_clean else '#667eea' for t in sorted_df['Ticker']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_df['Ticker'], x=sorted_df['Market Cap (B)'],
        orientation='h', marker_color=colors,
        text=[f"${v:.1f}B" if v > 0 else 'N/A' for v in sorted_df['Market Cap (B)']],
        textposition='outside', textfont=dict(color='#e2e8f0')
    ))
    fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_title='Market Cap (Billions)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Valuation Metrics
    st.markdown("#### 📈 Key Metrics Comparison")
    metrics_to_plot = ['P/E Ratio', 'P/B Ratio', 'Revenue Growth', 'ROE']
    available = [m for m in metrics_to_plot if m in peer_df.columns and peer_df[m].notna().any()]
    
    if available:
        fig = make_subplots(rows=2, cols=2, subplot_titles=available[:4], vertical_spacing=0.15)
        positions = [(1,1), (1,2), (2,1), (2,2)]
        
        for i, metric in enumerate(available[:4]):
            row, col = positions[i]
            valid_data = peer_df[peer_df[metric].notna()]
            colors = ['#ff4757' if t == main_ticker_clean else '#667eea' for t in valid_data['Ticker']]
            fig.add_trace(go.Bar(x=valid_data['Ticker'], y=valid_data[metric], marker_color=colors, text=[f"{v:.1f}" for v in valid_data[metric]], textposition='outside'), row=row, col=col)
        
        fig.update_layout(height=600, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, title_text="Peer Comparison - Key Metrics")
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary Stats
    st.markdown("#### 📊 Peer Group Summary")
    other_peers = peer_df[peer_df['Ticker'] != main_ticker_clean]
    
    c1, c2, c3, c4 = st.columns(4)
    main_pe = peer_df[peer_df['Ticker'] == main_ticker_clean]['P/E Ratio'].values
    main_roe = peer_df[peer_df['Ticker'] == main_ticker_clean]['ROE'].values
    main_growth = peer_df[peer_df['Ticker'] == main_ticker_clean]['Revenue Growth'].values
    main_de = peer_df[peer_df['Ticker'] == main_ticker_clean]['Debt/Equity'].values
    
    c1.metric("Avg Peer P/E", f"{other_peers['P/E Ratio'].mean():.1f}" if pd.notna(other_peers['P/E Ratio'].mean()) else "N/A", delta=f"{main_pe[0]:.1f} (You)" if len(main_pe)>0 else None)
    c2.metric("Avg Peer ROE", f"{other_peers['ROE'].mean():.1f}%" if pd.notna(other_peers['ROE'].mean()) else "N/A", delta=f"{main_roe[0]:.1f}% (You)" if len(main_roe)>0 else None)
    c3.metric("Avg Peer Growth", f"{other_peers['Revenue Growth'].mean():.1f}%" if pd.notna(other_peers['Revenue Growth'].mean()) else "N/A", delta=f"{main_growth[0]:.1f}% (You)" if len(main_growth)>0 else None)
    c4.metric("Avg Peer D/E", f"{other_peers['Debt/Equity'].mean():.1f}" if pd.notna(other_peers['Debt/Equity'].mean()) else "N/A", delta=f"{main_de[0]:.1f} (You)" if len(main_de)>0 else None, delta_color="inverse")
    
    # Detailed Table
    st.markdown("#### 📋 Detailed Comparison")
    st.dataframe(peer_df.style.apply(lambda row: ['background-color: rgba(255,71,87,0.2)']*len(row) if row['Ticker']==main_ticker_clean else ['']*len(row), axis=1), use_container_width=True)


# ========== UI COMPONENTS ==========
def create_live_price_dashboard(analyzer):
    pd_data = analyzer.live_price_data
    cur = analyzer.currency_symbol
    
    cp = pd_data.get('current_price')
    pc = pd_data.get('previous_close')
    
    if cp and pc:
        change = cp - pc
        change_pct = (change/pc)*100
        color_class = "price-up" if change >= 0 else "price-down"
        arrow = "▲" if change >= 0 else "▼"
        
        st.markdown(f"""
        <div class="live-price-box">
            <div style="position: relative; z-index: 1;">
                <span class="live-indicator"></span> LIVE
                <h3 style="margin: 0.5rem 0;">{analyzer.company_name}</h3>
                <div class="{color_class}">{cur}{cp:.2f} {arrow}</div>
                <div style="font-size: 1.2rem; margin-top: 0.5rem;">{cur}{abs(change):.2f} ({change_pct:+.2f}%)</div>
                <div style="margin-top: 1rem; font-size: 0.85rem; opacity: 0.8;">Last Updated: {datetime.now().strftime('%H:%M:%S')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open", f"{cur}{pd_data.get('open', 0):.2f}")
    c2.metric("Day High", f"{cur}{pd_data.get('day_high', 0):.2f}")
    c3.metric("Day Low", f"{cur}{pd_data.get('day_low', 0):.2f}")
    c4.metric("Volume", f"{pd_data.get('volume', 0):,.0f}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("52W High", f"{cur}{pd_data.get('fifty_two_week_high', 0):.2f}")
    c2.metric("52W Low", f"{cur}{pd_data.get('fifty_two_week_low', 0):.2f}")
    c3.metric("Market Cap", analyzer._format_amount(pd_data.get('market_cap', 0)))
    c4.metric("Beta", f"{pd_data.get('beta', 0):.2f}")


def create_ratio_dashboard(ratios, currency_symbol):
    st.markdown('<div class="section-header">📊 Financial Ratios</div>', unsafe_allow_html=True)
    
    categories = {
        '📈 Valuation': {'P/E Ratio': 'P/E', 'P/B Ratio': 'P/B', 'P/S Ratio': 'P/S', 'P/FCF Ratio': 'P/FCF', 'PEG Ratio': 'PEG', 'Dividend Yield': 'Div Yield'},
        '💰 Profitability': {'Net Profit Margin': 'Net Margin', 'Gross Profit Margin': 'Gross Margin', 'Operating Margin': 'Op Margin', 'ROE': 'ROE', 'ROA': 'ROA'},
        '📊 Growth': {'Revenue Growth (YoY)': 'Rev Growth', 'Net Income Growth (YoY)': 'Earn Growth', '52-Week Return': '52W Return', 'EPS': 'EPS'},
        '🏦 Health': {'Current Ratio': 'Curr Ratio', 'Quick Ratio': 'Quick Ratio', 'Debt to Equity': 'D/E', 'Asset Turnover': 'Asset Turn'},
    }
    
    for category, metrics in categories.items():
        available_metrics = {k: v for k, v in ratios.items() if k in metrics}
        if available_metrics:
            st.markdown(f"**{category}**")
            cols = st.columns(min(len(available_metrics), 4))
            for i, (name, value) in enumerate(available_metrics.items()):
                with cols[i % 4]:
                    if isinstance(value, (int, float)):
                        if 'Ratio' in name and 'P/E' not in name and 'PEG' not in name: display = f"{value:.2f}"
                        elif 'Margin' in name or 'Growth' in name or 'Yield' in name or 'ROE' in name or 'ROA' in name or 'Return' in name: display = f"{value:.2f}%"
                        elif 'per Share' in name: display = f"{currency_symbol}{value:.2f}"
                        else: display = f"{value:.2f}"
                        
                        card_class = "valuation-card" if 'Valuation' in category else "profitability-card" if 'Profitability' in category else "growth-card" if 'Growth' in category else "metric-card"
                        
                        st.markdown(f'<div class="{card_class}"><div class="metric-value">{display}</div><div class="metric-label">{metrics[name]}</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)


def create_advanced_charts(analyzer):
    financials = analyzer.financials
    currency = analyzer.currency_symbol
    
    st.markdown('<div class="section-header">📉 Advanced Charts</div>', unsafe_allow_html=True)
    
    prices = financials.get('prices')
    if prices is not None and not prices.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3], subplot_titles=('Price & Moving Averages', 'Volume'))
        
        fig.add_trace(go.Candlestick(x=prices.index, open=prices['Open'], high=prices['High'], low=prices['Low'], close=prices['Close'], name='Price'), row=1, col=1)
        
        for ma, color, name in [(20, '#ffa500', '20 MA'), (50, '#00b4d8', '50 MA'), (200, '#ff4757', '200 MA')]:
            ma_data = prices['Close'].rolling(window=ma).mean()
            fig.add_trace(go.Scatter(x=prices.index, y=ma_data, name=name, line=dict(color=color, width=1.5)), row=1, col=1)
        
        colors = ['#00ff88' if prices['Close'].iloc[i] >= prices['Open'].iloc[i] else '#ff4757' for i in range(len(prices))]
        fig.add_trace(go.Bar(x=prices.index, y=prices['Volume'], name='Volume', marker_color=colors, opacity=0.5), row=2, col=1)
        
        fig.update_layout(height=600, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    # Returns Distribution
    if prices is not None and not prices.empty:
        returns = prices['Close'].pct_change().dropna() * 100
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=returns, nbinsx=50, name='Returns', marker_color='#667eea', opacity=0.7, histnorm='probability density'))
        
        if len(returns) > 1:
            mean_r, std_r = returns.mean(), returns.std()
            x_range = np.linspace(returns.min(), returns.max(), 100)
            y_curve = (1/(std_r * np.sqrt(2*np.pi))) * np.exp(-(x_range - mean_r)**2 / (2*std_r**2))
            fig.add_trace(go.Scatter(x=x_range, y=y_curve, name='Normal', line=dict(color='#00ff88', width=2)))
        
        fig.add_vline(x=returns.mean(), line_dash="dash", line_color="#ffa500", annotation_text=f"Mean: {returns.mean():.2f}%")
        fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean Return", f"{returns.mean():.3f}%")
        c2.metric("Volatility", f"{returns.std():.3f}%")
        c3.metric("Skewness", f"{returns.skew():.3f}")
        c4.metric("Kurtosis", f"{returns.kurtosis():.3f}")


def detect_peer_group(ticker):
    for group_name, tickers in PEER_GROUPS.items():
        if ticker in tickers:
            return group_name, tickers
    return None, []


# ========== MAIN APP ==========
def main():
    st.markdown('<h1 class="main-header">FinAnalyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Financial Analysis • Live Prices • Peer Comparison • Advanced Analytics</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🔍 Search")
        
        ticker = st.text_input("Stock Ticker", "AAPL", max_chars=50, placeholder="e.g., AAPL, RELIANCE")
        
        exchange = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"])
        exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": None, "Auto-detect": None}
        
        st.divider()
        st.markdown("### 🏢 Peer Comparison")
        use_peers = st.checkbox("Enable Peer Comparison", value=True)
        custom_peers = st.text_input("Custom Peers", placeholder="AAPL, MSFT, GOOGL")
        
        st.divider()
        auto_refresh = st.checkbox("Auto-refresh (30s)")
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
        
        st.divider()
        
        tab1, tab2 = st.tabs(["🇮🇳 India", "🇺🇸 US"])
        with tab1:
            for tick in list(INDIAN_STOCKS_DB.keys())[:12]:
                if st.button(f"{tick}", use_container_width=True, key=f"i_{tick}"):
                    st.session_state['ticker'] = tick
                    st.rerun()
        with tab2:
            for s in ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM"]:
                if st.button(s, use_container_width=True, key=f"u_{s}"):
                    st.session_state['ticker'] = s
                    st.rerun()
    
    if 'ticker' in st.session_state:
        ticker = st.session_state['ticker']
    
    if not analyze_btn and 'ticker' not in st.session_state:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2 style="color: #e2e8f0;">🚀 Welcome to FinAnalyzer Pro</h2>
            <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 1rem auto;">
                Analyze any stock worldwide with live prices, 20+ financial ratios, peer comparison, and interactive charts.
            </p>
            <p style="color: #667eea;">👈 Enter a ticker in the sidebar to get started!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    analyzer = ProFinancialAnalyzer(ticker, exchange=exchange_map.get(exchange))
    
    # Progress
    pb = st.progress(0)
    st_msg = st.empty()
    
    for i, (msg, prog) in enumerate([("Fetching live data...", 25), ("Downloading financials...", 50), ("Calculating ratios...", 75), ("Rendering...", 100)]):
        st_msg.text(msg)
        pb.progress(prog)
        if i == 0: analyzer.get_live_price()
        elif i == 1: 
            if not analyzer.fetch_financial_data():
                pb.empty(); st_msg.empty()
                st.error("Unable to fetch data.")
                return
        elif i == 2: analyzer.calculate_all_ratios()
    
    time.sleep(0.3)
    pb.empty(); st_msg.empty()
    
    # Display
    create_live_price_dashboard(analyzer)
    if auto_refresh: time.sleep(30); st.rerun()
    
    # Analyst
    if analyzer.live_price_data.get('recommendation'):
        rec = analyzer.live_price_data.get('recommendation', '').upper()
        rec_colors = {'BUY': '#00ff88', 'STRONG_BUY': '#00ff88', 'HOLD': '#ffa500', 'SELL': '#ff4757', 'STRONG_SELL': '#ff4757'}
        st.markdown(f'<div class="analyst-card" style="background-color: {rec_colors.get(rec, "#666")};">{rec.replace("_"," ")} • {analyzer.live_price_data.get("number_of_analysts","N/A")} analysts</div>', unsafe_allow_html=True)
    
    # Info
    info = analyzer.financials['info']
    st.markdown(f'<div class="info-box"><strong>{analyzer.company_name}</strong> | {analyzer.financials.get("sector","N/A")} | {analyzer.financials.get("industry","N/A")} | {analyzer.currency} ({analyzer.currency_symbol})</div>', unsafe_allow_html=True)
    
    # Ratios
    create_ratio_dashboard(analyzer.ratios, analyzer.currency_symbol)
    
    # Charts
    create_advanced_charts(analyzer)
    
    # Peer Comparison
    if use_peers:
        if custom_peers:
            peer_list = [p.strip().upper() for p in custom_peers.split(',') if p.strip()]
        else:
            group_name, peer_list = detect_peer_group(analyzer.ticker)
            if group_name:
                st.info(f"🔍 Auto-detected: **{group_name}**")
        
        peer_list = [p for p in peer_list if p != analyzer.ticker]
        all_tickers = [analyzer.ticker] + peer_list[:7]
        
        if len(all_tickers) >= 2:
            with st.spinner("Fetching peer data..."):
                peer_df = get_peer_comparison(analyzer.ticker, all_tickers)
                create_peer_comparison_charts(peer_df, analyzer.ticker, analyzer.currency_symbol)
    
    # Financial Statements
    st.markdown("---")
    st.markdown('<div class="section-header">📋 Financial Statements</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📊 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])
    
    for tab, key, name in [(t1, 'income', 'Income'), (t2, 'balance', 'Balance'), (t3, 'cashflow', 'Cash')]:
        with tab:
            df = analyzer.financials.get(key)
            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True)
                st.download_button(f"📥 Download {name} Statement", df.to_csv(), f"{analyzer.original_ticker}_{key}.csv", "text/csv")
            else:
                st.warning(f"{name} Statement not available.")
    
    st.divider()
    st.caption(f"Data: Yahoo Finance | {analyzer.currency} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()