import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask, render_template, request

# Initialize Flask app
app = Flask(__name__)

# Load CSV data (Check for issues)
try:
    df = pd.read_csv('2018-Happiness-Index-Cleaned.csv')
    print("CSV file loaded successfully!")
except FileNotFoundError:
    print("Error: CSV file not found! Make sure '2018-Happiness-Index-Cleaned.csv' exists.")
    df = None  # Prevent crashes if the file is missing

# Preprocess DataFrame
if df is not None:
    df.columns = df.columns.str.strip()  # Remove unwanted spaces
    df.rename(columns={'Country or Region': 'Country or region', 'Happiness Score': 'Score'}, inplace=True)

    # Ensure 'Score' is numeric
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce')

    # Handle missing values in 'Score'
    if df['Score'].isnull().sum() > 0:
        print("Warning: 'Score' column has missing values!")
        df['Score'].fillna(df['Score'].mean(), inplace=True)

@app.route('/')
def index():
    print("Home route function started!")

    if df is None:
        return "Error: Data file is missing!", 500

    print("Rendering Home Page...")
    return render_template('index.html')

@app.route('/statistics_page', methods=['GET','POST'])
def statistics_page():
    print("Statistics Page Requested")

    if df is None:
        return "Error: Data file is missing!", 500

    print("Processing statistics...")
    stats_archive = {}
    non_numeric_columns = ['Country or region']

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

    # Create Bar Chart using Plotly
    bar_fig = px.bar(df,  
                     x='Country or region',
                     y='Score',
                     title='Happiness Score by Country',
                     labels={'Score': 'Happiness Score', 'Country or region': 'Country'},
                     color='Score',
                     color_continuous_scale='viridis')

    # Adjust the layout for the bar chart
    bar_fig.update_layout(
        xaxis=dict(
            tickangle=35,  
            tickmode='array',
            tickvals=df['Country or region'],
            automargin=True  
        ),
        autosize=True,
        margin=dict(l=50, r=50, t=40, b=300),  
        height=600,  
        width=4000,  
        bargap=0.2
    )

    # Convert bar chart to HTML for embedding
    bar_chart_html = bar_fig.to_html(full_html=False)

    # Create Line Plot
    line_fig = px.line(df, x='Country or region', y='GDP per capita', title='GDP per capita by Country')

    # Adjust the layout for the line chart
    line_fig.update_layout(
        xaxis=dict(
            tickangle=35,  
            tickmode='array',
            tickvals=df['Country or region'],
            automargin=True  
        ),
        autosize=True,
        margin=dict(l=50, r=50, t=40, b=300),  
        height=600,  
        width=4000,  
        bargap=0.2
    )

    # Convert line chart to HTML for embedding
    line_chart_html = line_fig.to_html(full_html=False)

    continent_mapping = {
        'Africa': ['South Africa', 'Nigeria', 'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Ivory Coast', 'Ghana', 'Senegal', 'Somalia', 'Cameroon', 'Uganda', 'Benin', 'Niger', 'Sudan', 'Togo', 'Guinea', 'Lesotho', 'Angola', 'Madagascar', 'Zimbabwe', 'Botswana', 'Malawi', 'Namibia', 'Liberia', 'Mali', 'Mozambique', 'Kenya', 'Zambia', 'Mauritania', 'Ethiopia', 'Rwanda', 'Central African Republic', 'Burundi', 'Chad', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Sierra Leone', 'Mauritius'],
        'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Taiwan', 'Singapore', 'Malaysia', 'Thailand', 'Hong Kong', 'Azerbaijan', 'Turkmenistan', 'Kazakhstan', 'Uzbekistan', 'Kyrgyzstan', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal', 'Vietnam', 'Philippines', 'Myanmar', 'Cambodia', 'Laos', 'Iraq', 'Jordan', 'Lebanon', 'Armenia'],
        'Europe': ['Finland', 'Norway', 'Denmark', 'Iceland', 'Switzerland', 'Netherlands', 'Sweden', 'United Kingdom', 'Austria', 'Ireland', 'Germany', 'Belgium', 'Luxembourg', 'France', 'Malta', 'Czech Republic', 'Poland', 'Slovakia', 'Estonia', 'Lithuania', 'Slovenia', 'Romania', 'Latvia', 'Italy', 'Portugal', 'Serbia', 'Greece', 'Cyprus', 'Northern Cyprus', 'Russia', 'Kazakhstan', 'Belarus', 'Moldova', 'Kosovo', 'Hungary', 'Ukraine', 'Albania', 'Montenegro', 'Croatia', 'Bosnia and Herzegovina', 'Georgia'],
        'North America': ['United States', 'Canada', 'Mexico', 'Costa Rica', 'Panama', 'Guatemala', 'Belize', 'Trinidad & Tobago', 'Jamaica', 'Haiti', 'Honduras', 'El Salvador', 'Nicaragua', 'Dominican Republic'],
        'South America': ['Brazil', 'Argentina', 'Chile', 'Uruguay', 'Colombia', 'Ecuador', 'Bolivia', 'Paraguay', 'Peru', 'Venezuela'],
        'Oceania': ['Australia', 'New Zealand'],
        'Middle East': ['Israel', 'United Arab Emirates', 'Qatar', 'Saudi Arabia', 'Bahrain', 'Kuwait', 'Turkey', 'Cyprus', 'Iran', 'Syria', 'Yemen', 'Palestine'],
    }

    # Create a new 'Continent' column based on the country
    def assign_continent(country):
        for continent, countries in continent_mapping.items():
            if country in countries:
                return continent
        return 'Other'  # Default value if country isn't found in any mapping

    df['Continent'] = df['Country or region'].apply(assign_continent)

    # Get list of unique continents
    continents = df['Continent'].unique()

    # Handle form submission for selected continents
    if request.method == 'POST':  # Ensure we handle POST requests for the form
        selected_continents = request.form.getlist('continents') or list(df['Continent'].unique())  # Default to all continents
    else:
        selected_continents = list(df['Continent'].unique())  # Default to all continents on GET request
        
    # Filter DataFrame based on selected continents
    filtered_df = df[df['Continent'].isin(selected_continents)]

    # ✅ Sunburst Chart (Moved Inside Function)
    sunburst_fig = px.sunburst(filtered_df, 
                               path=['Country or region'],  
                               values='Perceptions of corruption', 
                               title='Perceptions of Corruption by Country',  
                               color_discrete_sequence=px.colors.qualitative.Set2)  

    # Adjust layout for better visibility
    sunburst_fig.update_layout(
        height=600,  
        width=900,
        margin=dict(l=100, r=100, t=100, b=100)  
    )

    # Convert sunburst chart to HTML for embedding
    sunburst_chart_html = sunburst_fig.to_html(full_html=False)

    # Ensure return statement is inside the function
    return render_template('statistics_page.html', 
                           stats=stats_archive, 
                           bar_chart=bar_chart_html, 
                           line_chart=line_chart_html, 
                           sunburst_chart=sunburst_chart_html)

@app.route('/user_poll')
def userpoll():
    return render_template('user_poll.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
     





