"""
Data loading utilities for SME Vietnam World Bank Analysis.
"""

import pandas as pd
from pathlib import Path

# Define paths
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_indicator_file(filename: str) -> pd.DataFrame:
    """
    Load a World Bank indicator Excel file.

    Args:
        filename: Name of the file in the raw data directory

    Returns:
        DataFrame with the indicator data
    """
    filepath = RAW_DIR / filename
    df = pd.read_excel(filepath)
    return df


def load_all_indicators() -> dict[str, pd.DataFrame]:
    """
    Load all indicator files from the raw directory.

    Returns:
        Dictionary mapping file names to DataFrames
    """
    indicator_files = [
        "Viet Nam.xlsx",
        "Viet Nam Finance.xlsx",
        "Viet Nam Access to Finance Constraints.xlsx",
        "Viet Nam Investment Financing.xlsx",
        "Viet Nam Working Capital Financing.xlsx",
    ]

    data = {}
    for filename in indicator_files:
        filepath = RAW_DIR / filename
        if filepath.exists():
            data[filename.replace(".xlsx", "")] = pd.read_excel(filepath)

    return data


def load_firm_level_data(filepath: str | Path = None) -> pd.DataFrame:
    """
    Load the firm-level survey data.

    Supports:
    - CSV files
    - Stata (.dta) files
    - Excel files

    Args:
        filepath: Optional path to data file. If None, looks for .dta file in raw dir.

    Returns:
        DataFrame with firm-level data
    """
    if filepath is None:
        # Look for the Stata file
        dta_files = list(RAW_DIR.glob("*.dta"))
        if dta_files:
            filepath = dta_files[0]
        else:
            raise FileNotFoundError(
                "No .dta file found in raw directory. "
                "Please download the firm-level data from the World Bank Data Portal."
            )

    filepath = Path(filepath)

    if filepath.suffix == ".dta":
        df = pd.read_stata(filepath)
    elif filepath.suffix == ".csv":
        df = pd.read_csv(filepath)
    elif filepath.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")

    return df


def get_available_files() -> list[str]:
    """Return list of available files in the raw data directory."""
    return [f.name for f in RAW_DIR.iterdir() if f.is_file()]
