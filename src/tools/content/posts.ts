/**
 * Ghost Content API - Posts Tools
 *
 * MCP tools for read-only access to Ghost posts via Content API.
 * Implements tools: ghost_list_posts, ghost_get_post_by_id, ghost_get_post_by_slug
 */

// TODO: Phase 2 - Implement Content API posts tools
// - ghost_list_posts
// - ghost_get_post_by_id
// - ghost_get_post_by_slug

export const postsContentTools = [
  {
    name: 'ghost_list_posts',
    description: 'List all published posts from Ghost Content API',
    inputSchema: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: 'Number of posts to return (max 50)' },
        page: { type: 'number', description: 'Page number for pagination' },
        filter: { type: 'string', description: 'Filter posts using Ghost filter syntax' },
        include: { type: 'string', description: 'Include related resources (tags,authors)' },
        fields: { type: 'string', description: 'Comma-separated list of fields to return' },
      },
    },
  },
  // TODO: Phase 2 - Add other posts tools
];

// TODO: Phase 2 - Implement tool handlers