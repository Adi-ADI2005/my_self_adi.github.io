from flask import Flask, request, jsonify, render_template# uset to handel tmplates of html
import pandas as pd # pandas is mainly used to manipulate (handle, change, process) datasets easily
#It helps avoid overfitting  and checks if the model can generalize to new data.
from sklearn.model_selection import train_test_split  # used to train and test the data set 
from sklearn.preprocessing import StandardScaler# it reshapes  data to a standard form so that all features have the same scale.
from sklearn.ensemble import RandomForestClassifier #it is a Machine Learning algorithm used for classification tasks.
# it is used to evaluate the performance of a classification model. It tells you how often your model correctly predicts the labels.
from sklearn.metrics import accuracy_score 

# Load the dataset
data = pd.read_csv('crop_data.csv')

# Features and target
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['label']

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train  the mode using  Random Forest Classifier algorithm
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy * 100:.2f}%")# print the accuracy in % 

# Function to make predictions
def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    input_data = scaler.transform([[N, P, K, temperature, humidity, ph, rainfall]])
    prediction = model.predict(input_data)
    return prediction[0]

