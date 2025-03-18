import os
import csv
import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import pycountry

# creating a flask web application
app = Flask(__name__)

# loading csv file with print error handling messages
data_file = '2018-Happiness-Index-Cleaned.csv'
if os.path.isfile(data_file):
    df = pd.read_csv(data_file)
    print("CSV file loaded successfully!")
else:
    print("Error: CSV file not found!")
    df = None

# cleaning and processing the dataframe if it is not empty
if df is not None:
    df.columns = df.columns.str.strip()
    df.rename(columns={'Country or Region': 'Country or region', 'Happiness Score': 'Score'}, inplace=True)
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')
    df.fillna({'Score': df['Score'].mean()}, inplace=True)  

# creating home page
@app.route('/')
def index():
    if df is None:
        return "Error: Data file is missing!", 500
    return render_template('index.html')

# creating statistics page
@app.route('/statistics_page', methods=['GET', 'POST'])
def statistics_page():
    if df is None:
        return "Error: Data file is missing!", 500

    # creating bar charts
    bar_chart_html1 = px.bar(df, x='Country or region', y='Score', title='Happiness Score by Country', labels={'Score': 'Happiness Score', 'Country or region': 'Country'}, color='Score', color_continuous_scale='viridis').to_html(full_html=False)
    bar_chart_html2 = px.bar(df, x='Country or region', y='GDP per capita', title='GDP per capita by Country', labels={'GDP per capita': 'GDP per capita', 'Country or region': 'Country'}, color='Score', color_continuous_scale='viridis').to_html(full_html=False)

    # creating line charts
    line_chart_html1 = px.line(df, x='Country or region', y='Social support', title='Social support per Country').to_html(full_html=False)
    line_chart_html2 = px.line(df, x='Country or region', y='Healthy life expectancy', title='Healthy life expectancy by Country').to_html(full_html=False)

    # creating scatter plot
    scatter_plot_html = px.scatter(df, x='Country or region', y='Freedom to make life choices', color='Freedom to make life choices', color_continuous_scale='viridis').to_html(full_html=False)

# mapping countries to their corresponding continents
    continent_mapping = {
        'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Ivory Coast', 'Ghana', 'Senegal', 'Somalia', 'Cameroon', 'Uganda', 'Benin', 'Niger', 'Sudan', 'Togo', 'Guinea', 'Lesotho', 'Angola', 'Madagascar', 'Zimbabwe', 'Botswana', 'Malawi', 'Namibia', 'Liberia', 'Mali', 'Mozambique', 'Kenya', 'Zambia', 'Mauritania', 'Ethiopia', 'Rwanda', 'Central African Republic', 'Burundi', 'Chad', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Sierra Leone', 'Mauritius'],
        'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Taiwan', 'Singapore', 'Malaysia', 'Thailand', 'Hong Kong', 'Azerbaijan', 'Turkmenistan', 'Kazakhstan', 'Uzbekistan', 'Kyrgyzstan', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal', 'Vietnam', 'Philippines', 'Myanmar', 'Cambodia', 'Laos', 'Iraq', 'Jordan', 'Lebanon', 'Armenia'],
        'Europe': ['Finland', 'Norway', 'Denmark', 'Iceland', 'Switzerland', 'Netherlands', 'Sweden', 'United Kingdom', 'Austria', 'Ireland', 'Germany', 'Belgium', 'Luxembourg', 'France', 'Malta', 'Czech Republic', 'Poland', 'Slovakia', 'Estonia', 'Lithuania', 'Slovenia', 'Romania', 'Latvia', 'Italy', 'Portugal', 'Serbia', 'Greece', 'Cyprus', 'Northern Cyprus', 'Russia', 'Kazakhstan', 'Belarus', 'Moldova', 'Kosovo', 'Hungary', 'Ukraine', 'Albania', 'Montenegro', 'Croatia', 'Bosnia and Herzegovina', 'Georgia'],
        'North America': ['United States', 'Canada', 'Mexico', 'Costa Rica', 'Panama', 'Guatemala', 'Belize', 'Trinidad & Tobago', 'Jamaica', 'Haiti', 'Honduras', 'El Salvador', 'Nicaragua', 'Dominican Republic'],
        'South America': ['Brazil', 'Argentina', 'Chile', 'Uruguay', 'Colombia', 'Ecuador', 'Bolivia', 'Paraguay', 'Peru', 'Venezuela'],
        'Oceania': ['Australia', 'New Zealand'],
        'Middle East': ['Israel', 'United Arab Emirates', 'Qatar', 'Saudi Arabia', 'Bahrain', 'Kuwait', 'Turkey', 'Cyprus', 'Iran', 'Syria', 'Yemen', 'Palestine'],
    }

    def assign_continent(country):
        for continent, countries in continent_mapping.items():
            if country in countries:
                return continent
        return 'Other'

    df['Continent'] = df['Country or region'].apply(assign_continent)

    # creating checkboxes for selected continents
    selected_continents = request.form.getlist('continents') if request.method == 'POST' else list(df['Continent'].unique())
    filtered_df = df[df['Continent'].isin(selected_continents)]

    # creating sunburst charts
    sunburst_chart_html1 = px.sunburst(filtered_df, path=['Country or region'], values='Perceptions of corruption', title='Perceptions of Corruption by Country').to_html(full_html=False)
    sunburst_chart_html2 = px.sunburst(filtered_df, path=['Country or region'], values='Generosity', title='Generosity by Country').to_html(full_html=False)

    # calculating continent-based statistics (mean, median, mode, range)
    continent_stats = {}
    for continent in selected_continents:
        continent_df = df[df['Continent'] == continent]
        
        if not continent_df.empty:
            continent_stats[continent] = {
                column: {
                    'Mean': round(continent_df[column].mean(), 2) if not continent_df[column].isnull().all() else "N/A",
                    'Median': round(continent_df[column].median(), 2) if not continent_df[column].isnull().all() else "N/A",
                    'Mode': round(continent_df[column].mode()[0], 2) if not continent_df[column].mode().empty else "N/A",
                    'Range': round(continent_df[column].max() - continent_df[column].min(), 2) if not continent_df[column].isnull().all() else "N/A"
                }
                for column in ['Score', 'GDP per capita', 'Social support', 'Healthy life expectancy', 'Freedom to make life choices', 'Generosity', 'Perceptions of corruption']
                if column in df.columns
            }

    return render_template('statistics_page.html',
                           bar_chart1=bar_chart_html1, bar_chart2=bar_chart_html2,
                           line_chart1=line_chart_html1, line_chart2=line_chart_html2,
                           scatter_plot=scatter_plot_html, sunburst_chart1=sunburst_chart_html1,
                           sunburst_chart2=sunburst_chart_html2,
                           selected_continents=selected_continents,
                           continent_stats=continent_stats)

# creating user poll csv file
csv_file = "user_poll_data.csv"
if not os.path.isfile(csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(["Country", "Happiness Response", "Score"])

# creating user poll page
@app.route('/userpoll', methods=['GET', 'POST'])
def userpoll():
    all_countries = [country.name for country in pycountry.countries]
    if request.method == 'POST':
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow([request.form.get('Country'), request.form.get('happy'), request.form.get('Score')])
        return redirect(url_for('summary_page', message="Thank you for participating in the poll!"))
    return render_template('userpoll.html', all_countries=all_countries)

# creating summary page
@app.route('/summary')
def summary_page():
    if not os.path.isfile(csv_file):
        return render_template('summary.html', user_submissions=[], message=request.args.get('message', ''), pie_chart=None)
    user_df = pd.read_csv(csv_file)
    user_df['Score'] = pd.to_numeric(user_df['Score'], errors='coerce')
    pie_chart_html = None
    if not user_df.empty and user_df['Score'].notnull().any():
        pie_chart_html = px.pie(user_df, names='Country', values='Score', title="User Happiness Scores by Country").to_html(full_html=False)
    return render_template('summary.html', user_submissions=user_df.to_dict(orient='records'), message=request.args.get('message', ''), pie_chart=pie_chart_html)

# run flask application with given link
if __name__ == "__main__":
    app.run(debug=True, port=5050)



     





