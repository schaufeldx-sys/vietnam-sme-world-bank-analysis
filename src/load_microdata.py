"""
Load firm-level microdata for SME Vietnam analysis.
"""

import pandas as pd
from pathlib import Path

# Define paths
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"


def load_firm_level_data(filename: str = "Viet-Nam-2023-full-data.dta") -> pd.DataFrame:
    """
    Load the firm-level survey data.

    Args:
        filename: Name of the .dta file

    Returns:
        DataFrame with firm-level data
    """
    filepath = RAW_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"File not found: {filepath}\n"
            f"Please ensure {filename} is in {RAW_DIR}"
        )

    df = pd.read_stata(filepath)
    return df


def categorize_industry(isic_code) -> str:
    """
    Convert ISIC Rev. 4 code to broad category.

    Args:
        isic_code: Industry code (numeric or string)

    Returns:
        Industry category name
    """
    code = str(isic_code)[:2]

    mapping = {
        '10': 'Food manufacturing',
        '11': 'Beverages',
        '13': 'Textiles',
        '14': 'Apparel',
        '15': 'Leather',
        '16': 'Wood products',
        '17': 'Paper',
        '18': 'Printing',
        '20': 'Chemicals',
        '22': 'Plastics/rubber',
        '23': 'Mineral products',
        '25': 'Metal products',
        '26': 'Electronics',
        '27': 'Electrical equipment',
        '28': 'Machinery',
        '29': 'Motor vehicles',
        '31': 'Furniture',
        '32': 'Other manufacturing',
        '41': 'Construction',
        '45': 'Wholesale/retail trade',
        '49': 'Land transport',
        '50': 'Water transport',
        '52': 'Warehousing',
        '55': 'Accommodation',
        '56': 'Food services',
        '58': 'Publishing',
        '62': 'Computer programming',
        '69': 'Legal/accounting',
        '70': 'Management consulting',
        '71': 'Architecture/engineering',
        '73': 'Advertising/marketing',
        '95': 'Repair of goods',
    }

    return mapping.get(code, f'Other ({code})')


def prepare_microdata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns to the microdata.

    Args:
        df: Raw firm-level DataFrame

    Returns:
        DataFrame with additional columns for analysis
    """
    df = df.copy()

    # Add industry category
    if 'd1a2_v4' in df.columns:
        df['industry_cat'] = df['d1a2_v4'].apply(categorize_industry)

    # Add size labels
    if 'a6a' in df.columns:
        size_labels = {
            'Small': 'Small (5-19)',
            'Medium': 'Medium (20-99)',
            'Large': 'Large (100+)'
        }
        df['size_label'] = df['a6a'].map(size_labels)

    # Add constraint categories
    if 'fin34' in df.columns:
        df['is_constrained'] = df['fin34'] == 1

    # Add region labels
    if 'a2' in df.columns:
        region_labels = {
            'Red River Delta': 'Red River Delta (Hanoi area)',
            'Northern Midlands and Mountains': 'Northern Midlands',
            'Northern Central region, the Central Coast, Central Highlands': 'North-Central + Highlands',
            'Southeast': 'Southeast (HCMC area)',
            'Mekong River Delta': 'Mekong River Delta',
        }
        df['region_label'] = df['a2'].map(region_labels)

    return df


if __name__ == "__main__":
    # Test loading
    print("Loading firm-level data...")
    df = load_firm_level_data()
    print(f"Loaded {len(df):,} firms with {len(df.columns):,} variables")

    print("\nPreparing data...")
    df = prepare_microdata(df)
    print(f"Added derived columns.")

    print(f"\nSample size by firm size:")
    if 'size_label' in df.columns:
        print(df['size_label'].value_counts())
