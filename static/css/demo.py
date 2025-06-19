from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("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")

# Initialize OpenAI client
client = OpenAI.api_key=OPENAI_API_KEY

# AI response function
def ai_assistant_response(user_input):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use "gpt-4" or "gpt-3.5-turbo" if needed
            messages=[{"role": "user", "content": user_input}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Sorry, there was an error processing your request."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    response = ai_assistant_response(user_input)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
