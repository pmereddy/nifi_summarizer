import os
import logging

class PromptLoader:
    """
    Loads prompt templates from a given directory.
    """
    def __init__(self, prompt_dir: str):
        self.prompt_dir = prompt_dir
        self.logger = logging.getLogger(__name__)

    def load(self, template_name: str) -> str:
        """
        Read and return the content of the given template file.
        Raises FileNotFoundError if not found.
        """
        path = os.path.join(self.prompt_dir, template_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.debug(f"Loaded prompt template: {template_name}")
            return content
        except FileNotFoundError:
            self.logger.error(f"Prompt template not found: {path}")
            raise
        except Exception as e:
            self.logger.exception(f"Error reading prompt template {path}: {e}")
            raise
