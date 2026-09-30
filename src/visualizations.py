"""
Visualization utilities for SME Vietnam World Bank Analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 11

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "reports" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_vietnam_benchmark_comparison(
    data: pd.Series,
    title: str = None,
    filename: str = None,
) -> plt.Figure:
    """
    Create a horizontal bar chart comparing Vietnam to benchmarks.

    Args:
        data: Series with Vietnam, East Asia, and All Economies values
        title: Chart title
        filename: If provided, save chart to this filename

    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    colors = ["#2E86AB", "#A23B72", "#F18F01"]
    bars = ax.barh(data.index, data.values, color=colors, height=0.6)

    # Add value labels
    for bar, val in zip(bars, data.values):
        ax.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            va="center",
            fontsize=11,
        )

    ax.set_xlabel("Percentage (%)", fontsize=12)
    ax.set_xlim(0, max(data.values) * 1.15)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()

    if filename:
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        print(f"Saved: {filepath}")

    return fig


def plot_financing_sources(
    df: pd.DataFrame,
    title: str = "Sources of Investment Financing - Vietnam 2023",
    filename: str = None,
) -> plt.Figure:
    """
    Create a grouped bar chart comparing financing sources.

    Args:
        df: DataFrame with Source, Vietnam, East Asia & Pacific, All Economies
        title: Chart title
        filename: If provided, save chart to this filename

    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(df["Source"]))
    width = 0.25

    bars1 = ax.bar(x - width, df["Vietnam"], width, label="Vietnam", color="#2E86AB")
    bars2 = ax.bar(x, df["East Asia & Pacific"], width, label="East Asia & Pacific", color="#A23B72")
    bars3 = ax.bar(x + width, df["All Economies"], width, label="All Economies", color="#F18F01")

    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df["Source"], rotation=15, ha="right")
    ax.legend(loc="upper right")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylim(0, 100)

    plt.tight_layout()

    if filename:
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        print(f"Saved: {filepath}")

    return fig


def plot_constraint_breakdown(
    fully_constrained: float,
    partially_constrained: float,
    not_constrained: float,
    title: str = "Credit Constraint Status - Vietnam 2023",
    filename: str = None,
) -> plt.Figure:
    """
    Create a pie chart showing credit constraint breakdown.

    Args:
        fully_constrained: Percentage fully constrained
        partially_constrained: Percentage partially constrained
        not_constrained: Percentage not constrained (calculated as remainder)
        title: Chart title
        filename: If provided, save chart to this filename

    Returns:
        Matplotlib Figure object
    """
    # Calculate not constrained
    not_constrained = 100 - fully_constrained - partially_constrained

    fig, ax = plt.subplots(figsize=(9, 9))

    sizes = [fully_constrained, partially_constrained, not_constrained]
    labels = [
        f"Fully Constrained\n({fully_constrained:.1f}%)",
        f"Partially Constrained\n({partially_constrained:.1f}%)",
        f"Not Constrained\n({not_constrained:.1f}%)",
    ]
    colors = ["#E63946", "#F4A261", "#2A9D8F"]
    explode = (0.05, 0.02, 0)

    ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="",
        shadow=True,
        startangle=90,
    )
    ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()

    if filename:
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        print(f"Saved: {filepath}")

    return fig


def plot_collateral_requirement(
    vietnam: float,
    east_asia: float,
    global_avg: float,
    title: str = "Loan Collateral Requirements",
    filename: str = None,
) -> plt.Figure:
    """
    Create a bar chart showing collateral requirements.

    Args:
        vietnam: Vietnam percentage
        east_asia: East Asia & Pacific percentage
        global_avg: Global average percentage
        title: Chart title
        filename: If provided, save chart to this filename

    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    data = pd.Series({
        "Vietnam": vietnam,
        "East Asia & Pacific": east_asia,
        "All Economies": global_avg,
    })

    colors = ["#2E86AB", "#A23B72", "#F18F01"]
    bars = ax.bar(data.index, data.values, color=colors, width=0.6)

    for bar, val in zip(bars, data.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_ylabel("Percentage of Loans (%)", fontsize=12)
    ax.set_ylim(0, 110)
    ax.set_title(title, fontsize=14, fontweight="bold")

    plt.tight_layout()

    if filename:
        filepath = OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        print(f"Saved: {filepath}")

    return fig


def save_all_figures():
    """Generate and save all standard visualizations."""
    from src.load_data import load_all_indicators
    from src.analysis import calculate_financing_sources, compare_to_benchmarks

    indicators = load_all_indicators()

    # 1. Credit constraint comparison
    finance = indicators.get("Viet Nam Finance")
    if finance is not None:
        data = compare_to_benchmarks(finance, "fin34")
        plot_vietnam_benchmark_comparison(
            data,
            title="Firms Experiencing Credit Constraints (%)",
            filename="credit_constraints_comparison.png",
        )

    # 2. Financing sources
    investment = indicators.get("Viet Nam Investment Financing")
    if investment is not None:
        sources = calculate_financing_sources(investment)
        plot_financing_sources(
            sources,
            filename="financing_sources_comparison.png",
        )

    # 3. Collateral requirement
    if finance is not None:
        data = compare_to_benchmarks(finance, "fin11")
        plot_collateral_requirement(
            data["Vietnam"],
            data["East Asia & Pacific"],
            data["All Economies"],
            filename="collateral_requirements.png",
        )

    # 4. Constraint pie chart
    if finance is not None:
        plot_constraint_breakdown(
            fully_constrained=8.2,
            partially_constrained=18.0,
            not_constrained=73.8,
            filename="constraint_breakdown.png",
        )

    print("All figures saved to:", OUTPUT_DIR)
