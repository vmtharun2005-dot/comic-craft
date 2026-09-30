import os

from google import genai

api_key = os.getenv("GEMINI_API_KEY")

STORY_PROMPT = """
Expand this comic outline into narration:
Outline: {outline}

Character: {character_name}, Setting: {setting}, Tone: {tone}

For each panel, write:
Caption: (ambient description)
Narration: (what character does/says, engaging dialogue)

Return panel by panel in format:
PANEL 1:
Caption:...
Narration:...

... up to PANEL 5. Keep story cohesive and {tone}.
"""


def generate_story(outline, character_name, setting, tone):
    try:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        client = genai.Client(api_key=api_key)
        prompt = STORY_PROMPT.format(
            outline=str(outline),
            character_name=character_name,
            setting=setting,
            tone=tone,
        )
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=prompt,
        )
        story = getattr(response, "text", "")
        if story:
            return story
        raise ValueError("Empty story response")
    except Exception as e:
        print(f"Pro Error: {e}")
        story = ""
        for p in outline:
            story += (
                f"PANEL {p.get('panel', 1)}:\n"
                f"Caption: {p.get('scene_description', '')}\n"
                f"Narration: {character_name} says 'What an adventure in {setting}!'.\n\n"
            )
        return story