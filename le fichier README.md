# Tableau de Bord de la Campagne de Don du Sang

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue.svg)](docs/mkdocs.yml)

Un tableau de bord complet d'analyse et de visualisation de données pour les campagnes de don du sang, développé pour le Hackathon IndabaX Cameroun 2025. Cet outil aide les organisateurs de campagne à prendre des décisions basées sur les données pour améliorer les initiatives de don du sang grâce à l'analyse en temps réel, au profilage des donneurs et au suivi de l'efficacité des campagnes.

Voici [le lien du projet](https://testsiteg.pythonanywhere.com/) pour vérifier si vous êtes éligible au don de sang.

Voici l'aperçu du tableau de bord : [Aperçu du tableau de bord](../reports/Dashboard_Overview_French.md)

## 🎯 Aperçu du Projet

Le Tableau de Bord de la Campagne de Don du Sang répond aux défis critiques de la gestion des dons de sang en fournissant :

- Une analyse en temps réel de l'efficacité des campagnes
- Une analyse du comportement et de la fidélisation des donneurs
- Une visualisation de la distribution géographique
- Un suivi des indicateurs de santé
- Des informations démographiques

### 🌟 Fonctionnalités Clés

- **Analyse Géographique**

- Cartes interactives montrant la distribution des donneurs
- Tendances des dons par région
- Identification des zones mal desservies

- **Informations Démographiques**

- Analyse de la distribution par âge et par sexe
- Suivi de la contribution par secteur professionnel
- Reconnaissance des tendances socio-économiques

- **Indicateurs de Santé**

- Suivi du taux d'éligibilité
- Analyse de l'impact des conditions de santé
- Surveillance de l'IMC et du taux d'hémoglobine

- **Efficacité des Campagnes**

- Visualisation du taux de succès
- Analyse des tendances temporelles
- Métriques de contribution démographique

- **Fidélisation des Donneurs**

- Suivi des donneurs réguliers
- Analyse des schémas d'engagement
- Visualisation du taux de fidélisation

### 📊 Aperçu du Tableau de Bord

### Distribution Géographique
    - Cartographie régionale des donneurs
    - Analyse de la densité de population
    - Métriques basées sur la localisation

### Top 10 des quartiers dans la sous-division, dans (ce cas Douala 5)
![Top 10 des quartiers dans la sous-division, dans (ce cas Douala 5)](reports/figures/geagraphic_distribution.png)

### Top 10 des sous-divisions dans la région, dans (ce cas Littoral)
![Top 10 des sous-divisions dans la région, dans (ce cas Littoral)](reports/figures/top_10_subdivision.png)

### Profilage des Donneurs
    - Analyse démographique
    - Impact des conditions de santé
    - Tendances de fidélisation
    - Impact des facteurs médicaux

### Distribution Démographique par Âge et Sexe
![Distribution Démographique par Âge et Sexe](reports/figures/age_gender.png)

### Distribution Démographique par Profession et Niveau d'Éducation et Catégorie d'IMC
![Distribution Démographique par Profession et Niveau d'Éducation et Catégorie d'IMC](reports/figures/professional_educational_bmi.png)

### Analyse de l'impact des conditions de santé
![Analyse de l'impact des conditions de santé](reports/figures/health_impact.png)

### Résumé des Conditions de Santé
![Résumé des Conditions de Santé](reports/figures/health_summary.png)

### Analyse des Campagnes
    - Tendances temporelles
    - Métriques de succès
    - Contributions démographiques

### Métriques de Contribution Démographique
![Métriques de Contribution Démographique](reports/figures/demographic_contribution.png)

## 🚀 Démarrage

### Prérequis   
    - Python 3.8+
    - Gestionnaire de paquets pip
    - Make (facultatif, pour l'utilisation des commandes Makefile)

### Installation
1. Cloner le dépôt :
```bash
git clone [https://github.com/yourusername/blood-donation-dashboard.git](https://github.com/yourusername/blood-donation-dashboard.git)
cd blood-donation-dashboard

2. Créer et activer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Exécuter le tableau de bord:
```bash
streamlit run src/dashboard.py
```

### 🛠️ Développement

*Exécution des Tests*
```bash
python -m pytest tests/
```

*Style de Code*
Ce projet suit les directives PEP 8. Pour vérifier le style du code:
```bash
flake8 src/
``` 

### 📂 Détails des Répertoires
- **`data/`**: Stocke tous les fichiers de données du projet
    - `raw/`: Données originales et immuables
    - `processed/`: Données propres et prêtes pour l'analyse
    - `interim/`: Étapes de traitement intermédiaires
    - `external/`: Données provenant de sources tierces

- **`src/`**: Code source principal
    - `app.py`: Application principale du tableau de bord Streamlit
    - `data_loader.py`: Utilitaires de chargement des données
    - `data_preprocessor.py`: Pipeline de prétraitement des données

- **`notebooks/`**: Notebooks Jupyter pour l'analyse
    - Exploration des données
    - Développement de modèles
    - Expériences de visualisation

- **`models/`**: Modèles entraînés et artefacts
    - Modèles Random Forest
    - Objets de prétraitement des modèles
    - Instantanés des données d'entraînement

- **`tests/`**: Tests unitaires et données de test
    - Couverture des tests pour les fonctionnalités principales
    - Tests d'intégration
    - Fixtures de test

- **`docs/`**: Documentation du projet

- Spécifications techniques
- Documentation API
- Guides d'utilisation

### 🔧 Fichiers de Configuration

- `pyproject.toml`: Métadonnées du projet et configuration de la construction
- `requirements.txt`: Dépendances des packages Python
- `Makefile`: Automatisation de la construction et tâches de développement
- `.env`: Variables d'environnement (non suivies par le contrôle de version)
- `setup.cfg`: Configurations spécifiques aux outils


### 🔧 Fichiers de Configuration

- `pyproject.toml`: Métadonnées du projet et configuration de la construction
- `requirements.txt`: Dépendances des packages Python
- `Makefile`: Automatisation de la construction et tâches de développement
- `.env`: Variables d'environnement (non suivies par le contrôle de version)
- `setup.cfg`: Configurations spécifiques aux outils

Ajoutez cette section à votre README.md pour fournir un aperçu clair de l'organisation et de la structure du projet.

### 🤝 Contribution
Les contributions sont les bienvenues ! Veuillez lire nos Directives de Contribution pour plus de détails sur la manière de soumettre des demandes dePull, de signaler des problèmes et de contribuer au projet.

### 🙏 Remerciements

- Organisateurs du Hackathon IndabaX Cameroun 2025
- Développeurs contributeurs
- Organisations de don du sang pour leur expertise du domaine

### 📞 Contact

Pour toute question ou assistance, veuillez [ouvrir un problème](https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard/issues) ou contacter les responsables: 

- Chef de Projet: [Alphonse Brandon](https://github.com/AlphonseBrandon)
- Responsable Technique: [PetraAG](https://github.com/PetraAG)
