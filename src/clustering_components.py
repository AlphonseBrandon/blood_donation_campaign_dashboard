from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np , re
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.express as px
import random
import streamlit as st


blood_donation_data  = None  # Dataset to be loaded and processed
TARGET_COLUMN_NAME = "statut_d'éligibilité" # Column indicating donor eligibility
VALIDATED_COLUMNS = ['age', 'genre', 'profession', 'taux_d’hémoglobine', 'raison_indisponibilité_est_sous_anti-biothérapie_',
                     'raison_indisponibilité_date_de_dernier_don_<_3_mois_',
                     'raison_de_l’indisponibilité_de_la_femme_la_ddr_est_mauvais_si_<14_jour_avant_le_don',
                     'raison_de_non-eligibilité_totale_opéré', 'raison_de_non-eligibilité_totale_tatoué',
                     'raison_de_non-eligibilité_totale_scarifié', 'imc', 'fréquence_de_don', 'chronic_diseases',
                     'transmissible_diseases'] # Columns used for clustering and analysis
CHRONIC_DISEASES_COLUMNS = [ 'raison_de_non-eligibilité_totale_diabétique', 'raison_de_non-eligibilité_totale_hypertendus',
                            'raison_de_non-eligibilité_totale_asthmatiques', 'raison_de_non-eligibilité_totale_cardiaque',
                            'raison_de_non-eligibilité_totale_drepanocytaire'] # Columns related to chronic conditions
TRANSMISSIBLE_DISEASES_COLUMNS = ['raison_de_non-eligibilité_totale_porteurhiv,hbs,hcv',
                                  'raison_indisponibilité_ist_récente_exclu_vih,_hbs,_hcv'] # Columns related to transmissible conditions

COLUMN_RENAME_FUNCTIONS = [lambda x: x.lower(), lambda x: x.replace(" ", "_"), lambda x: x.replace("(", "").replace(")", ""),
                           lambda x: x.replace('__', '_').replace('[', '').replace(']', ''),
                           lambda x: x.replace('[', '').replace(']', '')] # Functions for cleaning column names


def categorize_profession(job_title):
    """Categorizes job titles into broader professional categories."""
    print ( '- ',  job_title , '\n') # Keeping for potential debugging
    if not job_title or job_title in ['pas precise', 'pas précisé', 'pas mentionné', 'pas precisé', 'non precise', 'non precisé', 'ras', 'r a s', 'sp', 's1p']:
        return "autre"

    if re.search(r'[eé]tudiant|[ée]l[eè]ve|[eé]tudiante|stagiaire|stagiaitaire', job_title):
        return "Étudiant"
    elif re.search(r'informaticien|d[eé]veloppeur|programmeur|analyste|data scientist|ingénieur logiciel|web developer|web designer|ui/ux designer|graphic designer|cyber security|it support|system administrator|network engineer|database administrator|software engineer|informatticien|informatien|infor\'aticien|ingenieur en informatique|réseaux et télécommunications|content manager', job_title):
        return "Technologies de l'information"
    elif re.search(r'ingénieur|architecte|technicien|mécanicien|électricien|ingénieur civil|ingénieur génie civil|technicien supérieur|electronicien|électronicien|agent technique|chaudron(?:ier|nier)|machiniste|tolier|tôlier|soudeur|maintenancier|électro(?:\s|-)?m[ée]cani(?:cien|que)|genie civil|constructeur|carreleur|géometre|ingenieur agronome|ingenieur en bateau|mecatronicien|maintenance industrielle|grutier|plantelier|rebobineur|cableur|operateur portique|électricité|trieur|vitri(?:er|é)|étanchéiste|ferrailleur|trefilleur|superviseur maintenance|collaborateur architecture|énergéticien|echaffaudeur', job_title):
        return "Ingénierie et Technique"
    elif re.search(r'médecin|infirmier|pharmacien|dentiste|vétérinaire|kinésithérapeute|psychologue|aide-soignant|sage-femme|biologiste|chercheur|medecin|infirmièr|personnel de sante|laborantin|ambulancier|delegue medical|chimiste|auxiliaire de pharmacie|agent d\'appui pharmicie|ide urgentiste|brancardier|veterinaire|public health expert|administrateur des hopitaux|aide chirugien', job_title):
        return "Santé et Médecine"
    elif re.search(r'enseignant|professeur|instituteur|éducateur|formateur|bibliothécaire|chercheur|maitresse|educateur des enfants|moniteur|pleg|philosophe', job_title):
        return "Professeur"
    elif re.search(r'commercial|vend(?:eur|euse)|marketing|gest(?:ionnaire|ion)|compt(?:able|abilité)|financ(?:ier|e)|banqu(?:ier|e)|assur(?:eur|ance)|agent commercial|représentant|conseiller financier|consultant|business analyst|sales manager|account manager|marketing manager|project manager|product manager|customer service|human resources|businessm[ae]n|commerçant|entrepreneur|trader|homme d\'affaire|caissière|conseiller client|chargé de clientèle|agent de banque|auditeur interne|agent marketiste|conseiller juridique|fiscaliste|business development|market-developper|acheteur|responsable transport|agent immobilier|conseille agropastoral|chargée de communication|agent rh|assistant rh|agent de recouvriment|agent des ressourses humaines|manager administratif|directeur|directrice|contoleur gestion|jeune cadre|courtier|receptioniste', job_title):
        return "Commerce et Gestion"
    elif re.search(r'artiste|musicien|acteur|écrivain|journaliste|photographe|designer|graphiste|styliste|danseur|chanteur|peintre|sculpteur|réalisateur|realisateur|infographe|beat maker|communicateur|decorateur|agent video|regisseur son et lumiere|serigraphe|sérigraph(?:e|ie)', job_title):
        return "Arts et Culture"
    elif re.search(r'artisan|coiff(?:eur|euse)|couturi(?:er|ère)|cuisinier|pâtissier|patissier|boulanger|menuisier|m[ae]con|plombier|électricien|mécanicien|chauffeur|conducteur|agriculteur|pêcheur|éleveur|tailleur|menusier|ménuisier|mnuisier|planteur|cultivateur|cultuvateur|forestier|pecheur|estheti(?:cien|que)|soudeur|bijoutier|imprimeur|ouvrier|manoeuvre|manœuvre|maitre pecheur|staffeur|tapissier|ebeniste|cordonnier|coifffeur|restaurateur|brasseur|docker|do[lk]ker|pousseur|débrouillard|debrouillard|homme a tout faire|hoteli(?:er|ère|ere)|hotelluere|gouvernant d\'hotel|maître de chien', job_title):
        return "Artisanat et Métiers Manuels"
    elif re.search(r'polic(?:ier|e)|militaire|pompier|agent de s[eé]curit[eé]|garde du corps|secouriste|douanier|gendarme|juge|avocat|huissier|vigil|controleur des douanes|security officer|juriste|agent hse|chef de sécurité|greffier|charger de la sécurité|securite', job_title):
        return "Sécurité et Justice"
    elif re.search(r'sans emploi|chômeur|chomeur|au foyer|retraité|étudiant|femme au foyer|homme au foyer|ménagère|menagere', job_title):
        return "Sans Emploi"
    elif re.search(r'administ(?:rateur|ration|ratif)|secretary|secretaire|secrétaire|clerical|office|assistant|assistante|archiviste|documentaliste|agent de liaison|transita(?:ire|ir)|déclarant|declarant|agent maritime|agent portuaire|agent communal|agent municipal|intendant|fonctionnaire|contractuel|cadre|logisticien', job_title):
        return "Administration et Services"
    elif re.search(r'transport(?:eur)?|taxi(?:man)?|moto(?:\s|-)?taxi(?:man)?|chauffeur|conducteur|motoman', job_title):
        return "Transport"
    elif re.search(r'pasteur|evangeliste|missionary|missionnaire', job_title):
        return "Religieux"
    elif re.search(r'sportifs|footballeur|coach', job_title):
        return "Sport"
    else:
        return 'autre'


def mine_cluster_information ( clustered_data ):
    """Analyzes donor eligibility distribution across clusters and visualizes it."""

    eligibility_status = clustered_data[TARGET_COLUMN_NAME].values
    cluster_labels = clustered_data['cluster'].values

    cluster_counts = pd.Series(cluster_labels).value_counts()
    donor_clusters = cluster_labels[eligibility_status == 1]
    donor_cluster_counts = pd.Series(donor_clusters).value_counts()

    donor_percentage = donor_cluster_counts * 100 / cluster_counts
    not_donor_percentage = 100 - donor_percentage
    cluster_percentage_in_dataset = (donor_cluster_counts / clustered_data.shape[0]) * 100


    fig, ax = plt.subplots(figsize=(10, 6))
    donor_color = 'skyblue'
    not_donor_color = 'salmon'
    sorted_indices = sorted(donor_percentage.index)
    x_pos = np.arange(len(sorted_indices))
    bar_width = 0.5


    for i, cluster_val in enumerate(sorted_indices):
        donor_value = donor_percentage.get(cluster_val, 0)
        not_donor_value = not_donor_percentage.get(cluster_val, 0)

        bar1 = ax.bar(x_pos[i], donor_value, bar_width, label='donor' if i == 0 else None, color=donor_color)
        bar2 = ax.bar(x_pos[i], not_donor_value, bar_width, bottom=donor_value, label='Not donor' if i == 0 else None, color=not_donor_color)

        ax.text(bar1[0].get_x() + bar1[0].get_width() / 2, donor_value / 2, f'{donor_value:.1f}%', ha='center', va='center', color='black', fontsize=10)
        ax.text(bar1[0].get_x() + bar1[0].get_width() / 2, 100.9, f'{cluster_percentage_in_dataset.get(cluster_val, 0):.1f}%', ha='center', va='bottom', color='black', fontsize=10)


    ax.set_xticks(x_pos)
    ax.set_xticklabels(sorted_indices)
    ax.legend(loc='lower center', ncol=2)
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Percentage of Donors")
    ax.set_title("Donor Eligibility Status Distribution Across Clusters")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    st.pyplot(fig)



def cluster_columns(data_with_disease_columns):
    """Groups chronic and transmissible disease columns into combined columns."""

    data_with_disease_columns['chronic_diseases'] = data_with_disease_columns[CHRONIC_DISEASES_COLUMNS].apply(lambda row: 'Oui' if row.str.contains('Oui').any() else 'Non', axis=1)
    data_with_disease_columns['transmissible_diseases'] = data_with_disease_columns[TRANSMISSIBLE_DISEASES_COLUMNS].apply(lambda row: 'Oui' if row.str.contains('Oui').any() else 'Non', axis=1)

    random_chronic_disease_column = random.choice(CHRONIC_DISEASES_COLUMNS)
    individual_disease_count = (data_with_disease_columns[random_chronic_disease_column] == 'Oui').sum()
    grouped_disease_count = (data_with_disease_columns['chronic_diseases'] == 'Oui').sum()

    assert individual_disease_count <= grouped_disease_count, f"Test failed for {random_chronic_disease_column}. Individual count exceeds grouped count."
    print(f"Test passed for {random_chronic_disease_column}. Individual count: {individual_disease_count}, Grouped count: {grouped_disease_count}")



def one_hot_encode_column(data_column, drop_first=True, use_sklearn=False):
    """One-hot encodes a single pandas Series or numpy array column."""
    if isinstance(data_column, np.ndarray):
        data_column = pd.Series(data_column)

    if not use_sklearn:
        one_hot_encoded_data = pd.get_dummies(data_column, drop_first=drop_first, dtype=int)
        return np.array(one_hot_encoded_data)
    else:
        encoder = OneHotEncoder(drop='first' if drop_first else None, sparse_output=False)
        one_hot_encoded_data = encoder.fit_transform(data_column.values.reshape(-1, 1))
        encoded_df = pd.DataFrame(one_hot_encoded_data, columns=encoder.get_feature_names_out([data_column.name]))
        return encoded_df



def perform_kmeans_clustering(data_for_clustering , show_plot=False ):
    """Performs K-means clustering on specified columns of the DataFrame."""

    clustering_columns = VALIDATED_COLUMNS

    selected_data = data_for_clustering[clustering_columns].copy()
    categorical_columns = selected_data.select_dtypes(include=['object']).columns
    numerical_data_for_kmeans = selected_data.copy()


    for col in categorical_columns:
        encoded_col_df = pd.DataFrame(one_hot_encode_column(data_for_clustering[col].values), index=numerical_data_for_kmeans.index)
        encoded_col_df.columns = [f'{col}_{val}' for val in encoded_col_df.columns]
        numerical_data_for_kmeans = pd.concat([numerical_data_for_kmeans.drop(col, axis=1), encoded_col_df], axis=1)


    kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
    data_for_clustering['cluster'] = kmeans_model.fit_predict(numerical_data_for_kmeans)


    if show_plot:
        pca_model = PCA(n_components=3)
        pca_components = pca_model.fit_transform(numerical_data_for_kmeans)

        pca_dataframe = pd.DataFrame(pca_components, columns=['pca_1', 'pca_2', 'pca_3'])
        pca_dataframe['cluster'] = data_for_clustering['cluster']

        for col in clustering_columns:
            pca_dataframe[col] = data_for_clustering[col]


        fig = px.scatter_3d(pca_dataframe, x='pca_1', y='pca_2', z='pca_3', color='cluster',
                            hover_data=[col for col in pca_dataframe.columns if col not in ['pca_1', 'pca_2', 'pca_3']],
                            title='Donor Clustering with PCA')

        cluster_centroids_pca = pca_model.transform(kmeans_model.cluster_centers_)
        fig.add_scatter3d(x=cluster_centroids_pca[:, 0], y=cluster_centroids_pca[:, 1], z=cluster_centroids_pca[:, 2],
                            mode='markers', marker=dict(size=10, color='black', symbol='x'), name='Centroids')
        st.plotly_chart(fig , use_container_width=True)



def get_cluster_subset(clustered_dataset, target_cluster_label):
    """Retrieves a subset of data for a specific cluster."""
    subset_data = clustered_dataset[clustered_dataset['cluster'] == target_cluster_label]
    return subset_data



def clustering_data_sanitisation ( input_dataframe  ):
    """Sanitizes data, performs clustering, and prepares the dataset."""
    global blood_donation_data
    if not isinstance(blood_donation_data, pd.DataFrame) :
        blood_donation_data = input_dataframe.copy()

        for function in COLUMN_RENAME_FUNCTIONS:
            blood_donation_data.columns = blood_donation_data.columns.map(function)

        cluster_columns(blood_donation_data)

        blood_donation_data['profession'] = blood_donation_data['profession'].apply(lambda x: x.lower().strip())
        blood_donation_data['profession'] = blood_donation_data['profession'].apply(categorize_profession)

        perform_kmeans_clustering( blood_donation_data,  show_plot=False )
    return blood_donation_data