from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import re
import pickle
from models import db, Users, Stroke, Cholesterol

# Load the trained model from their pickle files
with open('static/ml_models/logistic_regression.pkl', 'rb') as file:
    lo_model = pickle.load(file)

with open('static/ml_models/linear_regression.pkl', 'rb') as file:
    li_model = pickle.load(file)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ml-models-webapp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/ml_models'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt(app) 
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("login.html")

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']
         
        user_exists = Users.query.filter_by(email=email).first() is not None
       
        if user_exists:
            mesage = 'Email already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not fullname or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = Users(name=fullname, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)

@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        #print(email)
        #print(password)
        if email == '' or password == '':
            mesage = 'Please enter email and password !'
        else:
            user = Users.query.filter_by(email=email).first()
            print(user)
 
            if user is None:
                mesage = 'Please enter correct email / password !'
            else:
                if not bcrypt.check_password_hash(user.password, password):
                    mesage = 'Please enter correct email and password !'
                else:    
                    session['loggedin'] = True
                    session['userid'] = user.id
                    session['name'] = user.name
                    session['email'] = user.email
                    mesage = 'Logged in successfully !'           
                    return redirect(url_for('dashboard'))
 
    return render_template('login.html', mesage = mesage)

@app.route("/dashboard", methods =['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        # Fetch all rows from the DB table
        strokes = Stroke.query.all()
        cholesterols = Cholesterol.query.all()

        return render_template("dashboard.html", name=session['name'], strokes=strokes, cholesterols=cholesterols)
    return redirect(url_for('login'))

# Prediction functions and routes
@app.route("/logistic", methods =['GET', 'POST'])
def logistic():
    if 'loggedin' in session:        
        return render_template("/predict/logistic.html")
    return redirect(url_for('login'))   

@app.route("/logistic_predict", methods =['GET', 'POST'])
def logistic_predict():
    if 'loggedin' in session:
        if request.method == 'POST':
            # Get the data from the POST request.
            Age = int(request.form['age'])
            Hypertension = int(request.form['hypertension'])
            Heart_Disease = int(request.form['heartdisease'])           
            Glucose = float(request.form['glucose'])
            BMI = float(request.form['bmi'])

            # Store the inputs to the model then predict
            lo_prediction = lo_model.predict([[Age, Hypertension, Heart_Disease, Glucose, BMI]])
            
            # Create a new instance of Stroke for db storing
            stroke_data_entry = Stroke(age=Age, hypertension=Hypertension, heart_disease=Heart_Disease, glucose=Glucose, bmi=BMI, stroke=lo_prediction[0])

            # Add the new entry to the database
            db.session.add(stroke_data_entry)
            db.session.commit()

            # Check if the prediction is 1 or 0
            if lo_prediction[0] == 1:
                return render_template('/predict/logistic.html', prediction_text='The patient will likely to have stroke 😟')
            else:
                return render_template('/predict/logistic.html', prediction_text='The patient will not likely to have stroke 😃')
        return redirect(url_for('logistic'))
    
@app.route("/linear", methods =['GET', 'POST'])
def linear():
    if 'loggedin' in session:        
        return render_template("/predict/linear.html")
    return redirect(url_for('login'))   

@app.route("/linear_predict", methods =['GET', 'POST'])
def linear_predict():
    if 'loggedin' in session:
        if request.method == 'POST':
            # Get the data from the POST request.
            Age = int(request.form['age'])
            SysBP = float(request.form['sysBP'])
            DiaBP = float(request.form['diaBP'])
            BMI = float(request.form['bmi'])
            HeartRate = int(request.form['heartRate'])
            Glucose = float(request.form['glucose'])

            # Store the inputs to the model then predict
            li_prediction = li_model.predict([[Age, SysBP, DiaBP, BMI, HeartRate, Glucose]])
            
            # Create a new instance of Cholesterol for db storing
            cholesterol_data_entry = Cholesterol(age=Age, sys_bp=SysBP, dia_bp=DiaBP, bmi=BMI, heart_rate=HeartRate, glucose=Glucose, tot_chol=li_prediction[0])

            # Add the new entry to the database
            db.session.add(cholesterol_data_entry)
            db.session.commit()

            return render_template('/predict/linear.html', prediction_text='The total cholesterol of the patient is {:.2f}'.format(li_prediction[0]))
        return redirect(url_for('linear'))

# Visualization
@app.route("/visualize", methods =['GET', 'POST'])
def visualize():
    if 'loggedin' in session:
        # Fetch all data from the stroke and cholesterol tables
        stroke_data = Stroke.query.all()
        cholesterol_data_db = Cholesterol.query.all()

        # Process the data into the format needed for the bar chart
        age_bins = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100"]
        strokeCounts = [0]*10
        noStrokeCounts = [0]*10
        for item in stroke_data:
            # Determine which age bin this item belongs to
            bin_index = min(item.age // 10, 9)  # Ensure that ages 100 and above fall into the last bin
            if item.stroke == 1:
                strokeCounts[bin_index] += 1
            else:
                noStrokeCounts[bin_index] += 1

        # Process the data into the format needed for the line chart
        glucose_data = [[] for _ in range(10)]
        cholesterol_data = [[] for _ in range(10)]
        for item in cholesterol_data_db:
            if not isinstance(item, list):
                # Determine which age bin this item belongs to
                bin_index = min(item.age // 10, 9)  # Ensure that ages 100 and above fall into the last bin
                glucose_data[bin_index].append(item.glucose)
                cholesterol_data[bin_index].append(item.tot_chol)

        # Calculate the average glucose and cholesterol levels for each age bin
        glucose_data = [sum(g) / len(g) if g else 0 for g in glucose_data]
        cholesterol_data = [sum(c) / len(c) if c else 0 for c in cholesterol_data]

        # Pass the data to the template
        return render_template("visualize.html", ages=age_bins, strokeCounts=strokeCounts, noStrokeCounts=noStrokeCounts, glucose_data=glucose_data, cholesterol_data=cholesterol_data)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)