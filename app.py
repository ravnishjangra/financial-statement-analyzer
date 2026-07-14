"""
Financial Statement Analyzer - Pro Version (Fixed)
Live prices, valuation ratios, and comprehensive financial analysis
No scipy required - works with just numpy
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
                'earnings_per_share': info.get('trailingEps'),
                'revenue_per_share': info.get('revenuePerShare'),
                'book_value_per_share': info.get('bookValue'),
                'free_cashflow_per_share': info.get('freeCashflow'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'target_mean_price': info.get('targetMeanPrice'),
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'recommendation': info.get('recommendationKey'),
                'number_of_analysts': info.get('numberOfAnalystOpinions'),
                'short_ratio': info.get('shortRatio'),
                'short_percent': info.get('shortPercentOfFloat'),
                'held_by_institutions': info.get('heldPercentInstitutions'),
                'held_by_insiders': info.get('heldPercentInsiders'),
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
            
            # Try alternative exchange if data is sparse
            if not info or len(info) < 5:
                if not self.ticker.endswith('.NS'):
                    alt_ticker = self.ticker + '.NS'
                    st.info(f"Trying NSE exchange: {alt_ticker}")
                    self.stock = yf.Ticker(alt_ticker)
                    self.ticker = alt_ticker
                    info = self.stock.info
            
            self.financials['info'] = info
            self.company_name = info.get('longName', self.original_ticker)
            
            # Get financial statements - FORCE fetch
            self.financials['income'] = self.stock.financials
            self.financials['balance'] = self.stock.balance_sheet
            self.financials['cashflow'] = self.stock.cashflow
            
            # Get quarterly data
            self.financials['quarterly_income'] = self.stock.quarterly_financials
            self.financials['quarterly_balance'] = self.stock.quarterly_balance_sheet
            self.financials['quarterly_cashflow'] = self.stock.quarterly_cashflow
            
            # Get historical prices
            end = datetime.now()
            start = end - timedelta(days=365*3)  # 3 years
            self.financials['prices'] = self.stock.history(start=start, end=end)
            
            # Detect currency
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
        """Format amount based on currency"""
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
        """Safely get value with multiple possible keys"""
        if isinstance(keys, str):
            keys = [keys]
        
        for key in keys:
            if key in df.index and len(df.columns) > col:
                val = df.loc[key].iloc[col]
                if pd.notna(val):
                    return val
        return None
    
    def calculate_all_ratios(self):
        """Calculate comprehensive financial ratios"""
        try:
            income = self.financials['income']
            balance = self.financials['balance']
            cashflow = self.financials['cashflow']
            prices = self.financials.get('prices')
            
            current_price = self.live_price_data.get('current_price')
            
            # === PROFITABILITY RATIOS ===
            revenue = self._safe_get(income, ['Total Revenue', 'Revenue'])
            revenue_prev = self._safe_get(income, ['Total Revenue', 'Revenue'], 1)
            net_income = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'])
            gross_profit = self._safe_get(income, ['Gross Profit'])
            op_income = self._safe_get(income, ['Operating Income', 'EBIT'])
            ebitda = self._safe_get(income, ['EBITDA', 'Normalized EBITDA'])
            
            if revenue:
                if net_income:
                    self.ratios['Net Profit Margin'] = (net_income / revenue) * 100
                if gross_profit:
                    self.ratios['Gross Profit Margin'] = (gross_profit / revenue) * 100
                if op_income:
                    self.ratios['Operating Margin'] = (op_income / revenue) * 100
                if ebitda:
                    self.ratios['EBITDA Margin'] = (ebitda / revenue) * 100
                if revenue_prev and revenue_prev != 0:
                    self.ratios['Revenue Growth (YoY)'] = ((revenue - revenue_prev) / revenue_prev) * 100
            
            net_income_prev = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'], 1)
            if net_income and net_income_prev and net_income_prev != 0:
                self.ratios['Net Income Growth (YoY)'] = ((net_income - net_income_prev) / net_income_prev) * 100
            
            # === BALANCE SHEET RATIOS ===
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
                if total_debt:
                    self.ratios['Debt to Assets'] = (total_debt / assets) * 100
            
            if curr_assets and curr_liab:
                self.ratios['Current Ratio'] = curr_assets / curr_liab
                inventory = self._safe_get(balance, ['Inventory', 'Inventories'])
                if inventory:
                    self.ratios['Quick Ratio'] = (curr_assets - inventory) / curr_liab
            
            # === CASH FLOW RATIOS ===
            free_cashflow = self._safe_get(cashflow, ['Free Cash Flow'])
            operating_cashflow = self._safe_get(cashflow, ['Operating Cash Flow'])
            
            if free_cashflow and net_income:
                self.ratios['FCF to Net Income'] = free_cashflow / net_income
            if operating_cashflow and curr_liab:
                self.ratios['Operating CF to Current Liabilities'] = operating_cashflow / curr_liab
            
            # === VALUATION RATIOS ===
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
                        self.ratios['Sales per Share'] = sps
                        if sps > 0:
                            self.ratios['P/S Ratio'] = current_price / sps
                    
                    if free_cashflow:
                        fcfps = free_cashflow / shares
                        self.ratios['FCF per Share'] = fcfps
                        if fcfps > 0:
                            self.ratios['P/FCF Ratio'] = current_price / fcfps
                    
                    dividends = self._safe_get(cashflow, ['Dividends Paid'])
                    if dividends:
                        dps = abs(dividends) / shares
                        self.ratios['Dividend per Share'] = dps
                        if current_price > 0:
                            self.ratios['Dividend Yield'] = (dps / current_price) * 100
                
                # PEG Ratio
                earnings_growth = self.ratios.get('Net Income Growth (YoY)')
                pe = self.ratios.get('P/E Ratio')
                if earnings_growth and pe and earnings_growth > 0:
                    self.ratios['PEG Ratio'] = pe / earnings_growth
                
                # Earnings Yield
                if self.ratios.get('P/E Ratio'):
                    self.ratios['Earnings Yield'] = (1 / self.ratios['P/E Ratio']) * 100
            
            # === MARKET RATIOS ===
            if prices is not None and not prices.empty:
                if len(prices) >= 252:
                    price_52w_ago = prices['Close'].iloc[-252]
                    current = prices['Close'].iloc[-1]
                    self.ratios['52-Week Return'] = ((current - price_52w_ago) / price_52w_ago) * 100
                
                if len(prices) >= 30:
                    returns = prices['Close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252) * 100
                    self.ratios['Annualized Volatility'] = volatility
            
            # === EFFICIENCY RATIOS ===
            if revenue:
                if assets:
                    self.ratios['Asset Turnover'] = revenue / assets
                if equity:
                    self.ratios['Equity Turnover'] = revenue / equity
            
            cogs = self._safe_get(income, ['Cost Of Revenue', 'Cost of Goods Sold'])
            inventory = self._safe_get(balance, ['Inventory', 'Inventories'])
            if cogs and inventory and inventory != 0:
                self.ratios['Inventory Turnover'] = cogs / inventory
            
            self.metrics = self.ratios.copy()
            return True
            
        except Exception as e:
            st.error(f"Error calculating ratios: {str(e)}")
            return False

def create_live_price_dashboard(analyzer):
    """Create live price dashboard"""
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
            <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
                Last Updated: {datetime.now().strftime('%H:%M:%S')}
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
    """Create categorized ratio dashboard"""
    st.markdown("### 📊 Financial Ratios Dashboard")
    
    categories = {
        '📈 Valuation Ratios': {
            'P/E Ratio': 'Price to Earnings',
            'P/B Ratio': 'Price to Book',
            'P/S Ratio': 'Price to Sales',
            'P/FCF Ratio': 'Price to Free Cash Flow',
            'PEG Ratio': 'Price/Earnings to Growth',
            'Earnings Yield': 'Earnings Yield %',
            'Dividend Yield': 'Dividend Yield %',
        },
        '💰 Profitability Ratios': {
            'Net Profit Margin': 'Net Margin %',
            'Gross Profit Margin': 'Gross Margin %',
            'Operating Margin': 'Operating Margin %',
            'EBITDA Margin': 'EBITDA Margin %',
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
            'Debt to Assets': 'Debt Ratio',
            'Asset Turnover': 'Asset Efficiency',
            'Inventory Turnover': 'Inventory Efficiency',
        },
        '💵 Cash Flow Metrics': {
            'FCF to Net Income': 'FCF/Income Ratio',
            'Operating CF to Current Liabilities': 'CF Coverage',
            'FCF per Share': 'FCF per Share',
            'Dividend per Share': 'Dividend per Share',
        }
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
    """Create advanced financial charts - NO SCIPY REQUIRED"""
    financials = analyzer.financials
    currency = analyzer.currency_symbol
    
    st.markdown("### 📉 Advanced Charts")
    
    # Chart 1: Price with Moving Averages
    prices = financials.get('prices')
    if prices is not None and not prices.empty:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('Price & Moving Averages', 'Volume')
        )
        
        fig.add_trace(
            go.Candlestick(
                x=prices.index,
                open=prices['Open'],
                high=prices['High'],
                low=prices['Low'],
                close=prices['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        ma20 = prices['Close'].rolling(window=20).mean()
        ma50 = prices['Close'].rolling(window=50).mean()
        ma200 = prices['Close'].rolling(window=200).mean()
        
        fig.add_trace(go.Scatter(x=prices.index, y=ma20, name='20-day MA', line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=prices.index, y=ma50, name='50-day MA', line=dict(color='blue', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=prices.index, y=ma200, name='200-day MA', line=dict(color='red', width=1)), row=1, col=1)
        
        colors = ['green' if prices['Close'].iloc[i] >= prices['Open'].iloc[i] else 'red' for i in range(len(prices))]
        fig.add_trace(go.Bar(x=prices.index, y=prices['Volume'], name='Volume', marker_color=colors), row=2, col=1)
        
        fig.update_layout(
            height=600,
            template='plotly_white',
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        fig.update_yaxes(title_text=f"Price ({currency})", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Chart 2: Financial Metrics Trend
    income = financials.get('income')
    if income is not None and not income.empty:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue Trend', 'Net Income Trend', 'Profit Margins', 'ROE & ROA')
        )
        
        rev_key = None
        for key in ['Total Revenue', 'Revenue']:
            if key in income.index:
                rev_key = key
                break
        
        net_key = None
        for key in ['Net Income', 'Net Income Common Stockholders']:
            if key in income.index:
                net_key = key
                break
        
        divider = 1e7 if analyzer.currency == 'INR' else 1e9
        unit = 'Cr' if analyzer.currency == 'INR' else 'B'
        
        if rev_key:
            rev_data = income.loc[rev_key]
            years = [d.strftime('%Y') for d in rev_data.index]
            fig.add_trace(
                go.Bar(x=years[::-1], y=rev_data.values[::-1] / divider, name='Revenue', marker_color='#1f77b4'),
                row=1, col=1
            )
        
        if net_key:
            net_data = income.loc[net_key]
            fig.add_trace(
                go.Bar(x=years[::-1], y=net_data.values[::-1] / divider, name='Net Income', marker_color='#2ca02c'),
                row=1, col=2
            )
        
        if rev_key and net_key:
            margins = (income.loc[net_key] / income.loc[rev_key] * 100)[::-1]
            fig.add_trace(
                go.Scatter(x=years[::-1], y=margins.values, mode='lines+markers', name='Net Margin %', line=dict(color='#ff7f0e')),
                row=2, col=1
            )
        
        # ROE & ROA
        balance = financials.get('balance')
        if balance is not None and not balance.empty and net_key:
            eq_key = None
            for key in ['Stockholders Equity', 'Total Stockholder Equity', 'Total Equity']:
                if key in balance.index:
                    eq_key = key
                    break
            
            asset_key = None
            for key in ['Total Assets']:
                if key in balance.index:
                    asset_key = key
                    break
            
            if eq_key and asset_key:
                years_count = min(len(income.columns), len(balance.columns))
                roe_values, roa_values, year_labels = [], [], []
                
                for i in range(years_count):
                    net = income.loc[net_key].iloc[i]
                    eq = balance.loc[eq_key].iloc[i] if i < len(balance.columns) else None
                    ast = balance.loc[asset_key].iloc[i] if i < len(balance.columns) else None
                    
                    year_labels.append(income.columns[i].strftime('%Y'))
                    roe_values.append((net / eq) * 100 if eq and eq != 0 else None)
                    roa_values.append((net / ast) * 100 if ast and ast != 0 else None)
                
                fig.add_trace(go.Scatter(x=year_labels[::-1], y=roe_values[::-1], mode='lines+markers', name='ROE %', line=dict(color='#1f77b4', width=3)), row=2, col=2)
                fig.add_trace(go.Scatter(x=year_labels[::-1], y=roa_values[::-1], mode='lines+markers', name='ROA %', line=dict(color='#ff7f0e', width=2, dash='dot')), row=2, col=2)
        
        fig.update_layout(height=600, template='plotly_white', showlegend=True, hovermode='x unified')
        fig.update_yaxes(title_text=f"Amount ({currency} {unit})", row=1, col=1)
        fig.update_yaxes(title_text=f"Amount ({currency} {unit})", row=1, col=2)
        fig.update_yaxes(title_text="Percentage (%)", row=2, col=1)
        fig.update_yaxes(title_text="Percentage (%)", row=2, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Chart 3: Returns Distribution (NO SCIPY - Using NumPy only)
    if prices is not None and not prices.empty:
        returns = prices['Close'].pct_change().dropna() * 100
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Daily Returns',
            marker_color='#1f77b4',
            opacity=0.7,
            histnorm='probability density'
        ))
        
        # Add normal distribution curve using numpy (no scipy needed)
        if len(returns) > 1:
            mean_ret = returns.mean()
            std_ret = returns.std()
            x_range = np.linspace(returns.min(), returns.max(), 100)
            
            # Normal distribution formula: (1/(σ√(2π))) * e^(-(x-μ)²/(2σ²))
            y_curve = (1/(std_ret * np.sqrt(2*np.pi))) * np.exp(-(x_range - mean_ret)**2 / (2*std_ret**2))
            
            fig.add_trace(go.Scatter(
                x=x_range,
                y=y_curve,
                name='Normal Distribution',
                line=dict(color='red', width=2)
            ))
        
        fig.add_vline(x=returns.mean(), line_dash="dash", line_color="green",
                      annotation_text=f"Mean: {returns.mean():.2f}%")
        
        fig.update_layout(
            title='Daily Returns Distribution (with Normal Curve)',
            template='plotly_white',
            height=400,
            xaxis_title='Daily Return (%)',
            yaxis_title='Probability Density',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Return statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean Return", f"{returns.mean():.3f}%")
        col2.metric("Std Deviation", f"{returns.std():.3f}%")
        col3.metric("Skewness", f"{returns.skew():.3f}")
        col4.metric("Kurtosis", f"{returns.kurtosis():.3f}")

def main():
    st.markdown('<h1 class="main-header">📊 Financial Statement Analyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Live Prices • Comprehensive Ratios • Advanced Analytics</p>', unsafe_allow_html=True)
    
    # Sidebar
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
        
        auto_refresh = st.checkbox("Auto-refresh price (30s)", value=False)
        analyze_btn = st.button("🔍 Analyze Company", type="primary", use_container_width=True)
        
        st.divider()
        
        # Quick access tabs
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
    
    # Progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Fetching live market data...")
    progress_bar.progress(25)
    analyzer.get_live_price()
    
    status_text.text("Downloading financial statements...")
    progress_bar.progress(50)
    if not analyzer.fetch_financial_data():
        st.error("Unable to fetch financial data. Please check the ticker.")
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
        Exchange: {info.get('exchange', 'N/A')} | 
        Currency: {analyzer.currency} ({analyzer.currency_symbol}) | 
        Sector: {info.get('sector', 'N/A')} | 
        Industry: {info.get('industry', 'N/A')}
    </div>
    """, unsafe_allow_html=True)
    
    # 4. Financial Ratios
    create_ratio_dashboard(analyzer.ratios, analyzer.currency_symbol)
    
    # 5. Advanced Charts
    create_advanced_charts(analyzer)
    
    # 6. FINANCIAL STATEMENTS - ALWAYS DISPLAY
    st.markdown("### 📋 Financial Statements")
    st.caption(f"All amounts in {analyzer.currency} ({analyzer.currency_symbol})")
    
    tab1, tab2, tab3 = st.tabs(["📊 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])
    
    with tab1:
        income_df = analyzer.financials.get('income')
        if income_df is not None and not income_df.empty:
            st.dataframe(income_df, use_container_width=True)
            
            # Add download button
            csv = income_df.to_csv()
            st.download_button(
                label="📥 Download Income Statement (CSV)",
                data=csv,
                file_name=f"{analyzer.original_ticker}_income_statement.csv",
                mime="text/csv"
            )
        else:
            st.warning("Income Statement data not available for this ticker.")
    
    with tab2:
        balance_df = analyzer.financials.get('balance')
        if balance_df is not None and not balance_df.empty:
            st.dataframe(balance_df, use_container_width=True)
            
            csv = balance_df.to_csv()
            st.download_button(
                label="📥 Download Balance Sheet (CSV)",
                data=csv,
                file_name=f"{analyzer.original_ticker}_balance_sheet.csv",
                mime="text/csv"
            )
        else:
            st.warning("Balance Sheet data not available for this ticker.")
    
    with tab3:
        cashflow_df = analyzer.financials.get('cashflow')
        if cashflow_df is not None and not cashflow_df.empty:
            st.dataframe(cashflow_df, use_container_width=True)
            
            csv = cashflow_df.to_csv()
            st.download_button(
                label="📥 Download Cash Flow (CSV)",
                data=csv,
                file_name=f"{analyzer.original_ticker}_cash_flow.csv",
                mime="text/csv"
            )
        else:
            st.warning("Cash Flow Statement data not available for this ticker.")
    
    # Footer
    st.divider()
    st.caption(f"Data sourced from Yahoo Finance | Currency: {analyzer.currency} | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()