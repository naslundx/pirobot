import json
from openai import OpenAI


TOWARDS_GOAL_PROMPT = """
You are on a robot with wheels. You will receive a target goal, memory, and an image from the front camera and return a JSON with a description, a memory, and a list of commands. Possible commands are forward, reverse, turn_left, turn_right and done.

Example:
Input: The goal is "Move to the next room." and the image shows an opening to another room.
Output: A JSON with the following content: {{ "description": "Opening to the other room far ahead. Nothing else intersting in the room.", "memory": "No openings found to the left or to the right. Stop after the room has been entered.", "commands": ["forward", "forward", "forward"] }}

Input: The goal is "Locate the clown" and the image shows a clown.
Output: A JSON with the following content: {{ "description": "A large clown covers most of the image. Goal has been reached.", "memory": "Clown was not located in the room that's behind.", "commands": ["done"] }}

Input: The goal is "Turn right 90 degrees".
Output: A JSON with the following content: {{ "description": "Image description", "memory": "Same memory as before", "commands": ["turn_right", "turn_right"] }}

Possible commands:
forward, reverse: Moves forward or backward for 2 seconds and then stops.
turn_left, turn_right: Turns 45 degrees to the left or to the right.
done: Indicates that the goal has been reached.

You will be prompted with a new image and the returned memory when all commands in the list have been exhausted.

Current goal: {goal}
Current memory: {memory}

Return a JSON with description, a memory, and a list of commands.
"""


class AIConnection:
    def __init__(self):
        self.client = OpenAI()
        self.is_autonomous = False
        self.busy = False

        self._goal = ""
        self._memory = "Just started."
        self._latest_description = "N/A"
        self._commands = []

    @property
    def status(self):
        return self._latest_description

    def get_next_command(self):
        if self._commands:
            return self._commands.pop(0)

        return None

    def set_goal(self, goal):
        self._goal = goal

    def set_memory(self, memory):
        self._memory = memory

    def get_response(self, user_input):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": user_input}
            ],
        )

        return response.choices[0].message.content

    def update_towards_goal(self, image_data: str):
        prompt = TOWARDS_GOAL_PROMPT.format(goal=self._goal, memory=self._memory)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"} }
                        ]
                    }
                ]
            )

        content = response.choices[0].message.content
        start = content.find("{")
        end = content.find("}") + 1
        data = json.loads(content[start:end])

        description = data["description"]
        memory = data["memory"]
        commands = data["commands"]

        self._latest_description = description
        self._memory = memory
        self._commands = commands

        print("---")
        print("AI Description:", self._latest_description)
        print("AI Memory:", self._memory)
        print("AI commands:", self._commands)
