"""
Analysis functions for SME Vietnam World Bank data.
"""

import pandas as pd
import numpy as np
from typing import Optional


def calculate_constraint_rate(df: pd.DataFrame, constraint_col: str = "fin34") -> dict:
    """
    Calculate credit constraint statistics.

    Args:
        df: DataFrame with constraint indicator
        constraint_col: Column name for constraint rate

    Returns:
        Dictionary with constraint statistics
    """
    return {
        "fully_constrained": df.loc[df["Indicator Code"] == "fin23", "Viet Nam (2023)"].values[0],
        "partially_constrained": df.loc[df["Indicator Code"] == "fin24", "Viet Nam (2023)"].values[0],
        "total_constrained": df.loc[df["Indicator Code"] == "fin34", "Viet Nam (2023)"].values[0],
    }


def compare_to_benchmarks(df: pd.DataFrame, indicator_code: str) -> pd.Series:
    """
    Compare a Vietnam indicator to regional and global benchmarks.

    Args:
        df: DataFrame containing indicator data
        indicator_code: The World Bank indicator code (e.g., 'fin34')

    Returns:
        Series with Vietnam, East Asia, and All Economies values
    """
    row = df[df["Indicator Code"] == indicator_code]
    if row.empty:
        raise ValueError(f"Indicator '{indicator_code}' not found in data")

    return pd.Series({
        "Vietnam": row["Viet Nam (2023)"].values[0],
        "East Asia & Pacific": row["East Asia & Pacific"].values[0],
        "All Economies": row["All Economies"].values[0],
    })


def categorize_firms_by_size(df: pd.DataFrame, size_col: str = "a6a") -> pd.Series:
    """
    Categorize firms by size from firm-level data.

    Returns counts for:
    - Small (5-19 employees)
    - Medium (20-99 employees)
    - Large (100+ employees)

    Args:
        df: Firm-level DataFrame
        size_col: Column containing firm size information

    Returns:
        Series with firm counts by size category
    """
    size_categories = {
        "Small (5-19)": len(df[df[size_col] == 1]),
        "Medium (20-99)": len(df[df[size_col] == 2]),
        "Large (100+)": len(df[df[size_col] == 3]),
    }
    return pd.Series(size_categories)


def calculate_financing_sources(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract financing source percentages from investment data.

    Returns DataFrame with:
    - Internal funds
    - Bank financing
    - Supplier/customer credit
    - Equity
    - Other sources

    Args:
        df: Investment financing DataFrame

    Returns:
        DataFrame with financing source breakdown
    """
    sources = {
        "Source": ["Internal Funds", "Bank Loans", "Supplier Credit", "Equity", "Other"],
        "Vietnam": [
            df.loc[df["Indicator Code"] == "fin1", "Viet Nam (2023)"].values[0],
            df.loc[df["Indicator Code"] == "fin2", "Viet Nam (2023)"].values[0],
            df.loc[df["Indicator Code"] == "fin3", "Viet Nam (2023)"].values[0],
            df.loc[df["Indicator Code"] == "fin4", "Viet Nam (2023)"].values[0],
            df.loc[df["Indicator Code"] == "fin5", "Viet Nam (2023)"].values[0],
        ],
        "East Asia & Pacific": [
            df.loc[df["Indicator Code"] == "fin1", "East Asia & Pacific"].values[0],
            df.loc[df["Indicator Code"] == "fin2", "East Asia & Pacific"].values[0],
            df.loc[df["Indicator Code"] == "fin3", "East Asia & Pacific"].values[0],
            df.loc[df["Indicator Code"] == "fin4", "East Asia & Pacific"].values[0],
            df.loc[df["Indicator Code"] == "fin5", "East Asia & Pacific"].values[0],
        ],
        "All Economies": [
            df.loc[df["Indicator Code"] == "fin1", "All Economies"].values[0],
            df.loc[df["Indicator Code"] == "fin2", "All Economies"].values[0],
            df.loc[df["Indicator Code"] == "fin3", "All Economies"].values[0],
            df.loc[df["Indicator Code"] == "fin4", "All Economies"].values[0],
            df.loc[df["Indicator Code"] == "fin5", "All Economies"].values[0],
        ],
    }

    return pd.DataFrame(sources)


def generate_summary_stats(indicator_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Generate a summary table of key indicators across all files.

    Args:
        indicator_dict: Dictionary of loaded indicator DataFrames

    Returns:
        Summary DataFrame with key metrics
    """
    summaries = []

    # From Finance file
    finance_df = indicator_dict.get("Viet Nam Finance")
    if finance_df is not None:
        key_metrics = ["fin34", "fin23", "fin24", "fin14", "fin11", "fin21"]
        for code in key_metrics:
            row = finance_df[finance_df["Indicator Code"] == code]
            if not row.empty:
                summaries.append({
                    "Indicator Code": code,
                    "Vietnam": row["Viet Nam (2023)"].values[0],
                    "East Asia & Pacific": row["East Asia & Pacific"].values[0],
                    "All Economies": row["All Economies"].values[0],
                })

    return pd.DataFrame(summaries)
