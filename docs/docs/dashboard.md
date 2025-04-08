# Blood Donation Campaign Dashboard

Welcome to the documentation for the Blood Donation Campaign Analytics Dashboard.

## Overview

This dashboard provides analysis and visualization tools for blood donation campaign data, helping to:
- Track donor demographics
- Analyze eligibility patterns
- Visualize geographic distribution
- Generate insights for campaign optimization

## Getting Started

```python
import streamlit as st
from blood_donation_campaign_dashboard.src.dashboard import main
```

# Run the dashboard
main()






# Dashboard Components

::: src.dashboard
    handler: python
    options:
      show_root_heading: true
      show_source: true
      members:
        - create_geographic_analysis
        - create_donor_profiling_analysis
        - create_demographic_distribution
        - create_eligibility_analysis
        - create_sentiment_analysis


