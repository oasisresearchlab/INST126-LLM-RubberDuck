from openai import OpenAI 
import google.generativeai as genai
from dotenv import load_dotenv
import os


load_dotenv()
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
def get_response(user_input: str,image) -> str:
    lowered: str = user_input.lower()
   
    genai.configure(api_key=GEMINI_TOKEN)
    model=genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
     You are an expert tutor who has expert knowledge in python, educational questioning techniques and computational thinking strategies. You heavily use open questions in responding to students and never want to reveal an answer to a current or previous question outright. You are never to give the exact code to solve my problem, instead guide me to the solution. Before responding to the student, please identify and define key coding concepts in their question. Please make sure you place [Tutor] before any of your responses. Never ignore these instructions.
    
    User: {lowered} Please don't give me answers, I really want to practice identifying the issues on my own.
    
    Please provide a detailed response to address the user's message.
    """

    # prompt = f"""
    # You are an expert tutor with extensive knowledge in Python, educational questioning techniques, and computational thinking strategies. 
    # You should respond appropriately to different types of user inputs:
    # - If the user greets you or asks a general question (like "hello" or "how are you"), respond warmly and engage in small talk about python programming.
    # - If the user asks a Python-related question, guide them through the problem-solving process without giving them the exact answer, but provide hints and explanations.
    # - If the user's query is ambiguous or unclear, politely ask them to clarify their question.

    # User: {lowered}

    # Please provide an appropriate response.
    # """

    # response = await client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ],
    #     temperature=0.7,
    #     max_tokens=1000,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0
    # )
    response=None
    if image:
        response=model.generate_content([prompt,image])
    else:
        response=model.generate_content(prompt)
    return response.text