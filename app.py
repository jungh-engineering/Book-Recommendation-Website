"""
pip install langchain-core langchain-openai pydantic flask dotenv
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- LangChain Setup (From your script) ---

# Standardize environment setup
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://eu.api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "agent-book"

class Recomm(BaseModel):
    title: list[str] = Field(description="title of the book")
    author: list[str] = Field(description="author of the book")
    # I added 'genre' to help the UI look a bit more populated, 
    # but strictly kept your logic as the core.
    genre: list[str] = Field(description="genre of the book") 

def get_recommendations(user_input):
    try:
        parser = PydanticOutputParser(pydantic_object=Recomm)
        format_instructions = parser.get_format_instructions()

        prompt = ChatPromptTemplate(
            [
                ("system", "You are a book recommendation system. Given the user's prompt, output a list of book recommendations. The recommendation list should be at least 5 books long. Follow the format instructions below: {format_instructions}. OUTPUT THE JSON ONLY, DO NOT EXPLAIN YOUR BOOK RECOMMENDATIONS OR WRITE INTRODUCTORY SENTENCES BEFORE YOUR JSON."),
                ("human", "{user_input}")
            ]
        )

        prompt_with_format_instructions = prompt.partial(format_instructions=format_instructions)
        prompt_value = prompt_with_format_instructions.invoke({"user_input": user_input})

        # Using OpenRouter/Llama as per your script
        model = ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="meta-llama/llama-3.2-3b-instruct", 
            openai_api_key=os.getenv("OPENROUTER_API_KEY")
        )

        ai_message = model.invoke(prompt_value)
        recomm = parser.invoke(ai_message)
        
        # Transform the 'List of Lists' structure into a 'List of Objects' for easier Frontend parsing
        # e.g. from {titles: [A, B], authors: [X, Y]} to [{title: A, author: X}, ...]
        books = []
        for i in range(len(recomm.title)):
            books.append({
                "title": recomm.title[i],
                "author": recomm.author[i] if i < len(recomm.author) else "Unknown",
                "genre": recomm.genre[i] if i < len(recomm.genre) else "General"
            })
            
        return books
        
    except Exception as e:
        print(f"Error: {e}")
        return []

# --- Flask Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_prompt = data.get('prompt', '')
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    recommendations = get_recommendations(user_prompt)
    return jsonify(recommendations)

if __name__ == '__main__':
    # host='0.0.0.0' allows access from outside the VM
    app.run(debug=True, host='0.0.0.0', port=5000)