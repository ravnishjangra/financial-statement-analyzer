"""
FinAnalyzer Pro - Enterprise Financial Analysis Platform
DCF Valuation • Monte Carlo Stress Tests • Graham & EPV Models
Technical Analysis • Portfolio Tracker • Peer Comparison • Live Prices
Multi-Currency Support • Analyst Ratings • Financial Statements
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

# ===== PAGE CONFIG =====
st.set_page_config(page_title="FinAnalyzer Pro | Enterprise Analysis", page_icon="📊", layout="wide")

# ===== PROFESSIONAL CSS =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        font-size: 2.8rem; font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem; letter-spacing: -1px;
    }
    .sub-header { font-size: 1rem; color: #94a3b8; text-align: center; margin-bottom: 2rem; font-weight: 400; }
    
    .card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(102,126,234,0.2); padding: 1.5rem;
        border-radius: 16px; margin: 0.5rem 0; color: #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 20px 40px rgba(102,126,234,0.15); border-color: rgba(102,126,234,0.4); }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #e2e8f0; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.25rem; }
    
    .live-price-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 2px solid rgba(102,126,234,0.4); padding: 2.5rem;
        border-radius: 24px; color: white; text-align: center; margin: 1rem 0;
        box-shadow: 0 25px 50px rgba(0,0,0,0.4); position: relative; overflow: hidden;
    }
    .live-price-box::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
        animation: rotate 15s linear infinite;
    }
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .price-up { color: #10b981; font-size: 3.5rem; font-weight: 900; text-shadow: 0 0 30px rgba(16,185,129,0.3); }
    .price-down { color: #ef4444; font-size: 3.5rem; font-weight: 900; text-shadow: 0 0 30px rgba(239,68,68,0.3); }
    
    .info-box {
        background: #1e293b; border: 1px solid rgba(102,126,234,0.3);
        padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0;
        border-left: 4px solid #667eea; color: #e2e8f0;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    .stButton button {
        width: 100%; border-radius: 12px; padding: 0.7rem;
        font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; transition: all 0.3s ease;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(102,126,234,0.4); }
    
    .section-header {
        font-size: 1.4rem; font-weight: 700; color: #e2e8f0;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102,126,234,0.3);
        display: flex; align-items: center; gap: 0.5rem;
    }
    
    .source-badge {
        display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem;
    }
    .source-yahoo { background: #7200ff; color: white; }
    .source-google { background: #4285f4; color: white; }
    
    .portfolio-profit { color: #10b981; font-weight: 700; }
    .portfolio-loss { color: #ef4444; font-weight: 700; }
    
    .quick-access-btn {
        background: rgba(102,126,234,0.1); border: 1px solid rgba(102,126,234,0.3);
        padding: 0.5rem; border-radius: 8px; text-align: center;
        cursor: pointer; transition: all 0.2s; font-size: 0.8rem; color: #e2e8f0;
    }
    .quick-access-btn:hover { background: rgba(102,126,234,0.2); border-color: #667eea; }
</style>
""", unsafe_allow_html=True)

# ===== CONSTANTS =====
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

if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = []

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
        try:
            self.stock = yf.Ticker(self.ticker)
            info = self.stock.info
            if not info or not info.get('marketCap'):
                alts = []
                if self.ticker.endswith('.NS'): alts = [self.ticker.replace('.NS','.BO'), self.ticker.replace('.NS','')]
                elif self.ticker.endswith('.BO'): alts = [self.ticker.replace('.BO','.NS'), self.ticker.replace('.BO','')]
                else: alts = [self.ticker+'.NS', self.ticker+'.BO']
                for alt in alts:
                    try:
                        s = yf.Ticker(alt); i = s.info
                        if i and i.get('marketCap'): self.stock = s; self.ticker = alt; info = i; break
                    except: continue
            if info:
                self._populate_from_info(info); self.data_source = 'Yahoo Finance'; return True
            return False
        except: return False

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


# ===== VALUATION MODELS (FIXED) =====

class AdvancedDCF:
    def __init__(self, fcf, shares, current_price, revenue_growth, beta, risk_free_rate, market_return):
        self.fcf = fcf
        self.shares = shares
        self.current_price = current_price
        self.revenue_growth = revenue_growth
        self.beta = beta
        self.risk_free_rate = risk_free_rate
        self.market_return = market_return
        self._calc_wacc()
    
    def _calc_wacc(self):
        cost_of_equity = self.risk_free_rate + self.beta * (self.market_return - self.risk_free_rate)
        cost_of_debt = self.risk_free_rate + 0.03
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
        
        # Scenarios (simple multipliers - NO RECURSION)
        bear_iv = intrinsic_value * 0.6
        bull_iv = intrinsic_value * 1.5
        
        if upside > 30: rec, rc = "STRONG BUY 🟢", "#10b981"
        elif upside > 10: rec, rc = "BUY 🟢", "#34d399"
        elif upside > -10: rec, rc = "HOLD 🟡", "#f59e0b"
        elif upside > -30: rec, rc = "SELL 🔴", "#ef4444"
        else: rec, rc = "STRONG SELL 🔴", "#dc2626"
        
        return {
            'intrinsic_value': intrinsic_value, 'current_price': self.current_price,
            'upside': upside, 'wacc': self.wacc, 'pv_fcfs': pv_fcfs,
            'terminal_value': terminal_value, 'pv_terminal': pv_terminal,
            'enterprise_value': enterprise_value, 'projections': projections,
            'bear_case': bear_iv, 'bull_case': bull_iv,
            'recommendation': rec, 'rec_color': rc
        }


class MonteCarloStressTest:
    def __init__(self, current_price, volatility, expected_return):
        self.current_price = current_price
        self.volatility = volatility
        self.expected_return = expected_return

    def run(self, num_sims=1000, days=252):
        dt = 1 / days
        simulations = np.zeros((num_sims, days))
        simulations[:, 0] = self.current_price
        for i in range(1, days):
            shocks = np.random.normal(0, 1, num_sims)
            simulations[:, i] = simulations[:, i-1] * np.exp(
                (self.expected_return - 0.5 * self.volatility**2) * dt + self.volatility * np.sqrt(dt) * shocks
            )
        final = simulations[:, -1]
        var_95 = np.percentile(final, 5)
        var_99 = np.percentile(final, 1)
        cvar_95 = final[final <= var_95].mean()
        prob_profit = np.mean(final > self.current_price) * 100
        expected = np.mean(final)
        return {
            'simulations': simulations, 'final_prices': final,
            'var_95': var_95, 'var_99': var_99, 'cvar_95': cvar_95,
            'prob_profit': prob_profit, 'expected_price': expected,
            'price_range': (np.percentile(final, 10), np.percentile(final, 90)),
            'max_loss': (var_95 / self.current_price - 1) * 100,
        }


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

def create_valuation_dashboard(analyzer):
    st.markdown('<div class="section-header">💰 Advanced Valuation Models</div>', unsafe_allow_html=True)
    
    info = analyzer.financials.get('info', {})
    income = analyzer.financials.get('income')
    cashflow = analyzer.financials.get('cashflow')
    cp = analyzer.live_price_data.get('current_price')
    cur = analyzer.currency_symbol
    
    if not cp: st.warning("Current price not available."); return
    
    # Get data
    rev = analyzer._safe_get(income, ['Total Revenue', 'Revenue']) if income is not None else 0
    ni = analyzer._safe_get(income, ['Net Income', 'Net Income Common Stockholders']) if income is not None else 0
    fcf = analyzer._safe_get(cashflow, ['Free Cash Flow']) if cashflow is not None else None
    if not fcf: fcf = ni * 0.8 if ni else (rev * 0.1 if rev else 1e6)
    
    shares = analyzer._safe_get(income, ['Diluted Average Shares']) or analyzer._safe_get(income, ['Basic Average Shares']) if income is not None else None
    if not shares: shares = analyzer.live_price_data.get('market_cap', 1e9) / cp if cp > 0 else 1e6
    
    beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
    rg = analyzer.ratios.get('Revenue Growth (YoY)', 10)
    rg = max(0.02, min((rg or 10) / 100, 0.35))
    om = analyzer.ratios.get('Operating Margin', 15) / 100 if analyzer.ratios.get('Operating Margin') else 0.15
    rf = 0.072 if analyzer.currency == 'INR' else 0.045
    mr = 0.12 if analyzer.currency == 'INR' else 0.10
    
    # Parameters
    with st.expander("⚙️ DCF Parameters", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            dcf_growth = st.slider("Growth %", 1, 35, int(rg*100)) / 100
            dcf_fcf = st.number_input("FCF (Millions)", value=float(fcf)/1e6, format="%.1f") * 1e6
        with c2:
            dcf_shares = st.number_input("Shares (Millions)", value=float(shares)/1e6, format="%.1f") * 1e6
            dcf_beta = st.number_input("Beta", value=float(beta), min_value=0.1, max_value=3.0, step=0.1)
        with c3:
            dcf_rf = st.slider("Risk-Free %", 1.0, 12.0, rf*100, 0.1) / 100
            dcf_mr = st.slider("Market Return %", 5.0, 18.0, mr*100, 0.1) / 100
    
    dcf = AdvancedDCF(dcf_fcf, dcf_shares, cp, dcf_growth, dcf_beta, dcf_rf, dcf_mr)
    result = dcf.calculate()
    
    # Recommendation
    st.markdown(f"""
    <div style="background-color:{result['rec_color']};padding:1.5rem;border-radius:16px;color:white;text-align:center;margin:1rem 0;">
        <h2 style="margin:0;">{result['recommendation']}</h2>
        <p style="margin:0.5rem 0 0 0;">Intrinsic Value: {cur}{result['intrinsic_value']:.2f} | Upside: {result['upside']:+.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Intrinsic Value", f"{cur}{result['intrinsic_value']:.2f}")
    col2.metric("Current Price", f"{cur}{cp:.2f}", delta=f"{result['upside']:+.1f}%")
    col3.metric("WACC", f"{result['wacc']*100:.1f}%")
    col4.metric("Bear/Bull", f"{cur}{result['bear_case']:.0f} - {cur}{result['bull_case']:.0f}")
    
    # FCF Chart
    unit = 'Cr' if analyzer.currency == 'INR' else 'B'
    div = 1e7 if analyzer.currency == 'INR' else 1e9
    years = [p['year'] for p in result['projections']]
    fcf_vals = [p['fcf']/div for p in result['projections']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=fcf_vals, name='FCF', marker_color='#667eea'))
    fig.update_layout(title=f'10-Year FCF Projection ({cur}{unit})', template='plotly_white', height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    # Graham & EPV
    eps = analyzer.ratios.get('EPS', ni/shares if ni and shares else 1)
    graham_val = GrahamValuation.calculate(eps, rg, rf)
    epv = EarningsPowerValue.calculate(rev or 0, om, 0.25, result['wacc'], shares)
    
    # All models comparison
    st.markdown("### 📊 Valuation Model Comparison")
    models = {'Advanced DCF': result['intrinsic_value'], 'Graham': graham_val, 'EPV': epv, 'Current Price': cp}
    fig = go.Figure()
    for model, val in models.items():
        color = '#10b981' if val > cp else '#ef4444' if val < cp else '#f59e0b'
        fig.add_trace(go.Bar(x=[model], y=[val], marker_color=color, text=[f"{cur}{val:.2f}"], textposition='outside'))
    fig.add_hline(y=cp, line_dash="dash", line_color="#94a3b8", annotation_text=f"Current: {cur}{cp:.2f}")
    fig.update_layout(title='All Valuation Models', template='plotly_white', height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def create_stress_test_dashboard(analyzer):
    st.markdown('<div class="section-header">🎲 Monte Carlo Stress Test</div>', unsafe_allow_html=True)
    
    prices = analyzer.financials.get('prices')
    cp = analyzer.live_price_data.get('current_price')
    cur = analyzer.currency_symbol
    
    if not cp or prices is None or prices.empty: st.warning("Need price data."); return
    
    returns = prices['Close'].pct_change().dropna()
    vol = returns.std() * np.sqrt(252)
    er = returns.mean() * 252
    
    with st.expander("⚙️ Simulation Parameters", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            num_sims = st.select_slider("Simulations", [100, 500, 1000, 5000, 10000], value=1000)
            days = st.select_slider("Time Horizon (Days)", [63, 126, 252, 504], value=252)
        with c2:
            vol_in = st.number_input("Volatility %", value=round(vol*100, 1)) / 100
            er_in = st.number_input("Expected Return %", value=round(er*100, 1)) / 100
    
    if st.button("🎲 Run Monte Carlo Simulation", type="primary", use_container_width=True):
        mc = MonteCarloStressTest(cp, vol_in, er_in)
        result = mc.run(num_sims, days)
        
        st.success(f"✅ {num_sims:,} scenarios tested!")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Expected Price", f"{cur}{result['expected_price']:.2f}")
        col2.metric("VaR 95%", f"{cur}{result['var_95']:.2f}", delta=f"{result['max_loss']:+.1f}%", delta_color="inverse")
        col3.metric("Prob. of Profit", f"{result['prob_profit']:.1f}%")
        col4.metric("CVaR 95%", f"{cur}{result['cvar_95']:.2f}")
        
        # Simulation paths
        fig = go.Figure()
        for i in range(min(100, num_sims)):
            fig.add_trace(go.Scatter(y=result['simulations'][i], mode='lines', line=dict(width=0.5, color='rgba(102,126,234,0.1)'), showlegend=False))
        fig.add_hline(y=cp, line_dash="dash", line_color="#10b981", annotation_text="Current")
        fig.add_hline(y=result['expected_price'], line_dash="dash", line_color="#f59e0b", annotation_text="Expected")
        fig.update_layout(title=f'Monte Carlo Price Paths ({num_sims} scenarios)', template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=result['final_prices'], nbinsx=50, marker_color='#667eea', opacity=0.7, histnorm='probability density'))
        fig.add_vline(x=cp, line_dash="dash", line_color="#10b981", annotation_text="Current")
        fig.add_vline(x=result['expected_price'], line_dash="dash", line_color="#f59e0b", annotation_text="Expected")
        fig.add_vline(x=result['var_95'], line_dash="dot", line_color="#ef4444", annotation_text="VaR 95%")
        fig.update_layout(title='Final Price Distribution', template='plotly_white', height=350)
        st.plotly_chart(fig, use_container_width=True)


def create_technical_dashboard(analyzer):
    st.markdown('<div class="section-header">📈 Technical Analysis</div>', unsafe_allow_html=True)
    
    prices = analyzer.financials.get('prices')
    if prices is None or prices.empty: st.warning("No price data."); return
    
    close = prices['Close']
    cur = analyzer.currency_symbol
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = close.ewm(span=12).mean(); ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26; signal = macd.ewm(span=9).mean(); hist = macd - signal
    
    # Bollinger
    sma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20; lower = sma20 - 2 * std20
    
    # Signals
    rsi_now = rsi.iloc[-1]
    rsi_sig = "Overbought 🔴" if rsi_now > 70 else "Oversold 🟢" if rsi_now < 30 else "Neutral 🟡"
    macd_sig = "Bullish 🟢" if macd.iloc[-1] > signal.iloc[-1] else "Bearish 🔴"
    sma50 = close.rolling(50).mean().iloc[-1]; sma200 = close.rolling(200).mean().iloc[-1]
    trend = "Golden Cross ✨" if sma50 > sma200 else "Death Cross 💀"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RSI (14)", f"{rsi_now:.1f}", delta=rsi_sig)
    col2.metric("MACD", f"{macd.iloc[-1]:.2f}", delta=macd_sig)
    col3.metric("Trend", trend.split(' ')[0])
    col4.metric("Close", f"{cur}{close.iloc[-1]:.2f}")
    
    # Combined chart
    idx = slice(-120, None)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.5, 0.25, 0.25])
    fig.add_trace(go.Scatter(x=close.index[idx], y=upper.iloc[idx], line=dict(color='gray', width=1, dash='dash'), name='Upper BB'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[idx], y=sma20.iloc[idx], line=dict(color='orange', width=1.5), name='20 MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[idx], y=lower.iloc[idx], line=dict(color='gray', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(102,126,234,0.1)', name='Lower BB'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[idx], y=close.iloc[idx], line=dict(color='#667eea', width=2), name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=rsi.index[idx], y=rsi.iloc[idx], line=dict(color='#667eea', width=2), name='RSI'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_trace(go.Scatter(x=macd.index[idx], y=macd.iloc[idx], line=dict(color='#667eea', width=2), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=signal.index[idx], y=signal.iloc[idx], line=dict(color='#f59e0b', width=1.5), name='Signal'), row=3, col=1)
    colors = ['#10b981' if h >= 0 else '#ef4444' for h in hist.iloc[idx]]
    fig.add_trace(go.Bar(x=hist.index[idx], y=hist.iloc[idx], marker_color=colors, name='Histogram'), row=3, col=1)
    fig.update_layout(height=750, template='plotly_white', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


def create_portfolio_tracker():
    st.markdown('<div class="section-header">💼 Portfolio Tracker</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add Stock to Portfolio", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1: add_t = st.text_input("Ticker", key="pt_t")
        with c2: add_q = st.number_input("Quantity", min_value=1, value=10, key="pt_q")
        with c3: add_p = st.number_input("Buy Price", min_value=0.01, value=100.0, key="pt_p")
        if st.button("➕ Add to Portfolio", type="primary"):
            st.session_state['portfolio'].append({'ticker': add_t.upper(), 'quantity': add_q, 'buy_price': add_p, 'date': datetime.now().strftime('%Y-%m-%d')})
            st.success(f"Added {add_t}!"); st.rerun()
    
    if st.session_state['portfolio']:
        data = []; total_inv = 0; total_cur = 0
        for i, h in enumerate(st.session_state['portfolio']):
            try:
                t = INDIAN_STOCKS_DB.get(h['ticker'], h['ticker'])
                s = yf.Ticker(t); info = s.info
                is_ind = t.endswith('.NS') or t.endswith('.BO')
                cur_sym = '₹' if is_ind else '$'
                cp_s = info.get('currentPrice') or info.get('regularMarketPrice', h['buy_price'])
                inv = h['quantity'] * h['buy_price']; cur_v = h['quantity'] * cp_s
                pnl = cur_v - inv; pnl_pct = (pnl/inv)*100 if inv > 0 else 0
                total_inv += inv; total_cur += cur_v
                data.append({'#': i+1, 'Ticker': h['ticker'], 'Qty': h['quantity'],
                           'Buy': f"{cur_sym}{h['buy_price']:.2f}", 'Current': f"{cur_sym}{cp_s:.2f}",
                           'Invested': f"{cur_sym}{inv:,.0f}", 'Value': f"{cur_sym}{cur_v:,.0f}",
                           'P&L': pnl, 'P&L %': pnl_pct})
            except: pass
        
        if data:
            df = pd.DataFrame(data)
            def color_pnl(val):
                return 'color: #10b981; font-weight: 700' if isinstance(val, (int, float)) and val > 0 else 'color: #ef4444; font-weight: 700' if isinstance(val, (int, float)) and val < 0 else ''
            st.dataframe(df.style.applymap(color_pnl, subset=['P&L', 'P&L %']), use_container_width=True, height=300)
            
            total_pnl = total_cur - total_inv
            total_pnl_pct = (total_pnl/total_inv)*100 if total_inv > 0 else 0
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Invested", f"${total_inv:,.0f}")
            c2.metric("Current Value", f"${total_cur:,.0f}")
            c3.metric("Total P&L", f"${total_pnl:,.0f}", delta=f"{total_pnl_pct:.1f}%")
            c4.metric("Holdings", len(st.session_state['portfolio']))
            
            if len(st.session_state['portfolio']) > 1:
                st.markdown("#### 🎯 Diversification")
                tickers = [h['ticker'] for h in st.session_state['portfolio']]
                values = []
                for h in st.session_state['portfolio']:
                    try:
                        t = INDIAN_STOCKS_DB.get(h['ticker'], h['ticker'])
                        s = yf.Ticker(t); cp_s = s.info.get('currentPrice', h['buy_price'])
                        values.append(h['quantity'] * cp_s)
                    except: values.append(h['quantity'] * h['buy_price'])
                fig = go.Figure(data=[go.Pie(labels=tickers, values=values, hole=0.4)])
                fig.update_layout(height=350, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
            
            if st.button("🗑️ Clear Portfolio"):
                st.session_state['portfolio'] = []; st.rerun()
    else:
        st.info("📝 Your portfolio is empty. Add stocks using the expander above!")


def get_peer_comparison(main_ticker, peer_tickers):
    data = []
    for ticker in peer_tickers:
        try:
            s = yf.Ticker(ticker); info = s.info
            if not info: continue
            is_ind = ticker.endswith('.NS') or ticker.endswith('.BO')
            p_cur = 'INR' if is_ind else 'USD'
            mcap = info.get('marketCap', 0) or 0
            mcap_disp = round(mcap/1e7, 1) if p_cur == 'INR' else round(mcap/1e9, 1)
            mcap_unit = 'Cr' if p_cur == 'INR' else 'B'
            mcap_sign = '₹' if p_cur == 'INR' else '$'
            data.append({
                'Ticker': ticker.replace('.NS','').replace('.BO',''),
                'Company': info.get('longName', ticker)[:25],
                'Market Cap': f"{mcap_sign}{mcap_disp} {mcap_unit}",
                'P/E': round(info.get('trailingPE', 0), 1) if info.get('trailingPE') else 'N/A',
                'ROE %': round((info.get('returnOnEquity', 0) or 0)*100, 1),
                'D/E': round(info.get('debtToEquity', 0) or 0, 2),
                'Div Yield %': round((info.get('dividendYield', 0) or 0)*100, 2),
                'Price': info.get('currentPrice') or info.get('regularMarketPrice'),
            })
        except: continue
    return pd.DataFrame(data)


def detect_peer_group(ticker):
    for group_name, tickers in PEER_GROUPS.items():
        if ticker in tickers: return group_name, tickers
    return None, []


# ===== MAIN APP =====
def main():
    st.markdown('<h1 class="main-header">📊 FinAnalyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced DCF • Monte Carlo Stress Tests • Graham & EPV • Technical Analysis • Portfolio • Peer Comparison</p>', unsafe_allow_html=True)

    if 'current_ticker' not in st.session_state: st.session_state['current_ticker'] = "AAPL"
    if 'current_exchange' not in st.session_state: st.session_state['current_exchange'] = "Auto-detect"
    if 'analyze_clicked' not in st.session_state: st.session_state['analyze_clicked'] = False

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Stock Analysis", "🎲 Stress Test", "💼 Portfolio", "📈 Technical"])

    # ===== TAB 1: STOCK ANALYSIS =====
    with tab1:
        c1, c2, c3 = st.columns([3, 1.5, 1])
        with c1: ticker = st.text_input("Stock Ticker", value=st.session_state['current_ticker'], max_chars=50, key="main_ticker", placeholder="e.g., AAPL, RELIANCE, TATAMOTORS")
        with c2: exchange = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"], index=["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"].index(st.session_state['current_exchange']), key="main_exchange")
        with c3: st.write(""); st.write(""); analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True, key="main_analyze")

        # Quick Access
        st.markdown("#### ⚡ Quick Access")
        qcols = st.columns(8)
        quick_stocks = ["AAPL", "RELIANCE", "TCS", "MSFT", "TATAMOTORS", "INFY", "GOOGL", "HDFCBANK"]
        quick_exchanges = ["US Market", "NSE India (.NS)", "NSE India (.NS)", "US Market", "NSE India (.NS)", "NSE India (.NS)", "US Market", "NSE India (.NS)"]
        for i, (s, e) in enumerate(zip(quick_stocks, quick_exchanges)):
            with qcols[i]:
                if st.button(s, use_container_width=True, key=f"quick_{s}"):
                    st.session_state['current_ticker'] = s; st.session_state['current_exchange'] = e
                    st.session_state['analyze_clicked'] = True; st.rerun()

        # More stocks
        with st.expander("📋 More Stocks"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Indian Stocks**")
                icols = st.columns(4)
                for i, t in enumerate(list(INDIAN_STOCKS_DB.keys())[:24]):
                    with icols[i%4]:
                        if st.button(t, use_container_width=True, key=f"mi_{t}"):
                            st.session_state['current_ticker'] = t; st.session_state['current_exchange'] = "NSE India (.NS)"
                            st.session_state['analyze_clicked'] = True; st.rerun()
            with c2:
                st.markdown("**US Stocks**")
                ucols = st.columns(4)
                us_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "WMT", "NFLX", "ADBE", "ORCL", "CRM", "AMD", "INTC"]
                for i, s in enumerate(us_list):
                    with ucols[i%4]:
                        if st.button(s, use_container_width=True, key=f"mu_{s}"):
                            st.session_state['current_ticker'] = s; st.session_state['current_exchange'] = "US Market"
                            st.session_state['analyze_clicked'] = True; st.rerun()

        st.session_state['current_ticker'] = ticker
        st.session_state['current_exchange'] = exchange
        if analyze_btn: st.session_state['analyze_clicked'] = True

        if not st.session_state['analyze_clicked']:
            st.markdown('<div style="text-align:center;padding:4rem 2rem;"><h2 style="color:#e2e8f0;">🏦 Enterprise Financial Analysis Platform</h2><p style="color:#94a3b8;">Advanced DCF • Monte Carlo • Graham • EPV • Technical Analysis</p></div>', unsafe_allow_html=True)
        else:
            em = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            analyzer = ProFinancialAnalyzer(st.session_state['current_ticker'], exchange=em.get(st.session_state['current_exchange'], "Auto"))

            with st.spinner("🔍 Running comprehensive analysis..."):
                analyzer.get_live_price()
                analyzer.fetch_financial_data()
                analyzer.calculate_all_ratios()

            # Live Price
            pd_d = analyzer.live_price_data; cur = analyzer.currency_symbol
            cp = pd_d.get('current_price'); pc = pd_d.get('previous_close')
            if cp and pc:
                ch = cp - pc; ch_pct = (ch/pc)*100
                color = "price-up" if ch >= 0 else "price-down"; arrow = "▲" if ch >= 0 else "▼"
                st.markdown(f'<div class="live-price-box"><div style="position:relative;z-index:1;"><h2 style="margin:0;">{analyzer.company_name}</h2><div class="{color}">{cur}{cp:.2f} {arrow}</div><div style="font-size:1.2rem;margin-top:0.5rem;">{cur}{abs(ch):.2f} ({ch_pct:+.2f}%)</div><div style="margin-top:1rem;display:flex;justify-content:center;gap:2rem;font-size:0.9rem;opacity:0.8;"><span>H: {cur}{pd_d.get("day_high","N/A")}</span><span>L: {cur}{pd_d.get("day_low","N/A")}</span><span>Vol: {pd_d.get("volume","N/A"):,.0f}</span></div></div></div>', unsafe_allow_html=True)

            # Analyst Recommendation
            rec = analyzer.live_price_data.get('recommendation', '').upper()
            if rec:
                rc = {'BUY': '#10b981', 'STRONG_BUY': '#10b981', 'HOLD': '#f59e0b', 'SELL': '#ef4444', 'STRONG_SELL': '#ef4444'}.get(rec, '#666')
                analysts = analyzer.live_price_data.get('number_of_analysts', 'N/A')
                st.markdown(f'<div style="background-color:{rc};padding:0.75rem;border-radius:12px;color:white;text-align:center;font-weight:700;margin:0.5rem 0;">🎯 {rec.replace("_"," ")} • Based on {analysts} Analysts</div>', unsafe_allow_html=True)

            # Company Info
            st.markdown(f'<div class="info-box"><span>📊 <strong>{analyzer.company_name}</strong> | {analyzer.financials.get("sector","N/A")} | {analyzer.currency} ({analyzer.currency_symbol})</span><span>💰 Market Cap: {analyzer._format_amount(pd_d.get("market_cap",0))}</span><span class="source-badge source-yahoo">{analyzer.data_source}</span></div>', unsafe_allow_html=True)

            # Key Ratios
            st.markdown('<div class="section-header">📊 Key Financial Ratios</div>', unsafe_allow_html=True)
            ratios = analyzer.ratios
            if ratios:
                cols = st.columns(5)
                km = [('P/E Ratio', ratios.get('P/E Ratio')), ('ROE %', ratios.get('ROE')),
                      ('P/B Ratio', ratios.get('P/B Ratio')), ('Debt/Equity', ratios.get('Debt to Equity')),
                      ('Div Yield %', ratios.get('Dividend Yield'))]
                for col, (l, v) in zip(cols, km):
                    with col:
                        if isinstance(v, (int, float)):
                            d = f"{v:.1f}%" if l in ['ROE %', 'Div Yield %'] else f"{v:.2f}"
                            st.markdown(f'<div class="card"><div class="metric-value">{d}</div><div class="metric-label">{l}</div></div>', unsafe_allow_html=True)

            # Valuation Dashboard
            create_valuation_dashboard(analyzer)

            # Peer Comparison
            group_name, peer_list = detect_peer_group(analyzer.ticker)
            if peer_list:
                peer_list = [p for p in peer_list if p != analyzer.ticker][:5]
                all_t = [analyzer.ticker] + peer_list
                if len(all_t) >= 2:
                    with st.spinner("Fetching peer comparison data..."):
                        pdf = get_peer_comparison(analyzer.ticker, all_t)
                        if not pdf.empty:
                            st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
                            st.dataframe(pdf, use_container_width=True, hide_index=True)
                            st.caption(f"📌 Peer Group: {group_name.replace('_', ' ')}")

            # Financial Statements
            st.markdown('<div class="section-header">📋 Financial Statements</div>', unsafe_allow_html=True)
            st.caption(f"All amounts in {analyzer.currency} ({analyzer.currency_symbol})")
            t1, t2, t3 = st.tabs(["📊 Income Statement", "💰 Balance Sheet", "💵 Cash Flow"])
            for tab, key, name in [(t1, 'income', 'Income'), (t2, 'balance', 'Balance'), (t3, 'cashflow', 'Cash')]:
                with tab:
                    df = analyzer.financials.get(key)
                    if df is not None and not df.empty:
                        formatted = format_financial_df(df, analyzer.currency_symbol, analyzer.currency)
                        if formatted is not None: st.dataframe(formatted, use_container_width=True)
                        with st.expander("📥 Download CSV"):
                            st.download_button(f"Download {name} Statement", df.to_csv(), f"{analyzer.original_ticker}_{key}.csv", "text/csv")
                    else:
                        st.info(f"{name} Statement not available. Key metrics calculated from available data.")

    # ===== TAB 2: STRESS TEST =====
    with tab2:
        st.markdown("### 🎲 Monte Carlo Stress Test")
        st2_t = st.text_input("Ticker", "AAPL", key="st2_t")
        st2_e = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"], key="st2_e")
        if st.button("🎲 Run Stress Test", type="primary", key="st2_btn"):
            em2 = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            a2 = ProFinancialAnalyzer(st2_t, exchange=em2.get(st2_e, "Auto"))
            with st.spinner("Loading data..."): a2.get_live_price(); a2.fetch_financial_data()
            create_stress_test_dashboard(a2)

    # ===== TAB 3: PORTFOLIO =====
    with tab3:
        create_portfolio_tracker()

    # ===== TAB 4: TECHNICAL =====
    with tab4:
        st.markdown("### 📈 Technical Analysis")
        ta_t = st.text_input("Ticker", "AAPL", key="ta_t")
        ta_e = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"], key="ta_e")
        if st.button("📈 Run Technical Analysis", type="primary", key="ta_btn"):
            em3 = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            a3 = ProFinancialAnalyzer(ta_t, exchange=em3.get(ta_e, "Auto"))
            with st.spinner("Calculating indicators..."): a3.get_live_price(); a3.fetch_financial_data()
            create_technical_dashboard(a3)

    st.divider()
    st.caption(f"FinAnalyzer Pro | Enterprise Financial Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()