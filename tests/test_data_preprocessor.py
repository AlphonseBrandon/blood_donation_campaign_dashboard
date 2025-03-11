# tests/test_data_preprocessor.py

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
from src.data_preprocessor import BloodDonationPreprocessor, PreprocessConfig

@pytest.fixture
def raw_data_sample():
    """Sample raw data matching the structure from BloodDonationDataLoader"""
    return {
        "Volontaire": pd.DataFrame({
            'ID': ['DONOR_001', 'DONOR_002'],
            'Age_': ['25', '30'],
            'Horodateur_': ['', ''],
            'Taille_': ['170', ''],
            'Poids_': ['70', ''],
            'Situation_Matrimoniale_(SM)_': ['Célibataire', 'Marié(e)'],
            'Raison_de_non-eligibilité_totale__[Scarifié]_': ['', 'Oui'],
            'Arrondissement_de_résidence_': ['Douala 3 (Non précisé)', ''],
            'Taux_d’hémoglobine_': ['13.5', '11.2'],
            'A-t-il_(elle)_déjà_donné_le_sang_': ['Oui', 'Non']
        })
    }

@pytest.fixture
def preprocessor(raw_data_sample):
    return BloodDonationPreprocessor(raw_data_sample)

def test_initialization(preprocessor):
    assert 'Volontaire' in preprocessor.interim_data
    assert len(preprocessor.raison_columns) > 0
    assert preprocessor.volontaire_df.shape[0] == 2

def test_drop_columns(preprocessor):
    preprocessor._clean_column_names()
    original_columns = preprocessor.volontaire_df.columns.tolist()
    preprocessor._drop_columns()
    new_columns = preprocessor.volontaire_df.columns.tolist()
    
    # Verify removed columns
    assert 'Horodateur' not in new_columns
    assert 'Date_de_dernières_règles_(DDR)' not in new_columns
    # Verify kept columns
    assert 'Age' in new_columns
    assert 'Taux_d’hémoglobine' in new_columns

def test_handle_numeric_columns(preprocessor):
    preprocessor._clean_column_names()
    preprocessor._handle_numeric_columns()
    
    # Check numeric conversion
    assert pd.api.types.is_numeric_dtype(preprocessor.volontaire_df['Age'])
    assert pd.api.types.is_numeric_dtype(preprocessor.volontaire_df['Poids'])
    assert pd.api.types.is_numeric_dtype(preprocessor.volontaire_df['Taux_d’hémoglobine'])
    
    # Check NaN handling
    assert preprocessor.volontaire_df['Taille'].isna().sum() == 0
    assert preprocessor.volontaire_df['Poids'].isna().sum() == 0
