from typing import Dict, Any, List, Set, Tuple
from pathlib import Path
import json
import anthropic
from anthropic import Anthropic
import click

class Translator:
    """Translates text using Anthropic's API"""
    
    def __init__(self, reference_data: Dict[str, Any], docs_content: str):
        """
        Initialize translator with reference data and docs content
        
        Args:
            reference_data: Parsed reference.yaml content
            docs_content: Content of docs.md
        """
        self.reference_data = reference_data
        self.docs_content = docs_content
        self.client = Anthropic()

    def system_prompt(self) -> str:
        """Returns the system prompt for the translator"""
        with open(Path(__file__).parent / 'prompts' / 'translator_system.md', 'r') as file:
            return file.read()

    def create_translation_prompt(self, target_lang: str) -> str:
        """
        Create the full translation prompt
        
        Args:
            target_lang: Target language code (e.g., 'ko', 'ja')
            
        Returns:
            Complete prompt with reference data and docs
        """
        # Convert reference data to JSON string with proper formatting
        reference_json = json.dumps(self.reference_data, ensure_ascii=False, indent=2)
        
        # Create the input sections using the format from the system prompt
        input_sections = f"""<reference.json>
{reference_json}
</reference.json>

<docs.md>
{self.docs_content}
</docs.md>

<target_language>
{target_lang}
</target_language>"""
        
        return input_sections

    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from Claude's response
        
        Args:
            response: Full response from Claude
            
        Returns:
            Parsed JSON object
        """
        try:
            # Find the JSON content between <output_json> tags
            start_tag = "<output_json>"
            end_tag = "</output_json>"
            start_idx = response.find(start_tag) + len(start_tag)
            end_idx = response.find(end_tag)
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("Could not find output JSON tags in response")
            
            json_str = response[start_idx:end_idx].strip()
            return json.loads(json_str)
            
        except Exception as e:
            raise click.ClickException(f"Failed to parse translation output: {str(e)}")

    def translate(self, target_lang: str) -> str:
        """
        Translate the reference content to target language
        
        Args:
            target_lang: Target language code (e.g., 'ko', 'ja')
            
        Returns:
            Translated content in same structure as reference
        """
        try:
            system_prompt = self.system_prompt()
            translation_prompt = self.create_translation_prompt(target_lang)
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": translation_prompt
                    }
                ]
            )
            
            # Extract and parse the JSON from response
            translated_content = self.extract_json_from_response(message.content[0].text)
            
            return translated_content
            
        except anthropic.APIError as e:
            raise click.ClickException(f"Translation API error: {str(e)}")
        except Exception as e:
            raise click.ClickException(f"Translation failed: {str(e)}")

    def validate_translation(self, translated_content: Dict[str, Any]) -> bool:
        """
        Validate the translated content matches reference structure
        
        Args:
            translated_content: Translated content to validate
            
        Returns:
            True if valid, raises exception if not
        """
        def check_structure(ref: Dict[str, Any], trans: Dict[str, Any], path: str = "") -> None:
            """Recursively check structure matches"""
            ref_keys = set(ref.keys())
            trans_keys = set(trans.keys())
            
            if ref_keys != trans_keys:
                missing = ref_keys - trans_keys
                extra = trans_keys - ref_keys
                if missing:
                    raise click.ClickException(
                        f"Missing keys at {path}: {', '.join(missing)}"
                    )
                if extra:
                    raise click.ClickException(
                        f"Extra keys at {path}: {', '.join(extra)}"
                    )
            
            for key in ref_keys:
                new_path = f"{path}.{key}" if path else key
                if isinstance(ref[key], dict):
                    if not isinstance(trans[key], dict):
                        raise click.ClickException(
                            f"Type mismatch at {new_path}: expected dict"
                        )
                    check_structure(ref[key], trans[key], new_path)

        try:
            check_structure(self.reference_data, translated_content)
            return True
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Validation error: {str(e)}")