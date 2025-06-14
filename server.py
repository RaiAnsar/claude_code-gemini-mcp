#!/usr/bin/env python3
"""
Claude-Gemini MCP Server
Enables Claude Code to collaborate with Google's Gemini AI
"""

import json
import sys
import os
from typing import Dict, Any, Optional

# Ensure unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

# Server version
__version__ = "1.0.0"

# Initialize Gemini
try:
    import google.generativeai as genai
    
    # Get API key from environment
    API_KEY = os.environ.get("CLAUDE_GEMINI_MCP_API_KEY")
    if not API_KEY:
        print(json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Please set your Gemini API key in the CLAUDE_GEMINI_MCP_API_KEY environment variable"
            }
        }), file=sys.stdout, flush=True)
        sys.exit(1)
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    GEMINI_ERROR = str(e)

def send_response(response: Dict[str, Any]):
    """Send a JSON-RPC response"""
    print(json.dumps(response), flush=True)

def handle_initialize(request_id: Any) -> Dict[str, Any]:
    """Handle initialization"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "claude-gemini-mcp",
                "version": __version__
            }
        }
    }

def handle_tools_list(request_id: Any) -> Dict[str, Any]:
    """List available tools"""
    tools = []
    
    if GEMINI_AVAILABLE:
        tools = [
            {
                "name": "ask_gemini",
                "description": "Ask Gemini a question and get the response directly in Claude's context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The question or prompt for Gemini"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature for response (0.0-1.0)",
                            "default": 0.5
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "gemini_code_review",
                "description": "Have Gemini review code and return feedback directly to Claude",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to review"
                        },
                        "focus": {
                            "type": "string",
                            "description": "Specific focus area (security, performance, etc.)",
                            "default": "general"
                        }
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "gemini_brainstorm",
                "description": "Brainstorm solutions with Gemini, response visible to Claude",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to brainstorm about"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context",
                            "default": ""
                        }
                    },
                    "required": ["topic"]
                }
            }
        ]
    else:
        tools = [
            {
                "name": "server_info",
                "description": "Get server status and error information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": tools
        }
    }

def call_gemini(prompt: str, temperature: float = 0.5) -> str:
    """Call Gemini and return response"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            )
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

def handle_tool_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tool execution"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        result = ""
        
        if tool_name == "server_info":
            if GEMINI_AVAILABLE:
                result = f"Server v{__version__} - Gemini connected and ready!"
            else:
                result = f"Server v{__version__} - Gemini error: {GEMINI_ERROR}"
        
        elif tool_name == "ask_gemini":
            if not GEMINI_AVAILABLE:
                result = f"Gemini not available: {GEMINI_ERROR}"
            else:
                prompt = arguments.get("prompt", "")
                temperature = arguments.get("temperature", 0.5)
                result = call_gemini(prompt, temperature)
            
        elif tool_name == "gemini_code_review":
            if not GEMINI_AVAILABLE:
                result = f"Gemini not available: {GEMINI_ERROR}"
            else:
                code = arguments.get("code", "")
                focus = arguments.get("focus", "general")
                prompt = f"""Please review this code with a focus on {focus}:

```
{code}
```

Provide specific, actionable feedback on:
1. Potential issues or bugs
2. Security concerns
3. Performance optimizations
4. Best practices
5. Code clarity and maintainability"""
                result = call_gemini(prompt, 0.2)
            
        elif tool_name == "gemini_brainstorm":
            if not GEMINI_AVAILABLE:
                result = f"Gemini not available: {GEMINI_ERROR}"
            else:
                topic = arguments.get("topic", "")
                context = arguments.get("context", "")
                prompt = f"Let's brainstorm about: {topic}"
                if context:
                    prompt += f"\n\nContext: {context}"
                prompt += "\n\nProvide creative ideas, alternatives, and considerations."
                result = call_gemini(prompt, 0.7)
            
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"🤖 GEMINI RESPONSE:\n\n{result}"
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

def main():
    """Main server loop"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})
            
            if method == "initialize":
                response = handle_initialize(request_id)
            elif method == "tools/list":
                response = handle_tools_list(request_id)
            elif method == "tools/call":
                response = handle_tool_call(request_id, params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            send_response(response)
            
        except json.JSONDecodeError:
            continue
        except EOFError:
            break
        except Exception as e:
            if 'request_id' in locals():
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                })

if __name__ == "__main__":
    main()