import pandas as pd
from pathlib import Path
import logging
from typing import Dict
from data_loader import BloodDonationDataLoader

# File: src/data_preprocessor.py

"""
Module for preprocessing blood donation data (aligned 1:1 with notebook steps)
"""


class PreprocessConfig:
    """Preprocessing configuration"""
    PROCESSED_DATA_DIR = Path("data/processed")
    OUTPUT_PATH = PROCESSED_DATA_DIR/"processed.xlsx"

class BloodDonationPreprocessor:
    """Class replicating exact notebook preprocessing steps"""
    
    def __init__(self, raw_data: Dict[str, pd.DataFrame]):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
        
        self.interim_data = raw_data.copy()
        self.volontaire_df = self.interim_data["Volontaire"]
        self._identify_raison_columns()

    def _identify_raison_columns(self) -> None:
        """Identify all columns starting with 'Raison' as in notebook"""
        self.raison_columns = [col for col in self.volontaire_df.columns 
                              if col.startswith("Raison")]
        self.logger.debug(f"Identified {len(self.raison_columns)} 'Raison' columns")

    def _clean_column_names(self) -> None:
        """Exact column cleaning from notebook cells 414-420"""
        # Remove trailing underscores
        self.volontaire_df.columns = [col.rstrip('_') for col in self.volontaire_df.columns]
        
        # Remove trailing periods
        self.volontaire_df.columns = [col.rstrip('.') for col in self.volontaire_df.columns]
        
        self.logger.info("Cleaned column names (trailing _ and . removed)")

    def _drop_columns(self) -> None:
        """Replicate notebook column dropping from cells 419, 428-429, 439-440"""
        columns_to_drop = [
            'Horodateur',
            'Si_oui_preciser_la_date_du_dernier_don',
            'Date_de_dernières_règles_(DDR)',
            'Autre_raisons,__preciser',
            'Sélectionner_"ok"_pour_envoyer',
            'Si_autres_raison_préciser'
        ]
        
        self.volontaire_df.drop(
            columns=columns_to_drop,
            errors='ignore',
            inplace=True
        )
        self.logger.info("Dropped columns as per notebook")

    def _handle_numeric_columns(self) -> None:
        """Replicate numeric handling from cells 422-429"""
        # Convert to numeric as in notebook cell 422
        numeric_cols = ['Age', 'Poids', 'Taille']
        for col in numeric_cols:
            self.volontaire_df[col] = pd.to_numeric(
                self.volontaire_df[col], 
                errors='coerce'
            )
        
        # Handle Poids as in cell 423
        poids_mean = self.volontaire_df['Poids'].mean()
        self.volontaire_df['Poids'] = self.volontaire_df['Poids'].fillna(poids_mean)

        # Handle Taile as in cell 423
        taille_mean = self.volontaire_df['Taille'].mean()
        self.volontaire_df['Taille'] = self.volontaire_df['Taille'].fillna(taille_mean)
        
        # Handle Age as in cell 424
        age_mean = self.volontaire_df['Age'].mean()
        self.volontaire_df['Age'] = self.volontaire_df['Age'].fillna(age_mean)
        
        # Handle Taux d'hémoglobine as in cell 450
        self.volontaire_df['Taux_d’hémoglobine'] = pd.to_numeric(
            self.volontaire_df['Taux_d’hémoglobine'],
            errors='coerce'
        )
        taux_mean = self.volontaire_df['Taux_d’hémoglobine'].mean().round(1)
        self.volontaire_df['Taux_d’hémoglobine'] = self.volontaire_df['Taux_d’hémoglobine'].fillna(taux_mean)
        
        self.logger.info("Processed numeric columns (Age, Poids, Taux_d’hémoglobine)")

    def _process_raison_columns(self) -> None:
        """Replicate Raison column processing from cells 430-444"""
        # First fill NA with empty string as in notebook cell 431
        self.volontaire_df[self.raison_columns] = self.volontaire_df[self.raison_columns].fillna('')
        
        # Then replace empty strings with 'Non' as in cell 441
        self.volontaire_df[self.raison_columns] = self.volontaire_df[self.raison_columns].replace('', 'Non')
        
        # Special handling for Scarifié column as in cells 435-444
        if 'Raison_de_non-eligibilité_totale__[Scarifié]' in self.volontaire_df:
            scarifie_col = 'Raison_de_non-eligibilité_totale__[Scarifié]'
            self.volontaire_df[scarifie_col] = self.volontaire_df[scarifie_col].replace('', 'Non')
        
        self.logger.info("Processed Raison columns (empty→Non)")

    def _clean_geographic_columns(self) -> None:
        """Replicate geographic cleaning from cell 452"""
        arrondissement_col = 'Arrondissement_de_résidence'
        self.volontaire_df[arrondissement_col] = self.volontaire_df[arrondissement_col].str.replace(
            r'\s*\(Non précisé \)', 
            '', 
            regex=True
        )
        self.logger.info("Cleaned Arrondissement_de_résidence column")

    def _calculate_bmi(self) -> None:
        """Calculate BMI and add it as a new column"""
        self.volontaire_df["IMC"] = (self.volontaire_df["Poids"] / (self.volontaire_df["Taille"] / 100) ** 2).round(2)
        self.logger.info("Calculated BMI and added as a new column")

    def _feature_engineering(self) -> None:
        """Replicate feature engineering from notebook"""
        # Fréquence_de_don
        self.volontaire_df["Fréquence_de_don"] = self.volontaire_df["A-t-il_(elle)_déjà_donné_le_sang"].apply(lambda x: 1 if x == 'Oui' else 0)

        # Groupe_d'âge
        bins = [18, 25, 35, 45, 55, 65, 75, 85, 95]
        labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76-85', '86-95']
        self.volontaire_df["Groupe_d'âge"] = pd.cut(self.volontaire_df["Age"], bins=bins, labels=labels, right=False)

        # Catégorie_d'IMC
        IMC_bins = [0, 18.5, 24.9, 29.9, 39.9, 100]
        IMC_labels = ['Insuffisance pondérale', 'Poids normal', 'Surpoids', 'Obèse', 'Obésité sévère']
        self.volontaire_df["Catégorie_d'IMC"] = pd.cut(self.volontaire_df["IMC"], bins=IMC_bins, labels=IMC_labels, right=False)

        # Statut_d'éligibilité
        self.volontaire_df["Statut_d'éligibilité"] = self.volontaire_df["ÉLIGIBILITÉ_AU_DON"].apply(lambda x: 1 if x == 'Eligible' else 0)

        # Catégorie_de_niveau_d'hémoglobine
        hemoglobin_bins = [0, 12, 16, 20]
        hemoglobin_labels = ['Bas', 'Normal', 'Élevé']
        self.volontaire_df["Catégorie_de_niveau_d'hémoglobine"] = pd.cut(self.volontaire_df["Taux_d’hémoglobine"], bins=hemoglobin_bins, labels=hemoglobin_labels, right=False)

        self.logger.info("Completed feature engineering")

    def _reorder_columns(self) -> None:
        """Reorder columns to match notebook output"""
        new_column_order = [
            'ID', 'Age', "Groupe_d'âge", 'Taille', 'Poids', 'IMC', "Catégorie_d'IMC", 'Fréquence_de_don', 'Taux_d’hémoglobine', "Catégorie_de_niveau_d'hémoglobine", "Statut_d'éligibilité", 'ÉLIGIBILITÉ_AU_DON', 'Genre', "Niveau_d'etude", 'Situation_Matrimoniale_(SM)', 'Profession', 'Arrondissement_de_résidence', 'Quartier_de_Résidence', 'Nationalité', 'Religion', 'A-t-il_(elle)_déjà_donné_le_sang', 'Raison_indisponibilité__[Est_sous_anti-biothérapie__]', 'Raison_indisponibilité__[Taux_d’hémoglobine_bas_]', 'Raison_indisponibilité__[date_de_dernier_Don_<_3_mois_]', 'Raison_indisponibilité__[IST_récente_(Exclu_VIH,_Hbs,_Hcv)]', 'Raison_de_l’indisponibilité_de_la_femme_[La_DDR_est_mauvais_si_<14_jour_avant_le_don]', 'Raison_de_l’indisponibilité_de_la_femme_[Allaitement_]', 'Raison_de_l’indisponibilité_de_la_femme_[A_accoucher_ces_6_derniers_mois__]', 'Raison_de_l’indisponibilité_de_la_femme_[Interruption_de_grossesse__ces_06_derniers_mois]', 'Raison_de_l’indisponibilité_de_la_femme_[est_enceinte_]', 'Raison_de_non-eligibilité_totale__[Antécédent_de_transfusion]', 'Raison_de_non-eligibilité_totale__[Porteur(HIV,hbs,hcv)]', 'Raison_de_non-eligibilité_totale__[Opéré]', 'Raison_de_non-eligibilité_totale__[Drepanocytaire]', 'Raison_de_non-eligibilité_totale__[Diabétique]', 'Raison_de_non-eligibilité_totale__[Hypertendus]', 'Raison_de_non-eligibilité_totale__[Asthmatiques]', 'Raison_de_non-eligibilité_totale__[Cardiaque]', 'Raison_de_non-eligibilité_totale__[Tatoué]', 'Raison_de_non-eligibilité_totale__[Scarifié]'
        ]
        self.volontaire_df = self.volontaire_df[new_column_order]
        self.logger.info("Reordered columns to match notebook output")

    def _validate_output(self) -> None:
        """Replicate notebook validation checks"""
        # Check for missing values as in cell 446
        missing_values = self.volontaire_df.isnull().sum()
        columns_with_missing_values = missing_values[missing_values > 0]
        if not columns_with_missing_values.empty:
            self.logger.info(f"Columns with missing values: {columns_with_missing_values}")
            for column in columns_with_missing_values.index:
                most_frequent_value = self.volontaire_df[column].mode()[0]
                self.volontaire_df[column].fillna(most_frequent_value, inplace=True)
            self.logger.info("Filled missing values with the most frequent value")
        
        # Check final column count as per notebook
        if len(self.volontaire_df.columns) != 40:
            self.logger.error(f"Column count mismatch: {len(self.volontaire_df.columns)} vs expected 40")
            raise ValueError("Column count validation failed")
        
        self.logger.info("Validation passed: No missing values, correct column count")

    def process(self) -> Dict[str, pd.DataFrame]:
        """Execute exact notebook processing sequence"""
        processing_steps = [
            self._clean_column_names,
            self._drop_columns,
            self._handle_numeric_columns,
            self._process_raison_columns,
            self._clean_geographic_columns,
            self._calculate_bmi,
            self._feature_engineering,
            self._reorder_columns,
            self._validate_output
        ]
        
        self.logger.info("Starting notebook-exact preprocessing...")
        for step in processing_steps:
            step()
            self.logger.debug(f"Completed step: {step.__name__}")
        
        self.logger.info("Processing completed successfully")
        return self.interim_data

    def save_processed_data(self) -> None:
        """Save processed data matching notebook output"""
        PreprocessConfig.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(PreprocessConfig.OUTPUT_PATH) as writer:
            for sheet_name, df in self.interim_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        self.logger.info(f"Saved processed data to {PreprocessConfig.OUTPUT_PATH}")

if __name__ == "__main__":
    """Command-line usage replicating notebook execution"""
    
    logging.basicConfig(level=logging.INFO)
    
    loader = BloodDonationDataLoader()
    raw_data = loader.load_raw_excel()
    
    preprocessor = BloodDonationPreprocessor(raw_data)
    processed_data = preprocessor.process()
    preprocessor.save_processed_data()