"""
Module for preprocessing blood donation data
"""

import pandas as pd
from pathlib import Path
import logging
from typing import Dict

class PreprocessConfig:
    """Preprocessing configuration"""
    PROCESSED_DATA_DIR = Path("data/processed")
    OUTPUT_PATH = PROCESSED_DATA_DIR/"processed.xlsx"

class BloodDonationPreprocessor:
    """Class for preprocessing raw blood donation data"""
    
    def __init__(self, raw_data: Dict[str, pd.DataFrame]):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
        
        self.interim_data = raw_data.copy()
        self.raison_columns = [
            col for col in self.interim_data["Volontaire"].columns 
            if col.startswith("Raison")
        ]

    def _clean_column_names(self) -> None:
        """Clean column names by removing trailing underscores and periods"""
        volontaire_df = self.interim_data["Volontaire"]
        volontaire_df.columns = [
            col.rstrip('_').rstrip('.') 
            for col in volontaire_df.columns
        ]
        self.logger.info("Cleaned column names")

    def _drop_columns(self) -> None:
        """Remove unnecessary columns"""
        cols_to_drop = [
            'Horodateur', 'Taille', 
            'Si_oui_preciser_la_date_du_dernier_don',
            'Date_de_dernières_règles_(DDR)',
            'Autre_raisons,__preciser',
            'Sélectionner_\"ok\"_pour_envoyer',
            'Si_autres_raison_préciser'
        ]
        self.interim_data["Volontaire"].drop(
            columns=cols_to_drop, 
            errors='ignore'
        )
        self.logger.info("Dropped unnecessary columns")

    def _convert_numeric_types(self) -> None:
        """Handle numeric type conversions and missing values"""
        volontaire_df = self.interim_data["Volontaire"]
        
        # Convert to numeric
        for col in ['Age', 'Poids']:
            volontaire_df[col] = pd.to_numeric(
                volontaire_df[col], 
                errors='coerce'
            )
            
        # Fill missing values
        volontaire_df['Poids'].fillna(
            volontaire_df['Poids'].mean()
        )
        volontaire_df['Age'].fillna(
            volontaire_df['Age'].mean()
        )
        
        # Handle hemoglobin rate
        volontaire_df['Taux_d’hémoglobine'] = pd.to_numeric(
            volontaire_df['Taux_d’hémoglobine'], 
            errors='coerce'
        )
        volontaire_df['Taux_d’hémoglobine'].fillna(
            volontaire_df['Taux_d’hémoglobine'].mean().round(1)
        )
        
        self.logger.info("Converted numeric types and handled missing values")

    def _handle_raison_columns(self) -> None:
        """Process columns starting with 'Raison'"""
        volontaire_df = self.interim_data["Volontaire"]
        volontaire_df[self.raison_columns] = volontaire_df[self.raison_columns]\
            .replace('', 'Non')\
            .fillna('Non')
        self.logger.info("Processed 'Raison' columns")

    def _clean_arrondissement(self) -> None:
        """Clean residence column"""
        volontaire_df = self.interim_data["Volontaire"]
        volontaire_df['Arrondissement_de_résidence'] = volontaire_df[
            'Arrondissement_de_résidence'
        ].str.replace(
            r'\\s*\\(Non précisé \\)$', 
            '', 
            regex=True
        )
        self.logger.info("Cleaned Arrondissement_de_résidence column")

    def process(self) -> Dict[str, pd.DataFrame]:
        """Execute full preprocessing pipeline"""
        self.logger.info("Starting preprocessing...")
        
        processing_steps = [
            self._clean_column_names,
            self._drop_columns,
            self._convert_numeric_types,
            self._handle_raison_columns,
            self._clean_arrondissement
        ]
        
        for step in processing_steps:
            try:
                step()
            except Exception as e:
                self.logger.error(f"Error in {step.__name__}: {str(e)}")
                raise
        
        self.logger.info("Preprocessing completed successfully")
        return self.interim_data

    def save_processed_data(self) -> None:
        """Save processed data to Excel file"""
        PreprocessConfig.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(PreprocessConfig.OUTPUT_PATH) as writer:
            for sheet_name, df in self.interim_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        self.logger.info(f"Saved processed data to {PreprocessConfig.OUTPUT_PATH}")

if __name__ == "__main__":
    """Example usage"""
    from data_loader import BloodDonationDataLoader
    
    # Load and process data
    loader = BloodDonationDataLoader()
    raw_data = loader.load_raw_excel()
    
    preprocessor = BloodDonationPreprocessor(raw_data)
    processed_data = preprocessor.process()
    preprocessor.save_processed_data()