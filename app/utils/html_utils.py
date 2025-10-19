"""
HTML Utilities for Content Validation and Formatting
=====================================================

Tools for validating, sanitizing, and analyzing HTML content.
"""

import os
import re
import logging
from typing import List, Dict, Set, Tuple
from bs4 import BeautifulSoup, Tag


logger = logging.getLogger(__name__)


# Default allowed HTML tags (configurable via environment)
DEFAULT_ALLOWED_TAGS = {
    'p', 'strong', 'em', 'mark', 'code', 'span',
    'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td'
}

# Default allowed attributes
DEFAULT_ALLOWED_ATTRS = {
    '*': ['class', 'id'],  # Global attributes
    'span': ['data-value', 'data-unit', 'data-*'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan', 'scope']
}


class HTMLValidator:
    """
    Validates HTML content for presentation use.

    Checks for:
    - Valid HTML structure
    - Allowed tags only
    - Proper nesting
    - Balanced tags
    """

    def __init__(
        self,
        allowed_tags: Set[str] = None,
        allowed_attrs: Dict[str, List[str]] = None
    ):
        """
        Initialize HTML validator.

        Args:
            allowed_tags: Set of allowed HTML tag names
            allowed_attrs: Dictionary of tag -> allowed attributes
        """
        # Load from environment or use defaults
        env_tags = os.getenv("HTML_ALLOWED_TAGS")
        if env_tags:
            self.allowed_tags = set(env_tags.split(','))
        else:
            self.allowed_tags = allowed_tags or DEFAULT_ALLOWED_TAGS

        self.allowed_attrs = allowed_attrs or DEFAULT_ALLOWED_ATTRS

    def validate(self, html_content: str) -> Tuple[bool, List[str]]:
        """
        Validate HTML content.

        Args:
            html_content: HTML string to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not html_content or not html_content.strip():
            errors.append("Empty HTML content")
            return False, errors

        try:
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Check for disallowed tags
            for tag in soup.find_all():
                if tag.name not in self.allowed_tags:
                    errors.append(f"Disallowed tag: <{tag.name}>")

            # Check for balanced tags (BeautifulSoup auto-fixes, so we check original)
            if not self._check_balanced_tags(html_content):
                errors.append("Unbalanced HTML tags detected")

            # Check nesting rules (e.g., no block elements inside inline)
            nesting_errors = self._check_nesting(soup)
            errors.extend(nesting_errors)

        except Exception as e:
            errors.append(f"HTML parsing error: {str(e)}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def _check_balanced_tags(self, html: str) -> bool:
        """
        Check if all HTML tags are balanced.

        Args:
            html: HTML string

        Returns:
            True if balanced, False otherwise
        """
        # Simple stack-based check
        stack = []
        tag_pattern = re.compile(r'<(/?)(\w+)[^>]*>')

        for match in tag_pattern.finditer(html):
            is_closing = match.group(1) == '/'
            tag_name = match.group(2)

            # Skip self-closing tags
            if tag_name in {'br', 'hr', 'img', 'input'}:
                continue

            if is_closing:
                if not stack or stack[-1] != tag_name:
                    return False
                stack.pop()
            else:
                stack.append(tag_name)

        return len(stack) == 0

    def _check_nesting(self, soup: BeautifulSoup) -> List[str]:
        """
        Check HTML nesting rules.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of nesting errors
        """
        errors = []

        # Define block and inline elements
        block_elements = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table', 'blockquote'}
        inline_elements = {'span', 'strong', 'em', 'mark', 'code'}

        # Check for block elements inside inline elements
        for inline_tag in soup.find_all(inline_elements):
            for child in inline_tag.find_all():
                if child.name in block_elements:
                    errors.append(
                        f"Block element <{child.name}> inside inline element <{inline_tag.name}>"
                    )

        return errors


class HTMLSanitizer:
    """
    Sanitizes HTML by removing disallowed tags and attributes.
    """

    def __init__(
        self,
        allowed_tags: Set[str] = None,
        allowed_attrs: Dict[str, List[str]] = None
    ):
        """
        Initialize HTML sanitizer.

        Args:
            allowed_tags: Set of allowed HTML tag names
            allowed_attrs: Dictionary of tag -> allowed attributes
        """
        self.allowed_tags = allowed_tags or DEFAULT_ALLOWED_TAGS
        self.allowed_attrs = allowed_attrs or DEFAULT_ALLOWED_ATTRS

    def sanitize(self, html_content: str) -> str:
        """
        Sanitize HTML by removing disallowed tags and attributes.

        Args:
            html_content: Raw HTML string

        Returns:
            Sanitized HTML string
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove disallowed tags
        for tag in soup.find_all():
            if tag.name not in self.allowed_tags:
                tag.unwrap()  # Remove tag but keep content

        # Remove disallowed attributes
        for tag in soup.find_all():
            # Get allowed attrs for this tag
            tag_allowed_attrs = self.allowed_attrs.get(tag.name, [])
            global_attrs = self.allowed_attrs.get('*', [])
            all_allowed = set(tag_allowed_attrs + global_attrs)

            # Remove disallowed attributes
            attrs_to_remove = []
            for attr in tag.attrs:
                if attr not in all_allowed:
                    # Check for data-* pattern
                    if not (attr.startswith('data-') and 'data-*' in all_allowed):
                        attrs_to_remove.append(attr)

            for attr in attrs_to_remove:
                del tag.attrs[attr]

        return str(soup)


class WordCounter:
    """
    Counts words in HTML content (excluding tags).
    """

    @staticmethod
    def count_words(html_content: str) -> int:
        """
        Count words in HTML, excluding tags.

        Args:
            html_content: HTML string

        Returns:
            Word count
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get text content only
        text = soup.get_text(separator=' ', strip=True)

        # Split and count words
        words = text.split()
        return len(words)

    @staticmethod
    def count_words_with_details(html_content: str) -> Dict[str, int]:
        """
        Count words with additional details.

        Args:
            html_content: HTML string

        Returns:
            Dictionary with word count details
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        text = soup.get_text(separator=' ', strip=True)
        words = text.split()

        return {
            "total_words": len(words),
            "total_characters": len(text),
            "characters_no_spaces": len(text.replace(' ', '')),
            "avg_word_length": round(sum(len(w) for w in words) / len(words), 1) if words else 0
        }

    @staticmethod
    def estimate_reading_time(word_count: int, words_per_minute: int = 200) -> float:
        """
        Estimate reading time in minutes.

        Args:
            word_count: Number of words
            words_per_minute: Average reading speed (default: 200 wpm)

        Returns:
            Estimated reading time in minutes
        """
        return word_count / words_per_minute


class HTMLAnalyzer:
    """
    Analyzes HTML structure and content.
    """

    @staticmethod
    def extract_tags(html_content: str) -> List[str]:
        """
        Extract unique HTML tags used.

        Args:
            html_content: HTML string

        Returns:
            Sorted list of unique tag names
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        tags = set(tag.name for tag in soup.find_all())
        return sorted(tags)

    @staticmethod
    def analyze_structure(html_content: str) -> Dict[str, any]:
        """
        Analyze HTML structure.

        Args:
            html_content: HTML string

        Returns:
            Dictionary with structure analysis
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        analysis = {
            "total_elements": len(soup.find_all()),
            "unique_tags": len(set(tag.name for tag in soup.find_all())),
            "tags_used": sorted(set(tag.name for tag in soup.find_all())),
            "depth": HTMLAnalyzer._calculate_depth(soup),
            "text_nodes": len(list(soup.stripped_strings)),
            "has_lists": soup.find('ul') is not None or soup.find('ol') is not None,
            "has_tables": soup.find('table') is not None,
            "has_headings": any(soup.find(f'h{i}') for i in range(1, 7))
        }

        # Count specific elements
        analysis["list_items"] = len(soup.find_all('li'))
        analysis["paragraphs"] = len(soup.find_all('p'))
        analysis["tables"] = len(soup.find_all('table'))

        return analysis

    @staticmethod
    def _calculate_depth(element, current_depth=0) -> int:
        """
        Calculate maximum nesting depth of HTML.

        Args:
            element: BeautifulSoup element
            current_depth: Current depth level

        Returns:
            Maximum depth
        """
        if not hasattr(element, 'children'):
            return current_depth

        max_child_depth = current_depth
        for child in element.children:
            if isinstance(child, Tag):
                child_depth = HTMLAnalyzer._calculate_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    @staticmethod
    def extract_classes(html_content: str) -> List[str]:
        """
        Extract all CSS classes used.

        Args:
            html_content: HTML string

        Returns:
            Sorted list of unique class names
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        classes = set()

        for tag in soup.find_all(class_=True):
            classes.update(tag.get('class', []))

        return sorted(classes)


class HTMLFormatter:
    """
    Formats and prettifies HTML.
    """

    @staticmethod
    def prettify(html_content: str, indent: int = 2) -> str:
        """
        Prettify HTML with proper indentation.

        Args:
            html_content: Raw HTML string
            indent: Number of spaces for indentation

        Returns:
            Prettified HTML string
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.prettify(formatter="html")

    @staticmethod
    def minify(html_content: str) -> str:
        """
        Minify HTML by removing whitespace.

        Args:
            html_content: HTML string

        Returns:
            Minified HTML string
        """
        # Remove extra whitespace
        minified = re.sub(r'\s+', ' ', html_content)
        minified = re.sub(r'>\s+<', '><', minified)
        return minified.strip()


# Convenience functions

def validate_html(html_content: str) -> Tuple[bool, List[str]]:
    """
    Validate HTML content (convenience function).

    Args:
        html_content: HTML string

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = HTMLValidator()
    return validator.validate(html_content)


def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content (convenience function).

    Args:
        html_content: HTML string

    Returns:
        Sanitized HTML string
    """
    sanitizer = HTMLSanitizer()
    return sanitizer.sanitize(html_content)


def count_words(html_content: str) -> int:
    """
    Count words in HTML (convenience function).

    Args:
        html_content: HTML string

    Returns:
        Word count
    """
    return WordCounter.count_words(html_content)


def analyze_html(html_content: str) -> Dict[str, any]:
    """
    Analyze HTML structure (convenience function).

    Args:
        html_content: HTML string

    Returns:
        Analysis dictionary
    """
    return HTMLAnalyzer.analyze_structure(html_content)


# Example usage
if __name__ == "__main__":
    # Example HTML
    test_html = """
    <p>Q3 demonstrated <strong>exceptional revenue growth</strong> across all key markets.</p>
    <ul>
      <li>Revenue increased by <span class="metric positive">+32%</span> quarter-over-quarter</li>
      <li>Market expansion into <em>three new regions</em></li>
      <li>Cost efficiency improved through <mark>strategic automation</mark></li>
    </ul>
    """

    print("="*80)
    print("HTML VALIDATION:")
    print("="*80)
    is_valid, errors = validate_html(test_html)
    print(f"Valid: {is_valid}")
    if errors:
        print("Errors:", errors)

    print("\n" + "="*80)
    print("WORD COUNT:")
    print("="*80)
    words = count_words(test_html)
    print(f"Total words: {words}")

    details = WordCounter.count_words_with_details(test_html)
    print(f"Details: {details}")

    print("\n" + "="*80)
    print("HTML ANALYSIS:")
    print("="*80)
    analysis = analyze_html(test_html)
    for key, value in analysis.items():
        print(f"  {key}: {value}")

    print("\n" + "="*80)
    print("TAGS AND CLASSES:")
    print("="*80)
    print(f"Tags used: {HTMLAnalyzer.extract_tags(test_html)}")
    print(f"Classes used: {HTMLAnalyzer.extract_classes(test_html)}")
