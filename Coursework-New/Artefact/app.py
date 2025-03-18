import os
import csv
import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import pycountry

# Initialize Flask application
app = Flask(__name__)

# Load CSV data with error handling
data_file = '2018-Happiness-Index-Cleaned.csv'
if os.path.isfile(data_file):
    df = pd.read_csv(data_file)
    print("CSV file loaded successfully!")
else:
    print("Error: CSV file not found!")
    df = None

# Preprocess DataFrame if data is loaded
if df is not None:
    df.columns = df.columns.str.strip()
    df.rename(columns={'Country or Region': 'Country or region', 'Happiness Score': 'Score'}, inplace=True)
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')  # Ensure 'Score' is numeric
    df.fillna({'Score': df['Score'].mean()}, inplace=True)  # Handle missing values

# Define home page route
@app.route('/')
def index():
    if df is None:
        return "Error: Data file is missing!", 500
    return render_template('index.html')

# Define statistics page route
@app.route('/statistics_page', methods=['GET', 'POST'])
def statistics_page():
    if df is None:
        return "Error: Data file is missing!", 500

    # Create bar charts
    bar_chart_html1 = px.bar(df, x='Country or region', y='Score', title='Happiness Score by Country',
                             labels={'Score': 'Happiness Score', 'Country or region': 'Country'},
                             color='Score', color_continuous_scale='viridis').to_html(full_html=False)
    bar_chart_html2 = px.bar(df, x='Country or region', y='GDP per capita', title='GDP per capita by Country',
                             labels={'GDP per capita': 'GDP per capita', 'Country or region': 'Country'},
                             color='Score', color_continuous_scale='viridis').to_html(full_html=False)

    # Create line charts
    line_chart_html1 = px.line(df, x='Country or region', y='Social support',
                               title='Social support per Country').to_html(full_html=False)
    line_chart_html2 = px.line(df, x='Country or region', y='Healthy life expectancy',
                               title='Healthy life expectancy by Country').to_html(full_html=False)

    # Create scatter plot
    scatter_plot_html = px.scatter(df, x='Country or region', y='Freedom to make life choices',
                                   color='Freedom to make life choices',
                                   color_continuous_scale='viridis').to_html(full_html=False)

    # Define continent mapping
    continent_mapping = {
        'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Morocco', 'Algeria'],
        'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia'],
        'Europe': ['Finland', 'Norway', 'Denmark', 'Iceland', 'Switzerland'],
        'North America': ['United States', 'Canada', 'Mexico'],
        'South America': ['Brazil', 'Argentina', 'Chile'],
        'Oceania': ['Australia', 'New Zealand'],
        'Middle East': ['Israel', 'United Arab Emirates', 'Qatar']
    }

    # Function to assign continent
    def assign_continent(country):
        for continent, countries in continent_mapping.items():
            if country in countries:
                return continent
        return 'Other'

    df['Continent'] = df['Country or region'].apply(assign_continent)

    # Handle selected continents
    selected_continents = request.form.getlist('continents') if request.method == 'POST' else list(df['Continent'].unique())
    filtered_df = df[df['Continent'].isin(selected_continents)]

    # Create sunburst charts
    sunburst_chart_html1 = px.sunburst(filtered_df, path=['Country or region'], values='Perceptions of corruption',
                                       title='Perceptions of Corruption by Country').to_html(full_html=False)
    sunburst_chart_html2 = px.sunburst(filtered_df, path=['Country or region'], values='Generosity',
                                       title='Generosity by Country').to_html(full_html=False)

    # Compute continent-based statistics
    continent_stats = {}
    for continent in selected_continents:
        continent_df = df[df['Continent'] == continent]
        
        if not continent_df.empty:
            continent_stats[continent] = {
                column: {
                    "Mean": round(continent_df[column].mean(), 2) if not continent_df[column].isnull().all() else "N/A",
                    "Median": round(continent_df[column].median(), 2) if not continent_df[column].isnull().all() else "N/A",
                    "Mode": round(continent_df[column].mode()[0], 2) if not continent_df[column].mode().empty else "N/A",
                    "Range": round(continent_df[column].max() - continent_df[column].min(), 2) if not continent_df[column].isnull().all() else "N/A"
                }
                for column in ['Score', 'GDP per capita', 'Social support', 'Healthy life expectancy',
                               'Freedom to make life choices', 'Generosity', 'Perceptions of corruption']
                if column in df.columns
            }

    return render_template('statistics_page.html',
                           bar_chart1=bar_chart_html1, bar_chart2=bar_chart_html2,
                           line_chart1=line_chart_html1, line_chart2=line_chart_html2,
                           scatter_plot=scatter_plot_html, sunburst_chart1=sunburst_chart_html1,
                           sunburst_chart2=sunburst_chart_html2,
                           selected_continents=selected_continents,
                           continent_stats=continent_stats)

# Define user poll CSV file
csv_file = "user_poll_data.csv"
if not os.path.isfile(csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(["Country", "Happiness Response", "Score"])

# User poll route
@app.route('/userpoll', methods=['GET', 'POST'])
def userpoll():
    all_countries = [country.name for country in pycountry.countries]
    if request.method == 'POST':
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow([request.form.get('Country'), request.form.get('happy'), request.form.get('Score')])
        return redirect(url_for('summary_page', message="Thank you for participating in the poll!"))
    return render_template('userpoll.html', all_countries=all_countries)

# Summary page route
@app.route('/summary')
def summary_page():
    if not os.path.isfile(csv_file):
        return render_template('summary.html', user_submissions=[], message=request.args.get('message', ''), pie_chart=None)
    user_df = pd.read_csv(csv_file)
    user_df['Score'] = pd.to_numeric(user_df['Score'], errors='coerce')
    pie_chart_html = None
    if not user_df.empty and user_df['Score'].notnull().any():
        pie_chart_html = px.pie(user_df, names='Country', values='Score',
                                title="User Happiness Scores by Country").to_html(full_html=False)
    return render_template('summary.html', user_submissions=user_df.to_dict(orient='records'),
                           message=request.args.get('message', ''), pie_chart=pie_chart_html)

# Run Flask application
if __name__ == "__main__":
    app.run(debug=True, port=5050)



     





