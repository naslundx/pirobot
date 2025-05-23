import json
from openai import OpenAI


TOWARDS_GOAL_PROMPT = """
You are a robot on wheels. You will receive a target goal, an image from the front camera, and more context. You will return a JSON with a description, what to remember for next call, and a list of commands.

You will be prompted again when all commands in the list have been exhausted.

# Examples

Input: The goal is "Move to the next room." and the image shows an opening to another room.
Output: JSON: {{ "description": "Opening to the other room far ahead. Nothing else intersting in the room.", "memory": "No openings found to the left or to the right. Stop after the room has been entered.", "commands": ["forward", "forward", "forward"] }}

Input: The goal is "Locate the clown" and the image shows a clown.
Output: JSON: {{ "description": "A large clown covers most of the image. Goal has been reached.", "memory": "Clown was not located in the room that's behind.", "commands": ["done"] }}

Input: The goal is "Turn right until a ball is seen, then move close to it.".
Output: JSON: {{ "description": "Image description", "memory": "Has turned right.", "commands": ["turn_right"] }}

Input: The input is black.
Output: JSON: {{ "description": "Black image.", "memory": "Camera error or bumped up against a wall. Stopped once to get a fresh camera image.", "commands": ["pass"] }}

Input: The input is black and memory says the robot has stopped once.
Output: JSON: {{ "description": "Black image.", "memory": "Reversed to get better image.", "commands": ["reverse"] }}

# Output
Return a JSON.

Possible commands are:
- forward, reverse: Moves forward or backward for 1.5 seconds and then stops.
- turn_left, turn_right: Turns 45 degrees to the left or to the right.
- pass: Do nothing this time.
- done: Indicates that the goal has been reached.

Always try to turn around 360 degrees while looking for a specific object, rather than moving forward/backward, if possible!

# Current context

Current goal: {goal}
Current memory: {memory}
Previous commands: {previous_commands}
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

    def get_response(self, user_input, image_data=None):
        content = [
            {"type": "text", "text": user_input}
        ]
        if image_data:
            content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"} }
            )

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

        return response.choices[0].message.content

    def update_towards_goal(self, image_data: str):
        previous_commands = ', '.join(self._previous_commands)
        prompt = TOWARDS_GOAL_PROMPT.format(goal=self._goal, memory=self._memory, previous_commands=previous_commands)

        response = self.get_response(prompt, image_data)

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
