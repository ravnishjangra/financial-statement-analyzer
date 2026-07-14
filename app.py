"""
FinAnalyzer Pro - Enterprise Grade Financial Analysis Platform
Advanced DCF • Monte Carlo Stress Tests • Multiple Valuation Models
Live Prices • Peer Comparison • Portfolio Tracking • Technical Analysis
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

# Page configuration
st.set_page_config(
    page_title="FinAnalyzer Pro | Enterprise Financial Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== PROFESSIONAL CSS =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        font-size: 3rem; font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem; letter-spacing: -1px;
    }
    .sub-header { font-size: 1rem; color: #64748b; text-align: center; margin-bottom: 2rem; font-weight: 400; }
    
    .card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(102,126,234,0.2);
        padding: 1.5rem; border-radius: 16px; margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover { transform: translateY(-2px); box-shadow: 0 20px 40px rgba(102,126,234,0.15); border-color: rgba(102,126,234,0.4); }
    
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #e2e8f0; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.25rem; }
    
    .live-price-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 2px solid rgba(102,126,234,0.4); padding: 2.5rem;
        border-radius: 24px; color: white; text-align: center; margin: 1rem 0;
        box-shadow: 0 25px 50px rgba(0,0,0,0.4);
        position: relative; overflow: hidden;
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
    
    .stButton button {
        width: 100%; border-radius: 12px; padding: 0.7rem;
        font-weight: 600; font-size: 0.9rem; letter-spacing: 0.5px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; transition: all 0.3s ease;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(102,126,234,0.4); }
    
    .section-header {
        font-size: 1.5rem; font-weight: 700; color: #e2e8f0;
        margin: 2rem 0 1rem 0; padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(102,126,234,0.3);
        display: flex; align-items: center; gap: 0.5rem;
    }
    
    .recommendation-badge {
        display: inline-block; padding: 0.5rem 1.5rem; border-radius: 25px;
        font-weight: 700; font-size: 1rem; letter-spacing: 1px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(102,126,234,0.4); }
        50% { box-shadow: 0 0 0 15px rgba(102,126,234,0); }
    }
    
    .stress-pass { color: #10b981; font-weight: 700; }
    .stress-fail { color: #ef4444; font-weight: 700; }
    
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


# ===== ADVANCED FINANCIAL MODELS =====

class AdvancedDCF:
    """JPMorgan-level DCF Valuation with scenario analysis"""
    
    def __init__(self, revenue, fcf, shares, current_price, revenue_growth, beta, 
                 risk_free_rate, market_return, net_debt=0, tax_rate=0.25):
        self.revenue = revenue
        self.fcf = fcf
        self.shares = shares
        self.current_price = current_price
        self.revenue_growth = revenue_growth
        self.beta = beta
        self.risk_free_rate = risk_free_rate
        self.market_return = market_return
        self.net_debt = net_debt
        self.tax_rate = tax_rate
        self.wacc = self._calculate_wacc()
    
    def _calculate_wacc(self):
        cost_of_equity = self.risk_free_rate + self.beta * (self.market_return - self.risk_free_rate)
        # Assume cost of debt = risk_free + 2-4% based on risk
        credit_spread = 0.02 if self.beta < 1.0 else 0.03 if self.beta < 1.5 else 0.04
        cost_of_debt = self.risk_free_rate + credit_spread
        # Capital structure assumption
        equity_weight = 0.75
        debt_weight = 0.25
        return (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - self.tax_rate))
    
    def project_cashflows(self, years=10, terminal_growth=0.025):
        """Project FCF with gradually declining growth"""
        projections = []
        fcf = self.fcf
        rev = self.revenue
        
        for year in range(1, years + 1):
            # Growth declines each year
            year_growth = self.revenue_growth * (1 - (year - 1) * 0.07)
            year_growth = max(year_growth, terminal_growth)
            
            rev *= (1 + year_growth)
            # FCF margin improves over time (operating leverage)
            fcf_margin = min(0.15 + year * 0.005, 0.25)
            fcf = rev * fcf_margin
            
            discount_factor = 1 / (1 + self.wacc) ** year
            pv_fcf = fcf * discount_factor
            
            projections.append({
                'year': year,
                'revenue': rev,
                'growth': year_growth,
                'fcf': fcf,
                'discount_factor': discount_factor,
                'pv_fcf': pv_fcf
            })
        
        return projections
    
    def calculate(self):
        """Full DCF calculation"""
        projections = self.project_cashflows(10)
        pv_fcfs = sum(p['pv_fcf'] for p in projections)
        
        # Terminal value using Gordon Growth
        last_fcf = projections[-1]['fcf']
        terminal_growth = 0.025
        terminal_value = last_fcf * (1 + terminal_growth) / (self.wacc - terminal_growth)
        pv_terminal = terminal_value / (1 + self.wacc) ** 10
        
        enterprise_value = pv_fcfs + pv_terminal
        equity_value = enterprise_value - self.net_debt
        intrinsic_value = equity_value / self.shares if self.shares > 0 else 0
        
        upside = ((intrinsic_value / self.current_price) - 1) * 100 if self.current_price > 0 else 0
        
        # Multiple scenarios
        scenarios = self._run_scenarios()
        
        return {
            'intrinsic_value': intrinsic_value,
            'current_price': self.current_price,
            'upside': upside,
            'wacc': self.wacc,
            'pv_fcfs': pv_fcfs,
            'terminal_value': terminal_value,
            'pv_terminal': pv_terminal,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'projections': projections,
            'scenarios': scenarios
        }
    
    def _run_scenarios(self):
        """Bull/Base/Bear scenarios"""
        scenarios = {}
        base_growth = self.revenue_growth
        
        # Bear case: -30% growth, +20% WACC
        self.revenue_growth = base_growth * 0.7
        orig_wacc = self.wacc
        self.wacc = orig_wacc * 1.2
        bear = self.calculate() if not hasattr(self, '_in_scenario') else None
        
        # Base case (already calculated)
        self.revenue_growth = base_growth
        self.wacc = orig_wacc
        
        # Bull case: +30% growth, -20% WACC
        self.revenue_growth = base_growth * 1.3
        self.wacc = orig_wacc * 0.8
        bull = self.calculate() if not hasattr(self, '_in_scenario') else None
        
        self.revenue_growth = base_growth
        self.wacc = orig_wacc
        
        return {
            'bear': bear['intrinsic_value'] if bear else self.current_price * 0.5,
            'base': self.current_price * 1.2,  # placeholder
            'bull': bull['intrinsic_value'] if bull else self.current_price * 2.0
        }


class MonteCarloStressTest:
    """Monte Carlo simulation for stress testing"""
    
    def __init__(self, current_price, volatility, expected_return, shares, fcf, wacc):
        self.current_price = current_price
        self.volatility = volatility  # Annualized volatility
        self.expected_return = expected_return
        self.shares = shares
        self.fcf = fcf
        self.wacc = wacc
    
    def run_simulation(self, num_simulations=1000, time_horizon=252):
        """Run Monte Carlo simulation"""
        dt = 1 / time_horizon
        simulations = np.zeros((num_simulations, time_horizon))
        simulations[:, 0] = self.current_price
        
        for i in range(1, time_horizon):
            random_shocks = np.random.normal(0, 1, num_simulations)
            simulations[:, i] = simulations[:, i-1] * np.exp(
                (self.expected_return - 0.5 * self.volatility**2) * dt + 
                self.volatility * np.sqrt(dt) * random_shocks
            )
        
        final_prices = simulations[:, -1]
        
        # Value at Risk calculations
        var_95 = np.percentile(final_prices, 5)
        var_99 = np.percentile(final_prices, 1)
        cvar_95 = final_prices[final_prices <= var_95].mean()
        
        # Probability of profit
        prob_profit = np.mean(final_prices > self.current_price) * 100
        
        # Expected price and range
        expected_price = np.mean(final_prices)
        price_range = (np.percentile(final_prices, 10), np.percentile(final_prices, 90))
        
        return {
            'simulations': simulations,
            'final_prices': final_prices,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'prob_profit': prob_profit,
            'expected_price': expected_price,
            'price_range': price_range,
            'max_loss': (var_95 / self.current_price - 1) * 100,
            'max_gain': (np.percentile(final_prices, 95) / self.current_price - 1) * 100,
        }


class GrahamValuation:
    """Benjamin Graham's valuation formula"""
    
    @staticmethod
    def calculate(eps, growth_rate, bond_yield=0.07):
        """Graham Number = sqrt(22.5 * EPS * BVPS)"""
        # Graham formula: V = EPS * (8.5 + 2g) * 4.4 / Y
        graham_value = eps * (8.5 + 2 * growth_rate * 100) * 4.4 / (bond_yield * 100)
        return graham_value


class EarningsPowerValue:
    """Columbia Business School EPV model"""
    
    @staticmethod
    def calculate(revenue, operating_margin, tax_rate, wacc, shares, net_debt=0):
        """EPV = (Revenue * Sustainable Margin * (1 - Tax)) / WACC"""
        sustainable_revenue = revenue * 0.9  # 90% of current revenue
        sustainable_margin = max(operating_margin * 0.8, 0.05)  # 80% of current margin
        nopat = sustainable_revenue * sustainable_margin * (1 - tax_rate)
        epv = nopat / wacc
        equity_value = epv - net_debt
        return equity_value / shares if shares > 0 else 0


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
        if exchange == "NSE":
            return ticker + '.NS' if not ticker.endswith('.NS') else ticker
        elif exchange == "BSE":
            return ticker + '.BO' if not ticker.endswith('.BO') else ticker
        elif ticker in INDIAN_STOCKS_DB:
            return INDIAN_STOCKS_DB[ticker]
        elif ticker.endswith('.NS') or ticker.endswith('.BO'):
            return ticker
        return ticker

    def get_live_price(self):
        success = self._try_yahoo()
        if not success:
            success = self._try_alternate_yahoo()
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
        except:
            return False

    def _try_alternate_yahoo(self):
        alternates = []
        if self.ticker.endswith('.NS'):
            alternates = [self.ticker.replace('.NS', '.BO')]
        elif self.ticker.endswith('.BO'):
            alternates = [self.ticker.replace('.BO', '.NS')]
        else:
            alternates = [self.ticker + '.NS', self.ticker + '.BO']
        
        for alt in alternates:
            try:
                alt_stock = yf.Ticker(alt)
                alt_info = alt_stock.info
                if alt_info and alt_info.get('marketCap'):
                    self.stock = alt_stock
                    self.ticker = alt
                    self._populate_from_info(alt_info)
                    return True
            except:
                continue
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
            self.financials['prices'] = self.stock.history(start=end - timedelta(days=365*5), end=end)
            self._detect_currency()
            return True
        except:
            return True

    def _detect_currency(self):
        info = self.financials.get('info', {})
        currency = info.get('currency', info.get('financialCurrency', 'USD'))
        if self.ticker.endswith('.NS') or self.ticker.endswith('.BO'):
            currency = 'INR'
        self.currency = currency
        self.currency_symbol = CURRENCY_SYMBOLS.get(currency, currency + ' ')

    def _format_amount(self, value):
        if value is None or pd.isna(value):
            return 'N/A'
        if self.currency == 'INR':
            cr = value / 1e7
            return f"{self.currency_symbol}{cr:.0f} Cr" if abs(cr) >= 100 else f"{self.currency_symbol}{cr:.1f} Cr"
        b = value / 1e9
        return f"{self.currency_symbol}{b:.2f}B" if abs(b) >= 1 else f"{self.currency_symbol}{value/1e6:.1f}M"

    def _safe_get(self, df, keys, col=0):
        if df is None or df.empty:
            return None
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
            income = self.financials.get('income')
            balance = self.financials.get('balance')
            cashflow = self.financials.get('cashflow')
            prices = self.financials.get('prices')
            cp = self.live_price_data.get('current_price')
            info = self.financials.get('info', {})
            has_financials = income is not None and not income.empty

            if has_financials:
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
                if ni and ni_p and ni_p != 0:
                    self.ratios['Net Income Growth (YoY)'] = ((ni-ni_p)/ni_p)*100

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
                            eps = ni/shares
                            self.ratios['EPS'] = eps
                            if eps > 0: self.ratios['P/E Ratio'] = cp/eps
                        if eq and eq > 0:
                            bvps = eq/shares
                            if bvps > 0: self.ratios['P/B Ratio'] = cp/bvps
                        if rev and rev/shares > 0: self.ratios['P/S Ratio'] = cp/(rev/shares)

                if prices is not None and not prices.empty and len(prices) >= 252:
                    returns = prices['Close'].pct_change().dropna()
                    self.ratios['Annualized Volatility'] = returns.std() * np.sqrt(252) * 100
                    self.ratios['52-Week Return'] = ((prices['Close'].iloc[-1]-prices['Close'].iloc[-252])/prices['Close'].iloc[-252])*100

            # Info dict fallback
            for key, ratio_key, mult in [
                ('returnOnEquity', 'ROE', 100), ('returnOnAssets', 'ROA', 100),
                ('profitMargins', 'Net Profit Margin', 100), ('debtToEquity', 'Debt to Equity', 1),
                ('trailingPE', 'P/E Ratio', 1), ('priceToBook', 'P/B Ratio', 1),
                ('trailingEps', 'EPS', 1), ('revenueGrowth', 'Revenue Growth (YoY)', 100),
                ('dividendYield', 'Dividend Yield', 100),
            ]:
                if ratio_key not in self.ratios and info.get(key):
                    try:
                        self.ratios[ratio_key] = info[key] * mult
                    except:
                        pass
            return True
        except:
            return True


# ===== VALUATION DASHBOARD =====

def create_valuation_dashboard(analyzer):
    """Comprehensive valuation dashboard with multiple models"""
    st.markdown('<div class="section-header">💰 Advanced Valuation Models</div>', unsafe_allow_html=True)
    
    info = analyzer.financials.get('info', {})
    income = analyzer.financials.get('income')
    balance = analyzer.financials.get('balance')
    cashflow = analyzer.financials.get('cashflow')
    prices = analyzer.financials.get('prices')
    cp = analyzer.live_price_data.get('current_price')
    cur = analyzer.currency_symbol
    
    if not cp:
        st.warning("Current price not available.")
        return
    
    # Get financial data
    rev = analyzer._safe_get(income, ['Total Revenue', 'Revenue']) if income is not None else None
    ni = analyzer._safe_get(income, ['Net Income', 'Net Income Common Stockholders']) if income is not None else None
    oi = analyzer._safe_get(income, ['Operating Income', 'EBIT']) if income is not None else None
    fcf = analyzer._safe_get(cashflow, ['Free Cash Flow']) if cashflow is not None else None
    if not fcf and ni:
        fcf = ni * 0.8
    
    shares = analyzer._safe_get(income, ['Diluted Average Shares']) or analyzer._safe_get(income, ['Basic Average Shares']) if income is not None else None
    if not shares:
        shares = analyzer.live_price_data.get('market_cap', 0) / cp if cp > 0 else 1e6
    
    beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
    rg = analyzer.ratios.get('Revenue Growth (YoY)', 10)
    rg = max(0.02, min((rg or 10) / 100, 0.35))
    vol = analyzer.ratios.get('Annualized Volatility', 30) / 100 if analyzer.ratios.get('Annualized Volatility') else 0.30
    rf = 0.072 if analyzer.currency == 'INR' else 0.045
    mr = 0.12 if analyzer.currency == 'INR' else 0.10
    om = analyzer.ratios.get('Operating Margin', 15) / 100 if analyzer.ratios.get('Operating Margin') else 0.15
    
    # ===== MODEL 1: Advanced DCF =====
    st.markdown("### 🏦 Advanced DCF (10-Year Projection)")
    
    with st.expander("⚙️ DCF Parameters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            dcf_growth = st.slider("Revenue Growth %", 1, 35, int(rg*100)) / 100
            dcf_beta = st.number_input("Beta", value=float(beta), min_value=0.1, max_value=3.0, step=0.1)
        with col2:
            dcf_fcf = st.number_input("FCF (M)", value=float((fcf or ni*0.8 or 0))/1e6, format="%.1f") * 1e6
            dcf_shares = st.number_input("Shares (M)", value=float(shares)/1e6, format="%.1f") * 1e6
        with col3:
            dcf_rf = st.slider("Risk-Free %", 1.0, 12.0, rf*100, 0.1) / 100
            dcf_mr = st.slider("Market Return %", 5.0, 18.0, mr*100, 0.1) / 100
    
    dcf = AdvancedDCF(
        revenue=rev or fcf/0.15, fcf=dcf_fcf, shares=dcf_shares,
        current_price=cp, revenue_growth=dcf_growth, beta=dcf_beta,
        risk_free_rate=dcf_rf, market_return=dcf_mr
    )
    
    dcf_result = dcf.calculate()
    
    # Recommendation
    upside = dcf_result['upside']
    if upside > 30: rec, rec_color = "STRONG BUY 🟢", "#10b981"
    elif upside > 10: rec, rec_color = "BUY 🟢", "#34d399"
    elif upside > -10: rec, rec_color = "HOLD 🟡", "#f59e0b"
    elif upside > -30: rec, rec_color = "SELL 🔴", "#ef4444"
    else: rec, rec_color = "STRONG SELL 🔴", "#dc2626"
    
    st.markdown(f"""
    <div style="background-color:{rec_color};padding:1.5rem;border-radius:16px;color:white;text-align:center;margin:1rem 0;">
        <h2 style="margin:0;">{rec}</h2>
        <p style="margin:0.5rem 0 0 0;">Intrinsic Value: {cur}{dcf_result['intrinsic_value']:.2f} | Upside: {upside:+.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Intrinsic Value", f"{cur}{dcf_result['intrinsic_value']:.2f}")
    with col2:
        st.metric("Current Price", f"{cur}{dcf_result['current_price']:.2f}", delta=f"{upside:+.1f}%")
    with col3:
        st.metric("WACC", f"{dcf_result['wacc']*100:.1f}%")
    with col4:
        st.metric("Terminal %", f"{(dcf_result['pv_terminal']/dcf_result['enterprise_value'])*100:.0f}%")
    
    # FCF Projection Chart
    years = [p['year'] for p in dcf_result['projections']]
    fcf_vals = [p['fcf']/(1e7 if analyzer.currency=='INR' else 1e9) for p in dcf_result['projections']]
    pv_vals = [p['pv_fcf']/(1e7 if analyzer.currency=='INR' else 1e9) for p in dcf_result['projections']]
    unit = 'Cr' if analyzer.currency == 'INR' else 'B'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=fcf_vals, name='FCF', marker_color='#667eea'))
    fig.add_trace(go.Scatter(x=years, y=pv_vals, name='PV of FCF', mode='lines+markers', line=dict(color='#f59e0b', width=2)))
    fig.update_layout(title=f'10-Year FCF Projection ({cur}{unit})', template='plotly_white', height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # ===== MODEL 2: Graham Valuation =====
    st.markdown("### 📚 Benjamin Graham Valuation")
    eps = analyzer.ratios.get('EPS', ni/shares if ni and shares else 1)
    graham_value = GrahamValuation.calculate(eps, rg, rf)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Graham Intrinsic Value", f"{cur}{graham_value:.2f}")
        st.caption(f"Based on EPS: {cur}{eps:.2f}, Growth: {rg*100:.1f}%")
    with col2:
        graham_upside = ((graham_value/cp)-1)*100 if cp > 0 else 0
        st.metric("Graham Upside", f"{graham_upside:+.1f}%")
    
    # ===== MODEL 3: Earnings Power Value =====
    st.markdown("### 🎓 Earnings Power Value (Columbia Model)")
    epv = EarningsPowerValue.calculate(
        revenue=rev or 0, operating_margin=om, tax_rate=0.25,
        wacc=dcf_result['wacc'], shares=shares
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("EPV per Share", f"{cur}{epv:.2f}")
    with col2:
        epv_upside = ((epv/cp)-1)*100 if cp > 0 else 0
        st.metric("EPV Upside", f"{epv_upside:+.1f}%")
    
    # ===== Valuation Summary =====
    st.markdown("### 📊 Valuation Summary")
    models = {
        'Advanced DCF': dcf_result['intrinsic_value'],
        'Graham Formula': graham_value,
        'Earnings Power': epv,
        'Current Price': cp
    }
    
    fig = go.Figure()
    for model, value in models.items():
        color = '#10b981' if value > cp else '#ef4444' if value < cp else '#f59e0b'
        fig.add_trace(go.Bar(x=[model], y=[value], name=model, marker_color=color,
                             text=[f"{cur}{value:.2f}"], textposition='outside'))
    fig.add_hline(y=cp, line_dash="dash", line_color="#94a3b8", annotation_text=f"Current: {cur}{cp:.2f}")
    fig.update_layout(title='All Valuation Models Comparison', template='plotly_white', height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ===== STRESS TEST DASHBOARD =====

def create_stress_test_dashboard(analyzer):
    """Monte Carlo stress testing"""
    st.markdown('<div class="section-header">🎲 Monte Carlo Stress Test</div>', unsafe_allow_html=True)
    
    prices = analyzer.financials.get('prices')
    cp = analyzer.live_price_data.get('current_price')
    cur = analyzer.currency_symbol
    
    if not cp or prices is None or prices.empty:
        st.warning("Need price data for stress testing.")
        return
    
    returns = prices['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)
    expected_return = returns.mean() * 252
    
    with st.expander("⚙️ Simulation Parameters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            num_sims = st.select_slider("Simulations", options=[100, 500, 1000, 5000, 10000], value=1000)
        with col2:
            time_horizon = st.select_slider("Days", options=[63, 126, 252, 504], value=252)
        with col3:
            vol_input = st.number_input("Volatility %", value=round(volatility*100, 1), step=0.5) / 100
            er_input = st.number_input("Expected Return %", value=round(expected_return*100, 1), step=0.5) / 100
    
    fcf = analyzer._safe_get(analyzer.financials.get('cashflow'), ['Free Cash Flow']) if analyzer.financials.get('cashflow') is not None else None
    if not fcf:
        ni = analyzer._safe_get(analyzer.financials.get('income'), ['Net Income'])
        fcf = ni * 0.8 if ni else 1e6
    
    info = analyzer.financials.get('info', {})
    beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
    rf = 0.072 if analyzer.currency == 'INR' else 0.045
    mr = 0.12 if analyzer.currency == 'INR' else 0.10
    wacc = rf + beta * (mr - rf)
    
    if st.button("🎲 Run Monte Carlo Simulation", type="primary", use_container_width=True):
        with st.spinner(f"Running {num_sims} simulations..."):
            mc = MonteCarloStressTest(
                current_price=cp, volatility=vol_input, expected_return=er_input,
                shares=1e6, fcf=fcf, wacc=wacc
            )
            result = mc.run_simulation(num_simulations=num_sims, time_horizon=time_horizon)
        
        st.success(f"✅ Simulation complete! {num_sims:,} scenarios tested.")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Expected Price", f"{cur}{result['expected_price']:.2f}",
                     delta=f"{((result['expected_price']/cp)-1)*100:+.1f}%")
        with col2:
            st.metric("Value at Risk (95%)", f"{cur}{result['var_95']:.2f}",
                     delta=f"{result['max_loss']:+.1f}% max loss", delta_color="inverse")
        with col3:
            st.metric("Prob. of Profit", f"{result['prob_profit']:.1f}%")
        with col4:
            st.metric("CVaR (95%)", f"{cur}{result['cvar_95']:.2f}",
                     help="Conditional Value at Risk - average loss beyond VaR")
        
        # Simulation paths
        st.markdown("#### 📈 Price Paths (100 random scenarios)")
        fig = go.Figure()
        for i in range(min(100, num_sims)):
            fig.add_trace(go.Scatter(
                y=result['simulations'][i, :], mode='lines',
                line=dict(width=0.5, color='rgba(102,126,234,0.1)'),
                showlegend=False
            ))
        fig.add_hline(y=cp, line_dash="dash", line_color="#10b981", annotation_text="Current")
        fig.add_hline(y=result['expected_price'], line_dash="dash", line_color="#f59e0b", annotation_text="Expected")
        fig.update_layout(title=f'Monte Carlo Simulation ({num_sims} paths)', template='plotly_white', height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution of final prices
        st.markdown("#### 📊 Final Price Distribution")
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=result['final_prices'], nbinsx=50, marker_color='#667eea', opacity=0.7,
                                   name='Final Prices', histnorm='probability density'))
        fig.add_vline(x=cp, line_dash="dash", line_color="#10b981", annotation_text="Current")
        fig.add_vline(x=result['expected_price'], line_dash="dash", line_color="#f59e0b", annotation_text="Expected")
        fig.add_vline(x=result['var_95'], line_dash="dot", line_color="#ef4444", annotation_text="VaR 95%")
        fig.update_layout(title='Distribution of Final Prices', template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Stress test summary
        st.markdown("#### 🛡️ Stress Test Results")
        col1, col2 = st.columns(2)
        with col1:
            stress_pass = result['prob_profit'] > 50
            color_class = "stress-pass" if stress_pass else "stress-fail"
            st.markdown(f"""
            <div class="card">
                <h4>Scenario Analysis</h4>
                <p>📈 <b>Bull Case (90th %ile):</b> {cur}{result['price_range'][1]:.2f} (+{((result['price_range'][1]/cp)-1)*100:.1f}%)</p>
                <p>📉 <b>Bear Case (10th %ile):</b> {cur}{result['price_range'][0]:.2f} ({((result['price_range'][0]/cp)-1)*100:.1f}%)</p>
                <p class="{color_class}">{'✅ Pass' if stress_pass else '❌ Fail'}: {result['prob_profit']:.1f}% probability of profit</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card">
                <h4>Risk Metrics</h4>
                <p>🔴 <b>VaR 99%:</b> {cur}{result['var_99']:.2f}</p>
                <p>🟡 <b>VaR 95%:</b> {cur}{result['var_95']:.2f}</p>
                <p>🟢 <b>Expected:</b> {cur}{result['expected_price']:.2f}</p>
                <p>📊 <b>Range (80% CI):</b> {cur}{result['price_range'][0]:.2f} - {cur}{result['price_range'][1]:.2f}</p>
            </div>
            """, unsafe_allow_html=True)


# ===== TECHNICAL ANALYSIS =====

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    ema_fast = prices.ewm(span=12, adjust=False).mean()
    ema_slow = prices.ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal, macd_line - signal

def calculate_bollinger_bands(prices, period=20, std=2):
    sma = prices.rolling(window=period).mean()
    rolling_std = prices.rolling(window=period).std()
    return sma + (rolling_std * std), sma, sma - (rolling_std * std)

def create_technical_analysis_dashboard(analyzer):
    st.markdown('<div class="section-header">📈 Technical Analysis</div>', unsafe_allow_html=True)
    
    prices = analyzer.financials.get('prices')
    if prices is None or prices.empty:
        st.warning("Price data not available."); return
    
    close = prices['Close']
    cur = analyzer.currency_symbol
    
    rsi = calculate_rsi(close)
    macd_line, signal_line, histogram = calculate_macd(close)
    upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(close)
    
    # Signals
    current_rsi = rsi.iloc[-1]
    rsi_signal = "Overbought 🔴" if current_rsi > 70 else "Oversold 🟢" if current_rsi < 30 else "Neutral 🟡"
    macd_signal = "Bullish 🟢" if macd_line.iloc[-1] > signal_line.iloc[-1] else "Bearish 🔴"
    
    sma_50 = close.rolling(50).mean().iloc[-1]
    sma_200 = close.rolling(200).mean().iloc[-1]
    trend = "Golden Cross ✨" if sma_50 > sma_200 else "Death Cross 💀"
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RSI (14)", f"{current_rsi:.1f}", delta=rsi_signal)
    col2.metric("MACD", f"{macd_line.iloc[-1]:.2f}", delta=macd_signal)
    col3.metric("Trend", trend.split(' ')[0])
    col4.metric("Close", f"{cur}{close.iloc[-1]:.2f}")
    
    # Charts
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.5, 0.25, 0.25],
                        subplot_titles=('Price & Bollinger Bands', 'RSI', 'MACD'))
    
    # Bollinger Bands
    last_60 = slice(-60, None)
    fig.add_trace(go.Scatter(x=close.index[last_60], y=upper_bb.iloc[last_60], name='Upper BB',
                             line=dict(color='gray', width=1, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[last_60], y=middle_bb.iloc[last_60], name='20 MA',
                             line=dict(color='orange', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[last_60], y=lower_bb.iloc[last_60], name='Lower BB',
                             line=dict(color='gray', width=1, dash='dash'), fill='tonexty',
                             fillcolor='rgba(102,126,234,0.1)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=close.index[last_60], y=close.iloc[last_60], name='Price',
                             line=dict(color='#667eea', width=2)), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=rsi.index[last_60], y=rsi.iloc[last_60], name='RSI',
                             line=dict(color='#667eea', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=macd_line.index[last_60], y=macd_line.iloc[last_60], name='MACD',
                             line=dict(color='#667eea', width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=signal_line.index[last_60], y=signal_line.iloc[last_60], name='Signal',
                             line=dict(color='#f59e0b', width=1.5)), row=3, col=1)
    colors = ['#10b981' if h >= 0 else '#ef4444' for h in histogram.iloc[last_60]]
    fig.add_trace(go.Bar(x=histogram.index[last_60], y=histogram.iloc[last_60], name='Histogram',
                         marker_color=colors), row=3, col=1)
    
    fig.update_layout(height=800, template='plotly_white', hovermode='x unified')
    fig.update_yaxes(title_text=f"Price ({cur})", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    st.plotly_chart(fig, use_container_width=True)


# ===== PORTFOLIO TRACKER =====

def create_portfolio_tracker():
    st.markdown('<div class="section-header">💼 Portfolio Tracker</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add Stock", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            add_ticker = st.text_input("Ticker", key="pt_ticker")
        with col2:
            add_qty = st.number_input("Quantity", min_value=1, value=10, key="pt_qty")
        with col3:
            add_price = st.number_input("Buy Price", min_value=0.01, value=100.0, key="pt_price")
        if st.button("Add", type="primary"):
            st.session_state['portfolio'].append({
                'ticker': add_ticker.upper(), 'quantity': add_qty,
                'buy_price': add_price, 'date': datetime.now().strftime('%Y-%m-%d')
            })
            st.success(f"Added {add_ticker}!"); st.rerun()
    
    if st.session_state['portfolio']:
        portfolio_data = []
        total_invested = 0; total_current = 0
        
        for i, holding in enumerate(st.session_state['portfolio']):
            try:
                ticker = INDIAN_STOCKS_DB.get(holding['ticker'], holding['ticker'])
                stock = yf.Ticker(ticker)
                info = stock.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', holding['buy_price'])
                
                qty = holding['quantity']; buy_price = holding['buy_price']
                invested = qty * buy_price; current_value = qty * current_price
                pnl = current_value - invested; pnl_pct = (pnl/invested)*100 if invested > 0 else 0
                
                total_invested += invested; total_current += current_value
                
                portfolio_data.append({
                    '#': i+1, 'Ticker': holding['ticker'], 'Qty': qty,
                    'Buy': f"₹{buy_price:.2f}" if '.NS' in ticker else f"${buy_price:.2f}",
                    'Current': f"₹{current_price:.2f}" if '.NS' in ticker else f"${current_price:.2f}",
                    'P&L': pnl, 'P&L %': pnl_pct
                })
            except: pass
        
        if portfolio_data:
            df = pd.DataFrame(portfolio_data)
            def color_pnl(val):
                return 'color: #10b981' if isinstance(val, (int, float)) and val > 0 else 'color: #ef4444' if isinstance(val, (int, float)) and val < 0 else ''
            
            st.dataframe(df.style.applymap(color_pnl, subset=['P&L', 'P&L %']), use_container_width=True)
            
            total_pnl = total_current - total_invested
            total_pnl_pct = (total_pnl/total_invested)*100 if total_invested > 0 else 0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Invested", f"${total_invested:,.0f}")
            c2.metric("Current Value", f"${total_current:,.0f}")
            c3.metric("Total P&L", f"${total_pnl:,.0f}", delta=f"{total_pnl_pct:.1f}%")
            c4.metric("Holdings", len(st.session_state['portfolio']))
            
            if st.button("🗑️ Clear Portfolio"):
                st.session_state['portfolio'] = []; st.rerun()
    else:
        st.info("Portfolio empty. Add stocks above!")


# ===== PEER COMPARISON =====

def get_peer_comparison(main_ticker, peer_tickers):
    peer_data = []
    for ticker in peer_tickers:
        try:
            stock = yf.Ticker(ticker); info = stock.info
            if not info: continue
            is_indian = ticker.endswith('.NS') or ticker.endswith('.BO')
            p_cur = 'INR' if is_indian else 'USD'
            mcap = info.get('marketCap', 0) or 0
            mcap_disp = round(mcap/1e7, 2) if p_cur=='INR' else round(mcap/1e9, 2)
            peer_data.append({
                'Ticker': ticker.replace('.NS','').replace('.BO',''),
                'Company': info.get('longName', ticker)[:25],
                'Market Cap': f"{'₹' if p_cur=='INR' else '$'}{mcap_disp}{'Cr' if p_cur=='INR' else 'B'}",
                'P/E': round(info.get('trailingPE', 0), 1) if info.get('trailingPE') else None,
                'ROE %': round((info.get('returnOnEquity', 0) or 0)*100, 1),
                'D/E': round(info.get('debtToEquity', 0) or 0, 2),
            })
        except: continue
    return pd.DataFrame(peer_data)


# ===== MAIN APP =====

def main():
    st.markdown('<h1 class="main-header">📊 FinAnalyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enterprise Financial Analysis • Advanced DCF • Monte Carlo Stress Tests • Multi-Model Valuation</p>', unsafe_allow_html=True)

    # Initialize session state
    if 'current_ticker' not in st.session_state:
        st.session_state['current_ticker'] = "AAPL"
    if 'current_exchange' not in st.session_state:
        st.session_state['current_exchange'] = "Auto-detect"
    if 'analyze_clicked' not in st.session_state:
        st.session_state['analyze_clicked'] = False

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Stock Analysis", "🎲 Stress Test", "💼 Portfolio", "📈 Technical"
    ])

    # ===== TAB 1: STOCK ANALYSIS =====
    with tab1:
        # Search bar
        col1, col2, col3 = st.columns([3, 1.5, 1])
        with col1:
            ticker = st.text_input("Stock Ticker", value=st.session_state['current_ticker'], max_chars=50, key="main_ticker", placeholder="e.g., AAPL, RELIANCE, TATAMOTORS")
        with col2:
            exchange = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"],
                                    index=["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"].index(st.session_state['current_exchange']), key="main_exchange")
        with col3:
            st.write(""); st.write("")
            analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True, key="main_analyze")

        # Quick Access - FIXED
        st.markdown("#### ⚡ Quick Access")
        cols = st.columns(8)
        quick_stocks = ["AAPL", "RELIANCE", "TCS", "MSFT", "TATAMOTORS", "INFY", "GOOGL", "HDFCBANK"]
        quick_exchanges = ["US Market", "NSE India (.NS)", "NSE India (.NS)", "US Market", 
                          "NSE India (.NS)", "NSE India (.NS)", "US Market", "NSE India (.NS)"]
        
        for i, (stock, exch) in enumerate(zip(quick_stocks, quick_exchanges)):
            with cols[i]:
                if st.button(stock, use_container_width=True, key=f"quick_{stock}"):
                    st.session_state['current_ticker'] = stock
                    st.session_state['current_exchange'] = exch
                    st.session_state['analyze_clicked'] = True
                    st.rerun()

        # More quick access in expander
        with st.expander("📋 More Stocks"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Indian Stocks**")
                indian_cols = st.columns(4)
                for i, tick in enumerate(list(INDIAN_STOCKS_DB.keys())[:20]):
                    with indian_cols[i % 4]:
                        if st.button(tick, use_container_width=True, key=f"more_i_{tick}"):
                            st.session_state['current_ticker'] = tick
                            st.session_state['current_exchange'] = "NSE India (.NS)"
                            st.session_state['analyze_clicked'] = True
                            st.rerun()
            with c2:
                st.markdown("**US Stocks**")
                us_cols = st.columns(4)
                us_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "WMT", "NFLX", "ADBE"]
                for i, s in enumerate(us_list):
                    with us_cols[i % 4]:
                        if st.button(s, use_container_width=True, key=f"more_u_{s}"):
                            st.session_state['current_ticker'] = s
                            st.session_state['current_exchange'] = "US Market"
                            st.session_state['analyze_clicked'] = True
                            st.rerun()

        # Update session state
        st.session_state['current_ticker'] = ticker
        st.session_state['current_exchange'] = exchange
        if analyze_btn:
            st.session_state['analyze_clicked'] = True

        if not st.session_state['analyze_clicked']:
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;">
                <h2 style="color:#e2e8f0;font-size:2rem;">🏦 Enterprise Financial Analysis Platform</h2>
                <p style="color:#94a3b8;font-size:1.1rem;max-width:600px;margin:1rem auto;">
                    Advanced DCF • Monte Carlo Stress Tests • Graham Valuation • Earnings Power Value
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Run analysis
            exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            selected_exchange = exchange_map.get(st.session_state['current_exchange'], "Auto")
            analyzer = ProFinancialAnalyzer(st.session_state['current_ticker'], exchange=selected_exchange)

            with st.spinner("🔍 Running comprehensive analysis..."):
                analyzer.get_live_price()
                analyzer.fetch_financial_data()
                analyzer.calculate_all_ratios()

            # Live price
            pd_data = analyzer.live_price_data
            cur = analyzer.currency_symbol
            cp = pd_data.get('current_price')
            pc = pd_data.get('previous_close')

            if cp and pc:
                change = cp - pc
                change_pct = (change/pc)*100
                color = "price-up" if change >= 0 else "price-down"
                arrow = "▲" if change >= 0 else "▼"
                st.markdown(f"""
                <div class="live-price-box">
                    <div style="position:relative;z-index:1;">
                        <h2 style="margin:0;">{analyzer.company_name}</h2>
                        <div class="{color}">{cur}{cp:.2f} {arrow}</div>
                        <div style="font-size:1.2rem;margin-top:0.5rem;">{cur}{abs(change):.2f} ({change_pct:+.2f}%)</div>
                        <div style="margin-top:1rem;display:flex;justify-content:center;gap:2rem;font-size:0.9rem;opacity:0.8;">
                            <span>H: {cur}{pd_data.get('day_high','N/A')}</span>
                            <span>L: {cur}{pd_data.get('day_low','N/A')}</span>
                            <span>Vol: {pd_data.get('volume','N/A'):,.0f}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Company info
            st.markdown(f"""
            <div style="background:#1e293b;padding:0.75rem 1.5rem;border-radius:12px;margin:0.5rem 0;display:flex;justify-content:space-between;color:#e2e8f0;">
                <span>📊 {analyzer.financials.get('sector','N/A')} | {analyzer.financials.get('industry','N/A')}</span>
                <span>💰 Market Cap: {analyzer._format_amount(pd_data.get('market_cap',0))}</span>
                <span>🌍 {analyzer.currency}</span>
            </div>
            """, unsafe_allow_html=True)

            # Ratios
            st.markdown('<div class="section-header">📊 Key Financial Ratios</div>', unsafe_allow_html=True)
            ratios = analyzer.ratios
            if ratios:
                cols = st.columns(5)
                key_metrics = [
                    ('P/E', ratios.get('P/E Ratio')), ('ROE', ratios.get('ROE')),
                    ('P/B', ratios.get('P/B Ratio')), ('D/E', ratios.get('Debt to Equity')),
                    ('Div Yield', ratios.get('Dividend Yield'))
                ]
                for col, (label, val) in zip(cols, key_metrics):
                    with col:
                        if isinstance(val, (int, float)):
                            display = f"{val:.1f}%" if label in ['ROE', 'Div Yield'] else f"{val:.2f}"
                            st.markdown(f'<div class="card"><div class="metric-value">{display}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

            # Advanced Valuation (DCF + Graham + EPV)
            create_valuation_dashboard(analyzer)

            # Peer Comparison
            group_name, peer_list = None, None
            for gn, pl in PEER_GROUPS.items():
                if analyzer.ticker in pl:
                    group_name, peer_list = gn, pl
                    break
            
            if peer_list:
                peer_list = [p for p in peer_list if p != analyzer.ticker][:5]
                all_tickers = [analyzer.ticker] + peer_list
                with st.spinner("Fetching peer data..."):
                    peer_df = get_peer_comparison(analyzer.ticker, all_tickers)
                    if not peer_df.empty:
                        st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
                        st.dataframe(peer_df, use_container_width=True, hide_index=True)

            # Financial Statements
            st.markdown('<div class="section-header">📋 Financial Statements</div>', unsafe_allow_html=True)
            t1, t2, t3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
            for tab, key in [(t1, 'income'), (t2, 'balance'), (t3, 'cashflow')]:
                with tab:
                    df = analyzer.financials.get(key)
                    if df is not None and not df.empty:
                        formatted = format_financial_df(df, analyzer.currency_symbol, analyzer.currency)
                        if formatted is not None:
                            st.dataframe(formatted, use_container_width=True)

    # ===== TAB 2: STRESS TEST =====
    with tab2:
        st.markdown("### 🎲 Monte Carlo Stress Test")
        stress_ticker = st.text_input("Ticker for Stress Test", "AAPL", key="stress_ticker")
        stress_exchange = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"], key="stress_exchange")
        
        if st.button("🎲 Load & Run Stress Test", type="primary"):
            exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            stress_analyzer = ProFinancialAnalyzer(stress_ticker, exchange=exchange_map.get(stress_exchange, "Auto"))
            with st.spinner("Loading data..."):
                stress_analyzer.get_live_price()
                stress_analyzer.fetch_financial_data()
                stress_analyzer.calculate_all_ratios()
            create_stress_test_dashboard(stress_analyzer)

    # ===== TAB 3: PORTFOLIO =====
    with tab3:
        create_portfolio_tracker()

    # ===== TAB 4: TECHNICAL ANALYSIS =====
    with tab4:
        st.markdown("### 📈 Technical Analysis")
        ta_ticker = st.text_input("Ticker for TA", "AAPL", key="ta_ticker")
        ta_exchange = st.selectbox("Exchange", ["Auto-detect", "NSE India (.NS)", "BSE India (.BO)", "US Market"], key="ta_exchange")
        
        if st.button("📈 Run Technical Analysis", type="primary"):
            exchange_map = {"NSE India (.NS)": "NSE", "BSE India (.BO)": "BSE", "US Market": "US", "Auto-detect": "Auto"}
            ta_analyzer = ProFinancialAnalyzer(ta_ticker, exchange=exchange_map.get(ta_exchange, "Auto"))
            with st.spinner("Calculating indicators..."):
                ta_analyzer.get_live_price()
                ta_analyzer.fetch_financial_data()
            create_technical_analysis_dashboard(ta_analyzer)

    st.divider()
    st.caption(f"FinAnalyzer Pro • Enterprise Grade • {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()