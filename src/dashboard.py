import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import folium
from streamlit_folium import st_folium
import requests
import json 
from clustering_components import (
perform_kmeans_clustering, 
mine_cluster_information,
clustering_data_sanitisation,
)


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

def create_geographic_analysis(filtered_df):
    """Create geographic distribution visualizations"""
    st.header("Geographic Distribution")
    
    # Filter data based on selection
    geo_df = filtered_df.copy()
    
    # Get top 10 arrondissements by donor count
    arrond_counts = geo_df["Arrondissement_de_résidence"].value_counts()
    top_10_arrond = arrond_counts.head(10)
    
    # Create DataFrame for top 10 arrondissements
    arrond_df = pd.DataFrame({
        "Arrondissement": top_10_arrond.index,
        "Donors": top_10_arrond.values,
        "Percentage": (top_10_arrond.values / len(geo_df) * 100).round(1)
    })
    
    # Distribution table with metrics
    total_donors = top_10_arrond.sum()
    total_percentage = (total_donors / len(geo_df) * 100).round(1)
    
    
    
    # Create tabs for different views
    tab2, tab1 = st.tabs(["Quartier Analysis", "Top 10 Arrondissements"])
    
    with tab1:
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
    
    with tab2:
        # Quartier Analysis for selected arrondissement
        selected_arrond = st.selectbox(
            "Select Arrondissement to see Quartier distribution",
            options=top_10_arrond.index
        )
        
        quartier_df = geo_df[
            geo_df["Arrondissement_de_résidence"] == selected_arrond
        ]["Quartier_de_Résidence"].value_counts()
        
        # Show top 10 quartiers for selected arrondissement
        top_10_quartiers = quartier_df.head(10)
        
        fig = px.bar(
            x=top_10_quartiers.index,
            y=top_10_quartiers.values,
            title=f"Top 10 Quartiers in {selected_arrond}",
            labels={"x": "Quartier", "y": "Number of Donors"},
            color=top_10_quartiers.values,
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Summary Statistics
    st.subheader("Geographic Distribution Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Top Arrondissement",
            top_10_arrond.index[0],
            f"{top_10_arrond.values[0]} donors"
        )
    
    with col2:
        st.metric(
            "Contribution",
            f"{total_percentage}%",
            f"of total {len(geo_df):,} donors"
        )
    
    with col3:
        avg_donors = int(top_10_arrond.mean())
        st.metric(
            "Average Donors",
            f"{avg_donors:,}",
            f"per top arrondissement"
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
    st.header("Donor Profiling")

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

    with st.sidebar.form("eligibility_form"):
        age = st.number_input("Âge (ans)", min_value=0, max_value=120, value=30)
        poids = st.number_input("Poids (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
        genre = st.selectbox("Genre", ["Homme", "Femme"])
        taille = st.number_input("Taille (cm)", min_value=0, max_value=250, value=170)
        chronic_diseases = st.radio("Avez-vous une maladie chronique ?", ["Oui", "Non"])
        transmissible_diseases = st.radio("Avez-vous une maladie transmissible ?", ["Oui", "Non"])

        submit_button = st.form_submit_button("Vérifier mon éligibilité")

        # --- Prediction ---
        if submit_button:
            # form data
            form_data = {
                "age": age,
                "poids": poids,
                "genre": genre,
                "taille": taille,
                "chronic_diseases": chronic_diseases,
                "transmissible_diseases": transmissible_diseases,
            }

            prediction_placeholder = st.empty()
            with prediction_placeholder:
                st.info("Please wait while we check your eligibility...")

            result = get_prediction(form_data)

            prediction_placeholder.empty()

            # prediction results
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                probability = result["probability"]
                if float ( probability ) >= 0.4:
                    prediction = "1"
                else:
                    prediction = "0"

                if prediction == "1":
                    st.success(f"Félicitations ! Vous êtes éligible au don de sang. Probabilité d'éligibilité : {probability}")
                else:
                    st.error(f"Désolé, vous n'êtes pas éligible au don de sang. Probabilité d'éligibilité : {probability}")

      
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

    # Rest of the dashboard sections
    create_donor_profiling_analysis(filtered_df)
    create_geographic_analysis(filtered_df)
    create_demographic_distribution(filtered_df)
    create_campaign_effectiveness_analysis(filtered_df)
    create_donor_retention_analysis(filtered_df)
    create_health_conditions_analysis(filtered_df)
    create_eligibility_analysis(filtered_df)

    # Raw Data Table
    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Data Preview")
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()