import json
from openai import OpenAI


TOWARDS_GOAL_PROMPT = """
You are a robot on wheels. You will receive a target goal, an image from the front camera, and more context. You will return a JSON with a description, what to remember for next call, and a list of commands.

You will be prompted again when all commands in the list have been exhausted.

Example:
Input: The goal is "Move to the next room." and the image shows an opening to another room.
Output: JSON: {{ "description": "Opening to the other room far ahead. Nothing else intersting in the room.", "memory": "No openings found to the left or to the right. Stop after the room has been entered.", "commands": ["forward", "forward", "forward"] }}

Input: The goal is "Locate the clown" and the image shows a clown.
Output: JSON: {{ "description": "A large clown covers most of the image. Goal has been reached.", "memory": "Clown was not located in the room that's behind.", "commands": ["done"] }}

Input: The goal is "Turn right 90 degrees".
Output: JSON: {{ "description": "Image description", "memory": "Has turned right.", "commands": ["turn_right", "turn_right", "done"] }}

Input: The input contains a blurry image.
Output: JSON: {{ "description": "Blurry image.", "memory": "Stopping once to get a fresh camera image.", "commands": ["pass"] }}

Input: The input contains a blurry image and the memory says the robot has stopped once to get a fresh camera image.
Output: JSON: {{ "description": "Blurry image.", "memory": "Has tried to get fresh image, reversing to get a better overview.", "commands": ["reverse"] }}

Possible commands are:
- forward, reverse: Moves forward or backward for 1.5 seconds and then stops.
- turn_left, turn_right: Turns 45 degrees to the left or to the right.
- pass: Do nothing
- done: Indicates that the goal has been reached.

Current goal: {goal}
Current memory: {memory}
Previous commands: {previous_commands}

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
        self._previous_commands = []

    @property
    def status(self):
        return self._latest_description

    def get_next_command(self):
        if self._commands:
            return self._commands.pop(0)

        return None

    def set_goal(self, goal):
        self._commands = []
        self._memory = ""
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
        previous_commands = ', '.join(self._previous_commands)
        prompt = TOWARDS_GOAL_PROMPT.format(goal=self._goal, memory=self._memory, previous_commands=previous_commands)

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
        self._previous_commands = commands[:]

        print("---")
        print("AI Description:", self._latest_description)
        print("AI Memory:", self._memory)
        print("AI Commands:", self._commands)
