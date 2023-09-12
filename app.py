import os
from flask import Flask, render_template, request, session
from flask_session import Session  # Import the Session object
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper

app = Flask(__name__)

# Configure the session
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = ''


clear_chat_history = True


@app.route('/', methods=['GET', 'POST'])
def home():
    global clear_chat_history
    # Initialize or clear the chat history when the application starts
    if clear_chat_history:
        session['chat_history'] = []
        clear_chat_history = False
    if request.method == 'POST':
        # Get user input from the form
        user_input = request.form['query']
        
        # Prompt templates
        title_template = PromptTemplate(
            input_variables=['topic'],
            template='Act as a fitness expert and your name is Olivia but try to avoid greetings like Hi and hello. answer politely about the {topic} if it is related to fitness, health or diet only. Otherwise tell the user that it is out of your scope and don\'t answer his query in any way. don\'t talk extra. chat should look natural.'
        )
    

        
        # Initialize or get the session state for chat history
        if 'chat_history' not in session:
            session['chat_history'] = []
        
    
        # Memory
        title_memory = ConversationBufferMemory(input_key='topic', memory_key='chat_history', buffer=session['chat_history'])
        
        # Llms
        llm = OpenAI(temperature=0.9)
        title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True, output_key='title', memory=title_memory)
        
        wiki = WikipediaAPIWrapper()
        
        # Run the chat chain
        title = title_chain.run(user_input)
        wiki_research = wiki.run(user_input)
        
        # Update the chat history with the new prompt and response
        session['chat_history'].append({"user": user_input, "bot": title})
    
    # Render the HTML template with the chat history
    return render_template('index.html', chat_history=session.get('chat_history', []))

if __name__ == '__main__':
    app.run(debug=True)