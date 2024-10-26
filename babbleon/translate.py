import json
import toml
from pathlib import Path
from babbleon.config import BabbleonConfig
from importlib_resources import files, as_file
from anthropic import Anthropic


class BabbleonTranslator:
    def __init__(self, reference_raw: str, output_format: str):
        self.reference_raw = reference_raw
        self.output_format = output_format
        self.anthropic_client = Anthropic()

    def parse_reference(self) -> dict:
        reference = toml.loads(self.reference_raw)
        reference_json = json.dumps(reference, indent=2)

        return reference_json

    def get_reference_prompt(self) -> str:
        reference_prompt = f"""<reference.toml>{self.reference_raw}</reference.toml>"""
        if self.output_format == "toml":
            return reference_prompt
        else:
            return (
                reference_prompt
                + f"""<reference.json>{self.parse_reference()}</reference.json>"""
            )

    def get_system_message(self) -> list[dict]:
        reference_prompt = self.get_reference_prompt()
        static_prompt_path = files("babbleon.prompts").joinpath(
            f"translator_{self.output_format}.md"
        )
        with open(static_prompt_path, "r", encoding="utf-8") as src:
            static_prompts = src.read()
        return [
            {
                "type": "text",
                "text": static_prompts,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": reference_prompt,
                "cache_control": {"type": "ephemeral"},
            },
        ]

    def translate(self, language: str) -> str:
        response = self.anthropic_client.beta.prompt_caching.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=self.get_system_message(),
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"<language>{language}</language>",
                }
            ],
        )
        response_text = response.content[0].text
        output = response_text.split("<output>")[1].split("</output>")[0]
        return output


if __name__ == "__main__":
    reference_raw = """
[title]
home = "Home"

[home.hero]
# It should be welcoming and inviting as the first thing new users see
title = "Welcome to Babbleon"
"""
    translator = BabbleonTranslator(reference_raw)
    translator.translate("ko")
