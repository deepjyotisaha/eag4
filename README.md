# EAG4 Project

This repository contains the EAG4 (Enhanced AI Generation) project, which includes various AI agents and tools for different purposes.

## Project Structure

```
eag4/
├── math_agent/         # Math problem solving agent with visual and email support
├── gmail-mcp-server/   # Gmail MCP server for email functionality
├── examples/           # Example implementations
│   ├── agent/         # Agent-based MCP examples
│   ├── react_client/  # React-based MCP client examples
│   ├── ts_client/     # TypeScript-based MCP client examples
│   └── basic_client_server/  # Basic MCP client-server examples
└── ...
```

## Components

### Math Agent
The math agent is a specialized tool that can:
- Solve mathematical problems
- Display results visually on a canvas
- Send results via email
- Support visually impaired users

For detailed information about the math agent, see [Math Agent Documentation](math_agent/README.md).

### Gmail MCP Server
The Gmail MCP server provides email functionality for the math agent. It's based on the [Gmail MCP Server](https://github.com/jasonsum/gmail-mcp-server/tree/main) project.

### Examples
The project includes several example implementations demonstrating different aspects of MCP:

#### Agent Examples (`examples/agent/`)
- `example.py`: Basic agent implementation
- `talk2mcp-2.py`: Interactive MCP communication example
- `AgenticMCPUse.py`: Advanced agent usage patterns
- Includes logging and configuration examples

#### React Client Examples (`examples/react_client/`)
- React-based frontend implementation
- Integration with Python MCP server
- Frontend-backend communication examples

#### TypeScript Client Examples (`examples/ts_client/`)
- TypeScript-based MCP client implementation
- Type-safe MCP communication
- Client-server architecture examples

#### Basic Client-Server Examples (`examples/basic_client_server/`)
- Simple MCP client-server implementation
- Basic communication patterns
- Getting started examples

## Getting Started

1. Navigate to the specific component you want to use:
   ```bash
   cd math_agent
   ```

2. Follow the setup instructions in the component's README file.

3. For examples, choose the appropriate directory based on your needs:
   ```bash
   # For basic examples
   cd examples/basic_client_server
   
   # For agent examples
   cd examples/agent
   
   # For React examples
   cd examples/react_client
   
   # For TypeScript examples
   cd examples/ts_client
   ```

## Development

Each component in this project has its own setup and configuration requirements. Please refer to the individual README files for specific instructions.

## Contributing

Feel free to submit issues and enhancement requests for any component in the project.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 