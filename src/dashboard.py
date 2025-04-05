import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import requests
import json 
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
import matplotlib.pyplot as plt
from textblob import TextBlob
import re
from wordcloud import WordCloud


import os
from pathlib import Path

def get_data_path():
    """Get correct data path for both local and deployed environments"""
    root_dir = Path(__file__).parent.parent
    data_path = root_dir / "data" / "processed" / "processed.xlsx"
    if not data_path.exists():
        # Fallback for deployment
        data_path = Path("data/processed/processed.xlsx")
    return data_path

DATA_PATH = get_data_path()




# Configuration
DATA_PATH = Path("data/processed/processed.xlsx")
STREAMLIT_CONFIG = {
    "page_title": "Blood Donation Dashboard",
    "page_icon": "🩸",
    "layout": "wide",
    "initial_sidebar_state": "auto",
    "menu_items": {
        "About": "Blood Donation Campaign Analytics Dashboard",
        "Get help": "https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard",
        "Report a bug": "https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard/issues"
    }
}

def get_screen_width():
    """Get current screen width using streamlit's get_option API"""
    try:
        if 'screen_width' not in st.session_state:
            st.session_state.screen_width = 1200
        
        st.markdown(
            """
            <script>
                var screenWidth = window.innerWidth;
                if (window.streamlitPythonConnection) {
                    window.streamlitPythonConnection.setSessionState({
                        screen_width: screenWidth
                    });
                }
            </script>
            """,
            unsafe_allow_html=True
        )
        return st.session_state.screen_width
    except:
        return 1200

def get_responsive_columns(num_columns):
    """Return responsive column count based on screen size"""
    screen_width = get_screen_width()
    if screen_width < 768:
        return 1
    elif screen_width < 992:
        return min(2, num_columns) 
    return num_columns

def create_responsive_columns(num_columns):
    """Create responsive columns based on screen width"""
    return st.columns(get_responsive_columns(num_columns))

def get_responsive_chart_config(is_mobile=False):
    """Get responsive chart configuration"""
    return {
        "height": 350 if is_mobile else 500,
        "margin": dict(l=10, r=10, t=30, b=10),
        "autosize": True,
        "showlegend": not is_mobile
    }

def create_responsive_chart(fig, use_container_width=True):
    """Create responsive plotly chart"""
    is_mobile = get_screen_width() < 768
    config = get_responsive_chart_config(is_mobile)
    fig.update_layout(**config)
    return st.plotly_chart(fig, use_container_width=use_container_width)

def create_responsive_map(m, height=None):
    """Create responsive folium map"""
    if height is None:
        height = 350 if get_screen_width() < 768 else 500
    return st_folium(m, width=None, height=height)

def display_responsive_metrics(metrics):
    """Display metrics responsively"""
    col_count = get_responsive_columns(4)
    cols = create_responsive_columns(col_count)
    
    metrics_data = [
        ("Total Donors", f"{metrics['total_donors']:,}", None),
        ("Eligibility Rate", f"{metrics['eligibility_rate']:.1f}%" if metrics['eligibility_rate'] else "N/A", None),
        ("Average Age", f"{metrics['avg_age']:.1f} years" if metrics['avg_age'] else "N/A", None),
        ("Avg Hemoglobin", f"{metrics['avg_hemoglobin']:.1f} g/dL" if metrics['avg_hemoglobin'] else "N/A", None)
    ]
    
    for i, col in enumerate(cols):
        with col:
            start_idx = i * (len(metrics_data) // col_count)
            end_idx = (i + 1) * (len(metrics_data) // col_count)
            for metric_name, value, delta in metrics_data[start_idx:end_idx]:
                st.metric(metric_name, value, delta)


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
    """Create geographic distribution visualizations with optimized map loading"""
    st.header("Map Donor Distribution")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Interactive Map", "Static Map", "Arrondissements", "Quartier Analysis"])

    with tab1:
        # Show loading state while generating map
        with st.spinner("Loading map..."):
            try:
                # Cache the coordinates generation
                @st.cache_data(ttl=3600)  # Cache for 1 hour
                def get_map_data(df):
                    """Cache map data generation to prevent reloading"""
                    # Get cached coordinates
                    cached_coords = get_cached_coordinates()
                    
                    # Create a copy to avoid modifying original
                    df_with_coords = df.copy()
                    
                    # Use cached coordinates instead of geocoding
                    df_with_coords['coordinates'] = df_with_coords['Arrondissement_de_résidence'].map(
                        lambda x: cached_coords.get(x.upper(), cached_coords["YAOUNDE"])
                    )
                    
                    df_with_coords['Latitude'] = df_with_coords['coordinates'].apply(lambda x: x[0])
                    df_with_coords['Longitude'] = df_with_coords['coordinates'].apply(lambda x: x[1])
                    
                    return df_with_coords

                # Get cached map data
                map_data = get_map_data(filtered_df)

                # Create base map once and cache it
                @st.cache_data(ttl=3600)
                def create_base_map():
                    """Create and cache base map"""
                    m = folium.Map(location=[3.848, 11.5021], zoom_start=6)
                    folium.TileLayer('cartodbpositron').add_to(m)
                    return m

                # Get cached base map
                m = create_base_map()

                # Add marker cluster
                marker_cluster = MarkerCluster().add_to(m)

                # Add markers efficiently
                for idx, row in map_data.iterrows():
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

                # Add layer control
                folium.LayerControl().add_to(m)

                # Display map
                st_folium(m, width=None, height=500)

                # Show map metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Total Locations",
                        len(map_data['Arrondissement_de_résidence'].unique()),
                        "unique arrondissements"
                    )
                with col2:
                    st.metric(
                        "Coverage Area",
                        f"{len(map_data['Quartier_de_Résidence'].unique()):,}",
                        "unique quartiers"
                    )
                with col3:
                    st.metric(
                        "Mapped Donors",
                        f"{len(map_data):,}",
                        "total donors"
                    )

            except Exception as e:
                st.error(f"Error creating map: {str(e)}")
                st.info("Please ensure geographic data is available")

    with tab2:
        st.subheader("Static Map Distribution")
        
        with st.spinner("Loading static map..."):
            try:
                # Load the Cameroon map shapefile
                cameroon_map = gpd.read_file('data/processed/cmr_cities.zip')

                # Create a figure and axis
                fig, ax = plt.subplots(figsize=(12, 10))

                # Plot base map
                cameroon_map.plot(ax=ax, color='lightgrey')

                # Create GeoDataFrame for donors
                donors_geo = gpd.GeoDataFrame(
                    map_data,  # Use already processed map_data
                    geometry=gpd.points_from_xy(map_data.Longitude, map_data.Latitude)
                )
                donors_geo.crs = cameroon_map.crs

                # Plot donor locations
                donors_geo.plot(
                    ax=ax,
                    marker='o',
                    color='red',
                    markersize=5,
                    label='Donors',
                    alpha=0.6
                )

                # Customize plot
                plt.title('Geographical Distribution of Blood Donors in Cameroon')
                plt.legend()
                plt.axis('equal')
                ax.grid(True, linestyle='--', alpha=0.6)

                # Add major city labels
                major_cities = {
                    'Yaoundé': (3.848, 11.5021),
                    'Douala': (4.0511, 9.7679),
                    'Bamenda': (5.9631, 10.1591),
                    'Garoua': (9.3017, 13.3921),
                    'Maroua': (10.5910, 14.3158)
                }

                for city, coords in major_cities.items():
                    ax.annotate(
                        city,
                        xy=coords,
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(
                            boxstyle='round,pad=0.5',
                            fc='white',
                            ec='gray',
                            alpha=0.7
                        )
                    )

                # Display map and metrics
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.pyplot(fig)
                with col2:
                    st.metric("Total Locations Mapped", len(donors_geo['Arrondissement_de_résidence'].unique()))
                    st.metric("Donor Density", f"{len(donors_geo) / cameroon_map.geometry.area.sum():.2f} donors/km²")

            except Exception as e:
                st.error(f"Error creating static map: {str(e)}")
                st.info("Please ensure geographic data and shapefiles are available")

    with tab3:
        # Arrondissement analysis
        st.subheader("Donor Distribution by Arrondissement")
        
        # Calculate arrondissement metrics
        arrond_counts = filtered_df["Arrondissement_de_résidence"].value_counts()
        top_10_arrond = arrond_counts.head(10)
        
        # Create summary DataFrame
        arrond_df = pd.DataFrame({
            "Arrondissement": top_10_arrond.index,
            "Donors": top_10_arrond.values,
            "Percentage": (top_10_arrond.values / len(filtered_df) * 100).round(1)
        })
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(
                arrond_df,
                x="Donors",
                y="Arrondissement",
                orientation='h',
                title="Top 10 Arrondissements by Donor Count",
                labels={"Donors": "Number of Donors"},
                color="Donors",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Detailed metrics table
            st.dataframe(
                arrond_df,
                column_config={
                    "Arrondissement": "Arrondissement",
                    "Donors": st.column_config.NumberColumn(
                        "Number of Donors",
                        help="Total number of donors from this arrondissement",
                        format="%d"
                    ),
                    "Percentage": st.column_config.NumberColumn(
                        "% of Total Donors",
                        help="Percentage of total donors from this arrondissement",
                        format="%.1f%%"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

    with tab4:
        # Quartier analysis
        st.subheader("Quartier Distribution Analysis")
        
        # Arrondissement selector
        selected_arrond = st.selectbox(
            "Select Arrondissement or Quartier to see distribution",
            options=sorted(filtered_df["Arrondissement_de_résidence"].unique())
        )
        
        # Filter data for selected arrondissement
        arrond_data = filtered_df[filtered_df["Arrondissement_de_résidence"] == selected_arrond]
        quartier_counts = arrond_data["Quartier_de_Résidence"].value_counts()
        
        # Create visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of quartier distribution
            fig = px.bar(
                x=quartier_counts.head(10).values,
                y=quartier_counts.head(10).index,
                orientation='h',
                title=f"Top 10 Quartiers in {selected_arrond}",
                labels={"x": "Number of Donors", "y": "Quartier"},
                color=quartier_counts.head(10).values,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Quartier metrics
            quartier_metrics = pd.DataFrame({
                "Quartier": quartier_counts.index,
                "Donors": quartier_counts.values,
                "Percentage": (quartier_counts.values / len(arrond_data) * 100).round(1)
            })
            
            st.dataframe(
                quartier_metrics,
                column_config={
                    "Quartier": "Quartier",
                    "Donors": st.column_config.NumberColumn(
                        "Number of Donors",
                        help="Total number of donors from this quartier",
                        format="%d"
                    ),
                    "Percentage": st.column_config.NumberColumn(
                        "% of Arrondissement",
                        help="Percentage of donors in this arrondissement",
                        format="%.1f%%"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

def create_health_conditions_analysis(filtered_df):
    """Analyze and visualize the impact of health conditions on eligibility"""
    st.header("Health Conditions & Eligibility")

    # Helper function to extract condition name from column
    def clean_condition_name(column_name):
        """Extract condition name from between square brackets"""
        import re
        match = re.search(r'\[(.*?)\]', column_name)
        return match.group(1) if match else column_name

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
    
    # Calculate deferrals using original column names
    total_deferrals = filtered_df[all_conditions].apply(
        lambda x: x.value_counts().get("Oui", 0)
    ).sort_values(ascending=True)

    # Create display names mapping but keep original data
    display_names = {col: clean_condition_name(col) for col in total_deferrals.index}
    
    # Create visualization data with display names
    viz_data = pd.DataFrame({
        'Original': total_deferrals.index,
        'Display': [display_names[col] for col in total_deferrals.index],
        'Values': total_deferrals.values
    })

    # Calculate other metrics using original column names
    total_deferral_rate = (
        filtered_df[all_conditions].eq("Oui").any(axis=1).mean() * 100
    ).round(1)
    health_eligible = len(filtered_df) - filtered_df[all_conditions].eq("Oui").any(axis=1).sum()

    # Create summary DataFrame with both original and display names
    summary_df = pd.DataFrame({
        "Original": total_deferrals.index,
        "Condition": [display_names[col] for col in total_deferrals.index],
        "Deferrals": total_deferrals.values,
        "Percentage": (total_deferrals.values / len(filtered_df) * 100).round(1)
    })

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Impact Visualization", "Detailed Summary"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart using display names
            fig = px.bar(
                viz_data,
                x='Values',
                y='Display',
                orientation="h",
                title="Health Conditions Impact on Eligibility",
                labels={
                    "Values": "Number of Deferrals",
                    "Display": "Condition"
                },
                color='Values',
                color_continuous_scale="Reds"
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Detailed Health Conditions Summary")
        # Display using formatted names but keep original data
        st.dataframe(
            summary_df[["Condition", "Deferrals", "Percentage"]],  # Exclude Original column from display
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
            # Age group contribution analysis - Fixed version
            age_contributions = pd.DataFrame({
                "Total_Donors": filtered_df.groupby("Groupe_d'âge").size(),
                "Eligible_Donors": filtered_df[filtered_df["Statut_d'éligibilité"] == 1].groupby("Groupe_d'âge").size()
            }).reset_index()  # Reset index to make age groups a column
            
            age_contributions["Success_Rate"] = (
                age_contributions["Eligible_Donors"] / age_contributions["Total_Donors"] * 100
            ).round(1)
            
            fig = px.bar(
                data_frame=age_contributions,  # Pass the DataFrame
                x="Total_Donors",  # Use column name
                y="Groupe_d'âge",  # Use column name
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

def create_donor_profiling_analysis(filtered_df):
    """Analyze and profile ideal donors based on demographic and health features"""

    st.header("Profiling Ideal Donors")


    # Create success metrics for profiling
    filtered_df['is_eligible'] = filtered_df["Statut_d'éligibilité"] == 1
    filtered_df['is_repeat_donor'] = filtered_df["A-t-il_(elle)_déjà_donné_le_sang"] == "Oui"
    
    tab1, tab2 , tab3 = st.tabs(["Ideal Donor Profile", "Clustering Insights",  "Demographic Success Patterns"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create profile metrics for eligible, repeat donors
            ideal_donors = filtered_df[
                (filtered_df['is_eligible']) & 
                (filtered_df['is_repeat_donor'])
            ]
            
            if len(ideal_donors) == 0:
                st.warning("No ideal donors found with current filters")
                return
            
            try:
                # Calculate profile characteristics with error handling
                profile_metrics = {
                    "Age_Range": ideal_donors["Groupe_d'âge"].mode()[0],
                    "Gender": ideal_donors["Genre"].mode()[0],
                    "BMI_Category": ideal_donors["Catégorie_d'IMC"].mode()[0],
                    "Profession": ideal_donors["Profession"].mode()[0],
                    "Location": ideal_donors["Arrondissement_de_résidence"].mode()[0],
                    "Success_Rate": float(len(ideal_donors)) / len(filtered_df) * 100
                }

                # Add hemoglobin metric only if column exists
                hemoglobin_col = next((col for col in filtered_df.columns if "hémoglobine" in col.lower()), None)
                if hemoglobin_col:
                    hemoglobin_mean = ideal_donors[hemoglobin_col].mean()
                    if pd.notnull(hemoglobin_mean):
                        profile_metrics["Avg_Hemoglobin"] = round(hemoglobin_mean, 1)
                
            except Exception as e:
                st.error(f"Error calculating profile metrics: {str(e)}")
                return
            
            # Display ideal donor profile
            st.subheader("Ideal Donor Profile")
            
            # Create three-column metrics display
            m1, m2, m3 = st.columns(3)
            
            with m1:
                st.metric("Most Common Age Group", profile_metrics["Age_Range"])
                st.metric("Typical BMI Category", profile_metrics["BMI_Category"])
            
            with m2:
                st.metric("Predominant Gender", profile_metrics["Gender"])
                if "Avg_Hemoglobin" in profile_metrics:
                    st.metric("Average Hemoglobin", f"{profile_metrics['Avg_Hemoglobin']} g/dL")
                else:
                    st.metric("Average Hemoglobin", "N/A")
            
            with m3:
                st.metric("Common Profession", profile_metrics["Profession"])
                st.metric("Success Rate", f"{profile_metrics['Success_Rate']:.1f}%")

        with col2:
            # Success factors visualization
            success_factors = pd.DataFrame({
                "Factor": ["Age Match", "Gender Match", "BMI Match"],
                "Success_Rate": [
                    (filtered_df["Groupe_d'âge"] == profile_metrics["Age_Range"]).mean() * 100,
                    (filtered_df["Genre"] == profile_metrics["Gender"]).mean() * 100,
                    (filtered_df["Catégorie_d'IMC"] == profile_metrics["BMI_Category"]).mean() * 100
                ]
            })
            
            fig = px.bar(
                success_factors,
                x="Success_Rate",
                y="Factor",
                orientation="h",
                title="Success Factors Impact",
                labels={"Success_Rate": "Match Rate (%)"},
                color="Success_Rate",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Clustering insights
        sheet = clustering_data_sanitisation( filtered_df )
        st.subheader("Clustering Insights")
        col1, col2 = st.columns(2)
        with col1:
            perform_kmeans_clustering( sheet , show_plot=True)
        with col2:
            st.info("The value above each cluster bar represents the Pecentage of the dataset held by that cluster" )
            mine_cluster_information(sheet)
        

    with tab3:
        # Demographic success patterns
        st.subheader("Success Patterns by Demographics")
        
        # Calculate success rates by combined demographics
        demo_success = filtered_df.groupby(["Groupe_d'âge", "Genre", "Catégorie_d'IMC"])["is_eligible"].agg([
            "count",
            "mean"
        ]).reset_index()
        demo_success["success_rate"] = demo_success["mean"] * 100
        
        # Create visualization
        fig = px.scatter(
            demo_success,
            x="Groupe_d'âge",
            y="success_rate",
            size="count",
            color="Genre",
            facet_col="Catégorie_d'IMC",
            title="Success Patterns by Age, Gender, and BMI",
            labels={
                "success_rate": "Success Rate (%)",
                "Groupe_d'âge": "Age Group",
                "count": "Number of Donors"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

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

# --- Prediction Function  ---
#@st.cache_data(show_spinner=False)
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


def main():
    # Configure page settings
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Load data
    df = load_data()
    
    # Print available columns for debugging
    print("Available columns:", df.columns.tolist())
    
    # Sidebar filters with safe handling of age groups
    st.sidebar.header("Filter Data")
    try:
        age_groups = st.sidebar.multiselect(
            "Select Age Groups",
            options=list(sorted(df["Groupe_d'âge"].unique().astype(str))),
            default=list(sorted(df["Groupe_d'âge"].unique().astype(str)))
        )
    except Exception as e:
        st.error(f"Error loading age groups: {str(e)}")
        age_groups = []
    
    # Safe filtering with error handling
    try:
        filtered_df = df[df["Groupe_d'âge"].astype(str).isin(age_groups)] if age_groups else df
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        filtered_df = df
    
    st.sidebar.markdown("---")
    st.sidebar.header("Check Your Eligibility")


    if st.sidebar.button("Vérifier mon éligibilité", use_container_width=True):
        st.sidebar.info("Redirecting to eligibility check website...")
        st.sidebar.markdown(
            f'<a href="https://testsiteg.pythonanywhere.com/" target="_blank" rel="noopener noreferrer" '
            f'style="display: inline-block; width: 100%; text-align: center; '
            f'text-decoration: none; background-color: transparent;">'
            f'Click here if not redirected automatically</a>', 
            unsafe_allow_html=True
        )
        st.sidebar.markdown(
            '<script>window.open("https://testsiteg.pythonanywhere.com/", "_blank");</script>', 
            unsafe_allow_html=True
        )


      
    # Main dashboard layout
    st.title("Blood Donation Campaign Analytics")
    
    # Key Metrics with error handling
    metrics = create_key_metrics(filtered_df)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Donors",
            f"{metrics['total_donors']:,}"
        )
    
    with col2:
        if metrics["eligibility_rate"] is not None:
            st.metric(
                "Eligibility Rate",
                f"{metrics['eligibility_rate']:.1f}%"
            )
        else:
            st.metric("Eligibility Rate", "N/A")
    
    with col3:
        if metrics["avg_age"] is not None:
            st.metric(
                "Average Age",
                f"{metrics['avg_age']:.1f} years"
            )
        else:
            st.metric("Average Age", "N/A")
    
    with col4:
        if metrics["avg_hemoglobin"] is not None:
            st.metric(
                "Avg Hemoglobin",
                f"{metrics['avg_hemoglobin']:.1f} g/dL"
            )
        else:
            st.metric("Avg Hemoglobin", "N/A")



    create_geographic_analysis(filtered_df)
    create_demographic_distribution(filtered_df) 
    create_health_conditions_analysis(filtered_df)
    create_donor_profiling_analysis(filtered_df)
    create_campaign_effectiveness_analysis(filtered_df)       
    create_donor_retention_analysis(filtered_df)       
    create_eligibility_analysis(filtered_df)

    # Raw Data Table
    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Data Preview")
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()