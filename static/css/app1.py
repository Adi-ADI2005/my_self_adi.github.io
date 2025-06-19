from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from soil import predict_crop  # Import the crop prediction function
from d_weather import dw_home
from w_weather import home as ww_home  

app = Flask(__name__)
app.secret_key = 'a658914e47696c55b51090d5d0e395798559fa0d181fff9fe8be5281cb21718d'

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['FarmTech']
    collection = db['users']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# ==================== USER AUTHENTICATION ====================

@app.route('/')
def home():
    return render_template('reg.html')

@app.route('/register', methods=['POST'])
def register():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    password = request.form.get('password')
    mob = request.form.get('mob')

    if not all([fname, lname, password, mob]):
        flash("All fields are required.")
        return redirect(url_for('home'))

    if len(mob) != 10 or not mob.isdigit():
        flash("Mobile number must be exactly 10 digits.")
        return redirect(url_for('home'))

    existing_user = collection.find_one({"mobile": mob})
    if existing_user:
        flash("User already exists. Please login.")
        return redirect(url_for('home'))

    collection.insert_one({
        "Firstname": fname,
        "Lastname": lname,
        "password": password,
        "mobile": mob
    })

    flash("Registration successful! Please log in.")
    return redirect(url_for('user_login'))

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        mob = request.form.get('mob')
        password = request.form.get('password')

        if not mob or len(mob) != 10 or not mob.isdigit():
            flash("Mobile number must be exactly 10 digits.", "danger")
            return redirect(url_for('user_login'))

        user = collection.find_one({"mobile": mob})

        if user and user.get('password') == password:
            session['mobile'] = mob
            session['firstname'] = user.get('Firstname', '')  
            flash("Login successful!", "success")
            return redirect(url_for('home_page'))
        else:
            flash("Invalid credentials.", "danger")

        return redirect(url_for('user_login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    firstname = session.get('firstname', 'User')                            
    session.pop('mobile', None)
    session.pop('firstname', None) 
    flash(f"{firstname}, you have been logged out!")
    return redirect(url_for('user_login'))

# ==================== HOME & DASHBOARD ====================

@app.route('/home') 
def home_page():
    if 'firstname' in session:
        firstname = session['firstname']  
        return render_template('home.html', firstname=firstname)
    return redirect(url_for('user_login'))

# ==================== CROP PREDICTION ====================

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            data = request.form
            N = float(data.get('Nitrogen', 0))
            P = float(data.get('Phosporus', 0))
            K = float(data.get('Potassium', 0))
            temperature = float(data.get('Tempe', 0))
            humidity = float(data.get('Humidity', 0))
            ph = float(data.get('Ph', 0))
            rainfall = float(data.get('Rainfall', 0))

            result = predict_crop(N, P, K, temperature, humidity, ph, rainfall)

            flash(f'Recommended Crop: {result}', 'success')
            return redirect(url_for('result'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('soil'))

@app.route('/soil')
def soil():
    return render_template('soil.html')

@app.route('/result')
def result():
    return render_template('result.html')

# ==================== WEATHER MODULE ====================

@app.route("/weather", methods=["GET", "POST"])
def weather():
    return ww_home()

@app.route("/hourly", methods=["GET", "POST"])
def weather_hourly():
    return dw_home()

# ==================== OTHER PAGES ====================

@app.route('/suggestion')
def suggestion():
    return render_template('suggestion.html')

@app.route('/shop')
def buy():
    return render_template('buy.html')

if __name__ == '__main__':
    app.run(debug=True)
