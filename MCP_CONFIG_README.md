# MCP Configuration Guide

## Overview

The `mcp-config.json` file provides a comprehensive configuration for connecting to Flowstate-AI services using the Model Context Protocol (MCP). This file demonstrates all three MCP connection types with clear examples and documentation.

## Connection Types

### 1. STDIO (Standard Input/Output)
**Best for:** Local development, CLI tools, desktop applications

**Examples in config:**
- `flowstate-backend-stdio` - Backend API via subprocess
- `flowstate-python-worker-stdio` - Python AI worker via subprocess

**How it works:** Launches an MCP server as a child process and communicates through stdin/stdout streams.

**Setup:**
```bash
# Update the command and args to point to your MCP server
{
  "type": "stdio",
  "command": "node",
  "args": ["/path/to/your/mcp-server.js"]
}
```

### 2. SSE (Server-Sent Events)
**Best for:** Real-time updates, live dashboards, event streams

**Examples in config:**
- `flowstate-backend-sse` - Real-time customer events and updates
- `flowstate-python-worker-sse` - Live AI recommendations
- `flowstate-godmode-sse` - AI agent status streaming

**How it works:** Maintains a persistent HTTP connection where the server pushes updates to clients in real-time.

**Setup:**
```bash
# Configure the SSE endpoint URL
{
  "type": "sse",
  "url": "http://localhost:3001/mcp/sse",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  }
}
```

### 3. HTTP (REST API)
**Best for:** Standard web services, microservices, production APIs

**Examples in config:**
- `flowstate-backend-http` - Full REST API access
- `flowstate-python-worker-http` - AI service REST API
- `flowstate-godmode-http` - GODMODE dashboard API
- `production-backend-http` - Production HTTPS example

**How it works:** Traditional request/response pattern using REST endpoints.

**Setup:**
```bash
# Configure the base URL and endpoints
{
  "type": "http",
  "baseUrl": "http://localhost:3001/api",
  "endpoints": {
    "customers": "/customers",
    "interactions": "/interactions"
  }
}
```

## Quick Start

### 1. Replace Placeholders

The configuration file contains several placeholders that you need to replace:

**Authentication tokens:**
- `YOUR_API_TOKEN_HERE`
- `YOUR_PYTHON_API_TOKEN`
- `YOUR_GODMODE_TOKEN`
- `YOUR_JWT_TOKEN_HERE`
- `YOUR_PRODUCTION_API_KEY`

**File paths:**
- `/absolute/path/to/backend/dist/mcp-server.js`
- `/absolute/path/to/python-worker/src/mcp_server.py`

**Configuration values:**
- `your-secret-key-here`
- `your-api-key-here`
- `your-client-id`

### 2. Choose Your Connection Type

Depending on your use case, enable only the connections you need:

- **Local development?** Use STDIO connections
- **Need real-time updates?** Use SSE connections
- **Building a web service?** Use HTTP connections
- **Production deployment?** Use HTTPS with authentication

### 3. Configure Environment Variables

Each service may need environment variables:

```bash
# Backend (.env)
NODE_ENV=production
PORT=3001
DATABASE_URL=./data/flowstate.db
JWT_SECRET=your-secret-key

# Python Worker
PYTHONPATH=/path/to/python-worker
PORT=8000
```

### 4. Test Your Configuration

Test each connection type individually:

```bash
# Test STDIO connection
node /path/to/your/mcp-server.js

# Test SSE connection
curl -N http://localhost:3001/mcp/sse

# Test HTTP connection
curl http://localhost:3001/api/health
```

## Flowstate-AI Services

### Backend (Node.js/Express)
- **Port:** 3001
- **Capabilities:** Customer management, interactions, events, reminders, NBA
- **Connection types:** All three (STDIO, SSE, HTTP)

### Python Worker (FastAPI)
- **Port:** 8000
- **Capabilities:** AI recommendations, reminder processing
- **Connection types:** All three (STDIO, SSE, HTTP)

### GODMODE Dashboard (Flask)
- **Port:** 3333
- **Capabilities:** AI agent monitoring, chat interface
- **Connection types:** SSE and HTTP

## Configuration Structure

```
mcp-config.json
├── mcpServers/           # Individual server configurations
│   ├── stdio examples    # Local subprocess connections
│   ├── sse examples      # Real-time streaming connections
│   └── http examples     # REST API connections
├── global/               # Global settings
│   ├── logging          # Logging configuration
│   ├── security         # Security settings
│   └── defaults         # Default values
└── documentation/        # Comprehensive docs
    ├── connectionTypes  # Details on each type
    ├── examples         # Usage examples
    ├── placeholders     # What to replace
    └── setup            # Setup instructions
```

## Features

### Comprehensive Coverage
✅ All three MCP connection types (STDIO, SSE, HTTP)  
✅ Multiple real-world examples for each type  
✅ Both development and production configurations  
✅ Clear inline comments explaining each option  

### Well-Documented
✅ Detailed connection type descriptions  
✅ Pros and cons for each approach  
✅ Use case recommendations  
✅ Complete setup instructions  

### Production-Ready
✅ Authentication examples  
✅ Retry and timeout configurations  
✅ Rate limiting setup  
✅ Security settings  
✅ Error handling patterns  

### Flowstate-AI Specific
✅ Backend API endpoints  
✅ Python worker endpoints  
✅ GODMODE dashboard endpoints  
✅ Webhook configurations  
✅ Real service capabilities  

## Security Notes

1. **Never commit tokens:** Keep your API tokens in environment variables
2. **Use HTTPS in production:** Always use secure connections for production
3. **Rotate credentials:** Regularly update API keys and tokens
4. **Validate certificates:** Keep certificate validation enabled
5. **Rate limit:** Implement rate limiting to prevent abuse
6. **Monitor access:** Log and monitor API access patterns

## Troubleshooting

### STDIO Connection Issues
- Verify the command path is correct and executable
- Check that all required dependencies are installed
- Ensure environment variables are set correctly
- Look for error output in stderr

### SSE Connection Issues
- Verify the SSE endpoint is running and accessible
- Check that the server supports Server-Sent Events
- Ensure network/firewall allows the connection
- Verify authentication tokens are valid

### HTTP Connection Issues
- Test with curl or Postman first
- Verify the base URL and endpoints are correct
- Check authentication headers are included
- Look at server logs for error details
- Verify timeout and retry settings

## Additional Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Flowstate-AI Documentation](./docs/)
- [Backend API Reference](./backend/README.md)
- [Python Worker API](./python-worker/README.md)

## Support

For questions or issues:
1. Check the inline comments in `mcp-config.json`
2. Review the `documentation` section in the config file
3. Consult the Flowstate-AI README.md
4. Open an issue on GitHub

---

**Note:** This configuration file is a template. You must customize it for your specific environment before use.
