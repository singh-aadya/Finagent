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
