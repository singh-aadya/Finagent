import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import io
def make_dashboard_chart(h1, h2, t1, t2, p1, p2, sd1, sd2):
    """
    Combined chart panel:
    Row 1: Normalised price comparison
    Row 2: RSI for both stocks
    Row 3: Volume for both stocks
    """
    fig = plt.figure(figsize=(14, 9), facecolor="#080c10")
    gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.3)

    BG   = "#0d1117"
    C1   = "#00d4ff"
    C2   = "#f0c040"
    GRID = "#1e2d3d"
    TEXT = "#8fa8c0"

    def style_ax(ax):
        ax.set_facecolor(BG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)
        ax.tick_params(colors=TEXT, labelsize=8)
        ax.yaxis.label.set_color(TEXT)
        ax.xaxis.label.set_color(TEXT)
        ax.grid(True, linestyle="--", alpha=0.15, color=TEXT)

    # ── Panel 1: Normalised prices (spans both columns) ───────────────────────
    ax0 = fig.add_subplot(gs[0, :])
    n1 = h1["Close"] / h1["Close"].iloc[0]
    n2 = h2["Close"] / h2["Close"].iloc[0]
    ax0.plot(n1.index, n1.values, color=C1, lw=2, label=f"{t1} ({p1:+.1f}%)")
    ax0.plot(n2.index, n2.values, color=C2, lw=2, label=f"{t2} ({p2:+.1f}%)")
    ax0.axhline(1.0, color=GRID, lw=1, ls="--")
    ax0.fill_between(n1.index, 1, n1.values, alpha=0.07, color=C1)
    ax0.fill_between(n2.index, 1, n2.values, alpha=0.07, color=C2)
    ax0.set_title("Normalised Price Performance (1.0 = Day 1)", color="#e8f0f8", fontsize=11, pad=10)
    ax0.legend(facecolor=BG, edgecolor=GRID, labelcolor="#e8f0f8", fontsize=9)
    style_ax(ax0)

    # ── Panel 2: RSI ──────────────────────────────────────────────────────────
    def plot_rsi(ax, history, color, label):
        close  = history["Close"]
        delta  = close.diff()
        gain   = delta.clip(lower=0).rolling(14).mean()
        loss   = (-delta.clip(upper=0)).rolling(14).mean()
        rsi    = 100 - (100 / (1 + gain / loss))
        ax.plot(rsi.index, rsi.values, color=color, lw=1.5, label=label)
        ax.axhline(70, color="#ff4d6a", lw=0.8, ls="--", alpha=0.6)
        ax.axhline(30, color="#00e5a0", lw=0.8, ls="--", alpha=0.6)
        ax.fill_between(rsi.index, 70, rsi.values, where=rsi.values > 70, alpha=0.1, color="#ff4d6a")
        ax.fill_between(rsi.index, 30, rsi.values, where=rsi.values < 30, alpha=0.1, color="#00e5a0")
        ax.set_ylim(0, 100)
        ax.set_ylabel("RSI", fontsize=8)

    ax1 = fig.add_subplot(gs[1, 0])
    plot_rsi(ax1, h1, C1, t1)
    ax1.set_title(f"{t1} — RSI (14)", color="#e8f0f8", fontsize=10)
    style_ax(ax1)

    ax2 = fig.add_subplot(gs[1, 1])
    plot_rsi(ax2, h2, C2, t2)
    ax2.set_title(f"{t2} — RSI (14)", color="#e8f0f8", fontsize=10)
    style_ax(ax2)

    # ── Panel 3: Volume ───────────────────────────────────────────────────────
    def plot_volume(ax, history, color, label):
        vols = history["Volume"]
        avg  = vols.rolling(20).mean()
        bars = ax.bar(vols.index, vols.values, color=color, alpha=0.4, width=1)
        ax.plot(avg.index, avg.values, color=color, lw=1.2, ls="--", label="20-day avg")
        ax.set_ylabel("Volume", fontsize=8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))

    ax3 = fig.add_subplot(gs[2, 0])
    plot_volume(ax3, h1, C1, t1)
    ax3.set_title(f"{t1} — Volume", color="#e8f0f8", fontsize=10)
    ax3.legend(facecolor=BG, edgecolor=GRID, labelcolor=TEXT, fontsize=8)
    style_ax(ax3)

    ax4 = fig.add_subplot(gs[2, 1])
    plot_volume(ax4, h2, C2, t2)
    ax4.set_title(f"{t2} — Volume", color="#e8f0f8", fontsize=10)
    ax4.legend(facecolor=BG, edgecolor=GRID, labelcolor=TEXT, fontsize=8)
    style_ax(ax4)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Helper: signal colour ─────────────────────────────────────────────────────
def signal_class(signal):
    if signal == "BUY":  return "signal-buy"
    if signal == "SELL": return "signal-sell"
    return "signal-hold"

def signal_emoji(signal):
    if signal == "BUY":  return "🟢"
    if signal == "SELL": return "🔴"
    return "🟡"

def risk_colour(score):
    if score <= 3:  return "#00e5a0"
    if score <= 6:  return "#f0c040"
    return "#ff4d6a"

def fmt_metric(v, suffix=""):
    if isinstance(v, float): return f"{v:.2f}{suffix}"
    if isinstance(v, int):   return f"{v}{suffix}"
    return str(v) if v else "N/A"

def data_completeness(sd):
    total = len(sd)
    filled = sum(1 for v in sd.values() if v not in [None, "N/A"])
    return round(filled / total * 100, 2)

# def check_consistency(sd, insight):
#     score = sd["momentum_score"]
#     signal = insight["signal"]

#     if score > 70 and signal == "BUY":
#         return True
#     if score < 30 and signal == "SELL":
#         return True
#     return False

def check_consistency(sd, insight):
    score = sd["momentum_score"]
    signal = insight["signal"]

    if score >= 70:
        return signal in ["BUY", "HOLD"]
    elif score <= 30:
        return signal in ["SELL", "HOLD"]
    else:
        return signal in ["HOLD", "BUY"]


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN FLOW
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:

    # Validation
    if not groq_key:
        st.error("❌ Please enter your free Groq API key. Get one at console.groq.com")
        st.stop()
    if not ticker1 or not ticker2:
        st.error("❌ Please enter both stock tickers.")
        st.stop()
    if ticker1 == ticker2:
        st.error("❌ Please enter two different tickers.")
        st.stop()

    today = datetime.now().strftime("%Y-%m-%d")

    # ── Step 1: Fetch raw data ────────────────────────────────────────────────
    with st.status("⬇️ Fetching market data from Yahoo Finance (free)...", expanded=True) as s:
        st.write(f"Downloading **{ticker1}**...")
        h1, m1 = fetch_stock(ticker1, period)
        st.write(f"Downloading **{ticker2}**...")
        h2, m2 = fetch_stock(ticker2, period)

        if h1 is None or m1 is None:
            s.update(label=f"❌ Could not fetch {ticker1}", state="error")
            st.error(f"Ticker '{ticker1}' not found. Check the symbol.")
            st.stop()
        if h2 is None or m2 is None:
            s.update(label=f"❌ Could not fetch {ticker2}", state="error")
            st.error(f"Ticker '{ticker2}' not found. Check the symbol.")
            st.stop()
        s.update(label="✅ Market data ready", state="complete")

    # Correlation
    df_combined = pd.DataFrame({"A": h1["Close"], "B": h2["Close"]}).dropna()
    corr = round(df_combined.corr().loc["A", "B"], 4)

    # ── Step 2: AGENT 01 ──────────────────────────────────────────────────────
    st.divider()
    st.markdown('<span class="agent-badge badge-01">Agent 01 — Data Agent</span>', unsafe_allow_html=True)

    with st.status("🔢 Agent 01 computing metrics & indicators...", expanded=True) as s:
        st.write(f"Processing **{ticker1}**: RSI, moving averages, volatility, momentum score...")
        sd1 = run_data_agent(ticker1, h1, m1, period)
        st.write(f"Processing **{ticker2}**: RSI, moving averages, volatility, momentum score...")
        sd2 = run_data_agent(ticker2, h2, m2, period)
        sd1["correlation"] = corr
        sd2["correlation"] = corr
        s.update(label="✅ Agent 01 complete — all indicators computed", state="complete")

    # Show Agent 01 output
    with st.expander("🔍 View Agent 01 output (raw computed data)"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**{ticker1}**")
            st.json(sd1)
        with col_b:
            st.markdown(f"**{ticker2}**")
            st.json(sd2)

    # ── Step 3: Charts ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Technical Analysis Charts")
    chart_buf = make_dashboard_chart(h1, h2, ticker1, ticker2,
                                     sd1["pct_change"], sd2["pct_change"], sd1, sd2)
    st.image(chart_buf, use_container_width=True)

    # ── Step 4: Quick metrics row ─────────────────────────────────────────────
    st.subheader("📋 Key Metrics at a Glance")
    cols = st.columns(6)
    metrics_row = [
        (f"{ticker1} Change",   f"{sd1['pct_change']:+.2f}%"),
        (f"{ticker2} Change",   f"{sd2['pct_change']:+.2f}%"),
        ("Correlation",         str(corr)),
        (f"{ticker1} RSI",      str(sd1["rsi"])),
        (f"{ticker2} RSI",      str(sd2["rsi"])),
        ("Period",              period),
    ]
    for col, (label, value) in zip(cols, metrics_row):
        col.metric(label, value)

    # Detailed metrics table
    metrics_df = pd.DataFrame({
        "Metric": ["Momentum Score", "Volatility %", "P/E Ratio", "Forward P/E",
                   "ROE", "Debt/Equity", "Beta", "Drawdown from 52w High",
                   "Upside to Target", "Volume Trend"],
        ticker1: [
            f"{sd1['momentum_score']}/100", f"{sd1['volatility_pct']}%",
            fmt_metric(sd1["pe_ratio"]), fmt_metric(sd1["forward_pe"]),
            fmt_metric(sd1["roe"]), fmt_metric(sd1["debt_to_equity"]),
            fmt_metric(sd1["beta"]),
            f"{sd1['drawdown_from_52w_high']}%" if sd1["drawdown_from_52w_high"] else "N/A",
            f"{sd1['upside_to_target']}%" if sd1["upside_to_target"] else "N/A",
            sd1["volume_trend"],
        ],
        ticker2: [
            f"{sd2['momentum_score']}/100", f"{sd2['volatility_pct']}%",
            fmt_metric(sd2["pe_ratio"]), fmt_metric(sd2["forward_pe"]),
            fmt_metric(sd2["roe"]), fmt_metric(sd2["debt_to_equity"]),
            fmt_metric(sd2["beta"]),
            f"{sd2['drawdown_from_52w_high']}%" if sd2["drawdown_from_52w_high"] else "N/A",
            f"{sd2['upside_to_target']}%" if sd2["upside_to_target"] else "N/A",
            sd2["volume_trend"],
        ],
    })
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    # ── Step 5: AGENT 02 ──────────────────────────────────────────────────────
    st.divider()
    st.markdown('<span class="agent-badge badge-02">Agent 02 — Insight Agent (Groq · Llama 3.3 · Free)</span>', unsafe_allow_html=True)

    with st.status("🤖 Agent 02 generating AI insights & signals...", expanded=True) as s:
        try:
            insights = run_insight_agent(groq_key, sd1, sd2, corr)

            

        # 🔥 FIX HERE (add this)
            insights_fixed = {}
            insights_fixed["stock1"] = insights.get(ticker1)
            insights_fixed["stock2"] = insights.get(ticker2)
            insights_fixed["comparison"] = insights.get("comparison")
            insights_fixed["better_pick"] = insights.get("better_pick")
            insights_fixed["better_pick_reason"] = insights.get("better_pick_reason")

            insights = insights_fixed

            s.update(label="✅ Agent 02 complete — signals & insights ready", state="complete")

        except Exception as e:
            s.update(label="❌ Agent 02 failed", state="error")
            st.error(f"Groq API error: {e}")
            st.stop()
            s.update(label="✅ Agent 02 complete — signals & insights ready", state="complete")
        # except Exception as e:
        #      s.update(label="❌ Agent 02 failed", state="error")
        #     st.error(f"Groq API error: {e}\n\nCheck your API key at console.groq.com")
        #     st.stop()

    # ── Display signals ───────────────────────────────────────────────────────
    st.subheader("🎯 AI Signals & Insights")

    col1, col2 = st.columns(2)

    for col, ticker, key, color in [
        (col1, ticker1, "stock1", "#00d4ff"),
        (col2, ticker2, "stock2", "#f0c040"),
    ]:
        data = insights.get(key)

        if data is None:
            st.error(f"Missing data for {key}. API response issue.")
            st.json(insights)  # debug view
            continue
        signal = data["signal"]
        risk   = data["risk_score"]
        rc     = risk_colour(risk)

        with col:
            st.markdown(f"#### {ticker} — {m1['full_name'] if key=='stock1' else m2['full_name']}")

            # Signal box
            sig_emoji = signal_emoji(signal)
            sig_cls   = signal_class(signal)
            st.markdown(
                f"**Signal:** <span class='{sig_cls}'>{sig_emoji} {signal}</span><br/>"
                f"<span style='color:#8fa8c0;font-size:13px'>{data['signal_reason']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown("")

            # Risk score
            st.markdown(
                f"**Risk Score:** <span style='color:{rc};font-weight:700;font-size:18px'>"
                f"{risk}/10 — {data['risk_label']}</span>",
                unsafe_allow_html=True,
            )
            st.progress(risk / 10)

            # Strength
            strength_colors = {"Bullish": "#00e5a0", "Bearish": "#ff4d6a", "Neutral": "#f0c040"}
            sc = strength_colors.get(data["strength"], "#e8f0f8")
            st.markdown(
                f"**Market Strength:** <span style='color:{sc}'>{data['strength']}</span>",
                unsafe_allow_html=True,
            )

            st.markdown("**Key Insights:**")
            for insight in data["key_insights"]:
                st.markdown(f"→ {insight}")

    # ── Comparison panel ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("⚖️ Comparative Analysis")

    bp = insights["better_pick"]
    bp_color = "#00d4ff" if bp == ticker1 else "#f0c040" if bp == ticker2 else "#8fa8c0"
    st.markdown(
        f"**Better Pick:** <span style='color:{bp_color};font-weight:700;font-size:18px'>{bp}</span> — {insights['better_pick_reason']}",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(insights["comparison"])

    # ── Downloads ─────────────────────────────────────────────────────────────
    st.divider()
    # summary = json.dumps({"agent01": {"stock1": sd1, "stock2": sd2}, "agent02": insights}, indent=2)
    clean_sd1 = convert_to_python(sd1)
    clean_sd2 = convert_to_python(sd2)
    clean_insights = convert_to_python(insights)

    summary = json.dumps({
        "agent01": {"stock1": clean_sd1, "stock2": clean_sd2},
        "agent02": clean_insights
    }, indent=2)
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "⬇️ Download Full Analysis (JSON)",
            data=summary,
            file_name=f"finagent_{ticker1}_{ticker2}_{today}.json",
            mime="application/json",
            use_container_width=True,
        )
    with dl2:
        chart_buf.seek(0)
        st.download_button(
            "⬇️ Download Charts (PNG)",
            data=chart_buf,
            file_name=f"charts_{ticker1}_{ticker2}_{today}.png",
            mime="image/png",
            use_container_width=True,
        )

    # Disclaimer
    st.markdown("---")
    st.caption("⚠️ For educational purposes only. Not financial advice. Always consult a qualified financial advisor.")

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.info("👈 Enter your free Groq API key and two stock tickers, then click **Analyse Stocks**.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🔢 Agent 01 — Data Agent")
        st.markdown("Pure Python. No API needed. Computes:")
        st.markdown("- RSI (14-day)")
        st.markdown("- Moving Averages (20/50/200)")
        st.markdown("- Momentum Score (0–100)")
        st.markdown("- Volatility (annualised)")
        st.markdown("- Volume trend analysis")
        st.markdown("- Drawdown from 52-week high")

    with c2:
        st.markdown("### 🤖 Agent 02 — Insight Agent")
        st.markdown("Groq + Llama 3.3 70B (free). Produces:")
        st.markdown("- BUY / HOLD / SELL signal")
        st.markdown("- Risk Score 1–10")
        st.markdown("- 3 key insights per stock")
        st.markdown("- Market strength rating")
        st.markdown("- Comparative analysis")
        st.markdown("- Better pick recommendation")

    with c3:
        st.markdown("### 📊 Dashboard Charts")
        st.markdown("Multi-panel technical chart:")
        st.markdown("- Normalised price comparison")
        st.markdown("- RSI for both stocks")
        st.markdown("- Volume with 20-day avg")
        st.markdown("- Downloadable PNG")
        st.markdown("- Downloadable JSON report")

# ── Evaluation Metrics ──
st.divider()
st.subheader("📊 Evaluation Metrics")

col1, col2 = st.columns(2)

# Agent 01 metrics
comp1 = data_completeness(sd1)
comp2 = data_completeness(sd2)

with col1:
    st.markdown("### Agent 01 — Data Agent")
    st.metric("Data Completeness (Stock 1)", f"{comp1}%")
    st.metric("Data Completeness (Stock 2)", f"{comp2}%")

# Agent 02 metrics
cons1 = check_consistency(sd1, insights["stock1"])
cons2 = check_consistency(sd2, insights["stock2"])

with col2:
    st.markdown("### Agent 02 — Insight Agent")
    st.metric("Consistency (Stock 1)", "✅" if cons1 else "❌")
    st.metric("Consistency (Stock 2)", "✅" if cons2 else "❌")
