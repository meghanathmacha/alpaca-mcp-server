Product Requirements Document (PRD)

Project Name: SPY 0-DTE Trading Bot (extension of alpaca-mcp-server)
Product Owner: Meghanath Macha – Head of AI & Platform, ZeroToOne.ai
Version: 1.2 (Claude-as-UI, 19 Jun 2025)

⸻

1  Purpose & Background

alpaca-mcp-server already exposes Alpaca’s Trading & Market-Data APIs as Model-Context-Protocol (MCP) tools.
We will extend it into a production-grade, option-focused intraday trading system that:
	1.	Streams same-day-expiry (0-DTE) SPY option chains with greeks in real-time.
	2.	Generates, previews and (on explicit confirmation) sends trades for predefined strategies.
	3.	Enforces deterministic risk guardrails before any order reaches Alpaca.
	4.	Executes single- and multi-leg option orders via Alpaca’s broker API.
	5.	Publishes auditable logs, metrics and alerts.
	6.	Uses Claude (or any MCP-capable LLM) as the sole user interface; all interaction occurs through tool calls.

⸻

2  Objectives & Success Metrics

Objective	KPI	Target
Accurate chain ingestion	Snapshot latency (option-chain → Redis)	≤ 1 s p95
Reliable execution	Rejected-order rate	< 0.5 % per day
Risk containment	Daily loss beyond cap	0 incidents
Operational transparency	MTTR after crash	< 5 min
Trader latency	Tick → order send	≤ 500 ms p95
Dev velocity	Mean PR cycle time	≤ 48 h


⸻

3  Scope

Layer	In-scope (v 1)	Out-of-scope / Backlog
Infrastructure	Mono-repo, Dockerised FastAPI app; Redis side-car; Prometheus metrics.	Micro-service split; multi-cloud.
Market Data	Option-chain snapshots, WS stream, IV-Rank, VWAP, OR-high/low, realised σ.	L2 depth, full tape.
Strategies	Opening-Range (long call / put), 30-Δ Iron Condor, late-day 5-Δ “lotto”, Flatten All, Show P&L.	Gamma scalping, SPX, multi-underlying.
Risk	Max daily loss $, per-trade stop %, portfolio ∆ cap, kill-switch.	Portfolio VaR, margin optimisation.
Execution	Adaptive limit pricing (mid ± ¼ spread, 3 retries); auto OCO stop / TP.	Smart-venue routing.
Interface	MCP tools only; Claude chat is the UI.	Gradio / mobile / Slack.
Compliance	Immutable JSONL in S3, Prometheus, PagerDuty.	FINRA CAT feed.


⸻

4  Personas & Core Use-Cases

Persona	Core Workflow via Claude
Lead Trader	“Buy a 30-delta SPY call with 50 % stop.” Claude → orb_long_call tool → returns preview. After “Execute”, order is sent; fills stream back.
Quant Engineer	Implements new strategy module (straddle_scan) → adds tool metadata → Claude can now execute “Find profitable straddles…”.
Risk Officer/COO	“Flatten all positions.” Claude calls flatten_all, receives summary + daily P&L.


⸻

5  Functional Requirements

ID	Requirement	Acceptance Criteria
F-01	Central config loader (common.config.Settings) reads .env vars (ALPACA_*, risk caps).	Missing/invalid var aborts boot with clear log.
F-02	Market-data module fetches 0-DTE chain: GET /v1beta1/options/snapshots/SPY every ≤ 2 s; publishes to Redis.	Snapshot p95 latency ≤ 1 s; greeks present.
F-03	Risk layer (brokerage_service.risk.validate) blocks orders breaching caps before submission.	Unit test simulating breach raises exception.
F-04	Execution layer uses adaptive limits; retries ≤ 3; sets stop loss per tool spec.	Fill ≠ mid-price spread fraction ≤ 25 %.
F-05	Tool lifecycle – every trade tool supports preview → confirm pattern.	First call returns "status":"preview"; second call with confirm=true executes.
F-06	Streaming updates – positions/P&L pushed to Claude via MCP streaming hooks.	Fill appears in Claude within 2 s of broker message.
F-07	Utility tools: flatten_all, show_pnl, kill_switch(toggle) available.	Each returns JSON result; audited.
F-08	Metrics endpoint /metrics exposes latency, chain age, P&L, rejects.	Grafana dashboard live.


⸻

6  Non-Functional Requirements
	•	Performance: Tick → order p95 ≤ 500 ms.
	•	Reliability: ≥ 99.5 % uptime during market hours.
	•	Security: Secrets in AWS Secrets Mgr; least-priv IAM.
	•	Scalability: Redis fan-out to ≥ 3 concurrent MCP clients without stall.
	•	Observability: OpenTelemetry trace-IDs across layers.

⸻

7  High-Level Architecture

Claude (LLM)
  │  natural-language
  │  + MCP tool calls
  ▼
alpaca-mcp-server (extended FastAPI)
  ├─ /tools/*  (MCP handlers)
  │    • strategy tools
  │    • risk / utility tools
  ├─ market_data_service/
  │    • snapshots.py  (REST)
  │    • stream.py     (WS → Redis)
  ├─ research_service/
  │    • strategies/
  ├─ brokerage_service/
  │    • client.py     (TradingClient wrapper)
  │    • risk.py
  │    • execution.py
  ├─ common/
  └─ /metrics  /health

Redis  (pub/sub, state cache)
S3     (immutable logs)
Prometheus ➜ Grafana
PagerDuty  (alerts)

Alpaca Market-Data WS / REST
Alpaca Trading API


⸻

8  Environment & Configuration

# .env  (root)
ALPACA_API_KEY_ID=pk_live_xxx
ALPACA_API_SECRET_KEY=sk_live_xxx
ALPACA_PAPER=true
ALPACA_DATA_FEED=sip

MAX_DAILY_LOSS=500      # dollars
DELTA_CAP=50            # absolute portfolio delta


⸻

9  Dependencies & Assumptions

Item	Status
Alpaca account with Options Level 3, SIP feed.	Ready
Redis instance (Elasticache or Docker side-car).	Provisioning
Claude MCP tool-call latency budget ≤ 30 s.	Verified
One shared Alpaca account for now; per-user keys later.	Accepted


⸻

10  Risks & Mitigations

Risk	Impact	Mitigation
Alpaca WS disconnects	Missed ticks → stale greeks	Auto-reconnect, polling fallback.
LLM misunderstanding preview/confirm flow	Unintended trades	Two-step confirmation enforced server-side.
Reg-T margin calls	Forced liquidation	Validate account.options_buying_power each submit.
Single-broker outage	Lost trading day	Backlog: IBKR adapter; kill-switch now.


⸻

11  Milestones & Timeline (6-week roadmap)

Week	Deliverables
W1	Package scaffolding; config loader; CI (ruff, pytest, pyright).
W2	Market-data snapshot + WS stream; Redis cache; Prometheus metrics.
W3	Risk layer; adaptive-limit execution; unit tests; kill-switch tool.
W4	Strategy tools (ORB call/put, Iron Condor, Lotto); preview-confirm logic; tool discovery endpoint.
W5	Streaming fills → Claude; immutable JSONL logs → S3; PagerDuty alerts; 100-session paper-trade burn-in.
W6	Live capital pilot (≤ $10k); KPI review against objectives; Go/No-Go gate.


⸻

12  Open Questions
	1.	Capital allocation per strategy during pilot (equal weight or discretionary)?
	2.	Is per-user audit of Claude chat logs required for compliance?
	3.	Do we need dual-broker redundancy before increasing capital above $10 k?
	4.	Preferred hosting: AWS Fargate vs. EC2 near Alpaca’s colo?

⸻

13  Acceptance & Sign-Off

Upon stakeholder approval (CTO, COO, Risk Officer), epics and user stories will be created in Jira aligned to the milestones above.