import os
import csv
import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import pycountry

# main Flask program
app = Flask(__name__)

# load CSV data (checking for issues)
try:
    df = pd.read_csv('2018-Happiness-Index-Cleaned.csv')
    print("CSV file loaded successfully!")
except FileNotFoundError:
    print("Error: CSV file not found! Make sure '2018-Happiness-Index-Cleaned.csv' exists.")
    df = None

# preprocess DataFrame
if df is not None:
    df.columns = df.columns.str.strip()
    df.rename(columns={'Country or Region': 'Country or region', 'Happiness Score': 'Score'}, inplace=True)

# ensure 'Score' is numerical
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')

# handle missing values in 'Score'
    if df['Score'].isnull().sum() > 0:
        print("Warning: 'Score' column has missing values!")
        df['Score'].fillna(df['Score'].mean(), inplace=True)

# home page of website
@app.route('/')
def index():
    print("Home Page Requested")

    if df is None:
        return "Error: Data file is missing!", 500

    print("Rendering Home Page...")
    return render_template('index.html')

# statistics page of website
@app.route('/statistics_page', methods=['GET', 'POST'])
def statistics_page():
    print("Statistics Page Requested")

    if df is None:
        return "Error: Data file is missing!", 500

    print("Rendering statistics...")
    stats_archive = {}
    non_numeric_columns = ['Country or region']

# create first bar chart using Plotly
    bar_fig2 = px.bar(
        df,
        x='Country or region',
        y='GDP per capita',
        title='GDP per capita by Country',
        labels={'GDP per capita': 'GDP per capita', 'Country or region': 'Country'},
        color='Score',
        color_continuous_scale='viridis'
    )
    
    bar_fig1 = px.bar(
        df,
        x='Country or region',
        y='Score',
        title='Happiness Score by Country',
        labels={'Score': 'Happiness Score', 'Country or region': 'Country'},
        color='Score',
        color_continuous_scale='viridis'
    )

# remove countries from x-axis
    bar_fig1.update_layout(xaxis=dict(showticklabels=False))
    bar_fig2.update_layout(xaxis=dict(showticklabels=False))
    
# convert bar charts to HTML for embedding
    bar_chart_html1 = bar_fig1.to_html(full_html=False)
    bar_chart_html2 = bar_fig2.to_html(full_html=False)

# create line plots using Plotly
    line_fig1 = px.line(df, x='Country or region', y='Social support', title='Social support per Country')
    line_fig2 = px.line(df, x='Country or region', y='Healthy life expectancy', title='Healthy life expectancy by Country')
    
# remove countries from x-axis
    line_fig1.update_layout(xaxis=dict(showticklabels=False))
    line_fig2.update_layout(xaxis=dict(showticklabels=False))
    
# convert line chart to HTML for embedding
    line_chart_html1 = line_fig1.to_html(full_html=False)
    line_chart_html2 = line_fig2.to_html(full_html=False)

# create scatter plot chart using Plotly
    scatter_fig = px.scatter(
        df,
        x='Country or region',
        y='Freedom to make life choices',
        color='Freedom to make life choices',
        color_continuous_scale='viridis'
    )

# remove countries from x-axis
    scatter_fig.update_layout(xaxis=dict(showticklabels=False))
# convert scatter plot chart to HTML for embedding
    scatter_plot_html = scatter_fig.to_html(full_html=False)

# define continent mapping (using lists)
    continent_mapping = {
        'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Ivory Coast', 'Ghana', 'Senegal', 'Somalia', 'Cameroon', 'Uganda', 'Benin', 'Niger', 'Sudan', 'Togo', 'Guinea', 'Lesotho', 'Angola', 'Madagascar', 'Zimbabwe', 'Botswana', 'Malawi', 'Namibia', 'Liberia', 'Mali', 'Mozambique', 'Kenya', 'Zambia', 'Mauritania', 'Ethiopia', 'Rwanda', 'Central African Republic', 'Burundi', 'Chad', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Sierra Leone', 'Mauritius'],
        'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Taiwan', 'Singapore', 'Malaysia', 'Thailand', 'Hong Kong', 'Azerbaijan', 'Turkmenistan', 'Kazakhstan', 'Uzbekistan', 'Kyrgyzstan', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal', 'Vietnam', 'Philippines', 'Myanmar', 'Cambodia', 'Laos', 'Iraq', 'Jordan', 'Lebanon', 'Armenia'],
        'Europe': ['Finland', 'Norway', 'Denmark', 'Iceland', 'Switzerland', 'Netherlands', 'Sweden', 'United Kingdom', 'Austria', 'Ireland', 'Germany', 'Belgium', 'Luxembourg', 'France', 'Malta', 'Czech Republic', 'Poland', 'Slovakia', 'Estonia', 'Lithuania', 'Slovenia', 'Romania', 'Latvia', 'Italy', 'Portugal', 'Serbia', 'Greece', 'Cyprus', 'Northern Cyprus', 'Russia', 'Kazakhstan', 'Belarus', 'Moldova', 'Kosovo', 'Hungary', 'Ukraine', 'Albania', 'Montenegro', 'Croatia', 'Bosnia and Herzegovina', 'Georgia'],
        'North America': ['United States', 'Canada', 'Mexico', 'Costa Rica', 'Panama', 'Guatemala', 'Belize', 'Trinidad & Tobago', 'Jamaica', 'Haiti', 'Honduras', 'El Salvador', 'Nicaragua', 'Dominican Republic'],
        'South America': ['Brazil', 'Argentina', 'Chile', 'Uruguay', 'Colombia', 'Ecuador', 'Bolivia', 'Paraguay', 'Peru', 'Venezuela'],
        'Oceania': ['Australia', 'New Zealand'],
        'Middle East': ['Israel', 'United Arab Emirates', 'Qatar', 'Saudi Arabia', 'Bahrain', 'Kuwait', 'Turkey', 'Cyprus', 'Iran', 'Syria', 'Yemen', 'Palestine'],
    }
    
# function to assign continent based on country
    def assign_continent(country):
        for continent, countries in continent_mapping.items():
            if country in countries:
                return continent

    df['Continent'] = df['Country or region'].apply(assign_continent)
    continents = df['Continent'].unique()

# handle check boxes for selected continents (in preparation for sunburst chart)
    if request.method == 'POST':
        selected_continents = request.form.getlist('continents') or list(df['Continent'].unique())
    else:
        selected_continents = list(df['Continent'].unique())

# filter DataFrame based on selected continents
    filtered_df = df[df['Continent'].isin(selected_continents)]

# creating sunburst charts using Plotly
    sunburst_fig1 = px.sunburst(
        filtered_df,
        path=['Country or region'],
        values='Perceptions of corruption',
        title='Perceptions of Corruption by Country',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    sunburst_fig1.update_layout(height=500, width=750, margin=dict(l=50, r=50, t=50, b=50))

    sunburst_fig2 = px.sunburst(
        filtered_df,
        path=['Country or region'],
        values='Generosity',
        title='Generosity by Country',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    sunburst_fig2.update_layout(height=500, width=750, margin=dict(l=50, r=50, t=50, b=50))

# convert sunburst chart to HTML for embedding
    sunburst_chart_html1 = sunburst_fig1.to_html(full_html=False)
    sunburst_chart_html2 = sunburst_fig2.to_html(full_html=False)
    
# clean country names to ensure consistency
    df['Country or region'] = df['Country or region'].str.strip()
    df['Continent'] = df['Country or region'].apply(assign_continent)

# initialise dictionaries for statistics
    stats_archive = {}
    continent_stats = {}

# list of non-numeric columns
    non_numeric_columns = ['Country or region', 'Continent']

# calculate mean, median, mode and range for all numeric columns
    for col in df.columns:
        if col not in non_numeric_columns:
            stats_data = pd.to_numeric(df[col], errors='coerce')

            if stats_data.notna().any():
                stats_archive[col] = {
                    'Mean': round(stats_data.mean(), 2),
                    'Median': round(stats_data.median(), 2),
                    'Mode': round(stats_data.mode().iloc[0], 2) if not stats_data.mode().empty else np.nan,
                    'Range': round(stats_data.max() - stats_data.min(), 2)
                }

# calculate mean, median, mode and range for continent-based statistics
    for continent in df['Continent'].unique():
        continent_df = df[df['Continent'] == continent]

        if not continent_df.empty:
            continent_stats[continent] = {}

            for col in df.columns:
                if col not in non_numeric_columns:
                    col_data = pd.to_numeric(continent_df[col], errors='coerce')

                    if col_data.notna().any():
                        continent_stats[continent][col] = {
                            'Mean': round(col_data.mean(), 2),
                            'Median': round(col_data.median(), 2),
                            'Mode': round(col_data.mode().iloc[0], 2) if not col_data.mode().empty else np.nan,
                            'Range': round(col_data.max() - col_data.min(), 2)
                        }

# debugging print statements
    print("Overall Statistics:", stats_archive)
    print("\nContinent-Based Statistics:", continent_stats)

# return template with embedded charts
    return render_template(
        'statistics_page.html',
        stats=stats_archive,
        bar_chart1=bar_chart_html1,
        bar_chart2=bar_chart_html2,
        line_chart1=line_chart_html1,
        line_chart2=line_chart_html2,
        scatter_plot=scatter_plot_html,
        sunburst_chart1=sunburst_chart_html1,
        sunburst_chart2=sunburst_chart_html2,
        continent_stats=continent_stats
    )


# define the user poll CSV file path
csv_file = "user_poll_data.csv"

# ensure the CSV file exists with proper headers
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Country", "Happiness Response", "Score"])

# store user submissions
user_submissions = []

# user poll page of website
@app.route('/userpoll', methods=['GET', 'POST'])
def userpoll():
    
# extract sorted list of all countries
    all_countries = [country.name for country in pycountry.countries]
    
    if request.method == 'POST':
        country = request.form.get('Country')
        happiness_response = request.form.get('happy')
        score = request.form.get('Score')

# append the user submission to the CSV file
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([country, happiness_response, score])

        message = "Thank you for participating in the poll!"
        return redirect(url_for('summary_page', message=message))

    return render_template('userpoll.html', all_countries=all_countries)

# summary page of website
@app.route('/summary')
def summary_page():
    message = request.args.get('message', '')

# ensure CSV file exists
    if not os.path.isfile(csv_file):
        return render_template('summary.html', user_submissions=[], message=message, pie_chart=None)

# load user submissions from CSV
    user_df = pd.read_csv(csv_file)

# debugging print to check CSV structure
    print("User Poll Data (First 5 rows):\n", user_df.head())

# ensure required columns exist in the user CSV
    required_columns = {'Country', 'Happiness Response', 'Score'}
    if not required_columns.issubset(set(user_df.columns)):
        return "Error: The user poll data is missing required columns!", 500
    
# fill missing country names with 'Unknown'
    user_df['Country'] = user_df['Country'].fillna('Unknown')

# ensure 'Country' column is treated as a string
    user_df['Country'] = user_df['Country'].astype(str)

# convert 'Score' to numeric (handle errors safely)
    user_df['Score'] = pd.to_numeric(user_df['Score'], errors='coerce')

# if the main dataset is loaded, match actual happiness scores
    if df is not None:
        df['Country or region'] = df['Country or region'].str.lower()

# match user poll responses with actual happiness scores
        user_df['Actual Score'] = user_df['Country'].apply(
            lambda c: df.loc[df['Country or region'] == c.lower(), 'Score'].values[0]
            if (df['Country or region'] == c.lower()).any() else "N/A"
        )

# generate a pie chart if data exists using Plotly
    pie_chart_html = None
    if not user_df.empty and user_df['Score'].notnull().any():
        pie_fig = px.pie(user_df, names='Country', values='Score', title="User Happiness Scores by Country")
        pie_chart_html = pie_fig.to_html(full_html=False)

# convert DataFrame to a list of dictionaries for rendering
    user_submissions = user_df.to_dict(orient='records')

    return render_template(
        'summary.html',
        user_submissions=user_submissions,
        message=message,
        pie_chart=pie_chart_html
    )

# Flask running the app on computer's ID
if __name__ == "__main__":
    app.run(debug=True, port=5000)
     





