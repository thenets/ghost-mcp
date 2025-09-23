# Ghost Content Formats Documentation

## Overview
Ghost supports multiple content formats for creating and managing posts and pages. Understanding these formats is crucial for proper MCP tool implementation.

## Content Format Evolution

### Historical Context
1. **Mobiledoc** (Legacy): Ghost's previous JSON-based content format
2. **HTML**: Traditional markup format
3. **Lexical** (Current): Ghost's current standardized JSON content format

## Current Content Formats

### 1. Lexical Format (Primary)
**Status**: Current standard format
**Type**: JSON-based structured content
**Usage**: Default format for all new content

#### Structure
```json
{
  "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Welcome to Ghost!\",\"type\":\"text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}"
}
```

#### Benefits
- Rich content representation
- Structured, parseable format
- Supports complex layouts and content blocks
- Platform-agnostic content storage

### 2. HTML Format (Optional)
**Status**: Available for output/input
**Type**: Rendered HTML markup
**Usage**: For compatibility and direct HTML input

#### Structure
```json
{
  "html": "<p>Welcome to Ghost!</p><p>This is a simple HTML paragraph.</p>"
}
```

#### Use Cases
- Content migration from HTML-based systems
- Direct HTML content creation
- Output for web rendering

### 3. Mobiledoc Format (Legacy)
**Status**: Legacy support (deprecated)
**Type**: JSON-based (older format)
**Usage**: Existing content only

**Note**: New content should use Lexical format. Mobiledoc is maintained for backward compatibility.

## API Content Handling

### Content Retrieval

#### Default Behavior
- API returns Lexical format by default
- HTML format requires explicit request

#### Format Selection
```javascript
// Get only Lexical (default)
GET /ghost/api/content/posts/

// Get both Lexical and HTML
GET /ghost/api/content/posts/?formats=html,lexical

// Get only HTML
GET /ghost/api/content/posts/?formats=html
```

#### Response Examples

**Lexical Only (Default)**:
```json
{
  "posts": [
    {
      "id": "post_id",
      "title": "My Post",
      "lexical": "{\"root\":{...}}",
      "slug": "my-post"
    }
  ]
}
```

**HTML and Lexical**:
```json
{
  "posts": [
    {
      "id": "post_id",
      "title": "My Post",
      "lexical": "{\"root\":{...}}",
      "html": "<p>Post content</p>",
      "slug": "my-post"
    }
  ]
}
```

### Content Creation & Updates

#### Admin API Content Fields
```javascript
// Creating a post with Lexical
const postData = {
  posts: [{
    title: "New Post",
    lexical: JSON.stringify(lexicalContent),
    status: "draft"
  }]
};

// Creating a post with HTML
const postData = {
  posts: [{
    title: "New Post",
    html: "<p>HTML content here</p>",
    status: "draft"
  }]
};

// Creating with both (Lexical takes precedence)
const postData = {
  posts: [{
    title: "New Post",
    lexical: JSON.stringify(lexicalContent),
    html: "<p>Fallback HTML</p>",
    status: "draft"
  }]
};
```

## Content Format Priorities

### Create/Update Priority Order
1. **Lexical** (highest priority)
2. **HTML** (fallback if no Lexical)
3. **Mobiledoc** (legacy fallback)

### Conversion Behavior
- HTML → Lexical: Ghost converts HTML to Lexical automatically
- Lexical → HTML: Ghost renders Lexical to HTML
- Mobiledoc → Lexical: Ghost migrates existing Mobiledoc content

## Implementation for MCP Server

### Content Format Detection
```javascript
class GhostContentHandler {
  detectContentFormat(content) {
    if (typeof content === 'object' && content.root) {
      return 'lexical';
    }
    if (typeof content === 'string' && content.startsWith('<')) {
      return 'html';
    }
    if (typeof content === 'object' && content.version) {
      return 'mobiledoc';
    }
    return 'unknown';
  }

  prepareContentForAPI(content, preferredFormat = 'lexical') {
    const format = this.detectContentFormat(content);

    switch (format) {
      case 'lexical':
        return {
          lexical: typeof content === 'string' ? content : JSON.stringify(content)
        };
      case 'html':
        return {
          html: content
        };
      case 'mobiledoc':
        return {
          mobiledoc: typeof content === 'string' ? content : JSON.stringify(content)
        };
      default:
        // Assume plain text, wrap in HTML
        return {
          html: `<p>${content}</p>`
        };
    }
  }
}
```

### MCP Tool Content Parameters

#### Create Post Tool
```javascript
const createPostTool = {
  name: "ghost_admin_create_post",
  parameters: {
    title: { type: "string", required: true },

    // Content format options (one required)
    lexical: { type: "string", description: "Lexical JSON content" },
    html: { type: "string", description: "HTML content" },
    mobiledoc: { type: "string", description: "Mobiledoc JSON content (legacy)" },

    // Other parameters...
    status: { type: "string", enum: ["draft", "published"] }
  }
};
```

#### Content Validation
```javascript
function validateContentInput(params) {
  const contentFormats = ['lexical', 'html', 'mobiledoc'].filter(
    format => params[format] !== undefined
  );

  if (contentFormats.length === 0) {
    throw new Error('At least one content format (lexical, html, or mobiledoc) is required');
  }

  if (contentFormats.length > 1) {
    console.warn('Multiple content formats provided. Lexical will take precedence.');
  }

  // Validate Lexical JSON if provided
  if (params.lexical) {
    try {
      JSON.parse(params.lexical);
    } catch (error) {
      throw new Error('Invalid Lexical JSON format');
    }
  }

  return true;
}
```

## Content Format Examples

### 1. Simple Lexical Content
```json
{
  "root": {
    "children": [
      {
        "children": [
          {
            "detail": 0,
            "format": 0,
            "mode": "normal",
            "style": "",
            "text": "Hello World!",
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
}
```

### 2. Rich HTML Content
```html
<h1>My Blog Post</h1>
<p>This is a <strong>rich</strong> HTML post with <em>formatting</em>.</p>
<ul>
  <li>First item</li>
  <li>Second item</li>
</ul>
<blockquote>
  <p>This is a quote block.</p>
</blockquote>
```

### 3. Content Conversion Utility
```javascript
class ContentConverter {
  // Convert HTML to simple Lexical
  htmlToLexical(html) {
    // Basic implementation - in practice, use Ghost's conversion utilities
    const paragraphs = html.split('</p>').filter(p => p.trim());
    const children = paragraphs.map(p => {
      const text = p.replace(/<[^>]*>/g, '').trim();
      return {
        children: [{
          detail: 0,
          format: 0,
          mode: "normal",
          style: "",
          text: text,
          type: "text",
          version: 1
        }],
        direction: "ltr",
        format: "",
        indent: 0,
        type: "paragraph",
        version: 1
      };
    });

    return {
      root: {
        children: children,
        direction: "ltr",
        format: "",
        indent: 0,
        type: "root",
        version: 1
      }
    };
  }

  // Convert Lexical to simple HTML
  lexicalToHtml(lexical) {
    const content = typeof lexical === 'string' ? JSON.parse(lexical) : lexical;
    const paragraphs = content.root.children.map(child => {
      if (child.type === 'paragraph') {
        const text = child.children.map(textNode => textNode.text).join('');
        return `<p>${text}</p>`;
      }
      return '';
    });
    return paragraphs.join('\n');
  }
}
```

## Best Practices

### For MCP Implementation
1. **Default to Lexical**: Use Lexical format for new content creation
2. **Support HTML Input**: Allow HTML for ease of use and migration
3. **Validate JSON**: Always validate Lexical JSON before sending to API
4. **Handle Conversion**: Provide utilities for format conversion if needed
5. **Graceful Fallback**: Handle legacy Mobiledoc content gracefully

### Content Creation Guidelines
1. **Use Lexical for Rich Content**: Complex layouts, cards, embeds
2. **Use HTML for Simple Content**: Basic text formatting
3. **Provide Format Options**: Let users choose their preferred input format
4. **Validate Before Submission**: Check content validity before API calls

## Implementation Status
- ✅ Content formats identified and documented
- ✅ API handling patterns documented
- ✅ Implementation strategy planned
- ✅ Validation approaches defined
- ⏳ Content conversion utilities pending implementation
- ⏳ Real format testing pending API access