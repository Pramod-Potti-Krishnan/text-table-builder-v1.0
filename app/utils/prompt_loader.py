"""
Prompt Loader Utility
=====================

Loads and manages system prompts from markdown files with template substitution.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    Loads system prompts from markdown files and performs template substitution.

    Supports caching for performance and flexible template variable substitution.
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize prompt loader.

        Args:
            prompts_dir: Directory containing prompt markdown files.
                        Defaults to app/prompts/
        """
        if prompts_dir is None:
            # Default to app/prompts/ relative to this file
            current_dir = Path(__file__).parent.parent
            prompts_dir = current_dir / "prompts"

        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory does not exist: {self.prompts_dir}")

    def load_prompt(self, prompt_name: str, use_cache: bool = True) -> str:
        """
        Load a prompt from markdown file.

        Args:
            prompt_name: Name of the prompt (without .md extension)
            use_cache: Whether to use cached version if available

        Returns:
            Raw prompt content as string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        # Check cache first
        if use_cache and prompt_name in self._cache:
            logger.debug(f"Using cached prompt: {prompt_name}")
            return self._cache[prompt_name]

        # Load from file
        prompt_file = self.prompts_dir / f"{prompt_name}.md"

        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}\n"
                f"Available prompts: {self.list_available_prompts()}"
            )

        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Cache the content
            self._cache[prompt_name] = content
            logger.info(f"Loaded prompt from file: {prompt_name}")

            return content

        except Exception as e:
            logger.error(f"Error loading prompt {prompt_name}: {e}")
            raise

    def get_prompt_with_vars(
        self,
        prompt_name: str,
        variables: Dict[str, Any],
        strict: bool = False
    ) -> str:
        """
        Load prompt and substitute template variables.

        Args:
            prompt_name: Name of the prompt (without .md extension)
            variables: Dictionary of variable name -> value mappings
            strict: If True, raises error on missing variables.
                   If False, leaves unsubstituted variables as-is.

        Returns:
            Prompt with variables substituted

        Example:
            loader.get_prompt_with_vars(
                "text_generation",
                {
                    "target_words": 50,
                    "min_words": 45,
                    "max_words": 55,
                    "theme": "professional",
                    "previous_context": "Slide 1 covered revenue growth..."
                }
            )
        """
        # Load raw prompt
        prompt = self.load_prompt(prompt_name)

        # Substitute variables
        try:
            if strict:
                # Strict mode: all variables must be provided
                return prompt.format(**variables)
            else:
                # Lenient mode: use format_map with custom dict that returns placeholder for missing keys
                return prompt.format_map(_SafeFormatter(variables))

        except KeyError as e:
            logger.error(f"Missing required variable in prompt {prompt_name}: {e}")
            if strict:
                raise ValueError(f"Missing required variable: {e}")
            return prompt
        except Exception as e:
            logger.error(f"Error substituting variables in prompt {prompt_name}: {e}")
            raise

    def list_available_prompts(self) -> list[str]:
        """
        List all available prompt files.

        Returns:
            List of prompt names (without .md extension)
        """
        if not self.prompts_dir.exists():
            return []

        return [
            f.stem for f in self.prompts_dir.glob("*.md")
            if f.is_file()
        ]

    def clear_cache(self):
        """Clear the prompt cache."""
        self._cache.clear()
        logger.info("Prompt cache cleared")

    def reload_prompt(self, prompt_name: str) -> str:
        """
        Reload a prompt from disk, bypassing cache.

        Args:
            prompt_name: Name of the prompt to reload

        Returns:
            Reloaded prompt content
        """
        # Remove from cache if present
        if prompt_name in self._cache:
            del self._cache[prompt_name]

        # Load fresh from disk
        return self.load_prompt(prompt_name, use_cache=False)


class _SafeFormatter(dict):
    """
    Safe dictionary for string formatting that returns placeholder for missing keys.

    Used for lenient template substitution.
    """

    def __missing__(self, key):
        """Return the placeholder for missing keys."""
        return "{" + key + "}"


# Singleton instance for application-wide use
_prompt_loader_instance: Optional[PromptLoader] = None


def get_prompt_loader() -> PromptLoader:
    """
    Get the singleton PromptLoader instance.

    Returns:
        Shared PromptLoader instance
    """
    global _prompt_loader_instance

    if _prompt_loader_instance is None:
        _prompt_loader_instance = PromptLoader()

    return _prompt_loader_instance


# Convenience functions for common use cases

def load_text_generation_prompt(
    target_words: int,
    previous_context: str,
    theme: str,
    audience: str,
    slide_title: str,
    narrative: str,
    topics: str
) -> str:
    """
    Load text generation prompt with standard variables.

    Args:
        target_words: Target word count for the content
        previous_context: Summary of previous slides
        theme: Presentation theme
        audience: Target audience
        slide_title: Current slide title
        narrative: Slide narrative/story
        topics: Topics to cover (formatted string)

    Returns:
        Formatted text generation prompt
    """
    loader = get_prompt_loader()

    # Calculate word count range (±10% tolerance)
    tolerance = 0.10
    min_words = int(target_words * (1 - tolerance))
    max_words = int(target_words * (1 + tolerance))

    variables = {
        "target_words": target_words,
        "min_words": min_words,
        "max_words": max_words,
        "previous_context": previous_context,
        "theme": theme,
        "audience": audience,
        "slide_title": slide_title,
        "narrative": narrative,
        "topics": topics
    }

    return loader.get_prompt_with_vars("text_generation", variables)


def load_table_generation_prompt(
    description: str,
    data: str,
    previous_context: str,
    theme: str,
    audience: str,
    slide_title: str,
    context: str = ""
) -> str:
    """
    Load table generation prompt with standard variables.

    Args:
        description: Description of what the table should show
        data: Raw data (formatted as string, e.g., JSON)
        previous_context: Summary of previous slides
        theme: Presentation theme
        audience: Target audience
        slide_title: Current slide title
        context: Additional context information

    Returns:
        Formatted table generation prompt
    """
    loader = get_prompt_loader()

    variables = {
        "description": description,
        "data": data,
        "previous_context": previous_context,
        "theme": theme,
        "audience": audience,
        "slide_title": slide_title,
        "context": context
    }

    return loader.get_prompt_with_vars("table_generation", variables)


# Example usage
if __name__ == "__main__":
    # Example: Load and test prompts
    loader = PromptLoader()

    print("Available prompts:", loader.list_available_prompts())

    # Test text generation prompt
    text_prompt = load_text_generation_prompt(
        target_words=50,
        previous_context="Slide 1 covered Q2 revenue growth of 32% across all regions.",
        theme="professional",
        audience="executives",
        slide_title="Q3 Market Expansion",
        narrative="Strategic expansion into three new markets drove exceptional growth",
        topics="- New market entry\n- Partnership acquisitions\n- Revenue impact"
    )

    print("\n" + "="*80)
    print("TEXT GENERATION PROMPT (first 500 chars):")
    print("="*80)
    print(text_prompt[:500] + "...")

    # Test table generation prompt
    table_prompt = load_table_generation_prompt(
        description="Quarterly revenue comparison by region",
        data='{"Q2": {"NA": 45.2, "EU": 32.1}, "Q3": {"NA": 58.3, "EU": 39.4}}',
        previous_context="Previous slide showed overall growth of 32%",
        theme="professional",
        audience="executives",
        slide_title="Regional Performance"
    )

    print("\n" + "="*80)
    print("TABLE GENERATION PROMPT (first 500 chars):")
    print("="*80)
    print(table_prompt[:500] + "...")
