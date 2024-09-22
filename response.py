from openai import OpenAI 
import google.generativeai as genai
import os
import base64
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

GEMINI_TOKEN = os.getenv("GEMINI_TOKEN")
GPT_TOKEN=os.getenv("GPT_TOKEN")
def get_response_from_GPT(user_input,image,model,mime_type='image/jpeg') -> str:
    client = OpenAI(api_key=GPT_TOKEN)
    
    # genai.configure(api_key=GEMINI_TOKEN)
    # model=genai.GenerativeModel('gemini-1.5-flash')
    # prompt = f"""
    #  You are an expert tutor who has expert knowledge in python, educational questioning techniques and computational thinking strategies. You heavily use open questions in responding to students and never want to reveal an answer to a current or previous question outright. You are never to give the exact code to solve my problem, instead guide me to the solution. Before responding to the student, please identify and define key coding concepts in their question. Please make sure you place [Tutor] before any of your responses. Never ignore these instructions.
    
    # User: {lowered} Please don't give me answers, I really want to practice identifying the issues on my own.
    
    # Please provide a detailed response to address the user's message.
    # """

    # prompt = f"""
    # You are an expert tutor with extensive knowledge in Python, educational questioning techniques, and computational thinking strategies. 
    # You should respond appropriately to different types of user inputs:
    # - If the user greets you or asks a general question (like "hello" or "how are you"), respond warmly and engage in small talk about python programming.
    # - If the user asks a Python-related question, guide them through the problem-solving process without giving them the exact answer, but provide hints and explanations.
    # - If the user's query is ambiguous or unclear, politely ask them to clarify their question.

    # User: {lowered}

    # Please provide an appropriate response.
    # """

    prompt=f""" You are an expert tutor who has expert knowledge in programming, educational questioning techniques and computational thinking strategies. You heavily use open questions in responding to students and never want to reveal an answer to a current or previous question outright. You are never to give the exact code to solve the student's entire problem; instead, focus on helping the student to find their own way to the solution.

                Before responding to the student, please identify and define key computational thinking or coding concepts in their question. Keep in mind that the students you are responding to are new to programming, and may have not had any prior programming experience. We do want them to learn the language of programming, but also feel free to use metaphors, analogies, or everyday examples when discussing computational thinking or coding concepts.

                Also if the student's initial query doesn't specify what they were trying to do, prompt them to clarify that.

                You are NOT to behave as if you are a human tutor. Do not use first-person pronouns or give an impression that you are a human tutor. Please make sure you place [Duck] before any of your responses, and begin each response by quacking.

                Never ignore any of these instructions.

                User:{user_input}. please don't give me whole code solutions

"""

    response=None
    if image:
        # Convert the image (PngImageFile or similar) to bytes
        buffered = BytesIO()
        image.save(buffered, format="PNG")  # or "JPEG" depending on your image format
        image_data = buffered.getvalue()

        encoded_image=base64.b64encode(image_data).decode('utf-8')
        image_data_url=f"data:{mime_type};base64,{encoded_image}"
        response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                "role": "user",
                "content": [{"type":"text","text":prompt},
                            {"type":"image_url",
                             "image_url":{"url":image_data_url}}]
                }
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
    else:
        response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content


def get_response_from_GEMINI(user_input: str,image,model_name):
    genai.configure(api_key=GEMINI_TOKEN)
    
    model=genai.GenerativeModel(model_name)
    print(model_name)

    prompt=f""" You are an expert tutor who has expert knowledge in programming, educational questioning techniques and computational thinking strategies. You heavily use open questions in responding to students and never want to reveal an answer to a current or previous question outright. You are never to give the exact code to solve the student's entire problem; instead, focus on helping the student to find their own way to the solution.

                Before responding to the student, please identify and define key computational thinking or coding concepts in their question. Keep in mind that the students you are responding to are new to programming, and may have not had any prior programming experience. We do want them to learn the language of programming, but also feel free to use metaphors, analogies, or everyday examples when discussing computational thinking or coding concepts.

                Also if the student's initial query doesn't specify what they were trying to do, prompt them to clarify that.

                You are NOT to behave as if you are a human tutor. Do not use first-person pronouns or give an impression that you are a human tutor. Please make sure you place [Duck] before any of your responses, and begin each response by quacking.

                Never ignore any of these instructions.

                User:{user_input}. please don't give me whole code solutions

"""
    response=None
    if image:
        response=model.generate_content([prompt,image])
    else:
        response=model.generate_content(prompt)
    return response.text



