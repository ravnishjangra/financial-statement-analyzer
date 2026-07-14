"""
Financial Statement Analyzer - Pro Version
DCF Valuation • Stock Screener • Portfolio Tracker • Technical Analysis
Live prices • Peer comparison • 20+ Ratios
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import requests
import re
import json

# Page configuration
st.set_page_config(
    page_title="FinAnalyzer Pro | Ultimate Stock Analysis",
    page_icon="📊",
    layout="wide"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem; font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 1rem;
    }
    .sub-header { font-size: 1.1rem; color: #94a3b8; text-align: center; margin-bottom: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        border: 1px solid rgba(102,126,234,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
    }
    .metric-value { font-size: 1.5rem; font-weight: bold; }
    .metric-label { font-size: 0.8rem; opacity: 0.9; margin-top: 0.3rem; }
    .valuation-card {
        background: linear-gradient(135deg, #f093fb15, #f5576c15);
        border: 1px solid rgba(240,147,251,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
    }
    .profitability-card {
        background: linear-gradient(135deg, #4facfe15, #00f2fe15);
        border: 1px solid rgba(79,172,254,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
    }
    .growth-card {
        background: linear-gradient(135deg, #43e97b15, #38f9d715);
        border: 1px solid rgba(67,233,123,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
    }
    .live-price-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        border: 1px solid rgba(102,126,234,0.3); padding: 2rem;
        border-radius: 20px; color: white; text-align: center; margin: 1rem 0;
    }
    .price-up { color: #00ff88; font-size: 3rem; font-weight: 800; }
    .price-down { color: #ff4757; font-size: 3rem; font-weight: 800; }
    .info-box {
        background: #1e293b; border: 1px solid rgba(102,126,234,0.3);
        padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0;
        border-left: 4px solid #667eea; color: #e2e8f0;
    }
    .stButton button {
        width: 100%; border-radius: 12px; padding: 0.6rem;
        font-weight: 600; font-size: 0.9rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; transition: all 0.3s ease;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102,126,234,0.4); }
    .section-header {
        font-size: 1.4rem; font-weight: 700; color: #e2e8f0;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102,126,234,0.3);
    }
    .source-badge {
        display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem;
    }
    .source-yahoo { background: #7200ff; color: white; }
    .source-google { background: #4285f4; color: white; }
    .portfolio-profit { color: #00ff88; font-weight: bold; }
    .portfolio-loss { color: #ff4757; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Constants (same as before)
CURRENCY_SYMBOLS = {
    'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
}

INDIAN_STOCKS_DB = {
    'RELIANCE': 'RELIANCE.NS', 'TCS': 'TCS.NS', 'HDFCBANK': 'HDFCBANK.NS',
    'INFY': 'INFY.NS', 'ICICIBANK': 'ICICIBANK.NS', 'ITC': 'ITC.NS',
    'WIPRO': 'WIPRO.NS', 'TATAMOTORS': 'TATAMOTORS.NS', 'SBIN': 'SBIN.NS',
    'BHARTIARTL': 'BHARTIARTL.NS', 'KOTAKBANK': 'KOTAKBANK.NS',
    'MARUTI': 'MARUTI.NS', 'SUNPHARMA': 'SUNPHARMA.NS',
    'TATASTEEL': 'TATASTEEL.NS', 'BAJFINANCE': 'BAJFINANCE.NS',
    'ADANIENT': 'ADANIENT.NS', 'NTPC': 'NTPC.NS', 'ONGC': 'ONGC.NS',
    'HCLTECH': 'HCLTECH.NS', 'ASIANPAINT': 'ASIANPAINT.NS',
    'TITAN': 'TITAN.NS', 'NESTLEIND': 'NESTLEIND.NS', 'DRREDDY': 'DRREDDY.NS',
    'CIPLA': 'CIPLA.NS', 'HINDUNILVR': 'HINDUNILVR.NS', 'BRITANNIA': 'BRITANNIA.NS',
    'TECHM': 'TECHM.NS', 'JSWSTEEL': 'JSWSTEEL.NS',
    'EICHERMOT': 'EICHERMOT.NS', 'HEROMOTOCO': 'HEROMOTOCO.NS',
    'COALINDIA': 'COALINDIA.NS', 'DIVISLAB': 'DIVISLAB.NS',
    'INDUSINDBK': 'INDUSINDBK.NS', 'BAJAJFINSV': 'BAJAJFINSV.NS',
    'AXISBANK': 'AXISBANK.NS', 'LT': 'LT.NS', 'POWERGRID': 'POWERGRID.NS',
    'ULTRACEMCO': 'ULTRACEMCO.NS', 'GRASIM': 'GRASIM.NS',
}

PEER_GROUPS = {
    'Tech_US': ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NVDA'],
    'Tech_India': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
    'Banking_India': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
    'Auto_India': ['TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
    'Pharma_India': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
    'Oil_India': ['RELIANCE.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS'],
    'Finance_US': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
}

# Screener stock list
SCREENER_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V', 'WMT',
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'WIPRO.NS',
    'TATAMOTORS.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'ASIANPAINT.NS',
    'HCLTECH.NS', 'NESTLEIND.NS', 'TITAN.NS', 'BAJFINANCE.NS',
]

# Initialize portfolio in session state
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = []


# ===== PRO ANALYZER CLASS (KEEP EXISTING) =====
class ProFinancialAnalyzer:
    def __init__(self, ticker, exchange="Auto"):
        self.original_ticker = ticker.upper().strip()
        self.ticker = self._resolve_ticker(ticker.upper().strip(), exchange)
        self.stock = None
        self.financials = {}
        self.ratios = {}
        self.live_price_data = {}
        self.currency = 'USD'
        self.currency_symbol = '$'
        self.company_name = ''
        self.data_source = 'Yahoo Finance'

    def _resolve_ticker(self, ticker, exchange):
        if exchange == "NSE":
            return ticker + '.NS' if not ticker.endswith('.NS') else ticker
        elif exchange == "BSE":
            return ticker + '.BO' if not ticker.endswith('.BO') else ticker
        elif ticker in INDIAN_STOCKS_DB:
            return INDIAN_STOCKS_DB[ticker]
        return ticker

    def get_live_price(self):
        success = self._try_yahoo()
        if not success: success = self._try_alternate_yahoo()
        if not success: success = self._try_minimal_fetch()
        return success

    def _try_yahoo(self):
        try:
            self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            if info and info.get('marketCap'):
                self._populate_from_info(info)
                self.data_source = 'Yahoo Finance'
                return True
            return False
        except: return False

    def _try_alternate_yahoo(self):
        alternates = []
        if self.ticker.endswith('.NS'): alternates = [self.ticker.replace('.NS', '.BO')]
        elif self.ticker.endswith('.BO'): alternates = [self.ticker.replace('.BO', '.NS')]
        else: alternates = [self.ticker + '.NS', self.ticker + '.BO']
        for alt in alternates:
            try:
                alt_stock = yf.Ticker(alt); alt_info = alt_stock.info
                if alt_info and alt_info.get('marketCap'):
                    self.stock = alt_stock; self.ticker = alt
                    self._populate_from_info(alt_info)
                    self.data_source = 'Yahoo Finance'; return True
            except: continue
        return False

    def _try_minimal_fetch(self):
        try:
            info = self.stock.info if self.stock else {}
            if info: self._populate_from_info(info); self.data_source = 'Yahoo Finance (limited)'; return True
        except: pass
        return False

    def _populate_from_info(self, info):
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
            'recommendation': info.get('recommendationKey'),
            'number_of_analysts': info.get('numberOfAnalystOpinions'),
        }
        self.live_price_data = {k: v for k, v in self.live_price_data.items() if v is not None}

    def fetch_financial_data(self):
        try:
            if not self.stock: self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            self.financials['info'] = info
            self.company_name = info.get('longName', self.original_ticker)
            self.financials['sector'] = info.get('sector', 'N/A')
            self.financials['industry'] = info.get('industry', 'N/A')
            self.financials['income'] = self.stock.financials
            self.financials['balance'] = self.stock.balance_sheet
            self.financials['cashflow'] = self.stock.cashflow
            end = datetime.now()
            self.financials['prices'] = self.stock.history(start=end - timedelta(days=365*3), end=end)
            self._detect_currency(); return True
        except: return True

    def _detect_currency(self):
        info = self.financials.get('info', {})
        currency = info.get('currency', 'USD')
        if self.ticker.endswith('.NS') or self.ticker.endswith('.BO'): currency = 'INR'
        self.currency = currency
        self.currency_symbol = CURRENCY_SYMBOLS.get(currency, currency + ' ')

    def _format_amount(self, value):
        if value is None or pd.isna(value): return 'N/A'
        if self.currency == 'INR':
            cr = value / 1e7
            return f"{self.currency_symbol}{cr:.0f} Cr" if abs(cr) >= 100 else f"{self.currency_symbol}{cr:.1f} Cr"
        b = value / 1e9
        return f"{self.currency_symbol}{b:.2f}B" if abs(b) >= 1 else f"{self.currency_symbol}{value/1e6:.1f}M"

    def _safe_get(self, df, keys, col=0):
        if df is None or df.empty: return None
        if isinstance(keys, str): keys = [keys]
        for key in keys:
            if key in df.index and len(df.columns) > col:
                val = df.loc[key].iloc[col]
                if pd.notna(val): return val
        return None

    def calculate_all_ratios(self):
        try:
            income = self.financials.get('income')
            balance = self.financials.get('balance')
            cashflow = self.financials.get('cashflow')
            prices = self.financials.get('prices')
            cp = self.live_price_data.get('current_price')
            info = self.financials.get('info', {})
            has_financials = income is not None and not income.empty

            if has_financials:
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

                if balance is not None and not balance.empty:
                    eq = self._safe_get(balance, ['Stockholders Equity', 'Total Stockholder Equity', 'Total Equity'])
                    ast = self._safe_get(balance, ['Total Assets'])
                    ca = self._safe_get(balance, ['Current Assets'])
                    cl = self._safe_get(balance, ['Current Liabilities'])
                    td = self._safe_get(balance, ['Total Debt']) or self._safe_get(balance, ['Long Term Debt'])
                    if eq:
                        if ni: self.ratios['ROE'] = (ni/eq)*100
                        if td: self.ratios['Debt to Equity'] = td/eq
                    if ast and ni: self.ratios['ROA'] = (ni/ast)*100
                    if ca and cl:
                        self.ratios['Current Ratio'] = ca/cl
                        inv = self._safe_get(balance, ['Inventory', 'Inventories'])
                        if inv: self.ratios['Quick Ratio'] = (ca-inv)/cl
                    if rev:
                        if ast: self.ratios['Asset Turnover'] = rev/ast
                        if eq: self.ratios['Equity Turnover'] = rev/eq

                if cp:
                    shares = self._safe_get(income, ['Diluted Average Shares']) or self._safe_get(income, ['Basic Average Shares'])
                    if shares:
                        if ni:
                            eps = ni/shares; self.ratios['EPS'] = eps
                            if eps > 0: self.ratios['P/E Ratio'] = cp/eps
                        if eq:
                            bvps = eq/shares
                            if bvps > 0: self.ratios['P/B Ratio'] = cp/bvps
                        if rev and rev/shares > 0: self.ratios['P/S Ratio'] = cp/(rev/shares)

            for key, ratio_key, multiplier in [
                ('returnOnEquity', 'ROE', 100), ('returnOnAssets', 'ROA', 100),
                ('profitMargins', 'Net Profit Margin', 100), ('debtToEquity', 'Debt to Equity', 1),
                ('trailingPE', 'P/E Ratio', 1), ('priceToBook', 'P/B Ratio', 1),
                ('trailingEps', 'EPS', 1), ('revenueGrowth', 'Revenue Growth (YoY)', 100),
                ('dividendYield', 'Dividend Yield', 100),
            ]:
                if ratio_key not in self.ratios and info.get(key):
                    try: self.ratios[ratio_key] = info[key] * multiplier
                    except: pass
            return True
        except: return True


# ===== TECHNICAL ANALYSIS =====

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices, period=20, std=2):
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    rolling_std = prices.rolling(window=period).std()
    upper_band = sma + (rolling_std * std)
    lower_band = sma - (rolling_std * std)
    return upper_band, sma, lower_band

def create_technical_analysis_dashboard(analyzer):
    """Technical Analysis Dashboard"""
    st.markdown('<div class="section-header">📈 Technical Analysis</div>', unsafe_allow_html=True)
    
    prices = analyzer.financials.get('prices')
    if prices is None or prices.empty:
        st.warning("Price data not available for technical analysis.")
        return
    
    close_prices = prices['Close']
    cur = analyzer.currency_symbol
    
    # Calculate indicators
    rsi = calculate_rsi(close_prices)
    macd_line, signal_line, histogram = calculate_macd(close_prices)
    upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(close_prices)
    
    # Current values
    current_rsi = rsi.iloc[-1]
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    
    # RSI Signal
    if current_rsi > 70: rsi_signal = "Overbought 🔴"
    elif current_rsi < 30: rsi_signal = "Oversold 🟢"
    else: rsi_signal = "Neutral 🟡"
    
    # MACD Signal
    if current_macd > current_signal: macd_signal = "Bullish 🟢"
    else: macd_signal = "Bearish 🔴"
    
    # Price vs SMA
    sma_50 = close_prices.rolling(50).mean().iloc[-1]
    sma_200 = close_prices.rolling(200).mean().iloc[-1]
    current_price = close_prices.iloc[-1]
    
    if sma_50 > sma_200: trend = "Golden Cross ✨ (Bullish)"
    elif sma_50 < sma_200: trend = "Death Cross 💀 (Bearish)"
    else: trend = "Neutral"
    
    # Display signals
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("RSI (14)", f"{current_rsi:.1f}", delta=rsi_signal)
    with col2:
        st.metric("MACD", f"{current_macd:.2f}", delta=macd_signal)
    with col3:
        st.metric("50 vs 200 MA", trend.split('(')[0].strip(), delta=trend.split('(')[1].replace(')','') if '(' in trend else "")
    with col4:
        bb_position = ((current_price - lower_bb.iloc[-1]) / (upper_bb.iloc[-1] - lower_bb.iloc[-1])) * 100
        st.metric("BB Position", f"{bb_position:.0f}%", delta="Upper zone" if bb_position > 80 else "Lower zone" if bb_position < 20 else "Middle")
    
    # RSI Chart
    st.markdown("#### 📉 RSI (Relative Strength Index)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rsi.index, y=rsi, name='RSI', line=dict(color='#667eea', width=2)))
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4757", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Oversold (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="#94a3b8")
    fig.update_layout(height=350, template='plotly_white', yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)
    
    # MACD Chart
    st.markdown("#### 📊 MACD")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=macd_line.index, y=macd_line, name='MACD', line=dict(color='#667eea', width=2)))
    fig.add_trace(go.Scatter(x=signal_line.index, y=signal_line, name='Signal', line=dict(color='#ff4757', width=1.5)))
    colors = ['#00ff88' if h >= 0 else '#ff4757' for h in histogram.iloc[-100:]]
    fig.add_trace(go.Bar(x=histogram.index[-100:], y=histogram.iloc[-100:], name='Histogram', marker_color=colors))
    fig.update_layout(height=350, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
    
    # Bollinger Bands
    st.markdown("#### 🎯 Bollinger Bands")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=upper_bb.index[-100:], y=upper_bb.iloc[-100:], name='Upper Band', line=dict(color='#94a3b8', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=middle_bb.index[-100:], y=middle_bb.iloc[-100:], name='20 MA', line=dict(color='#ffa500', width=1.5)))
    fig.add_trace(go.Scatter(x=lower_bb.index[-100:], y=lower_bb.iloc[-100:], name='Lower Band', line=dict(color='#94a3b8', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=close_prices.index[-100:], y=close_prices.iloc[-100:], name='Price', line=dict(color='#667eea', width=2)))
    fig.update_layout(height=400, template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)


# ===== STOCK SCREENER =====

def create_stock_screener():
    """Stock Screener Dashboard"""
    st.markdown('<div class="section-header">🔍 Stock Screener</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pe_max = st.number_input("Max P/E Ratio", value=30, min_value=1, max_value=100)
    with col2:
        roe_min = st.slider("Min ROE (%)", 0, 50, 15)
    with col3:
        de_max = st.number_input("Max Debt/Equity", value=2.0, min_value=0.1, max_value=10.0, step=0.1)
    with col4:
        div_min = st.slider("Min Dividend Yield (%)", 0.0, 10.0, 1.0, 0.1)
    
    if st.button("🔍 Run Screener", type="primary"):
        with st.spinner("Screening stocks..."):
            results = []
            progress_bar = st.progress(0)
            
            for i, ticker in enumerate(SCREENER_STOCKS):
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    pe = info.get('trailingPE', 999)
                    roe = (info.get('returnOnEquity', 0) or 0) * 100
                    de = info.get('debtToEquity', 999) or 999
                    dy = (info.get('dividendYield', 0) or 0) * 100
                    mcap = info.get('marketCap', 0) or 0
                    
                    if pe and pe < pe_max and roe > roe_min and de < de_max and dy > div_min:
                        is_indian = ticker.endswith('.NS') or ticker.endswith('.BO')
                        cur = '₹' if is_indian else '$'
                        mcap_disp = round(mcap / 1e7, 1) if is_indian else round(mcap / 1e9, 1)
                        mcap_unit = 'Cr' if is_indian else 'B'
                        
                        results.append({
                            'Ticker': ticker.replace('.NS', '').replace('.BO', ''),
                            'Company': info.get('longName', ticker)[:30],
                            'P/E': round(pe, 1),
                            'ROE %': round(roe, 1),
                            'D/E': round(de, 2),
                            'Div Yield %': round(dy, 2),
                            f'Market Cap ({cur}{mcap_unit})': mcap_disp,
                            'Price': info.get('currentPrice') or info.get('regularMarketPrice'),
                        })
                except: pass
                
                progress_bar.progress((i + 1) / len(SCREENER_STOCKS))
            
            progress_bar.empty()
            
            if results:
                st.success(f"Found {len(results)} stocks matching your criteria!")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.warning("No stocks match your criteria. Try relaxing the filters.")


# ===== PORTFOLIO TRACKER =====

def create_portfolio_tracker():
    """Portfolio Tracker Dashboard"""
    st.markdown('<div class="section-header">💼 Portfolio Tracker</div>', unsafe_allow_html=True)
    
    # Add stock to portfolio
    with st.expander("➕ Add Stock to Portfolio", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            add_ticker = st.text_input("Ticker", key="port_ticker")
        with col2:
            add_qty = st.number_input("Quantity", min_value=1, value=10, key="port_qty")
        with col3:
            add_price = st.number_input("Buy Price", min_value=0.01, value=100.0, key="port_price")
        
        if st.button("Add to Portfolio", type="primary"):
            st.session_state['portfolio'].append({
                'ticker': add_ticker.upper(),
                'quantity': add_qty,
                'buy_price': add_price,
                'date': datetime.now().strftime('%Y-%m-%d')
            })
            st.success(f"Added {add_ticker} to portfolio!")
            st.rerun()
    
    # Display portfolio
    if st.session_state['portfolio']:
        st.markdown("#### 📊 Your Holdings")
        
        portfolio_data = []
        total_invested = 0
        total_current = 0
        
        for i, holding in enumerate(st.session_state['portfolio']):
            try:
                ticker = holding['ticker']
                if ticker in INDIAN_STOCKS_DB:
                    ticker = INDIAN_STOCKS_DB[ticker]
                elif not ticker.endswith('.NS') and not ticker.endswith('.BO'):
                    pass
                
                stock = yf.Ticker(ticker)
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                
                qty = holding['quantity']
                buy_price = holding['buy_price']
                invested = qty * buy_price
                current_value = qty * current_price
                pnl = current_value - invested
                pnl_pct = (pnl / invested) * 100 if invested > 0 else 0
                
                total_invested += invested
                total_current += current_value
                
                portfolio_data.append({
                    '#': i + 1,
                    'Ticker': holding['ticker'],
                    'Qty': qty,
                    'Buy Price': f"₹{buy_price:.2f}" if '.NS' in ticker else f"${buy_price:.2f}",
                    'Current': f"₹{current_price:.2f}" if '.NS' in ticker else f"${current_price:.2f}",
                    'Invested': f"₹{invested:,.0f}" if '.NS' in ticker else f"${invested:,.0f}",
                    'Current Value': f"₹{current_value:,.0f}" if '.NS' in ticker else f"${current_value:,.0f}",
                    'P&L': pnl,
                    'P&L %': pnl_pct,
                })
            except:
                portfolio_data.append({
                    '#': i + 1, 'Ticker': holding['ticker'], 'Qty': holding['quantity'],
                    'Buy Price': f"${holding['buy_price']:.2f}", 'Current': 'N/A',
                    'Invested': 'N/A', 'Current Value': 'N/A', 'P&L': 0, 'P&L %': 0,
                })
        
        if portfolio_data:
            df = pd.DataFrame(portfolio_data)
            
            # Color P&L
            def color_pnl(val):
                if isinstance(val, (int, float)):
                    return 'color: #00ff88' if val > 0 else 'color: #ff4757' if val < 0 else ''
                return ''
            
            st.dataframe(df.style.applymap(color_pnl, subset=['P&L', 'P&L %']), use_container_width=True)
            
            # Summary
            total_pnl = total_current - total_invested
            total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invested", f"${total_invested:,.0f}")
            col2.metric("Current Value", f"${total_current:,.0f}")
            col3.metric("Total P&L", f"${total_pnl:,.0f}", delta=f"{total_pnl_pct:.1f}%")
            col4.metric("Holdings", f"{len(st.session_state['portfolio'])}")
            
            # Diversification Pie Chart
            if len(st.session_state['portfolio']) > 1:
                st.markdown("#### 🎯 Portfolio Diversification")
                tickers = [h['ticker'] for h in st.session_state['portfolio']]
                values = [h['quantity'] * (yf.Ticker(INDIAN_STOCKS_DB.get(h['ticker'], h['ticker'])).info.get('currentPrice', h['buy_price']) or h['buy_price']) for h in st.session_state['portfolio']]
                
                fig = go.Figure(data=[go.Pie(labels=tickers, values=values, hole=0.4)])
                fig.update_layout(height=400, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
            
            # Clear portfolio button
            if st.button("🗑️ Clear Portfolio", type="secondary"):
                st.session_state['portfolio'] = []
                st.rerun()
    else:
        st.info("Your portfolio is empty. Add stocks using the expander above!")


# ===== DCF (KEEP EXISTING) =====
class DCFValuation:
    def __init__(self, free_cashflow, shares_outstanding, current_price, revenue_growth=0.10, beta=1.0, risk_free_rate=0.07, market_return=0.12):
        self.fcf = free_cashflow; self.shares = shares_outstanding; self.current_price = current_price
        self.revenue_growth = revenue_growth; self.beta = beta
        self.risk_free_rate = risk_free_rate; self.market_return = market_return
        self.wacc = self.calculate_wacc()
        
    def calculate_wacc(self):
        cost_of_equity = self.risk_free_rate + self.beta * (self.market_return - self.risk_free_rate)
        cost_of_debt = self.risk_free_rate + 0.02
        return (0.70 * cost_of_equity) + (0.30 * cost_of_debt * (1 - 0.25))
    
    def project_cashflows(self, years=5):
        projections = []
        growth_rates = [self.revenue_growth * (1 - i*0.1) for i in range(years)]
        fcf = self.fcf
        for i, growth in enumerate(growth_rates, 1):
            fcf = fcf * (1 + growth)
            projections.append({'year': i, 'growth_rate': f"{growth*100:.1f}%", 'fcf': fcf, 'pv_fcf': fcf / (1 + self.wacc)**i})
        return projections
    
    def calculate_intrinsic_value(self):
        projections = self.project_cashflows(5)
        pv_fcfs = sum(p['pv_fcf'] for p in projections)
        last_fcf = projections[-1]['fcf']
        terminal_value = last_fcf * 1.03 / (self.wacc - 0.03)
        pv_terminal = terminal_value / (1 + self.wacc)**5
        enterprise_value = pv_fcfs + pv_terminal
        equity_value = enterprise_value
        intrinsic_value = equity_value / self.shares if self.shares > 0 else 0
        mos = ((intrinsic_value - self.current_price) / intrinsic_value) * 100 if self.current_price > 0 else 0
        return {'intrinsic_value': intrinsic_value, 'current_price': self.current_price, 'margin_of_safety': mos,
                'pv_fcfs': pv_fcfs, 'terminal_value': terminal_value, 'pv_terminal': pv_terminal,
                'wacc': self.wacc, 'projections': projections}
    
    def get_recommendation(self):
        mos = self.calculate_intrinsic_value()['margin_of_safety']
        if mos > 25: return "STRONG BUY 🟢", "#00ff88", f"Undervalued by {mos:.1f}%"
        elif mos > 10: return "BUY 🟢", "#88ff00", f"Undervalued by {mos:.1f}%"
        elif mos > -10: return "HOLD 🟡", "#ffa500", f"Fairly valued ({mos:.1f}%)"
        elif mos > -25: return "SELL 🔴", "#ff4757", f"Overvalued by {abs(mos):.1f}%"
        else: return "STRONG SELL 🔴", "#ff0000", f"Overvalued by {abs(mos):.1f}%"


def create_dcf_dashboard(analyzer):
    st.markdown('<div class="section-header">💰 DCF Valuation</div>', unsafe_allow_html=True)
    info = analyzer.financials.get('info', {})
    income = analyzer.financials.get('income')
    cashflow = analyzer.financials.get('cashflow')
    current_price = analyzer.live_price_data.get('current_price')
    if not current_price: st.warning("Price not available."); return
    
    fcf = None
    if cashflow is not None and not cashflow.empty:
        fcf = analyzer._safe_get(cashflow, ['Free Cash Flow'])
    if not fcf:
        ni = analyzer._safe_get(income, ['Net Income']) if income is not None else None
        fcf = ni * 0.8 if ni else 0
    if not fcf or fcf <= 0: st.warning("FCF not available."); return
    
    shares = None
    if income is not None and not income.empty:
        shares = analyzer._safe_get(income, ['Diluted Average Shares']) or analyzer._safe_get(income, ['Basic Average Shares'])
    if not shares: shares = analyzer.live_price_data.get('market_cap', 0) / current_price if current_price > 0 else 1e6
    
    rg = analyzer.ratios.get('Revenue Growth (YoY)', 10)
    rg = max(0.01, min((rg or 10) / 100, 0.30))
    beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
    rf = 0.072 if analyzer.currency == 'INR' else 0.045
    mr = 0.12 if analyzer.currency == 'INR' else 0.10
    
    dcf = DCFValuation(fcf, shares, current_price, rg, beta, rf, mr)
    result = dcf.calculate_intrinsic_value()
    recommendation, rec_color, rec_reason = dcf.get_recommendation()
    cur = analyzer.currency_symbol
    
    st.markdown(f'<div style="background-color:{rec_color};padding:1.5rem;border-radius:15px;color:white;text-align:center;margin:1rem 0;"><h2>{recommendation}</h2><p>{rec_reason}</p></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Intrinsic Value", f"{cur}{result['intrinsic_value']:.2f}")
    c2.metric("Current Price", f"{cur}{result['current_price']:.2f}")
    c3.metric("Margin of Safety", f"{result['margin_of_safety']:.1f}%")
    c4.metric("WACC", f"{result['wacc']*100:.1f}%")
    st.caption("⚠️ Simplified DCF for educational purposes.")


# ===== FORMATTING & PEER COMPARISON (KEEP EXISTING) =====
def format_financial_number(value, symbol, currency):
    if pd.isna(value) or value is None: return 'N/A'
    try:
        value = float(value); sign = '-' if value < 0 else ''; abs_val = abs(value)
        if currency == 'INR':
            if abs_val >= 1e7: return f"{sign}{symbol}{abs_val/1e7:,.2f} Cr"
            elif abs_val >= 1e5: return f"{sign}{symbol}{abs_val/1e5:,.2f} L"
            else: return f"{sign}{symbol}{abs_val:,.0f}"
        else:
            if abs_val >= 1e9: return f"{sign}{symbol}{abs_val/1e9:,.2f}B"
            elif abs_val >= 1e6: return f"{sign}{symbol}{abs_val/1e6:,.2f}M"
            else: return f"{sign}{symbol}{abs_val:,.0f}"
    except: return str(value)

def format_financial_df(df, currency_symbol, currency):
    if df is None or df.empty: return None
    formatted_df = df.copy()
    for col in formatted_df.columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: format_financial_number(x, currency_symbol, currency))
    return formatted_df

def get_peer_comparison(main_ticker, peer_tickers):
    peer_data = []
    for ticker in peer_tickers:
        try:
            stock = yf.Ticker(ticker); info = stock.info
            if not info: continue
            is_indian = ticker.endswith('.NS') or ticker.endswith('.BO')
            p_currency = 'INR' if is_indian else 'USD'
            mcap = info.get('marketCap', 0) or 0
            mcap_display = round(mcap / 1e7, 2) if p_currency == 'INR' else round(mcap / 1e9, 2)
            mcap_label = 'Market Cap (₹ Cr)' if p_currency == 'INR' else 'Market Cap ($ B)'
            peer_data.append({
                'Ticker': ticker.replace('.NS', '').replace('.BO', ''),
                'Company': info.get('longName', ticker)[:25], mcap_label: mcap_display,
                'P/E Ratio': round(info['trailingPE'], 2) if info.get('trailingPE') else None,
                'P/B Ratio': round(info['priceToBook'], 2) if info.get('priceToBook') else None,
                'Revenue Growth': round(info['revenueGrowth']*100, 2) if info.get('revenueGrowth') else None,
                'ROE': round(info['returnOnEquity']*100, 2) if info.get('returnOnEquity') else None,
                'Debt/Equity': round(info['debtToEquity'], 2) if info.get('debtToEquity') else None,
                'Current Price': info.get('currentPrice') or info.get('regularMarketPrice'),
            })
        except: continue
    return pd.DataFrame(peer_data)

def safe_mean(series):
    valid = series.dropna(); return valid.mean() if len(valid) > 0 else None

def create_peer_comparison_charts(peer_df, main_ticker_name, currency_symbol, currency):
    st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
    if peer_df.empty or len(peer_df) < 2: st.warning("Not enough peer data."); return
    main_clean = main_ticker_name.replace('.NS', '').replace('.BO', '')
    mcap_col = [c for c in peer_df.columns if 'Market Cap' in c][0]
    st.markdown("#### 📊 Market Cap")
    sorted_df = peer_df.sort_values(mcap_col, ascending=True)
    colors = ['#ff4757' if t == main_clean else '#667eea' for t in sorted_df['Ticker']]
    unit, sign = ('Cr', '₹') if '₹' in mcap_col else ('B', '$')
    fig = go.Figure()
    fig.add_trace(go.Bar(y=sorted_df['Ticker'], x=sorted_df[mcap_col], orientation='h', marker_color=colors,
                         text=[f"{sign}{v:.1f}{unit}" if pd.notna(v) and v>0 else 'N/A' for v in sorted_df[mcap_col]], textposition='outside'))
    fig.update_layout(height=400, template='plotly_white', showlegend=False, margin=dict(l=100))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### 📊 Summary")
    other = peer_df[peer_df['Ticker'] != main_clean]
    c1, c2, c3, c4 = st.columns(4)
    mp = peer_df[peer_df['Ticker']==main_clean]['P/E Ratio'].values
    c1.metric("Avg Peer P/E", f"{safe_mean(other['P/E Ratio']):.1f}" if safe_mean(other['P/E Ratio']) else "N/A", delta=f"{mp[0]:.1f}" if len(mp)>0 and pd.notna(mp[0]) else None)
    mr = peer_df[peer_df['Ticker']==main_clean]['ROE'].values
    c2.metric("Avg Peer ROE", f"{safe_mean(other['ROE']):.1f}%" if safe_mean(other['ROE']) else "N/A", delta=f"{mr[0]:.1f}%" if len(mr)>0 and pd.notna(mr[0]) else None)
    mg = peer_df[peer_df['Ticker']==main_clean]['Revenue Growth'].values
    c3.metric("Avg Peer Growth", f"{safe_mean(other['Revenue Growth']):.1f}%" if safe_mean(other['Revenue Growth']) else "N/A", delta=f"{mg[0]:.1f}%" if len(mg)>0 and pd.notna(mg[0]) else None)
    md = peer_df[peer_df['Ticker']==main_clean]['Debt/Equity'].values
    c4.metric("Avg Peer D/E", f"{safe_mean(other['Debt/Equity']):.1f}" if safe_mean(other['Debt/Equity']) else "N/A", delta=f"{md[0]:.1f}" if len(md)>0 and pd.notna(md[0]) else None, delta_color="inverse")


# ===== DASHBOARD FUNCTIONS =====
def create_live_price_dashboard(analyzer):
    pd_data = analyzer.live_price_data; cur = analyzer.currency_symbol
    source_class = "source-yahoo" if "Yahoo" in analyzer.data_source else "source-fallback"
    cp = pd_data.get('current_price'); pc = pd_data.get('previous_close')
    if cp and pc:
        change = cp - pc; change_pct = (change/pc)*100
        color = "price-up" if change >= 0 else "price-down"; arrow = "▲" if change >= 0 else "▼"
        st.markdown(f'<div class="live-price-box"><h3>{analyzer.company_name}<span class="source-badge {source_class}">{analyzer.data_source}</span></h3><div class="{color}">{cur}{cp:.2f} {arrow}</div><div style="font-size:1.2rem;margin-top:0.5rem;">{cur}{abs(change):.2f} ({change_pct:+.2f}%)</div></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open", f"{cur}{pd_data.get('open', 0):.2f}" if pd_data.get('open') else "N/A")
    c2.metric("Day High", f"{cur}{pd_data.get('day_high', 0):.2f}" if pd_data.get('day_high') else "N/A")
    c3.metric("Day Low", f"{cur}{pd_data.get('day_low', 0):.2f}" if pd_data.get('day_low') else "N/A")
    c4.metric("Volume", f"{pd_data.get('volume', 0):,.0f}" if pd_data.get('volume') else "N/A")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("52W High", f"{cur}{pd_data.get('fifty_two_week_high', 0):.2f}" if pd_data.get('fifty_two_week_high') else "N/A")
    c2.metric("52W Low", f"{cur}{pd_data.get('fifty_two_week_low', 0):.2f}" if pd_data.get('fifty_two_week_low') else "N/A")
    c3.metric("Market Cap", analyzer._format_amount(pd_data.get('market_cap', 0)))
    c4.metric("Beta", f"{pd_data.get('beta', 0):.2f}" if pd_data.get('beta') else "N/A")

def create_ratio_dashboard(ratios, currency_symbol):
    st.markdown('<div class="section-header">📊 Financial Ratios</div>', unsafe_allow_html=True)
    if not ratios: st.warning("No ratios available."); return
    categories = {
        '📈 Valuation': {'P/E Ratio': 'P/E', 'P/B Ratio': 'P/B', 'P/S Ratio': 'P/S', 'PEG Ratio': 'PEG', 'Dividend Yield': 'Div Yield'},
        '💰 Profitability': {'Net Profit Margin': 'Net Margin', 'Gross Profit Margin': 'Gross Margin', 'Operating Margin': 'Op Margin', 'ROE': 'ROE', 'ROA': 'ROA'},
        '📊 Growth': {'Revenue Growth (YoY)': 'Rev Growth', 'Net Income Growth (YoY)': 'Earn Growth', '52-Week Return': '52W Return', 'EPS': 'EPS'},
        '🏦 Health': {'Current Ratio': 'Curr Ratio', 'Quick Ratio': 'Quick Ratio', 'Debt to Equity': 'D/E', 'Asset Turnover': 'Asset Turn'},
    }
    for category, metrics in categories.items():
        available = {k: v for k, v in ratios.items() if k in metrics}
        if available:
            st.markdown(f"**{category}**"); cols = st.columns(min(len(available), 4))
            for i, (name, value) in enumerate(available.items()):
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
    prices = analyzer.financials.get('prices')
    if prices is not None and not prices.empty:
        st.markdown('<div class="section-header">📉 Price Charts</div>', unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=prices.index, open=prices['Open'], high=prices['High'], low=prices['Low'], close=prices['Close'], name='Price'), row=1, col=1)
        for ma, color, name in [(20, '#ffa500', '20 MA'), (50, '#00b4d8', '50 MA'), (200, '#ff4757', '200 MA')]:
            fig.add_trace(go.Scatter(x=prices.index, y=prices['Close'].rolling(window=ma).mean(), name=name, line=dict(color=color, width=1.5)), row=1, col=1)
        vol_colors = ['#00ff88' if prices['Close'].iloc[i] >= prices['Open'].iloc[i] else '#ff4757' for i in range(len(prices))]
        fig.add_trace(go.Bar(x=prices.index, y=prices['Volume'], name='Volume', marker_color=vol_colors, opacity=0.5), row=2, col=1)
        fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

def detect_peer_group(ticker):
    for group_name, tickers in PEER_GROUPS.items():
        if ticker in tickers: return group_name, tickers
    return None, []


# ===== MAIN APP WITH TABS =====
def main():
    st.markdown('<h1 class="main-header">📊 FinAnalyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">DCF • Screener • Portfolio • Technical Analysis • Peer Comparison</p>', unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Stock Analysis", "🔎 Stock Screener", "💼 Portfolio Tracker", "📈 Technical Analysis"])
    
    # ===== TAB 1: STOCK ANALYSIS =====
    with tab1:
        if 'current_ticker' not in st.session_state:
            st.session_state['current_ticker'] = "AAPL"
        if 'current_exchange' not in st.session_state:
            st.session_state['current_exchange'] = "Auto-detect"
        if 'analyze_clicked' not in st.session_state:
            st.session_state['analyze_clicked'] = False

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ticker = st.text_input("Stock Ticker:", value=st.session_state['current_ticker'], max_chars=50, key="main_ticker")
        with col2:
            exchange = st.selectbox("Exchange:", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"],
                                    index=["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"].index(st.session_state['current_exchange']), key="main_exchange")
        with col3:
            st.write("")  # spacer
            st.write("")
            analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True, key="main_analyze")

        # Quick access
        with st.expander("📋 Quick Access"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Indian Stocks**")
                cols = st.columns(4)
                indian_list = list(INDIAN_STOCKS_DB.keys())[:12]
                for i, tick in enumerate(indian_list):
                    with cols[i % 4]:
                        if st.button(tick, use_container_width=True, key=f"q_i_{tick}"):
                            st.session_state['current_ticker'] = tick
                            st.session_state['current_exchange'] = "NSE India (.NS)"
                            st.session_state['analyze_clicked'] = True
                            st.rerun()
            with c2:
                st.markdown("**US Stocks**")
                cols = st.columns(4)
                for i, s in enumerate(["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM"]):
                    with cols[i % 4]:
                        if st.button(s, use_container_width=True, key=f"q_u_{s}"):
                            st.session_state['current_ticker'] = s
                            st.session_state['current_exchange'] = "US Market"
                            st.session_state['analyze_clicked'] = True
                            st.rerun()

        st.session_state['current_ticker'] = ticker
        st.session_state['current_exchange'] = exchange
        if analyze_btn:
            st.session_state['analyze_clicked'] = True

        if not st.session_state['analyze_clicked']:
            st.markdown("""
            <div style="text-align:center;padding:3rem;">
                <h2>🚀 Welcome to FinAnalyzer Pro</h2>
                <p style="font-size:1.1rem;color:#94a3b8;">The ultimate stock analysis toolkit</p>
            </div>
            """, unsafe_allow_html=True)
            return

        exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
        selected_exchange = exchange_map.get(st.session_state['current_exchange'], "Auto")
        analyzer = ProFinancialAnalyzer(st.session_state['current_ticker'], exchange=selected_exchange)

        with st.spinner("🔍 Analyzing..."):
            analyzer.get_live_price()
            analyzer.fetch_financial_data()
            analyzer.calculate_all_ratios()

        create_live_price_dashboard(analyzer)
        st.markdown(f'<div class="info-box"><strong>{analyzer.company_name}</strong> | {analyzer.currency} ({analyzer.currency_symbol}) | <span class="source-badge source-yahoo">{analyzer.data_source}</span></div>', unsafe_allow_html=True)
        create_ratio_dashboard(analyzer.ratios, analyzer.currency_symbol)
        create_advanced_charts(analyzer)
        create_dcf_dashboard(analyzer)

        # Peer comparison
        group_name, peer_list = detect_peer_group(analyzer.ticker)
        if peer_list:
            peer_list = [p for p in peer_list if p != analyzer.ticker]
            all_tickers = [analyzer.ticker] + peer_list[:7]
            if len(all_tickers) >= 2:
                with st.spinner("Fetching peer data..."):
                    peer_df = get_peer_comparison(analyzer.ticker, all_tickers)
                    if not peer_df.empty:
                        create_peer_comparison_charts(peer_df, analyzer.ticker, analyzer.currency_symbol, analyzer.currency)

        # Financial Statements
        st.markdown('<div class="section-header">📋 Financial Statements</div>', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
        for tab, key, name in [(t1, 'income', 'Income'), (t2, 'balance', 'Balance'), (t3, 'cashflow', 'Cash')]:
            with tab:
                df = analyzer.financials.get(key)
                if df is not None and not df.empty:
                    formatted = format_financial_df(df, analyzer.currency_symbol, analyzer.currency)
                    if formatted is not None: st.dataframe(formatted, use_container_width=True)
                    with st.expander("📥 Download CSV"):
                        st.download_button(f"Download {name}", df.to_csv(), f"{analyzer.original_ticker}_{key}.csv", "text/csv")
                else:
                    st.info(f"{name} statement not available.")

    # ===== TAB 2: STOCK SCREENER =====
    with tab2:
        create_stock_screener()

    # ===== TAB 3: PORTFOLIO TRACKER =====
    with tab3:
        create_portfolio_tracker()

    # ===== TAB 4: TECHNICAL ANALYSIS =====
    with tab4:
        st.markdown("### 📈 Technical Analysis")
        tech_ticker = st.text_input("Enter Ticker for TA:", "AAPL", key="tech_ticker")
        tech_exchange = st.selectbox("Exchange:", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"], key="tech_exchange")
        
        if st.button("🔍 Run Technical Analysis", type="primary"):
            exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            ta_analyzer = ProFinancialAnalyzer(tech_ticker, exchange=exchange_map.get(tech_exchange, "Auto"))
            with st.spinner("Calculating indicators..."):
                ta_analyzer.get_live_price()
                ta_analyzer.fetch_financial_data()
            create_technical_analysis_dashboard(ta_analyzer)

    st.divider()
    st.caption(f"FinAnalyzer Pro | Data: Yahoo Finance | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()