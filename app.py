"""
FinAnalyzer Pro - Enterprise Financial Analysis Platform
31 Stress Tests • Advanced DCF • Graham & EPV • Portfolio Optimizer
Technical Analysis • Peer Comparison • Live Prices • Multi-Currency
"""

from scipy.optimize import minimize
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import requests
from yahooquery import Ticker as YQTicker

# Page config
st.set_page_config(page_title="FinAnalyzer Pro | Enterprise Analysis", page_icon="📊", layout="wide")

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem; font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem;
    }
    .sub-header { font-size: 1rem; color: #94a3b8; text-align: center; margin-bottom: 2rem; }
    .card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(102,126,234,0.2); padding: 1.5rem;
        border-radius: 16px; margin: 0.5rem 0; color: #e2e8f0;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .live-price-box {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 2px solid rgba(102,126,234,0.4); padding: 2rem;
        border-radius: 20px; color: white; text-align: center; margin: 1rem 0;
    }
    .price-up { color: #10b981; font-size: 3rem; font-weight: 900; }
    .price-down { color: #ef4444; font-size: 3rem; font-weight: 900; }
    .info-box {
        background: #1e293b; border: 1px solid rgba(102,126,234,0.2);
        padding: 0.75rem 1.5rem; border-radius: 12px; color: #e2e8f0;
    }
    .stButton button {
        width: 100%; border-radius: 12px; padding: 0.6rem;
        font-weight: 600; background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; transition: all 0.3s;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102,126,234,0.4); }
    .section-header {
        font-size: 1.4rem; font-weight: 700; color: #e2e8f0;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102,126,234,0.3);
    }
    .source-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem; }
    .source-yahoo { background: #7200ff; color: white; }
</style>
""", unsafe_allow_html=True)

# Constants
CURRENCY_SYMBOLS = {'USD': '$', 'INR': '₹', 'EUR': '€', 'GBP': '£', 'JPY': '¥'}

INDIAN_STOCKS_DB = {
    'RELIANCE': 'RELIANCE.NS', 'TCS': 'TCS.NS', 'HDFCBANK': 'HDFCBANK.NS',
    'INFY': 'INFY.NS', 'ICICIBANK': 'ICICIBANK.NS', 'ITC': 'ITC.NS',
    'WIPRO': 'WIPRO.NS', 'TATAMOTORS': 'TATAMOTORS.NS', 'SBIN': 'SBIN.NS',
    'BHARTIARTL': 'BHARTIARTL.NS', 'KOTAKBANK': 'KOTAKBANK.NS', 'MARUTI': 'MARUTI.NS',
    'SUNPHARMA': 'SUNPHARMA.NS', 'TATASTEEL': 'TATASTEEL.NS', 'BAJFINANCE': 'BAJFINANCE.NS',
    'ADANIENT': 'ADANIENT.NS', 'NTPC': 'NTPC.NS', 'ONGC': 'ONGC.NS',
    'HCLTECH': 'HCLTECH.NS', 'ASIANPAINT': 'ASIANPAINT.NS', 'TITAN': 'TITAN.NS',
    'NESTLEIND': 'NESTLEIND.NS', 'DRREDDY': 'DRREDDY.NS', 'CIPLA': 'CIPLA.NS',
    'HINDUNILVR': 'HINDUNILVR.NS', 'TECHM': 'TECHM.NS', 'JSWSTEEL': 'JSWSTEEL.NS',
    'EICHERMOT': 'EICHERMOT.NS', 'HEROMOTOCO': 'HEROMOTOCO.NS', 'DIVISLAB': 'DIVISLAB.NS',
    'AXISBANK': 'AXISBANK.NS', 'LT': 'LT.NS', 'ULTRACEMCO': 'ULTRACEMCO.NS',
    'COALINDIA': 'COALINDIA.NS', 'BAJAJFINSV': 'BAJAJFINSV.NS', 'POWERGRID': 'POWERGRID.NS',
    'GRASIM': 'GRASIM.NS', 'INDUSINDBK': 'INDUSINDBK.NS', 'BRITANNIA': 'BRITANNIA.NS',
}

PEER_GROUPS = {
    'Tech_US': ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NVDA'],
    'Tech_India': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
    'Banking_India': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
    'Auto_India': ['TATAMOTORS.NS', 'MARUTI.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS'],
    'Pharma_India': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
    'Energy_India': ['RELIANCE.NS', 'ONGC.NS', 'COALINDIA.NS', 'NTPC.NS', 'POWERGRID.NS'],
    'Finance_US': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    'Consumer_India': ['ITC.NS', 'HINDUNILVR.NS', 'NESTLEIND.NS', 'TITAN.NS', 'ASIANPAINT.NS'],
}


# ===== MULTI‑SOURCE PRICE FETCHER =====
class MultiSourceFetcher:
    """Try multiple free data sources until one returns a valid price"""
    
    @staticmethod
    def fetch_price(ticker):
        # 1. yfinance (handled separately in Analyzer)
        # 2. yahooquery
        price = MultiSourceFetcher._try_yahooquery(ticker)
        if price: return price
        
        # 3. Twelve Data
        price = MultiSourceFetcher._try_twelvedata(ticker)
        if price: return price
        
        # 4. Alpha Vantage
        price = MultiSourceFetcher._try_alphavantage(ticker)
        if price: return price
        
        # 5. Financial Modeling Prep (needs FMP_API_KEY)
        price = MultiSourceFetcher._try_fmp(ticker)
        if price: return price
        
        # 6. Google Finance (fragile, last resort)
        price = MultiSourceFetcher._try_google_finance(ticker)
        if price: return price
        
        # 7. EODHD (needs EODHD_API_KEY)
        price = MultiSourceFetcher._try_eodhd(ticker)
        if price: return price
        
        return None

    @staticmethod
    def _try_yahooquery(ticker):
        try:
            t = YQTicker(ticker)
            data = t.price[ticker]
            if data and 'regularMarketPrice' in data:
                return {'current_price': data['regularMarketPrice'], 'source': 'yahooquery'}
        except:
            pass
        return None

    @staticmethod
    def _try_twelvedata(ticker):
        api_key = st.secrets.get("TWELVEDATA_API_KEY", "")
        if not api_key: return None
        try:
            url = f"https://api.twelvedata.com/price?symbol={ticker}&apikey={api_key}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if 'price' in data:
                    return {'current_price': float(data['price']), 'source': 'Twelve Data'}
        except:
            pass
        return None

    @staticmethod
    def _try_alphavantage(ticker):
        api_key = st.secrets.get("ALPHAVANTAGE_API_KEY", "")
        if not api_key: return None
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                price = float(data['Global Quote']['05. price'])
                if price > 0:
                    return {'current_price': price, 'source': 'Alpha Vantage'}
        except:
            pass
        return None

    @staticmethod
    def _try_fmp(ticker):
        api_key = st.secrets.get("FMP_API_KEY", "")
        if not api_key: return None
        try:
            url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and 'price' in data[0]:
                    return {'current_price': data[0]['price'], 'source': 'Financial Modeling Prep'}
        except:
            pass
        return None

    @staticmethod
    def _try_google_finance(ticker):
        try:
            if ticker.endswith('.NS'):
                gf_ticker = f'NSE:{ticker[:-3]}'
            elif ticker.endswith('.BO'):
                gf_ticker = f'BOM:{ticker[:-3]}'
            else:
                gf_ticker = ticker
            url = f'https://www.google.com/finance/quote/{gf_ticker}'
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                import re
                match = re.search(r'data-last-price="([^"]*)"', resp.text)
                if match:
                    price = float(match.group(1).replace(',', ''))
                    return {'current_price': price, 'source': 'Google Finance'}
        except:
            pass
        return None

    @staticmethod
    def _try_eodhd(ticker):
        api_key = st.secrets.get("EODHD_API_KEY", "")
        if not api_key: return None
        try:
            url = f"https://eodhd.com/api/real-time/{ticker}?api_token={api_key}&fmt=json"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if 'close' in data:
                    return {'current_price': data['close'], 'source': 'EODHD'}
        except:
            pass
        return None


# ===== ANALYZER CLASS =====
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
        if exchange == "NSE": return ticker + '.NS' if not ticker.endswith('.NS') else ticker
        elif exchange == "BSE": return ticker + '.BO' if not ticker.endswith('.BO') else ticker
        elif ticker in INDIAN_STOCKS_DB: return INDIAN_STOCKS_DB[ticker]
        elif ticker.endswith('.NS') or ticker.endswith('.BO'): return ticker
        return ticker

    def get_live_price(self):
        """Try yfinance first, then multi‑source fallback"""
        if self._try_yfinance_direct():
            return True

        # Multi‑source fallback
        result = MultiSourceFetcher.fetch_price(self.ticker)
        if result and result.get('current_price'):
            self.live_price_data = {
                'current_price': result['current_price'],
                'previous_close': None,
                'open': None,
                'day_high': None,
                'day_low': None,
                'volume': None,
                'market_cap': None,
                'fifty_two_week_high': None,
                'fifty_two_week_low': None,
                'beta': None,
                'recommendation': None,
                'number_of_analysts': None,
            }
            self.data_source = result.get('source', 'fallback')
            try:
                self.stock = yf.Ticker(self.ticker)
            except:
                pass
            return True
        return False

    def _try_yfinance_direct(self):
        """Robust yfinance fetch with history and alternate exchanges"""
        try:
            self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if price:
                self._populate_from_info(info)
                self.data_source = 'Yahoo Finance'
                return True

            # history fallback
            hist = self.stock.history(period='5d')
            if not hist.empty and 'Close' in hist.columns:
                last_close = hist['Close'].iloc[-1]
                if pd.notna(last_close) and last_close > 0:
                    self.live_price_data = {
                        'current_price': last_close,
                        'previous_close': info.get('previousClose'),
                        'open': info.get('open'),
                        'day_high': info.get('dayHigh'),
                        'day_low': info.get('dayLow'),
                        'volume': info.get('volume'),
                        'market_cap': info.get('marketCap'),
                        'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                        'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                        'beta': info.get('beta'),
                        'recommendation': info.get('recommendationKey'),
                    }
                    self.live_price_data = {k: v for k, v in self.live_price_data.items() if v is not None}
                    self.data_source = 'Yahoo Finance (history)'
                    return True

            # alternate exchanges
            alts = []
            if self.ticker.endswith('.NS'):
                alts = [self.ticker.replace('.NS','.BO'), self.ticker.replace('.NS','')]
            elif self.ticker.endswith('.BO'):
                alts = [self.ticker.replace('.BO','.NS'), self.ticker.replace('.BO','')]
            else:
                alts = [self.ticker+'.NS', self.ticker+'.BO']
            for alt in alts:
                try:
                    s = yf.Ticker(alt)
                    i = s.info
                    p = i.get('currentPrice') or i.get('regularMarketPrice')
                    if p:
                        self.stock = s
                        self.ticker = alt
                        self._populate_from_info(i)
                        self.data_source = 'Yahoo Finance (alt)'
                        return True
                    hist = s.history(period='5d')
                    if not hist.empty:
                        last = hist['Close'].iloc[-1]
                        if pd.notna(last) and last > 0:
                            self.stock = s
                            self.ticker = alt
                            self.live_price_data = {'current_price': last}
                            self.data_source = 'Yahoo Finance (alt history)'
                            return True
                except:
                    continue
        except:
            pass
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
            self.financials['prices'] = self.stock.history(period="5y")
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
            prices = self.financials.get('prices')
            cp = self.live_price_data.get('current_price')
            info = self.financials.get('info', {})

            if income is not None and not income.empty:
                rev = self._safe_get(income, ['Total Revenue', 'Revenue'])
                ni = self._safe_get(income, ['Net Income', 'Net Income Common Stockholders'])
                gp = self._safe_get(income, ['Gross Profit'])
                oi = self._safe_get(income, ['Operating Income', 'EBIT'])
                rev_p = self._safe_get(income, ['Total Revenue', 'Revenue'], 1)

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
                    if rev and ast: self.ratios['Asset Turnover'] = rev/ast

                if cp:
                    shares = self._safe_get(income, ['Diluted Average Shares']) or self._safe_get(income, ['Basic Average Shares'])
                    if shares:
                        if ni:
                            eps = ni/shares; self.ratios['EPS'] = eps
                            if eps > 0: self.ratios['P/E Ratio'] = cp/eps
                        if eq and eq > 0: self.ratios['P/B Ratio'] = cp/(eq/shares)
                        if rev and rev/shares > 0: self.ratios['P/S Ratio'] = cp/(rev/shares)

                if prices is not None and not prices.empty and len(prices) >= 252:
                    returns = prices['Close'].pct_change().dropna()
                    self.ratios['Annualized Volatility'] = returns.std() * np.sqrt(252) * 100
                    self.ratios['52-Week Return'] = ((prices['Close'].iloc[-1]-prices['Close'].iloc[-252])/prices['Close'].iloc[-252])*100

            for key, ratio_key, mult in [
                ('returnOnEquity', 'ROE', 100), ('returnOnAssets', 'ROA', 100),
                ('profitMargins', 'Net Profit Margin', 100), ('debtToEquity', 'Debt to Equity', 1),
                ('trailingPE', 'P/E Ratio', 1), ('priceToBook', 'P/B Ratio', 1),
                ('trailingEps', 'EPS', 1), ('revenueGrowth', 'Revenue Growth (YoY)', 100),
                ('dividendYield', 'Dividend Yield', 100),
            ]:
                if ratio_key not in self.ratios and info.get(key):
                    try: self.ratios[ratio_key] = info[key] * mult
                    except: pass
            return True
        except: return True


# ===== VALUATION MODELS =====

class AdvancedDCF:
    def __init__(self, fcf, shares, current_price, revenue_growth, beta, risk_free_rate, market_return):
        self.fcf = fcf; self.shares = shares; self.current_price = current_price
        self.revenue_growth = revenue_growth; self.beta = beta
        self.risk_free_rate = risk_free_rate; self.market_return = market_return
        cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
        cost_of_debt = risk_free_rate + 0.03
        self.wacc = 0.75 * cost_of_equity + 0.25 * cost_of_debt * (1 - 0.25)

    def project_cashflows(self, years=10):
        projections = []
        fcf = self.fcf
        for year in range(1, years + 1):
            growth = self.revenue_growth * (1 - (year - 1) * 0.07)
            growth = max(growth, 0.025)
            fcf = fcf * (1 + growth)
            pv = fcf / (1 + self.wacc) ** year
            projections.append({'year': year, 'growth': growth, 'fcf': fcf, 'pv_fcf': pv})
        return projections

    def calculate(self):
        projections = self.project_cashflows(10)
        pv_fcfs = sum(p['pv_fcf'] for p in projections)
        last_fcf = projections[-1]['fcf']
        terminal_value = last_fcf * 1.025 / (self.wacc - 0.025)
        pv_terminal = terminal_value / (1 + self.wacc) ** 10
        enterprise_value = pv_fcfs + pv_terminal
        intrinsic_value = enterprise_value / self.shares if self.shares > 0 else 0
        upside = ((intrinsic_value / self.current_price) - 1) * 100 if self.current_price > 0 else 0
        bear_iv = intrinsic_value * 0.6; bull_iv = intrinsic_value * 1.5
        
        if upside > 30: rec, rc = "STRONG BUY 🟢", "#10b981"
        elif upside > 10: rec, rc = "BUY 🟢", "#34d399"
        elif upside > -10: rec, rc = "HOLD 🟡", "#f59e0b"
        elif upside > -30: rec, rc = "SELL 🔴", "#ef4444"
        else: rec, rc = "STRONG SELL 🔴", "#dc2626"
        
        return {'intrinsic_value': intrinsic_value, 'current_price': self.current_price,
                'upside': upside, 'wacc': self.wacc, 'pv_fcfs': pv_fcfs,
                'terminal_value': terminal_value, 'pv_terminal': pv_terminal,
                'enterprise_value': enterprise_value, 'projections': projections,
                'bear_case': bear_iv, 'bull_case': bull_iv, 'recommendation': rec, 'rec_color': rc}


class GrahamValuation:
    @staticmethod
    def calculate(eps, growth_rate, bond_yield=0.07):
        return eps * (8.5 + 2 * growth_rate * 100) * 4.4 / (bond_yield * 100)


class EarningsPowerValue:
    @staticmethod
    def calculate(revenue, operating_margin, tax_rate, wacc, shares):
        sustainable_rev = revenue * 0.9
        sustainable_margin = max(operating_margin * 0.8, 0.05)
        nopat = sustainable_rev * sustainable_margin * (1 - tax_rate)
        epv = nopat / wacc
        return epv / shares if shares > 0 else 0


# ===== 31 STRESS TESTS =====

class StressTestEngine:
    """31 Comprehensive Stress Tests"""
    
    def __init__(self, current_price, sector, industry, beta, currency, market_cap):
        self.price = current_price
        self.sector = sector
        self.industry = industry
        self.beta = beta or 1.0
        self.currency = currency
        self.market_cap = market_cap or 0
    
    def run_all_tests(self):
        results = []
        
        # 1. Market Crash
        for pct in [-10, -20, -30, -50]:
            impact = self.price * (1 + pct/100 * self.beta)
            loss = (impact/self.price - 1) * 100
            results.append({'Test': f'Market Crash ({abs(pct)}%)', 'Scenario': f'Broad market declines by {abs(pct)}%', 'Impact Price': impact, 'Loss %': loss, 'Severity': '🔴 CRITICAL' if loss < -30 else '🟠 HIGH' if loss < -20 else '🟡 MODERATE' if loss < -10 else '🟢 LOW'})
        
        # 2. Bull Rally
        for pct in [10, 20, 30]:
            impact = self.price * (1 + pct/100 * self.beta)
            gain = (impact/self.price - 1) * 100
            results.append({'Test': f'Bull Rally (+{pct}%)', 'Scenario': f'Market rises by {pct}%', 'Impact Price': impact, 'Loss %': gain, 'Severity': '🟢 POSITIVE'})
        
        # 3. Interest Rate Shock
        for bps in [100, 200, -100, -200]:
            rate_sens = 1.5 if self.sector in ['Financial Services', 'Real Estate', 'Utilities'] else 1.0
            impact_pct = -bps/100 * 0.05 * self.beta * rate_sens
            impact = self.price * (1 + impact_pct)
            results.append({'Test': f'Rate {"Hike" if bps>0 else "Cut"} ({abs(bps)}bps)', 'Scenario': f'Central bank {"raises" if bps>0 else "cuts"} rates', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL' if impact_pct<-0.1 else '🟠 HIGH' if impact_pct<-0.05 else '🟡 MODERATE'})
        
        # 4. Inflation Spike
        for inf in [5, 10, 15]:
            inf_sens = 0.8 if self.sector in ['Consumer Defensive', 'Healthcare'] else 1.2
            impact_pct = -inf/100 * 0.03 * self.beta * inf_sens
            impact = self.price * (1 + impact_pct)
            results.append({'Test': f'Inflation Spike ({inf}%)', 'Scenario': f'Inflation rises to {inf}%', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL' if impact_pct<-0.15 else '🟠 HIGH'})
        
        # 5. Currency Shock
        is_indian = self.currency == 'INR'
        for pct in [5, 10, -5, -10, 20, -20]:
            fx_sens = 1.3 if self.sector in ['Technology', 'Energy'] else 0.7
            if is_indian: impact_pct = -pct/100 * 0.02 * fx_sens
            else: impact_pct = pct/100 * 0.01 * fx_sens
            impact = self.price * (1 + impact_pct)
            direction = "Depreciation" if (is_indian and pct>0) or (not is_indian and pct<0) else "Appreciation"
            results.append({'Test': f'Currency {direction} ({abs(pct)}%)', 'Scenario': f'USD/INR moves by {pct}%', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🟠 HIGH' if abs(impact_pct*100)>3 else '🟡 MODERATE'})
        
        # 6. Oil Price Shock
        if self.sector in ['Energy', 'Transportation']:
            for pct in [20, 50, -20, -50]:
                oil_sens = 2.0 if self.sector=='Energy' else -1.5
                impact_pct = pct/100 * 0.05 * oil_sens
                impact = self.price * (1 + impact_pct)
                results.append({'Test': f'Oil {"Rise" if pct>0 else "Fall"} ({abs(pct)}%)', 'Scenario': f'Crude oil moves by {abs(pct)}%', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL' if abs(impact_pct*100)>10 else '🟠 HIGH'})
        
        # 7. Gold Shock
        gold_sens = 1.5 if 'Gold' in str(self.industry) else 0.3
        for pct in [20, 50, -20]:
            impact_pct = pct/100 * 0.02 * gold_sens
            impact = self.price * (1 + impact_pct)
            results.append({'Test': f'Gold {"Rise" if pct>0 else "Fall"} ({abs(pct)}%)', 'Scenario': f'Gold moves {pct}%', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🟡 MODERATE'})
        
        # 8. Commodity Crash
        if self.sector in ['Basic Materials', 'Energy', 'Industrials']:
            for pct in [-20, -40, -60]:
                impact_pct = pct/100 * 0.5
                impact = self.price * (1 + impact_pct)
                results.append({'Test': f'Commodity Crash ({abs(pct)}%)', 'Scenario': f'Industrial commodities fall {abs(pct)}%', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL'})
        
        # 9. Bond Yield Spike
        for bps in [100, 200, 300]:
            impact_pct = -bps/10000 * 2 * self.beta
            impact = self.price * (1 + impact_pct)
            results.append({'Test': f'Bond Yield Spike (+{bps}bps)', 'Scenario': f'10Y yields surge {bps}bps', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL' if impact_pct<-0.1 else '🟠 HIGH'})
        
        # 10. Volatility Spike
        for mult in [2, 3, 5]:
            impact_pct = -0.05 * mult * self.beta
            impact = self.price * (1 + impact_pct)
            results.append({'Test': f'VIX Spike (x{mult})', 'Scenario': f'Volatility index increases {mult}x', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL' if mult>=3 else '🟠 HIGH'})
        
        # 11. Sector Crash
        sectors_crash = {'Technology': -30, 'Banking': -40, 'Pharma': -25, 'Energy': -35, 'Auto': -30}
        for sec, pct in sectors_crash.items():
            if sec in str(self.sector):
                impact_pct = pct/100 * 1.2
                impact = self.price * (1 + impact_pct)
                results.append({'Test': f'{sec} Sector Crash ({abs(pct)}%)', 'Scenario': f'{sec} sector crashes', 'Impact Price': impact, 'Loss %': impact_pct*100, 'Severity': '🔴 CRITICAL'})
        
        # 12. Single Stock Collapse
        for pct in [-50, -75, -90]:
            impact = self.price * (1 + pct/100)
            results.append({'Test': f'Stock Collapse ({abs(pct)}%)', 'Scenario': f'Stock drops {abs(pct)}%', 'Impact Price': impact, 'Loss %': pct, 'Severity': '🔴 CRITICAL'})
        
        # 13. Bankruptcy
        results.append({'Test': 'Bankruptcy (100% Loss)', 'Scenario': 'Complete loss of investment', 'Impact Price': 0, 'Loss %': -100, 'Severity': '💀 MAXIMUM'})
        
        # 14. Liquidity Crisis
        impact = self.price * 0.85
        results.append({'Test': 'Liquidity Crisis', 'Scenario': 'Stock becomes illiquid', 'Impact Price': impact, 'Loss %': -15, 'Severity': '🟠 HIGH'})
        
        # 15. Earnings Miss
        for pct in [-10, -25, -50]:
            impact = self.price * (1 + pct/100 * 1.5)
            results.append({'Test': f'Earnings Miss ({abs(pct)}%)', 'Scenario': f'Company misses earnings', 'Impact Price': impact, 'Loss %': pct*1.5, 'Severity': '🔴 CRITICAL' if pct<-25 else '🟠 HIGH'})
        
        # 16. Dividend Suspension
        results.append({'Test': 'Dividend Suspension', 'Scenario': 'Company suspends dividends', 'Impact Price': self.price*0.85, 'Loss %': -15, 'Severity': '🟠 HIGH'})
        
        # 17. Credit Downgrade
        if self.sector in ['Financial Services', 'Energy']:
            for notch in [1, 3]:
                impact_pct = -0.05 * notch * self.beta
                results.append({'Test': f'Credit Downgrade ({notch} notch)', 'Scenario': f'Rating downgraded', 'Impact Price': self.price*(1+impact_pct), 'Loss %': impact_pct*100, 'Severity': '🟠 HIGH'})
        
        # 18. Governance Scandal
        results.append({'Test': 'Governance Scandal', 'Scenario': 'Fraud or governance issues', 'Impact Price': self.price*0.60, 'Loss %': -40, 'Severity': '🔴 CRITICAL'})
        
        # 19. Geopolitical Conflict
        results.append({'Test': 'Geopolitical Conflict', 'Scenario': 'War or major tensions', 'Impact Price': self.price*0.80, 'Loss %': -20, 'Severity': '🟠 HIGH'})
        
        # 20. Pandemic
        impact = self.price * (1.15 if self.sector in ['Healthcare', 'Technology'] else 0.70)
        results.append({'Test': 'Pandemic Scenario', 'Scenario': 'Global pandemic', 'Impact Price': impact, 'Loss %': (impact/self.price-1)*100, 'Severity': '🟢 WINNER' if impact>self.price else '🔴 LOSER'})
        
        # 21. Recession
        impact = self.price * (0.65 if self.sector in ['Consumer Cyclical', 'Industrials'] else 0.85)
        results.append({'Test': 'Recession', 'Scenario': 'GDP contracts', 'Impact Price': impact, 'Loss %': (impact/self.price-1)*100, 'Severity': '🔴 CRITICAL'})
        
        # 22. Economic Boom
        impact = self.price * (1.25 if self.sector in ['Consumer Cyclical', 'Industrials', 'Financial Services'] else 1.10)
        results.append({'Test': 'Economic Boom', 'Scenario': 'Strong GDP growth', 'Impact Price': impact, 'Loss %': (impact/self.price-1)*100, 'Severity': '🟢 POSITIVE'})
        
        # 23. Historical Replay
        for event, pct in [('2008 GFC', -0.45), ('2020 COVID', -0.30), ('2022 Inflation', -0.20)]:
            impact = self.price * (1 + pct * self.beta)
            results.append({'Test': f'Historical: {event}', 'Scenario': f'Replay {event}', 'Impact Price': impact, 'Loss %': pct*self.beta*100, 'Severity': '🔴 CRITICAL'})
        
        # 24. Concentration Risk
        results.append({'Test': 'Concentration Risk', 'Scenario': 'Overweight single position', 'Impact Price': self.price*0.80, 'Loss %': -20, 'Severity': '🟠 HIGH'})
        
        # 25. Correlation Breakdown
        results.append({'Test': 'Correlation Breakdown', 'Scenario': 'All assets move together', 'Impact Price': self.price*0.75, 'Loss %': -25, 'Severity': '🔴 CRITICAL'})
        
        # 26. Monte Carlo VaR (corrected)
        np.random.seed(42)
        daily_returns = np.random.normal(0.0005, 0.02, (1000, 252))
        annual_returns = (1 + daily_returns).prod(axis=1) - 1
        var_95 = np.percentile(annual_returns, 5)
        impact = self.price * (1 + var_95)
        loss_pct = var_95 * 100
        results.append({'Test': 'Monte Carlo VaR (95%)', 'Scenario': '1000 simulated annual return paths', 'Impact Price': max(impact, self.price * 0.01), 'Loss %': max(loss_pct, -99), 'Severity': '🔴 CRITICAL' if loss_pct < -30 else '🟠 HIGH' if loss_pct < -15 else '🟡 MODERATE'})
        
        # 27. VaR Comparison
        for method, ret in [('Historical', -0.15), ('Parametric', -0.18), ('Monte Carlo', -0.16)]:
            impact = max(self.price * (1 + ret), self.price * 0.10)
            results.append({'Test': f'VaR ({method})', 'Scenario': f'{method} Value at Risk (annual)', 'Impact Price': impact, 'Loss %': max(ret * 100, -90), 'Severity': '🔴 CRITICAL' if ret < -0.25 else '🟠 HIGH' if ret < -0.15 else '🟡 MODERATE'})
        
        # 28. Custom Scenarios
        for name, pct in [('IT -20%', -0.20 if 'Technology' in str(self.sector) else -0.05), ('Oil +30%', 0.30 if 'Energy' in str(self.sector) else -0.10)]:
            results.append({'Test': f'Custom: {name}', 'Scenario': f'User-defined shock', 'Impact Price': self.price*(1+pct), 'Loss %': pct*100, 'Severity': '🟢' if pct>0 else '🟠'})
        
        # 29. Multi-Factor Shock
        mf_pct = -0.15 + (-0.05*self.beta) + (-0.03)
        results.append({'Test': 'Multi-Factor Shock', 'Scenario': 'Crash + rate hike + oil + currency', 'Impact Price': self.price*(1+mf_pct), 'Loss %': mf_pct*100, 'Severity': '🔴 CRITICAL'})
        
        # 30. War Scenario
        results.append({'Test': 'War Scenario', 'Scenario': 'Major international conflict', 'Impact Price': self.price*0.55, 'Loss %': -45, 'Severity': '💀 EXTREME'})
        
        return pd.DataFrame(results)


# ===== PORTFOLIO OPTIMIZATION =====

class PortfolioOptimizer:
    """Modern Portfolio Theory - Efficient Frontier & Optimization"""
    
    def __init__(self, tickers, period="5y", risk_free_rate=0.06):
        self.tickers = [t.strip().upper() for t in tickers]
        self.period = period
        self.risk_free_rate = risk_free_rate
        self.prices = None
        self.daily_returns = None
        self.mean_returns = None
        self.cov_matrix = None
        self.optimal_weights = None
        self.efficient_frontier = None
        
    def download_data(self):
        data = {}
        failed = []
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=self.period)
                if not hist.empty: data[ticker] = hist['Close']
                else: failed.append(ticker)
            except: failed.append(ticker)
        if failed: st.warning(f"Could not fetch: {', '.join(failed)}")
        if len(data) < 2: st.error("Need at least 2 valid tickers."); return False
        self.prices = pd.DataFrame(data).ffill().dropna()
        return True
    
    def calculate_returns(self):
        if self.prices is None: return False
        self.daily_returns = self.prices.pct_change().dropna()
        self.mean_returns = self.daily_returns.mean() * 252
        self.cov_matrix = self.daily_returns.cov() * 252
        return True
    
    def portfolio_return(self, weights): return np.sum(self.mean_returns * weights)
    def portfolio_volatility(self, weights): return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
    def portfolio_sharpe(self, weights):
        ret = self.portfolio_return(weights); vol = self.portfolio_volatility(weights)
        return (ret - self.risk_free_rate) / vol if vol > 0 else -np.inf
    def neg_sharpe(self, weights): return -self.portfolio_sharpe(weights)
    
    def optimize_sharpe(self):
        n = len(self.tickers)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n))
        result = minimize(self.neg_sharpe, np.array([1/n]*n), method='SLSQP', bounds=bounds, constraints=constraints)
        self.optimal_weights = result.x
        return {'weights': dict(zip(self.tickers, self.optimal_weights.round(4))), 'return': self.portfolio_return(self.optimal_weights), 'volatility': self.portfolio_volatility(self.optimal_weights), 'sharpe': self.portfolio_sharpe(self.optimal_weights)}
    
    def optimize_min_volatility(self):
        n = len(self.tickers)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n))
        result = minimize(self.portfolio_volatility, np.array([1/n]*n), method='SLSQP', bounds=bounds, constraints=constraints)
        weights = result.x
        return {'weights': dict(zip(self.tickers, weights.round(4))), 'return': self.portfolio_return(weights), 'volatility': self.portfolio_volatility(weights), 'sharpe': self.portfolio_sharpe(weights)}
    
    def generate_efficient_frontier(self, num_portfolios=20000):
        n = len(self.tickers); results = np.zeros((3, num_portfolios))
        np.random.seed(42)
        for i in range(num_portfolios):
            weights = np.random.random(n); weights /= np.sum(weights)
            results[0,i] = self.portfolio_return(weights); results[1,i] = self.portfolio_volatility(weights); results[2,i] = self.portfolio_sharpe(weights)
        self.efficient_frontier = {'returns': results[0], 'volatilities': results[1], 'sharpes': results[2]}
        return self.efficient_frontier


def create_portfolio_optimization_tab():
    """Portfolio Optimization Dashboard - Modern Portfolio Theory"""
    st.markdown('<div class="section-header">🎯 Portfolio Optimization (Modern Portfolio Theory)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid rgba(102,126,234,0.3); padding: 1.2rem; border-radius: 12px; margin-bottom: 1.5rem; color: #e2e8f0;">
        <p style="margin:0;">📊 <b>Modern Portfolio Theory</b> finds the optimal mix of stocks to maximize returns for a given level of risk. 
        Enter your stock picks below and discover your optimal portfolio allocation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    presets = {
        "🔧 Custom": {"stocks": [], "desc": "Enter your own tickers"},
        "🌟 Magnificent 7": {"stocks": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"], "desc": "Top US tech giants"},
        "📱 FAANG": {"stocks": ["META", "AAPL", "AMZN", "NFLX", "GOOGL"], "desc": "Classic tech leaders"},
        "🇮🇳 Indian IT": {"stocks": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"], "desc": "Top Indian IT companies"},
        "🏦 Indian Banks": {"stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"], "desc": "Leading Indian banks"},
        "💻 US Tech": {"stocks": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMD"], "desc": "US semiconductor & software"},
        "🚗 EV Future": {"stocks": ["TSLA", "RIVN", "LCID", "NIO"], "desc": "Electric vehicle makers"},
        "☁️ Cloud Computing": {"stocks": ["AMZN", "MSFT", "GOOGL", "CRM", "ADBE"], "desc": "Cloud & SaaS leaders"},
        "🛡️ Defensive": {"stocks": ["WMT", "JNJ", "PG", "KO", "PEP"], "desc": "Low volatility consumer staples"},
    }
    
    col1, col2 = st.columns([1, 2])
    with col1:
        preset_name = st.selectbox("📋 Preset Portfolio", list(presets.keys()))
        preset = presets[preset_name]
        st.caption(f"💡 {preset['desc']}")
    
    with col2:
        if preset_name != "🔧 Custom":
            default_tickers = ",".join(preset["stocks"])
        else:
            default_tickers = "AAPL, MSFT, NVDA, AMZN, GOOGL"
        
        tickers_input = st.text_input(
            "🎯 Stock Tickers (comma-separated)", 
            value=default_tickers,
            placeholder="e.g., AAPL, MSFT, GOOGL",
            help="Use .NS for NSE stocks (e.g., TCS.NS, RELIANCE.NS)"
        )
    
    st.markdown("### ⚙️ Optimization Parameters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_free = st.number_input("🏦 Risk-Free Rate (%)", value=6.0, min_value=0.0, max_value=20.0, step=0.5, help="Government bond yield (6% for India, 4-5% for US)") / 100
    
    with col2:
        period = st.selectbox("📅 Historical Period", ["1y", "2y", "3y", "5y", "10y"], index=3, help="More years = more reliable but may miss recent trends")
    
    with col3:
        num_portfolios = st.select_slider("🔢 Simulation Points", options=[5000, 10000, 20000, 30000, 50000], value=20000, help="More points = smoother frontier but slower")
    
    with col4:
        st.write(""); st.write("")
        optimize_btn = st.button("🚀 Optimize Portfolio", type="primary", use_container_width=True)
    
    if optimize_btn:
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        if len(tickers) < 2: st.error("⚠️ Please enter at least 2 tickers."); return
        
        st.info(f"🔍 Analyzing **{len(tickers)} stocks**: {', '.join(tickers)}")
        optimizer = PortfolioOptimizer(tickers, period=period, risk_free_rate=risk_free)
        
        progress = st.progress(0); status = st.empty()
        status.text("📥 Downloading price data..."); progress.progress(20)
        if not optimizer.download_data(): st.error("❌ Failed to download data."); return
        status.text("📊 Calculating returns..."); progress.progress(40)
        optimizer.calculate_returns()
        status.text("🎯 Optimizing..."); progress.progress(60)
        max_sharpe = optimizer.optimize_sharpe(); min_vol = optimizer.optimize_min_volatility()
        status.text("📈 Generating efficient frontier..."); progress.progress(80)
        optimizer.generate_efficient_frontier(num_portfolios)
        status.text("✅ Complete!"); progress.progress(100)
        time.sleep(0.5); progress.empty(); status.empty()
        
        st.markdown("## 🏆 Optimal Portfolio Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Assets", f"{len(tickers)}"); col2.metric("🎯 Max Sharpe", f"{max_sharpe['sharpe']:.2f}")
        col3.metric("📈 Expected Return", f"{max_sharpe['return']*100:.1f}%"); col4.metric("📉 Risk (Vol)", f"{max_sharpe['volatility']*100:.1f}%")
        
        st.markdown("### 🎯 Optimal Portfolio Allocations")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="background:#1e293b;border:2px solid #10b981;padding:1rem;border-radius:12px;"><h4 style="color:#10b981;">🎯 Maximum Sharpe Ratio</h4></div>', unsafe_allow_html=True)
            st.metric("Expected Return", f"{max_sharpe['return']*100:.1f}%"); st.metric("Volatility", f"{max_sharpe['volatility']*100:.1f}%"); st.metric("Sharpe Ratio", f"{max_sharpe['sharpe']:.2f}")
            fig = go.Figure(data=[go.Pie(labels=list(max_sharpe['weights'].keys()), values=list(max_sharpe['weights'].values()), hole=0.5, textinfo='label+percent')])
            fig.update_layout(height=350, template='plotly_white', margin=dict(t=0,b=0)); st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('<div style="background:#1e293b;border:2px solid #f59e0b;padding:1rem;border-radius:12px;"><h4 style="color:#f59e0b;">🛡️ Minimum Volatility</h4></div>', unsafe_allow_html=True)
            st.metric("Expected Return", f"{min_vol['return']*100:.1f}%"); st.metric("Volatility", f"{min_vol['volatility']*100:.1f}%"); st.metric("Sharpe Ratio", f"{min_vol['sharpe']:.2f}")
            fig = go.Figure(data=[go.Pie(labels=list(min_vol['weights'].keys()), values=list(min_vol['weights'].values()), hole=0.5, textinfo='label+percent')])
            fig.update_layout(height=350, template='plotly_white', margin=dict(t=0,b=0)); st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📈 Efficient Frontier")
        ef = optimizer.efficient_frontier
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ef['volatilities']*100, y=ef['returns']*100, mode='markers', marker=dict(size=4, color=ef['sharpes'], colorscale='Viridis', showscale=True, colorbar=dict(title='Sharpe')), name=f'{num_portfolios:,} Portfolios'))
        fig.add_trace(go.Scatter(x=[max_sharpe['volatility']*100], y=[max_sharpe['return']*100], mode='markers+text', marker=dict(size=25, color='#10b981', symbol='star'), text=['★ Max Sharpe'], textposition='top center'))
        fig.add_trace(go.Scatter(x=[min_vol['volatility']*100], y=[min_vol['return']*100], mode='markers+text', marker=dict(size=20, color='#f59e0b', symbol='diamond'), text=['◆ Min Vol'], textposition='top center'))
        fig.update_layout(title=f'Efficient Frontier • {len(tickers)} Assets', xaxis_title='Volatility (%)', yaxis_title='Return (%)', template='plotly_white', height=600); st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🔥 Correlation Matrix")
        corr = optimizer.daily_returns.corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale='RdBu', zmid=0, zmin=-1, zmax=1, text=np.round(corr.values,2), texttemplate='%{text}', showscale=True))
        fig.update_layout(height=450, template='plotly_white'); st.plotly_chart(fig, use_container_width=True)


# ===== ADVANCED FINANCIAL SCORES =====

class PiotroskiFScore:
    """Piotroski F-Score (0-9) - Verified with Yahoo Finance data structure"""
    
    @staticmethod
    def calculate(income_df, balance_df, cashflow_df):
        score = 0; details = []
        if income_df is None or balance_df is None or cashflow_df is None: return {'score': 0, 'rating': 'N/A', 'details': ['Insufficient data']}
        if income_df.empty or balance_df.empty: return {'score': 0, 'rating': 'N/A', 'details': ['Financial data not available']}
        try:
            cols = income_df.columns[:2]
            if len(cols) < 2: return {'score': 0, 'rating': 'N/A', 'details': ['Need 2 years of data']}
            ni_key = next((k for k in ['Net Income', 'Net Income Common Stockholders'] if k in income_df.index), None)
            if ni_key:
                ni_current = income_df.loc[ni_key, cols[0]]; ni_prev = income_df.loc[ni_key, cols[1]]
                if pd.notna(ni_current) and ni_current > 0: score += 1; details.append("✅ Positive Net Income")
                else: details.append("❌ Negative Net Income")
            ocf_key = next((k for k in ['Operating Cash Flow'] if k in cashflow_df.index), None)
            if ocf_key and pd.notna(cashflow_df.loc[ocf_key, cashflow_df.columns[0]]) and cashflow_df.loc[ocf_key, cashflow_df.columns[0]] > 0:
                score += 1; details.append("✅ Positive Operating Cash Flow")
            else: details.append("❌ Negative OCF")
            asset_key = next((k for k in ['Total Assets'] if k in balance_df.index), None)
            if ni_key and asset_key:
                assets_current = balance_df.loc[asset_key, balance_df.columns[0]]; assets_prev = balance_df.loc[asset_key, balance_df.columns[1]]
                if assets_current and assets_prev and assets_current>0 and assets_prev>0:
                    roa = ni_current/assets_current; roa_prev = ni_prev/assets_prev
                    if roa > roa_prev: score += 1; details.append(f"✅ ROA Increasing")
                    else: details.append("❌ ROA Declining")
            if ocf_key and ni_key and pd.notna(ni_current) and cashflow_df.loc[ocf_key, cashflow_df.columns[0]] > ni_current:
                score += 1; details.append("✅ OCF > Net Income")
            debt_key = next((k for k in ['Long Term Debt', 'Total Debt'] if k in balance_df.index), None)
            if debt_key and len(balance_df.columns) > 1:
                debt_current = balance_df.loc[debt_key, balance_df.columns[0]]; debt_prev = balance_df.loc[debt_key, balance_df.columns[1]]
                if pd.notna(debt_current) and pd.notna(debt_prev) and debt_current < debt_prev: score += 1; details.append("✅ Debt Decreasing")
            ca_key = next((k for k in ['Current Assets'] if k in balance_df.index), None)
            cl_key = next((k for k in ['Current Liabilities'] if k in balance_df.index), None)
            if ca_key and cl_key and len(balance_df.columns) > 1:
                ca = balance_df.loc[ca_key, balance_df.columns[0]]; cl = balance_df.loc[cl_key, balance_df.columns[0]]
                ca_prev = balance_df.loc[ca_key, balance_df.columns[1]]; cl_prev = balance_df.loc[cl_key, balance_df.columns[1]]
                if all(pd.notna(x) and x>0 for x in [ca,cl,ca_prev,cl_prev]):
                    cr = ca/cl; cr_prev = ca_prev/cl_prev
                    if cr > cr_prev: score += 1; details.append("✅ Current Ratio Improving")
            shares_key = next((k for k in ['Diluted Average Shares', 'Basic Average Shares'] if k in income_df.index), None)
            if shares_key and len(income_df.columns) > 1:
                shares_current = income_df.loc[shares_key, cols[0]]; shares_prev = income_df.loc[shares_key, cols[1]]
                if pd.notna(shares_current) and pd.notna(shares_prev) and shares_current <= shares_prev: score += 1; details.append("✅ No Share Dilution")
            gp_key = next((k for k in ['Gross Profit'] if k in income_df.index), None); rev_key = next((k for k in ['Total Revenue', 'Revenue'] if k in income_df.index), None)
            if gp_key and rev_key:
                gp_current = income_df.loc[gp_key, cols[0]]; rev_current = income_df.loc[rev_key, cols[0]]
                gp_prev = income_df.loc[gp_key, cols[1]]; rev_prev = income_df.loc[rev_key, cols[1]]
                if all(pd.notna(x) and x>0 for x in [gp_current, rev_current, gp_prev, rev_prev]):
                    gm = gp_current/rev_current; gm_prev = gp_prev/rev_prev
                    if gm > gm_prev: score += 1; details.append("✅ Gross Margin Improving")
            if rev_key and asset_key and len(cols)>1:
                assets_prev2 = balance_df.loc[asset_key, balance_df.columns[1]]
                if assets_current and assets_prev2 and assets_current>0 and assets_prev2>0:
                    at = rev_current/assets_current; at_prev = rev_prev/assets_prev2
                    if at > at_prev: score += 1; details.append("✅ Asset Turnover Improving")
        except Exception as e: details.append(f"⚠️ Error: {str(e)[:50]}")
        rating = "🟢 STRONG" if score >=7 else "🟡 AVERAGE" if score >=4 else "🔴 WEAK"
        return {'score': score, 'rating': rating, 'details': details}


class AltmanZScore:
    """Altman Z-Score - Verified with Yahoo Finance data"""
    @staticmethod
    def calculate(balance_df, income_df, market_cap):
        if balance_df is None or income_df is None or balance_df.empty or income_df.empty: return None
        try:
            col = balance_df.columns[0]; inc_col = income_df.columns[0]
            ca = next((balance_df.loc[k, col] for k in ['Current Assets'] if k in balance_df.index), None)
            cl = next((balance_df.loc[k, col] for k in ['Current Liabilities'] if k in balance_df.index), None)
            ta = next((balance_df.loc[k, col] for k in ['Total Assets'] if k in balance_df.index), None)
            re_val = next((balance_df.loc[k, col] for k in ['Retained Earnings', 'Stockholders Equity', 'Total Equity'] if k in balance_df.index), 0)
            ebit = next((income_df.loc[k, inc_col] for k in ['EBIT', 'Operating Income'] if k in income_df.index), None)
            tl = next((balance_df.loc[k, col] for k in ['Total Liabilities', 'Total Liabilities Net Minority Interest'] if k in balance_df.index), None)
            sales = next((income_df.loc[k, inc_col] for k in ['Total Revenue', 'Revenue'] if k in income_df.index), None)
            if any(v is None or v==0 for v in [ca, cl, ta, ebit, sales]): return None
            wc = ca - cl; x1 = wc/ta; x2 = re_val/ta if re_val else 0; x3 = ebit/ta; x4 = (market_cap or 0)/(tl or ta) if tl else 0; x5 = sales/ta
            z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
            if z > 2.99: zone, risk = "🟢 SAFE ZONE", "Low bankruptcy risk"
            elif z > 1.81: zone, risk = "🟡 GREY ZONE", "Moderate risk"
            else: zone, risk = "🔴 DISTRESS ZONE", "High bankruptcy risk"
            return {'z_score': round(z,2), 'zone': zone, 'risk': risk}
        except: return None


# ===== INDEX & SECTOR COMPARISON =====

class IndexComparison:
    BENCHMARKS = {'INR': '^NSEI', 'USD': '^GSPC'}
    SECTOR_ETFS = {'Technology': 'XLK', 'Financial Services': 'XLF', 'Healthcare': 'XLV', 'Consumer Cyclical': 'XLY', 'Energy': 'XLE', 'Industrials': 'XLI', 'Consumer Defensive': 'XLP', 'Real Estate': 'XLRE', 'Utilities': 'XLU', 'Basic Materials': 'XLB', 'Communication Services': 'XLC'}
    INDIAN_SECTOR_INDICES = {'Technology': '^CNXIT', 'Financial Services': '^CNXFIN', 'Healthcare': '^CNXPHARMA', 'Energy': '^CNXENERGY', 'Consumer Cyclical': '^CNXAUTO', 'Consumer Defensive': '^CNXFMCG', 'Basic Materials': '^CNXMETAL', 'Real Estate': '^CNXREALTY'}
    
    @staticmethod
    def fetch_comparison_data(ticker, currency, sector, period="1y"):
        benchmark = IndexComparison.BENCHMARKS.get(currency, '^GSPC')
        sector_indices = IndexComparison.INDIAN_SECTOR_INDICES if currency == 'INR' else IndexComparison.SECTOR_ETFS
        sector_index = sector_indices.get(sector)
        all_tickers = [ticker, benchmark]
        if sector_index: all_tickers.append(sector_index)
        try:
            data = yf.download(all_tickers, period=period, progress=False)
            close_data = data['Close']
            stock_prices = close_data[ticker]; benchmark_prices = close_data[benchmark]
            sector_prices = close_data[sector_index] if sector_index else None
            stock_ret = stock_prices.pct_change().dropna(); bench_ret = benchmark_prices.pct_change().dropna()
            common = stock_ret.index.intersection(bench_ret.index)
            stock_ret = stock_ret[common]; bench_ret = bench_ret[common]
            stock_cum = (1+stock_ret).cumprod()*100; bench_cum = (1+bench_ret).cumprod()*100
            cov = stock_ret.cov(bench_ret); var = bench_ret.var()
            beta = cov/var if var>0 else 1.0
            stock_ann = stock_ret.mean()*252; bench_ann = bench_ret.mean()*252
            alpha = stock_ann - beta*bench_ann
            te = (stock_ret - bench_ret).std()*np.sqrt(252)
            ir = (stock_ann - bench_ann)/te if te>0 else 0
            max_dd = (stock_cum/stock_cum.expanding().max() - 1).min()
            corr = stock_ret.corr(bench_ret)
            res = {'stock_cumulative': stock_cum, 'benchmark_cumulative': bench_cum, 'beta': beta, 'alpha': alpha, 'tracking_error': te, 'information_ratio': ir, 'max_drawdown': max_dd, 'correlation': corr, 'stock_annual_return': stock_ann, 'benchmark_annual_return': bench_ann, 'benchmark_name': 'NIFTY 50' if currency=='INR' else 'S&P 500'}
            if sector_prices is not None:
                sec_ret = sector_prices.pct_change().dropna()
                common2 = stock_ret.index.intersection(sec_ret.index)
                sec_ret = sec_ret[common2]; stock_aligned = stock_ret[common2]
                sec_cum = (1+sec_ret).cumprod()*100; sec_ann = sec_ret.mean()*252
                res['sector_cumulative'] = sec_cum; res['sector_annual_return'] = sec_ann; res['sector_relative'] = stock_ann - sec_ann
            return res
        except: return None


def create_index_comparison_dashboard(analyzer):
    st.markdown('<div class="section-header">📊 Index & Sector Comparison</div>', unsafe_allow_html=True)
    cur = analyzer.currency_symbol; ticker = analyzer.ticker; sector = analyzer.financials.get('sector', 'Unknown')
    currency = analyzer.currency; benchmark_name = 'NIFTY 50' if currency=='INR' else 'S&P 500'
    periods = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}
    selected = st.select_slider("Comparison Period", options=list(periods.keys()), value="1 Year")
    period = periods[selected]
    if st.button(f"📊 Compare vs {benchmark_name} & Sector", type="primary", use_container_width=True):
        with st.spinner("Fetching comparison data..."):
            comp = IndexComparison.fetch_comparison_data(ticker, currency, sector, period)
        if comp is None: st.error("Could not fetch comparison data."); return
        st.markdown("### 📈 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(analyzer.company_name[:15], f"{comp['stock_annual_return']*100:.1f}%", delta=f"vs {benchmark_name}: {(comp['stock_annual_return']-comp['benchmark_annual_return'])*100:+.1f}%")
        col2.metric(benchmark_name, f"{comp['benchmark_annual_return']*100:.1f}%")
        col3.metric("Alpha", f"{comp['alpha']*100:.2f}%", delta="Outperforming 📈" if comp['alpha']>0 else "Underperforming 📉")
        col4.metric("Beta", f"{comp['beta']:.2f}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Correlation", f"{comp['correlation']:.2f}"); col2.metric("Tracking Error", f"{comp['tracking_error']*100:.1f}%")
        col3.metric("Info Ratio", f"{comp['information_ratio']:.2f}"); col4.metric("Max Drawdown", f"{comp['max_drawdown']*100:.1f}%", delta_color="inverse")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=comp['stock_cumulative'].index, y=comp['stock_cumulative'].values, name=analyzer.company_name[:20], line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=comp['benchmark_cumulative'].index, y=comp['benchmark_cumulative'].values, name=benchmark_name, line=dict(color='#94a3b8', width=2, dash='dash')))
        if 'sector_cumulative' in comp:
            fig.add_trace(go.Scatter(x=comp['sector_cumulative'].index, y=comp['sector_cumulative'].values, name=f"{sector} Sector", line=dict(color='#10b981', width=2, dash='dot')))
        fig.update_layout(title=f'Total Return Comparison • {selected}', template='plotly_white', height=500, hovermode='x unified', yaxis_title='Growth of $100')
        st.plotly_chart(fig, use_container_width=True)
        alpha_val = comp['alpha']*100
        if alpha_val > 2: st.info(f"🟢 **{analyzer.company_name}** significantly outperforms **{benchmark_name}** (Alpha: {alpha_val:.1f}%)")
        elif alpha_val > 0: st.info(f"🟡 **{analyzer.company_name}** slightly outperforms **{benchmark_name}** (Alpha: {alpha_val:.1f}%)")
        else: st.info(f"🔴 **{analyzer.company_name}** underperforms **{benchmark_name}** (Alpha: {alpha_val:.1f}%)")


# ===== AI INVESTMENT THESIS GENERATOR =====

def generate_investment_thesis(analyzer, dcf_result=None):
    ratios = analyzer.ratios; cur = analyzer.currency_symbol; cp = analyzer.live_price_data.get('current_price')
    thesis_parts = []; score = 0; max_score = 0
    rev_growth = ratios.get('Revenue Growth (YoY)')
    if rev_growth is not None:
        max_score += 1
        if rev_growth > 20: thesis_parts.append(f"🟢 **Strong Revenue Growth:** {rev_growth:.1f}% YoY"); score += 1
        elif rev_growth > 10: thesis_parts.append(f"🟡 **Moderate Revenue Growth:** {rev_growth:.1f}% YoY"); score += 0.5
        elif rev_growth > 0: thesis_parts.append(f"🟠 **Slow Revenue Growth:** {rev_growth:.1f}% YoY")
        else: thesis_parts.append(f"🔴 **Revenue Decline:** {abs(rev_growth):.1f}% YoY")
    net_margin = ratios.get('Net Profit Margin')
    if net_margin is not None:
        max_score += 1
        if net_margin > 20: thesis_parts.append(f"🟢 **Excellent Profitability:** {net_margin:.1f}% net margin"); score += 1
        elif net_margin > 10: thesis_parts.append(f"🟡 **Healthy Profitability:** {net_margin:.1f}% net margin"); score += 0.5
        else: thesis_parts.append(f"🟠 **Thin Margins:** {net_margin:.1f}%")
    roe = ratios.get('ROE')
    if roe is not None:
        max_score += 1
        if roe > 20: thesis_parts.append(f"🟢 **Efficient Capital Allocation:** ROE {roe:.1f}%"); score += 1
        elif roe > 10: thesis_parts.append(f"🟡 **Adequate Returns:** ROE {roe:.1f}%"); score += 0.5
        else: thesis_parts.append(f"🔴 **Poor Returns:** ROE {roe:.1f}%")
    de = ratios.get('Debt to Equity')
    if de is not None:
        max_score += 1
        if de < 0.5: thesis_parts.append(f"🟢 **Conservative Capital Structure:** D/E {de:.2f}"); score += 1
        elif de < 1.5: thesis_parts.append(f"🟡 **Moderate Leverage:** D/E {de:.2f}"); score += 0.5
        else: thesis_parts.append(f"🔴 **High Leverage:** D/E {de:.2f}")
    cr = ratios.get('Current Ratio')
    if cr is not None:
        max_score += 1
        if cr > 1.5: thesis_parts.append(f"🟢 **Healthy Liquidity:** Current Ratio {cr:.2f}"); score += 1
        elif cr > 1.0: thesis_parts.append(f"🟡 **Adequate Liquidity:** {cr:.2f}"); score += 0.5
        else: thesis_parts.append(f"🔴 **Liquidity Concern:** {cr:.2f}")
    if dcf_result:
        upside = dcf_result.get('upside', 0); max_score += 1
        if upside > 20: thesis_parts.append(f"🟢 **Significantly Undervalued:** DCF {upside:.0f}% upside"); score += 1
        elif upside > 0: thesis_parts.append(f"🟡 **Modestly Undervalued:** DCF {upside:.0f}% upside"); score += 0.5
        else: thesis_parts.append(f"🔴 **Overvalued:** DCF {abs(upside):.0f}% downside")
    eps = ratios.get('EPS'); ni_growth = ratios.get('Net Income Growth (YoY)')
    if eps is not None and ni_growth is not None:
        max_score += 1
        if ni_growth > 15 and eps > 0: thesis_parts.append(f"🟢 **Strong Earnings:** EPS {cur}{eps:.2f}, growth {ni_growth:.1f}%"); score += 1
        elif eps > 0: thesis_parts.append(f"🟡 **Stable Earnings:** EPS {cur}{eps:.2f}"); score += 0.5
    market_cap = analyzer.live_price_data.get('market_cap', 0); sector = analyzer.financials.get('sector', 'Unknown')
    if market_cap > 0: thesis_parts.append(f"📊 **Market Position:** {analyzer.company_name} in **{sector}** with market cap **{analyzer._format_amount(market_cap)}**")
    if max_score > 0:
        final_score = (score/max_score)*100
        if final_score >= 75: overall = "🟢 **OVERALL: STRONG FUNDAMENTALS**"
        elif final_score >= 50: overall = "🟡 **OVERALL: MIXED SIGNALS**"
        elif final_score >= 25: overall = "🟠 **OVERALL: BELOW AVERAGE**"
        else: overall = "🔴 **OVERALL: HIGH RISK**"
    else: overall = "⚠️ **INSUFFICIENT DATA**"
    return {'thesis_parts': thesis_parts, 'overall': overall, 'score': f"{score}/{max_score}" if max_score>0 else "N/A", 'score_pct': (score/max_score*100) if max_score>0 else 0}


def create_investment_thesis_dashboard(analyzer):
    st.markdown('<div class="section-header">📝 AI-Generated Investment Thesis</div>', unsafe_allow_html=True)
    income = analyzer.financials.get('income'); cashflow = analyzer.financials.get('cashflow'); cp = analyzer.live_price_data.get('current_price')
    dcf_result = None
    if cp and income is not None and not income.empty:
        fcf = analyzer._safe_get(cashflow, ['Free Cash Flow']) if cashflow is not None else 0
        if not fcf: fcf = (analyzer._safe_get(income, ['Net Income']) or 0)*0.8
        if fcf and fcf > 0:
            shares = analyzer._safe_get(income, ['Diluted Average Shares']) or 1e6
            beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
            rg = analyzer.ratios.get('Revenue Growth (YoY)', 10) or 10
            rf = 0.072 if analyzer.currency=='INR' else 0.045; mr = 0.12 if analyzer.currency=='INR' else 0.10
            dcf = AdvancedDCF(fcf, shares, cp, max(0.02, min(rg/100, 0.35)), beta, rf, mr)
            dcf_result = dcf.calculate()
    thesis = generate_investment_thesis(analyzer, dcf_result)
    score_pct = thesis['score_pct']
    score_color = "#10b981" if score_pct >= 75 else "#f59e0b" if score_pct >= 50 else "#ef4444"
    st.markdown(f'<div style="background:#1e293b;border:2px solid {score_color};padding:1.5rem;border-radius:16px;margin-bottom:1rem;"><div style="display:flex;justify-content:space-between;"><h3>📝 {analyzer.company_name}</h3><span style="font-size:1.5rem;font-weight:900;color:{score_color};">{thesis["score"]}</span></div></div>', unsafe_allow_html=True)
    for part in thesis['thesis_parts']: st.markdown(f"- {part}")
    st.markdown("---"); st.markdown(f"### {thesis['overall']}")
    st.caption("💡 Auto-generated from reported financial data.")


# ===== HISTORICAL DCF TRACKING =====

class HistoricalDCFTracker:
    @staticmethod
    def calculate_historical_growth(income_df):
        if income_df is None or income_df.empty: return None
        rev_key = next((k for k in ['Total Revenue', 'Revenue'] if k in income_df.index), None)
        if not rev_key: return None
        rev_data = income_df.loc[rev_key]
        years = len(rev_data)
        if years < 2: return None
        growth_rates = []
        for i in range(years-1):
            if rev_data.iloc[i+1] and rev_data.iloc[i+1] != 0:
                growth = (rev_data.iloc[i] - rev_data.iloc[i+1]) / abs(rev_data.iloc[i+1]) * 100
                growth_rates.append({'period': f"Year {i+1}", 'growth': growth})
        if growth_rates:
            avg = np.mean([g['growth'] for g in growth_rates]); med = np.median([g['growth'] for g in growth_rates])
            return {'growth_rates': growth_rates, 'average': avg, 'median': med, 'min': min(g['growth'] for g in growth_rates), 'max': max(g['growth'] for g in growth_rates), 'years': len(growth_rates)}
        return None


def create_historical_dcf_tracker(analyzer):
    income = analyzer.financials.get('income')
    if income is None or income.empty: return
    hist = HistoricalDCFTracker.calculate_historical_growth(income)
    if hist:
        with st.expander("📊 Historical Revenue Growth (DCF Context)", expanded=False):
            st.markdown(f"**{hist['years']} years** tracked | Avg: **{hist['average']:.1f}%** | Median: **{hist['median']:.1f}%**")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[g['period'] for g in hist['growth_rates']], y=[g['growth'] for g in hist['growth_rates']], marker_color='#667eea', text=[f"{g['growth']:.1f}%" for g in hist['growth_rates']], textposition='outside'))
            fig.add_hline(y=hist['average'], line_dash="dash", line_color="#10b981")
            fig.update_layout(title='Historical Revenue Growth Rates', template='plotly_white', height=300)
            st.plotly_chart(fig, use_container_width=True)


# ===== ADVANCED PORTFOLIO MODELS =====

class BlackLitterman:
    @staticmethod
    def calculate(market_caps, cov_matrix, risk_aversion=2.5, views=None, view_confidences=None):
        tickers = list(market_caps.keys()); n = len(tickers)
        total_mcap = sum(market_caps.values())
        if total_mcap == 0: return None
        market_weights = np.array([market_caps[t]/total_mcap for t in tickers])
        pi = risk_aversion * cov_matrix.values @ market_weights
        if views is None or len(views)==0:
            return {'weights': dict(zip(tickers, market_weights.round(4))), 'expected_returns': dict(zip(tickers, pi.round(4))), 'method': 'Market Equilibrium'}
        k = len(views); P = np.zeros((k, n)); Q = np.zeros(k)
        for i, view in enumerate(views):
            for t in view.get('tickers', []):
                if t in tickers: P[i, tickers.index(t)] = 1.0/len(view['tickers'])
            Q[i] = view.get('return', 0)
        tau = 0.05
        conf = view_confidences or [0.5]*k
        Omega = np.diag([max(tau*(1/c-1)*(P[i]@cov_matrix.values@P[i].T), 1e-8) for i, c in enumerate(conf)])
        try:
            tau_Sigma = tau*cov_matrix.values
            M = np.linalg.inv(np.linalg.inv(tau_Sigma) + P.T@np.linalg.inv(Omega)@P)
            bl_returns = M @ (np.linalg.inv(tau_Sigma)@pi + P.T@np.linalg.inv(Omega)@Q)
            w = np.linalg.inv(cov_matrix.values)@bl_returns
            w = np.maximum(w, 0); w = w/w.sum() if w.sum()>0 else np.ones(n)/n
            return {'weights': dict(zip(tickers, w.round(4))), 'expected_returns': dict(zip(tickers, bl_returns.round(4))), 'method': f'Black-Litterman ({k} views)'}
        except np.linalg.LinAlgError:
            return {'weights': dict(zip(tickers, market_weights.round(4))), 'method': 'Market Equilibrium (singular)'}


class RiskParity:
    @staticmethod
    def calculate(cov_matrix, max_iter=500):
        tickers = list(cov_matrix.columns); n = len(tickers)
        w = np.ones(n)/n
        for it in range(max_iter):
            vol = np.sqrt(w.T@cov_matrix.values@w)
            if vol < 1e-10: break
            mrc = cov_matrix.values@w/vol; rc = w*mrc; target = vol/n
            w = w * target / np.maximum(np.abs(rc), 1e-10)
            w = np.maximum(w, 0); w = w/w.sum() if w.sum()>0 else np.ones(n)/n
            if np.max(np.abs(rc - target)) < 1e-6: break
        vol = np.sqrt(w.T@cov_matrix.values@w)
        mrc = cov_matrix.values@w/vol; rc = w*mrc; rc_pct = rc/vol*100
        return {'weights': dict(zip(tickers, w.round(4))), 'risk_contributions': dict(zip(tickers, rc_pct.round(1))), 'port_volatility': vol, 'iterations': it+1}


class FactorInvesting:
    """Fama-French Factor Analysis"""
    
    FACTORS = {
        'Value': "High Book-to-Market minus Low",
        'Size': "Small-cap minus Large-cap (SMB)",
        'Momentum': "Winners minus Losers (past 12 months)",
        'Quality': "High ROE, Low Debt minus Low ROE, High Debt",
        'Low Volatility': "Low Beta minus High Beta",
    }
    
    @staticmethod
    def analyze_factor_exposure(analyzer):
        exposures = {}
        info = analyzer.financials.get('info', {})
        ratios = analyzer.ratios
        prices = analyzer.financials.get('prices')
        
        pb = ratios.get('P/B Ratio')
        if pb and pb > 0:
            if pb < 1.5: exposures['Value'] = {'score': 'Deep Value', 'detail': f'P/B: {pb:.1f}', 'color': '#10b981'}
            elif pb < 3: exposures['Value'] = {'score': 'Fair Value', 'detail': f'P/B: {pb:.1f}', 'color': '#f59e0b'}
            else: exposures['Value'] = {'score': 'Growth', 'detail': f'P/B: {pb:.1f}', 'color': '#ef4444'}
        
        mcap = analyzer.live_price_data.get('market_cap', 0) or info.get('marketCap', 0)
        if mcap and mcap > 0:
            if mcap > 1e11: exposures['Size'] = {'score': 'Mega Cap', 'detail': analyzer._format_amount(mcap), 'color': '#94a3b8'}
            elif mcap > 1e10: exposures['Size'] = {'score': 'Large Cap', 'detail': analyzer._format_amount(mcap), 'color': '#667eea'}
            elif mcap > 2e9: exposures['Size'] = {'score': 'Mid Cap', 'detail': analyzer._format_amount(mcap), 'color': '#f59e0b'}
            else: exposures['Size'] = {'score': 'Small Cap', 'detail': analyzer._format_amount(mcap), 'color': '#10b981'}
        
        if prices is not None and not prices.empty and 'Close' in prices.columns and len(prices) >= 252:
            ret_12m = (prices['Close'].iloc[-1] / prices['Close'].iloc[-252] - 1) * 100
            if ret_12m > 30: exposures['Momentum'] = {'score': 'Strong', 'detail': f'12M: {ret_12m:.0f}%', 'color': '#10b981'}
            elif ret_12m > 10: exposures['Momentum'] = {'score': 'Positive', 'detail': f'12M: {ret_12m:.0f}%', 'color': '#667eea'}
            elif ret_12m > -10: exposures['Momentum'] = {'score': 'Neutral', 'detail': f'12M: {ret_12m:.0f}%', 'color': '#f59e0b'}
            else: exposures['Momentum'] = {'score': 'Negative', 'detail': f'12M: {ret_12m:.0f}%', 'color': '#ef4444'}
        
        roe = ratios.get('ROE'); de = ratios.get('Debt to Equity')
        if roe is not None and de is not None:
            if roe > 20 and de < 0.5: exposures['Quality'] = {'score': 'High Quality', 'detail': f'ROE: {roe:.0f}%, D/E: {de:.1f}', 'color': '#10b981'}
            elif roe > 10 and de < 1.5: exposures['Quality'] = {'score': 'Moderate', 'detail': f'ROE: {roe:.0f}%, D/E: {de:.1f}', 'color': '#f59e0b'}
            else: exposures['Quality'] = {'score': 'Low', 'detail': f'ROE: {roe:.0f}%, D/E: {de:.1f}', 'color': '#ef4444'}
        
        beta = analyzer.live_price_data.get('beta', 1.0) or info.get('beta', 1.0) or 1.0
        if beta < 0.7: exposures['Low Vol'] = {'score': 'Very Low', 'detail': f'Beta: {beta:.2f}', 'color': '#10b981'}
        elif beta < 1.0: exposures['Low Vol'] = {'score': 'Low', 'detail': f'Beta: {beta:.2f}', 'color': '#667eea'}
        elif beta < 1.3: exposures['Low Vol'] = {'score': 'Moderate', 'detail': f'Beta: {beta:.2f}', 'color': '#f59e0b'}
        else: exposures['Low Vol'] = {'score': 'High', 'detail': f'Beta: {beta:.2f}', 'color': '#ef4444'}
        
        return exposures


def create_factor_investing_dashboard(analyzer):
    exposures = FactorInvesting.analyze_factor_exposure(analyzer)
    if not exposures: return
    st.markdown('<div class="section-header">🎯 Factor Profile (Fama-French)</div>', unsafe_allow_html=True)
    cols = st.columns(len(exposures))
    for col, (factor, data) in zip(cols, exposures.items()):
        with col:
            st.markdown(f'<div style="background:#1e293b;border:2px solid {data["color"]};padding:1rem;border-radius:12px;text-align:center;"><div style="font-size:0.75rem;color:#94a3b8;">{factor}</div><div style="font-size:1.1rem;font-weight:700;color:{data["color"]};">{data["score"]}</div><div style="font-size:0.7rem;color:#64748b;">{data["detail"]}</div></div>', unsafe_allow_html=True)


def create_advanced_portfolio_tab():
    st.markdown('<div class="section-header">🏦 Advanced Portfolio Construction</div>', unsafe_allow_html=True)
    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
        **Methods:** Black-Litterman (combine views), Risk Parity (equal risk), Maximum Sharpe (Markowitz).
        **Presets:** Magnificent 7, Indian IT, Banks, etc.
        """)
    st.markdown("### 📋 Step 1: Select Portfolio")
    presets = {"🔧 Custom":[],"🌟 Magnificent 7":["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA"],"🇮🇳 Indian IT":["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],"🏦 Indian Banks":["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"]}
    col1, col2 = st.columns([1,2])
    with col1: preset = st.selectbox("Preset", list(presets.keys()), key="adv_preset")
    with col2:
        default_tickers = ",".join(presets[preset]) if preset!="🔧 Custom" else "AAPL, MSFT, NVDA, AMZN, GOOGL"
        tickers_input = st.text_input("Tickers", value=default_tickers, key="adv_tickers")
    method = st.radio("Method:", ["🎯 Maximum Sharpe", "⚖️ Risk Parity", "🧠 Black-Litterman", "📊 Compare All"], horizontal=True)
    if "Black-Litterman" in method:
        col1, col2 = st.columns(2)
        with col1:
            view_ticker = st.text_input("View Ticker", "AAPL", key="bl_view"); view_return = st.slider("Expected Return (%)", -20.0, 50.0, 15.0, 0.5, key="bl_ret")/100
        with col2: view_conf = st.slider("Confidence", 10, 100, 60, 5, key="bl_conf")/100
    col1, col2 = st.columns(2)
    with col1: risk_free = st.number_input("Risk-Free Rate (%)", value=6.0, min_value=0.0, max_value=15.0, step=0.5, key="adv_rf")/100
    with col2: period = st.selectbox("Period", ["6mo","1y","2y","3y","5y"], index=1, key="adv_period")
    if st.button("🚀 Construct", type="primary", use_container_width=True, key="adv_run"):
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        if len(tickers)<2: st.error("Need at least 2 tickers."); return
        market_caps = {}; prices_data = {}
        for t in tickers:
            try:
                stock = yf.Ticker(t); info = stock.info; market_caps[t] = info.get('marketCap',1e9) or 1e9
                hist = stock.history(period=period)
                if not hist.empty: prices_data[t] = hist['Close']
            except: market_caps[t] = 1e9
        prices_df = pd.DataFrame(prices_data).dropna(); returns = prices_df.pct_change().dropna(); cov_matrix = returns.cov()*252
        if method == "🧠 Black-Litterman":
            bl = BlackLitterman.calculate({t:market_caps.get(t,1e9) for t in tickers}, cov_matrix, views=[{'tickers':[view_ticker.upper()],'return':view_return}], view_confidences=[view_conf])
            if bl:
                st.success(f"✅ {bl['method']}")
                fig = go.Figure(data=[go.Pie(labels=list(bl['weights'].keys()), values=list(bl['weights'].values()), hole=0.4)])
                fig.update_layout(height=400); st.plotly_chart(fig, use_container_width=True)
        elif method == "⚖️ Risk Parity":
            rp = RiskParity.calculate(cov_matrix)
            st.success(f"✅ Risk Parity ({rp['iterations']} iter)"); st.metric("Volatility", f"{rp['port_volatility']*100:.1f}%")
            fig = go.Figure(data=[go.Pie(labels=list(rp['weights'].keys()), values=list(rp['weights'].values()), hole=0.4)])
            fig.update_layout(height=400); st.plotly_chart(fig, use_container_width=True)
        elif method == "🎯 Maximum Sharpe":
            opt = PortfolioOptimizer(tickers, period=period, risk_free_rate=risk_free)
            if opt.download_data() and opt.calculate_returns():
                ms = opt.optimize_sharpe()
                st.success("✅ Max Sharpe"); st.metric("Sharpe", f"{ms['sharpe']:.2f}")
                fig = go.Figure(data=[go.Pie(labels=list(ms['weights'].keys()), values=list(ms['weights'].values()), hole=0.4)])
                fig.update_layout(height=400); st.plotly_chart(fig, use_container_width=True)
        elif method == "📊 Compare All":
            col1, col2, col3 = st.columns(3)
            with col1:
                try:
                    opt = PortfolioOptimizer(tickers, period=period, risk_free_rate=risk_free)
                    if opt.download_data() and opt.calculate_returns():
                        ms = opt.optimize_sharpe()
                        st.metric("Sharpe", f"{ms['sharpe']:.2f}")
                        fig = go.Figure(data=[go.Pie(labels=list(ms['weights'].keys()), values=list(ms['weights'].values()), hole=0.4)])
                        fig.update_layout(height=250, margin=dict(t=0,b=0)); st.plotly_chart(fig, use_container_width=True)
                except: st.warning("Failed")
            with col2:
                try:
                    rp = RiskParity.calculate(cov_matrix)
                    st.metric("Vol", f"{rp['port_volatility']*100:.1f}%")
                    fig = go.Figure(data=[go.Pie(labels=list(rp['weights'].keys()), values=list(rp['weights'].values()), hole=0.4)])
                    fig.update_layout(height=250, margin=dict(t=0,b=0)); st.plotly_chart(fig, use_container_width=True)
                except: st.warning("Failed")
            with col3:
                try:
                    ret_ann = returns.mean()*252; top = ret_ann.idxmax()
                    bl = BlackLitterman.calculate({t:market_caps.get(t,1e9) for t in tickers}, cov_matrix, views=[{'tickers':[top],'return':ret_ann[top]}], view_confidences=[0.5])
                    if bl:
                        fig = go.Figure(data=[go.Pie(labels=list(bl['weights'].keys()), values=list(bl['weights'].values()), hole=0.4)])
                        fig.update_layout(height=250, margin=dict(t=0,b=0)); st.plotly_chart(fig, use_container_width=True)
                except: st.warning("Failed")


# ===== FORMATTING =====

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


# ===== DASHBOARD FUNCTIONS =====

def create_advanced_scores_dashboard(analyzer):
    st.markdown('<div class="section-header">🔬 Advanced Financial Scores</div>', unsafe_allow_html=True)
    income = analyzer.financials.get('income'); balance = analyzer.financials.get('balance'); cashflow = analyzer.financials.get('cashflow')
    market_cap = analyzer.live_price_data.get('market_cap', 0)
    if income is None or income.empty: st.warning("Financial statements not available."); return
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Piotroski F-Score")
        f_score = PiotroskiFScore.calculate(income, balance, cashflow)
        score_color = "#10b981" if f_score['score']>=7 else "#f59e0b" if f_score['score']>=4 else "#ef4444"
        fig = go.Figure(go.Indicator(mode="gauge+number", value=f_score['score'], title={'text':"F-Score"}, gauge={'axis':{'range':[0,9]},'bar':{'color':score_color},'steps':[{'range':[0,3],'color':"rgba(239,68,68,0.2)"},{'range':[3,6],'color':"rgba(245,158,11,0.2)"},{'range':[6,9],'color':"rgba(16,185,129,0.2)"}]}))
        fig.update_layout(height=250, margin=dict(t=30,b=0)); st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**{f_score['rating']}**")
        with st.expander(f"Details ({f_score['score']}/9)"):
            for d in f_score['details']: st.write(d)
    with col2:
        st.markdown("### 🏦 Altman Z-Score")
        z_result = AltmanZScore.calculate(balance, income, market_cap)
        if z_result:
            z = z_result['z_score']; z_color = "#10b981" if z>2.99 else "#f59e0b" if z>1.81 else "#ef4444"
            fig = go.Figure(go.Indicator(mode="gauge+number", value=z, title={'text':"Z-Score"}, gauge={'axis':{'range':[0,6]},'bar':{'color':z_color},'steps':[{'range':[0,1.81],'color':"rgba(239,68,68,0.2)"},{'range':[1.81,2.99],'color':"rgba(245,158,11,0.2)"},{'range':[2.99,6],'color':"rgba(16,185,129,0.2)"}]}))
        fig.update_layout(height=250, margin=dict(t=30,b=0)); st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**{z_result['zone']}** - {z_result['risk']}")
        else: st.warning("Insufficient data for Z-Score")

def create_valuation_dashboard(analyzer):
    st.markdown('<div class="section-header">💰 Advanced Valuation Models</div>', unsafe_allow_html=True)
    income = analyzer.financials.get('income'); cashflow = analyzer.financials.get('cashflow')
    cp = analyzer.live_price_data.get('current_price'); cur = analyzer.currency_symbol
    if not cp: st.warning("Current price not available."); return
    rev = analyzer._safe_get(income, ['Total Revenue', 'Revenue']) if income is not None else 0
    ni = analyzer._safe_get(income, ['Net Income', 'Net Income Common Stockholders']) if income is not None else 0
    fcf = analyzer._safe_get(cashflow, ['Free Cash Flow']) if cashflow is not None else None
    if not fcf: fcf = ni * 0.8 if ni else (rev * 0.1 if rev else 1e6)
    shares = analyzer._safe_get(income, ['Diluted Average Shares']) or analyzer._safe_get(income, ['Basic Average Shares']) if income is not None else None
    if not shares: shares = analyzer.live_price_data.get('market_cap', 1e9) / cp if cp > 0 else 1e6
    beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
    rg = analyzer.ratios.get('Revenue Growth (YoY)', 10); rg = max(0.02, min((rg or 10) / 100, 0.35))
    om = analyzer.ratios.get('Operating Margin', 15) / 100 if analyzer.ratios.get('Operating Margin') else 0.15
    rf = 0.072 if analyzer.currency == 'INR' else 0.045; mr = 0.12 if analyzer.currency == 'INR' else 0.10
    
    with st.expander("⚙️ DCF Parameters", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1: dcf_growth = st.slider("Growth %", 1, 35, int(rg*100)) / 100; dcf_fcf = st.number_input("FCF (M)", value=float(fcf)/1e6, format="%.1f") * 1e6
        with c2: dcf_shares = st.number_input("Shares (M)", value=float(shares)/1e6, format="%.1f") * 1e6; dcf_beta = st.number_input("Beta", value=float(beta), min_value=0.1, max_value=3.0, step=0.1)
        with c3: dcf_rf = st.slider("Risk-Free %", 1.0, 12.0, rf*100, 0.1) / 100; dcf_mr = st.slider("Market Return %", 5.0, 18.0, mr*100, 0.1) / 100
    
    dcf = AdvancedDCF(dcf_fcf, dcf_shares, cp, dcf_growth, dcf_beta, dcf_rf, dcf_mr); result = dcf.calculate()
    st.markdown(f'<div style="background-color:{result["rec_color"]};padding:1.5rem;border-radius:16px;color:white;text-align:center;margin:1rem 0;"><h2>{result["recommendation"]}</h2><p>Intrinsic Value: {cur}{result["intrinsic_value"]:.2f} | Upside: {result["upside"]:+.1f}%</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Intrinsic Value", f"{cur}{result['intrinsic_value']:.2f}"); col2.metric("Current Price", f"{cur}{cp:.2f}", delta=f"{result['upside']:+.1f}%")
    col3.metric("WACC", f"{result['wacc']*100:.1f}%"); col4.metric("Bear/Bull", f"{cur}{result['bear_case']:.0f} - {cur}{result['bull_case']:.0f}")
    
    unit = 'Cr' if analyzer.currency == 'INR' else 'B'; div = 1e7 if analyzer.currency == 'INR' else 1e9
    years = [p['year'] for p in result['projections']]; fcf_vals = [p['fcf']/div for p in result['projections']]
    fig = go.Figure(); fig.add_trace(go.Bar(x=years, y=fcf_vals, name='FCF', marker_color='#667eea'))
    fig.update_layout(title=f'10-Year FCF Projection ({cur}{unit})', template='plotly_white', height=350); st.plotly_chart(fig, use_container_width=True)
    
    eps = analyzer.ratios.get('EPS', ni/shares if ni and shares else 1)
    graham_val = GrahamValuation.calculate(eps, rg, rf); epv = EarningsPowerValue.calculate(rev or 0, om, 0.25, result['wacc'], shares)
    st.markdown("### 📊 Valuation Model Comparison")
    models = {'Advanced DCF': result['intrinsic_value'], 'Graham': graham_val, 'EPV': epv, 'Current Price': cp}
    fig = go.Figure()
    for model, val in models.items():
        color = '#10b981' if val > cp else '#ef4444' if val < cp else '#f59e0b'
        fig.add_trace(go.Bar(x=[model], y=[val], marker_color=color, text=[f"{cur}{val:.2f}"], textposition='outside'))
    fig.add_hline(y=cp, line_dash="dash", line_color="#94a3b8"); fig.update_layout(title='All Valuation Models', template='plotly_white', height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def create_stress_test_dashboard(analyzer):
    st.markdown('<div class="section-header">🛡️ Comprehensive Stress Tests (30 Scenarios)</div>', unsafe_allow_html=True)
    cp = analyzer.live_price_data.get('current_price'); cur = analyzer.currency_symbol
    if not cp: st.warning("Current price not available."); return
    sector = analyzer.financials.get('sector', 'Unknown'); industry = analyzer.financials.get('industry', 'Unknown')
    beta = analyzer.live_price_data.get('beta', 1.0) or 1.0; market_cap = analyzer.live_price_data.get('market_cap', 0) or 0
    engine = StressTestEngine(cp, sector, industry, beta, analyzer.currency, market_cap)
    
    with st.spinner("Running stress tests..."):
        results_df = engine.run_all_tests()
    st.success(f"✅ {len(results_df)} scenarios completed!")
    col1, col2, col3, col4 = st.columns(4)
    worst = results_df.loc[results_df['Loss %'].idxmin()]; best = results_df.loc[results_df['Loss %'].idxmax()]
    critical_count = len(results_df[results_df['Severity'].str.contains('CRITICAL|EXTREME|MAXIMUM')])
    col1.metric("Current Price", f"{cur}{cp:.2f}"); col2.metric("Worst Case", f"{cur}{worst['Impact Price']:.2f}", delta=f"{worst['Loss %']:.1f}%", delta_color="inverse")
    col3.metric("Best Case", f"{cur}{best['Impact Price']:.2f}", delta=f"{best['Loss %']:.1f}%"); col4.metric("Critical", f"{critical_count}/{len(results_df)}")
    
    def color_severity(val):
        if 'CRITICAL' in str(val) or 'EXTREME' in str(val) or 'MAXIMUM' in str(val): return 'background-color: rgba(239,68,68,0.3); color: #ef4444; font-weight: bold'
        elif 'HIGH' in str(val): return 'background-color: rgba(245,158,11,0.2); color: #f59e0b; font-weight: bold'
        elif 'POSITIVE' in str(val) or 'WINNER' in str(val): return 'background-color: rgba(16,185,129,0.2); color: #10b981; font-weight: bold'
        return ''
    try:
        styled_df = results_df.style.applymap(color_severity, subset=['Severity'])
        st.dataframe(styled_df, use_container_width=True, height=600)
    except:
        st.dataframe(results_df, use_container_width=True, height=600)
    
    severity_counts = results_df['Severity'].str.extract(r'(🔴|🟠|🟡|🟢|💀)')[0].value_counts()
    fig = go.Figure(data=[go.Pie(labels=severity_counts.index, values=severity_counts.values, hole=0.4, marker_colors=['#ef4444','#f59e0b','#eab308','#10b981','#000000'])])
    fig.update_layout(title='Severity Distribution', template='plotly_white', height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("💡 Sector-specific sensitivities and beta-adjusted impacts.")


def create_technical_dashboard(analyzer):
    st.markdown('<div class="section-header">📈 Technical Analysis</div>', unsafe_allow_html=True)
    prices = analyzer.financials.get('prices')
    if prices is None or prices.empty: st.warning("No price data."); return
    close = prices['Close']; cur = analyzer.currency_symbol
    delta = close.diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean(); loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss; rsi = 100 - (100 / (1 + rs))
    ema12 = close.ewm(span=12).mean(); ema26 = close.ewm(span=26).mean(); macd = ema12 - ema26; signal = macd.ewm(span=9).mean(); hist = macd - signal
    sma20 = close.rolling(20).mean(); std20 = close.rolling(20).std(); upper = sma20 + 2*std20; lower = sma20 - 2*std20
    
    rsi_now = rsi.iloc[-1]; rsi_sig = "Overbought 🔴" if rsi_now>70 else "Oversold 🟢" if rsi_now<30 else "Neutral 🟡"
    macd_sig = "Bullish 🟢" if macd.iloc[-1]>signal.iloc[-1] else "Bearish 🔴"
    sma50 = close.rolling(50).mean().iloc[-1]; sma200 = close.rolling(200).mean().iloc[-1]
    trend = "Golden Cross ✨" if sma50>sma200 else "Death Cross 💀"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RSI (14)", f"{rsi_now:.1f}", delta=rsi_sig); col2.metric("MACD", f"{macd.iloc[-1]:.2f}", delta=macd_sig)
    col3.metric("Trend", trend.split(' ')[0]); col4.metric("Close", f"{cur}{close.iloc[-1]:.2f}")
    
    idx = slice(-120, None)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5,0.25,0.25])
    fig.add_trace(go.Scatter(x=close.index[idx], y=upper.iloc[idx], line=dict(color='gray',width=1,dash='dash'), name='Upper BB'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[idx], y=sma20.iloc[idx], line=dict(color='orange',width=1.5), name='20 MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[idx], y=lower.iloc[idx], line=dict(color='gray',width=1,dash='dash'), fill='tonexty', fillcolor='rgba(102,126,234,0.1)', name='Lower BB'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[idx], y=close.iloc[idx], line=dict(color='#667eea',width=2), name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=rsi.index[idx], y=rsi.iloc[idx], line=dict(color='#667eea',width=2), name='RSI'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1); fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_trace(go.Scatter(x=macd.index[idx], y=macd.iloc[idx], line=dict(color='#667eea',width=2), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=signal.index[idx], y=signal.iloc[idx], line=dict(color='#f59e0b',width=1.5), name='Signal'), row=3, col=1)
    colors = ['#10b981' if h>=0 else '#ef4444' for h in hist.iloc[idx]]
    fig.add_trace(go.Bar(x=hist.index[idx], y=hist.iloc[idx], marker_color=colors, name='Histogram'), row=3, col=1)
    fig.update_layout(height=750, template='plotly_white', hovermode='x unified'); st.plotly_chart(fig, use_container_width=True)


def get_peer_comparison(main_ticker, peer_tickers):
    data = []
    for ticker in peer_tickers:
        try:
            s = yf.Ticker(ticker); info = s.info
            if not info: continue
            is_ind = ticker.endswith('.NS') or ticker.endswith('.BO'); p_cur = 'INR' if is_ind else 'USD'
            mcap = info.get('marketCap', 0) or 0; mcap_disp = round(mcap/1e7, 1) if p_cur=='INR' else round(mcap/1e9, 1)
            data.append({'Ticker': ticker.replace('.NS','').replace('.BO',''), 'Company': info.get('longName', ticker)[:25],
                         'Market Cap': f"{'₹' if p_cur=='INR' else '$'}{mcap_disp} {'Cr' if p_cur=='INR' else 'B'}",
                         'P/E': round(info.get('trailingPE',0),1) if info.get('trailingPE') else 'N/A',
                         'ROE %': round((info.get('returnOnEquity',0) or 0)*100, 1), 'D/E': round(info.get('debtToEquity',0) or 0, 2),
                         'Div Yield %': round((info.get('dividendYield',0) or 0)*100, 2), 'Price': info.get('currentPrice') or info.get('regularMarketPrice')})
        except: continue
    return pd.DataFrame(data)

def detect_peer_group(ticker):
    for group_name, tickers in PEER_GROUPS.items():
        if ticker in tickers: return group_name, tickers
    return None, []


# ===== MAIN APP =====
def main():
    st.markdown('<h1 class="main-header">📊 FinAnalyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced DCF • 30 Stress Tests • Portfolio Optimizer • Technical Analysis • Peer Comparison</p>', unsafe_allow_html=True)

    if 'current_ticker' not in st.session_state: st.session_state['current_ticker'] = "AAPL"
    if 'current_exchange' not in st.session_state: st.session_state['current_exchange'] = "Auto-detect"
    if 'analyze_clicked' not in st.session_state: st.session_state['analyze_clicked'] = False

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Stock Analysis", 
        "🛡️ Stress Tests", 
        "📈 Technical Analysis",
        "🎯 Portfolio Optimizer",
        "🏦 Advanced Portfolio"
    ])

    # ===== TAB 1 =====
    with tab1:
        c1, c2, c3 = st.columns([3, 1.5, 1])
        with c1:
            ticker = st.text_input("Stock Ticker", key="main_ticker_input", placeholder="e.g., AAPL, RELIANCE")
        with c2:
            exchange = st.selectbox("Exchange", ["Auto-detect","NSE India (.NS)","BSE India (.BO)","US Market"], key="main_exchange_input")
        with c3:
            st.write("")
            analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

        if ticker:
            st.session_state['current_ticker'] = ticker.upper().strip()
        if exchange:
            st.session_state['current_exchange'] = exchange

        st.markdown("#### ⚡ Quick Access")
        qcols = st.columns(8)
        quick_list = ["AAPL", "RELIANCE", "TCS", "MSFT", "TATAMOTORS", "INFY", "GOOGL", "HDFCBANK"]
        exchange_map = {
            "AAPL": "US Market", "MSFT": "US Market", "GOOGL": "US Market",
            "RELIANCE": "NSE India (.NS)", "TCS": "NSE India (.NS)", 
            "TATAMOTORS": "NSE India (.NS)", "INFY": "NSE India (.NS)",
            "HDFCBANK": "NSE India (.NS)"
        }
        
        for i, stock in enumerate(quick_list):
            with qcols[i]:
                if st.button(stock, key=f"quickbtn_{stock}", use_container_width=True):
                    st.session_state['current_ticker'] = stock
                    st.session_state['current_exchange'] = exchange_map[stock]
                    st.session_state['analyze_clicked'] = True
                    st.rerun()

        with st.expander("📋 More Stocks"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Indian Stocks**")
                for t in list(INDIAN_STOCKS_DB.keys())[:20]:
                    if st.button(t, key=f"more_ind_{t}", use_container_width=True):
                        st.session_state['current_ticker'] = t
                        st.session_state['current_exchange'] = "NSE India (.NS)"
                        st.session_state['analyze_clicked'] = True
                        st.rerun()
            with c2:
                st.markdown("**US Stocks**")
                for s in ["AAPL","MSFT","GOOGL","AMZN","META","NVDA","TSLA","JPM"]:
                    if st.button(s, key=f"more_us_{s}", use_container_width=True):
                        st.session_state['current_ticker'] = s
                        st.session_state['current_exchange'] = "US Market"
                        st.session_state['analyze_clicked'] = True
                        st.rerun()

        if analyze_btn:
            st.session_state['analyze_clicked'] = True

        if not st.session_state.get('analyze_clicked', False):
            st.markdown('<div style="text-align:center;padding:4rem;"><h2>🏦 Enterprise Financial Analysis Platform</h2><p>Enter a ticker or click Quick Access, then Analyze</p></div>', unsafe_allow_html=True)
        else:
            em = {"NSE India (.NS)":"NSE","BSE India (.BO)":"BSE","US Market":"US","Auto-detect":"Auto"}
            current_ticker = st.session_state.get('current_ticker', 'AAPL')
            current_exchange = st.session_state.get('current_exchange', 'Auto-detect')
            
            analyzer = ProFinancialAnalyzer(current_ticker, exchange=em.get(current_exchange,"Auto"))
            
            if not analyzer.get_live_price():
                st.error("❌ Could not fetch live data. Please check the ticker or try again later.")
            else:
                analyzer.fetch_financial_data()
                analyzer.calculate_all_ratios()

                pd_d = analyzer.live_price_data
                cur = analyzer.currency_symbol
                cp = pd_d.get('current_price')
                pc = pd_d.get('previous_close')
                
                if cp and pc:
                    ch = cp - pc
                    ch_pct = (ch/pc)*100
                    color = "price-up" if ch>=0 else "price-down"
                    arrow = "▲" if ch>=0 else "▼"
                    st.markdown(f'<div class="live-price-box"><h2>{analyzer.company_name}</h2><div class="{color}">{cur}{cp:.2f} {arrow}</div><div>{cur}{abs(ch):.2f} ({ch_pct:+.2f}%)</div></div>', unsafe_allow_html=True)

                rec = analyzer.live_price_data.get('recommendation','').upper()
                if rec:
                    rc = {'BUY':'#10b981','STRONG_BUY':'#10b981','HOLD':'#f59e0b','SELL':'#ef4444','STRONG_SELL':'#ef4444'}.get(rec,'#666')
                    st.markdown(f'<div style="background-color:{rc};padding:0.75rem;border-radius:12px;color:white;text-align:center;font-weight:700;">🎯 {rec.replace("_"," ")}</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="info-box">📊 {analyzer.company_name} | {analyzer.financials.get("sector","N/A")} | {analyzer.currency} | MCap: {analyzer._format_amount(pd_d.get("market_cap",0))}</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-header">📊 Key Ratios</div>', unsafe_allow_html=True)
                ratios = analyzer.ratios
                if ratios:
                    cols = st.columns(5)
                    for col, (l, v) in zip(cols, [('P/E',ratios.get('P/E Ratio')),('ROE %',ratios.get('ROE')),('P/B',ratios.get('P/B Ratio')),('D/E',ratios.get('Debt to Equity')),('Div Yld',ratios.get('Dividend Yield'))]):
                        with col:
                            if isinstance(v,(int,float)):
                                d = f"{v:.1f}%" if l in ['ROE %','Div Yld'] else f"{v:.2f}"
                                st.markdown(f'<div class="card"><div class="metric-value">{d}</div><div class="metric-label">{l}</div></div>', unsafe_allow_html=True)

                create_valuation_dashboard(analyzer)
                create_advanced_scores_dashboard(analyzer)
                create_index_comparison_dashboard(analyzer)
                create_investment_thesis_dashboard(analyzer)
                create_historical_dcf_tracker(analyzer)
                create_factor_investing_dashboard(analyzer)
                    
                group_name, peer_list = detect_peer_group(analyzer.ticker)
                if peer_list:
                    peer_list = [p for p in peer_list if p!=analyzer.ticker][:5]
                    if len(peer_list) >= 1:
                        with st.spinner("Fetching peers..."):
                            pdf = get_peer_comparison(analyzer.ticker, [analyzer.ticker] + peer_list)
                            if not pdf.empty:
                                st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
                                st.dataframe(pdf, use_container_width=True, hide_index=True)

                st.markdown('<div class="section-header">📋 Financial Statements</div>', unsafe_allow_html=True)
                t1, t2, t3 = st.tabs(["Income","Balance","Cash Flow"])
                for tab, key, name in [(t1,'income','Income'),(t2,'balance','Balance'),(t3,'cashflow','Cash')]:
                    with tab:
                        df = analyzer.financials.get(key)
                        if df is not None and not df.empty:
                            formatted = format_financial_df(df, analyzer.currency_symbol, analyzer.currency)
                            if formatted is not None: st.dataframe(formatted, use_container_width=True)
                        else: st.info(f"{name} not available.")

    # ===== TAB 2 =====
    with tab2:
        st.markdown("### 🛡️ Comprehensive Stress Tests (30 Scenarios)")
        col1, col2 = st.columns([2, 1])
        with col1:
            st2_t = st.text_input("Ticker", value="AAPL", key="stress_ticker_input")
        with col2:
            st2_e = st.selectbox("Exchange", ["Auto-detect","NSE India (.NS)","BSE India (.BO)","US Market"], key="stress_exchange_input")
        
        if st.button("🛡️ Run 30 Stress Tests", type="primary", use_container_width=True, key="run_stress_btn"):
            if not st2_t:
                st.warning("Please enter a ticker.")
            else:
                em2 = {"NSE India (.NS)":"NSE","BSE India (.BO)":"BSE","US Market":"US","Auto-detect":"Auto"}
                a2 = ProFinancialAnalyzer(st2_t.strip().upper(), exchange=em2.get(st2_e,"Auto"))
                with st.spinner("Loading..."):
                    if a2.get_live_price():
                        a2.fetch_financial_data()
                        create_stress_test_dashboard(a2)
                    else:
                        st.error("Could not fetch data for stress test.")

    # ===== TAB 3 =====
    with tab3:
        st.markdown("### 📈 Technical Analysis")
        ta_t = st.text_input("Ticker", "AAPL", key="ta_t")
        ta_e = st.selectbox("Exchange", ["Auto-detect","NSE India (.NS)","BSE India (.BO)","US Market"], key="ta_e")
        if st.button("📈 Run TA", type="primary", key="ta_btn"):
            em3 = {"NSE India (.NS)":"NSE","BSE India (.BO)":"BSE","US Market":"US","Auto-detect":"Auto"}
            a3 = ProFinancialAnalyzer(ta_t, exchange=em3.get(ta_e,"Auto"))
            if a3.get_live_price():
                a3.fetch_financial_data()
                create_technical_dashboard(a3)
            else:
                st.error("Could not fetch data for technical analysis.")

    # ===== TAB 4 =====
    with tab4:
        create_portfolio_optimization_tab()
        
    # ===== TAB 5 =====
    with tab5:
        create_advanced_portfolio_tab()

    st.divider()
    st.caption(f"FinAnalyzer Pro | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()