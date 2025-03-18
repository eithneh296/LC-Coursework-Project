from flask import Flask, render_template

app = Flask(__name__)

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/meetingbrief')
def meetingbrief():
    return render_template('meetingbrief.html')

@app.route('/investigation')
def investigation():
    return render_template('investigation.html')

@app.route('/plandesign')
def plandesign():
    return render_template('plandesign.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)