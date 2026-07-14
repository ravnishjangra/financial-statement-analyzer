"""
Financial Statement Analyzer - Pro Version
Yahoo Finance + Google Finance fallback
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
import requests
import json
import re

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
        font-size: 2.5rem; font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 1rem;
    }
    .sub-header { font-size: 1.2rem; color: #94a3b8; text-align: center; margin-bottom: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        border: 1px solid rgba(102,126,234,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(102,126,234,0.2); }
    .metric-value { font-size: 1.5rem; font-weight: bold; }
    .metric-label { font-size: 0.8rem; opacity: 0.9; margin-top: 0.3rem; }
    .valuation-card {
        background: linear-gradient(135deg, #f093fb15, #f5576c15);
        border: 1px solid rgba(240,147,251,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    .valuation-card:hover { transform: translateY(-3px); }
    .profitability-card {
        background: linear-gradient(135deg, #4facfe15, #00f2fe15);
        border: 1px solid rgba(79,172,254,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    .profitability-card:hover { transform: translateY(-3px); }
    .growth-card {
        background: linear-gradient(135deg, #43e97b15, #38f9d715);
        border: 1px solid rgba(67,233,123,0.2); padding: 1.2rem;
        border-radius: 15px; text-align: center; color: #e2e8f0; margin: 0.3rem 0;
        transition: all 0.3s ease;
    }
    .growth-card:hover { transform: translateY(-3px); }
    .live-price-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        border: 1px solid rgba(102,126,234,0.3); padding: 2rem;
        border-radius: 20px; color: white; text-align: center; margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
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
    .source-fallback { background: #ff6b00; color: white; }
</style>
""", unsafe_allow_html=True)

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


class GoogleFinanceFetcher:
    """Fetch stock data from Google Finance"""
    
    BASE_URL = "https://www.google.com/finance/quote/"
    
    @staticmethod
    def get_google_ticker(ticker):
        """Convert Yahoo ticker to Google Finance format"""
        ticker_clean = ticker.replace('.NS', '').replace('.BO', '')
        if ticker.endswith('.NS'):
            return f"NSE:{ticker_clean}"
        elif ticker.endswith('.BO'):
            return f"BOM:{ticker_clean}"
        return ticker_clean
    
    @staticmethod
    def fetch_price_data(ticker):
        """Fetch price and basic data from Google Finance"""
        google_ticker = GoogleFinanceFetcher.get_google_ticker(ticker)
        url = f"{GoogleFinanceFetcher.BASE_URL}{google_ticker}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            # Extract data from Google Finance page
            soup = BeautifulSoup(response.text, 'html.parser') if 'BeautifulSoup' in dir() else None
            
            # Try to find JSON data in the page
            data = {}
            
            # Look for price in the page
            price_pattern = r'data-last-price="([^"]*)"'
            price_match = re.search(price_pattern, response.text)
            if price_match:
                data['currentPrice'] = float(price_match.group(1))
            
            # Look for previous close
            prev_close_pattern = r'data-previous-close="([^"]*)"'
            prev_match = re.search(prev_close_pattern, response.text)
            if prev_match:
                data['previousClose'] = float(prev_match.group(1))
            
            # Try extracting from meta tags or script tags
            script_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
            script_match = re.search(script_pattern, response.text, re.DOTALL)
            if script_match:
                try:
                    import json
                    state_data = json.loads(script_match.group(1))
                    # Navigate through the state to find price data
                    # This structure may change, so handle gracefully
                except:
                    pass
            
            if data:
                data['source'] = 'Google Finance'
                data['currency'] = 'INR' if ('.NS' in ticker or '.BO' in ticker) else 'USD'
                return data
            
            return None
            
        except Exception as e:
            return None
    
    @staticmethod
    def fetch_company_info(ticker):
        """Fetch company info from Google Finance"""
        google_ticker = GoogleFinanceFetcher.get_google_ticker(ticker)
        url = f"{GoogleFinanceFetcher.BASE_URL}{google_ticker}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            info = {}
            
            # Extract market cap
            mcap_pattern = r'Market cap\s*</div><div[^>]*>([^<]*)</div>'
            mcap_match = re.search(mcap_pattern, response.text)
            if mcap_match:
                mcap_text = mcap_match.group(1).strip()
                info['marketCap'] = GoogleFinanceFetcher._parse_number(mcap_text)
            
            # Extract P/E ratio
            pe_pattern = r'P/E ratio\s*</div><div[^>]*>([^<]*)</div>'
            pe_match = re.search(pe_pattern, response.text)
            if pe_match:
                try:
                    info['trailingPE'] = float(pe_match.group(1).strip())
                except:
                    pass
            
            # Extract dividend yield
            div_pattern = r'Dividend yield\s*</div><div[^>]*>([^<]*)</div>'
            div_match = re.search(div_pattern, response.text)
            if div_match:
                try:
                    div_text = div_match.group(1).strip().replace('%', '')
                    info['dividendYield'] = float(div_text) / 100
                except:
                    pass
            
            # Extract 52-week range
            range_pattern = r'52-week range\s*</div><div[^>]*>([^<]*)</div>'
            range_match = re.search(range_pattern, response.text)
            if range_match:
                range_text = range_match.group(1).strip()
                prices = re.findall(r'[\d,.]+', range_text)
                if len(prices) >= 2:
                    info['fiftyTwoWeekLow'] = float(prices[0].replace(',', ''))
                    info['fiftyTwoWeekHigh'] = float(prices[1].replace(',', ''))
            
            return info if info else None
            
        except Exception as e:
            return None
    
    @staticmethod
    def _parse_number(text):
        """Parse number with suffixes like B, Cr, T, M"""
        text = text.replace(',', '').strip()
        multipliers = {'T': 1e12, 'B': 1e9, 'Cr': 1e7, 'M': 1e6, 'K': 1e3, 'L': 1e5}
        for suffix, mult in multipliers.items():
            if suffix in text:
                num = float(text.replace(suffix, '').strip())
                return num * mult
        try:
            return float(text)
        except:
            return None


# Import BeautifulSoup for Google Finance parsing
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class ProFinancialAnalyzer:
    def __init__(self, ticker, data_source="Yahoo Finance"):
        self.original_ticker = ticker.upper().strip()
        self.ticker = self._resolve_ticker(ticker.upper().strip())
        self.data_source = data_source
        self.stock = None
        self.financials = {}
        self.ratios = {}
        self.live_price_data = {}
        self.currency = 'USD'
        self.currency_symbol = '$'
        self.company_name = ''

    def _resolve_ticker(self, ticker):
        if ticker in INDIAN_STOCKS_DB:
            return INDIAN_STOCKS_DB[ticker]
        if ticker.endswith('.NS') or ticker.endswith('.BO'):
            return ticker
        return ticker

    def get_live_price(self):
        """Get live price from selected source"""
        success = False
        
        if self.data_source == "Yahoo Finance":
            success = self._get_from_yahoo()
            if not success:
                st.warning("⚠️ Yahoo Finance failed. Trying Google Finance...")
                success = self._get_from_google()
                if success:
                    self.data_source = "Google Finance (fallback)"
        else:
            success = self._get_from_google()
            if not success:
                st.warning("⚠️ Google Finance failed. Trying Yahoo Finance...")
                success = self._get_from_yahoo()
                if success:
                    self.data_source = "Yahoo Finance (fallback)"
        
        return success

    def _get_from_yahoo(self):
        try:
            self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            
            if not info or not info.get('marketCap'):
                if self.ticker.endswith('.NS'):
                    alt = self.ticker.replace('.NS', '.BO')
                else:
                    alt = self.ticker + '.NS'
                try:
                    alt_stock = yf.Ticker(alt)
                    alt_info = alt_stock.info
                    if alt_info and alt_info.get('marketCap'):
                        self.stock = alt_stock
                        self.ticker = alt
                        info = alt_info
                except:
                    pass

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
            
            if self.live_price_data.get('current_price'):
                return True
            return False
        except:
            return False

    def _get_from_google(self):
        try:
            # Try Google Finance
            gf_data = GoogleFinanceFetcher.fetch_price_data(self.ticker)
            gf_info = GoogleFinanceFetcher.fetch_company_info(self.ticker)
            
            if gf_data or gf_info:
                merged = {}
                if gf_info:
                    merged.update(gf_info)
                if gf_data:
                    merged.update(gf_data)
                
                self.live_price_data = {
                    'current_price': merged.get('currentPrice'),
                    'previous_close': merged.get('previousClose'),
                    'market_cap': merged.get('marketCap'),
                    'fifty_two_week_high': merged.get('fiftyTwoWeekHigh'),
                    'fifty_two_week_low': merged.get('fiftyTwoWeekLow'),
                    'trailingPE': merged.get('trailingPE'),
                    'dividendYield': merged.get('dividendYield'),
                }
                self.live_price_data = {k: v for k, v in self.live_price_data.items() if v is not None}
                
                if self.live_price_data.get('current_price'):
                    # Also try Yahoo for the stock object (for financials)
                    try:
                        self.stock = yf.Ticker(self.ticker)
                    except:
                        pass
                    return True
            
            return False
        except:
            return False

    def fetch_financial_data(self):
        try:
            if not self.stock:
                self.stock = yf.Ticker(self.ticker)

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

                if cashflow is not None and not cashflow.empty:
                    fcf = self._safe_get(cashflow, ['Free Cash Flow'])
                    if fcf and ni: self.ratios['FCF to Net Income'] = fcf/ni

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
                        if 'fcf' in dir() and fcf and fcf/shares > 0: self.ratios['P/FCF Ratio'] = cp/(fcf/shares)
                        if cashflow is not None and not cashflow.empty:
                            div = self._safe_get(cashflow, ['Dividends Paid'])
                            if div and cp > 0: self.ratios['Dividend Yield'] = (abs(div)/shares/cp)*100

                    eg = self.ratios.get('Net Income Growth (YoY)')
                    pe = self.ratios.get('P/E Ratio')
                    if eg and pe and eg > 0: self.ratios['PEG Ratio'] = pe/eg

                if prices is not None and not prices.empty and len(prices) >= 252:
                    self.ratios['52-Week Return'] = ((prices['Close'].iloc[-1]-prices['Close'].iloc[-252])/prices['Close'].iloc[-252])*100

            # Fallback from info dict
            for key, ratio_key, multiplier in [
                ('returnOnEquity', 'ROE', 100), ('returnOnAssets', 'ROA', 100),
                ('profitMargins', 'Net Profit Margin', 100), ('debtToEquity', 'Debt to Equity', 1),
                ('trailingPE', 'P/E Ratio', 1), ('priceToBook', 'P/B Ratio', 1),
                ('trailingEps', 'EPS', 1), ('revenueGrowth', 'Revenue Growth (YoY)', 100),
                ('dividendYield', 'Dividend Yield', 100), ('currentRatio', 'Current Ratio', 1),
                ('quickRatio', 'Quick Ratio', 1),
            ]:
                if ratio_key not in self.ratios and info.get(key):
                    self.ratios[ratio_key] = info[key] * multiplier

            return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False


# ===== FORMATTING =====

def format_financial_number(value, symbol, currency):
    if pd.isna(value) or value is None: return 'N/A'
    try:
        value = float(value)
        abs_val = abs(value)
        sign = '-' if value < 0 else ''
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


# ===== PEER COMPARISON =====

def get_peer_comparison(main_ticker, peer_tickers):
    peer_data = []
    for ticker in peer_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info: continue

            is_indian = ticker.endswith('.NS') or ticker.endswith('.BO')
            p_currency = 'INR' if is_indian else info.get('currency', 'USD')
            mcap = info.get('marketCap', 0) or 0
            mcap_display = round(mcap / 1e7, 2) if p_currency == 'INR' else round(mcap / 1e9, 2)
            mcap_label = 'Market Cap (₹ Cr)' if p_currency == 'INR' else 'Market Cap ($ B)'

            peer_data.append({
                'Ticker': ticker.replace('.NS', '').replace('.BO', ''),
                'Company': info.get('longName', ticker)[:25],
                mcap_label: mcap_display,
                'P/E Ratio': round(info['trailingPE'], 2) if info.get('trailingPE') else None,
                'P/B Ratio': round(info['priceToBook'], 2) if info.get('priceToBook') else None,
                'Revenue Growth': round(info['revenueGrowth']*100, 2) if info.get('revenueGrowth') else None,
                'ROE': round(info['returnOnEquity']*100, 2) if info.get('returnOnEquity') else None,
                'Debt/Equity': round(info['debtToEquity'], 2) if info.get('debtToEquity') else None,
                'Dividend Yield': round(info['dividendYield']*100, 2) if info.get('dividendYield') else None,
                'Current Price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'Recommendation': info.get('recommendationKey', 'N/A'),
            })
        except: continue
    return pd.DataFrame(peer_data)


def safe_mean(series):
    valid = series.dropna()
    return valid.mean() if len(valid) > 0 else None


def create_peer_comparison_charts(peer_df, main_ticker_name, currency_symbol, currency):
    st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
    if peer_df.empty or len(peer_df) < 2:
        st.warning("Not enough peer data."); return

    main_clean = main_ticker_name.replace('.NS', '').replace('.BO', '')
    mcap_col = [c for c in peer_df.columns if 'Market Cap' in c][0]

    st.markdown("#### 📊 Market Cap")
    sorted_df = peer_df.sort_values(mcap_col, ascending=True)
    colors = ['#ff4757' if t == main_clean else '#667eea' for t in sorted_df['Ticker']]
    unit, sign = ('Cr', '₹') if '₹' in mcap_col else ('B', '$')

    fig = go.Figure()
    fig.add_trace(go.Bar(y=sorted_df['Ticker'], x=sorted_df[mcap_col], orientation='h', marker_color=colors,
                         text=[f"{sign}{v:.1f}{unit}" if pd.notna(v) and v>0 else 'N/A' for v in sorted_df[mcap_col]],
                         textposition='outside'))
    fig.update_layout(height=400, template='plotly_white', showlegend=False, margin=dict(l=100))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📈 Key Metrics")
    metrics = ['P/E Ratio', 'P/B Ratio', 'Revenue Growth', 'ROE']
    available = [m for m in metrics if m in peer_df.columns and peer_df[m].notna().any()]
    if available:
        fig = make_subplots(rows=2, cols=2, subplot_titles=available[:4], vertical_spacing=0.15)
        for i, metric in enumerate(available[:4]):
            valid = peer_df[peer_df[metric].notna()]
            colors = ['#ff4757' if t==main_clean else '#667eea' for t in valid['Ticker']]
            fig.add_trace(go.Bar(x=valid['Ticker'], y=valid[metric], marker_color=colors,
                                 text=[f"{v:.1f}" for v in valid[metric]], textposition='outside'),
                          row=(i//2)+1, col=(i%2)+1)
        fig.update_layout(height=600, template='plotly_white', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📋 Table")
    def highlight(row):
        return ['background-color: rgba(255,71,87,0.2)']*len(row) if row['Ticker']==main_clean else ['']*len(row)
    display_df = peer_df.copy()
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'int64']:
            display_df[col] = display_df[col].apply(lambda x: round(x,2) if pd.notna(x) else x)
    st.dataframe(display_df.style.apply(highlight, axis=1), use_container_width=True, height=400)

    st.markdown("#### 📊 Summary")
    other = peer_df[peer_df['Ticker'] != main_clean]
    c1, c2, c3, c4 = st.columns(4)
    mp = peer_df[peer_df['Ticker']==main_clean]['P/E Ratio'].values
    c1.metric("Avg Peer P/E", f"{safe_mean(other['P/E Ratio']):.1f}" if safe_mean(other['P/E Ratio']) else "N/A",
              delta=f"{mp[0]:.1f}" if len(mp)>0 and pd.notna(mp[0]) else None)
    mr = peer_df[peer_df['Ticker']==main_clean]['ROE'].values
    c2.metric("Avg Peer ROE", f"{safe_mean(other['ROE']):.1f}%" if safe_mean(other['ROE']) else "N/A",
              delta=f"{mr[0]:.1f}%" if len(mr)>0 and pd.notna(mr[0]) else None)
    mg = peer_df[peer_df['Ticker']==main_clean]['Revenue Growth'].values
    c3.metric("Avg Peer Growth", f"{safe_mean(other['Revenue Growth']):.1f}%" if safe_mean(other['Revenue Growth']) else "N/A",
              delta=f"{mg[0]:.1f}%" if len(mg)>0 and pd.notna(mg[0]) else None)
    md = peer_df[peer_df['Ticker']==main_clean]['Debt/Equity'].values
    c4.metric("Avg Peer D/E", f"{safe_mean(other['Debt/Equity']):.1f}" if safe_mean(other['Debt/Equity']) else "N/A",
              delta=f"{md[0]:.1f}" if len(md)>0 and pd.notna(md[0]) else None, delta_color="inverse")


# ===== DASHBOARD =====

def create_live_price_dashboard(analyzer):
    pd_data = analyzer.live_price_data
    cur = analyzer.currency_symbol
    
    source_class = "source-yahoo" if "Yahoo" in analyzer.data_source else "source-google" if "Google" in analyzer.data_source else "source-fallback"
    
    st.markdown("### 🟢 Live Market Data")
    cp = pd_data.get('current_price')
    pc = pd_data.get('previous_close')

    if cp and pc:
        change = cp - pc
        change_pct = (change/pc)*100
        color = "price-up" if change >= 0 else "price-down"
        arrow = "▲" if change >= 0 else "▼"
        st.markdown(f'<div class="live-price-box"><h3>{analyzer.company_name}<span class="source-badge {source_class}">{analyzer.data_source}</span></h3><div class="{color}">{cur}{cp:.2f} {arrow}</div><div style="font-size:1.2rem;margin-top:0.5rem;">{cur}{abs(change):.2f} ({change_pct:+.2f}%)</div></div>', unsafe_allow_html=True)
    elif cp:
        st.markdown(f'<div class="live-price-box"><h3>{analyzer.company_name}<span class="source-badge {source_class}">{analyzer.data_source}</span></h3><div style="font-size:3rem;font-weight:800;">{cur}{cp:.2f}</div></div>', unsafe_allow_html=True)

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
    st.markdown('<div class="section-header">📉 Charts</div>', unsafe_allow_html=True)

    prices = financials.get('prices')
    if prices is not None and not prices.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=prices.index, open=prices['Open'], high=prices['High'], low=prices['Low'], close=prices['Close'], name='Price'), row=1, col=1)
        for ma, color, name in [(20, '#ffa500', '20 MA'), (50, '#00b4d8', '50 MA'), (200, '#ff4757', '200 MA')]:
            fig.add_trace(go.Scatter(x=prices.index, y=prices['Close'].rolling(window=ma).mean(), name=name, line=dict(color=color, width=1.5)), row=1, col=1)
        vol_colors = ['#00ff88' if prices['Close'].iloc[i] >= prices['Open'].iloc[i] else '#ff4757' for i in range(len(prices))]
        fig.add_trace(go.Bar(x=prices.index, y=prices['Volume'], name='Volume', marker_color=vol_colors, opacity=0.5), row=2, col=1)
        fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    if prices is not None and not prices.empty:
        returns = prices['Close'].pct_change().dropna() * 100
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=returns, nbinsx=50, marker_color='#667eea', opacity=0.7, histnorm='probability density'))
        if len(returns) > 1:
            mean_r, std_r = returns.mean(), returns.std()
            x_r = np.linspace(returns.min(), returns.max(), 100)
            fig.add_trace(go.Scatter(x=x_r, y=(1/(std_r*np.sqrt(2*np.pi)))*np.exp(-(x_r-mean_r)**2/(2*std_r**2)), line=dict(color='#00ff88', width=2)))
        fig.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean Return", f"{returns.mean():.3f}%")
        c2.metric("Volatility", f"{returns.std():.3f}%")
        c3.metric("Skewness", f"{returns.skew():.3f}")
        c4.metric("Kurtosis", f"{returns.kurtosis():.3f}")


def detect_peer_group(ticker):
    for group_name, tickers in PEER_GROUPS.items():
        if ticker in tickers: return group_name, tickers
    return None, []


# ===== MAIN =====

def main():
    st.markdown('<h1 class="main-header">📊 FinAnalyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Yahoo Finance + Google Finance • Peer Comparison • 20+ Ratios</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔍 Search")
        ticker = st.text_input("Stock Ticker:", "AAPL", max_chars=50)
        
        # === DATA SOURCE SELECTOR ===
        st.divider()
        st.subheader("📡 Data Source")
        data_source = st.radio(
            "Choose data source:",
            ["Yahoo Finance", "Google Finance"],
            help="Google Finance works better for some Indian stocks. Yahoo Finance has richer financial data."
        )
        
        st.divider()
        st.subheader("🏢 Peer Comparison")
        use_peers = st.checkbox("Enable", value=True)
        custom_peers = st.text_input("Custom Peers:", placeholder="AAPL, MSFT, GOOGL")
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

        st.divider()
        t1, t2 = st.tabs(["India 🇮🇳", "US 🇺🇸"])
        with t1:
            for tick in list(INDIAN_STOCKS_DB.keys())[:12]:
                if st.button(tick, use_container_width=True, key=f"i_{tick}"):
                    st.session_state['ticker'] = tick; st.session_state['source'] = data_source; st.rerun()
        with t2:
            for s in ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "JPM"]:
                if st.button(s, use_container_width=True, key=f"u_{s}"):
                    st.session_state['ticker'] = s; st.session_state['source'] = data_source; st.rerun()

    if 'ticker' in st.session_state:
        ticker = st.session_state['ticker']
    if 'source' in st.session_state:
        data_source = st.session_state['source']

    if not analyze_btn and 'ticker' not in st.session_state:
        st.markdown('<div style="text-align:center;padding:3rem;"><h2>🚀 Welcome to FinAnalyzer Pro</h2><p>Choose <b>Yahoo Finance</b> or <b>Google Finance</b> in the sidebar.<br>Google Finance works better for some Indian stocks!</p><p>👈 Enter a ticker and click Analyze!</p></div>', unsafe_allow_html=True)
        return

    analyzer = ProFinancialAnalyzer(ticker, data_source=data_source)

    pb = st.progress(0)
    st_msg = st.empty()

    st_msg.text(f"Fetching data from {data_source}..."); pb.progress(33)
    if not analyzer.get_live_price():
        pb.empty(); st_msg.empty()
        st.error(f"Unable to fetch data from {data_source}. Try switching data source.")
        return

    st_msg.text("Downloading financials..."); pb.progress(66)
    if not analyzer.fetch_financial_data():
        pb.empty(); st_msg.empty(); return

    st_msg.text("Calculating ratios..."); pb.progress(100)
    analyzer.calculate_all_ratios()
    time.sleep(0.3)
    pb.empty(); st_msg.empty()

    create_live_price_dashboard(analyzer)

    if analyzer.live_price_data.get('recommendation'):
        rec = analyzer.live_price_data.get('recommendation', '').upper()
        rc = {'BUY': '#00ff88', 'STRONG_BUY': '#00ff88', 'HOLD': '#ffa500', 'SELL': '#ff4757', 'STRONG_SELL': '#ff4757'}.get(rec, '#666')
        st.markdown(f'<div style="background-color:{rc};padding:1rem;border-radius:10px;color:white;text-align:center;"><h3>{rec.replace("_"," ")}</h3></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box"><strong>{analyzer.company_name}</strong> | {analyzer.financials.get("sector","N/A")} | {analyzer.currency} ({analyzer.currency_symbol})</div>', unsafe_allow_html=True)

    create_ratio_dashboard(analyzer.ratios, analyzer.currency_symbol)
    create_advanced_charts(analyzer)

    if use_peers:
        if custom_peers:
            peer_list = [p.strip().upper() for p in custom_peers.split(',') if p.strip()]
        else:
            group_name, peer_list = detect_peer_group(analyzer.ticker)
            if group_name: st.info(f"🔍 Peer group: **{group_name.replace('_',' ')}**")
            else: st.info("No auto peer group. Add custom peers.")

        if peer_list:
            peer_list = [p for p in peer_list if p != analyzer.ticker]
            all_tickers = [analyzer.ticker] + peer_list[:7]
            if len(all_tickers) >= 2:
                with st.spinner("Fetching peer data..."):
                    peer_df = get_peer_comparison(analyzer.ticker, all_tickers)
                    if not peer_df.empty:
                        create_peer_comparison_charts(peer_df, analyzer.ticker, analyzer.currency_symbol, analyzer.currency)

    st.markdown('<div class="section-header">📋 Financial Statements</div>', unsafe_allow_html=True)
    st.caption(f"Currency: {analyzer.currency} ({analyzer.currency_symbol}) | Source: {analyzer.data_source}")

    tab1, tab2, tab3 = st.tabs(["📊 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])

    for tab, key, name in [(tab1, 'income', 'Income'), (tab2, 'balance', 'Balance'), (tab3, 'cashflow', 'Cash')]:
        with tab:
            df = analyzer.financials.get(key)
            if df is not None and not df.empty:
                formatted = format_financial_df(df, analyzer.currency_symbol, analyzer.currency)
                if formatted is not None:
                    st.dataframe(formatted, use_container_width=True)
                with st.expander("📥 Raw Data / Download"):
                    st.dataframe(df, use_container_width=True)
                    st.download_button(f"Download {name}", df.to_csv(), f"{analyzer.original_ticker}_{key}.csv", "text/csv")
            else:
                st.warning(f"{name} Statement not available. Some ratios shown from available market data.")

    st.divider()
    st.caption(f"Data: {analyzer.data_source} | {analyzer.currency} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()