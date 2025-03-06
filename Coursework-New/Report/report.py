import pandas as pd
import numpy as np
import io
from flask import Flask, render_template, Response

# Define `app` BEFORE using `@app.route()`
app = Flask(__name__)

# Check if the dataset exists before reading
try:
    df = pd.read_csv('2018-Happiness-Index-Cleaned.csv')
except FileNotFoundError:
    print("CSV file not found! Make sure '2018-Happiness-Index-Cleaned.csv' exists.")
    df = None  # Prevent crashes if the file is missing

@app.route('/')
def index():
    print("Home route function started!")

    return render_template('index.html')

@app.route('/plan_design')
def plan_design():
    print("work it")

    return render_template('user_poll')

@app.route('/meeting_brief')
def meeting_brief():
    print("work it")

    return render_template('user_poll')

# Run Flask only when the script is executed directly
if __name__ == "__main__":
    app.run(debug=True, port=5000)