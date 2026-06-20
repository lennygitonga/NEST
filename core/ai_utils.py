from groq import Groq
import os


def get_groq_client():
    return Groq(api_key=os.getenv('GROQ_API_KEY'))


def ask_groq(prompt, system_prompt="You are a helpful assistant.", model="llama-3.3-70b-versatile"):
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI service unavailable: {str(e)}"