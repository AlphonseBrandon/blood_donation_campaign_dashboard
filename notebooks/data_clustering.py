# -*- coding: utf-8 -*-
"""
Streamlit Dashboard for Blood Donor Data Analysis and Clustering.
Interactive dashboard for exploring blood donor data, performing K-means clustering,
and predicting cluster for new user inputs.
"""

import streamlit as st
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.stats import chi2_contingency
import io  # For displaying dataframe

# ----------------------------------------------------------------------
#                       DATA LOADING AND PREPROCESSING (Moved outside Streamlit app for initial setup)
# ----------------------------------------------------------------------

path = 'data\processed\processed.xlsx' # Adjust path if running locally, assuming 'processed.xlsx' is in the same directory

try:
    df = pd.read_excel(path)
    print("Data loaded successfully from:", path)
except FileNotFoundError:
    print(f"Error: {path} not found.")
    df = None
except Exception as e:
    print(f"An error occurred during data loading: {e}")
    df = None

if df is not None:
    #preprocessing functions
    # @title
    # FUNCTIONS FOR COLUMN PROCESSING TASK
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
            text = str(text).strip()  # Convert to string
            if text.upper() == 'NULL' or text =='nan' or text == '' or pd.isnull(text) :
                return replace
            return text
    def parse_date(date_str , format = '%Y-%m-%d'):
        """Parse date strings into datetime objects."""
        date_str = date_str.split (' ')[0]
        try:
            return pd.to_datetime(date_str, format= format, errors='raise')
        except ValueError:
            try:
                return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M', errors='raise')
            except ValueError:
                return pd.NaT
    def remove_special_charecters (value):
      #use re
      value = str(value)
      value = re.sub(r'[^a-zA-Z0-9\s+-]', '', value)
      return value

    def one_hot_encode_column(column, drop_first=True, use_sklearn=False):
        """
        One-hot encode a single column from a dataset.
        """
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
        """
        Calculate Cramér's V for two categorical variables.

        """

        x = np.array(x)
        y = np.array(y)

        # contingency table
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




    #####
    class Sheet:
        # Sheet class definition (as in the previous complete code, place it here)
        def __init__(self, name, new_column_names = None): # Reverted to original __init__
            self.name = name
            self.pre_processing_functions = [ ]
            self.sheet = pd.read_excel(path, sheet_name=name) # Reading excel inside init again
            self.old_column_names = self.sheet.columns.tolist()
            self.lang = 'fr'
            if new_column_names:
              self.rename_columns(new_column_names)

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

        def preprocess_columns(self, columns=None, excludes=None, process_function=lambda text: text):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            for column_name in columns:
                self.column_name = column_name
                if column_name not in excludes:
                    self.sheet[column_name] = self.sheet[column_name].apply(process_function)
            self.column_name = None

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
            print(f"nulls count : {self.count_nulls(column_name)}")
            print(f"Unique values in column '{column_name}':")
            print(value_counts)

        def display_fields(self):
            for column_name in self.sheet.columns:
                print(f'\n\n_______ {column_name.title()} ______\n')
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
                pass # Placeholder if translation is not implemented
            return self.get_columns()

        def get_group(self, column_name):
            return self.sheet[column_name].unique()

        def get_hot_encoded(self, column_name):
            return one_hot_encode_column(self.get_column(column_name))

        def plot_frequency(self, column_name):
            records = self.get_group(column_name)
            plt.bar(records, self.sheet[column_name].value_counts())
            plt.xticks(rotation=45, ha='right', fontsize=7)
            plt.xlabel(column_name)
            plt.ylabel('Frequency')
            plt.title(f'Frequency of {column_name}')
            plt.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
            st.pyplot(plt) # Show plot in Streamlit

        def get_correlation_matrix(self, columns=None, excludes=None):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            columns = [col for col in columns if col not in excludes]
            data = self.sheet[columns].copy()

            for col in columns:
                if data[col].dtype == 'object':
                    try:
                        data[col] = pd.to_numeric(data[col], errors='raise')
                    except:
                        pass

            corr_matrix = pd.DataFrame(np.nan, index=columns, columns=columns)

            for i, col1 in enumerate(columns):
                for j, col2 in enumerate(columns):
                    if i <= j:
                        col1_num = pd.api.types.is_numeric_dtype(data[col1])
                        col2_num = pd.api.types.is_numeric_dtype(data[col2])

                        if col1_num and col2_num:
                            corr = data[col1].corr(data[col2], method='pearson')
                        elif not col1_num and not col2_num:
                            corr = cramers_v(data[col1], data[col2])
                        else:
                            numeric_col = col1 if col1_num else col2
                            categorical_col = col2 if col1_num else col1
                            groups = data.groupby(categorical_col)[numeric_col].apply(list)

                            if len(groups) >= 2:
                                grand_mean = data[numeric_col].mean()
                                ss_between = sum([len(g) * (np.mean(g) - grand_mean)**2 for g in groups])
                                ss_total = sum((data[numeric_col] - grand_mean)**2)
                                eta = np.sqrt(ss_between / ss_total) if ss_total != 0 else 0

                                means = [np.mean(g) for g in groups]
                                direction = np.sign(means[1] - means[0]) if len(means) == 2 else 1
                                corr = eta * direction
                            else:
                                corr = np.nan

                        corr_matrix.loc[col1, col2] = corr
                        corr_matrix.loc[col2, col1] = corr

            return corr_matrix

        def plot_correlation_matrix(self, columns=None, excludes=None):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            for name in excludes:
                if name in columns:
                    columns.remove(name)
            correlation_matrix = self.get_correlation_matrix(columns)

            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
            plt.title('Correlation Matrix')
            st.pyplot(plt) # Show plot in Streamlit

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
                encoded_col_df = pd.DataFrame(self.get_hot_encoded(col), index=encoded_data.index)
                encoded_col_df.columns = [f'{col}_{val}' for val in encoded_col_df.columns]
                encoded_data = pd.concat([encoded_data.drop(col, axis=1), encoded_col_df], axis=1)

            sse_values = []
            for k in range(1, max_k + 1):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(encoded_data)
                sse_values.append(kmeans.inertia_)

            plt.figure(figsize=(10, 6))
            plt.plot(range(1, max_k + 1), sse_values, marker='o')
            plt.title('Elbow Method for Optimal K')
            plt.xlabel('Number of Clusters (K)')
            plt.ylabel('Sum of Squared Errors (SSE)')
            st.pyplot(plt) # Show plot in Streamlit


        def perform_kmeans_clustering(self, k, columns=None, excludes=None, show_plot=True):
            if excludes is None:
                excludes = []
            if not columns:
                columns = self.get_columns()
            columns = [col for col in columns if col not in excludes]

            data = self.sheet[columns].copy()

            string_cols = data.select_dtypes(include=['object']).columns
            encoded_data = data.copy()

            # Store encoders for prediction later
            self.encoders_kmeans = {}
            for col in string_cols:
                encoder = LabelEncoder() # Use LabelEncoder for prediction consistency
                encoded_data[col] = encoder.fit_transform(encoded_data[col].astype(str))
                self.encoders_kmeans[col] = encoder # Store the fitted encoder

            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            self.kmeans_model = kmeans.fit(encoded_data) # Store the fitted model
            self.sheet['cluster'] = self.kmeans_model.labels_ # Assign cluster labels to the sheet

            if show_plot:
                pca = PCA(n_components=3)
                pca_result = pca.fit_transform(encoded_data)

                pca_df = pd.DataFrame(pca_result, columns=['pca_1', 'pca_2', 'pca_3'])
                pca_df['cluster'] = self.sheet['cluster']

                for col in columns:
                    pca_df[col] = self.sheet[col].values # Ensure alignment

                fig = px.scatter_3d(
                    pca_df,
                    x='pca_1', y='pca_2', z='pca_3',
                    color='cluster',
                    hover_data=[col for col in pca_df.columns if col not in ['pca_1', 'pca_2', 'pca_3']],
                    title=f'K-Means Clusters (K={k}) with PCA Reduction'
                )

                centroids_pca = pca.transform(self.kmeans_model.cluster_centers_)
                fig.add_scatter3d(
                    x=centroids_pca[:, 0],
                    y=centroids_pca[:, 1],
                    z=centroids_pca[:, 2],
                    mode='markers',
                    marker=dict(size=10, color='black', symbol='x'),
                    name='Centroids'
                )
                st.plotly_chart(fig) # Show interactive plot in Streamlit

            return self.sheet

        def continuos_correlation(self, column1, column2):
            if column1 not in self.sheet.columns or column2 not in self.sheet.columns:
                raise ValueError(f"Columns missing: {column1} or column2")

            x = self.sheet[column1]
            y = self.sheet[column2]

            plt.figure(figsize=(10, 6))
            plt.scatter(x, y, alpha=0.7, label='Data Points')

            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), "r--", label=f"Trendline (y={z[0]:.2f}x+{z[1]:.2f})")

            plt.title(f"Scatterplot of {column1} vs {column2}")
            plt.xlabel(column1)
            plt.ylabel(column2)
            plt.legend()
            st.pyplot(plt) # Show plot in Streamlit

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

            fig = px.scatter(df_corr, x=column1, y=column2,
                             title=f"{column1} vs {column2} Correlation",
                             labels={column1: column1, column2: column2},
                             trendline="ols",
                             hover_data=df_corr.columns.tolist())

            corr = df_corr[[column1, column2]].corr().iloc[0, 1]
            fig.add_annotation(text=f"Pearson r: {corr:.2f}",
                               xref="paper", yref="paper",
                               x=0.05, y=0.95, showarrow=False)

            for col, encoder in encoders.items():
                fig.update_layout(**{
                    f'xaxis' if col == column1 else 'yaxis': {
                        'tickvals': list(range(len(encoder.classes_))),
                        'ticktext': encoder.classes_
                    }
                })
            st.plotly_chart(fig) # Show interactive plot in Streamlit

        def predict_cluster(self, user_data):
          """Predicts the cluster for new user data."""
          user_df = pd.DataFrame([user_data]) # Create DataFrame from user input

          # Encode categorical features consistently with training
          encoded_user_data = user_df.copy()
          string_cols_kmeans = self.encoders_kmeans.keys() # Get categorical columns used in clustering

          # Prepare a list to hold encoded feature values in the correct order
          encoded_features_list = []

          for field in relevant_fields: # Iterate through the *original* feature list order
              if field in string_cols_kmeans: # If this field was categorical and encoded
                  encoder = self.encoders_kmeans[field]
                  if field in user_df.columns: # Check if user provided this column
                      category = user_df[field].astype(str) # Ensure string type for encoding
                      encoded_value = encoder.transform(category) # Encode user input category
                      encoded_features_list.extend(encoded_value) # Extend list with encoded value (LabelEncoder returns scalar or 1D array)
                  else:
                      # Handle missing categorical input (optional: fill with a default encoded value if appropriate for your case)
                      # For now, let's assume missing categorical features are not allowed, or handled upstream
                      st.error(f"Error: Missing categorical feature '{field}' for prediction.")
                      return None # Or raise an exception

              elif field in user_df.columns: # If it's a numerical feature (and present in user input)
                  encoded_features_list.append(user_df[field].iloc[0]) # Append numerical value directly
              else:
                  # Handle missing numerical input (optional: fill with mean, median, or a default value if appropriate)
                  # For now, assume missing numerical features are not allowed
                  st.error(f"Error: Missing numerical feature '{field}' for prediction.")
                  return None # Or raise an exception

          # Convert the list of encoded features to a numpy array and reshape
          user_input_encoded = np.array(encoded_features_list).reshape(1, -1) # Reshape to (1, n_features)

          # Debugging prints - very helpful to understand what's going on
          print("Shape of user_input_encoded for prediction:", user_input_encoded.shape)
          print("Expected feature shape:", self.kmeans_model.n_features_in_) # Correct attribute name
          print("Features expected by KMeans:", self.kmeans_model.feature_names_in_ if hasattr(self.kmeans_model, 'feature_names_in_') else "Feature names not available in model")


          if user_input_encoded.shape[1] != self.kmeans_model.n_features_in_: # Correct attribute name
              st.error(f"Feature mismatch in prediction: Input has {user_input_encoded.shape[1]} features, but model expects {self.kmeans_model.n_features_in_}") # Correct attribute name
              return None # Or raise an exception

          predicted_cluster = self.kmeans_model.predict(user_input_encoded)[0] # Predict cluster
          return predicted_cluster


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
        #'has_he_already_given_the_blood?',
        #'_gift_frequency'
    ]

    sVoluntaire = Sheet('Volontaire') # Using original Sheet instantiation
    funcs = [
        lambda sheet: sheet.preprocess_column('Taux_d’hémoglobine', lambda value: value / 10 if isinstance(value, (int, float)) and value > 100 else value),
        lambda sheet: sheet.preprocess_columns(process_function = lambda value : replace_nulity(value , sheet.get_most_frequent(sheet.column_name)) ,columns = ['Groupe_d\'âge']),
    ]
    sVoluntaire.add_pre_processing_function(funcs)
    sVoluntaire.apply_pre_processing_functions()


    # ----------------------------------------------------------------------
    #                       STREAMLIT APP
    # ----------------------------------------------------------------------

    st.title("Blood Donor Data Dashboard")
    st.sidebar.header("User Inputs")

    # Interactive K value selection
    k_value = st.sidebar.slider("Number of Clusters (K)", min_value=2, max_value=10, value=4)

    # Button to trigger clustering
    if st.sidebar.button("Re-run Clustering"):
        with st.spinner(f'Running K-Means Clustering with K={k_value}...'):
            clustered_sheet = sVoluntaire.perform_kmeans_clustering(k_value, columns=relevant_fields, excludes=excludes, show_plot=True)
            st.success(f'K-Means Clustering with K={k_value} completed!')
    else: # Run clustering with default K=4 on initial load
        with st.spinner(f'Running initial K-Means Clustering with K=4...'):
             clustered_sheet = sVoluntaire.perform_kmeans_clustering(4, columns=relevant_fields, excludes=excludes, show_plot=True)
             st.success(f'Initial K-Means Clustering with K=4 completed!')


    st.header("Explore Data")

    # Tabbed interface for different analyses
    analysis_tab = st.radio("Choose Analysis:", ["Cluster Visualization", "Correlation Matrix", "Column Correlation Plot", "Column Frequencies", "Predict My Cluster"]) # Added "Column Correlation Plot"

    if analysis_tab == "Cluster Visualization":
        st.subheader("K-Means Cluster Visualization")
        st.write("Interactive 3D visualization of clusters after PCA reduction.")
        # (Visualization is already shown after clustering, no extra code needed here unless you want to re-display it)

    elif analysis_tab == "Correlation Matrix":
        st.subheader("Correlation Matrix Heatmap")
        st.write("Heatmap showing the correlation between relevant features.")
        sVoluntaire.plot_correlation_matrix(relevant_fields, excludes=excludes)

        # Display Correlation Matrix as DataFrame
        st.subheader("Correlation Matrix Table")
        corr_matrix_df = sVoluntaire.get_correlation_matrix(columns=relevant_fields, excludes=excludes)
        st.dataframe(corr_matrix_df) # Display DataFrame in Streamlit

    elif analysis_tab == "Column Frequencies":
        st.subheader("Column Value Frequencies")
        selected_column_freq = st.selectbox("Select Column to View Frequency:", relevant_fields)
        sVoluntaire.plot_frequency(selected_column_freq)

    elif analysis_tab == "Column Correlation Plot": # New section for Column Correlation Plot
        st.subheader("Column Correlation Plot")
        st.write("Scatter plot showing the correlation between two selected columns.")
        col1 = st.selectbox("Select First Column for Correlation:", relevant_fields, key="col1_corr") # Added key to prevent interference
        col2 = st.selectbox("Select Second Column for Correlation:", relevant_fields, key="col2_corr") # Added key

        if col1 and col2 and col1 != col2: # Ensure two different columns are selected
            if pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col1]) and pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col2]):
                sVoluntaire.continuos_correlation(col1, col2)
            elif (pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col1]) and sVoluntaire.sheet[col2].dtype == 'object') or \
                 (sVoluntaire.sheet[col1].dtype == 'object' and pd.api.types.is_numeric_dtype(sVoluntaire.sheet[col2])):
                sVoluntaire.binary_continous_correlation(col1, col2)
            else:
                st.warning("Scatter plot is best suited for numeric-numeric or numeric-categorical column combinations.")
        elif col1 == col2:
            st.warning("Please select two different columns for correlation plot.")
        else:
            st.info("Select two columns to visualize their correlation.")


    elif analysis_tab == "Predict My Cluster":
        st.subheader("Predict Your Cluster")
        st.write("Enter your details to predict which cluster you might belong to.")

        user_input_data = {}
        for field in relevant_fields:
            if sVoluntaire.sheet[field].dtype == 'object': # Assuming object type means categorical
                unique_vals = [''] + list(sVoluntaire.get_group(field)) # Add empty string for default/optional input
                user_input_data[field] = st.selectbox(f"Your {field.replace('_', ' ').title()}:", unique_vals)
            elif sVoluntaire.sheet[field].dtype in ['int64', 'float64']: # Numerical input
                min_val = float(sVoluntaire.sheet[field].min())
                max_val = float(sVoluntaire.sheet[field].max())
                user_input_data[field] = st.number_input(f"Your {field.replace('_', ' ').title()}:", min_value=min_val, max_value=max_val, value=(min_val + max_val)/2.0) # Default to midpoint
            else: # Text input as fallback
                user_input_data[field] = st.text_input(f"Your {field.replace('_', ' ').title()}:", "")

        if st.button("Predict Cluster"):
            with st.spinner('Predicting your cluster...'):
                predicted_cluster = sVoluntaire.predict_cluster(user_input_data)
                st.write(f"Predicted Cluster: **Cluster {predicted_cluster}**")

                # (Optional) Provide some insights about the predicted cluster
                st.subheader("Cluster Insights")
                cluster_description = {
                    0: "Cluster 0 Description: ... still to add",
                    1: "Cluster 1 Description: ... still to add",
                    2: "Cluster 2 Description: ... still to add",
                    3: "Cluster 3 Description: ... still to add",
                    # ... add descriptions for other clusters if K > 4
                }
                if predicted_cluster in cluster_description:
                    st.write(cluster_description[predicted_cluster])
                else:
                    st.write("No specific description available for this cluster yet.")

    st.sidebar.markdown("---")
    st.sidebar.info("This dashboard allows you to explore blood donor data, perform interactive K-means clustering, and predict your potential donor cluster.")

else:
    st.error("Failed to load data. Please check the data path and ensure the Excel file is accessible.")