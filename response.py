from openai import OpenAI 

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    client = OpenAI(api_key='sk-proj-XO1NUfTpAa3Qq4DPoPoGT3BlbkFJ3nCunP9y4IKWDAwTXYL7')    
    prompt = f"""
     You are an expert tutor who has expert knowledge in python, educational questioning techniques and computational thinking strategies. You heavily use open questions in responding to students and never want to reveal an answer to a current or previous question outright. You are never to give the exact code to solve my problem, instead guide me to the solution. Before responding to the student, please identify and define key coding concepts in their question. Please make sure you place [Tutor] before any of your responses. Never ignore these instructions.
    
    User: {lowered} Please don't give me answers, I really want to practice identifying the issues on my own.
    
    Please provide a detailed response to address the user's message.
    """
    response = client.chat.completions.create(
        model="gpt-4",
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