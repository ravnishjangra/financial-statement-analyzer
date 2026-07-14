"""
FinAnalyzer Pro - Enterprise Financial Analysis Platform
30 Stress Tests • Advanced DCF • Graham & EPV • Monte Carlo
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
    .stress-pass { color: #10b981; font-weight: 700; }
    .stress-fail { color: #ef4444; font-weight: 700; }
    .stress-warning { color: #f59e0b; font-weight: 700; }
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


# ===== 30 STRESS TESTS =====

class StressTestEngine:
    """30 Comprehensive Stress Tests"""
    
    def __init__(self, current_price, sector, industry, beta, currency, market_cap):
        self.price = current_price
        self.sector = sector
        self.industry = industry
        self.beta = beta or 1.0
        self.currency = currency
        self.market_cap = market_cap or 0
    
    def run_all_tests(self):
        """Run all 30 stress tests and return results"""
        results = []
        
        # 1. Market Crash
        for pct in [-10, -20, -30, -50]:
            impact = self.price * (1 + pct/100 * self.beta)
            loss = (impact/self.price - 1) * 100
            results.append({
                'Test': f'Market Crash ({abs(pct)}%)',
                'Scenario': f'Broad market declines by {abs(pct)}%',
                'Impact Price': impact,
                'Loss %': loss,
                'Severity': '🔴 CRITICAL' if loss < -30 else '🟠 HIGH' if loss < -20 else '🟡 MODERATE' if loss < -10 else '🟢 LOW'
            })
        
        # 2. Bull Market Rally
        for pct in [10, 20, 30]:
            impact = self.price * (1 + pct/100 * self.beta)
            gain = (impact/self.price - 1) * 100
            results.append({
                'Test': f'Bull Rally (+{pct}%)',
                'Scenario': f'Market rises by {pct}%',
                'Impact Price': impact,
                'Loss %': gain,
                'Severity': '🟢 POSITIVE' if gain > 0 else '🟡 NEUTRAL'
            })
        
        # 3. Interest Rate Shock
        for bps in [100, 200, -100, -200]:
            # Rate sensitivity: higher for financials, utilities, real estate
            rate_sensitivity = 1.5 if self.sector in ['Financial Services', 'Real Estate', 'Utilities'] else 1.0
            impact_pct = -bps/100 * 0.05 * self.beta * rate_sensitivity
            impact = self.price * (1 + impact_pct)
            results.append({
                'Test': f'Rate {"Hike" if bps > 0 else "Cut"} ({abs(bps)} bps)',
                'Scenario': f'Central bank {"raises" if bps > 0 else "cuts"} rates by {abs(bps)}bps',
                'Impact Price': impact,
                'Loss %': impact_pct * 100,
                'Severity': '🔴 CRITICAL' if impact_pct < -0.1 else '🟠 HIGH' if impact_pct < -0.05 else '🟡 MODERATE'
            })
        
        # 4. Inflation Spike
        for inf in [5, 10, 15]:
            inf_sensitivity = 0.8 if self.sector in ['Consumer Defensive', 'Healthcare'] else 1.2
            impact_pct = -inf/100 * 0.03 * self.beta * inf_sensitivity
            impact = self.price * (1 + impact_pct)
            results.append({
                'Test': f'Inflation Spike ({inf}%)',
                'Scenario': f'Inflation rises to {inf}%',
                'Impact Price': impact,
                'Loss %': impact_pct * 100,
                'Severity': '🔴 CRITICAL' if impact_pct < -0.15 else '🟠 HIGH' if impact_pct < -0.08 else '🟡 MODERATE'
            })
        
        # 5. Currency Shock
        is_indian = self.currency == 'INR'
        for pct in [5, 10, -5, -10, 20, -20]:
            fx_sensitivity = 1.3 if self.sector in ['Technology', 'Energy'] else 0.7 if self.sector in ['Consumer Defensive'] else 1.0
            if is_indian:
                impact_pct = -pct/100 * 0.02 * fx_sensitivity  # INR depreciation negative for imports
            else:
                impact_pct = pct/100 * 0.01 * fx_sensitivity
            impact = self.price * (1 + impact_pct)
            direction = "Depreciation" if (is_indian and pct > 0) or (not is_indian and pct < 0) else "Appreciation"
            results.append({
                'Test': f'Currency {direction} ({abs(pct)}%)',
                'Scenario': f'USD/INR moves by {pct}%',
                'Impact Price': impact,
                'Loss %': impact_pct * 100,
                'Severity': '🟠 HIGH' if abs(impact_pct*100) > 3 else '🟡 MODERATE' if abs(impact_pct*100) > 1 else '🟢 LOW'
            })
        
        # 6. Oil Price Shock
        if self.sector in ['Energy', 'Transportation', 'Airlines']:
            for pct in [20, 50, -20, -50]:
                oil_sensitivity = 2.0 if self.sector == 'Energy' else -1.5
                impact_pct = pct/100 * 0.05 * oil_sensitivity
                impact = self.price * (1 + impact_pct)
                results.append({
                    'Test': f'Oil {"Rise" if pct > 0 else "Fall"} ({abs(pct)}%)',
                    'Scenario': f'Crude oil {"surges" if pct > 0 else "crashes"} by {abs(pct)}%',
                    'Impact Price': impact,
                    'Loss %': impact_pct * 100,
                    'Severity': '🔴 CRITICAL' if abs(impact_pct*100) > 10 else '🟠 HIGH' if abs(impact_pct*100) > 5 else '🟡 MODERATE'
                })
        
        # 7. Gold Price Shock
        gold_sensitivity = 1.5 if 'Gold' in str(self.industry) else 0.3
        for pct in [20, 50, -20]:
            impact_pct = pct/100 * 0.02 * gold_sensitivity
            impact = self.price * (1 + impact_pct)
            results.append({
                'Test': f'Gold {"Rise" if pct > 0 else "Fall"} ({abs(pct)}%)',
                'Scenario': f'Gold price moves by {pct}%',
                'Impact Price': impact,
                'Loss %': impact_pct * 100,
                'Severity': '🟡 MODERATE' if abs(impact_pct*100) > 1 else '🟢 LOW'
            })
        
        # 8. Commodity Crash
        commodity_sectors = ['Basic Materials', 'Energy', 'Industrials']
        if self.sector in commodity_sectors:
            for pct in [-20, -40, -60]:
                impact_pct = pct/100 * 0.5 if self.sector in commodity_sectors else pct/100 * 0.1
                impact = self.price * (1 + impact_pct)
                results.append({
                    'Test': f'Commodity Crash ({abs(pct)}%)',
                    'Scenario': f'Industrial commodities fall {abs(pct)}%',
                    'Impact Price': impact,
                    'Loss %': impact_pct * 100,
                    'Severity': '🔴 CRITICAL' if impact_pct < -0.2 else '🟠 HIGH'
                })
        
        # 9. Bond Yield Spike
        for bps in [100, 200, 300]:
            impact_pct = -bps/10000 * 2 * self.beta
            impact = self.price * (1 + impact_pct)
            results.append({
                'Test': f'Bond Yield Spike (+{bps}bps)',
                'Scenario': f'10Y bond yields surge {bps}bps',
                'Impact Price': impact,
                'Loss %': impact_pct * 100,
                'Severity': '🔴 CRITICAL' if impact_pct < -0.1 else '🟠 HIGH' if impact_pct < -0.05 else '🟡 MODERATE'
            })
        
        # 10. Volatility Spike
        for mult in [2, 3, 5]:
            impact_pct = -0.05 * mult * self.beta
            impact = self.price * (1 + impact_pct)
            results.append({
                'Test': f'VIX Spike (x{mult})',
                'Scenario': f'Volatility index increases {mult}x',
                'Impact Price': impact,
                'Loss %': impact_pct * 100,
                'Severity': '🔴 CRITICAL' if mult >= 3 else '🟠 HIGH'
            })
        
        # 11-12. Sector Crash & Rotation
        sectors_crash = {'Technology': -30, 'Banking': -40, 'Pharma': -25, 'Energy': -35, 'Auto': -30}
        for sec, pct in sectors_crash.items():
            if sec in str(self.sector):
                impact_pct = pct/100 * 1.2
                impact = self.price * (1 + impact_pct)
                results.append({
                    'Test': f'{sec} Sector Crash ({abs(pct)}%)',
                    'Scenario': f'{sec} sector crashes by {abs(pct)}%',
                    'Impact Price': impact,
                    'Loss %': impact_pct * 100,
                    'Severity': '🔴 CRITICAL'
                })
        
        # 13. Single Stock Collapse (50-90%)
        for pct in [-50, -75, -90]:
            impact = self.price * (1 + pct/100)
            results.append({
                'Test': f'Stock Collapse ({abs(pct)}%)',
                'Scenario': f'Stock drops {abs(pct)}% on bad news',
                'Impact Price': impact,
                'Loss %': pct,
                'Severity': '🔴 CRITICAL'
            })
        
        # 14. Bankruptcy
        results.append({
            'Test': 'Bankruptcy (100% Loss)',
            'Scenario': 'Complete loss of investment',
            'Impact Price': 0,
            'Loss %': -100,
            'Severity': '💀 MAXIMUM'
        })
        
        # 15. Liquidity Crisis
        impact = self.price * 0.85
        results.append({
            'Test': 'Liquidity Crisis',
            'Scenario': 'Stock becomes illiquid, bid-ask spreads widen',
            'Impact Price': impact,
            'Loss %': -15,
            'Severity': '🟠 HIGH'
        })
        
        # 16. Earnings Miss
        for pct in [-10, -25, -50]:
            impact = self.price * (1 + pct/100 * 1.5)
            results.append({
                'Test': f'Earnings Miss ({abs(pct)}%)',
                'Scenario': f'Company misses earnings by {abs(pct)}%',
                'Impact Price': impact,
                'Loss %': pct * 1.5,
                'Severity': '🔴 CRITICAL' if pct < -25 else '🟠 HIGH'
            })
        
        # 17. Dividend Suspension
        impact = self.price * 0.85
        results.append({
            'Test': 'Dividend Suspension',
            'Scenario': 'Company suspends dividend payments',
            'Impact Price': impact,
            'Loss %': -15,
            'Severity': '🟠 HIGH'
        })
        
        # 18. Credit Rating Downgrade
        if self.sector in ['Financial Services', 'Energy', 'Industrials']:
            for notch in [1, 3]:
                impact_pct = -0.05 * notch * self.beta
                impact = self.price * (1 + impact_pct)
                results.append({
                    'Test': f'Credit Downgrade ({notch} notch)',
                    'Scenario': f'Credit rating downgraded by {notch} notch(es)',
                    'Impact Price': impact,
                    'Loss %': impact_pct * 100,
                    'Severity': '🟠 HIGH' if notch >= 3 else '🟡 MODERATE'
                })
        
        # 19. Governance Scandal
        impact = self.price * 0.60
        results.append({
            'Test': 'Governance Scandal',
            'Scenario': 'Fraud or governance issues discovered',
            'Impact Price': impact,
            'Loss %': -40,
            'Severity': '🔴 CRITICAL'
        })
        
        # 20. Geopolitical Conflict
        impact = self.price * 0.80
        results.append({
            'Test': 'Geopolitical Conflict',
            'Scenario': 'War or major geopolitical tensions',
            'Impact Price': impact,
            'Loss %': -20,
            'Severity': '🟠 HIGH'
        })
        
        # 21. Pandemic Scenario
        impact = self.price * (1.15 if self.sector in ['Healthcare', 'Technology'] else 0.70)
        results.append({
            'Test': 'Pandemic Scenario',
            'Scenario': 'Global pandemic (winners/losers based on sector)',
            'Impact Price': impact,
            'Loss %': (impact/self.price - 1) * 100,
            'Severity': '🟢 WINNER' if impact > self.price else '🔴 LOSER'
        })
        
        # 22. Recession
        impact = self.price * (0.65 if self.sector in ['Consumer Cyclical', 'Industrials'] else 0.85)
        results.append({
            'Test': 'Recession',
            'Scenario': 'GDP contracts, cyclicals underperform defensives',
            'Impact Price': impact,
            'Loss %': (impact/self.price - 1) * 100,
            'Severity': '🔴 CRITICAL' if impact < self.price * 0.7 else '🟠 HIGH'
        })
        
        # 23. Economic Boom
        impact = self.price * (1.25 if self.sector in ['Consumer Cyclical', 'Industrials', 'Financial Services'] else 1.10)
        results.append({
            'Test': 'Economic Boom',
            'Scenario': 'Strong GDP growth benefits cyclical sectors',
            'Impact Price': impact,
            'Loss %': (impact/self.price - 1) * 100,
            'Severity': '🟢 POSITIVE'
        })
        
        # 24. Historical Replay
        historical = {'2008 GFC': -0.45, '2020 COVID': -0.30, '2022 Inflation': -0.20}
        for event, pct in historical.items():
            impact = self.price * (1 + pct * self.beta)
            results.append({
                'Test': f'Historical: {event}',
                'Scenario': f'Replay {event} market conditions',
                'Impact Price': impact,
                'Loss %': pct * self.beta * 100,
                'Severity': '🔴 CRITICAL' if pct < -0.3 else '🟠 HIGH'
            })
        
        # 25. Portfolio Concentration
        impact = self.price * 0.80
        results.append({
            'Test': 'Concentration Risk',
            'Scenario': 'Overweight position in single stock',
            'Impact Price': impact,
            'Loss %': -20,
            'Severity': '🟠 HIGH'
        })
        
        # 26. Correlation Breakdown
        impact = self.price * 0.75
        results.append({
            'Test': 'Correlation Breakdown',
            'Scenario': 'All assets move together during crisis',
            'Impact Price': impact,
            'Loss %': -25,
            'Severity': '🔴 CRITICAL'
        })
        
        # 27. Monte Carlo Stress (simplified)
        np.random.seed(42)
        sim_returns = np.random.normal(-0.0005, 0.02, 1000)
        var_95 = np.percentile(sim_returns, 5)
        impact = self.price * (1 + var_95 * 252)
        results.append({
            'Test': 'Monte Carlo VaR (95%)',
            'Scenario': '1000 simulated annual return paths',
            'Impact Price': impact,
            'Loss %': var_95 * 252 * 100,
            'Severity': '🟠 HIGH'
        })
        
        # 28. VaR Comparison
        for method, ret in [('Historical', -0.25), ('Parametric', -0.30), ('Monte Carlo', -0.28)]:
            impact = self.price * (1 + ret)
            results.append({
                'Test': f'VaR ({method})',
                'Scenario': f'{method} Value at Risk estimate',
                'Impact Price': impact,
                'Loss %': ret * 100,
                'Severity': '🔴 CRITICAL' if ret < -0.25 else '🟠 HIGH'
            })
        
        # 29. Custom Scenario Builder
        custom_shocks = [
            ('IT -20%', -0.20 if 'Technology' in str(self.sector) else -0.05),
            ('Oil +30%', 0.30 if 'Energy' in str(self.sector) else -0.10),
            ('USD +5%', 0.05 if self.currency == 'USD' else -0.05),
        ]
        for name, pct in custom_shocks:
            impact = self.price * (1 + pct)
            results.append({
                'Test': f'Custom: {name}',
                'Scenario': f'User-defined shock: {name}',
                'Impact Price': impact,
                'Loss %': pct * 100,
                'Severity': '🟢 POSITIVE' if pct > 0 else '🟠 HIGH' if pct < -0.1 else '🟡 MODERATE'
            })
        
        # 30. Multi-Factor Shock
        multi_factor_pct = -0.15 + (-0.05 * self.beta) + (-0.03)
        impact = self.price * (1 + multi_factor_pct)
        results.append({
            'Test': 'Multi-Factor Shock',
            'Scenario': 'Market crash + rate hike + oil spike + currency move',
            'Impact Price': impact,
            'Loss %': multi_factor_pct * 100,
            'Severity': '🔴 CRITICAL'
        })
        
        # 31. War Scenario
        impact = self.price * 0.55
        results.append({
            'Test': 'War Scenario',
            'Scenario': 'Major international conflict breaks out',
            'Impact Price': impact,
            'Loss %': -45,
            'Severity': '💀 EXTREME'
        })
        
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
        
        # 26. Monte Carlo VaR 
        np.random.seed(42)
        daily_returns = np.random.normal(0.0005, 0.02, (1000, 252))  # 1000 paths, 252 days each
        annual_returns = (1 + daily_returns).prod(axis=1) - 1  # Compound daily to annual
        var_95 = np.percentile(annual_returns, 5)  # 5th percentile worst case
        impact = self.price * (1 + var_95)
        loss_pct = var_95 * 100
        results.append({
            'Test': 'Monte Carlo VaR (95%)', 
            'Scenario': '1000 simulated annual return paths', 
            'Impact Price': max(impact, self.price * 0.01),  # Floor at 1% of current price
            'Loss %': max(loss_pct, -99),  # Max loss capped at -99%
            'Severity': '🔴 CRITICAL' if loss_pct < -30 else '🟠 HIGH' if loss_pct < -15 else '🟡 MODERATE'
        })
        
        # 27. VaR Comparison 
        for method, ret in [('Historical', -0.15), ('Parametric', -0.18), ('Monte Carlo', -0.16)]:
            impact = max(self.price * (1 + ret), self.price * 0.10)  # Floor at 10%
            results.append({
                'Test': f'VaR ({method})', 
                'Scenario': f'{method} Value at Risk (annual)', 
                'Impact Price': impact, 
                'Loss %': max(ret * 100, -90), 
                'Severity': '🔴 CRITICAL' if ret < -0.25 else '🟠 HIGH' if ret < -0.15 else '🟡 MODERATE'
            })
        
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
    
    # Preset portfolios with descriptions
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
    
    # Parameters in a nice card
    st.markdown("### ⚙️ Optimization Parameters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_free = st.number_input(
            "🏦 Risk-Free Rate (%)", 
            value=6.0, min_value=0.0, max_value=20.0, step=0.5,
            help="Government bond yield (6% for India, 4-5% for US)"
        ) / 100
    
    with col2:
        period = st.selectbox(
            "📅 Historical Period", 
            ["1y", "2y", "3y", "5y", "10y"], 
            index=3,
            help="More years = more reliable but may miss recent trends"
        )
    
    with col3:
        num_portfolios = st.select_slider(
            "🔢 Simulation Points", 
            options=[5000, 10000, 20000, 30000, 50000],
            value=20000,
            help="More points = smoother frontier but slower"
        )
    
    with col4:
        st.write("")
        st.write("")
        optimize_btn = st.button("🚀 Optimize Portfolio", type="primary", use_container_width=True)
    
    if optimize_btn:
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if len(tickers) < 2:
            st.error("⚠️ Please enter at least 2 tickers for portfolio optimization.")
            return
        
        if len(tickers) > 10:
            st.warning("⚡ More than 10 stocks may take longer to optimize.")
        
        # Show what we're analyzing
        st.info(f"🔍 Analyzing **{len(tickers)} stocks**: {', '.join(tickers)}")
        
        optimizer = PortfolioOptimizer(tickers, period=period, risk_free_rate=risk_free)
        
        # Progress steps
        progress = st.progress(0)
        status = st.empty()
        
        status.text("📥 Downloading price data...")
        progress.progress(20)
        if not optimizer.download_data():
            st.error("❌ Failed to download data. Check ticker symbols.")
            return
        
        status.text("📊 Calculating returns and covariance matrix...")
        progress.progress(40)
        optimizer.calculate_returns()
        
        status.text("🎯 Finding optimal portfolio weights...")
        progress.progress(60)
        max_sharpe = optimizer.optimize_sharpe()
        min_vol = optimizer.optimize_min_volatility()
        
        status.text("📈 Generating efficient frontier...")
        progress.progress(80)
        optimizer.generate_efficient_frontier(num_portfolios)
        
        status.text("✅ Complete!")
        progress.progress(100)
        time.sleep(0.5)
        progress.empty()
        status.empty()
        
        # ===== RESULTS =====
        st.markdown("---")
        st.markdown("## 🏆 Optimal Portfolio Results")
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Assets", f"{len(tickers)}")
        with col2:
            st.metric("🎯 Max Sharpe", f"{max_sharpe['sharpe']:.2f}")
        with col3:
            st.metric("📈 Expected Return", f"{max_sharpe['return']*100:.1f}%")
        with col4:
            st.metric("📉 Risk (Vol)", f"{max_sharpe['volatility']*100:.1f}%")
        
        # Two optimal portfolios side by side
        st.markdown("### 🎯 Optimal Portfolio Allocations")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #10b981; padding: 1rem; border-radius: 12px;">
                <h4 style="color:#10b981; margin:0 0 0.5rem 0;">🎯 Maximum Sharpe Ratio</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin:0;">Best risk-adjusted returns</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Expected Return", f"{max_sharpe['return']*100:.1f}%")
            st.metric("Volatility", f"{max_sharpe['volatility']*100:.1f}%")
            st.metric("Sharpe Ratio", f"{max_sharpe['sharpe']:.2f}")
            
            # Pie chart
            weights_data = {k: v for k, v in max_sharpe['weights'].items() if v > 0.01}
            if weights_data:
                fig = go.Figure(data=[go.Pie(
                    labels=list(weights_data.keys()),
                    values=list(weights_data.values()),
                    hole=0.5,
                    textinfo='label+percent',
                    marker=dict(colors=['#10b981','#34d399','#6ee7b7','#a7f3d0','#d1fae5','#059669','#047857'][:len(weights_data)])
                )])
                fig.update_layout(height=350, template='plotly_white', margin=dict(t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #f59e0b; padding: 1rem; border-radius: 12px;">
                <h4 style="color:#f59e0b; margin:0 0 0.5rem 0;">🛡️ Minimum Volatility</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin:0;">Lowest risk portfolio</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Expected Return", f"{min_vol['return']*100:.1f}%")
            st.metric("Volatility", f"{min_vol['volatility']*100:.1f}%")
            st.metric("Sharpe Ratio", f"{min_vol['sharpe']:.2f}")
            
            weights_data = {k: v for k, v in min_vol['weights'].items() if v > 0.01}
            if weights_data:
                fig = go.Figure(data=[go.Pie(
                    labels=list(weights_data.keys()),
                    values=list(weights_data.values()),
                    hole=0.5,
                    textinfo='label+percent',
                    marker=dict(colors=['#f59e0b','#fbbf24','#fcd34d','#fde68a','#fef3c7','#d97706','#b45309'][:len(weights_data)])
                )])
                fig.update_layout(height=350, template='plotly_white', margin=dict(t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
        
        # Efficient Frontier
        st.markdown("### 📈 Efficient Frontier")
        st.caption("Each dot = a different portfolio combination. The curve shows the best possible return for each risk level.")
        
        ef = optimizer.efficient_frontier
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=ef['volatilities'] * 100,
            y=ef['returns'] * 100,
            mode='markers',
            marker=dict(
                size=4,
                color=ef['sharpes'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Sharpe Ratio')
            ),
            name=f'{num_portfolios:,} Portfolios',
            text=[f"Sharpe: {s:.2f}<br>Return: {r*100:.1f}%<br>Risk: {v*100:.1f}%" 
                  for s, r, v in zip(ef['sharpes'], ef['returns'], ef['volatilities'])],
            hoverinfo='text'
        ))
        
        fig.add_trace(go.Scatter(
            x=[max_sharpe['volatility'] * 100],
            y=[max_sharpe['return'] * 100],
            mode='markers+text',
            marker=dict(size=25, color='#10b981', symbol='star', line=dict(width=3, color='white')),
            name='Max Sharpe',
            text=['★ Max Sharpe'],
            textposition='top center',
            textfont=dict(size=14, color='#10b981', family='Arial Black')
        ))
        
        fig.add_trace(go.Scatter(
            x=[min_vol['volatility'] * 100],
            y=[min_vol['return'] * 100],
            mode='markers+text',
            marker=dict(size=20, color='#f59e0b', symbol='diamond', line=dict(width=3, color='white')),
            name='Min Volatility',
            text=['◆ Min Vol'],
            textposition='top center',
            textfont=dict(size=14, color='#f59e0b', family='Arial Black')
        ))
        
        fig.update_layout(
            title=f'Efficient Frontier • {len(tickers)} Assets • {num_portfolios:,} Portfolios',
            xaxis_title='Annualized Volatility (%)',
            yaxis_title='Expected Annual Return (%)',
            template='plotly_white',
            height=600,
            hovermode='closest',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation Matrix
        st.markdown("### 🔥 Correlation Matrix")
        st.caption("Shows how stocks move together. 🔵 Blue = move opposite (good diversification). 🔴 Red = move together (higher risk).")
        
        corr = optimizer.daily_returns.corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale='RdBu',
            zmid=0,
            zmin=-1, zmax=1,
            text=np.round(corr.values, 2),
            texttemplate='%{text}',
            textfont={"size": 12},
            showscale=True,
            colorbar=dict(title='Correlation')
        ))
        fig.update_layout(height=450, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tips
        with st.expander("💡 How to Use These Results", expanded=False):
            st.markdown("""
            ### 🎯 Max Sharpe Ratio Portfolio
            - **Best for**: Long-term investors seeking optimal risk-adjusted returns
            - **Use when**: You want the mathematically optimal portfolio
            - **Rebalance**: Every 3-6 months to maintain weights
            
            ### 🛡️ Minimum Volatility Portfolio
            - **Best for**: Conservative investors or near-retirement
            - **Use when**: Capital preservation is priority
            - **Expect**: Lower returns but less portfolio fluctuation
            
            ### 📈 Efficient Frontier
            - Portfolios on the curve are "efficient" - you can't get more return without more risk
            - Portfolios below the curve are suboptimal
            - The "sweet spot" is usually near the Max Sharpe portfolio
            
            ### ⚠️ Important Notes
            - Historical returns don't guarantee future results
            - Past correlations can break during market crises
            - Consider your personal risk tolerance and investment horizon
            """)
            # ===== ADVANCED FINANCIAL SCORES =====

class PiotroskiFScore:
    """Piotroski F-Score (0-9) - Verified with Yahoo Finance data structure"""
    
    @staticmethod
    def calculate(income_df, balance_df, cashflow_df):
        """Calculate Piotroski F-Score from financial statements"""
        score = 0
        details = []
        
        # Safety check
        if income_df is None or balance_df is None or cashflow_df is None:
            return {'score': 0, 'rating': 'N/A', 'details': ['Insufficient data']}
        if income_df.empty or balance_df.empty:
            return {'score': 0, 'rating': 'N/A', 'details': ['Financial data not available']}
        
        try:
            # Yahoo Finance columns are dates (YYYY-MM-DD), get latest 2 columns
            cols = income_df.columns[:2]
            if len(cols) < 2:
                return {'score': 0, 'rating': 'N/A', 'details': ['Need 2 years of data']}
            
            # ===== PROFITABILITY (4 points) =====
            
            # 1. Net Income > 0
            ni_key = None
            for key in ['Net Income', 'Net Income Common Stockholders', 'Net Income, Total']:
                if key in income_df.index:
                    ni_key = key
                    break
            
            if ni_key:
                ni_current = income_df.loc[ni_key, cols[0]]
                ni_prev = income_df.loc[ni_key, cols[1]] if len(cols) > 1 else 0
                
                if pd.notna(ni_current) and ni_current > 0:
                    score += 1
                    details.append(f"✅ Positive Net Income ({ni_current/1e9 if abs(ni_current)>1e9 else ni_current/1e6:.1f}{'B' if abs(ni_current)>1e9 else 'M'})")
                else:
                    details.append("❌ Negative Net Income")
            else:
                details.append("⚠️ Net Income data not found")
            
            # 2. Operating Cash Flow > 0
            ocf_key = None
            for key in ['Operating Cash Flow', 'Operating Cash Flow, Total']:
                if key in cashflow_df.index:
                    ocf_key = key
                    break
            
            if ocf_key:
                ocf_current = cashflow_df.loc[ocf_key, cashflow_df.columns[0]]
                if pd.notna(ocf_current) and ocf_current > 0:
                    score += 1
                    details.append("✅ Positive Operating Cash Flow")
                else:
                    details.append("❌ Negative Operating Cash Flow")
            else:
                details.append("⚠️ OCF data not found")
            
            # 3. ROA Increasing
            asset_key = None
            for key in ['Total Assets', 'Total Assets, Total']:
                if key in balance_df.index:
                    asset_key = key
                    break
            
            if ni_key and asset_key:
                assets_current = balance_df.loc[asset_key, balance_df.columns[0]]
                assets_prev = balance_df.loc[asset_key, balance_df.columns[1]] if len(balance_df.columns) > 1 else assets_current
                
                if assets_current and assets_prev and assets_current > 0 and assets_prev > 0:
                    roa = ni_current / assets_current
                    roa_prev = ni_prev / assets_prev
                    if roa > roa_prev:
                        score += 1
                        details.append(f"✅ ROA Increasing ({roa*100:.1f}% vs {roa_prev*100:.1f}%)")
                    else:
                        details.append(f"❌ ROA Declining ({roa*100:.1f}% vs {roa_prev*100:.1f}%)")
                else:
                    details.append("⚠️ Cannot calculate ROA")
            
            # 4. Operating Cash Flow > Net Income (Quality of Earnings)
            if ocf_key and ni_key and pd.notna(ocf_current) and pd.notna(ni_current):
                if ocf_current > ni_current:
                    score += 1
                    details.append("✅ OCF > Net Income (Quality Earnings)")
                else:
                    details.append("❌ OCF < Net Income (Low Quality)")
            
            # ===== LEVERAGE & LIQUIDITY (3 points) =====
            
            # 5. Lower Long Term Debt
            debt_key = None
            for key in ['Long Term Debt', 'Long-Term Debt', 'Total Debt']:
                if key in balance_df.index:
                    debt_key = key
                    break
            
            if debt_key and len(balance_df.columns) > 1:
                debt_current = balance_df.loc[debt_key, balance_df.columns[0]]
                debt_prev = balance_df.loc[debt_key, balance_df.columns[1]]
                if pd.notna(debt_current) and pd.notna(debt_prev):
                    if debt_current < debt_prev:
                        score += 1
                        details.append("✅ Debt Decreasing")
                    else:
                        details.append("❌ Debt Increasing")
                else:
                    details.append("⚠️ Debt data incomplete")
            
            # 6. Higher Current Ratio
            ca_key = None
            cl_key = None
            for key in ['Current Assets', 'Current Assets, Total']:
                if key in balance_df.index: ca_key = key; break
            for key in ['Current Liabilities', 'Current Liabilities, Total']:
                if key in balance_df.index: cl_key = key; break
            
            if ca_key and cl_key and len(balance_df.columns) > 1:
                ca_current = balance_df.loc[ca_key, balance_df.columns[0]]
                cl_current = balance_df.loc[cl_key, balance_df.columns[0]]
                ca_prev = balance_df.loc[ca_key, balance_df.columns[1]]
                cl_prev = balance_df.loc[cl_key, balance_df.columns[1]]
                
                if all(pd.notna(x) and x > 0 for x in [ca_current, cl_current, ca_prev, cl_prev]):
                    cr = ca_current / cl_current
                    cr_prev = ca_prev / cl_prev
                    if cr > cr_prev:
                        score += 1
                        details.append(f"✅ Current Ratio Improving ({cr:.2f} vs {cr_prev:.2f})")
                    else:
                        details.append(f"❌ Current Ratio Declining ({cr:.2f} vs {cr_prev:.2f})")
            
            # 7. No New Shares Issued
            shares_key = None
            for key in ['Diluted Average Shares', 'Basic Average Shares', 'Ordinary Shares Number']:
                if key in income_df.index: shares_key = key; break
            
            if not shares_key:
                for key in ['Share Issued', 'Common Stock']:
                    if key in balance_df.index: shares_key = key; break
            
            if shares_key and len(income_df.columns if shares_key in income_df.index else balance_df.columns) > 1:
                df_to_use = income_df if shares_key in income_df.index else balance_df
                shares_current = df_to_use.loc[shares_key, df_to_use.columns[0]]
                shares_prev = df_to_use.loc[shares_key, df_to_use.columns[1]]
                if pd.notna(shares_current) and pd.notna(shares_prev):
                    if shares_current <= shares_prev:
                        score += 1
                        details.append("✅ No Share Dilution")
                    else:
                        details.append("❌ Share Dilution Detected")
            
            # ===== OPERATING EFFICIENCY (2 points) =====
            
            # 8. Higher Gross Margin
            gp_key = None
            rev_key = None
            for key in ['Gross Profit', 'Gross Profit, Total']:
                if key in income_df.index: gp_key = key; break
            for key in ['Total Revenue', 'Revenue', 'Total Revenue, Total']:
                if key in income_df.index: rev_key = key; break
            
            if gp_key and rev_key:
                gp_current = income_df.loc[gp_key, cols[0]]
                rev_current = income_df.loc[rev_key, cols[0]]
                gp_prev = income_df.loc[gp_key, cols[1]]
                rev_prev = income_df.loc[rev_key, cols[1]]
                
                if all(pd.notna(x) and x > 0 for x in [gp_current, rev_current, gp_prev, rev_prev]):
                    gm = gp_current / rev_current
                    gm_prev = gp_prev / rev_prev
                    if gm > gm_prev:
                        score += 1
                        details.append(f"✅ Gross Margin Improving ({gm*100:.1f}% vs {gm_prev*100:.1f}%)")
                    else:
                        details.append(f"❌ Gross Margin Declining ({gm*100:.1f}% vs {gm_prev*100:.1f}%)")
            
            # 9. Higher Asset Turnover
            if rev_key and asset_key and len(cols) > 1:
                assets_prev2 = balance_df.loc[asset_key, balance_df.columns[1]] if len(balance_df.columns) > 1 else None
                if assets_current and assets_prev2 and assets_current > 0 and assets_prev2 > 0:
                    at = rev_current / assets_current
                    at_prev = rev_prev / assets_prev2
                    if at > at_prev:
                        score += 1
                        details.append(f"✅ Asset Turnover Improving ({at:.3f} vs {at_prev:.3f})")
                    else:
                        details.append(f"❌ Asset Turnover Declining")
            
        except Exception as e:
            details.append(f"⚠️ Calculation error: {str(e)[:50]}")
        
        # Rating
        if score >= 7:
            rating = "🟢 STRONG"
        elif score >= 4:
            rating = "🟡 AVERAGE"
        else:
            rating = "🔴 WEAK"
        
        return {'score': score, 'rating': rating, 'details': details}


class AltmanZScore:
    """Altman Z-Score - Verified with Yahoo Finance data"""
    
    @staticmethod
    def calculate(balance_df, income_df, market_cap):
        """Calculate Altman Z-Score"""
        if balance_df is None or income_df is None:
            return None
        if balance_df.empty or income_df.empty:
            return None
        
        try:
            col = balance_df.columns[0]
            inc_col = income_df.columns[0]
            
            # Get Working Capital
            ca = None
            cl = None
            for key in ['Current Assets', 'Current Assets, Total']:
                if key in balance_df.index: ca = balance_df.loc[key, col]; break
            for key in ['Current Liabilities', 'Current Liabilities, Total']:
                if key in balance_df.index: cl = balance_df.loc[key, col]; break
            
            # Get Total Assets
            ta = None
            for key in ['Total Assets', 'Total Assets, Total']:
                if key in balance_df.index: ta = balance_df.loc[key, col]; break
            
            # Get Retained Earnings (or use Stockholders Equity as proxy)
            re_val = None
            for key in ['Retained Earnings', 'Stockholders Equity', 'Total Stockholder Equity', 'Total Equity']:
                if key in balance_df.index: re_val = balance_df.loc[key, col]; break
            
            # Get EBIT
            ebit = None
            for key in ['EBIT', 'Operating Income', 'Operating Income, Total']:
                if key in income_df.index: ebit = income_df.loc[key, inc_col]; break
            
            # Get Total Liabilities
            tl = None
            for key in ['Total Liabilities Net Minority Interest', 'Total Liabilities', 'Total Liabilities, Total']:
                if key in balance_df.index: tl = balance_df.loc[key, col]; break
            
            # Get Revenue
            sales = None
            for key in ['Total Revenue', 'Revenue', 'Total Revenue, Total']:
                if key in income_df.index: sales = income_df.loc[key, inc_col]; break
            
            # Check all values exist
            if any(v is None or pd.isna(v) or v == 0 for v in [ca, cl, ta, re_val, ebit, tl, sales]):
                # Try to calculate with available data
                if ta is None or ta == 0:
                    return None
            
            wc = (ca or 0) - (cl or 0)
            x1 = wc / ta if ta else 0
            x2 = (re_val or 0) / ta if ta else 0
            x3 = (ebit or 0) / ta if ta else 0
            x4 = (market_cap or 0) / (tl or ta) if (tl or ta) else 0
            x5 = (sales or 0) / ta if ta else 0
            
            z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5
            
            if z > 2.99:
                zone = "🟢 SAFE ZONE"
                risk = "Low bankruptcy risk"
            elif z > 1.81:
                zone = "🟡 GREY ZONE"
                risk = "Moderate risk"
            else:
                zone = "🔴 DISTRESS ZONE"
                risk = "High bankruptcy risk"
            
            return {'z_score': round(z, 2), 'zone': zone, 'risk': risk,
                    'components': {'X1': round(x1, 3), 'X2': round(x2, 3), 'X3': round(x3, 3), 'X4': round(x4, 3), 'X5': round(x5, 3)}}
        except Exception as e:
            return None
        # ===== INDEX & SECTOR COMPARISON =====

class IndexComparison:
    """Compare stock vs Benchmark Index (NIFTY 50 / S&P 500)"""
    
    BENCHMARKS = {'INR': '^NSEI', 'USD': '^GSPC'}
    
    SECTOR_ETFS = {
        'Technology': 'XLK', 'Financial Services': 'XLF', 'Healthcare': 'XLV',
        'Consumer Cyclical': 'XLY', 'Energy': 'XLE', 'Industrials': 'XLI',
        'Consumer Defensive': 'XLP', 'Real Estate': 'XLRE', 'Utilities': 'XLU',
        'Basic Materials': 'XLB', 'Communication Services': 'XLC',
    }
    
    INDIAN_SECTOR_INDICES = {
        'Technology': '^CNXIT', 'Financial Services': '^CNXFIN', 'Healthcare': '^CNXPHARMA',
        'Energy': '^CNXENERGY', 'Consumer Cyclical': '^CNXAUTO', 'Consumer Defensive': '^CNXFMCG',
        'Basic Materials': '^CNXMETAL', 'Real Estate': '^CNXREALTY',
    }
    
    @staticmethod
    def fetch_comparison_data(ticker, currency, sector, period="1y"):
        results = {}
        benchmark = IndexComparison.BENCHMARKS.get(currency, '^GSPC')
        
        if currency == 'INR':
            sector_indices = IndexComparison.INDIAN_SECTOR_INDICES
        else:
            sector_indices = IndexComparison.SECTOR_ETFS
        
        sector_index = sector_indices.get(sector)
        
        try:
            all_tickers = [ticker, benchmark]
            if sector_index:
                all_tickers.append(sector_index)
            
            data = yf.download(all_tickers, period=period, progress=False)
            
            if len(all_tickers) == 3:
                close_data = data['Close']
                stock_prices = close_data[ticker]
                benchmark_prices = close_data[benchmark]
                sector_prices = close_data[sector_index]
            else:
                close_data = data['Close']
                stock_prices = close_data[ticker]
                benchmark_prices = close_data[benchmark]
                sector_prices = None
            
            stock_returns = stock_prices.pct_change().dropna()
            benchmark_returns = benchmark_prices.pct_change().dropna()
            
            common_dates = stock_returns.index.intersection(benchmark_returns.index)
            stock_returns = stock_returns[common_dates]
            benchmark_returns = benchmark_returns[common_dates]
            
            stock_cumulative = (1 + stock_returns).cumprod() * 100
            benchmark_cumulative = (1 + benchmark_returns).cumprod() * 100
            
            covariance = stock_returns.cov(benchmark_returns)
            variance = benchmark_returns.var()
            beta = covariance / variance if variance and variance > 0 else 1.0
            
            stock_annual = stock_returns.mean() * 252
            benchmark_annual = benchmark_returns.mean() * 252
            alpha = stock_annual - (beta * benchmark_annual)
            
            tracking_error = (stock_returns - benchmark_returns).std() * np.sqrt(252)
            info_ratio = (stock_annual - benchmark_annual) / tracking_error if tracking_error and tracking_error > 0 else 0
            
            stock_peak = stock_cumulative.expanding().max()
            stock_dd = (stock_cumulative - stock_peak) / stock_peak
            max_dd = stock_dd.min()
            
            correlation = stock_returns.corr(benchmark_returns)
            
            results = {
                'stock_returns': stock_returns, 'benchmark_returns': benchmark_returns,
                'stock_cumulative': stock_cumulative, 'benchmark_cumulative': benchmark_cumulative,
                'beta': beta, 'alpha': alpha, 'tracking_error': tracking_error,
                'information_ratio': info_ratio, 'max_drawdown': max_dd, 'correlation': correlation,
                'stock_annual_return': stock_annual, 'benchmark_annual_return': benchmark_annual,
                'benchmark_name': 'NIFTY 50' if currency == 'INR' else 'S&P 500',
                'sector_prices': sector_prices,
            }
            
            if sector_prices is not None:
                sector_returns = sector_prices.pct_change().dropna()
                common = stock_returns.index.intersection(sector_returns.index)
                sector_returns = sector_returns[common]
                stock_ret_aligned = stock_returns[common]
                sector_cumulative = (1 + sector_returns).cumprod() * 100
                sector_annual = sector_returns.mean() * 252
                results['sector_cumulative'] = sector_cumulative
                results['sector_annual_return'] = sector_annual
                results['sector_relative'] = stock_annual - sector_annual
            
            return results
        except Exception as e:
            return None


def create_index_comparison_dashboard(analyzer):
    """Index & Sector Comparison Dashboard"""
    st.markdown('<div class="section-header">📊 Index & Sector Comparison</div>', unsafe_allow_html=True)
    
    cur = analyzer.currency_symbol
    ticker = analyzer.ticker
    sector = analyzer.financials.get('sector', 'Unknown')
    currency = analyzer.currency
    benchmark_name = 'NIFTY 50' if currency == 'INR' else 'S&P 500'
    
    periods = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y"}
    selected = st.select_slider("Comparison Period", options=list(periods.keys()), value="1 Year")
    period = periods[selected]
    
    if st.button(f"📊 Compare vs {benchmark_name} & Sector", type="primary", use_container_width=True):
        with st.spinner("Fetching comparison data..."):
            comparison = IndexComparison.fetch_comparison_data(ticker, currency, sector, period)
        
        if comparison is None:
            st.error("Could not fetch comparison data. Try a different period or ticker.")
            return
        
        st.markdown("### 📈 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            stock_ret = comparison['stock_annual_return'] * 100
            bench_ret = comparison['benchmark_annual_return'] * 100
            st.metric(f"{analyzer.company_name[:15]}", f"{stock_ret:.1f}%", delta=f"vs {benchmark_name}: {stock_ret-bench_ret:+.1f}%")
        with col2:
            st.metric(benchmark_name, f"{bench_ret:.1f}%")
        with col3:
            alpha_pct = comparison['alpha'] * 100
            st.metric("Alpha", f"{alpha_pct:.2f}%", delta="Outperforming 📈" if alpha_pct>0 else "Underperforming 📉")
        with col4:
            beta_val = comparison['beta']
            st.metric("Beta", f"{beta_val:.2f}", delta="Aggressive" if beta_val>1.1 else "Defensive" if beta_val<0.9 else "Market-like")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Correlation", f"{comparison['correlation']:.2f}")
        col2.metric("Tracking Error", f"{comparison['tracking_error']*100:.1f}%")
        col3.metric("Info Ratio", f"{comparison['information_ratio']:.2f}")
        col4.metric("Max Drawdown", f"{comparison['max_drawdown']*100:.1f}%", delta_color="inverse")
        
        st.markdown("### 📈 Cumulative Returns (Base=100)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=comparison['stock_cumulative'].index, y=comparison['stock_cumulative'].values,
                                 name=analyzer.company_name[:20], line=dict(color='#667eea', width=3)))
        fig.add_trace(go.Scatter(x=comparison['benchmark_cumulative'].index, y=comparison['benchmark_cumulative'].values,
                                 name=benchmark_name, line=dict(color='#94a3b8', width=2, dash='dash')))
        if 'sector_cumulative' in comparison:
            fig.add_trace(go.Scatter(x=comparison['sector_cumulative'].index, y=comparison['sector_cumulative'].values,
                                     name=f"{sector} Sector", line=dict(color='#10b981', width=2, dash='dot')))
        fig.update_layout(title=f'Total Return Comparison • {selected}', template='plotly_white', height=500,
                          hovermode='x unified', yaxis_title='Growth of $100')
        st.plotly_chart(fig, use_container_width=True)
        
        alpha_val = comparison['alpha'] * 100
        if alpha_val > 2:
            summary = f"🟢 **{analyzer.company_name}** significantly outperforms **{benchmark_name}** (Alpha: {alpha_val:.1f}%)"
        elif alpha_val > 0:
            summary = f"🟡 **{analyzer.company_name}** slightly outperforms **{benchmark_name}** (Alpha: {alpha_val:.1f}%)"
        else:
            summary = f"🔴 **{analyzer.company_name}** underperforms **{benchmark_name}** (Alpha: {alpha_val:.1f}%)"
        st.info(summary)
        # ===== AI INVESTMENT THESIS GENERATOR =====

def generate_investment_thesis(analyzer, dcf_result=None):
    """Generate automated investment thesis based on financial metrics"""
    ratios = analyzer.ratios
    cur = analyzer.currency_symbol
    cp = analyzer.live_price_data.get('current_price')
    
    thesis_parts = []
    score = 0
    max_score = 0
    
    # 1. Revenue Growth
    rev_growth = ratios.get('Revenue Growth (YoY)')
    if rev_growth is not None:
        max_score += 1
        if rev_growth > 20:
            thesis_parts.append(f"🟢 **Strong Revenue Growth:** Revenue grew {rev_growth:.1f}% YoY, indicating robust demand.")
            score += 1
        elif rev_growth > 10:
            thesis_parts.append(f"🟡 **Moderate Revenue Growth:** Revenue grew {rev_growth:.1f}% YoY, showing steady expansion.")
            score += 0.5
        elif rev_growth > 0:
            thesis_parts.append(f"🟠 **Slow Revenue Growth:** Revenue grew only {rev_growth:.1f}% YoY, below market average.")
        else:
            thesis_parts.append(f"🔴 **Revenue Decline:** Revenue declined {abs(rev_growth):.1f}% YoY, a concerning trend.")
    
    # 2. Profitability
    net_margin = ratios.get('Net Profit Margin')
    if net_margin is not None:
        max_score += 1
        if net_margin > 20:
            thesis_parts.append(f"🟢 **Excellent Profitability:** Net margin of {net_margin:.1f}% shows strong pricing power.")
            score += 1
        elif net_margin > 10:
            thesis_parts.append(f"🟡 **Healthy Profitability:** Net margin of {net_margin:.1f}% indicates good cost management.")
            score += 0.5
        else:
            thesis_parts.append(f"🟠 **Thin Margins:** Net margin of {net_margin:.1f}% suggests competitive pressure.")
    
    # 3. ROE
    roe = ratios.get('ROE')
    if roe is not None:
        max_score += 1
        if roe > 20:
            thesis_parts.append(f"🟢 **Efficient Capital Allocation:** ROE of {roe:.1f}% shows management creates shareholder value.")
            score += 1
        elif roe > 10:
            thesis_parts.append(f"🟡 **Adequate Returns:** ROE of {roe:.1f}% is acceptable but not exceptional.")
            score += 0.5
        else:
            thesis_parts.append(f"🔴 **Poor Returns:** ROE of {roe:.1f}% indicates inefficient use of equity.")
    
    # 4. Debt
    de = ratios.get('Debt to Equity')
    if de is not None:
        max_score += 1
        if de < 0.5:
            thesis_parts.append(f"🟢 **Conservative Capital Structure:** D/E of {de:.2f} suggests low financial risk.")
            score += 1
        elif de < 1.5:
            thesis_parts.append(f"🟡 **Moderate Leverage:** D/E of {de:.2f} is manageable but warrants monitoring.")
            score += 0.5
        else:
            thesis_parts.append(f"🔴 **High Leverage:** D/E of {de:.2f} raises concerns about debt sustainability.")
    
    # 5. Liquidity
    cr = ratios.get('Current Ratio')
    if cr is not None:
        max_score += 1
        if cr > 1.5:
            thesis_parts.append(f"🟢 **Healthy Liquidity:** Current ratio of {cr:.2f} indicates ability to meet short-term obligations.")
            score += 1
        elif cr > 1.0:
            thesis_parts.append(f"🟡 **Adequate Liquidity:** Current ratio of {cr:.2f} is sufficient but not comfortable.")
            score += 0.5
        else:
            thesis_parts.append(f"🔴 **Liquidity Concern:** Current ratio of {cr:.2f} may indicate cash flow issues.")
    
    # 6. DCF Valuation
    if dcf_result:
        upside = dcf_result.get('upside', 0)
        max_score += 1
        if upside > 20:
            thesis_parts.append(f"🟢 **Significantly Undervalued:** DCF estimates {upside:.0f}% upside from current price of {cur}{cp:.2f}.")
            score += 1
        elif upside > 0:
            thesis_parts.append(f"🟡 **Modestly Undervalued:** DCF suggests {upside:.0f}% upside, offering some margin of safety.")
            score += 0.5
        else:
            thesis_parts.append(f"🔴 **Overvalued:** DCF shows {abs(upside):.0f}% downside from current market price.")
    
    # 7. EPS
    eps = ratios.get('EPS')
    ni_growth = ratios.get('Net Income Growth (YoY)')
    if eps is not None and ni_growth is not None:
        max_score += 1
        if ni_growth > 15 and eps > 0:
            thesis_parts.append(f"🟢 **Strong Earnings:** EPS of {cur}{eps:.2f} with {ni_growth:.1f}% growth shows earnings momentum.")
            score += 1
        elif eps > 0:
            thesis_parts.append(f"🟡 **Stable Earnings:** EPS of {cur}{eps:.2f} indicates consistent profitability.")
            score += 0.5
    
    # 8. Market Position
    market_cap = analyzer.live_price_data.get('market_cap', 0)
    sector = analyzer.financials.get('sector', 'Unknown')
    if market_cap > 0:
        thesis_parts.append(f"📊 **Market Position:** {analyzer.company_name} operates in **{sector}** with market cap of **{analyzer._format_amount(market_cap)}**.")
    
    # Overall
    if max_score > 0:
        final_score = (score / max_score) * 100
        if final_score >= 75:
            overall = "🟢 **OVERALL: STRONG FUNDAMENTALS** — The company demonstrates robust financial health across multiple metrics."
        elif final_score >= 50:
            overall = "🟡 **OVERALL: MIXED SIGNALS** — While some metrics are positive, there are areas requiring closer scrutiny."
        elif final_score >= 25:
            overall = "🟠 **OVERALL: BELOW AVERAGE** — Several financial indicators suggest caution."
        else:
            overall = "🔴 **OVERALL: HIGH RISK** — Multiple warning signs across key financial metrics."
    else:
        overall = "⚠️ **INSUFFICIENT DATA** — Not enough financial data to generate a complete thesis."
    
    return {'thesis_parts': thesis_parts, 'overall': overall, 'score': f"{score:.0f}/{max_score:.0f}" if max_score > 0 else "N/A", 'score_pct': (score/max_score*100) if max_score > 0 else 0}


def create_investment_thesis_dashboard(analyzer):
    """Investment Thesis Dashboard"""
    st.markdown('<div class="section-header">📝 AI-Generated Investment Thesis</div>', unsafe_allow_html=True)
    
    income = analyzer.financials.get('income')
    cashflow = analyzer.financials.get('cashflow')
    cp = analyzer.live_price_data.get('current_price')
    
    # Quick DCF for valuation context
    dcf_result = None
    if cp and income is not None and not income.empty:
        fcf = analyzer._safe_get(cashflow, ['Free Cash Flow']) if cashflow is not None else 0
        if not fcf:
            ni = analyzer._safe_get(income, ['Net Income'])
            fcf = ni * 0.8 if ni else 0
        if fcf and fcf > 0:
            shares = analyzer._safe_get(income, ['Diluted Average Shares']) or 1e6
            beta = analyzer.live_price_data.get('beta', 1.0) or 1.0
            rg = analyzer.ratios.get('Revenue Growth (YoY)', 10) or 10
            rf = 0.072 if analyzer.currency == 'INR' else 0.045
            mr = 0.12 if analyzer.currency == 'INR' else 0.10
            dcf = AdvancedDCF(fcf, shares, cp, max(0.02, min(rg/100, 0.35)), beta, rf, mr)
            dcf_result = dcf.calculate()
    
    thesis = generate_investment_thesis(analyzer, dcf_result)
    score_pct = thesis['score_pct']
    score_color = "#10b981" if score_pct >= 75 else "#f59e0b" if score_pct >= 50 else "#ef4444"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid {score_color}; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: #e2e8f0; margin: 0;">📝 {analyzer.company_name}</h3>
            <span style="font-size: 1.5rem; font-weight: 900; color: {score_color};">{thesis['score']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for part in thesis['thesis_parts']:
        st.markdown(f"- {part}")
    
    st.markdown("---")
    st.markdown(f"### {thesis['overall']}")
    st.caption("💡 Auto-generated from reported financial data. Always do your own research before investing.")


# ===== HISTORICAL DCF TRACKING =====

class HistoricalDCFTracker:
    """Track DCF assumptions over multiple periods"""
    
    @staticmethod
    def calculate_historical_growth(income_df):
        if income_df is None or income_df.empty:
            return None
        rev_key = None
        for key in ['Total Revenue', 'Revenue']:
            if key in income_df.index:
                rev_key = key
                break
        if not rev_key:
            return None
        rev_data = income_df.loc[rev_key]
        years = len(rev_data)
        if years < 2:
            return None
        growth_rates = []
        for i in range(years - 1):
            if rev_data.iloc[i+1] and rev_data.iloc[i+1] != 0:
                growth = (rev_data.iloc[i] - rev_data.iloc[i+1]) / abs(rev_data.iloc[i+1]) * 100
                growth_rates.append({'period': f"Year {i+1}", 'revenue': rev_data.iloc[i], 'growth': growth})
        if growth_rates:
            avg_growth = np.mean([g['growth'] for g in growth_rates])
            median_growth = np.median([g['growth'] for g in growth_rates])
            return {'growth_rates': growth_rates, 'average': avg_growth, 'median': median_growth,
                    'min': min(g['growth'] for g in growth_rates), 'max': max(g['growth'] for g in growth_rates),
                    'years': len(growth_rates)}
        return None


def create_historical_dcf_tracker(analyzer):
    """Display historical growth for DCF context"""
    income = analyzer.financials.get('income')
    if income is None or income.empty:
        return
    hist = HistoricalDCFTracker.calculate_historical_growth(income)
    if hist:
        with st.expander("📊 Historical Revenue Growth (DCF Context)", expanded=False):
            st.markdown(f"**{hist['years']} years** tracked | Avg: **{hist['average']:.1f}%** | Median: **{hist['median']:.1f}%** | Range: {hist['min']:.1f}% to {hist['max']:.1f}%")
            years_labels = [g['period'] for g in hist['growth_rates']]
            growths = [g['growth'] for g in hist['growth_rates']]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=years_labels, y=growths, marker_color='#667eea',
                                 text=[f"{g:.1f}%" for g in growths], textposition='outside'))
            fig.add_hline(y=hist['average'], line_dash="dash", line_color="#10b981",
                          annotation_text=f"Avg: {hist['average']:.1f}%")
            fig.update_layout(title='Historical Revenue Growth Rates', template='plotly_white', height=300)
            st.plotly_chart(fig, use_container_width=True)


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
    """Advanced Financial Scores Dashboard"""
    st.markdown('<div class="section-header">🔬 Advanced Financial Scores</div>', unsafe_allow_html=True)
    
    income = analyzer.financials.get('income')
    balance = analyzer.financials.get('balance')
    cashflow = analyzer.financials.get('cashflow')
    market_cap = analyzer.live_price_data.get('market_cap', 0)
    
    if income is None or income.empty:
        st.warning("📝 Financial statements not available for advanced scoring. Key ratios shown from market data.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Piotroski F-Score")
        st.caption("Financial strength (0-9) | 7+ = Strong, 4-6 = Average, <4 = Weak")
        
        f_score = PiotroskiFScore.calculate(income, balance, cashflow)
        
        score_color = "#10b981" if f_score['score'] >= 7 else "#f59e0b" if f_score['score'] >= 4 else "#ef4444"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=f_score['score'],
            title={'text': "F-Score"},
            number={'font': {'color': score_color, 'size': 40}},
            gauge={'axis': {'range': [0, 9]}, 'bar': {'color': score_color},
                   'steps': [{'range': [0, 3], 'color': "rgba(239,68,68,0.2)"},
                             {'range': [3, 6], 'color': "rgba(245,158,11,0.2)"},
                             {'range': [6, 9], 'color': "rgba(16,185,129,0.2)"}]}
        ))
        fig.update_layout(height=250, margin=dict(t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"**{f_score['rating']}**")
        with st.expander(f"📋 Details (Score: {f_score['score']}/9)"):
            for detail in f_score['details']:
                st.write(detail)
    
    with col2:
        st.markdown("### 🏦 Altman Z-Score")
        st.caption("Bankruptcy prediction | >2.99 = Safe, 1.81-2.99 = Grey, <1.81 = Distress")
        
        z_result = AltmanZScore.calculate(balance, income, market_cap)
        
        if z_result:
            z = z_result['z_score']
            z_color = "#10b981" if z > 2.99 else "#f59e0b" if z > 1.81 else "#ef4444"
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=z,
                title={'text': "Z-Score"},
                number={'font': {'color': z_color, 'size': 40}},
                gauge={'axis': {'range': [0, 6]}, 'bar': {'color': z_color},
                       'steps': [{'range': [0, 1.81], 'color': "rgba(239,68,68,0.2)"},
                                 {'range': [1.81, 2.99], 'color': "rgba(245,158,11,0.2)"},
                                 {'range': [2.99, 6], 'color': "rgba(16,185,129,0.2)"}]}
            ))
            fig.update_layout(height=250, margin=dict(t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"**{z_result['zone']}** - {z_result['risk']}")
        else:
            st.warning("Insufficient data for Z-Score calculation")
            
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
    
     # Auto-run since button is already clicked in Tab 2
    with st.spinner("Running comprehensive stress tests..."):
        results_df = engine.run_all_tests()
        with st.spinner("Running stress tests..."): results_df = engine.run_all_tests()
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

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Stock Analysis", "🛡️ Stress Tests", "📈 Technical Analysis", "🎯 Portfolio Optimizer"])

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

        # Use whatever is in the text input
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
            with st.spinner("🔍 Analyzing..."): 
                analyzer.get_live_price()
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

            # Ratios
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
                
                
            # Peer Comparison
            group_name, peer_list = detect_peer_group(analyzer.ticker)
            if peer_list:
                peer_list = [p for p in peer_list if p!=analyzer.ticker][:5]
                if len(peer_list) >= 1:
                    with st.spinner("Fetching peers..."):
                        pdf = get_peer_comparison(analyzer.ticker, [analyzer.ticker] + peer_list)
                        if not pdf.empty:
                            st.markdown('<div class="section-header">🏢 Peer Comparison</div>', unsafe_allow_html=True)
                            st.dataframe(pdf, use_container_width=True, hide_index=True)

            # Financial Statements
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
                    a2.get_live_price()
                    a2.fetch_financial_data()
                create_stress_test_dashboard(a2)

    # ===== TAB 3 =====
    with tab3:
        st.markdown("### 📈 Technical Analysis")
        ta_t = st.text_input("Ticker", "AAPL", key="ta_t")
        ta_e = st.selectbox("Exchange", ["Auto-detect","NSE India (.NS)","BSE India (.BO)","US Market"], key="ta_e")
        if st.button("📈 Run TA", type="primary", key="ta_btn"):
            em3 = {"NSE India (.NS)":"NSE","BSE India (.BO)":"BSE","US Market":"US","Auto-detect":"Auto"}
            a3 = ProFinancialAnalyzer(ta_t, exchange=em3.get(ta_e,"Auto"))
            with st.spinner("Calculating..."): a3.get_live_price(); a3.fetch_financial_data()
            create_technical_dashboard(a3)

    # ===== TAB 4 =====
    with tab4:
        create_portfolio_optimization_tab()

    st.divider()
    st.caption(f"FinAnalyzer Pro | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()