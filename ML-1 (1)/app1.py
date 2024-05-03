from flask import Flask, request, render_template, redirect, session
import pickle
import numpy as np
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MySQL database connection configuration
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='abc123',
    database='ML'
)
db_cursor = db_connection.cursor(buffered=True)

# Load model
with open('model (5).pkl', 'rb') as file:
    model = pickle.load(file)

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')  # Redirect logged-in users to dashboard
    else:
        return render_template('index.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Remove the 'username' key from the session
    session.pop('username', None)
    # Redirect the user to the index page
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match in the database
        db_cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = db_cursor.fetchone()

        if user:
            session['username'] = username
            session['user_id'] = user[0]  # Store user_id in session
            return redirect('/dashboard')
        else:
            return 'Invalid username or password'

    # If it's a GET request, render the login page
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        db_cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        existing_user = db_cursor.fetchone()

        if existing_user:
            return 'Username or email already exists'
        else:
            # Insert new user into the database
            db_cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            db_connection.commit()
            session['username'] = username  # Store username in session
            return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
                # Get the user ID of the current user from the session
        user_id = session.get('user_id')

        # Fetch data from the database for the logged-in user
        db_cursor.execute('SELECT * FROM info WHERE user_id = %s', (user_id,))
        data = db_cursor.fetchall()
        
        return render_template('after_login.html', username=session['username'],data=data)
    else:
        return redirect('/login')

@app.route('/predict_page')
def predict_page():
    return render_template('index1.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract input data from form
        input1 = float(request.form['Time'])
        input2 = float(request.form['Amount'])
        input3 = float(request.form['Transaction_Type'])
        input4 = float(request.form['Origin_Account'])
        input5 = float(request.form['Destination_Account'])

        # Get the user ID of the current user from the session
        user_id = session.get('user_id')

        # Validate input data
        if any(np.isnan([input1, input2, input3, input4, input5, 0])):
            return render_template('index1.html', error="Invalid input. Please enter valid numbers.")

        features = np.array([[input1, input2, input3, input4, input5, 0]])
        
        # Make prediction using the correct model
        # prediction = model.predict(features)
        # prediction = 0
        print(prediction)

        # Map input3 to transaction type
        transaction_types = {1: 'CASH_IN', 2: 'TRANSFER', 3: 'CASH_OUT'}
        transaction_type = transaction_types.get(input3, 'UNKNOWN')
        
        

        result = 'NO suspicious' if prediction == 0 else 'suspicious'
        
        # Insert data into MySQL database
        sql = "INSERT INTO info (user_id, Time, Amount, Transaction_Type, Origin_Account, Destination_Account,result) VALUES (%s, %s, %s, %s, %s, %s,%s)"
        val = (user_id, input1, input2, transaction_type, input4, input5,result)
        db_cursor.execute(sql, val)
        db_connection.commit()

        return render_template('prediction_result.html')

    except Exception as e:
        return render_template('after_login.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
