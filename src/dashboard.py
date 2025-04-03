import streamlit as st
import pandas as pd
import plotly.express as px
<<<<<<< HEAD
=======

>>>>>>> 09a482a7acb3b51079d9c2808cfac672e9bb3a45
import plotly.graph_objects as go
from pathlib import Path
import requests
import json
from fuzzywuzzy import fuzz, process
import time
from geopy.geocoders import Nominatim
import unidecode
from clustering_components import (
    perform_kmeans_clustering,
    mine_cluster_information,
    clustering_data_sanitisation,
)
import geopandas as gpd
from geopy.geocoders import Nominatim 
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Tuple


# Configuration
DATA_PATH = Path("data/processed/processed.xlsx")
STREAMLIT_CONFIG = {
    "page_title": "Blood Donation Dashboard",
    "page_icon": "🩸",
    "layout": "wide"
}   

@st.cache_data
def load_data():
    """Load and cache processed data"""
    df = pd.read_excel(DATA_PATH, sheet_name="Volontaire")
    print(df.head())  # Verify data loading
    return df

def get_default_coordinates() -> Dict[str, Tuple[float, float]]:
    """Cached dictionary of known locations and their coordinates"""
    return {
        "YAOUNDE": (3.848, 11.5021),
        "DOUALA": (4.0511, 9.7679),
        "R A S": (3.848, 11.5021),  # Default to Yaounde if unknown
        # Add more known locations as needed
    }

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def geocode_with_retry(location: str, geolocator) -> Tuple[float, float]:
    """Geocode location with retry mechanism"""
    try:
        loc = geolocator.geocode(f"{location}, Cameroon", timeout=5)
        if loc:
            return (loc.latitude, loc.longitude)
    except Exception as e:
        st.warning(f"Retrying geocoding for {location}...")
        raise e
    return None

def get_coordinates(filtered_df):
    """Get or generate coordinates for locations with improved error handling"""
    if 'Latitude' not in filtered_df.columns or 'Longitude' not in filtered_df.columns:
        # Get default coordinates
        default_coords = get_default_coordinates()
        
        # Initialize Nominatim geocoder
        geolocator = Nominatim(
            user_agent="blood_donation_dashboard",
            timeout=5
        )
        
        # Get unique arrondissements
        unique_locations = filtered_df['Arrondissement_de_résidence'].unique()
        failed_locations = []
        
        # Create coordinates dictionary
        coordinates = {}
        
        with st.spinner('Generating coordinates for locations...'):
            progress_bar = st.progress(0)
            total_locations = len(unique_locations)
            
            for i, location in enumerate(unique_locations):
                # Update progress silently
                progress = (i + 1) / total_locations
                progress_bar.progress(progress)
                
                try:
                    # Check default coordinates first
                    if location.upper() in default_coords:
                        coordinates[location] = default_coords[location.upper()]
                        continue
                    
                    # Try geocoding with retry
                    result = geocode_with_retry(location, geolocator)
                    if result:
                        coordinates[location] = result
                    else:
                        failed_locations.append(location)
                        coordinates[location] = default_coords["YAOUNDE"]
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception:
                    failed_locations.append(location)
                    coordinates[location] = default_coords["YAOUNDE"]
            
            progress_bar.empty()
            
            # Show summary of failures at the end
            if failed_locations:
                st.info(f"Used default coordinates for {len(failed_locations)} locations")
        
        # Add coordinates to DataFrame
        filtered_df['Latitude'] = filtered_df['Arrondissement_de_résidence'].map(
            lambda x: coordinates.get(x, default_coords["YAOUNDE"])[0]
        )
        filtered_df['Longitude'] = filtered_df['Arrondissement_de_résidence'].map(
            lambda x: coordinates.get(x, default_coords["YAOUNDE"])[1]
        )
    
    return filtered_df

@st.cache_data
def get_cached_coordinates():
    """Cache coordinates for known locations"""
    return {
        "YAOUNDE": (3.848, 11.5021),
        "DOUALA": (4.0511, 9.7679),
        "R A S": (3.848, 11.5021),
        "DOUALA 1": (4.0511, 9.7679),
        "DOUALA 2": (4.0461, 9.7085),
        "DOUALA 3": (4.0531, 9.7701),
        "DOUALA 4": (4.0492, 9.7654),
        "DOUALA 5": (4.0972, 9.7424),
        "DOUALA 6": (4.0517, 9.7679),
        # Add more known coordinates
    }

@st.cache_data
def generate_location_coordinates(_df):
    """Generate and cache coordinates for all locations"""
    if 'Latitude' in _df.columns and 'Longitude' in _df.columns:
        return _df
    
    default_coords = get_cached_coordinates()
    coordinates = {}
    
    # Initialize Nominatim geocoder
    geolocator = Nominatim(
        user_agent="blood_donation_dashboard",
        timeout=5
    )
    
    # Get unique locations
    unique_locations = _df['Arrondissement_de_résidence'].unique()
    
    for location in unique_locations:
        try:
            # Check cached coordinates first
            if location.upper() in default_coords:
                coordinates[location] = default_coords[location.upper()]
                continue
            
            # Try geocoding
            loc = geolocator.geocode(f"{location}, Cameroon")
            if loc:
                coordinates[location] = (loc.latitude, loc.longitude)
            else:
                coordinates[location] = default_coords["YAOUNDE"]
            time.sleep(1)
        except Exception:
            coordinates[location] = default_coords["YAOUNDE"]
    
    # Add coordinates to DataFrame copy
    df_with_coords = _df.copy()
    df_with_coords['Latitude'] = df_with_coords['Arrondissement_de_résidence'].map(
        lambda x: coordinates.get(x, default_coords["YAOUNDE"])[0]
    )
    df_with_coords['Longitude'] = df_with_coords['Arrondissement_de_résidence'].map(
        lambda x: coordinates.get(x, default_coords["YAOUNDE"])[1]
    )
    
    return df_with_coords
    
def create_geographic_analysis(filtered_df):
    """Create geographic distribution visualizations"""
    st.header("Geographic Distribution")
    
    # Get cached coordinates
    df_with_coords = generate_location_coordinates(filtered_df)
    
    tab1, tab2, tab3 = st.tabs(["Interactive Map", "Arrondissements", "Quartier Analysis"])
    
    with tab1:
        try:
            # Create Folium map using cached coordinates
            m = folium.Map(location=[3.848, 11.5021], zoom_start=6)
            marker_cluster = folium.plugins.MarkerCluster().add_to(m)
            
            for idx, row in df_with_coords.iterrows():
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                    folium.CircleMarker(
                        location=(row['Latitude'], row['Longitude']),
                        radius=5,
                        color='blue',
                        fill=True,
                        fill_color='blue',
                        fill_opacity=0.6,
                        popup=f"""
                        <b>Arrondissement:</b> {row['Arrondissement_de_résidence']}<br>
                        <b>Quartier:</b> {row['Quartier_de_Résidence']}<br>
                        <b>Status:</b> {'Eligible' if row["Statut_d'éligibilité"] == 1 else 'Not Eligible'}
                        """
                    ).add_to(marker_cluster)
            
            folium.LayerControl().add_to(m)
            st_folium(m, width=None, height=500)
            
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
            st.info("Please ensure geographic data is available in the dataset")

    with tab2:
        st.subheader("Arrondissement Distribution")
        
        # Analyze arrondissement distribution
        arrond_counts = filtered_df['Arrondissement_de_résidence'].value_counts()
        
        # Create visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 arrondissements bar chart
            fig = px.bar(
                x=arrond_counts.head(10).index,
                y=arrond_counts.head(10).values,
                title="Top 10 Arrondissements by Donor Count",
                labels={"x": "Arrondissement", "y": "Number of Donors"},
                color=arrond_counts.head(10).values,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Display metrics
            total_arronds = len(arrond_counts)
            total_donors = len(filtered_df)
            avg_donors = total_donors / total_arronds if total_arronds > 0 else 0
            
            st.metric(
                "Total Arrondissements",
                f"{total_arronds:,}",
                f"Avg {avg_donors:.1f} donors per area"
            )
            
            st.metric(
                "Most Active Area",
                arrond_counts.index[0],
                f"{arrond_counts.iloc[0]:,} donors"
            )
            
            st.metric(
                "Coverage Rate",
                f"{(total_arronds/len(filtered_df.Arrondissement_de_résidence.unique())*100):.1f}%",
                "of total areas"
            )

    with tab3:
        st.subheader("Quartier Analysis")
        
        # Allow user to select arrondissement
        selected_arrond = st.selectbox(
            "Select Arrondissement",
            options=sorted(filtered_df['Arrondissement_de_résidence'].unique())
        )
        
        # Filter for selected arrondissement
        arrond_df = filtered_df[filtered_df['Arrondissement_de_résidence'] == selected_arrond]
        
        # Analyze quartiers
        quartier_counts = arrond_df['Quartier_de_Résidence'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quartier distribution visualization
            fig = px.bar(
                x=quartier_counts.head(10).index,
                y=quartier_counts.head(10).values,
                title=f"Top 10 Quartiers in {selected_arrond}",
                labels={"x": "Quartier", "y": "Number of Donors"},
                color=quartier_counts.head(10).values,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Quartier metrics
            st.metric(
                "Total Quartiers",
                len(quartier_counts),
                f"{len(arrond_df)} total donors"
            )
            
            st.metric(
                "Most Active Quartier",
                quartier_counts.index[0],
                f"{quartier_counts.iloc[0]} donors"
            )
            
            # Detailed quartier table
            st.dataframe(
                pd.DataFrame({
                    "Quartier": quartier_counts.index,
                    "Donors": quartier_counts.values,
                    "Percentage": (quartier_counts.values / len(arrond_df) * 100).round(1)
                }).head(10),
                column_config={
                    "Quartier": "Quartier Name",
                    "Donors": st.column_config.NumberColumn(
                        "Number of Donors",
                        help="Total donors from this quartier"
                    ),
                    "Percentage": st.column_config.NumberColumn(
                        "% of Arrondissement",
                        help="Percentage of donors in the arrondissement",
                        format="%.1f%%"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
def create_health_conditions_analysis(filtered_df):
    """Analyze and visualize the impact of health conditions on eligibility"""
    st.header("Health Conditions Impact")

    # Define health condition columns based on documentation
    health_conditions = {
        "Infectious Diseases": [
            col for col in filtered_df.columns
            if any(term in col.lower() for term in ["hiv", "hepatitis", "infection"])
        ],
        "Cardiovascular": [
            col for col in filtered_df.columns
            if any(term in col.lower() for term in ["hypertension", "cardiaque", "cardiovascular"])
        ],
        "Chronic Conditions": [
            col for col in filtered_df.columns
            if any(term in col.lower() for term in ["diabétique", "asthmatiques", "drepanocytaire"])
        ]
    }

    # Combine all health conditions
    all_conditions = [cond for conds in health_conditions.values() for cond in conds]
    total_deferrals = filtered_df[all_conditions].apply(
        lambda x: x.value_counts().get("Oui", 0)
    ).sort_values(ascending=True)

    # Calculate metrics
    total_deferral_rate = (
        filtered_df[all_conditions].eq("Oui").any(axis=1).mean() * 100
    ).round(1)
    health_eligible = len(filtered_df) - filtered_df[all_conditions].eq("Oui").any(axis=1).sum()

    # Create summary DataFrame
    summary_df = pd.DataFrame({
        "Condition": total_deferrals.index,
        "Deferrals": total_deferrals.values,
        "Percentage": (total_deferrals.values / len(filtered_df) * 100).round(1)
    })

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Impact Visualization", "Detailed Summary"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Bar chart of deferrals
            fig = px.bar(
                total_deferrals,
                orientation="h",
                title="Health Conditions Impact on Eligibility",
                labels={"value": "Number of Deferrals", "index": "Condition"},
                color=total_deferrals.values,
                color_continuous_scale="Reds"
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Display metrics
            st.metric(
                "Health-Related Deferral Rate",
                f"{total_deferral_rate}%",
                f"of {len(filtered_df):,} donors"
            )

            # Pie chart of eligibility
            fig = px.pie(
                values=[health_eligible, len(filtered_df) - health_eligible],
                names=["Eligible", "Deferred"],
                title="Health-Based Eligibility Distribution",
                color_discrete_sequence=["green", "red"]
            )
            fig.update_layout(
                showlegend=True,
                height=300,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Detailed Health Conditions Summary")
        st.dataframe(
            summary_df,
            column_config={
                "Condition": "Health Condition",
                "Deferrals": st.column_config.NumberColumn(
                    "Number of Deferrals",
                    help="Total number of donors deferred due to this condition",
                    format="%d"
                ),
                "Percentage": st.column_config.NumberColumn(
                    "% of Total Donors",
                    help="Percentage of total donors affected by this condition",
                    format="%.1f%%"
                )
            },
            hide_index=True,
            use_container_width=True
        )
def create_donor_retention_analysis(filtered_df):
    """Analyze donor retention and factors affecting repeat donations"""
    st.header("Donor Retention")

    # Calculate donor retention metrics
    donation_history = filtered_df["A-t-il_(elle)_déjà_donné_le_sang"].value_counts()
    repeat_donors = donation_history.get("Oui", 0)
    first_time_donors = donation_history.get("Non", 0)
    retention_rate = (repeat_donors / len(filtered_df) * 100).round(1)

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Repeat Donors",
            f"{repeat_donors:,}",
            f"{retention_rate}% of total donors"
        )
    with col2:
        st.metric(
            "First-Time Donors",
            f"{first_time_donors:,}",
            f"{100-retention_rate}% of total donors"
        )
    with col3:
        st.metric(
            "Retention Rate",
            f"{retention_rate}%",
            "Overall donor retention"
        )

    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["Demographic Factors", "Geographic Distribution"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Age group analysis
            age_retention = (
                filtered_df.groupby("Groupe_d'âge")["A-t-il_(elle)_déjà_donné_le_sang"]
                .apply(lambda x: (x == "Oui").mean() * 100)
                .round(1)
            )

            fig = px.bar(
                x=age_retention.index,
                y=age_retention.values,
                title="Donor Retention by Age Group",
                labels={"x": "Age Group", "y": "Retention Rate (%)"},
                color=age_retention.values,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Professional category analysis
            prof_retention = (
                filtered_df.groupby("Profession")["A-t-il_(elle)_déjà_donné_le_sang"]
                .apply(lambda x: (x == "Oui").mean() * 100)
                .round(1)
                .sort_values(ascending=True)
            )

            fig = px.bar(
                y=prof_retention.index,
                x=prof_retention.values,
                title="Donor Retention by Profession",
                labels={"y": "Profession", "x": "Retention Rate (%)"},
                orientation="h",
                color=prof_retention.values,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Geographic retention analysis
        geo_retention = (
            filtered_df.groupby("Arrondissement_de_résidence")["A-t-il_(elle)_déjà_donné_le_sang"]
            .apply(lambda x: (x == "Oui").mean() * 100)
            .round(1)
            .sort_values(ascending=True)
        )

        fig = px.bar(
            y=geo_retention.index,
            x=geo_retention.values,
            title="Donor Retention by Arrondissement",
            labels={"y": "Arrondissement", "x": "Retention Rate (%)"},
            orientation="h",
            color=geo_retention.values,
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Create summary table
        retention_summary = pd.DataFrame({
            "Arrondissement": geo_retention.index,
            "Retention_Rate": geo_retention.values,
            "Total_Donors": filtered_df.groupby("Arrondissement_de_résidence").size()
        }).sort_values("Retention_Rate", ascending=False)

        st.dataframe(
            retention_summary,
            column_config={
                "Arrondissement": "Arrondissement",
                "Retention_Rate": st.column_config.NumberColumn(
                    "Retention Rate",
                    help="Percentage of donors who have donated before",
                    format="%.1f%%"
                ),
                "Total_Donors": st.column_config.NumberColumn(
                    "Total Donors",
                    help="Total number of donors from this arrondissement",
                    format="%d"
                )
            },
            hide_index=True,
            use_container_width=True
        )

def create_campaign_effectiveness_analysis(filtered_df):
    """Analyze campaign effectiveness with focus on demographic contributions"""
    st.header("Campaign Effectiveness")

    # Create tabs for different demographic analyses
    tab1, tab2, tab3 = st.tabs(["Age & Gender Impact", "Professional Impact", "Geographic Impact"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Age group contribution analysis
            age_contributions = pd.DataFrame({
                "Total_Donors": filtered_df.groupby("Groupe_d'âge").size(),
                "Eligible_Donors": filtered_df[filtered_df["Statut_d'éligibilité"] == 1].groupby("Groupe_d'âge").size()
            }).reset_index()  # Reset index to make age groups a column

            age_contributions["Success_Rate"] = (
                age_contributions["Eligible_Donors"] / age_contributions["Total_Donors"] * 100
            ).round(1)

            fig = px.bar(
                data_frame=age_contributions,
                x="Total_Donors",
                y="Groupe_d'âge",
                color="Success_Rate",
                title="Contribution by Age Group",
                labels={
                    "Total_Donors": "Number of Donors",
                    "Groupe_d'âge": "Age Group",
                    "Success_Rate": "Success Rate (%)"
                },
                orientation="h",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gender distribution analysis
            gender_metrics = pd.DataFrame({
                "Total_Donors": filtered_df.groupby("Genre").size(),
                "Eligible_Donors": filtered_df[filtered_df["Statut_d'éligibilité"] == 1].groupby("Genre").size()
            })
            gender_metrics["Success_Rate"] = (gender_metrics["Eligible_Donors"] / gender_metrics["Total_Donors"] * 100).round(1)

            fig = px.pie(
                values=gender_metrics["Total_Donors"],
                names=gender_metrics.index,
                title="Gender Distribution in Campaigns",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Professional sector effectiveness
        prof_metrics = pd.DataFrame({
            "Total_Donors": filtered_df.groupby("Profession").size(),
            "Eligible_Donors": filtered_df[filtered_df["Statut_d'éligibilité"] == 1].groupby("Profession").size()
        }).sort_values("Total_Donors", ascending=True)

        prof_metrics["Success_Rate"] = (prof_metrics["Eligible_Donors"] / prof_metrics["Total_Donors"] * 100).round(1)

        fig = px.bar(
            prof_metrics,
            y=prof_metrics.index,
            x="Total_Donors",
            color="Success_Rate",
            title="Campaign Effectiveness by Profession",
            labels={
                "Total_Donors": "Number of Donors",
                "y": "Profession",
                "Success_Rate": "Success Rate (%)"
            },
            orientation="h",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Display detailed metrics
        st.dataframe(
            prof_metrics,
            column_config={
                "Total_Donors": st.column_config.NumberColumn(
                    "Total Donors",
                    help="Total number of donors from this profession",
                    format="%d"
                ),
                "Eligible_Donors": st.column_config.NumberColumn(
                    "Eligible Donors",
                    help="Number of eligible donors",
                    format="%d"
                ),
                "Success_Rate": st.column_config.NumberColumn(
                    "Success Rate",
                    help="Percentage of eligible donors",
                    format="%.1f%%"
                )
            },
            hide_index=False,
            use_container_width=True
        )

    with tab3:
        # Geographic contribution analysis
        geo_metrics = pd.DataFrame({
            "Total_Donors": filtered_df.groupby("Arrondissement_de_résidence").size(),
            "Eligible_Donors": filtered_df[filtered_df["Statut_d'éligibilité"] == 1]
            .groupby("Arrondissement_de_résidence").size()
        }).sort_values("Total_Donors", ascending=False)

        geo_metrics["Success_Rate"] = (geo_metrics["Eligible_Donors"] / geo_metrics["Total_Donors"] * 100).round(1)

        # Show top 10 contributing areas
        top_10_geo = geo_metrics.head(10)

        fig = px.bar(
            top_10_geo,
            y=top_10_geo.index,
            x="Total_Donors",
            color="Success_Rate",
            title="Top 10 Contributing Areas",
            labels={
                "Total_Donors": "Number of Donors",
                "y": "Arrondissement",
                "Success_Rate": "Success Rate (%)"
            },
            orientation="h",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            top_prof = prof_metrics["Total_Donors"].idxmax()
            st.metric(
                "Most Contributing Profession",
                top_prof,
                f"{prof_metrics.loc[top_prof, 'Success_Rate']}% success rate"
            )
        with col2:
            top_age = age_contributions["Total_Donors"].idxmax()
            st.metric(
                "Most Active Age Group",
                top_age,
                f"{age_contributions.loc[top_age, 'Success_Rate']}% success rate"
            )
        with col3:
            top_area = geo_metrics["Total_Donors"].idxmax()
            st.metric(
                "Most Contributing Area",
                top_area,
                f"{geo_metrics.loc[top_area, 'Success_Rate']}% success rate"
            )

def create_donor_mapping(challenge_df, cameroon_map, map_geo):
    """Create a mapping section for donor locations."""
    st.header("Donor Mapping")

    # Static Map
    plot_static_map(cameroon_map, map_geo)  # Call the static map function

    # Interactive Map
    interactive_map = plot_interactive_map(challenge_df)  # Call the interactive map function
    st_folium(interactive_map, width=700)  # Display the Folium map
def create_donor_profiling_analysis(filtered_df, challenge_df, cameroon_map):
    """Analyze and profile ideal donors based on demographic and health features"""
    st.header("Donor Profiling")

    if filtered_df.empty:
        st.warning("No data available for profiling.")
        return

    # Create map_geo GeoDataFrame from challenge_df for mapping operations
    map_geo = gpd.GeoDataFrame(
        challenge_df, 
        geometry=gpd.points_from_xy(challenge_df['Longitude'], challenge_df['Latitude']),
        crs="EPSG:4326"
    )

    # Create tabs for the sub-sections
    tab1, tab2, tab3, tab4 = st.tabs(["Ideal Donor Profile", "Clustering Insights", "Demographic Success Patterns", "Donor Mapping"])

    with tab1:
        # Ensure flags exist in the dataframe
        if 'is_eligible' not in filtered_df.columns:
            filtered_df['is_eligible'] = filtered_df["Statut_d'éligibilité"] == 1
        if 'is_repeat_donor' not in filtered_df.columns:
            filtered_df['is_repeat_donor'] = filtered_df["A-t-il_(elle)_déjà_donné_le_sang"] == "Oui"
            
        # Ideal Donor Profile logic...
        ideal_donors = filtered_df[
            (filtered_df['is_eligible']) &
            (filtered_df['is_repeat_donor'])
        ]

        if len(ideal_donors) == 0:
            st.warning("No ideal donors found with current filters")
            return

        try:
            profile_metrics = {
                "Age_Range": ideal_donors["Groupe_d'âge"].mode()[0],
                "Gender": ideal_donors["Genre"].mode()[0],
                "BMI_Category": ideal_donors["Catégorie_d'IMC"].mode()[0],
                "Profession": ideal_donors["Profession"].mode()[0],
                "Location": ideal_donors["Arrondissement_de_résidence"].mode()[0],
                "Success_Rate": float(len(ideal_donors)) / len(filtered_df) * 100
            }

            # Display ideal donor profile metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Most Common Age Group", profile_metrics["Age_Range"])
                st.metric("Predominant Gender", profile_metrics["Gender"])
            with col2:
                st.metric("Common Profession", profile_metrics["Profession"])
                st.metric("Success Rate", f"{profile_metrics['Success_Rate']:.1f}%")

        except Exception as e:
            st.error(f"Error calculating profile metrics: {str(e)}")
            return

    with tab2:
        # Clustering Insights logic...
        try:
            sheet = clustering_data_sanitisation(filtered_df)
            perform_kmeans_clustering(sheet, show_plot=True)
            st.info("The value above each cluster bar represents the percentage of the dataset held by that cluster.")
            mine_cluster_information(sheet)
        except Exception as e:
            st.error(f"Error in clustering analysis: {str(e)}")

    with tab3:
        # Demographic Success Patterns logic...
        try:
            demo_success = filtered_df.groupby(["Groupe_d'âge", "Genre", "Catégorie_d'IMC"])["is_eligible"].agg(["count", "mean"]).reset_index()
            demo_success["success_rate"] = demo_success["mean"] * 100

            fig = px.scatter(
                demo_success,
                x="Groupe_d'âge",
                y="success_rate",
                size="count",
                color="Genre",
                facet_col="Catégorie_d'IMC",
                title="Success Patterns by Age, Gender, and BMI",
                labels={"success_rate": "Success Rate (%)", "Groupe_d'âge": "Age Group"}
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error in demographic success patterns: {str(e)}")

    with tab4:
        # Donor Mapping
        try:
            # Static Map
            st.subheader("Static Map")
            fig, ax = plt.subplots(figsize=(12, 10))
            cameroon_map.plot(ax=ax, color='lightgrey', edgecolor='black')
            map_geo.plot(ax=ax, marker='o', color='red', markersize=5, label='Donors')
            plt.title('Geographical Distribution of Blood Donors in Cameroon')
            plt.legend()
            st.pyplot(fig)

            # Interactive Map
            st.subheader("Interactive Map")
            m = folium.Map(location=[3.848, 11.5021], zoom_start=6)
            for idx, row in challenge_df.iterrows():
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                    folium.CircleMarker(
                        location=(row['Latitude'], row['Longitude']),
                        radius=5,
                        color='blue',
                        fill=True,
                        fill_color='blue',
                        fill_opacity=0.6,
                        popup=f"Arrondissement: {row['Arrondissement_Matched']}<br>Quartier: {row.get('Quartier_de_Résidence', 'Not Available')}"
                    ).add_to(m)
            st_folium(m, width=700)
        except Exception as e:
            st.error(f"Error creating maps: {str(e)}")

    # Create success metrics for profiling
    filtered_df['is_eligible'] = filtered_df["Statut_d'éligibilité"] == 1
    filtered_df['is_repeat_donor'] = filtered_df["A-t-il_(elle)_déjà_donné_le_sang"] == "Oui"


def create_demographic_distribution(filtered_df):
    """Create demographic distribution analysis"""
    st.header("Demographic Distribution")

    tab1, tab2 = st.tabs(["Age & Gender", "Professional & Educational"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Age distribution
            age_dist = filtered_df["Groupe_d'âge"].value_counts().sort_index()

            fig = px.bar(
                x=age_dist.index,
                y=age_dist.values,
                title="Age Distribution of Donors",
                labels={"x": "Age Group", "y": "Number of Donors"},
                color=age_dist.values,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gender distribution
            gender_dist = filtered_df["Genre"].value_counts()

            fig = px.pie(
                values=gender_dist.values,
                names=gender_dist.index,
                title="Gender Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            # Professional distribution
            prof_dist = filtered_df["Profession"].value_counts().head(10)

            fig = px.bar(
                y=prof_dist.index,
                x=prof_dist.values,
                title="Top 10 Professions",
                labels={"y": "Profession", "x": "Number of Donors"},
                orientation="h",
                color=prof_dist.values,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # BMI distribution
            bmi_dist = filtered_df["Catégorie_d'IMC"].value_counts()

            fig = px.pie(
                values=bmi_dist.values,
                names=bmi_dist.index,
                title="BMI Category Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

def create_eligibility_analysis(filtered_df):
    """Create eligibility analysis"""
    st.header("Eligibility")

    # Calculate eligibility metrics
    total_donors = len(filtered_df)
    eligible_donors = filtered_df["Statut_d'éligibilité"].sum()
    eligibility_rate = (eligible_donors / total_donors * 100).round(1)

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Eligible Donors",
            f"{eligible_donors:,}",
            f"{eligibility_rate}% of total"
        )

    with col2:
        st.metric(
            "Total Ineligible Donors",
            f"{total_donors - eligible_donors:,}",
            f"{100 - eligibility_rate}% of total"
        )

    with col3:
        st.metric(
            "Overall Eligibility Rate",
            f"{eligibility_rate}%"
        )

    # Create columns for demographic patterns
    col1, col2 = st.columns(2)

    with col1:
        # Eligibility by age group
        age_elig = (
            filtered_df.groupby("Groupe_d'âge")["Statut_d'éligibilité"]
            .mean()
            .mul(100)
            .round(1)
        )

        fig = px.bar(
            x=age_elig.index,
            y=age_elig.values,
            title="Eligibility Rate by Age Group",
            labels={"x": "Age Group", "y": "Eligibility Rate (%)"},
            color=age_elig.values,
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Eligibility by BMI category
        bmi_elig = (
            filtered_df.groupby("Catégorie_d'IMC")["Statut_d'éligibilité"]
            .mean()
            .mul(100)
            .round(1)
        )

        fig = px.bar(
            x=bmi_elig.index,
            y=bmi_elig.values,
            title="Eligibility Rate by BMI Category",
            labels={"x": "BMI Category", "y": "Eligibility Rate (%)"},
            color=bmi_elig.values,
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)



def get_column_by_pattern(df, pattern):
    """Helper function to find column names containing a pattern"""
    matching_cols = [col for col in df.columns if pattern.lower() in col.lower()]
    return matching_cols[0] if matching_cols else None

def create_key_metrics(filtered_df):
    """Create key metrics with error handling"""
    metrics = {}

    # Total Donors
    metrics["total_donors"] = len(filtered_df)

    # Eligibility Rate
    try:
        metrics["eligibility_rate"] = filtered_df["Statut_d'éligibilité"].mean() * 100
    except:
        metrics["eligibility_rate"] = None

    # Average Age
    try:
        metrics["avg_age"] = filtered_df["Age"].mean()
    except:
        metrics["avg_age"] = None

    # Average Hemoglobin
    hemoglobin_col = get_column_by_pattern(filtered_df, "hémoglobine")
    if hemoglobin_col:
        try:
            metrics["avg_hemoglobin"] = filtered_df[hemoglobin_col].mean()
        except:
            metrics["avg_hemoglobin"] = None
    else:
        metrics["avg_hemoglobin"] = None

    return metrics

# --- Prediction Function ---
# @st.cache_data(show_spinner=False)
def get_prediction(form_data):
    """
    Sends form data to the backend and returns the prediction.
    This function is cached to avoid re-running the prediction logic.
    """
    try:
        flask_app_url = "http://127.0.0.1:5000/predict"
        response = requests.post(flask_app_url, json=form_data)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to Flask app: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Error decoding JSON response: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def geocode_arrondissements(df):
    """Geocode arrondissements to get their coordinates."""
    geolocator = Nominatim(user_agent="myGeocoder")

    arrondissements = df['Arrondissement_Matched'].unique()
    arrondissement_coords = {}

    for town in arrondissements:
        try:
            location = geolocator.geocode(town + ', Cameroon', timeout=10)
            if location:
                arrondissement_coords[town] = (location.latitude, location.longitude)
            time.sleep(1)  # Sleep to avoid hitting the rate limit
        except Exception as e:
            print(f"Geocoding error for {town}: {e}")
            time.sleep(5)

    coords_df = pd.DataFrame.from_dict(arrondissement_coords, orient='index', columns=['Latitude', 'Longitude'])
    coords_df.index.name = 'Arrondissement'
    coords_df.reset_index(inplace=True)

    return coords_df

def standardize_name(name):
    if pd.notna(name):
        return unidecode.unidecode(name.lower().strip())
    return name

def fuzzy_match_arrondissement(arrondissement, map_arrondissements):
    match = process.extractOne(arrondissement, map_arrondissements, scorer=fuzz.token_sort_ratio)
    return match[0] if match and match[1] >= 80 else arrondissement

def geocode_arrondissements(df):
    """Geocode arrondissements to get their coordinates."""
    geolocator = Nominatim(user_agent="myGeocoder")
    arrondissement_coords = {}

    for town in df['Arrondissement_Matched'].unique():
        try:
            location = geolocator.geocode(town + ', Cameroon', timeout=10)
            if location:
                arrondissement_coords[town] = (location.latitude, location.longitude)
            time.sleep(1)  # Sleep to avoid hitting the rate limit
        except Exception as e:
            print(f"Geocoding error for {town}: {e}")
            time.sleep(5)

    coords_df = pd.DataFrame.from_dict(arrondissement_coords, orient='index', columns=['Latitude', 'Longitude'])
    coords_df.index.name = 'Arrondissement'
    coords_df.reset_index(inplace=True)

    return coords_df

def main():
    st.set_page_config(**STREAMLIT_CONFIG)

    # Load processed data
    df = load_challenge_data()
    if df.empty:
        st.error("No processed data available")
        st.stop()

    # Load challenge dataset for mapping
    challenge_df = load_challenge_data()
    if challenge_df.empty:
        st.error("No challenge dataset available")
        st.stop()

    challenge_df['Arrondissement'] = challenge_df['Arrondissement_de_résidence'].apply(standardize_name)
    challenge_df['Arrondissement_Matched'] = challenge_df['Arrondissement'].apply(
        lambda x: fuzzy_match_arrondissement(x, challenge_df['Arrondissement'].unique())
    )
    arrondissement_coords_df = geocode_arrondissements(challenge_df)
    challenge_df = challenge_df.merge(arrondissement_coords_df, on='Arrondissement_Matched', how='left')

    map_geo = gpd.GeoDataFrame(
        challenge_df, 
        geometry=gpd.points_from_xy(challenge_df['Longitude'], challenge_df['Latitude']),
        crs="EPSG:4326"  # Adding coordinate reference system for better compatibility
    )
    cameroon_map = gpd.read_file(Path("data/processed/cmr_cities.zip"))

    # Filter data
    st.sidebar.header("Filter Data")
    age_groups = st.sidebar.multiselect(
        "Select Age Groups", 
        options=sorted(df["Groupe_d'âge"].unique().astype(str)), 
        default=sorted(df["Groupe_d'âge"].unique().astype(str))
    )
    filtered_df = df[df["Groupe_d'âge"].astype(str).isin(age_groups)] if age_groups else df

    # Create success metrics flags for later use
    filtered_df['is_eligible'] = filtered_df["Statut_d'éligibilité"] == 1
    filtered_df['is_repeat_donor'] = filtered_df["A-t-il_(elle)_déjà_donné_le_sang"] == "Oui"

    # Create dashboard
    st.title("Blood Donation Campaign Analytics")
    create_donor_profiling_analysis(filtered_df, challenge_df, cameroon_map)
    create_geographic_analysis(filtered_df)
    create_demographic_distribution(filtered_df)
    create_campaign_effectiveness_analysis(filtered_df)
    create_donor_retention_analysis(filtered_df)
    create_health_conditions_analysis(filtered_df)
    
    create_eligibility_analysis(filtered_df)

    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Data Preview")
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()