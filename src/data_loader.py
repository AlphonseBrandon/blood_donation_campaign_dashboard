"""
Module for loading raw blood donation data from Excel files
"""

import pandas as pd
from pathlib import Path
import logging
from typing import Dict

class Config:
    """Project configuration"""
    RAW_DATA_DIR = Path("/home/alphonse/github-repos/00_blood_campaign_dashboard/blood_donation_campaign_dashboard/data/raw")
    EXCEL_PATH = RAW_DATA_DIR/"blood_donation_data.xlsx"
    SHEET_NAMES = ["2019", "2020", "Volontaire"]

class BloodDonationDataLoader:
    """Class for loading raw Excel data without preprocessing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def load_raw_excel(self) -> Dict[str, pd.DataFrame]:
        """
        Load raw Excel data with three sheets
        Returns:
            Dictionary of DataFrames with keys: 2019, 2020, Volontaire
        """
        try:
            dfs = pd.read_excel(
                Config.EXCEL_PATH,
                sheet_name=Config.SHEET_NAMES,
                dtype=str,
                keep_default_na=False,
                engine="openpyxl"
            )
            self.logger.info(f"Successfully loaded Excel file: {Config.EXCEL_PATH}")
            return dfs

        except FileNotFoundError as e:
            self.logger.error(f"Missing Excel file: {Config.EXCEL_PATH}")
            raise
        except ValueError as e:
            self.logger.error(f"Missing sheet in Excel file. Required sheets: {Config.SHEET_NAMES}")
            raise

if __name__ == "__main__":
    """Command-line usage"""
    loader = BloodDonationDataLoader()
    data = loader.load_raw_excel()
    print(f"Loaded sheets: {list(data.keys())}")