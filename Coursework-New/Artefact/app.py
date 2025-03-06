import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import io
from flask import Flask, render_template, Response

# Define app BEFORE using @app.route()
app = Flask(__name__)

# Check if the dataset exists before reading
try:
    df = pd.read_csv('2018-Happiness-Index-Cleaned.csv')
except FileNotFoundError:
    print("CSV file not found! Make sure '2018-Happiness-Index-Cleaned.csv' exists.")
    df = None  # Prevent crashes if the file is missing

# Route to render a bar chart
@app.route('/barchart')
def barchart():
    if df is None:
        return "Error: Data file is missing!", 500

    # Create Bar Chart using Plotly Express
    fig = px.bar(df.head(10),  # Show top 10 countries
                 x='Country or region',
                 y='Score',
                 title='Happiness Score by Country',
                 labels={'Score': 'Happiness Score', 'Country or region': 'Country'},
                 color='Score',  # Color based on Score
                 color_continuous_scale='viridis')
    
    # Convert to HTML and embed in Flask template
    chart_html = fig.to_html(full_html=False)

    return render_template('barchart.html', chart=chart_html)


@app.route('/')
def index():
    print("Home route function started!")

    # If data file is missing, return an error page
    if df is None:
        print("Dataframe is None!")
        return "Error: Data file is missing!", 500

    print("Processing statistics")
    stats_archive = {}

    # Define non_numeric_columns within the function
    non_numeric_columns = ['Country or region']

    # Process numeric columns
    for col in df.columns:
        if col not in non_numeric_columns:
            stats_data = pd.to_numeric(df[col], errors='coerce')

            if stats_data.notna().any():
                stats_archive[col] = {
                    'Mean': stats_data.mean(),
                    'Median': stats_data.median(),
                    'Mode': stats_data.mode().iloc[0] if not stats_data.mode().empty else np.nan,
                    'Range': stats_data.max() - stats_data.min()
                }

    print("Finished processing. Rendering template...")

    return render_template('index.html', stats=stats_archive)

@app.route('/statistics_page')
def statistics_page():
    print("work it")

    # If data file is missing, return an error page
    if df is None:
        print("Dataframe is None!")
        return "Error: Data file is missing!", 500

    print("Processing statistics")
    stats_archive = {}

    # Define non_numeric_columns within the function
    non_numeric_columns = ['Country or region']

    # Process numeric columns
    for col in df.columns:
        if col not in non_numeric_columns:
            stats_data = pd.to_numeric(df[col], errors='coerce')

            if stats_data.notna().any():
                stats_archive[col] = {
                    'Mean': stats_data.mean(),
                    'Median': stats_data.median(),
                    'Mode': stats_data.mode().iloc[0] if not stats_data.mode().empty else np.nan,
                    'Range': stats_data.max() - stats_data.min()
                }

    return render_template('statistics_page.html', stats=stats_archive)

@app.route('/user_poll')
def userpoll():
    print("work it")

    return render_template('user_poll.html')  # Corrected here

# Run Flask only when the script is executed directly
if __name__ == "__main__":
    app.run(debug=True, port=5000)
