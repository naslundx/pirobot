import base64
import os
from openai import OpenAI


class AIConnection:
    def __init__(self):
        # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI()

    def get_response(self, user_input):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": user_input}
            ],
        )

        return response.choices[0].message.content

    def interpret_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What is in this image?"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"} }
                        ]
                    }
                ]
            )

        return response.choices[0].message.content
