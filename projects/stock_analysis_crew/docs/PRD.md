# PRD: Stock Analysis Crew — Indian Stocks Mini Project

## 1. Product Overview

**Product Name:** Stock Analysis Crew
**Type:** Mini Project / Learning Project
**Target Market:** Indian stock market learners, beginner investors, finance students, developers learning CrewAI
**Core Technology:** Python, CrewAI, LLM APIs, stock market data APIs, Streamlit/FastAPI

**One-line Description:**
Stock Analysis Crew is a multi-agent AI application that analyzes Indian stocks using market data, fundamentals, news sentiment, and technical indicators, then generates an easy-to-understand stock analysis report.

CrewAI is suitable for this project because it supports autonomous agents, task delegation, tools, memory, and collaborative workflows through "crews" of agents. ([CrewAI Documentation][1]) A CrewAI crew represents a group of agents working together to complete a set of tasks. ([CrewAI Documentation][2])

---

## 1.1 Confirmed Architectural Decisions

The following decisions have been finalized during the planning phase:

| Decision                  | Choice                                                                                             |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| **LLM Provider & Model**  | OpenAI `gpt-5.5` via `OPENAI_API_KEY`                                                             |
| **News Data Source**      | SerpAPI via CrewAI's `SerperDevTool` using `SERPER_API_KEY`                                        |
| **Crew Architecture**     | Single sequential `Crew` (6 agents) wrapped in a CrewAI `Flow` for state management and routing   |
| **Report Output**         | Auto-saved to `output/report.md` after every analysis run                                          |
| **Streamlit UI**          | Included in MVP (built alongside the core, not deferred)                                           |
| **Project Scaffold**      | Created via `crewai create flow stock_analysis_crew` (CLI-first, underscore naming)                |

---

## 2. Problem Statement

Retail investors and students often find it difficult to analyze Indian stocks because data is scattered across multiple sources:

| Problem                     | Explanation                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| Too much information        | Price data, financial ratios, news, market sentiment, and charts are available separately. |
| Lack of structured analysis | Beginners do not know how to combine technical, fundamental, and sentiment analysis.       |
| Time-consuming research     | Manually checking NSE/BSE data, news, and company details takes time.                      |
| No guided explanation       | Most platforms show numbers but do not explain what they mean in simple language.          |

---

## 3. Goal

Build a mini AI-powered stock analysis app where the user enters an Indian stock symbol such as:

```text
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
TATAMOTORS.NS
```

The app should return a structured stock analysis report containing:

1. Stock overview
2. Current/latest available market data
3. Technical indicator summary
4. Fundamental summary
5. Recent news sentiment
6. Risk factors
7. Final AI-generated explanation
8. Educational "Buy / Hold / Avoid style" view without giving financial advice

Yahoo Finance commonly represents NSE stocks with `.NS` suffix and BSE stocks with `.BO` suffix; for example, Yahoo Finance lists NIFTY 50 components such as `MARUTI.NS`, `ADANIENT.NS`, and `AXISBANK.NS`. ([Yahoo Finance][3]) For real-time NSE data, official or authorized paid data feeds may be required; NSE provides real-time data feeds through subscription models. ([NSE India][4])

---

## 4. Non-Goals

This project will **not**:

| Non-Goal                                   | Reason                                                             |
| ------------------------------------------ | ------------------------------------------------------------------ |
| Execute trades                             | It is an analysis and learning tool, not a trading platform.       |
| Provide guaranteed stock recommendations   | The output should be educational, not investment advice.           |
| Support intraday trading automation        | Real-time market feeds need licensed data and stronger compliance. |
| Predict future price with certainty        | The system can explain probabilities and signals, not guarantees.  |
| Replace SEBI-registered financial advisors | The app must include a financial disclaimer.                       |

---

## 5. Target Users

| User Type          | Need                                                     |
| ------------------ | -------------------------------------------------------- |
| Beginner investor  | Wants simple explanation of a stock.                     |
| Finance student    | Wants to learn stock analysis structure.                 |
| Developer          | Wants to learn CrewAI with a practical finance use case. |
| Trainer / educator | Wants to demonstrate AI agents with real-world data.     |
| Small investor     | Wants quick research before deeper manual analysis.      |

---

## 6. User Persona

### Persona 1: Beginner Investor

**Name:** Ravi
**Age:** 28
**Goal:** Understand whether a stock looks strong or weak.
**Pain Point:** Does not understand financial ratios and technical indicators.
**Expected Output:** Simple explanation like: "The stock is showing medium-term strength, but valuation is expensive."

### Persona 2: AI/ML Learner

**Name:** Sneha
**Age:** 24
**Goal:** Learn how multiple AI agents collaborate.
**Pain Point:** Knows Python basics but has not built agentic apps.
**Expected Output:** Clear CrewAI project with agents, tools, and tasks.

---

## 7. Key Features

## 7.1 Stock Input

The user should be able to enter:

```text
RELIANCE.NS
TCS.NS
INFY.NS
SBIN.NS
HDFCBANK.NS
```

Optional future support:

```text
RELIANCE.BO
NIFTY 50
BANKNIFTY
```

### Acceptance Criteria

| ID   | Criteria                                        |
| ---- | ----------------------------------------------- |
| AC-1 | User can enter a valid NSE stock symbol.        |
| AC-2 | App validates empty or invalid input.           |
| AC-3 | App shows a clear error if data is unavailable. |

---

## 7.2 Market Data Fetching

The system should fetch:

| Data Point                     | Example         |
| ------------------------------ | --------------- |
| Current/latest available price | ₹2,850          |
| Previous close                 | ₹2,810          |
| Day high / low                 | ₹2,880 / ₹2,795 |
| 52-week high / low             | ₹3,020 / ₹2,220 |
| Volume                         | 45,00,000       |
| Market cap                     | ₹19 lakh crore  |
| PE ratio                       | 28.5            |
| Dividend yield                 | 0.4%            |

### Suggested Data Sources

| Source                         | Use Case                               | Notes                                                                                 |
| ------------------------------ | -------------------------------------- | ------------------------------------------------------------------------------------- |
| Yahoo Finance / yfinance       | Mini project and learning              | Good for educational prototype.                                                       |
| NSE official data subscription | Production-grade real-time market data | NSE real-time data is subscription-based. ([NSE India][4])                            |
| TrueData / authorized vendors  | Real-time NSE/BSE feeds                | TrueData offers APIs for NSE, BSE, MCX, options, and historical data. ([TrueData][5]) |

---

## 7.3 Technical Analysis

The system should calculate technical indicators.

| Indicator            | Purpose                      |
| -------------------- | ---------------------------- |
| SMA 20               | Short-term trend             |
| SMA 50               | Medium-term trend            |
| SMA 200              | Long-term trend              |
| RSI 14               | Overbought / oversold signal |
| MACD                 | Momentum                     |
| Volume trend         | Participation strength       |
| Support / resistance | Important price zones        |

### Example Output

```text
Technical View:
The stock is trading above its 50-day moving average, which indicates medium-term strength.
RSI is 62, meaning the stock is strong but not yet heavily overbought.
Volume is slightly above average, showing decent participation.
```

---

## 7.4 Fundamental Analysis

The system should analyze company fundamentals.

| Metric         | Interpretation          |
| -------------- | ----------------------- |
| PE Ratio       | Valuation               |
| EPS            | Profitability per share |
| Revenue growth | Business growth         |
| Profit growth  | Earnings quality        |
| Debt-to-equity | Financial risk          |
| ROE            | Efficiency              |
| Dividend yield | Income potential        |
| Market cap     | Company size            |

### Example Output

```text
Fundamental View:
The company has strong profitability and stable revenue growth.
However, the PE ratio is higher than the sector average, which may indicate expensive valuation.
```

---

## 7.5 News Sentiment Analysis

The system should collect recent news headlines and summarize sentiment.

| Sentiment | Meaning                                                   |
| --------- | --------------------------------------------------------- |
| Positive  | Good earnings, expansion, order wins, analyst upgrades    |
| Neutral   | Routine announcements                                     |
| Negative  | Regulatory issue, weak results, downgrades, debt concerns |

### Example Output

```text
News Sentiment:
Recent news sentiment is mildly positive due to strong quarterly performance and sector momentum.
No major negative event was found in recent headlines.
```

---

## 7.6 AI Agent-Based Report Generation

The final report should be generated by multiple CrewAI agents.

### Proposed CrewAI Agents

| Agent                  | Responsibility                                              |
| ---------------------- | ----------------------------------------------------------- |
| Market Data Analyst    | Fetches stock price, volume, and basic market data.         |
| Technical Analyst      | Calculates indicators like SMA, RSI, MACD.                  |
| Fundamental Analyst    | Reviews valuation, profitability, and financial ratios.     |
| News Sentiment Analyst | Reads recent news and classifies sentiment.                 |
| Risk Analyst           | Identifies financial, market, sector, and news-based risks. |
| Report Writer          | Combines all findings into a simple final report.           |

CrewAI agents are autonomous units that can perform tasks, make decisions, use tools, and collaborate. ([CrewAI Documentation][1])

---

## 8. User Flow

```text
User opens app
        ↓
User enters stock symbol: RELIANCE.NS
        ↓
System validates symbol
        ↓
Market Data Agent fetches price data
        ↓
Technical Analyst calculates indicators
        ↓
Fundamental Analyst analyzes ratios
        ↓
News Agent summarizes sentiment
        ↓
Risk Agent identifies key risks
        ↓
Report Writer generates final report
        ↓
User views/downloads report
```

---

## 9. Screens

## 9.1 Home / Input Screen

### Fields

| Field                  | Type       | Required |
| ---------------------- | ---------- | -------- |
| Stock Symbol           | Text input | Yes      |
| Analysis Type          | Dropdown   | Optional |
| Time Period            | Dropdown   | Optional |
| Generate Report Button | Button     | Yes      |

### Example Options

```text
Analysis Type:
- Quick Analysis
- Detailed Analysis
- Technical Only
- Fundamental Only

Time Period:
- 1 Month
- 3 Months
- 6 Months
- 1 Year
```

---

## 9.2 Loading / Agent Progress Screen

Show agent progress:

```text
✅ Market Data Agent completed
✅ Technical Analyst completed
⏳ Fundamental Analyst running
⏳ News Sentiment Analyst running
```

---

## 9.3 Final Report Screen

Sections:

| Section              | Description                      |
| -------------------- | -------------------------------- |
| Stock Summary        | Basic company and price overview |
| Technical Analysis   | Indicators and trend             |
| Fundamental Analysis | Financial health                 |
| News Sentiment       | Recent news summary              |
| Risk Analysis        | Key risks                        |
| Final View           | Educational conclusion           |
| Disclaimer           | Not financial advice             |

---

## 10. Functional Requirements

| ID    | Requirement                                 | Priority |
| ----- | ------------------------------------------- | -------- |
| FR-1  | User can enter Indian stock symbol.         | High     |
| FR-2  | System validates stock symbol.              | High     |
| FR-3  | System fetches latest available price data. | High     |
| FR-4  | System calculates SMA, RSI, MACD.           | High     |
| FR-5  | System fetches basic financial metrics.     | Medium   |
| FR-6  | System fetches recent news headlines.       | Medium   |
| FR-7  | System performs sentiment analysis.         | Medium   |
| FR-8  | System generates final AI report.           | High     |
| FR-9  | User can download report as Markdown/PDF.   | Low      |
| FR-10 | System shows disclaimer.                    | High     |

---

## 11. Non-Functional Requirements

| Category        | Requirement                                                   |
| --------------- | ------------------------------------------------------------- |
| Performance     | Report should generate within 30–60 seconds for mini project. |
| Usability       | Beginner-friendly language.                                   |
| Reliability     | Handle missing data gracefully.                               |
| Security        | Store API keys in `.env`, not in code.                        |
| Compliance      | Must show "Not financial advice" disclaimer.                  |
| Scalability     | Architecture should allow adding more agents later.           |
| Maintainability | Agents, tasks, and tools should be separated cleanly.         |

---

## 12. Tech Stack (Confirmed)

| Layer                | Technology                                                  | Status    |
| -------------------- | ----------------------------------------------------------- | --------- |
| Agent Framework      | CrewAI (Flow + sequential Crew)                             | Confirmed |
| Language             | Python 3.10+                                                | Confirmed |
| UI                   | Streamlit (included in MVP)                                 | Confirmed |
| API Backend          | FastAPI — optional, not in MVP                              | Deferred  |
| Stock Data           | yfinance                                                    | Confirmed |
| News Data            | SerpAPI via `SerperDevTool` (`SERPER_API_KEY`)              | Confirmed |
| Charts               | Plotly / Matplotlib                                         | Confirmed |
| Technical Indicators | pandas, pandas-ta                                           | Confirmed |
| LLM                  | OpenAI `gpt-5.5` (`OPENAI_API_KEY`)                         | Confirmed |
| Config               | python-dotenv / `.env`                                      | Confirmed |
| Report Export        | Markdown (auto-saved to `output/report.md`)                 | Confirmed |

---

## 13. CrewAI Project Structure

```text
stock_analysis_crew/
│
├── .env
├── README.md
├── pyproject.toml
│
├── docs/
│   └── PRD.md
│
├── src/
│   └── stock_analysis_crew/
│       ├── __init__.py
│       ├── main.py                         # Flow class with @start/@listen
│       │
│       ├── crews/
│       │   └── analysis_crew/
│       │       ├── config/
│       │       │   ├── agents.yaml         # Agent definitions
│       │       │   └── tasks.yaml          # Task definitions
│       │       └── analysis_crew.py        # Crew class with @CrewBase
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── stock_price_tool.py         # yfinance price data fetcher
│       │   ├── technical_indicator_tool.py # SMA, RSI, MACD calculator
│       │   ├── financial_metrics_tool.py   # Fundamental data fetcher
│       │   └── news_search_tool.py         # News headline fetcher
│       │
│       ├── utils/
│       │   ├── validators.py               # Stock symbol validation
│       │   ├── formatter.py                # Report formatting helpers
│       │   └── disclaimer.py               # Financial disclaimer text
│       │
│       └── ui/
│           └── app.py                      # Streamlit UI
│
└── output/
    └── report.md                           # Generated reports
```

---

## 14. Agent Design

## 14.1 Market Data Agent

| Field  | Description                                            |
| ------ | ------------------------------------------------------ |
| Role   | Indian Stock Market Data Analyst                       |
| Goal   | Fetch latest available market data for the given stock |
| Tools  | Stock price tool, yfinance tool                        |
| Output | Structured market data JSON                            |

### Output Example

```json
{
  "symbol": "RELIANCE.NS",
  "current_price": 2850,
  "previous_close": 2810,
  "day_high": 2880,
  "day_low": 2795,
  "volume": 4500000
}
```

---

## 14.2 Technical Analyst Agent

| Field  | Description                          |
| ------ | ------------------------------------ |
| Role   | Technical Analysis Expert            |
| Goal   | Analyze price trend using indicators |
| Tools  | Technical indicator calculator       |
| Output | Technical summary                    |

### Output Example

```json
{
  "trend": "Bullish",
  "rsi": 62,
  "sma_50_signal": "Price above SMA 50",
  "macd_signal": "Positive momentum"
}
```

---

## 14.3 Fundamental Analyst Agent

| Field  | Description                                      |
| ------ | ------------------------------------------------ |
| Role   | Fundamental Equity Analyst                       |
| Goal   | Analyze company valuation and financial strength |
| Tools  | Financial metrics tool                           |
| Output | Fundamental summary                              |

---

## 14.4 News Sentiment Agent

| Field  | Description                                     |
| ------ | ----------------------------------------------- |
| Role   | Market News Researcher                          |
| Goal   | Analyze recent news and classify sentiment      |
| Tools  | News search tool                                |
| Output | Positive / Neutral / Negative sentiment summary |

---

## 14.5 Risk Analyst Agent

| Field  | Description                               |
| ------ | ----------------------------------------- |
| Role   | Risk Analyst                              |
| Goal   | Identify major risks related to the stock |
| Output | Risk factors                              |

Risk categories:

```text
- Valuation risk
- Market risk
- Sector risk
- Regulatory risk
- Debt risk
- News/event risk
```

---

## 14.6 Report Writer Agent

| Field  | Description                                 |
| ------ | ------------------------------------------- |
| Role   | Investment Research Report Writer           |
| Goal   | Convert agent findings into a simple report |
| Output | Final Markdown report                       |

---

## 15. Sample Final Report Format

```markdown
# Stock Analysis Report: RELIANCE.NS

## 1. Stock Overview
Reliance Industries is one of India's largest companies with businesses across energy, telecom, retail, and digital services.

## 2. Market Data Summary
- Current Price: ₹XXXX
- Previous Close: ₹XXXX
- 52-Week High: ₹XXXX
- 52-Week Low: ₹XXXX
- Volume: XX,XX,XXX

## 3. Technical Analysis
The stock is trading above its 50-day moving average, showing medium-term strength.
RSI is in a healthy range and does not indicate extreme overbought conditions.

## 4. Fundamental Analysis
The company has strong business diversification and large market capitalization.
Valuation should be compared with sector peers before making investment decisions.

## 5. News Sentiment
Recent news sentiment appears neutral to mildly positive.

## 6. Key Risks
- High valuation risk
- Market volatility
- Sector-specific regulatory changes
- Global crude oil price dependency

## 7. Educational View
Based on available data, the stock appears fundamentally strong but should be studied further before investing.

## Disclaimer
This report is generated for educational purposes only. It is not financial advice.
Please consult a SEBI-registered financial advisor before making investment decisions.
```

---

## 16. Data Model

### Stock Analysis Request

```json
{
  "symbol": "RELIANCE.NS",
  "analysis_type": "detailed",
  "period": "1y"
}
```

### Stock Analysis Response

```json
{
  "symbol": "RELIANCE.NS",
  "market_data": {},
  "technical_analysis": {},
  "fundamental_analysis": {},
  "news_sentiment": {},
  "risk_analysis": {},
  "final_report": "markdown text"
}
```

---

## 17. Validation Rules

| Rule                                  | Example                               |
| ------------------------------------- | ------------------------------------- |
| Symbol cannot be empty                | Reject empty input                    |
| NSE symbol should end with `.NS`      | `TCS.NS`                              |
| BSE symbol should end with `.BO`      | `TCS.BO`                              |
| Unsupported symbols should show error | "No data found for this symbol"       |
| Minimum historical data required      | At least 200 trading days for SMA 200 |

---

## 18. Error Handling

| Scenario         | Message                                                           |
| ---------------- | ----------------------------------------------------------------- |
| Invalid symbol   | "Please enter a valid Indian stock symbol like RELIANCE.NS."      |
| Data not found   | "No market data found for this stock."                            |
| API failure      | "Unable to fetch stock data right now. Please try again."         |
| News unavailable | "News sentiment could not be generated due to missing news data." |
| LLM failure      | "AI report generation failed. Please retry."                      |

---

## 19. MVP Scope

### Must-Have

| Feature                        | Included |
| ------------------------------ | -------- |
| Stock symbol input             | Yes      |
| Price data fetching            | Yes      |
| Technical indicators           | Yes      |
| Basic fundamentals             | Yes      |
| Live news search (SerpAPI)     | Yes      |
| AI-generated report            | Yes      |
| Streamlit UI                   | Yes      |
| Auto-save to `output/report.md`| Yes      |
| Disclaimer                     | Yes      |

### Good-to-Have

| Feature                  | Included Later |
| ------------------------ | -------------- |
| PDF export               | Later          |
| Watchlist                | Later          |
| Portfolio analysis       | Later          |
| Peer comparison          | Later          |
| Real-time WebSocket feed | Later          |
| User login               | Later          |

---

## 20. Future Enhancements

| Enhancement             | Description                                        |
| ----------------------- | -------------------------------------------------- |
| Portfolio Analyzer      | Analyze multiple stocks together.                  |
| Peer Comparison         | Compare TCS vs Infosys, HDFC Bank vs ICICI Bank.   |
| Sector Analysis         | Analyze banking, IT, auto, pharma sectors.         |
| Watchlist               | Save favorite stocks.                              |
| Alerts                  | Price or RSI-based alerts.                         |
| Backtesting             | Test simple strategies.                            |
| PDF Report              | Download professional stock report.                |
| Indian Language Support | Kannada/Hindi stock explanations.                  |
| Voice Assistant         | Ask: "Analyze Reliance stock."                     |
| Broker Integration      | Only for future advanced version, with compliance. |

---

## 21. Success Metrics

| Metric                         | Target                             |
| ------------------------------ | ---------------------------------- |
| Report generation success rate | 95%+                               |
| Average report generation time | Under 60 seconds                   |
| User understands report        | Beginner-friendly output           |
| Invalid symbol handling        | 100% graceful                      |
| Technical indicator accuracy   | Matches calculation library output |
| Agent output completeness      | All report sections generated      |

---

## 22. Risks and Mitigations

| Risk                                          | Mitigation                                       |
| --------------------------------------------- | ------------------------------------------------ |
| Free data source may be delayed or unreliable | Add fallback data provider.                      |
| Real-time data licensing issue                | Use educational delayed data in MVP.             |
| LLM hallucination                             | Force agents to use structured data only.        |
| Incorrect financial advice                    | Add disclaimer and avoid direct recommendations. |
| API rate limits                               | Add caching and retries.                         |
| Missing fundamentals                          | Show partial report with warning.                |

---

## 23. Compliance and Disclaimer Requirement

The app must clearly show:

```text
This application is for educational and research purposes only.
It does not provide financial, investment, trading, or legal advice.
Please consult a SEBI-registered investment advisor before making investment decisions.
```

This is especially important because Indian stock market analysis can influence financial decisions.

---

## 24. Recommended Mini Project Build Phases

All phases are included in the MVP build (Streamlit UI is not deferred).

| Phase   | Duration | Output                                                             |
| ------- | -------: | ------------------------------------------------------------------ |
| Phase 1 |    1 day | Project config, dependencies, `.env` setup                         |
| Phase 2 |    1 day | Custom tools: stock_price, technical_indicator, financial_metrics   |
| Phase 3 |    1 day | CrewAI agents (6) + tasks (6) with YAML config                     |
| Phase 4 |    1 day | Flow orchestration (`StockAnalysisFlow`) + validation utilities     |
| Phase 5 |    1 day | News search tool (SerpAPI) + risk analysis integration              |
| Phase 6 |    1 day | Streamlit UI + report display + download + agent progress tracking |

---

## 25. Final MVP Definition

The MVP is complete when:

```text
A user opens the Streamlit UI,
enters RELIANCE.NS, TCS.NS, or INFY.NS,
the app validates the symbol,
fetches stock data via yfinance,
searches recent news via SerpAPI,
runs 6 CrewAI agents in a sequential Crew wrapped in a Flow,
generates a structured educational stock analysis report
with market data, technical analysis, fundamentals, sentiment, risks, and disclaimer,
auto-saves the report to output/report.md,
and displays it in the Streamlit UI with download option.
```

---

## 26. Suggested Demo Script

```text
Today we are demonstrating Stock Analysis Crew, a multi-agent AI app built using CrewAI.

Instead of one AI model giving a direct answer, we divide the work among multiple expert agents.

One agent collects market data.
Another agent performs technical analysis.
Another checks fundamentals.
Another reads recent news.
A risk analyst identifies possible concerns.
Finally, a report writer combines everything into a simple stock analysis report.

Let us enter RELIANCE.NS and generate the report.

The system now shows price data, technical signals, financial summary, news sentiment, and risk factors.

This project is useful for learning AI agents, stock market research workflows, and practical Python automation.
```

[1]: https://docs.crewai.com/en/concepts/agents "Agents"
[2]: https://docs.crewai.com/en/concepts/crews "Crews"
[3]: https://finance.yahoo.com/quote/%5ENSEI/components/ "NIFTY 50 (^NSEI) Components"
[4]: https://www.nseindia.com/static/market-data/real-time-data-subscription "Paid Real time data"
[5]: https://www.truedata.in/products/marketdataapi "Real-Time Market Data API for NSE, BSE & MCX"
