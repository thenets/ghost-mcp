# Ghost API Filtering Syntax Documentation

## Overview
Ghost uses NQL (Node Query Language) for filtering API results. This provides powerful querying capabilities for both Content and Admin APIs.

## Basic Syntax

### Property-Operator-Value Format
```
property:operator value
```

### Simple Examples
```
status:published          # Posts with published status
featured:true             # Featured posts only
slug:welcome              # Post with slug "welcome"
tag:news                  # Posts tagged with "news"
```

## Operators

### 1. Equality (Default)
**Operator**: `:` (colon)
**Usage**: Exact match
```
status:published
featured:true
author:john-doe
```

### 2. Negation
**Operator**: `-` (minus prefix)
**Usage**: NOT equal to
```
-status:draft             # Not draft posts
-featured:true            # Non-featured posts
-tag:internal             # Posts not tagged "internal"
```

### 3. Comparison Operators
**Operators**: `>`, `>=`, `<`, `<=`
**Usage**: Numeric and date comparisons
```
published_at:>2023-01-01  # Posts published after date
read_time:>5              # Posts with reading time > 5 minutes
published_at:<=now-7d     # Posts published within last 7 days
```

### 4. Text Matching
**Operators**: `~`, `~^`, `~$`
**Usage**: Partial text matching
```
title:~ghost              # Title contains "ghost"
slug:~^getting-started    # Slug starts with "getting-started"
excerpt:~$tutorial        # Excerpt ends with "tutorial"
```

### 5. Group Selection
**Operator**: `[value1, value2, ...]`
**Usage**: Match any value in the list
```
tag:[news,updates,blog]   # Posts with any of these tags
author:[john,jane,bob]    # Posts by any of these authors
status:[published,draft]  # Published or draft posts
```

## Value Types

### 1. Null Values
```
feature_image:null        # Posts without feature image
custom_excerpt:-null      # Posts with custom excerpt (not null)
```

### 2. Boolean Values
```
featured:true
featured:false
page:true                 # Only pages
page:false                # Only posts
```

### 3. Numbers
```
read_time:>10
read_time:<=5
comment_count:0
```

### 4. Literal Strings
**Format**: No quotes needed for simple strings
```
status:published
tag:javascript
author:john-doe
```

### 5. Quoted Strings
**Format**: Single quotes for strings with special characters
```
title:'My Post Title'
tag:'getting started'
excerpt:'This is a long excerpt with spaces'
```

### 6. Relative Dates
**Format**: `now`, `now-Xd` (days), `now-Xm` (months), `now-Xy` (years)
```
published_at:>now-30d     # Last 30 days
created_at:<=now-1y       # More than 1 year old
updated_at:>now-7d        # Updated in last week
```

## Combination Logic

### 1. AND Operator
**Operator**: `+`
**Usage**: All conditions must be true
```
status:published+featured:true
tag:news+published_at:>now-7d
author:john+status:published+featured:true
```

### 2. OR Operator
**Operator**: `,` (comma)
**Usage**: Any condition can be true
```
status:published,status:draft
tag:news,tag:updates
author:john,author:jane
```

### 3. Precedence Control
**Operator**: `()` (parentheses)
**Usage**: Group conditions and control evaluation order
```
(tag:news,tag:updates)+status:published
author:john+(status:published,status:draft)
```

## Complex Filter Examples

### 1. Recent Featured Posts by Specific Authors
```
authors.slug:[john,jane]+featured:true+published_at:>now-30d
```

### 2. Published Content with Specific Tags, Excluding Drafts
```
tag:[tutorial,guide]+status:published+-status:draft
```

### 3. Posts with Reading Time Between 5-15 Minutes
```
read_time:>=5+read_time:<=15+status:published
```

### 4. Recent Posts with Feature Images
```
published_at:>now-7d+feature_image:-null+status:published
```

### 5. Pages or Featured Posts by Multiple Authors
```
(page:true,featured:true)+authors.slug:[admin,editor,writer]
```

## Field-Specific Filters

### Posts/Pages
```
id:5f7c1b4b0c7b4b001f7b4b1c
slug:my-post-slug
title:~'How to'
html:~'tutorial'
plaintext:~'javascript'
feature_image:null
featured:true
page:false
status:published
visibility:public
created_at:>now-30d
published_at:<=2023-12-31
updated_at:>now-7d
```

### Tags
```
id:tag_id
name:'JavaScript'
slug:javascript
description:~'programming'
visibility:public
```

### Authors
```
id:author_id
name:'John Doe'
slug:john-doe
email:john@example.com
```

### Relationships (Dot Notation)
```
authors.slug:john-doe
authors.name:'John Doe'
tags.slug:javascript
tags.name:'JavaScript'
primary_author.slug:admin
primary_tag.slug:featured
```

## URL Encoding

### Required Encoding
Filter strings must be URL encoded when used in URLs:
```javascript
const filter = "tag:javascript+published_at:>now-7d";
const encoded = encodeURIComponent(filter);
// Result: tag%3Ajavascript%2Bpublished_at%3A%3Enow-7d
```

### Common Encodings
```
:  → %3A
+  → %2B
,  → %2C
>  → %3E
<  → %3C
~  → %7E
[  → %5B
]  → %5D
'  → %27
```

## Limitations & Constraints

### 1. Property Naming
- Properties must start with a letter
- Use dot notation for relationships
- Case-sensitive property names

### 2. Value Constraints
- No regex or advanced pattern matching
- Limited to defined operators
- String values with special chars need quotes

### 3. Performance Considerations
- Complex filters may impact query performance
- Index-based fields filter faster
- Limit filter complexity for optimal response times

### 4. API Limitations
- Some fields may not be filterable
- Admin API may have different filter availability than Content API
- Check specific endpoint documentation for filter support

## Implementation for MCP Server

### Filter Builder Class
```javascript
class GhostFilterBuilder {
  constructor() {
    this.conditions = [];
  }

  equals(property, value) {
    this.conditions.push(`${property}:${this.formatValue(value)}`);
    return this;
  }

  notEquals(property, value) {
    this.conditions.push(`-${property}:${this.formatValue(value)}`);
    return this;
  }

  greaterThan(property, value) {
    this.conditions.push(`${property}:>${this.formatValue(value)}`);
    return this;
  }

  contains(property, value) {
    this.conditions.push(`${property}:~${this.formatValue(value)}`);
    return this;
  }

  inArray(property, values) {
    const formatted = values.map(v => this.formatValue(v)).join(',');
    this.conditions.push(`${property}:[${formatted}]`);
    return this;
  }

  formatValue(value) {
    if (value === null) return 'null';
    if (typeof value === 'boolean') return value.toString();
    if (typeof value === 'number') return value.toString();
    if (typeof value === 'string' && /^[a-zA-Z0-9\-_]+$/.test(value)) {
      return value; // Simple string, no quotes needed
    }
    return `'${value}'`; // Complex string, needs quotes
  }

  and() {
    // Next condition will be ANDed
    this.operator = '+';
    return this;
  }

  or() {
    // Next condition will be ORed
    this.operator = ',';
    return this;
  }

  build() {
    return this.conditions.join(this.operator || '+');
  }

  buildEncoded() {
    return encodeURIComponent(this.build());
  }
}

// Usage example
const filter = new GhostFilterBuilder()
  .equals('status', 'published')
  .and()
  .equals('featured', true)
  .and()
  .greaterThan('published_at', 'now-30d')
  .build();
// Result: status:published+featured:true+published_at:>now-30d
```

## Phase Implementation Strategy

### Phase 1: Basic Filters (Current)
```javascript
// Simple equality filters
status:published
featured:true
tag:news
author:john-doe
```

### Phase 2: Advanced Filters (Future)
```javascript
// Complex filters with operators
published_at:>now-30d+featured:true
authors.slug:[john,jane]+tag:[news,updates]
title:~'tutorial'+read_time:>=5
```

### Phase 3: Filter Builder (Future)
- Programmatic filter construction
- Validation and sanitization
- Advanced query optimization

## Testing Strategy

### Unit Tests
```javascript
describe('Ghost Filter Syntax', () => {
  test('simple equality filter', () => {
    expect(buildFilter('status', 'published')).toBe('status:published');
  });

  test('complex AND filter', () => {
    const filter = 'status:published+featured:true';
    expect(parseFilter(filter)).toMatchObject({
      conditions: [
        { property: 'status', operator: ':', value: 'published' },
        { property: 'featured', operator: ':', value: 'true' }
      ]
    });
  });
});
```

### Integration Tests
```javascript
test('filter with real API', async () => {
  const response = await contentApi.request('/posts/', {
    filter: 'status:published+featured:true',
    limit: 5
  });
  expect(response.posts.every(post =>
    post.status === 'published' && post.featured === true
  )).toBe(true);
});
```

## Implementation Status
- ✅ Filter syntax documented
- ✅ Operators and examples identified
- ✅ Implementation strategy planned
- ✅ Phase 1 vs Phase 2 filters defined
- ⏳ Filter builder implementation pending
- ⏳ Real API testing pending API keys