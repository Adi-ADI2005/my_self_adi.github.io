from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient #import function for MongoDB connector 
from soil import predict_crop  # Import the predict_crop function form soil.py
from datetime import datetime  # used to check the current data and time
from d_weather import dw_home   #import function dw_weather, to get daily weather update 
from w_weather import home as ww_home #import function ww_weather, to get weakely weather update 
from chat import find_best_answer, chat_with_gpt, responses #import these function from chat.py 


app = Flask(__name__) # Create a Flask app instance
app.secret_key = 'a658914e47696c55b51090d5d0e395798559fa0d181fff9fe8be5281cb21718d'

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/') #connection link of mongodb
    db = client['FarmTech']  # Client/Database name
    collection = db['users']  # Collection/table name
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)


#                                 ==================== USER AUTHENTICATION ====================



#                                  ==================== for registration ====================

@app.route('/')
def home():
    return render_template('reg.html')  # Return the registration form

#registration proces
@app.route('/register', methods=['POST'])
def register():
    # Get data form regstation from
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    password = request.form.get('password')
    mob = request.form.get('mob')

    if not all([fname, lname, password, mob]):
        flash("All fields are required.")
        return redirect(url_for('home'))

    # check the length of mobile_number is 10 or not
    if len(mob) != 10 or not mob.isdigit():
        flash("Mobile number must be exactly 10 digits.")
        return redirect(url_for('home'))

    # Check if the mobile_number already exists or not
    existing_user = collection.find_one({"mobile": mob})
    if existing_user:
        flash("Username already exists. Please go to login !!!")
        return redirect(url_for('home'))

    # Create a dictionary to store data
    user_data = {
        "Firstname": fname,
        "Lastname": lname,
        "password": password,
        "mobile": mob
    }

    # Insert data into MongoDB
    collection.insert_one(user_data)
    flash("Registration successful! Please log in.")
    return redirect(url_for('user_login'))        #return login form



#                                          ==================== for login ====================



@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        # Get data from login page
        mob = request.form.get('mob')
        password = request.form.get('password')

        # check the length of mobile_number is 10 or not
        if not mob or len(mob) != 10 or not mob.isdigit():
            flash("Mobile number must be exactly 10 digits.", "danger")
            return redirect(url_for('user_login'))

        # Check if the user exists in the database or not
        user = collection.find_one({"mobile": mob})

        if user:
            # If user exists, check password
            if user.get('password') == password:
                session['mobile'] = mob
                session['firstname'] = user.get('Firstname', '')  
                flash("Login successful! Access granted.", "success")
                return redirect(url_for('home_page'))  # Return to homepage
            else:
                flash("Incorrect password. Please try again.", "danger")
        else:
            flash("User does not exist. Please register.", "warning")

        return redirect(url_for('user_login'))

    return render_template('login.html')  # Return login page for GET requests

    return render_template('login.html') 



#                                      ==================== HOME & DASHBOARD ====================



#home page
@app.route('/home') 
def home_page():   # return the home_poage after successful login
    if 'firstname' in session:
        firstname = session['firstname']  
        return render_template('home.html', firstname=firstname) #show first_name in home_page
    return redirect(url_for('user_login'))

#log out
@app.route('/logout')
def logout(): 
    firstname = session.get('firstname', 'User')                            
    session.pop('username', None)
    session.pop('firstname', None) 
    flash(f"{firstname} ,has been logged out !!!")
    return redirect(url_for('user_login'))#After successfuly logout  return login page



#                                         ==================== CROP PREDICTION ====================



#for soil analysis 
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Collect data from soil.html form 
            data = request.form
            N = float(data.get('Nitrogen', 0))
            P = float(data.get('Phosporus', 0))
            K = float(data.get('Potassium', 0))
            temperature = float(data.get('Tempe', 0))
            humidity = float(data.get('Humidity', 0))
            ph = float(data.get('Ph', 0))
            rainfall = float(data.get('Rainfall', 0))

            # Call the prediction function in soil.py
            result = predict_crop(N, P, K, temperature, humidity, ph, rainfall)

             #print the prediction result 
            flash(f'Recommended Crop: {result}', 'success')
            return redirect(url_for('result'))  #print the result in result.html
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    # Return back to the soil form
    return redirect(url_for('soil'))
#soil  page
@app.route('/soil')
def soil():
    return render_template('soil.html') #return soil analysis form
@app.route('/result')
def result():
    return render_template('result.html')#return result of predected  crop



#                                        ==================== WEATHER MODULE ====================



@app.route("/weather", methods=["GET", "POST"])
def weather():
    return ww_home()     # to get weakely weather data

@app.route("/hourly", methods=["GET", "POST"])
def weather_hourly():
    return dw_home()       # to get weakely weather data



    
#                                 ==================== Agro AI PAGES ====================




@app.route('/chat')
def chat_page():
    return render_template('chat.html') # return the chat.html page

#take the user's query from chat.html page
@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.form.get('message').strip()

    for question, answer in responses.items():
        if question in user_message.lower():
            return answer

    pdf_answer = find_best_answer(user_message)
    if pdf_answer:
        return pdf_answer

    return chat_with_gpt(user_message)





if __name__ == '__main__':       # Ensures this runs only when executed directly
    app.run(debug=True)          # Starts the Flask development server
