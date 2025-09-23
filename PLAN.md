# Ghost MCP Implementation Plan

This document outlines the comprehensive implementation plan for the Ghost MCP server, distributed across multiple phases with research steps and clear success criteria.

## Overview

The Ghost MCP server will provide complete Ghost CMS functionality through the Model Context Protocol, supporting both read (Content API) and write (Admin API) operations with 44+ tools covering all Ghost REST API endpoints.

## Phase Distribution

- **Phase 0**: Research & Setup (1-2 days)
- **Phase 1**: Core Infrastructure (2-3 days)
- **Phase 2**: Content API Implementation (2-3 days)
- **Phase 3**: Admin API Core (3-4 days)
- **Phase 4**: Advanced Admin Features (3-4 days)
- **Phase 5**: Advanced Features (Stubs) (2-3 days)
- **Phase 6**: Testing & Documentation (2-3 days)

**Total Estimated Time**: 15-22 days

---

## Phase 0: Research & Setup

### Objectives
- Deep research into Ghost API authentication and patterns
- Set up development environment with Ghost instance
- Create project scaffolding and initial configuration

### Tasks

#### 0.1 Ghost API Research
- **Task**: Research Ghost Admin API JWT authentication flow
  - Investigate JWT token generation process
  - Document authentication headers and token refresh
  - Test Admin API endpoints with different authentication methods
- **Task**: Research Ghost Content API authentication
  - Document query parameter authentication
  - Test rate limiting and caching behavior
- **Task**: Research Ghost API error response formats
  - Document all possible error codes and formats
  - Map Ghost errors to appropriate MCP error responses
- **Task**: Research Ghost filtering syntax
  - Document basic and advanced filtering options
  - Test filter combinations and edge cases
  - Plan Phase 1 vs Phase 2 filtering implementation

#### 0.2 Development Environment Setup
- **Task**: Create Docker Compose setup
  - Set up Ghost with MySQL
  - Create admin account and obtain API keys
  - Test both Content and Admin API access
- **Task**: Initialize Node.js project
  - Set up TypeScript configuration
  - Install core dependencies (@modelcontextprotocol/sdk, axios, etc.)
  - Configure development tools (eslint, prettier, etc.)

#### 0.3 Project Scaffolding
- **Task**: Create project structure according to SPEC.md
  - Set up directory structure (src/tools/content, src/tools/admin, etc.)
  - Create placeholder files for all major components
  - Set up package.json with all required dependencies

### Research Questions to Answer
1. How exactly does Ghost Admin API JWT authentication work?
2. What are the specific error response formats for different failure scenarios?
3. What are the rate limits and best practices for Ghost API usage?
4. How does Ghost handle concurrent requests and connection pooling?
5. What are the exact file upload requirements and limitations?

### Success Criteria
- [ ] Local Ghost instance running and accessible
- [ ] Both Content and Admin API keys obtained and tested
- [ ] Project structure created with all placeholder files
- [ ] All dependencies installed and TypeScript compiling
- [ ] Research documentation completed for authentication flows
- [ ] Clear understanding of Ghost API error handling

### Dependencies
- Docker and Docker Compose installed
- Node.js v18+ installed
- Access to Ghost documentation

---

## Phase 1: Core Infrastructure

### Objectives
- Implement configuration system with precedence (env vars → .env → defaults)
- Set up authentication for both Content and Admin APIs
- Implement comprehensive logging system
- Create error handling infrastructure

### Tasks

#### 1.1 Configuration System
- **Task**: Implement configuration loading with precedence
  - Create config loader that reads .env file first, then environment variables
  - Implement validation for required vs optional configuration
  - Add support for operation modes (readonly, readwrite, auto)
- **Task**: Create configuration types and validation
  - Define TypeScript interfaces for all configuration options
  - Implement Zod schemas for runtime validation
  - Add configuration validation on startup

#### 1.2 Authentication Infrastructure
- **Task**: Implement Content API authentication
  - Create Content API client with query parameter authentication
  - Add automatic retry logic for authentication failures
- **Task**: Implement Admin API JWT authentication
  - Research and implement JWT token generation
  - Create token refresh mechanism
  - Handle token expiration gracefully
- **Task**: Create unified Ghost client
  - Abstract both Content and Admin API access
  - Implement automatic API selection based on operation and available keys
  - Add connection pooling and request optimization

#### 1.3 Logging System
- **Task**: Set up structured logging
  - Configure Winston or Pino for structured JSON logging
  - Implement log levels (DEBUG, INFO, WARN, ERROR)
  - Create log formatters with required fields (timestamp, tool_name, operation, etc.)
- **Task**: Add request ID tracking
  - Generate unique request IDs for all operations
  - Thread request IDs through all log messages
  - Add request/response logging for Ghost API calls

#### 1.4 Error Handling Infrastructure
- **Task**: Create comprehensive error types
  - Define error classes for all error categories (network, auth, API, MCP, file upload)
  - Map Ghost API errors to appropriate MCP error responses
  - Implement error serialization for logging
- **Task**: Implement retry logic
  - Add exponential backoff for transient errors
  - Respect rate limit headers from Ghost API
  - Implement authentication retry after token refresh

### Success Criteria
- [ ] Configuration loads correctly with proper precedence
- [ ] Content API authentication working
- [ ] Admin API JWT authentication working with refresh
- [ ] Structured logging implemented with all required fields
- [ ] Error handling catches and logs all error categories
- [ ] Request ID tracking working end-to-end
- [ ] Retry logic implemented and tested

### Dependencies
- Phase 0 completed
- Ghost instance accessible with API keys

---

## Phase 2: Content API Implementation

### Objectives
- Implement all 13 Content API MCP tools for read-only access
- Add comprehensive parameter validation and filtering
- Implement pagination support

### Tasks

#### 2.1 Content API Tools - Posts
- **Task**: Implement `ghost_list_posts`
  - Add parameter validation (limit, page, filter, include, fields)
  - Implement basic filtering support
  - Add pagination metadata handling
- **Task**: Implement `ghost_get_post_by_id`
  - Add ID validation and error handling
  - Support include and fields parameters
- **Task**: Implement `ghost_get_post_by_slug`
  - Add slug validation and URL encoding
  - Handle not found scenarios

#### 2.2 Content API Tools - Pages
- **Task**: Implement `ghost_list_pages`
- **Task**: Implement `ghost_get_page_by_id`
- **Task**: Implement `ghost_get_page_by_slug`

#### 2.3 Content API Tools - Tags
- **Task**: Implement `ghost_list_tags`
- **Task**: Implement `ghost_get_tag_by_id`
- **Task**: Implement `ghost_get_tag_by_slug`

#### 2.4 Content API Tools - Authors
- **Task**: Implement `ghost_list_authors`
- **Task**: Implement `ghost_get_author_by_id`
- **Task**: Implement `ghost_get_author_by_slug`

#### 2.5 Content API Tools - Other
- **Task**: Implement `ghost_list_tiers`
- **Task**: Implement `ghost_get_settings`

#### 2.6 Parameter Validation & Utilities
- **Task**: Create Zod schemas for all Content API parameters
- **Task**: Implement parameter validation middleware
- **Task**: Add response formatting utilities
- **Task**: Create filtering helper functions (Phase 1 basic filters)

### Success Criteria
- [ ] All 13 Content API tools implemented and functional
- [ ] Parameter validation working for all tools
- [ ] Basic filtering working (featured:true, status:published, etc.)
- [ ] Pagination working with proper metadata
- [ ] Include and fields parameters working
- [ ] Error handling working for all error scenarios
- [ ] Comprehensive logging for all operations

### Dependencies
- Phase 1 completed
- Content API authentication working

---

## Phase 3: Admin API Core

### Objectives
- Implement core Admin API CRUD operations for posts, pages, and tags
- Add create, update, copy, and delete functionality
- Implement proper Admin API authentication and error handling

### Tasks

#### 3.1 Admin API Tools - Posts
- **Task**: Implement `ghost_admin_list_posts`
  - Support draft and published post filtering
  - Add Admin API specific parameters
- **Task**: Implement `ghost_admin_get_post`
- **Task**: Implement `ghost_admin_create_post`
  - Add comprehensive parameter validation for post creation
  - Handle mobiledoc, lexical, and HTML content formats
  - Support tag and author associations
- **Task**: Implement `ghost_admin_update_post`
  - Add updated_at requirement for conflict resolution
  - Support partial updates
- **Task**: Implement `ghost_admin_copy_post`
- **Task**: Implement `ghost_admin_delete_post`

#### 3.2 Admin API Tools - Pages
- **Task**: Implement `ghost_admin_list_pages`
- **Task**: Implement `ghost_admin_get_page`
- **Task**: Implement `ghost_admin_create_page`
- **Task**: Implement `ghost_admin_update_page`
- **Task**: Implement `ghost_admin_copy_page`
- **Task**: Implement `ghost_admin_delete_page`

#### 3.3 Admin API Tools - Tags
- **Task**: Implement `ghost_admin_list_tags`
- **Task**: Implement `ghost_admin_get_tag`
- **Task**: Implement `ghost_admin_create_tag`
- **Task**: Implement `ghost_admin_update_tag`
- **Task**: Implement `ghost_admin_delete_tag`

#### 3.4 Admin API Infrastructure
- **Task**: Research and implement proper content creation workflows
  - Understand Ghost's content format requirements
  - Test different content input formats (HTML, Markdown, Lexical)
  - Implement content validation
- **Task**: Add Admin API specific error handling
  - Handle permission errors
  - Handle resource conflicts (updated_at mismatches)
  - Handle validation errors from Ghost

### Research Areas
1. What are the exact requirements for Ghost content creation?
2. How does Ghost handle different content formats (HTML vs Lexical vs Mobiledoc)?
3. What validation does Ghost perform on create/update operations?
4. How should we handle resource relationships (posts ↔ tags, posts ↔ authors)?

### Success Criteria
- [ ] All core CRUD operations working for posts, pages, tags
- [ ] Content creation working with proper validation
- [ ] Update operations handling conflicts correctly
- [ ] Delete operations working with proper confirmation
- [ ] Copy operations creating proper duplicates
- [ ] Admin API authentication working reliably
- [ ] Comprehensive error handling for all Admin API scenarios

### Dependencies
- Phase 2 completed
- Admin API authentication working

---

## Phase 4: Advanced Admin Features

### Objectives
- Implement member management tools
- Add media upload functionality
- Implement tiers and webhook management
- Add advanced content features

### Tasks

#### 4.1 Member Management
- **Task**: Implement `ghost_admin_list_members`
- **Task**: Implement `ghost_admin_get_member`
- **Task**: Implement `ghost_admin_create_member`
- **Task**: Implement `ghost_admin_update_member`

#### 4.2 Media Management
- **Task**: Research Ghost media upload requirements
  - Understand file format requirements and size limits
  - Test image and media upload processes
  - Document upload response formats
- **Task**: Implement `ghost_admin_upload_image`
  - Add file validation (size, format)
  - Handle base64 and file input
  - Add upload progress if applicable
- **Task**: Implement `ghost_admin_upload_media`

#### 4.3 Tiers Management
- **Task**: Implement `ghost_admin_list_tiers`
- **Task**: Implement `ghost_admin_get_tier`
- **Task**: Implement `ghost_admin_create_tier`
- **Task**: Implement `ghost_admin_update_tier`

#### 4.4 Webhook Management
- **Task**: Implement `ghost_admin_list_webhooks`
- **Task**: Implement `ghost_admin_create_webhook`
- **Task**: Implement `ghost_admin_update_webhook`
- **Task**: Implement `ghost_admin_delete_webhook`

#### 4.5 Theme Management
- **Task**: Research Ghost theme upload process
  - Understand theme package requirements
  - Test theme upload and activation
- **Task**: Implement `ghost_admin_upload_theme`
- **Task**: Implement `ghost_admin_activate_theme`

### Research Areas
1. What are Ghost's exact file upload requirements and limitations?
2. How does Ghost handle theme uploads and validation?
3. What are the webhook event types and payload formats?
4. How do tier pricing and currency settings work?

### Success Criteria
- [ ] Member CRUD operations working
- [ ] Image and media uploads working
- [ ] Tier management working with pricing
- [ ] Webhook management working
- [ ] Theme upload and activation working
- [ ] File validation preventing invalid uploads
- [ ] Progress tracking for large uploads

### Dependencies
- Phase 3 completed
- File upload research completed

---

## Phase 5: Advanced Features (Stubs)

### Objectives
- Implement stub versions of advanced features
- Create extensible architecture for future enhancement
- Provide basic functionality for complex operations

### Tasks

#### 5.1 Content Search (Stub)
- **Task**: Implement `ghost_admin_search_content`
  - Create basic pass-through to Ghost API search
  - Add parameter validation for search queries
  - Format results consistently

#### 5.2 Bulk Operations (Stub)
- **Task**: Implement `ghost_admin_bulk_operation`
  - Create framework for bulk operations
  - Implement basic bulk delete as proof of concept
  - Add operation validation and safety checks

#### 5.3 Analytics (Stub)
- **Task**: Research Ghost analytics capabilities
  - Investigate what analytics data Ghost API provides
  - Test analytics endpoints if available
- **Task**: Implement `ghost_admin_site_analytics`
  - Create stub that returns available analytics
  - Add parameter validation for date ranges and metrics

#### 5.4 Import/Export (Stub)
- **Task**: Research Ghost import/export formats
  - Understand Ghost export file formats
  - Test import/export API endpoints
- **Task**: Implement `ghost_admin_export_content`
- **Task**: Implement `ghost_admin_import_content`

#### 5.5 Stub Architecture
- **Task**: Create extensible stub framework
  - Design pattern for upgrading stubs to full implementations
  - Add logging for stub usage
  - Create documentation for future enhancement

### Success Criteria
- [ ] All 5 advanced feature stubs implemented
- [ ] Stubs provide basic functionality
- [ ] Clear upgrade path documented for each stub
- [ ] Analytics working if Ghost provides data
- [ ] Import/export working with basic formats
- [ ] Search providing usable results

### Dependencies
- Phase 4 completed
- Research into Ghost advanced capabilities completed

---

## Phase 6: Testing & Documentation

### Objectives
- Comprehensive testing of all functionality
- Create thorough documentation
- Prepare for deployment and distribution

### Tasks

#### 6.1 Testing Infrastructure
- **Task**: Set up testing framework
  - Configure Jest or similar testing framework
  - Set up test Ghost instance with sample data
  - Create test utilities and helpers
- **Task**: Unit testing
  - Test all individual tools
  - Test authentication flows
  - Test error handling scenarios
  - Test parameter validation
- **Task**: Integration testing
  - Test end-to-end workflows
  - Test with real Ghost instance
  - Test all API combinations

#### 6.2 Error Scenario Testing
- **Task**: Test all error scenarios
  - Network failures
  - Authentication failures
  - Invalid parameters
  - Rate limiting
  - Ghost API errors
- **Task**: Test configuration scenarios
  - Different operation modes
  - Missing API keys
  - Invalid configuration

#### 6.3 Documentation
- **Task**: Create comprehensive README
  - Installation instructions
  - Configuration guide
  - Usage examples
  - Troubleshooting guide
- **Task**: Create API documentation
  - Document all 44+ MCP tools
  - Provide examples for each tool
  - Document error responses
- **Task**: Create development guide
  - How to extend functionality
  - How to upgrade stubs
  - Architecture overview

#### 6.4 Performance & Optimization
- **Task**: Performance testing
  - Test with large datasets
  - Test concurrent operations
  - Test memory usage
- **Task**: Optimization
  - Optimize API calls
  - Implement caching where appropriate
  - Optimize error handling paths

#### 6.5 Deployment Preparation
- **Task**: Create deployment scripts
- **Task**: Create Docker image (optional)
- **Task**: Create release package
- **Task**: Create security audit checklist

### Success Criteria
- [ ] 95%+ test coverage
- [ ] All error scenarios tested
- [ ] Comprehensive documentation
- [ ] Performance benchmarks established
- [ ] Ready for production deployment
- [ ] Security review completed

### Dependencies
- All previous phases completed

---

## Risk Mitigation

### Technical Risks
1. **Ghost API changes**: Monitor Ghost releases and maintain compatibility
2. **Authentication complexity**: Thorough research in Phase 0
3. **File upload limitations**: Research and test early in Phase 4
4. **Performance issues**: Regular testing throughout development

### Schedule Risks
1. **Research taking longer**: Buffer time allocated in each phase
2. **Complex integrations**: Stub approach allows for iterative improvement
3. **Testing revealing issues**: Continuous testing throughout phases

### Quality Risks
1. **Incomplete error handling**: Comprehensive error testing in Phase 6
2. **Security vulnerabilities**: Security review in final phase
3. **Poor performance**: Performance testing integrated throughout

---

## Success Metrics

### Functionality
- [ ] All 44+ MCP tools implemented and working
- [ ] Both Content and Admin API operations functional
- [ ] Complete error handling coverage
- [ ] Comprehensive logging implemented

### Quality
- [ ] 95%+ test coverage
- [ ] All error scenarios handled gracefully
- [ ] Performance meets requirements
- [ ] Security audit passed

### Documentation
- [ ] Complete API documentation
- [ ] Installation and usage guides
- [ ] Development and extension guides
- [ ] Troubleshooting documentation

### Deployment Readiness
- [ ] Package ready for distribution
- [ ] Docker image available (optional)
- [ ] Configuration examples provided
- [ ] Production deployment tested

---

## Phase Dependencies

```
Phase 0 (Research & Setup)
    ↓
Phase 1 (Core Infrastructure)
    ↓
Phase 2 (Content API) ←→ Phase 3 (Admin API Core)
    ↓                        ↓
Phase 4 (Advanced Admin Features)
    ↓
Phase 5 (Advanced Features - Stubs)
    ↓
Phase 6 (Testing & Documentation)
```

**Note**: Phases 2 and 3 can be developed in parallel after Phase 1 is complete, as they use different authentication methods and API endpoints.