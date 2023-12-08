from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import re
import pickle
from models import db, Users

# Load the trained model and scaler from their pickle files
with open('static/ml_models/logistic_regression.pkl', 'rb') as file:
    model = pickle.load(file)

with open('static/ml_models/linear_regression.pkl', 'rb') as file:
    model = pickle.load(file)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ml-models-webapp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/ml-models'
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
        return render_template("dashboard.html")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
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
            prediction = model.predict([[Age, Hypertension, Heart_Disease, Glucose, BMI]])
            
            # For Checking the output
            # print(prediction)

            # Check if the prediction is 1 or 0
            if prediction[0] == 1:
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
            prediction = model.predict([[Age, SysBP, DiaBP, BMI, HeartRate, Glucose]])
            
            # Print output
            # print(prediction)

            return render_template('/predict/linear.html', prediction_text='The total cholesterol of the patient is {:.2f}'.format(prediction[0]))
        return redirect(url_for('linear'))

if __name__ == "__main__":
    app.run(debug=True)