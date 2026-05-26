"""
Stock Analysis Crew — Streamlit UI

A beautiful, interactive interface for the multi-agent stock analysis system.
Run with: streamlit run src/stock_analysis_crew/ui/app.py
"""

import sys
import time
from pathlib import Path

import streamlit as st

# Add src directory to path so imports work when running via streamlit
src_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(src_path))

from stock_analysis_crew.crews.analysis_crew.analysis_crew import AnalysisCrew
from stock_analysis_crew.utils.validators import validate_symbol
from stock_analysis_crew.utils.disclaimer import DISCLAIMER, DISCLAIMER_SHORT

# ── Page Config ──────────────────────────────────────────

st.set_page_config(
    page_title="Stock Analysis Crew",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────

st.markdown("""
<style>
    /* Main theme */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Agent status cards */
    .agent-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .agent-card-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ffd700;
    }
    .agent-card-done {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #10b981;
    }

    /* Stock input styling */
    .stock-input-container {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }

    /* Disclaimer box */
    .disclaimer-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 0.85rem;
        color: #856404;
    }

    /* Report section */
    .report-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: white;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.divider()

    # Analysis Type
    analysis_type = st.selectbox(
        "📋 Analysis Type",
        options=["Detailed Analysis", "Quick Analysis", "Technical Only", "Fundamental Only"],
        index=0,
        help="Choose the depth of analysis",
    )

    # Time Period
    period = st.selectbox(
        "📅 Time Period",
        options=["1 Month", "3 Months", "6 Months", "1 Year", "2 Years"],
        index=3,
        help="Historical data period for technical analysis",
    )

    period_map = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
    }

    st.divider()

    # Popular stocks quick select
    st.markdown("### 🇮🇳 Popular Indian Stocks")
    popular_stocks = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "SBI": "SBIN.NS",
        "Wipro": "WIPRO.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Bharti Airtel": "BHARTIARTL.NS",
        "ITC": "ITC.NS",
    }

    selected_stock = st.selectbox(
        "Quick Select",
        options=[""] + list(popular_stocks.keys()),
        index=0,
        help="Select a popular stock or type your own below",
    )

    st.divider()
    st.markdown(f"⚠️ {DISCLAIMER_SHORT}")


# ── Main Content ──────────────────────────────────────────

st.markdown('<h1 class="main-header">📊 Stock Analysis Crew</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Multi-Agent AI Stock Analysis for Indian Markets — Powered by CrewAI</p>',
    unsafe_allow_html=True,
)

# ── Stock Input ──────────────────────────────────────────

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Pre-fill from sidebar selection
    default_symbol = popular_stocks.get(selected_stock, "") if selected_stock else ""

    symbol = st.text_input(
        "🔍 Enter Stock Symbol",
        value=default_symbol,
        placeholder="e.g., RELIANCE.NS, TCS.NS, INFY.NS",
        help="Enter an Indian stock symbol with .NS (NSE) or .BO (BSE) suffix",
    )

    analyze_button = st.button(
        "🚀 Generate Analysis Report",
        use_container_width=True,
        type="primary",
    )


# ── Agent Info Section ──────────────────────────────────

if not analyze_button:
    st.divider()
    st.markdown("### 🤖 Meet the Analysis Agents")

    agents_info = [
        ("📈", "Market Data Analyst", "Fetches current price, volume, market cap, and key metrics"),
        ("📉", "Technical Analyst", "Calculates SMA, RSI, MACD, and identifies trends"),
        ("📊", "Fundamental Analyst", "Reviews PE, EPS, ROE, debt, and financial health"),
        ("📰", "News Sentiment Analyst", "Searches recent news and classifies sentiment"),
        ("⚠️", "Risk Analyst", "Identifies valuation, market, sector, and regulatory risks"),
        ("📝", "Report Writer", "Combines all findings into a clear, educational report"),
    ]

    cols = st.columns(3)
    for i, (icon, name, desc) in enumerate(agents_info):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="agent-card">
                <h4>{icon} {name}</h4>
                <p style="font-size: 0.9rem; color: #4b5563;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


# ── Analysis Execution ──────────────────────────────────

if analyze_button:
    if not symbol:
        st.error("❌ Please enter a stock symbol (e.g., RELIANCE.NS)")
    else:
        symbol = symbol.strip().upper()

        # ── Validation ──
        with st.spinner(f"🔍 Validating {symbol}..."):
            is_valid, message = validate_symbol(symbol)

        if not is_valid:
            st.error(f"❌ {message}")
        else:
            st.success(f"✅ {message}")

            # ── Progress Display ──
            st.divider()
            st.markdown("### 🤖 Agent Progress")

            agents_list = [
                ("📈", "Market Data Analyst", "Fetching price & market data..."),
                ("📉", "Technical Analyst", "Calculating SMA, RSI, MACD..."),
                ("📊", "Fundamental Analyst", "Analyzing financial metrics..."),
                ("📰", "News Sentiment Analyst", "Searching & analyzing news..."),
                ("⚠️", "Risk Analyst", "Identifying investment risks..."),
                ("📝", "Report Writer", "Generating final report..."),
            ]

            # Create placeholders for agent status
            agent_placeholders = []
            for icon, name, desc in agents_list:
                ph = st.empty()
                ph.markdown(f"""
                <div class="agent-card">
                    <span>⏳ {icon} <strong>{name}</strong> — Waiting...</span>
                </div>
                """, unsafe_allow_html=True)
                agent_placeholders.append((ph, icon, name, desc))

            st.divider()
            report_placeholder = st.empty()

            # ── Run the Crew ──
            with st.spinner("🚀 Running Stock Analysis Crew..."):
                try:
                    # Simulate agent progress (CrewAI runs sequentially)
                    # We update the UI as we kick off the crew
                    for i, (ph, icon, name, desc) in enumerate(agent_placeholders):
                        ph.markdown(f"""
                        <div class="agent-card-active">
                            <span>🔄 {icon} <strong>{name}</strong> — {desc}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # Run the actual crew
                    result = (
                        AnalysisCrew()
                        .crew()
                        .kickoff(inputs={"symbol": symbol})
                    )

                    # Mark all agents as done
                    for ph, icon, name, desc in agent_placeholders:
                        ph.markdown(f"""
                        <div class="agent-card-done">
                            <span>✅ {icon} <strong>{name}</strong> — Completed</span>
                        </div>
                        """, unsafe_allow_html=True)

                    report = result.raw

                    # Append disclaimer
                    if "Disclaimer" not in report:
                        report += f"\n\n{DISCLAIMER}"

                    # Save report
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    output_path = output_dir / "report.md"
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(report)

                    # ── Display Report ──
                    st.divider()
                    st.markdown("### 📄 Stock Analysis Report")

                    with st.container():
                        st.markdown(report)

                    # ── Download Button ──
                    st.divider()
                    col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                    with col_d2:
                        st.download_button(
                            label="📥 Download Report (Markdown)",
                            data=report,
                            file_name=f"stock_analysis_{symbol.replace('.', '_')}.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                    st.success(f"✅ Report saved to `{output_path}`")

                except Exception as e:
                    # Mark remaining agents as failed
                    for ph, icon, name, desc in agent_placeholders:
                        ph.markdown(f"""
                        <div class="agent-card">
                            <span>❌ {icon} <strong>{name}</strong> — Error</span>
                        </div>
                        """, unsafe_allow_html=True)

                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("💡 Please check your API keys in the `.env` file and try again.")


# ── Footer ──────────────────────────────────────────

st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #9ca3af; font-size: 0.85rem;">
        <p>
            <strong>Stock Analysis Crew</strong> — Built with 
            <a href="https://crewai.com" target="_blank">CrewAI</a> | 
            <a href="https://streamlit.io" target="_blank">Streamlit</a> | 
            <a href="https://pypi.org/project/yfinance/" target="_blank">yfinance</a>
        </p>
        <p>⚠️ For educational and research purposes only. Not financial advice.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
