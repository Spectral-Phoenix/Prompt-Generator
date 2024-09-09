import json
import os
import re
import openai

client = openai.OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ.get("OPENAI_API_KEY")
)


class MetaPrompt:
    def __init__(self):
        # Get the directory where the current script is located
        current_script_path = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the file
        prompt_guide_path = os.path.join(current_script_path, "metaprompt.txt")

        # Open the file using the full path
        with open(prompt_guide_path, "r") as f:
            self.metaprompt = f.read()

        # Set your OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def __call__(self, task, variables):
        variables = variables.split("\n")
        variables = [variable for variable in variables if len(variable)]

        variable_string = ""
        for variable in variables:
            variable_string += "\n{$" + variable.upper() + "}"
        prompt = self.metaprompt.replace("{{TASK}}", task)
        assistant_partial = "<Inputs>"
        if variable_string:
            assistant_partial += (
                variable_string + "\n</Inputs>\n<Instructions Structure>"
            )
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": assistant_partial},
        ]

        response = client.chat.completions.create(
            model="llama3.1-8b",  # Or another suitable OpenAI model
            messages=messages,
            max_tokens=8192,
            temperature=0.7,
        )

        message = response.choices[0].message.content
        # print(message)

        def pretty_print(message):
            print(
                "\n\n".join(
                    "\n".join(
                        line.strip()
                        for line in re.findall(
                            r".{1,100}(?:\s+|$)", paragraph.strip("\n")
                        )
                    )
                    for paragraph in re.split(r"\n\n+", message)
                )
            )

        extracted_prompt_template = self.extract_prompt(message)
        variables = self.extract_variables(message)

        return extracted_prompt_template.strip(), "\n".join(variables)

    def extract_between_tags(
        self, tag: str, string: str, strip: bool = False
    ) -> list[str]:
        ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        return ext_list

    def remove_empty_tags(self, text):
        return re.sub(r"\n<(\w+)>\s*</\1>\n", "", text, flags=re.DOTALL)

    def extract_prompt(self, metaprompt_response):
        between_tags = self.extract_between_tags("Instructions", metaprompt_response)[0]
        return (
            between_tags[:1000]
            + self.remove_empty_tags(
                self.remove_empty_tags(between_tags[1000:]).strip()
            ).strip()
        )

    def extract_variables(self, prompt):
        pattern = r"{([^}]+)}"
        variables = re.findall(pattern, prompt)
        return set(variables)