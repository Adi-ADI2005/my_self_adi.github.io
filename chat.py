from PyPDF2 import PdfReader   # use to read pdf file 
import difflib #used for comparing sequences
import openai  #to connect with the OpenAI platform

#API key to connect with openAI
openai.api_key = "YOUR_OPENAI_API_KEY"

# basic message 
responses = {
  "hii": "Hey there! Today I am your assistant, how can I help you?",
  "hello": "Hey there! 🌱",
  "how are you": "I am fine 😊😊",
  "what is your name": "My name is AgroAi, your farming assistant! 🤖",
  "developed by": "I was developed by AagroTech 🤖! 🚀",
  "thank you": "Most welcome ✌️✌️"
}



#Load all the text from a PDF file.
def load_pdf_text(filepath):
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print("PDF load error:", e)
    return text



# use to Break the loaded text into (Question, Answer) pairs.
def extract_qa_pairs(text):
    lines = text.split('\n')
    qa_pairs = []
    q, a = None, None
    for line in lines:
        line = line.strip()
        if line.endswith('?'):
            if q and a:
                qa_pairs.append((q, a))
            q = line
            a = ""
        elif line:
            if a is not None:
                a += " " + line
    if q and a:
        qa_pairs.append((q, a))
    return qa_pairs

pdf_content = load_pdf_text("Chat.pdf") # use to load pdf file
qa_list = extract_qa_pairs(pdf_content) # It holds the list of all Question-Answer pairs extracted from the PDF.



#When the user asks a question, find the closest matching question from the PDF list.
def find_best_answer(user_question):
    questions = [q for q, a in qa_list]
    match = difflib.get_close_matches(user_question, questions, n=1, cutoff=0.4)
    if match:
        for q, a in qa_list:
            if q == match[0]:
                return a
    return None



#If no good answer is found in the PDF, send the question to OpenAI GPT
def chat_with_gpt(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert agriculture assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "Sorry, an error occurred while contacting the AI."
