# Ghost MCP - Docker Development Setup

This guide helps you set up a Ghost instance for Ghost MCP development and API investigation.

## Quick Start

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Start Ghost and MySQL**:
   ```bash
   docker compose up -d
   ```

3. **Access Ghost**:
   - Ghost Admin: http://localhost:2368/ghost
   - Ghost Site: http://localhost:2368
   - phpMyAdmin (optional): http://localhost:8080

## Services

### Ghost (Main Service)
- **Image**: `ghost:5-alpine`
- **Port**: 2368
- **URL**: http://localhost:2368
- **Admin**: http://localhost:2368/ghost

### MySQL Database
- **Image**: `mysql:8.0`
- **Database**: `ghost_dev` (configurable via .env)
- **User**: `ghost` (configurable via .env)

### phpMyAdmin (Optional Debug Tool)
- **Image**: `phpmyadmin/phpmyadmin:latest`
- **Port**: 8080
- **Access**: http://localhost:8080

To start with phpMyAdmin for database debugging:
```bash
docker compose --profile debug up -d
```

## Initial Setup

### 1. First-time Ghost Setup
1. Start the services: `docker compose up -d`
2. Wait for Ghost to initialize (check logs: `docker compose logs ghost`)
3. Visit http://localhost:2368/ghost
4. Create your admin account
5. Complete the Ghost setup wizard

### 2. Obtain API Keys
1. In Ghost Admin, go to Settings → Integrations
2. Click "Add custom integration"
3. Give it a name (e.g., "MCP Development")
4. Copy both API keys:
   - **Content API Key**: For read-only operations
   - **Admin API Key**: For read/write operations

### 3. Update Environment (Optional)
Add the API keys to your `.env` file:
```bash
GHOST_CONTENT_API_KEY=your_content_api_key_here
GHOST_ADMIN_API_KEY=your_admin_api_key_here
```

## API Testing

### Content API (Read-only)
Test the Content API with curl:
```bash
# Get all posts
curl "http://localhost:2368/ghost/api/content/posts/?key=YOUR_CONTENT_API_KEY"

# Get site settings
curl "http://localhost:2368/ghost/api/content/settings/?key=YOUR_CONTENT_API_KEY"
```

### Admin API (Read/Write)
The Admin API requires JWT authentication. You'll need to generate a JWT token using your Admin API key.

## Management Commands

### Start services
```bash
docker compose up -d
```

### Stop services
```bash
docker compose down
```

### View logs
```bash
# All services
docker compose logs

# Ghost only
docker compose logs ghost

# Follow logs
docker compose logs -f ghost
```

### Reset everything (⚠️ Destroys all data)
```bash
docker compose down -v
docker volume rm ghost_mcp_content ghost_mcp_mysql
```

### Backup data
```bash
# Create backup of Ghost content
docker run --rm -v ghost_mcp_content:/data -v $(pwd):/backup alpine tar czf /backup/ghost-content-backup.tar.gz -C /data .

# Create backup of MySQL data
docker run --rm -v ghost_mcp_mysql:/data -v $(pwd):/backup alpine tar czf /backup/mysql-backup.tar.gz -C /data .
```

## Troubleshooting

### Ghost won't start
1. Check if MySQL is healthy: `docker compose ps`
2. Check Ghost logs: `docker compose logs ghost`
3. Verify environment variables in `.env`

### Can't access Ghost admin
1. Ensure Ghost is running: `docker compose ps`
2. Check if port 2368 is available: `netstat -an | grep 2368`
3. Try accessing directly: http://localhost:2368/ghost

### Database connection issues
1. Check MySQL health: `docker compose logs ghost-db`
2. Verify database credentials in `.env`
3. Ensure database has started before Ghost

### API requests failing
1. Verify API keys are correct
2. Check Content API: should work with query parameter
3. Check Admin API: requires proper JWT token generation

## Development Notes

- Ghost data persists in named Docker volumes
- Database is accessible via phpMyAdmin at localhost:8080
- All Ghost content (themes, images, etc.) is stored in the `ghost_content` volume
- MySQL data is stored in the `ghost_mysql` volume
- Environment variables are loaded from `.env` file

## Next Steps

Once Ghost is running, you can:
1. Create test content (posts, pages, tags)
2. Test API endpoints
3. Begin MCP server development
4. Investigate Ghost API authentication flows

For MCP development, see the main project documentation.