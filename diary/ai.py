import openai

def generate_ai_suggestion(note_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты помощник."},
            {"role": "user", "content": note_text}
        ]
    )
    return response['choices'][0]['message']['content']
