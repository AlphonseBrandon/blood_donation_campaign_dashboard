# @title
# -*- coding: utf-8 -*-
"""
Streamlit Dashboard for Blood Donor Data Analysis and Clustering.

Enhanced UI for exploring blood donor data, performing K-means clustering,
and predicting cluster for new user inputs.  UI is restructured to be more
organized and visually appealing, resembling a professional dashboard layout.
"""

import streamlit as st
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.stats import chi2_contingency
import matplotlib

# ----------------------------------------------------------------------
#                       DATA LOADING AND PREPROCESSING (No UI changes here)
# ----------------------------------------------------------------------

path = Path('data/processed/processed.xlsx')

try:
    df = pd.read_excel(path)
    print("Data loaded successfully from:", path) # Keep for initial debugging if needed
except FileNotFoundError:
    print(f"Error: {path} not found.") # Keep for initial debugging if needed
    df = None
except Exception as e:
    print(f"An error occurred during data loading: {e}") # Keep for initial debugging if needed
    df = None

if df is not None:
    # --- Preprocessing functions (No UI changes here) ---
    def clip_text ( text , max_len = 2):
        text = str( text ).strip( )
        if len(text) > max_len :
            return text[:max_len]
        return text
    def remove_0_entries( text ,   replace ):
        text = int(str(text).strip())
        if text == 0 :
            return int(replace)
        return text
    def replace_nulity(text, replace ):
        text = str(text).strip()
        if text.upper() == 'NULL' or text =='nan' or text == '' or pd.isnull(text) :
            return replace
        return text
    def parse_date(date_str , format = '%Y-%m-%d'):
        date_str = date_str.split (' ')[0]
        try:
            return pd.to_datetime(date_str, format= format, errors='raise')
        except ValueError:
            try:
                return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M', errors='raise')
            except ValueError:
                return pd.NaT
    def remove_special_charecters (value):
        value = str(value)
        value = re.sub(r'[^a-zA-Z0-9\s+-]', '', value)
        return value
    def one_hot_encode_column(column, drop_first=True, use_sklearn=False):
        if isinstance(column, np.ndarray):
            column = pd.Series(column)
        if not use_sklearn:
            encoded = pd.get_dummies(column, drop_first=drop_first, dtype=int)
            return np.array(encoded)
        else:
            encoder = OneHotEncoder(drop='first' if drop_first else None, sparse_output=False)
            encoded = encoder.fit_transform(column.values.reshape(-1, 1))
            encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out([column.name]))
            return encoded_df
    def cramers_v(x, y):
        x = np.array(x)
        y = np.array(y)
        contingency_table = pd.crosstab(x, y)
        chi2 = chi2_contingency(contingency_table)[0]
        n = contingency_table.sum().sum()
        phi2 = chi2 / n
        r, k = contingency_table.shape
        phi2corr = max(0, phi2)
        rcorr = r - ((r - 1) ** 2) / (n - 1)
        kcorr = k - ((k - 1) ** 2) / (n - 1)
        if min((kcorr - 1), (rcorr - 1)) < 0:
            raise ValueError("Cramér's V is not defined for this contingency table.")
        cramers_v = np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))
        return cramers_v

    # --- Sheet Class (Corrected plot_correlation_matrix and no UI changes here) ---
    class Sheet:
        def __init__(self, name, new_column_names = None):
            self.name = name
            self.pre_processing_functions = [ ]
            self.sheet = pd.read_excel(path, sheet_name=name)
            self.old_column_names = self.sheet.columns.tolist()
            self.lang = 'fr'
            if new_column_names:
              self.rename_columns(new_column_names)
            self.cluster_colors = {}
        def toggle_names(self):
            temp = self.old_column_names
            if self.lang == 'fr':
                self.lang = 'en'
            else:
                self.lang = 'fr'
            self.old_column_names = self.sheet.columns.tolist()
            self.rename_columns(temp, lang=self.lang)
        def get_column(self, column_name):
            return self.sheet[column_name].values
        def add_pre_processing_function(self, function):
            if isinstance(function, list):
                self.pre_processing_functions.extend(function)
            else:
                self.pre_processing_functions.append(function)
        def apply_pre_processing_functions(self, clear_on_applied=True):
            for function in self.pre_processing_functions:
                function(self)
            if clear_on_applied:
                self.pre_processing_functions = []
        def preprocess_column(self, column_name=None, process_function=lambda text: text, excludes=None):
            if excludes is None:
                excludes = []
            if column_name is None:
                for col_name in self.sheet.columns:
                    if col_name not in excludes:
                        self.sheet[col_name] = self.sheet[col_name].apply(process_function)
            else:
                self.sheet[column_name] = self.sheet[column_name].apply(process_function)
            return self.get_columns()
        def preprocess_columns(self, columns=None, excludes=None, process_function=replace_nulity):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            for column_name in columns:
                if column_name not in excludes:
                    most_frequent_value = self.get_most_frequent(column_name)
                    process_func_with_replace = lambda value: process_function(value, most_frequent_value)
                    self.sheet[column_name] = self.sheet[column_name].apply(process_func_with_replace)
        def get_most_frequent(self, column_name):
            return self.sheet[column_name].value_counts().idxmax()
        def count_nulls(self, column_name):
            return self.sheet[column_name].isnull().sum()
        def count_value(self, column_name, value=''):
            return (self.sheet[column_name] == value).sum()
        def get_records_in_column(self, column_name):
            return self.sheet[column_name].tolist()
        def get_column_details(self, column_name, show_contents=True):
            value_counts = self.sheet[column_name].value_counts(dropna=False)
            st.write(f"Nulls count : {self.count_nulls(column_name)}")
            st.write(f"Unique values in column '{column_name}':")
            st.write(value_counts)
        def display_fields(self):
            for column_name in self.sheet.columns:
                st.write(f'\n\n_______ {column_name.title()} ______\n')
                self.get_column_details(column_name)
        def get_columns(self):
            columns = self.sheet.columns.tolist()
            if 'cluster' in columns:
                columns.remove('cluster')
            return columns
        def rename_columns(self, new_column_names, lang='fr'):
            self.lang = lang
            self.old_column_names = self.sheet.columns.tolist()
            if isinstance(new_column_names, list):
                new_column_names = {self.sheet.columns[i]: new_column_names[i] for i in range(len(new_column_names))}
            self.sheet.rename(columns=new_column_names, inplace=True)
        def translate_columns(self, preprocess=lambda text: text, lang='en'):
            self.lang = lang
            self.old_column_names = self.sheet.columns.tolist()
            for col in self.sheet.columns:
                pass
            return self.get_columns()
        def get_group(self, column_name):
            return self.sheet[column_name].unique()
        def get_hot_encoded(self, column_name):
            return one_hot_encode_column(self.get_column(column_name))
        def plot_frequency(self, column_name):
            records = self.get_group(column_name)
            fig, ax = plt.subplots()
            ax.bar(records, self.sheet[column_name].value_counts())
            plt.xticks(rotation=45, ha='right', fontsize=7)
            plt.xlabel(column_name)
            plt.ylabel('Frequency')
            plt.title(f'Frequency of {column_name}')
            plt.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
            st.pyplot(fig)
            total_records = len(self.sheet)
            value_counts = self.sheet[column_name].value_counts()
            st.write("#### Class Distribution (Percentage):")
            for value, count in value_counts.items():
                percentage = (count / total_records) * 100
                st.write(f"- **{value}**: {percentage:.2f}% ({count} records)")
        def get_correlation_matrix(self, columns=None, excludes=None):
            """Calculates and returns the correlation matrix for specified NUMERIC columns."""
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            for name in excludes:
                if name in columns:
                    columns.remove(name)

            # --- Select only numeric columns for correlation calculation ---
            numeric_columns = self.sheet[columns].select_dtypes(include=np.number).columns.tolist()

            # --- DEBUGGING: Print columns used for correlation ---
            st.write("Numeric columns used for correlation matrix calculation:")
            st.write(numeric_columns)

            if not numeric_columns:
                st.warning("No numeric columns selected for correlation matrix. Please choose numeric features.")
                return pd.DataFrame()  # Return empty DataFrame if no numeric columns

            correlation_matrix = self.sheet[numeric_columns].corr()
            return correlation_matrix

        def plot_correlation_matrix(self, columns=None, excludes=None):
            """Plots the correlation matrix as a heatmap."""
            corr_matrix = self.get_correlation_matrix(columns=columns, excludes=excludes)

            if corr_matrix.empty: # Check if matrix is empty (e.g., no numeric columns)
                st.warning("Cannot display heatmap as correlation matrix is empty.")
                return

            # --- DEBUGGING: Display the correlation matrix before plotting ---
            st.subheader("Correlation Matrix Data (for debugging)")
            st.dataframe(corr_matrix)  # Display the matrix in Streamlit


            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
            plt.title('Correlation Matrix', fontsize=14)
            st.pyplot(fig)
        def determine_optimal_k(self, columns=None, excludes=None, max_k=10):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            for name in excludes:
                if name in columns:
                    columns.remove(name)
            data = self.sheet[columns].copy()
            string_columns = data.select_dtypes(include=['object']).columns
            encoded_data = data.copy()
            for col in string_columns:
                encoder = pd.get_dummies(data[col], prefix=col, drop_first=True, dtype=int)
                encoded_data = pd.concat([encoded_data, encoder], axis=1).drop(col, axis=1)
            sse_values = []
            for k in range(1, max_k + 1):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(encoded_data)
                sse_values.append(kmeans.inertia_)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(range(1, max_k + 1), sse_values, marker='o', color='skyblue')
            plt.title('Elbow Method for Optimal K', fontsize=14)
            plt.xlabel('Number of Clusters (K)', fontsize=12)
            plt.ylabel('Sum of Squared Errors (SSE)', fontsize=12)
            st.pyplot(fig)
        def perform_kmeans_clustering(self, k, columns=None, excludes=None, show_plot=True):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            columns = [col for col in columns if col not in excludes]
            data = self.sheet[columns].copy()
            string_cols = data.select_dtypes(include=['object']).columns
            encoded_data = data.copy()
            self.encoders_kmeans = {}
            for col in string_cols:
                encoder = LabelEncoder()
                encoded_data[col] = encoder.fit_transform(encoded_data[col].astype(str))
                self.encoders_kmeans[col] = {'encoder': encoder, 'classes': encoder.classes_}
            scaler = StandardScaler()
            scaled_encoded_data = scaler.fit_transform(encoded_data)
            self.scaler_kmeans = scaler
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            self.kmeans_model = kmeans.fit(scaled_encoded_data)
            self.sheet['cluster'] = self.kmeans_model.labels_
            cluster_labels = sorted(self.sheet['cluster'].unique())
            num_clusters = len(cluster_labels)
            colors = px.colors.qualitative.Plotly[:num_clusters]
            self.cluster_colors = dict(zip(cluster_labels, colors))
            if show_plot:
                pca = PCA(n_components=3)
                pca_result = pca.fit_transform(scaled_encoded_data)
                pca_df = pd.DataFrame(pca_result, columns=['pca_1', 'pca_2', 'pca_3'])
                pca_df['cluster'] = self.sheet['cluster']
                for col in columns:
                    pca_df[col] = self.sheet[col].values
                fig = px.scatter_3d(
                    pca_df,
                    x='pca_1', y='pca_2', z='pca_3',
                    color='cluster',
                    color_discrete_map=self.cluster_colors,
                    hover_data=[col for col in pca_df.columns if col not in ['pca_1', 'pca_2', 'pca_3']],
                    title=f'K-Means Clusters (K={k}) with PCA Reduction'
                )
                centroids_pca = pca.transform(self.kmeans_model.cluster_centers_)
                fig.add_scatter3d(
                    x=centroids_pca[:, 0],
                    y=centroids_pca[:, 1],
                    z=centroids_pca[:, 2],
                    mode='markers',
                    marker=dict(size=6, color='black', symbol='x'),
                    name='Centroids'
                )
                st.plotly_chart(fig)
                cluster_counts = self.sheet['cluster'].value_counts()
                total_records = len(self.sheet)
                st.write("#### Cluster Distribution (Percentage):")
                for cluster_label, count in cluster_counts.items():
                    percentage = (count / total_records) * 100
                    st.write(f"- **Cluster {cluster_label}**: {percentage:.2f}% ({count} records)")
            return self.sheet
        def continuos_correlation(self, column1, column2):
            if column1 not in self.sheet.columns or column2 not in self.sheet.columns:
                raise ValueError(f"Columns missing: {column1} or column2")
            x = self.sheet[column1]
            y = self.sheet[column2]
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(x, y, alpha=0.7, label='Data Points', color='skyblue')
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            ax.plot(x, p(x), "r--", label=f"Trendline (y={z[0]:.2f}x+{z[1]:.2f})", color='coral')
            plt.title(f"Scatterplot of {column1} vs {column2}", fontsize=14)
            plt.xlabel(column1, fontsize=12)
            plt.ylabel(column2, fontsize=12)
            plt.legend()
            st.pyplot(fig)
        def binary_continous_correlation(self, column1, column2):
            if column1 not in self.sheet.columns or column2 not in self.sheet.columns:
                raise ValueError(f"Columns missing: {column1} or column2")
            df_corr = self.sheet[[column1, column2]].copy()
            encoders = {}
            for col in [column1, column2]:
                if df_corr[col].dtype == 'object':
                    le = LabelEncoder()
                    df_corr[col] = le.fit_transform(df_corr[col].astype(str))
                    encoders[col] = le
            # --- Calculate Pearson correlation and p-value ---
            from scipy.stats import pearsonr
            corr, p_value = pearsonr(df_corr[column1], df_corr[column2])

            fig = px.scatter(df_corr, x=column1, y=column2,
                             title=f"{column1} vs {column2} Correlation",
                             labels={column1: column1, column2: column2},
                             trendline="ols",
                             trendline_color_override='coral',
                             color_discrete_sequence=['skyblue'],
                             hover_data=df_corr.columns.tolist())


            fig.add_annotation(text=f"Pearson r: {corr:.2f}, p-value: {p_value:.3f}", # Display p-value
                               xref="paper", yref="paper",
                               x=0.05, y=0.95, showarrow=False)

            for col, encoder in encoders.items():
                fig.update_layout(**{
                    f'xaxis' if col == column1 else 'yaxis': {
                        'tickvals': list(range(len(encoder.classes_))),
                        'ticktext': encoder.classes_
                    }
                })
            st.plotly_chart(fig)
        def categorical_categorical_correlation(self, column1, column2):
            if column1 not in self.sheet.columns or column2 not in self.sheet.columns:
                raise ValueError(f"Columns missing: {column1} or column2")
            cross_tab = pd.crosstab(self.sheet[column1], self.sheet[column2])
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(cross_tab, annot=True, fmt='d', cmap="viridis", ax=ax)
            plt.title(f'Counts of {column1} vs {column2}', fontsize=14)
            plt.xlabel(column2, fontsize=12)
            plt.ylabel(column1, fontsize=12)
            st.pyplot(fig)
        def color_rows_by_cluster(self, df_row):
            cluster_value = df_row['cluster']
            color = self.cluster_colors.get(cluster_value, '#ffffff')
            return [f'background-color: {color}'] * len(df_row)
        def predict_cluster(self, user_data):
            user_df = pd.DataFrame([user_data])
            encoded_features_list = []
            string_cols_kmeans = self.encoders_kmeans.keys()
            for field in relevant_fields:
                if field in string_cols_kmeans:
                    encoder_data = self.encoders_kmeans[field]
                    encoder = encoder_data['encoder']
                    classes = encoder_data['classes']
                    if field in user_df.columns:
                        category = user_df[field].astype(str).iloc[0]
                        if category not in classes:
                            st.error(f"Error: Category '{category}' in column '{field}' was not seen during training. Please choose from: {', '.join(classes)}")
                            return None
                        encoded_value = encoder.transform([category])
                        encoded_features_list.extend(encoded_value)
                    else:
                        st.error(f"Error: Missing categorical feature '{field}' for prediction.")
                        return None
                elif field in user_df.columns:
                    numerical_value = user_df[field].iloc[0]
                    encoded_features_list.append(numerical_value)
                else:
                    st.error(f"Error: Missing numerical feature '{field}' for prediction.")
                    return None
            user_input_encoded = np.array(encoded_features_list).reshape(1, -1)
            if hasattr(self, 'scaler_kmeans'):
                user_input_scaled = self.scaler_kmeans.transform(user_input_encoded)
            else:
                user_input_scaled = user_input_encoded
                st.warning("Warning: No scaler found. Prediction might be less accurate. Re-run clustering to fit scaler.")
            if user_input_encoded.shape[1] != self.kmeans_model.n_features_in_:
                st.error(f"Feature mismatch in prediction: Input has {user_input_encoded.shape[1]} features, but model expects {self.kmeans_model.n_features_in_}")
                return None
            predicted_cluster = self.kmeans_model.predict(user_input_scaled)[0]
            return predicted_cluster
        def generate_cluster_insights_table(self, cluster_column_name, columns_for_insight):
            insights = {}
            cluster_col = self.sheet[cluster_column_name]
            for column in columns_for_insight:
                target_col = self.sheet[column]
                if pd.api.types.is_numeric_dtype(target_col):
                    groups = self.sheet.groupby(cluster_col)[column].apply(list)
                    if len(groups) >= 2:
                        grand_mean = self.sheet[column].mean()
                        ss_between = sum([len(g) * (np.mean(g) - grand_mean)**2 for g in groups])
                        ss_total = sum((self.sheet[column] - grand_mean)**2)
                        eta = np.sqrt(ss_between / ss_total) if ss_total != 0 else 0
                        means = [np.mean(g) for g in groups]
                        direction = np.sign(means[1] - means[0]) if len(means) >= 2 else 1
                        insights[column] = eta * direction
                    else:
                        insights[column] = np.nan
                else:
                    insights[column] = cramers_v(target_col, cluster_col)
            insights_df = pd.DataFrame.from_dict(insights, orient='index', columns=['Association with Cluster'])
            return insights_df.fillna(0)
        def display_styled_insights_table(self, insights_df):
            def color_scale_association(val):
                vmin = -1
                vmax = 1
                norm_val = (val - vmin) / (vmax - vmin) if vmin != vmax else 0.5
                cmap = plt.cm.coolwarm
                rgba = cmap(norm_val)
                hex_color = matplotlib.colors.rgb2hex(rgba)
                return f'background-color: {hex_color}'
            styled_df = insights_df.style.background_gradient(cmap='coolwarm', axis=0, subset=['Association with Cluster'], vmin=-1, vmax=1).format("{:.2f}", subset=['Association with Cluster'])
            st.dataframe(styled_df)

    # --- Relevant Fields and Excludes (No UI changes here) ---
    fr_relevant_fields = [
        'Groupe_d\'âge',
        'Taux_d’hémoglobine',
        "Catégorie_d'IMC",
        'Profession',
        'Raison_de_non-eligibilité_totale__[Antécédent_de_transfusion]',
        'Raison_de_non-eligibilité_totale__[Porteur(HIV,hbs,hcv)]',
        'Raison_de_non-eligibilité_totale__[Opéré]',
        'Raison_de_non-eligibilité_totale__[Drepanocytaire]',
        'Raison_de_non-eligibilité_totale__[Diabétique]',
        'Raison_de_non-eligibilité_totale__[Hypertendus]',
        'Raison_de_non-eligibilité_totale__[Asthmatiques]',
        'Raison_de_non-eligibilité_totale__[Cardiaque]',
        'Raison_de_non-eligibilité_totale__[Tatoué]',
        'Raison_de_non-eligibilité_totale__[Scarifié]'
    ]
    relevant_fields = fr_relevant_fields
    excludes = [
        'id',
        'study_level',
        'gender',
        'age',
        'situation_matrimonial_(sm)',
        'situation_matrimonial_(sm)',
        'arrondissement_de_residence',
        'residency_district',
        'nationality',
        'religion',
    ]

    sVoluntaire = Sheet('Volontaire')
    funcs = [
        lambda sheet: sheet.preprocess_column('Taux_d’hémoglobine', lambda value: value / 10 if isinstance(value, (int, float)) and value > 100 else value),
        lambda sheet: sheet.preprocess_columns(columns = ['Groupe_d\'âge']),
    ]
    sVoluntaire.add_pre_processing_function(funcs)
    sVoluntaire.apply_pre_processing_functions()

    # ----------------------------------------------------------------------
    #                       STREAMLIT APP - UI RESTRUCTURED AND FIXED
    # ----------------------------------------------------------------------

    st.title("Blood Donor Data Dashboard")
    st.sidebar.header("Clustering Configuration")

    # --- Sidebar Controls ---
    k_value = st.sidebar.slider("Number of Clusters (K)", min_value=2, max_value=10, value=4)
    elbow_plot_toggle = st.sidebar.checkbox("Show Elbow Plot for K", False)
    show_dataset_toggle = st.sidebar.checkbox("Show Clustered Dataset", False)

    if st.sidebar.button("Re-run Clustering"):
        with st.spinner(f'Re-running K-Means Clustering with K={k_value}...'):
            clustered_sheet = sVoluntaire.perform_kmeans_clustering(k_value, columns=relevant_fields, excludes=excludes, show_plot=True)
            st.success(f'K-Means Clustering with K={k_value} completed!')
    else:
        with st.spinner(f'Initial K-Means Clustering with K=4...'):
             clustered_sheet = sVoluntaire.perform_kmeans_clustering(4, columns=relevant_fields, excludes=excludes, show_plot=True)
             st.success(f'Initial K-Means Clustering with K=4 completed!')

    st.sidebar.markdown("---")
    st.sidebar.info("Adjust clustering parameters here. Defaults are generally optimal for initial exploration.")

    st.header("Explore Data and Cluster Analysis")

    # --- Tabbed Analysis Interface ---
    analysis_tab = st.tabs([
        "Cluster Visualization", "Correlation Analysis", "Column Analysis",
        "Cluster Insights", "Predict Group"
    ])

    with analysis_tab[0]: # Cluster Visualization Tab
        st.subheader("K-Means Cluster Visualization")
        st.write("Interactive 3D visualization of donor clusters after PCA dimensionality reduction.")

        col1, col2 = st.columns([2, 1])
        with col1:
            # Visualization plot from perform_kmeans_clustering is already shown here
            if elbow_plot_toggle: # Conditionally show Elbow plot - CORRECTED PLACEMENT
                st.subheader("Elbow Plot for Optimal K")
                sVoluntaire.determine_optimal_k(columns=relevant_fields, excludes=excludes, max_k=10)

        with col2:
            if show_dataset_toggle: # Conditionally show dataset - CORRECTED PLACEMENT
                st.subheader("Clustered Dataset")
                st.write("##### Cluster Color Key:")
                for cluster_label, color in sVoluntaire.cluster_colors.items():
                    st.markdown(f"<span style='color:{color}; font-size: 1.5em;'>Cluster {cluster_label}</span>: <span style='background-color:{color}; display:inline-block; width: 1em; height: 1em; border: 1px solid black; vertical-align: middle;'></span> Group {cluster_label+1} Donors", unsafe_allow_html=True)
                styled_dataset = sVoluntaire.sheet.style.apply(sVoluntaire.color_rows_by_cluster, axis=1)
                st.dataframe(styled_dataset)

    with analysis_tab[1]: # Correlation Analysis Tab
        st.subheader("Feature Correlation Analysis")
        correlation_analysis_type = st.selectbox("Select Correlation Analysis:",
                                                 ["Correlation Matrix Heatmap", "Column Correlation Plot"])

        if correlation_analysis_type == "Correlation Matrix Heatmap":
            st.subheader("Correlation Matrix Heatmap")
            st.write("Heatmap displaying feature correlations. Darker/lighter colors indicate stronger positive/negative correlations.")
            sVoluntaire.plot_correlation_matrix(relevant_fields, excludes=excludes)
            st.subheader("Correlation Matrix Table")
            corr_matrix_df = sVoluntaire.get_correlation_matrix(columns=relevant_fields, excludes=excludes)
            st.dataframe(corr_matrix_df)

        elif correlation_analysis_type == "Column Correlation Plot":
            st.subheader("Column Correlation Plot")
            st.write("Explore correlation between two selected columns with scatter plots or heatmaps based on data types.")
            st.info("""Correlation values range from -1 to 1...""")
            with st.expander ("More Insights on Correlation Values"):
                st.write("""- **Strong Positive Correlation (0.7 to 1.0):** ...""")

            col1 = st.selectbox("Select First Column:", relevant_fields, key="col1_corr")
            col2 = st.selectbox("Select Second Column:", relevant_fields, key="col2_corr")

            if col1 and col2 and col1 != col2:
                if pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col1]) and pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col2]):
                    sVoluntaire.continuos_correlation(col1, col2)
                elif (pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col1]) and sVoluntaire.sheet[col2].dtype == 'object') or \
                     (sVoluntaire.sheet[col1].dtype == 'object' and pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col2])):
                    sVoluntaire.binary_continous_correlation(col1, col2)
                elif sVoluntaire.sheet[col1].dtype == 'object' and sVoluntaire.sheet[col2].dtype == 'object':
                    sVoluntaire.categorical_categorical_correlation(col1, col2)
                else:
                    st.warning("Plot type is automatically selected based on column data types.")
            elif col1 == col2:
                st.warning("Please select two different columns for correlation plot.")
            else:
                st.info("Select two columns to visualize their correlation.")

    with analysis_tab[2]: # Column Analysis Tab
        st.subheader("Individual Column Analysis")
        st.write("Explore frequency distribution and class distribution for each feature.")
        selected_column_freq = st.selectbox("Select Column for Frequency Analysis:", relevant_fields)
        sVoluntaire.plot_frequency(selected_column_freq)

    with analysis_tab[3]: # Cluster Insights Tab
        st.subheader("Cluster Feature Insights")
        st.write("Table showing feature associations with clusters, indicating feature importance and direction of influence.")
        default_insight_columns = relevant_fields
        all_columns_available = sVoluntaire.get_columns()
        include_all_columns = st.checkbox("Expand Insights to All Features", False)
        if include_all_columns:
            columns_to_show_insights = all_columns_available
        else:
            columns_to_show_insights = default_insight_columns
        insights_df = sVoluntaire.generate_cluster_insights_table('cluster', columns_to_show_insights)
        if not insights_df.empty:
            sVoluntaire.display_styled_insights_table(insights_df)
        else:
            st.warning("No cluster insights could be generated. Please check your data and column selections.")

    with analysis_tab[4]: # Predict Group Tab
        st.subheader("Predict Donor Group")
        st.write("Enter donor characteristics to predict the likely donor group based on the clustering model.")
        user_input_data = {}
        for field in relevant_fields:
            if sVoluntaire.sheet[field].dtype == 'object':
                unique_vals = [''] + list(sVoluntaire.get_group(field))
                user_input_data[field] = st.selectbox(f"{field.replace('_', ' ').title()}:", unique_vals)
            elif sVoluntaire.sheet[field].dtype in ['int64', 'float64']:
                min_val = float(sVoluntaire.sheet[field].min())
                max_val = float(sVoluntaire.sheet[field].max())
                user_input_data[field] = st.number_input(f"{field.replace('_', ' ').title()}:", min_value=min_val, max_value=max_val, value=(min_val + max_val)/2.0)
            else:
                user_input_data[field] = st.text_input(f"{field.replace('_', ' ').title()}:", "")

        if st.button("Predict Donor Group"):
            with st.spinner('Predicting donor group...'):
                predicted_cluster = sVoluntaire.predict_cluster(user_input_data)
                if predicted_cluster is not None:
                    st.write(f"### Predicted Donor Group: **Group {predicted_cluster + 1}**")

                    st.subheader("Group Insights")
                    cluster_description = {
                        0: "Likely a **Group 1** donor.",
                        1: "Likely belongs to **Group 2**.",
                        2: "Likely belongs to **Group 3**.",
                        3: "Analysis suggests **Group 4** donor.",
                    }
                    if predicted_cluster in cluster_description:
                        st.write(cluster_description[predicted_cluster])
                    else:
                        st.write("No specific description available for this group yet.")

    # --- Footer Information ---
    st.markdown("---")
    st.info("This dashboard provides tools for blood donor data exploration and cluster analysis to understand donor segments and characteristics.")

else:
    st.error("Failed to load data. Please check the data path and ensure the Excel file is accessible.")