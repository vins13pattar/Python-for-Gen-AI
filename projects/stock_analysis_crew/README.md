# 📊 Stock Analysis Crew

> Multi-Agent AI Stock Analysis for Indian Markets — Powered by CrewAI

Stock Analysis Crew is a multi-agent AI application that analyzes Indian stocks using market data, fundamentals, news sentiment, and technical indicators, then generates an easy-to-understand stock analysis report.

## 🤖 Architecture

This project uses **CrewAI Flow + Crew** architecture:

```
StockAnalysisFlow (Flow)
    └── AnalysisCrew (Sequential Crew)
            ├── 📈 Market Data Analyst    → StockPriceTool (yfinance)
            ├── 📉 Technical Analyst      → TechnicalIndicatorTool (pandas-ta)
            ├── 📊 Fundamental Analyst    → FinancialMetricsTool (yfinance)
            ├── 📰 News Sentiment Analyst → NewsSearchTool + SerperDevTool
            ├── ⚠️  Risk Analyst           → (uses context from prior agents)
            └── 📝 Report Writer          → (generates final markdown report)
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- [CrewAI CLI](https://docs.crewai.com/) installed
- OpenAI API key
- Serper API key (for news search)

### 2. Setup

```bash
cd stock_analysis_crew

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add your keys:
#   OPENAI_API_KEY=your_openai_key
#   OPENAI_MODEL_NAME=gpt-5.5
#   SERPER_API_KEY=your_serper_key

# Install dependencies
crewai install
```

### 3. Run via CLI

```bash
crewai run
# Enter stock symbol when prompted: RELIANCE.NS
```

### 4. Run via Streamlit UI

```bash
streamlit run src/stock_analysis_crew/ui/app.py
```

## 📁 Project Structure

```
stock_analysis_crew/
├── .env                          # API keys (not committed)
├── pyproject.toml                # Dependencies & project config
├── README.md
│
├── docs/
│   └── PRD.md                    # Product Requirements Document
│
├── src/stock_analysis_crew/
│   ├── main.py                   # Flow orchestration
│   │
│   ├── crews/analysis_crew/
│   │   ├── config/
│   │   │   ├── agents.yaml       # 6 agent definitions
│   │   │   └── tasks.yaml        # 6 task definitions
│   │   └── analysis_crew.py      # @CrewBase crew class
│   │
│   ├── tools/
│   │   ├── stock_price_tool.py         # yfinance price data
│   │   ├── technical_indicator_tool.py # SMA, RSI, MACD
│   │   ├── financial_metrics_tool.py   # PE, EPS, ROE, etc.
│   │   └── news_search_tool.py         # News headlines
│   │
│   ├── utils/
│   │   ├── validators.py         # Symbol validation
│   │   ├── formatter.py          # Indian number formatting
│   │   └── disclaimer.py         # SEBI compliance text
│   │
│   └── ui/
│       └── app.py                # Streamlit interface
│
└── output/
    └── report.md                 # Generated reports
```

## 🇮🇳 Supported Stock Symbols

Enter NSE stocks with `.NS` suffix:

| Symbol         | Company              |
| -------------- | -------------------- |
| RELIANCE.NS    | Reliance Industries  |
| TCS.NS         | Tata Consultancy     |
| INFY.NS        | Infosys              |
| HDFCBANK.NS    | HDFC Bank            |
| ICICIBANK.NS   | ICICI Bank           |
| SBIN.NS        | State Bank of India  |
| TATAMOTORS.NS  | Tata Motors          |
| BHARTIARTL.NS  | Bharti Airtel        |
| ITC.NS         | ITC Limited          |
| WIPRO.NS       | Wipro                |

BSE stocks use `.BO` suffix (e.g., `RELIANCE.BO`).

## 📊 Sample Report Output

The system generates a structured report with:

1. **Stock Overview** — Company description and market position
2. **Market Data Summary** — Price, volume, market cap in ₹
3. **Technical Analysis** — SMA, RSI, MACD signals explained simply
4. **Fundamental Analysis** — Financial health in plain language
5. **News Sentiment** — Recent headlines with sentiment classification
6. **Key Risks** — Risk factors rated High/Medium/Low
7. **Educational View** — Balanced assessment (not financial advice)
8. **Disclaimer** — SEBI compliance notice

## ⚠️ Disclaimer

This application is for **educational and research purposes only**.
It does not provide financial, investment, trading, or legal advice.
Please consult a **SEBI-registered investment advisor** before making investment decisions.

## 📚 Tech Stack

| Component            | Technology                |
| -------------------- | ------------------------- |
| Agent Framework      | CrewAI (Flow + Crew)      |
| Language             | Python 3.10+              |
| UI                   | Streamlit                 |
| Stock Data           | yfinance                  |
| News Search          | SerperDevTool (SerpAPI)   |
| Technical Indicators | pandas-ta                 |
| LLM                  | OpenAI gpt-5.5            |

## 📖 Documentation

- [PRD — Product Requirements Document](docs/PRD.md)
