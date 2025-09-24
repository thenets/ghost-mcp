"""Content validation utilities for Ghost posts and pages."""

import json
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Set, Union

from ..types.errors import ValidationError


class HTMLValidator(HTMLParser):
    """HTML validator to check for balanced tags and valid structure."""

    def __init__(self):
        super().__init__()
        self.tag_stack: List[str] = []
        self.errors: List[str] = []
        self.valid_tags: Set[str] = {
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span',
            'a', 'strong', 'em', 'b', 'i', 'u', 'code', 'pre',
            'ul', 'ol', 'li', 'blockquote', 'br', 'hr', 'img',
            'table', 'tr', 'td', 'th', 'thead', 'tbody',
        }
        self.self_closing_tags: Set[str] = {'br', 'hr', 'img'}

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:  # noqa: ARG002
        """Handle opening tags."""
        if tag not in self.valid_tags:
            self.errors.append(f"Invalid HTML tag: <{tag}>")

        if tag not in self.self_closing_tags:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        """Handle closing tags."""
        if tag in self.self_closing_tags:
            self.errors.append(f"Self-closing tag should not have closing tag: </{tag}>")
            return

        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag: </{tag}>")
            return

        if self.tag_stack[-1] != tag:
            self.errors.append(f"Mismatched tags: expected </{self.tag_stack[-1]}>, got </{tag}>")
        else:
            self.tag_stack.pop()

    def error(self, message: str) -> None:
        """Handle HTML parsing errors."""
        self.errors.append(f"HTML parsing error: {message}")

    def validate(self) -> List[str]:
        """Return validation errors."""
        if self.tag_stack:
            self.errors.extend([f"Unclosed tag: <{tag}>" for tag in self.tag_stack])
        return self.errors


def validate_lexical_content(content: str) -> Dict[str, Any]:
    """
    Validate Lexical JSON content structure.

    Args:
        content: Lexical JSON string

    Returns:
        Parsed Lexical structure if valid

    Raises:
        ValidationError: If content is invalid
    """
    if not content or not isinstance(content, str):
        raise ValidationError(
            "Lexical content must be a non-empty JSON string",
            context="Expected format: '{\"root\": {\"children\": [...], ...}}'"
        )

    try:
        lexical_data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON in Lexical content: {e}",
            context="Ensure the content is valid JSON with proper escaping"
        )

    if not isinstance(lexical_data, dict):
        raise ValidationError(
            "Lexical content must be a JSON object",
            context="Expected format: '{\"root\": {\"children\": [...], ...}}'"
        )

    # Validate root structure
    if "root" not in lexical_data:
        raise ValidationError(
            "Lexical content must have a 'root' property",
            context="Example: '{\"root\": {\"children\": [], \"direction\": \"ltr\", \"format\": \"\", \"indent\": 0, \"type\": \"root\", \"version\": 1}}'"
        )

    root = lexical_data["root"]
    if not isinstance(root, dict):
        raise ValidationError(
            "Lexical 'root' must be an object",
            context="The root property should contain the document structure"
        )

    # Validate required root properties
    required_root_props = ["children", "direction", "format", "indent", "type", "version"]
    for prop in required_root_props:
        if prop not in root:
            raise ValidationError(
                f"Lexical root missing required property: '{prop}'",
                context=f"Root must have: {', '.join(required_root_props)}"
            )

    if root.get("type") != "root":
        raise ValidationError(
            "Lexical root type must be 'root'",
            context="Set root.type to 'root'"
        )

    if not isinstance(root.get("children"), list):
        raise ValidationError(
            "Lexical root.children must be an array",
            context="Children should be an array of content nodes"
        )

    # Validate children nodes
    _validate_lexical_nodes(root["children"], "root.children")

    return lexical_data


def _validate_lexical_nodes(nodes: List[Dict], path: str) -> None:
    """Validate Lexical node structure recursively."""
    valid_node_types = {
        "paragraph", "heading", "text", "link", "list", "listitem",
        "code", "quote", "linebreak"
    }

    for i, node in enumerate(nodes):
        node_path = f"{path}[{i}]"

        if not isinstance(node, dict):
            raise ValidationError(
                f"Lexical node at {node_path} must be an object",
                context="Each node should be a JSON object with type, version, and other properties"
            )

        if "type" not in node:
            raise ValidationError(
                f"Lexical node at {node_path} missing 'type' property",
                context=f"Valid types: {', '.join(sorted(valid_node_types))}"
            )

        node_type = node.get("type")
        if node_type not in valid_node_types:
            raise ValidationError(
                f"Invalid Lexical node type '{node_type}' at {node_path}",
                context=f"Valid types: {', '.join(sorted(valid_node_types))}"
            )

        if "version" not in node:
            raise ValidationError(
                f"Lexical node at {node_path} missing 'version' property",
                context="All nodes must have a version number (usually 1)"
            )

        # Validate node-specific requirements
        if node_type == "heading" and "tag" not in node:
            raise ValidationError(
                f"Heading node at {node_path} missing 'tag' property",
                context="Heading nodes must specify tag (h1, h2, h3, h4, h5, h6)"
            )

        if node_type == "link" and "url" not in node:
            raise ValidationError(
                f"Link node at {node_path} missing 'url' property",
                context="Link nodes must have a URL property"
            )

        if node_type == "list" and "listType" not in node:
            raise ValidationError(
                f"List node at {node_path} missing 'listType' property",
                context="List nodes must specify listType ('bullet' or 'number')"
            )

        # Recursively validate children if present
        if "children" in node and isinstance(node["children"], list):
            _validate_lexical_nodes(node["children"], f"{node_path}.children")


def validate_html_content(content: str) -> str:
    """
    Validate HTML content structure.

    Args:
        content: HTML content string

    Returns:
        Cleaned HTML content

    Raises:
        ValidationError: If HTML is invalid
    """
    if not content or not isinstance(content, str):
        raise ValidationError(
            "HTML content must be a non-empty string",
            context="Provide valid HTML markup"
        )

    content = content.strip()
    if not content:
        raise ValidationError(
            "HTML content cannot be empty or whitespace only",
            context="Provide meaningful HTML content"
        )

    # Basic HTML validation
    validator = HTMLValidator()
    try:
        validator.feed(content)
    except Exception as e:
        raise ValidationError(
            f"HTML parsing failed: {e}",
            context="Check for malformed HTML tags or invalid characters"
        )

    errors = validator.validate()
    if errors:
        raise ValidationError(
            f"HTML validation errors: {'; '.join(errors[:3])}{'...' if len(errors) > 3 else ''}",
            context="Fix HTML structure issues before submitting"
        )

    return content


def validate_content_format(content_format: str) -> str:
    """
    Validate content format parameter.

    Args:
        content_format: Content format ('html' or 'lexical')

    Returns:
        Validated content format

    Raises:
        ValidationError: If format is invalid
    """
    if not content_format or not isinstance(content_format, str):
        raise ValidationError(
            "Content format must be specified",
            context="Valid values: 'html' or 'lexical' (recommended)"
        )

    format_lower = content_format.lower().strip()
    if format_lower not in ['html', 'lexical']:
        raise ValidationError(
            f"Invalid content format: '{content_format}'",
            context="Valid values: 'html' or 'lexical' (recommended for rich content)"
        )

    return format_lower


def validate_status(status: str) -> str:
    """
    Validate content status parameter.

    Args:
        status: Content status

    Returns:
        Validated status

    Raises:
        ValidationError: If status is invalid
    """
    if not status or not isinstance(status, str):
        raise ValidationError(
            "Content status must be specified",
            context="Valid values: 'draft', 'published', 'scheduled'"
        )

    status_lower = status.lower().strip()
    valid_statuses = ['draft', 'published', 'scheduled']

    if status_lower not in valid_statuses:
        raise ValidationError(
            f"Invalid content status: '{status}'",
            context=f"Valid values: {', '.join(valid_statuses)}"
        )

    return status_lower


def validate_title(title: str) -> str:
    """
    Validate content title.

    Args:
        title: Content title

    Returns:
        Cleaned title

    Raises:
        ValidationError: If title is invalid
    """
    if not title or not isinstance(title, str):
        raise ValidationError(
            "Title is required",
            context="Provide a descriptive title for your content"
        )

    cleaned_title = title.strip()
    if not cleaned_title:
        raise ValidationError(
            "Title cannot be empty or whitespace only",
            context="Provide a meaningful title for your content"
        )

    if len(cleaned_title) > 255:
        raise ValidationError(
            f"Title too long: {len(cleaned_title)} characters (max: 255)",
            context="Shorten the title to 255 characters or less"
        )

    return cleaned_title


def validate_published_at(published_at: Optional[str]) -> Optional[str]:
    """
    Validate published_at parameter for scheduled posts.

    Args:
        published_at: ISO datetime string or None

    Returns:
        Validated datetime string or None

    Raises:
        ValidationError: If datetime format is invalid
    """
    if published_at is None:
        return None

    if not isinstance(published_at, str):
        raise ValidationError(
            "Published date must be an ISO datetime string",
            context="Example: '2024-01-01T10:00:00.000Z'"
        )

    published_at = published_at.strip()
    if not published_at:
        return None

    # Basic ISO 8601 format validation
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
    if not re.match(iso_pattern, published_at):
        raise ValidationError(
            f"Invalid datetime format: '{published_at}'",
            context="Use ISO 8601 format: '2024-01-01T10:00:00.000Z'"
        )

    return published_at


def validate_content(content: Optional[str], content_format: str) -> Optional[Union[str, Dict[str, Any]]]:
    """
    Validate content based on format.

    Args:
        content: Content string (HTML or Lexical JSON)
        content_format: Content format ('html' or 'lexical')

    Returns:
        Validated content (string for HTML, dict for Lexical)

    Raises:
        ValidationError: If content is invalid
    """
    if content is None:
        return None

    # Validate content format first
    validated_format = validate_content_format(content_format)

    if validated_format == "html":
        return validate_html_content(content)
    elif validated_format == "lexical":
        return validate_lexical_content(content)

    # This should never be reached due to format validation above
    raise ValidationError(
        f"Unsupported content format: {content_format}",
        context="This is an internal error"
    )


def validate_meta_title(meta_title: str) -> str:
    """
    Validate meta title for SEO.

    Args:
        meta_title: Meta title string

    Returns:
        Cleaned meta title

    Raises:
        ValidationError: If meta title is invalid
    """
    if not meta_title or not isinstance(meta_title, str):
        raise ValidationError(
            "Meta title must be a non-empty string",
            context="Provide an SEO-optimized title for search engines"
        )

    cleaned_meta_title = meta_title.strip()
    if not cleaned_meta_title:
        raise ValidationError(
            "Meta title cannot be empty or whitespace only",
            context="Provide a meaningful meta title for SEO"
        )

    if len(cleaned_meta_title) > 300:
        raise ValidationError(
            f"Meta title too long: {len(cleaned_meta_title)} characters (max: 300)",
            context="Keep meta titles under 300 characters for optimal SEO"
        )

    return cleaned_meta_title


def validate_meta_description(meta_description: str) -> str:
    """
    Validate meta description for SEO.

    Args:
        meta_description: Meta description string

    Returns:
        Cleaned meta description

    Raises:
        ValidationError: If meta description is invalid
    """
    if not meta_description or not isinstance(meta_description, str):
        raise ValidationError(
            "Meta description must be a non-empty string",
            context="Provide an SEO-optimized description for search engines"
        )

    cleaned_meta_description = meta_description.strip()
    if not cleaned_meta_description:
        raise ValidationError(
            "Meta description cannot be empty or whitespace only",
            context="Provide a meaningful meta description for SEO"
        )

    if len(cleaned_meta_description) > 500:
        raise ValidationError(
            f"Meta description too long: {len(cleaned_meta_description)} characters (max: 500)",
            context="Keep meta descriptions under 500 characters for optimal SEO"
        )

    return cleaned_meta_description


# Backward compatibility aliases for posts
def validate_post_title(title: str) -> str:
    """Validate post title (backward compatibility alias)."""
    return validate_title(title)


def validate_post_status(status: str) -> str:
    """Validate post status (backward compatibility alias)."""
    return validate_status(status)


def validate_post_content(content: Optional[str], content_format: str) -> Optional[Union[str, Dict[str, Any]]]:
    """Validate post content (backward compatibility alias)."""
    return validate_content(content, content_format)


def get_content_format_examples() -> Dict[str, str]:
    """Get examples of valid content formats."""
    return {
        "lexical_simple": '''{
    "root": {
        "children": [
            {
                "children": [
                    {
                        "detail": 0,
                        "format": 0,
                        "mode": "normal",
                        "style": "",
                        "text": "Hello world!",
                        "type": "text",
                        "version": 1
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "paragraph",
                "version": 1
            }
        ],
        "direction": "ltr",
        "format": "",
        "indent": 0,
        "type": "root",
        "version": 1
    }
}''',
        "lexical_rich": '''{
    "root": {
        "children": [
            {
                "children": [
                    {
                        "detail": 0,
                        "format": 0,
                        "mode": "normal",
                        "style": "",
                        "text": "Rich Content Example",
                        "type": "text",
                        "version": 1
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "heading",
                "version": 1,
                "tag": "h1"
            },
            {
                "children": [
                    {
                        "detail": 0,
                        "format": 0,
                        "mode": "normal",
                        "style": "",
                        "text": "This is a paragraph with a ",
                        "type": "text",
                        "version": 1
                    },
                    {
                        "detail": 0,
                        "format": 0,
                        "mode": "normal",
                        "style": "",
                        "text": "link",
                        "type": "link",
                        "url": "https://example.com",
                        "version": 1
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "paragraph",
                "version": 1
            }
        ],
        "direction": "ltr",
        "format": "",
        "indent": 0,
        "type": "root",
        "version": 1
    }
}''',
        "html_simple": "<p>Hello world!</p>",
        "html_rich": '''<h1>Rich Content Example</h1>
<p>This is a paragraph with <strong>bold text</strong> and a <a href="https://example.com">link</a>.</p>
<ul>
    <li>First item</li>
    <li>Second item</li>
</ul>
<pre><code>code block</code></pre>'''
    }