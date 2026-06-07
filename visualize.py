import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

CSV_FILE = "expense_data.csv"
CHART_FOLDER = "static/charts"

os.makedirs(CHART_FOLDER, exist_ok=True)

pie_chart = os.path.join(CHART_FOLDER, "expense_pie_chart.png")
bar_chart = os.path.join(CHART_FOLDER, "category_expense.png")

# ── Theme colors (matched to updated dark UI) ─────────────────────
BG        = "#0a0a0f"
CARD_BG   = "#16161f"
ACCENT    = "#8fb020"   # darkened lime
MUTED     = "#4a4a5a"   # darkened muted
TEXT      = "#b0b0b8"   # darkened text
BORDER    = "#ffffff1a"

PALETTE = [
    "#8fb020",  # lime (accent)
    "#1a7a45",  # dark mint
    "#a83030",  # dark coral
    "#1a5c8a",  # dark sky blue
    "#a85a10",  # dark amber
    "#6a18a0",  # dark purple
    "#a01870",  # dark pink
    "#0d7a5f",  # dark teal
]

def apply_dark_style():
    mpl.rcParams.update({
        "figure.facecolor":  BG,
        "axes.facecolor":    CARD_BG,
        "axes.edgecolor":    BORDER,
        "axes.labelcolor":   MUTED,
        "axes.titlecolor":   TEXT,
        "xtick.color":       MUTED,
        "ytick.color":       MUTED,
        "text.color":        TEXT,
        "grid.color":        BORDER,
        "grid.linestyle":    "--",
        "grid.alpha":        1,
        "font.family":       "monospace",
        "font.size":         11,
    })

try:
    df = pd.read_csv(CSV_FILE)

    if "Amount" in df.columns:

        df["Amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
       )

        df["Amount"] = pd.to_numeric(
            df["Amount"],
            errors="coerce"
       )

    df = df.dropna(subset=["Amount"])

    apply_dark_style()

    if df.empty:
        for path in [pie_chart, bar_chart]:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, "No Expense Data", ha="center", va="center",
                    fontsize=14, color=MUTED)
            ax.axis("off")
            fig.savefig(path, dpi=120, bbox_inches="tight", facecolor=BG)
            plt.close(fig)

    else:
        category = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        print(df)
        print(category)
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(category))]

        # ── BAR CHART ─────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(category.index, category.values, color=colors,
                      width=0.5, zorder=3)

        ax.set_title("Expense by Category", fontsize=13, fontweight="bold",
                     color=TEXT, pad=16)
        ax.set_xlabel("Category", labelpad=10)
        ax.set_ylabel("Amount (₹)", labelpad=10)
        ax.yaxis.grid(True, zorder=0)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)

        for bar, val in zip(bars, category.values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(category.values) * 0.01,
                    f"₹{val:,.0f}", ha="center", va="bottom",
                    fontsize=9, color=ACCENT)

        fig.tight_layout()
        fig.savefig(bar_chart, dpi=120, bbox_inches="tight", facecolor=BG)
        plt.close(fig)

        # ── PIE CHART ─────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(7, 7))
        wedges, texts, autotexts = ax.pie(
            category.values,
            labels=category.index,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.78,
            wedgeprops={"linewidth": 2, "edgecolor": BG},
        )

        for t in texts:
            t.set_color(TEXT)
            t.set_fontsize(11)

        for at in autotexts:
            at.set_color(BG)
            at.set_fontsize(9)
            at.set_fontweight("bold")

        ax.set_title("Expense Distribution", fontsize=13, fontweight="bold",
                     color=TEXT, pad=20)

        fig.tight_layout()
        fig.savefig(pie_chart, dpi=120, bbox_inches="tight", facecolor=BG)
        plt.close(fig)

    print("Charts created successfully.")

except Exception as e:
    print("ERROR:", e)