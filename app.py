"""
Financial Statement Analyzer - Pro Version
Live prices, valuation ratios, peer comparison, and comprehensive financial analysis
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
            
            # Try NSE if data is sparse
            if (not info or len(info) < 5) and not self.ticker.endswith('.NS'):
                alt_ticker = self.ticker + '.NS'
                self.stock = yf.Ticker(alt_ticker)
                self.ticker = alt_ticker
                info = self.stock.info
            
            self.financials['info'] = info
            self.company_name = info.get('longName', self.original_ticker)
            self.financials['sector'] = info.get('sector', 'N/A')
            self.financials['industry'] = info.get('industry', 'N/A')
            
            # Fetch financial statements
            self.financials['income'] = self.stock.financials
            self.financials['balance'] = self.stock.balance_sheet
            self.financials['cashflow'] = self.stock.cashflow
            
            # Get historical prices
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
            
            if income is None or income.empty:
                return False
            
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
            
            if balance is not None and not balance.empty:
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
                
                if rev:
                    if ast: self.ratios['Asset Turnover'] = rev/ast
                    if eq: self.ratios['Equity Turnover'] = rev/eq
            
            if cashflow is not None and not cashflow.empty:
                fcf = self._safe_get(cashflow, ['Free Cash Flow'])
                if fcf and ni: self.ratios['FCF to Net Income'] = fcf/ni
            
            if cp:
                shares = self._safe_get(income, ['Diluted Average Shares', 'Diluted Shares Outstanding']) or self._safe_get(income, ['Basic Average Shares', 'Basic Shares Outstanding'])
                if shares:
                    if ni:
                        eps = ni/shares; self.ratios['EPS'] = eps
                        if eps > 0: self.ratios['P/E Ratio'] = cp/eps
                    if 'eq' in dir() and eq:
                        bvps = eq/shares
                        if bvps > 0: self.ratios['P/B Ratio'] = cp/bvps
                    if rev and rev/shares > 0: self.ratios['P/S Ratio'] = cp/(rev/shares)
                    if 'fcf' in dir() and fcf and fcf/shares > 0: self.ratios['P/FCF Ratio'] = cp/(fcf/shares)
                    if cashflow is not None and not cashflow.empty:
                        div = self._safe_get(cashflow, ['Dividends Paid'])
                        if div and cp > 0: self.ratios['Dividend Yield'] = (abs(div)/shares/cp)*100
                
                eg = self.ratios.get('Net Income Growth (YoY)')
                pe = self.ratios.get('P/E Ratio')
                if eg and pe and eg > 0: self.ratios['PEG Ratio'] = pe/eg
            
            if prices is not None and not prices.empty and len(prices) >= 252:
                self.ratios['52-Week Return'] = ((prices['Close'].iloc[-1]-prices['Close'].iloc[-252])/prices['Close'].iloc[-252])*100
            
            return True
        except Exception as e:
            st.error(f"Error calculating ratios: {str(e)}")
            return False


# ===== FORMATTING HELPERS =====

def format_financial_number(value, symbol, currency):
    if pd.isna(value) or value is None: return 'N/A'
    try:
        value = float(value)
        abs_val = abs(value)
        sign = '-' if value < 0 else ''
        if currency == 'INR':
            if abs_val >= 1e7: return f"{sign}{symbol}{abs_val/1e7:,.2f} Cr"
            elif abs_val >= 1e5: return f"{sign}{symbol}{abs_val/1e5:,.2f} L"
            elif abs_val >= 1e3: return f"{sign}{symbol}{abs_val/1e3:,.0f}K"
            else: return f"{sign}{symbol}{abs_val:,.0f}"
        else:
            if abs_val >= 1e9: return f"{sign}{symbol}{abs_val/1e9:,.2f}B"
            elif abs_val >= 1e6: return f"{sign}{symbol}{abs_val/1e6:,.2f}M"
            elif abs_val >= 1e3: return f"{sign}{symbol}{abs_val/1e3:,.0f}K"
            else: return f"{sign}{symbol}{abs_val:,.0f}"
    except:
        return str(value)


def format_financial_df(df, currency_symbol, currency):
    if df is None or df.empty: return None
    formatted_df = df.copy()
    for col in formatted_df.columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: format_financial_number(x, currency_symbol, currency))
    return formatted_df


# ===== PEER COMPARISON =====

def get_peer_comparison(main_ticker, peer_tickers):
    peer_data = []
    for ticker in peer_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info: continue
            
            is_indian = ticker.endswith('.NS') or ticker.endswith('.BO')
            peer_currency = 'INR' if is_indian else info.get('currency', 'USD')
            market_cap = info.get('marketCap', 0) or 0
            
            if peer_currency == 'INR':
                mcap_display = round(market_cap / 1e7, 2)
                mcap_label = 'Market Cap (₹ Cr)'
            else:
                mcap_display = round(market_cap / 1e9, 2)
                mcap_label = 'Market Cap ($ B)'
            
            pe = info.get('trailingPE')
            fpe = info.get('forwardPE')
            pb = info.get('priceToBook')
            rg = info.get('revenueGrowth')
            pm = info.get('profitMargins')
            roe = info.get('returnOnEquity')
            de = info.get('debtToEquity')
            dy = info.get('dividendYield')
            
            peer_data.append({
                'Ticker': ticker.replace('.NS', '').replace('.BO', ''),
                'Company': info.get('longName', ticker)[:25],
                mcap_label: mcap_display,
                'P/E Ratio': round(pe, 2) if pe else None,
                'Forward P/E': round(fpe, 2) if fpe else None,
                'P/B Ratio': round(pb, 2) if pb else None,
                'Revenue Growth': round(rg*100, 2) if rg else None,
                'Profit Margin': round(pm*100, 2) if pm else None,
                'ROE': round(roe*100, 2) if roe else None,
                'Debt/Equity': round(de, 2) if de else None,
                'Dividend Yield': round(dy*100, 2) if dy else None,
                'Current Price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'Recommendation': info.get('recommendationKey', 'N/A'),
            })
        except:
            continue
    return pd.DataFrame(peer_data)


def safe_mean(series):
    """Calculate mean safely"""
    valid = series.dropna()
    return valid.mean() if len(valid) > 0 else None


def create_peer_comparison_charts(peer_df, main_ticker_name, currency_symbol, currency):
    st.markdown("---")
    st.markdown("## 🏢 Peer Comparison")
    
    if peer_df.empty or len(peer_df) < 2:
        st.warning("Not enough peer data available for comparison.")
        return
    
    main_ticker_clean = main_ticker_name.replace('.NS', '').replace('.BO', '')
    
    mcap_col = [col for col in peer_df.columns if 'Market Cap' in col]
    mcap_col = mcap_col[0] if mcap_col else 'Market Cap ($ B)'
    
    # Market Cap Chart
    st.markdown("### 📊 Market Capitalization Comparison")
    sorted_df = peer_df.sort_values(mcap_col, ascending=True)
    colors = ['#ff4444' if t == main_ticker_clean else '#1f77b4' for t in sorted_df['Ticker']]
    
    if '₹' in mcap_col or 'Cr' in mcap_col:
        unit, curr_sign = 'Cr', '₹'
    else:
        unit, curr_sign = 'B', '$'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sorted_df['Ticker'], x=sorted_df[mcap_col],
        orientation='h', marker_color=colors,
        text=[f"{curr_sign}{v:.1f}{unit}" if pd.notna(v) and v > 0 else 'N/A' for v in sorted_df[mcap_col]],
        textposition='outside'
    ))
    fig.update_layout(title=f'Market Cap ({mcap_col})', height=400, template='plotly_white', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Metrics
    st.markdown("### 📈 Key Metrics Comparison")
    metrics_to_plot = ['P/E Ratio', 'P/B Ratio', 'Revenue Growth', 'ROE']
    available = [m for m in metrics_to_plot if m in peer_df.columns and peer_df[m].notna().any()]
    
    if available:
        fig = make_subplots(rows=2, cols=2, subplot_titles=available[:4], vertical_spacing=0.15)
        positions = [(1,1), (1,2), (2,1), (2,2)]
        for i, metric in enumerate(available[:4]):
            row, col = positions[i]
            valid = peer_df[peer_df[metric].notna()]
            colors = ['#ff4444' if t == main_ticker_clean else '#1f77b4' for t in valid['Ticker']]
            fig.add_trace(go.Bar(x=valid['Ticker'], y=valid[metric], marker_color=colors, text=[f"{v:.1f}" if pd.notna(v) else 'N/A' for v in valid[metric]], textposition='outside'), row=row, col=col)
        fig.update_layout(height=600, template='plotly_white', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Table
    st.markdown("### 📋 Detailed Comparison")
    def highlight_main(row):
        return ['background-color: #fff3cd'] * len(row) if row['Ticker'] == main_ticker_clean else [''] * len(row)
    display_df = peer_df.copy()
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'int64']:
            display_df[col] = display_df[col].apply(lambda x: round(x, 2) if pd.notna(x) else x)
    st.dataframe(display_df.style.apply(highlight_main, axis=1), use_container_width=True, height=400)
    
    # Summary Stats
    st.markdown("### 📊 Peer Group Summary")
    other = peer_df[peer_df['Ticker'] != main_ticker_clean]
    
    c1, c2, c3, c4 = st.columns(4)
    
    main_pe = peer_df[peer_df['Ticker'] == main_ticker_clean]['P/E Ratio'].values
    avg_pe = safe_mean(other['P/E Ratio'])
    c1.metric("Avg Peer P/E", f"{avg_pe:.1f}" if avg_pe else "N/A", delta=f"{main_pe[0]:.1f} (You)" if len(main_pe)>0 and pd.notna(main_pe[0]) else None)
    
    main_roe = peer_df[peer_df['Ticker'] == main_ticker_clean]['ROE'].values
    avg_roe = safe_mean(other['ROE'])
    c2.metric("Avg Peer ROE", f"{avg_roe:.1f}%" if avg_roe else "N/A", delta=f"{main_roe[0]:.1f}% (You)" if len(main_roe)>0 and pd.notna(main_roe[0]) else None)
    
    main_growth = peer_df[peer_df['Ticker'] == main_ticker_clean]['Revenue Growth'].values
    avg_growth = safe_mean(other['Revenue Growth'])
    c3.metric("Avg Peer Growth", f"{avg_growth:.1f}%" if avg_growth else "N/A", delta=f"{main_growth[0]:.1f}% (You)" if len(main_growth)>0 and pd.notna(main_growth[0]) else None)
    
    main_de = peer_df[peer_df['Ticker'] == main_ticker_clean]['Debt/Equity'].values
    avg_de = safe_mean(other['Debt/Equity'])
    c4.metric("Avg Peer D/E", f"{avg_de:.1f}" if avg_de else "N/A", delta=f"{main_de[0]:.1f} (You)" if len(main_de)>0 and pd.notna(main_de[0]) else None, delta_color="inverse")
    
    # Recommendations
    st.markdown("### 🎯 Analyst Recommendations")
    rec_counts = peer_df['Recommendation'].value_counts()
    if len(rec_counts) > 0:
        fig = go.Figure(data=[go.Pie(labels=rec_counts.index, values=rec_counts.values, hole=0.4, marker_colors=['#00ff88', '#88ff00', '#ffa500', '#ff4444', '#ff0000'])])
        fig.update_layout(height=350, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)


# ===== DASHBOARD COMPONENTS =====

def create_live_price_dashboard(analyzer):
    pd_data = analyzer.live_price_data
    cur = analyzer.currency_symbol
    
    st.markdown("### 🟢 Live Market Data")
    
    cp = pd_data.get('current_price')
    pc = pd_data.get('previous_close')
    
    if cp and pc:
        change = cp - pc
        change_pct = (change/pc)*100
        color = "price-up" if change >= 0 else "price-down"
        arrow = "▲" if change >= 0 else "▼"
        st.markdown(f'<div class="live-price-box"><h3>{analyzer.company_name}</h3><div class="{color}">{cur}{cp:.2f} {arrow}</div><div style="font-size:1.2rem;margin-top:0.5rem;">{cur}{abs(change):.2f} ({change_pct:+.2f}%)</div></div>', unsafe_allow_html=True)
    
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
    st.markdown("### 📊 Financial Ratios Dashboard")
    categories = {
        '📈 Valuation': {'P/E Ratio': 'P/E', 'P/B Ratio': 'P/B', 'P/S Ratio': 'P/S', 'P/FCF Ratio': 'P/FCF', 'PEG Ratio': 'PEG', 'Dividend Yield': 'Div Yield'},
        '💰 Profitability': {'Net Profit Margin': 'Net Margin', 'Gross Profit Margin': 'Gross Margin', 'Operating Margin': 'Op Margin', 'ROE': 'ROE', 'ROA': 'ROA'},
        '📊 Growth': {'Revenue Growth (YoY)': 'Rev Growth', 'Net Income Growth (YoY)': 'Earn Growth', '52-Week Return': '52W Return', 'EPS': 'EPS'},
        '🏦 Health': {'Current Ratio': 'Curr Ratio', 'Quick Ratio': 'Quick Ratio', 'Debt to Equity': 'D/E', 'Asset Turnover': 'Asset Turn'},
    }
    for category, metrics in categories.items():
        available = {k: v for k, v in ratios.items() if k in metrics}
        if available:
            st.markdown(f"**{category}**")
            cols = st.columns(min(len(available), 4))
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
    financials = analyzer.financials
    currency = analyzer.currency_symbol
    st.markdown("### 📉 Advanced Charts")
    
    prices = financials.get('prices')
    if prices is not None and not prices.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=prices.index, open=prices['Open'], high=prices['High'], low=prices['Low'], close=prices['Close'], name='Price'), row=1, col=1)
        for ma, color, name in [(20, 'orange', '20 MA'), (50, 'blue', '50 MA'), (200, 'red', '200 MA')]:
            fig.add_trace(go.Scatter(x=prices.index, y=prices['Close'].rolling(window=ma).mean(), name=name, line=dict(color=color, width=1)), row=1, col=1)
        vol_colors = ['green' if prices['Close'].iloc[i] >= prices['Open'].iloc[i] else 'red' for i in range(len(prices))]
        fig.add_trace(go.Bar(x=prices.index, y=prices['Volume'], name='Volume', marker_color=vol_colors), row=2, col=1)
        fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    if prices is not None and not prices.empty:
        returns = prices['Close'].pct_change().dropna() * 100
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=returns, nbinsx=50, name='Returns', marker_color='#1f77b4', opacity=0.7, histnorm='probability density'))
        if len(returns) > 1:
            mean_r, std_r = returns.mean(), returns.std()
            x_range = np.linspace(returns.min(), returns.max(), 100)
            fig.add_trace(go.Scatter(x=x_range, y=(1/(std_r*np.sqrt(2*np.pi)))*np.exp(-(x_range-mean_r)**2/(2*std_r**2)), name='Normal', line=dict(color='red', width=2)))
        fig.update_layout(height=400, template='plotly_white')
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


# ===== MAIN =====

def main():
    st.markdown('<h1 class="main-header">📊 Financial Statement Analyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Live Prices • Peer Comparison • 20+ Ratios • Advanced Charts</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("🔍 Search")
        ticker = st.text_input("Stock Ticker:", "AAPL", max_chars=50)
        exchange = st.selectbox("Exchange:", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"])
        exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": None, "Auto-detect": None}
        
        st.divider()
        st.subheader("🏢 Peer Comparison")
        use_peers = st.checkbox("Enable Peer Comparison", value=True)
        custom_peers = st.text_input("Custom Peers:", placeholder="AAPL, MSFT, GOOGL")
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
        
        st.divider()
        t1, t2 = st.tabs(["India", "US"])
        with t1:
            for tick in list(INDIAN_STOCKS_DB.keys())[:12]:
                if st.button(tick, use_container_width=True, key=f"i_{tick}"):
                    st.session_state['ticker'] = tick; st.rerun()
        with t2:
            for s in ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM"]:
                if st.button(s, use_container_width=True, key=f"u_{s}"):
                    st.session_state['ticker'] = s; st.rerun()
    
    if 'ticker' in st.session_state:
        ticker = st.session_state['ticker']
    
    if not analyze_btn and 'ticker' not in st.session_state:
        st.markdown('<div style="text-align:center;padding:3rem;"><h2>🚀 FinAnalyzer Pro</h2><p>Enter a ticker to analyze!</p></div>', unsafe_allow_html=True)
        return
    
    analyzer = ProFinancialAnalyzer(ticker, exchange=exchange_map.get(exchange))
    
    pb = st.progress(0)
    st_msg = st.empty()
    
    st_msg.text("Fetching data..."); pb.progress(25)
    analyzer.get_live_price()
    
    st_msg.text("Downloading financials..."); pb.progress(50)
    if not analyzer.fetch_financial_data():
        pb.empty(); st_msg.empty(); st.error("Unable to fetch data. Try another ticker."); return
    
    st_msg.text("Calculating ratios..."); pb.progress(75)
    analyzer.calculate_all_ratios()
    
    pb.progress(100); time.sleep(0.3)
    pb.empty(); st_msg.empty()
    
    # Display
    create_live_price_dashboard(analyzer)
    
    if analyzer.live_price_data.get('recommendation'):
        rec = analyzer.live_price_data.get('recommendation', '').upper()
        rc = {'BUY': '#00ff88', 'STRONG_BUY': '#00ff88', 'HOLD': '#ffa500', 'SELL': '#ff4444', 'STRONG_SELL': '#ff4444'}.get(rec, '#666')
        st.markdown(f'<div style="background-color:{rc};padding:1rem;border-radius:10px;color:white;text-align:center;"><h3>{rec.replace("_"," ")}</h3><p>{analyzer.live_price_data.get("number_of_analysts","N/A")} analysts</p></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="info-box"><strong>{analyzer.company_name}</strong> | {analyzer.financials.get("sector","N/A")} | {analyzer.financials.get("industry","N/A")} | {analyzer.currency} ({analyzer.currency_symbol})</div>', unsafe_allow_html=True)
    
    create_ratio_dashboard(analyzer.ratios, analyzer.currency_symbol)
    create_advanced_charts(analyzer)
    
    # Peer Comparison
    if use_peers:
        if custom_peers:
            peer_list = [p.strip().upper() for p in custom_peers.split(',') if p.strip()]
        else:
            group_name, peer_list = detect_peer_group(analyzer.ticker)
            if group_name: st.info(f"🔍 Peer group: **{group_name.replace('_',' ')}**")
            else: st.warning("No auto peer group. Add custom peers.")
        
        peer_list = [p for p in peer_list if p != analyzer.ticker]
        all_tickers = [analyzer.ticker] + peer_list[:7]
        
        if len(all_tickers) >= 2:
            with st.spinner("Fetching peer data..."):
                peer_df = get_peer_comparison(analyzer.ticker, all_tickers)
                if not peer_df.empty:
                    create_peer_comparison_charts(peer_df, analyzer.ticker, analyzer.currency_symbol, analyzer.currency)
    
    # Financial Statements
    st.markdown("---")
    st.markdown("### 📋 Financial Statements")
    st.caption(f"All amounts in {analyzer.currency} ({analyzer.currency_symbol})")
    
    tab1, tab2, tab3 = st.tabs(["📊 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])
    
    for tab, key, name in [(tab1, 'income', 'Income'), (tab2, 'balance', 'Balance'), (tab3, 'cashflow', 'Cash')]:
        with tab:
            df = analyzer.financials.get(key)
            if df is not None and not df.empty:
                formatted = format_financial_df(df, analyzer.currency_symbol, analyzer.currency)
                if formatted is not None:
                    st.dataframe(formatted, use_container_width=True)
                with st.expander("📥 Download / Raw Data"):
                    st.dataframe(df, use_container_width=True)
                    csv = df.to_csv()
                    st.download_button(f"📥 Download {name} CSV", csv, f"{analyzer.original_ticker}_{key}.csv", "text/csv")
            else:
                st.warning(f"{name} Statement not available for {analyzer.original_ticker}. This may be due to Yahoo Finance data limitations.")
    
    st.divider()
    st.caption(f"Data: Yahoo Finance | Currency: {analyzer.currency} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()