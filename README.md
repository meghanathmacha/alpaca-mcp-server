# Alpaca MCP Server

This is a Model Context Protocol (MCP) server implementation for Alpaca's Trading API. It enables large language models (LLMs) on Claude Desktop, Cursor, or VScode to interact with Alpaca's trading infrastructure using natural language (English). This server supports stock trading, options trading, portfolio management, watchlist handling, and real-time market data access.

## Features

- **Market Data**
  - Real-time quotes, trades, and price bars for stocks
  - Historical price data and trading history
  - Option contract quotes and Greeks (via snapshots)
- **Account Management**
  - View balances, buying power, and account status
  - Inspect all open and closed positions
- **Position Management**
  - Get detailed info on individual holdings
  - Liquidate all or partial positions by share count or percentage
- **Order Management**
  - Place stock and option orders (market or limit)
  - Cancel orders individually or in bulk
  - Retrieve full order history
- **Options Trading**
  - Search and view option contracts by expiration or strike price
  - Place multi-leg options strategies
  - Get latest quotes and Greeks for contracts
- **Market Status & Corporate Actions**
  - Check if markets are open
  - Fetch market calendar and trading sessions
  - View upcoming corporate announcements (earnings, splits, dividends)
- **Watchlist Management**
  - Create, update, and view personal watchlists
  - Manage multiple watchlists for tracking assets
- **Asset Search**
  - Query details for stocks and other Alpaca-supported assets

## 🚀 Quick Start - Direct Terminal Trading

**NEW**: You can now trade directly from the terminal without needing MCP/Claude Desktop!

### One-Time Setup
```bash
# Clone and enter directory
git clone https://github.com/alpacahq/alpaca-mcp-server.git
cd alpaca-mcp-server

# Install dependencies using uv (recommended)
pip install uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Copy environment template and add your API keys
cp .env.example .env
# Edit .env with your Alpaca paper trading API credentials

# Optional: Setup 'trade' command for easy access
./setup_alias.sh
```

### Start Trading (Every Session)
```bash
# Option 1: Quick command (if you ran setup_alias.sh)
trade

# Option 2: Manual start
./start_trading.sh

# Option 3: Direct Python
python trading_session.py
```

### Example Trading Session
```python
# Find SPY options under $5
await session.scan_options(max_price=5.0)

# Buy an option with auto-limit pricing
await session.quick_buy('SPY250620C00596000')

# Check order status
await session.check_orders()

# Account status
await session.status()
```

See [TRADING_GUIDE.md](TRADING_GUIDE.md) for complete trading commands and strategies.

### Claude Code Integration (MCP)
This repository includes `.mcp.json` configuration for Claude Code users:

```bash
# Navigate to the repository in Claude Code
cd /path/to/alpaca-mcp-server

# Claude Code will automatically discover and connect to the MCP server
# You'll have access to all 26 Alpaca trading tools directly in chat
```

**Available MCP Tools:** Account management, market data, options trading, risk management, and order execution - all integrated into your Claude Code workflow for seamless trading assistance.

---

## Prerequisites (MCP/Claude Desktop Usage)

- Python 3.10+
- Github account
- Alpaca API keys (with paper or live trading access)
- Claude for Desktop or another compatible MCP client

## Installation

1. Clone the repository and move to the repository:
   ```bash
   git clone https://github.com/alpacahq/alpaca-mcp-server.git
   cd alpaca-mcp-server
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
    **Note:** The virtual environment will use the Python version that was used to create it. If you run the command with Python 3.10 or newer, your virtual environment will also use Python 3.10+. If you want to confirm the version, you can run `python3 --version` after activating the virtual environment. 

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


## Project Structure

After cloning and activating the virtual environment, your directory structure should look like this:
```
alpaca-mcp-server/          ← This is the workspace folder (= project root)
├── alpaca_mcp_server.py    ← Script is directly in workspace root
├── .vscode/                ← VS Code settings (for VS Code users)
│   └── mcp.json
├── venv/                   ← Virtual environment folder
│   └── bin/python
├── .env.example            ← Environment template (use this to create .env file)
├── .gitignore              
├── Dockerfile              ← Docker configuration (for Docker use)
├── .dockerignore           ← Docker ignore (for Docker use)
├── requirements.txt           
└── README.md
```

## Create and edit a .env file for your credentials in the project directory

   ```
   ALPACA_API_KEY = "your_alpaca_api_key"
   ALPACA_SECRET_KEY = "your_alpaca_secret_key"
   PAPER = True
   TRADE_API_URL = None
   TRDE_API_WSS = None
   DATA_API_URL = None
   STREAM_DATA_WSS = None
   ```

## Claude Desktop Usage

The official Claude Desktop setup document is available here: https://modelcontextprotocol.io/quickstart/user

### Start the MCP Server

Open a terminal in the project root directory and run the following command:

```bash
python alpaca_mcp_server.py # or `python -m alpaca_mcp_server`
```

### Claude for Desktop Configuration

1. Open Claude Desktop
2. Navigate to: `Settings → Developer → Edit Config`
3. Update your `claude_desktop_config.json`:

  **Note:**\
    Replace <project_root> with the path to your cloned alpaca-mcp-server directory. This should point to the Python executable inside the virtual environment you created with `python3 -m venv venv` on terminal.

```json
{
  "mcpServers": {
    "alpaca": {
      "command": "<project_root>/venv/bin/python",
      "args": [
        "/path/to/alpaca-mcp-server/alpaca_mcp_server.py"
      ],
      "env": {
        "ALPACA_API_KEY": "your_alpaca_api_key_for_paper_account",
        "ALPACA_SECRET_KEY": "your_alpaca_secret_key_for_paper_account"
      }
    }
  }
}
```
## VS Code Usage

VS Code supports MCP servers through GitHub Copilot's agent mode.
The official VS Code setup document is available here: https://code.visualstudio.com/docs/copilot/chat/mcp-servers

**Prerequisites**
- VS Code with GitHub Copilot extension installed and active subscription
- Python 3.10+ and virtual environment set up (follow Installation steps above)
- MCP support enabled in VS Code (see below)

### 1. Enable MCP Support in VS Code

1. Open VS Code Settings (Ctrl/Cmd + ,)
2. Search for "chat.mcp.enabled" to check the box to enable MCP support
3. Search for "github.copilot.chat.experimental.mcp" to check the box to use instruction files

### 2. Configure the MCP Server

**Recommendation:** Use **workspace-specific** configuration (`.vscode/mcp.json`) instead of user-wide configuration. This allows different projects to use different API keys (multiple paper accounts or live trading) and keeps trading tools isolated from other development work.

**For workspace-specific settings:**

1. Create `.vscode/mcp.json` in your project root.
2. Add the Alpaca MCP server configuration manually to mcp.json file:
    ```json
    {
      "alpaca": {
        "type": "stdio",
        "command": "${workspaceFolder}/venv/bin/python",
        "args": ["${workspaceFolder}/alpaca_mcp_server.py"],
        "env": {
          "ALPACA_API_KEY": "your_alpaca_api_key",
          "ALPACA_SECRET_KEY": "your_alpaca_secret_key",
        }
      }
    }
    ```
    **Note:** Replace the "command" parameter with "${workspaceFolder}\\venv\\Scripts\\python.exe", for Windows use

**For user-wide settings:**

To configure an MCP server for all your workspaces, you can add the server configuration to your user settings.json. This allows you to reuse the same server configuration across multiple projects.
Specify the server in the `mcp` VS Code user settings (`settings.json`) to enable the MCP server across all workspaces.
```json
{
  "mcp": {
    "servers": {
      "alpaca": {
        "type": "stdio",
        "command": "${workspaceFolder}/venv/bin/python",
        "args": ["${workspaceFolder}/alpaca_mcp_server.py"],
        "env": {
          "ALPACA_API_KEY": "your_alpaca_api_key",
          "ALPACA_SECRET_KEY": "your_alpaca_secret_key",
        }
      }
    }
  }
}
```

## Docker Usage

**Prerequisite:**  
You must have [Docker installed](https://docs.docker.com/get-docker/) on your system.

### Run the latest published image (recommended for most users)
```bash
docker run -it --rm \
  -e ALPACA_API_KEY=your_alpaca_api_key \
  -e ALPACA_SECRET_KEY=your_alpaca_secret_key \
  ghcr.io/chand1012/alpaca-mcp-server:latest
```
This pulls and runs the latest published version of the server. Replace `your_alpaca_api_key` and `your_alpaca_secret_key` with your actual keys. If the server exposes a port (e.g., 8080), add `-p 8080:8080` to the command.

### Build and run locally (for development or custom changes)
```bash
docker build -t alpaca-mcp-server .
docker run -it --rm \
  -e ALPACA_API_KEY=your_alpaca_api_key \
  -e ALPACA_SECRET_KEY=your_alpaca_secret_key \
  alpaca-mcp-server
```
Use this if you want to run a modified or development version of the server.

### Using with Claude Desktop
```json
{
  "mcpServers": {
    "alpaca": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "ALPACA_API_KEY",
        "-e", "ALPACA_SECRET_KEY",
        "ghcr.io/chand1012/alpaca-mcp-server:latest"
      ],
      "env": {
        "ALPACA_API_KEY": "your_alpaca_api_key",
        "ALPACA_SECRET_KEY": "your_alpaca_secret_key"
      }
    }
  }
}
```
Environment variables can be set either with `-e` flags or in the `"env"` object, but not both. For Claude Desktop, use the `"env"` object.

**Security Note:**  
Never share your API keys or commit them to public repositories. Be cautious when passing secrets as environment variables, especially in shared or production environments.

**For more advanced Docker usage:**  
See the [official Docker documentation](https://docs.docker.com/).

## API Key Configuration for Live Trading

This MCP server connects to Alpaca's **paper trading API** by default for safe testing.
To enable **live trading with real funds**, update the following configuration files:

### 🔐 Set Your API Credentials in Two Places:

1. **`.env` in the project directory**

   ```
   ALPACA_API_KEY = "your_alpaca_api_key_for_live_account"
   ALPACA_SECRET_KEY = "your_alpaca_secret_key_for_live_account"
   PAPER = False
   TRADE_API_URL = None
   TRDE_API_WSS = None
   DATA_API_URL = None
   STREAM_DATA_WSS = None
   ```
2. **Claude for Desktop Configuration**

   In `claude_desktop_config.json`, provide your keys for your live account as environment variables:

   ```json
   {
     "mcpServers": {
       "alpaca": {
         "command": "<project_root>/venv/bin/python",
         "args": [
           "/path/to/alpaca_mcp_server.py"
         ],
         "env": {
           "ALPACA_API_KEY": "your_alpaca_api_key_for_live_account",
           "ALPACA_SECRET_KEY": "your_alpaca_secret_key_for_live_account"
         }
       }
     }
   }
   ```

## Available Tools

### Account & Positions

* `get_account_info()` – View balance, margin, and account status
* `get_positions()` – List all held assets
* `get_open_position(symbol)` – Detailed info on a specific position
* `close_position(symbol, qty|percentage)` – Close part or all of a position
* `close_all_positions(cancel_orders)` – Liquidate entire portfolio

### Stock Market Data

* `get_stock_quote(symbol)` – Real-time bid/ask quote
* `get_stock_bars(symbol, start_date, end_date)` – OHLCV historical bars
* `get_stock_latest_trade(symbol)` – Latest market trade price
* `get_stock_latest_bar(symbol)` – Most recent OHLC bar
* `get_stock_trades(symbol, start_time, end_time)` – Trade-level history

### Orders

* `get_orders(status, limit)` – Retrieve all or filtered orders
* `place_stock_order(symbol, side, quantity, order_type="market", limit_price=None, stop_price=None, trail_price=None, trail_percent=None, time_in_force="day", extended_hours=False, client_order_id=None)` – Place a stock order of any type (market, limit, stop, stop_limit, trailing_stop)
* `cancel_order_by_id(order_id)` – Cancel a specific order
* `cancel_all_orders()` – Cancel all open orders

### Options

* `get_option_contracts(underlying_symbol, expiration_date)` – Fetch contracts
* `get_option_latest_quote(option_symbol)` – Latest bid/ask on contract
* `get_option_snapshot(symbol_or_symbols)` – Get Greeks and underlying
* `place_option_market_order(legs, order_class, quantity)` – Execute option strategy

### Market Info & Corporate Actions

* `get_market_clock()` – Market open/close schedule
* `get_market_calendar(start, end)` – Holidays and trading days
* `get_corporate_announcements(...)` – Earnings, dividends, splits

### Watchlists

* `create_watchlist(name, symbols)` – Create a new list
* `update_watchlist(id, name, symbols)` – Modify an existing list
* `get_watchlists()` – Retrieve all saved watchlists

### Assets

* `get_asset_info(symbol)` – Search asset metadata
* `get_all_assets(status)` – List all tradable instruments

## Example Natural Language Queries
See the "Example Queries" section below for 50 real examples covering everything from trading to corporate data to option strategies.

### Basic Trading
1. What's my current account balance and buying power?
2. Show me my current positions.
3. Buy 10 shares of AAPL at market price.
4. Sell 5 shares of TSLA with a limit price of $300.
5. Cancel all open stock orders.
6. Cancel the order with ID abc123.
7. Liquidate my entire position in GOOGL.
8. Close 10% of my position in NVDA.
9. How many shares of AMZN do I currently hold?
10. Place a limit order to buy 100 shares of MSFT at $450.
11. Place a market order to sell 25 shares of META.

### Option Trading
12. Show me available option contracts for AAPL expiring next month.
13. Get the latest quote for AAPL250613C00200000.
14. Retrieve the option snapshot for SPY250627P00400000.
15. Liquidate my position in 2 contracts of QQQ calls expiring next week.
16. Place a market order to buy 1 call option on AAPL expiring next Friday.
17. What are the option Greeks for TSLA250620P00500000?
18. Find all TSLA option contracts with strike prices within 5% of the current market price.
19. Get all contracts for SPY expiring in June that are call options.
20. Place a bull call spread using AAPL June 6th options: one with a 190.00 strike and the other with a 200.00 strike.

### Market Information
21. Is the US stock market currently open?
22. What are the market open and close times today?
23. Show me the market calendar for next week.
24. Are there any corporate announcements for major tech stocks this month?
25. What are the next dividend announcements for SPY?
26. List earnings announcements coming tomorrow.

### Historical & Real-time Data
27. Show me AAPL's daily price history for the last 5 trading days.
28. What was the closing price of TSLA yesterday?
29. Get the latest bar for GOOG.
30. What was the latest trade price for NVDA?
31. Show me the most recent quote for MSFT.
32. Retrieve the last 100 trades for AMD.
33. Show me intraday bars for AMZN from last Tuesday through last Friday.

### Orders
34. Show me all my open and filled orders from this week.
35. What orders do I have for AAPL?
36. List all limit orders I placed in the past 3 days.
37. Filter all orders by status: filled.
38. Get me the order history for yesterday.

### Watchlists
39. Create a new watchlist called "Tech Stocks" with AAPL, MSFT, and NVDA.
40. Update my "Tech Stocks" watchlist to include TSLA and AMZN.
41. What stocks are in my "Dividend Picks" watchlist?
42. Remove META from my "Growth Portfolio" watchlist.
43. List all my existing watchlists.

### Asset Information
44. Search for details about the asset 'AAPL'.
45. List all tradeable US Large-cap stocks.
46. Show me the top 5 tradable crypto assets by trading volume.
47. Filter all assets with status 'active'.
48. Show me details for the stock with symbol 'GOOGL'.

### Combined Scenarios
49. Get today's market clock and show me my buying power before placing a limit buy order for TSLA at $340.
50. Place a bull call spread with SPY July 3rd options: buy one 5% above and sell one 3% below the current SPY price.

## Example Outputs

The MCP server provides detailed, well-formatted responses for various trading queries. Here are some examples:

### Option Greeks Analysis
Query: "What are the option Greeks for TSLA250620P00500000?"

Response:
Option Details:
- Current Bid/Ask: $142.62 / $143.89
- Last Trade: $138.85
- Implied Volatility: 92.54%

Greeks:
- Delta: -0.8968 (Very Bearish)
- Gamma: 0.0021 (Low Rate of Change)
- Theta: -0.2658 (Time Decay: $26.58/day)
- Vega: 0.1654 (Volatility Sensitivity)
- Rho: -0.3060 (Interest Rate Sensitivity)

Key Insights:
- High Implied Volatility (92.54%)
- Deep In-the-Money (Delta: -0.90)
- Significant Time Decay ($27/day)

### Multi-Leg Option Order
Query: "Place a bull call spread using AAPL June 6th options: one with a 190.00 strike and the other with a 200.00 strike."

Response:
Order Details:
- Order ID: fc1c04b1-8afa-4b2d-aab1-49613bbed7cb
- Order Class: Multi-Leg (MLEG)
- Status: Pending New
- Quantity: 1 spread

Spread Legs:
1. Long Leg (BUY):
   - AAPL250606C00190000 ($190.00 strike)
   - Status: Pending New

2. Short Leg (SELL):
   - AAPL250606C00200000 ($200.00 strike)
   - Status: Pending New

Strategy Summary:
- Max Profit: $10.00 per spread
- Max Loss: Net debit paid
- Breakeven: $190 + net debit paid

These examples demonstrate the server's ability to provide:
- Detailed market data analysis
- Comprehensive order execution details
- Clear strategy explanations
- Well-formatted, easy-to-read responses

The server maintains this level of detail and formatting across all supported queries, making it easy to understand and act on the information provided.

## ⚠️ Security Notice

This server can place real trades and access your portfolio. Treat your API keys as sensitive credentials. Review all actions proposed by the LLM carefully, especially for complex options strategies or multi-leg trades.

## License

MIT
