import openai

class BackendAgent:
    """Dedicated AI agent for backend development tasks with Python/Flask expertise."""

    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        openai.api_key = self.api_key

    def generate_flask_code(self, prompt: str) -> str:
        """
        Generate Python/Flask backend code based on the provided prompt.
        :param prompt: Description of the backend task.
        :return: Generated Python/Flask code as string.
        """
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful AI assistant specialized in Python backend development using Flask."
                " Provide clean, efficient, and PEP8-compliant Flask code snippets."
            )
        }
        user_message = {"role": "user", "content": prompt}

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[system_message, user_message],
            temperature=0.2,
            max_tokens=800,
            n=1,
            stop=None
        )

        code = response.choices[0].message.content.strip()
        return code

    def review_flask_code(self, code: str) -> str:
        """
        Review and provide suggestions or improvements for the given Flask code.
        :param code: Flask backend code as string.
        :return: Review comments and suggested improvements.
        """
        system_message = {
            "role": "system",
            "content": (
                "You are a Python backend expert specializing in Flask."
                " Review the following code and suggest improvements, highlight bugs, and check best practices."
            )
        }
        user_message = {"role": "user", "content": code}

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[system_message, user_message],
            temperature=0.0,
            max_tokens=600,
            n=1,
            stop=None
        )

        review = response.choices[0].message.content.strip()
        return review


if __name__ == "__main__":
    import os

    agent = BackendAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))

    sample_prompt = "Create a Flask API endpoint that accepts a POST request with JSON data containing 'name' and 'age', and returns a greeting message including the name and age."
    generated_code = agent.generate_flask_code(sample_prompt)
    print("Generated Flask Code:\n", generated_code)

    review = agent.review_flask_code(generated_code)
    print("\nCode Review:\n", review)
