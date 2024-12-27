import os
import json
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_personas(theme):
    prompt = f"""
    Create two contrasting personas for a dialogue about the theme: "{theme}".
    Focus on creating characters that can have an interesting discussion about this topic.
    Return a JSON object with the following structure:
    {{
        "persona_a": {{
            "name": "character name (can be in Japanese)",
            "description": "detailed character description including personality and viewpoint (can be in Japanese)",
            "icon": "icon name from Font Awesome (fa-*)"
        }},
        "persona_b": {{
            "name": "character name (can be in Japanese)",
            "description": "detailed character description including personality and viewpoint (can be in Japanese)",
            "icon": "icon name from Font Awesome (fa-*)"
        }}
    }}
    Ensure the response is valid JSON with proper escaping for any special characters.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Failed to generate personas: {str(e)}")

def generate_dialogue(previous_messages, current_speaker):
    context = "\n".join([
        f"{msg['speaker']}: {msg['content']}" 
        for msg in previous_messages[-5:]  # Only use last 5 messages for context
    ])

    prompt = f"""
    Given the following conversation context:
    {context}

    Generate the next message from {current_speaker}'s perspective.
    The response should be natural, in character, and continue the dialogue naturally.
    You can respond in Japanese if the context is in Japanese.
    Only return the message content, no additional formatting.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Failed to generate dialogue: {str(e)}")