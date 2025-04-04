# Blood Donation Campaign Report

## How to Launch the Dashboard

### Steps to Launch the Dashboard

1.  **Open a Code Editor**
    Start by launching Visual Studio Code (VS Code).

2.  **Clone the Repository**
    Open source control, and take clone repository
    
    When asked to input repository, input [https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard](https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard)
    
    Clone the repository, and voila!, you have the dashboard in your work space.

    Navigate into the cloned directory:

    Next, open terminal, and making sure all required packages have been installed, run 

    ```bash
    streamlit run src/dashboard.py
    ```

    Access the Dashboard

    After running the command, your default web browser should automatically open, displaying the dashboard. If it doesn't, you can manually navigate to http://localhost:8501.

    Your dashboard should look something like this:

    ![Dashboard](..\reports\figures\dashboard_images\home.PNG)


## Dashboard Overview

The Blood Donation Campaign Dashboard provides a comprehensive analysis of blood donation data, allowing campaign organizers to make informed decisions. The dashboard features various visualizations that highlight donor demographics, campaign effectiveness, retention rates, and the impact of health conditions on donation eligibility. This enables a data-driven approach to enhance outreach and improve the overall effectiveness of blood donation campaigns.

We have the folllowing summary of our donors
![Total Summary of campaign](..\reports\figures\dashboard_images\summary_of_entire_campaign.PNG)

We can see that, out of the 1,846 donors, the average age was those of 31 years, and Average Hemoglobin level of 13.9g/dL, giving a percentage of 85.1% eligigbility rate. 
This summary results is expantiated below;

## 1. Donor Profiling

Let us now look at the profiles of our various donors, so as to have more insight of the demographics of the persons suitable for blood donation.

### 1.1 Donor by Geographical Town

Understanding the geographical distribution of donors helps identify key areas for targeted campaigns. Here is a summary of the distribution of donors as per the geographical location.

![summary of Geographical Town Chart](..\reports\figures\dashboard_images\summary_of_town_distribution.PNG)

The chart shows that Douala is the top contributor to donor numbers, with 97.4% of the total donations coming from this town. This highlights a concentrated area for potential campaigns, indicating where resources might be best allocated for maximum impact.

Our dashboard gives you the ability to switch between towns, and quarters allowing campaign organizers to tailor strategies based on local donor demographics and behaviors. We shall now look at the campaign details in the quarter of Douala 3 for example.

![Donor by douala 3](..\reports\figures\dashboard_images\douala.png)

**Summary of results:** From the results above, we see the highest donors (34) from Douala 3 are from Yassa.

### 1.2 Donor by Age Groups

We will then look at the age distribution of our donors. Age is a crucial metric for understanding which demographics are most engaged in blood donation. By identifying age groups that contribute the most, targeted outreach initiatives can be developed to encourage donations among a particular age group. 

![Donor_by_Age_Groups_Chart](..\reports\figures\dashboard_images\donor_per_age.png)

**Summary of results:** The majority of donors fall within the 26-35 age range, accounting for 826 donors, which indicates a strong base for outreach efforts targeted at  working-calss active youths. 

### 1.3 Donor by Profession

When we understand which professions are most represented among donor, this will help tailor campaigns to specific workers.

![Donor by Profession Chart](..\reports\figures\dashboard_images\donor_per_profession.png)

**Summary of results:** The professional background of donors reveals that students constitute the largest segment, making up 276 of the total donors. This insight can help us to organize donation drives in educational institutions.

### 1.4 Donor by Gender

Gender dynamics play a significant role in blood donation rates. 

![Donor by Gender Chart](..\reports\figures\dashboard_images\donor_per_gender.png)

**Summary of results:** The gender breakdown shows a predominance of male donors, who represent 1664 (90.1%) of the total. Strategies to increase female participation could be beneficial, especially in targeting messaging that resonates with women. Most women are often confused because of restriction on periods, breastfeeding etc, which also limits the number of female donors.

Conclusively, We can say the most ideal age group was those between 26-35 years, typical BMI category being surpoids, and predominant gender being Male, with the average hemoglobin being 14.0g/dL, of profession being students, for donation as shown below.

![ideal_donor](..\reports\figures\dashboard_images\ideal_donor.PNG)

## 2. Campaign Effectiveness

### 2.1 Effectiveness by Age and Gender

By evaluating the effectiveness of campaigns by age group, we identify which age groups are most responsive to outreach efforts. 

![Effectiveness by Age Chart](..\reports\figures\dashboard_images\campaign_effectiveness_by_age.png)

Campaign effectiveness by Gender

![Effectiveness by Gender Chart](..\reports\figures\dashboard_images\campaign_effectiveness_by_gender.png)


**Summary of results:** The analysis indicates that the 26-35 age group has the highest number of donations as 826 donors came from this age group, giving a success rate of 86.2%, and the least being those of 56-65 years old. This suggest that the older one gets, the more likely they are to naturally be exposed to diseases like diabetes, cardiac arrest etc which makes them ineligible for blood donation. As per the gender, men show a more effective campaign with 1664 donors, at a 90.1% success rate.

### 2.2 Effectiveness by Location

Geographic analysis reveals which areas have the highest and lowest participation rates. This information is vital for resource allocation in future campaigns. The chart below indicates how effective the campaign was in the various locations the campaign was carried out.

![Effectiveness by Location Chart](..\reports\figures\dashboard_images\campaign_effectiveness_by_location.png)

**Summary of results:** Geographic analysis reveals that Douala is the most effective location for campaigns, with Douala showing the highest contribution, 952(91.3%) to overall donations. About 14 donors did not precise their towns, and the least percentage of donors came from RAS, 6 donors, with a campaign effectiveness rate of zerol

### 2.3 Effectiveness by Profession

When we look at campaign effectiveness as per profession, we have the following results.

![Effectiveness by Profession Chart](..\reports\figures\dashboard_images\campaign_effectiveness_by_profession.png)

**Summary of results:** Students are the most effective donor group, contributing to 206 of total donations, giving a campaign effectiveness rate of 100%. This reinforces the need for student-focused outreach initiatives, such as partnerships with universities and colleges for more blood donation. Given that they indicated being unemployed, subsequent needs for employment can be made through the campaign.

## 3. Donor Retention
In this section, we look at the probability of a donor coming back for donation once more, based on their demographics.

### Summary of Retention Donors

Measuring donor retention is crucial for understanding the success of campaigns in maintaining long-term relationships with donors. Retention metrics provide insights into how effectively campaigns engage and re-engage donors. From the figure below, we see that 1,060 donors were first timers, while 786 were returning donors, giving a retention rate of 42.6%.

![Retention Summary Chart](..\reports\figures\dashboard_images\sumary_of_donor_retention.PNG)

**Repeating Donors:** 786 (42.6% of total donors)
**First-Time Donors:** 1,060 (57.4% of total donors)
**Overall Retention Rate:** 42.6%

**Summary of results:** The retention rate of 42.6% indicates a healthy level of return donors, signifying the importance of maintaining engagement with first-time donors and converting them into repeat contributors, and if eligible, this rate has the possibility of going higher.

### 3.1 Retention by Age Group

Analyzing retention rates by age group helps identify which age group are more likely to return for future donations. This will help us inform targeted strategies to enhance donor engagement in that particular age group.

![Retention by Age Group Chart](..\reports\figures\dashboard_images\donor_retention_age.png)

**Summary of results:** The analysis shows that older age groups (56-65) have a higher retention rate of 60%, suggesting effective engagement strategies within this demographic. This indicates that initiatives aimed at younger donors might need to be reinforced because eventhough they constitute the highest percentage of donors, their retention rate is low, meaning they often change their minds about donation.

### 3.2 Retention by Profession

Understanding retention by profession provides insights into which professional groups are more likely to return for additional donations. Given that majority of the donors were students, the professions will focus on the employed as shown in the chart below.

![Retention by Profession Chart](..\reports\figures\dashboard_images\donor_retention_by_profession.png)

**Summary of results:** The figure below shows our retention by profession. We can see that those in the medical field, human resource  managers, men of God, security etc have a 100% retention rate . The least represented were htraders, salon workers etc, indicating potential areas to enhance outreach amongst these professions.

### 3.3 Retention by Location

Evaluating retention rates across different geographic locations allows for a better understanding of where campaigns are succeeding or struggling.

![Retention by Location Chart](..\reports\figures\dashboard_images\donor_retention_location.png)

**Summary of results:** The chart illustrates that Douala has the highest retention rate among locations, reinforcing its importance in future campaigns. This suggests that strategies working in Douala should be analyzed and possibly replicated in other areas, globally, as a 100% successful rate was found in locations that the donors did not mention.

## 4. Health Conditions Impact

### Summary of Health Conditions

Health conditions stand to be the essential factor that makes a donor qualified for donation or not. Analyzing health conditions that lead to donor deferrals is essential for understanding barriers to donation. Addressing these issues will improve overall donor eligibility.

![Health Conditions Summary Chart](..\reports\figures\dashboard_images\summary_of_health_conditions_impact.PNG)

**Summary of results:** The overview reveals that unhealthy conditions led to a 21 deferral rate among potential donors, with the most common issues being people who suffer from cardiac arrest. This indicates a need for educational initiatives around health and wellness, as our retention is high amongst old participants, but they are few donors, and most suffer from cardiac diseases.

### Total Eligibility Summary

Understanding donor eligibility is crucial for assessing the potential donor pool. Asides health conditions, other factors makes one ineligible for donation. The chart below indicates the overall ineligibility stats of our donors

![Total Eligibility Summary Chart](..\reports\figures\dashboard_images\eligibility_summary.PNG)

**Total Eligible Donors:** 1,571 (85.1% of total)
**Total Ineligible Donors:** 275 (14.9% of total)
**Overall Eligibility Rate:** 85.1%

**Summary of results:** The majority of donors are eligible to donate blood, indicating a generally healthy donor pool and suggesting that outreach efforts can be focused on educating ineligible donors, to make the pool a complete 100%.

### 4.1 Eligibility by Age

Breaking down eligibility rates by age group helps identify which age group are most likely to meet donation criteria.

![Eligibility by Age Chart](..\reports\figures\dashboard_images\eligibility_by_age.png)

**Summary of results:** The analysis shows that older age groups, 56-65 years, have a lower eligibility rate, suggesting that health issues become more prevalent with age. This indicates a need for targeted health interventions for older populations. The most eligible age group were those of 36-45 years.

### 4.2 Eligibility by BMI

Examining eligibility based on BMI categories provides insights into how health metrics influence donor eligibility. The Body Mass index of an individual talks alot about their lifestyle, and so, this can help know how to target campaigns based on a particular lifestyle of persons.

![Eligibility by BMI Chart](..\reports\figures\dashboard_images\eligibility_by_BMI.png)

**Summary of results:** The figure indicates that individuals in the "Normal" BMI category have the highest eligibility rates, while those classified as "Obese" show significantly lower eligibility, and there was no one who was severely obesed. This can only reinforces the importance of promoting healthy lifestyles among potential donors.

## Raw Data and Navigation Menu

The dashboard also provides access to raw data for deeper analysis and understanding of our results. 

![raw_data](..\reports\figures\dashboard_images\raw_data.PNG)

## Menu bar
A navigation menu allows users to test for their eligibility based on the provided metrics, allowing our dashboard to be flexible and interactive. This is to enhance the user experience and facilitate the usage of our dashboard in different scenarios.

![check_eligibility](..\reports\figures\dashboard_images\check_eligibility.PNG)

Which takes you to the API for eligibility checking.

Check your eligibility using the link: [check_eligibility](../https://testsiteg.pythonanywhere.com/)