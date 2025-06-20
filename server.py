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

# Available Gemini models
AVAILABLE_MODELS = {
    "gemini-2.5-flash": "Latest, best price-performance ratio",
    "gemini-2.0-flash": "Newest multimodal with next-gen features",
    "gemini-2.0-flash-lite": "Cost-efficient with low latency",
    "gemini-1.5-pro-latest": "Powerful with long context (up to 1M tokens)",
    "gemini-1.5-flash": "Fast and versatile multimodal",
    "gemini-1.5-flash-8b": "Small model for simple tasks",
    "gemini-1.0-pro-latest": "Legacy model with 32k context"
}

# Default model
DEFAULT_MODEL = "gemini-2.0-flash"

# System prompt configuration
DEFAULT_PROMPT_FILE = "~/.claude-mcp-servers/gemini-collab/GEMINI.md"
SYSTEM_PROMPT_FILE = os.path.expanduser(os.environ.get("GEMINI_SYSTEM_PROMPT", DEFAULT_PROMPT_FILE))
DEFAULT_SYSTEM_PROMPT = ""

# Load system prompt from file if exists
def load_system_prompt():
    global DEFAULT_SYSTEM_PROMPT
    if os.path.exists(SYSTEM_PROMPT_FILE):
        try:
            with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                DEFAULT_SYSTEM_PROMPT = f.read().strip()
                # Only show message if actually loaded something
                if DEFAULT_SYSTEM_PROMPT:
                    print(f"✓ Loaded system prompt from {SYSTEM_PROMPT_FILE}", file=sys.stderr)
        except Exception as e:
            # Silently continue if file cannot be read
            pass

# Initialize Gemini
try:
    import google.generativeai as genai
    
    # Get API key from environment or use the one provided during setup
    API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    if API_KEY == "YOUR_API_KEY_HERE":
        print(json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Please set your Gemini API key in the server.py file or GEMINI_API_KEY environment variable"
            }
        }), file=sys.stdout, flush=True)
        sys.exit(1)
    
    genai.configure(api_key=API_KEY)
    # Get model from environment or use default
    MODEL_NAME = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    
    # Validate model if specified
    if MODEL_NAME != DEFAULT_MODEL and MODEL_NAME not in AVAILABLE_MODELS:
        print(f"⚠️  Unknown model '{MODEL_NAME}', using default '{DEFAULT_MODEL}'", file=sys.stderr)
        MODEL_NAME = DEFAULT_MODEL
    
    model = genai.GenerativeModel(MODEL_NAME)
    GEMINI_AVAILABLE = True
    
    # Load system prompt
    load_system_prompt()
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
                        },
                        "model": {
                            "type": "string",
                            "description": f"Model to use. Available: {', '.join(AVAILABLE_MODELS.keys())}. Default: {MODEL_NAME}",
                            "default": MODEL_NAME
                        },
                        "include_system_prompt": {
                            "type": "boolean",
                            "description": "Include system prompt from GEMINI.md. Default: true",
                            "default": True
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

def call_gemini(prompt: str, temperature: float = 0.5, model_name: str = None, include_system_prompt: bool = True) -> str:
    """Call Gemini and return response"""
    try:
        # Use specified model or default
        if model_name and model_name != MODEL_NAME:
            if model_name not in AVAILABLE_MODELS:
                return f"❌ Unknown model '{model_name}'\n\nTry one of these:\n" + \
                       "\n".join([f"• {k} - {v}" for k, v in AVAILABLE_MODELS.items()])
            temp_model = genai.GenerativeModel(model_name)
        else:
            temp_model = model
            model_name = MODEL_NAME
        
        # Add system prompt if available and requested
        final_prompt = prompt
        if include_system_prompt and DEFAULT_SYSTEM_PROMPT:
            final_prompt = f"{DEFAULT_SYSTEM_PROMPT}\n\n---\n\nUser Request:\n{prompt}"
        
        response = temp_model.generate_content(
            final_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            )
        )
        # Only show model info if not using default
        if model_name != DEFAULT_MODEL:
            return f"✨ Using {model_name}\n\n{response.text}"
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
                system_info = f"Server v{__version__} - Gemini connected and ready!"
                if MODEL_NAME != DEFAULT_MODEL:
                    system_info += f"\n✨ Using model: {MODEL_NAME}"
                if DEFAULT_SYSTEM_PROMPT:
                    system_info += f"\n📝 System prompt loaded from {os.path.basename(SYSTEM_PROMPT_FILE)}"
                result = system_info
            else:
                result = f"Server v{__version__} - Gemini error: {GEMINI_ERROR}"
        
        elif tool_name == "ask_gemini":
            if not GEMINI_AVAILABLE:
                result = f"Gemini not available: {GEMINI_ERROR}"
            else:
                prompt = arguments.get("prompt", "")
                temperature = arguments.get("temperature", 0.5)
                model_name = arguments.get("model", None)
                include_system = arguments.get("include_system_prompt", True)
                result = call_gemini(prompt, temperature, model_name, include_system)
            
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
                result = call_gemini(prompt, 0.2, None, True)
            
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
                result = call_gemini(prompt, 0.7, None, True)
            
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