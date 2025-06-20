# Claude Code + Gemini MCP Server

Connect Claude Code with Google's Gemini AI for powerful AI collaboration. Ask Gemini questions, get code reviews, and brainstorm ideas - all within Claude Code!

## 🚀 Quick Start (2 minutes)

### Prerequisites
- Python 3.8+ installed
- Claude Code CLI installed
- Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))

### One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/RaiAnsar/claude_code-gemini-mcp/main/install.sh | bash
```

### Manual Install

1. **Clone this repo:**
```bash
git clone https://github.com/RaiAnsar/claude_code-gemini-mcp.git
cd claude_code-gemini-mcp
```

2. **Run setup with your API key:**
```bash
./setup.sh YOUR_GEMINI_API_KEY
```

That's it! 🎉

## 📖 Usage

Start Claude Code anywhere and use these commands:

```bash
claude

# Ask Gemini anything

mcp__gemini-collab__ask_gemini
  prompt: "Explain quantum computing in simple terms"

# Get code reviews
mcp__gemini-collab__gemini_code_review
  code: "def auth(u): return u.pwd == 'admin'"
  focus: "security"

# Brainstorm ideas
mcp__gemini-collab__gemini_brainstorm
  topic: "How to scale a web app to 1M users"

# Use a specific model (New Feature)
mcp__gemini-collab__ask_gemini
  prompt: "Analyze this long document..."
  model: "gemini-1.5-pro-latest"  # For long context tasks

Or simply ask claude code to correlate with Gemini, it is not a rocket sciene... (Author's note) 
```

## 🛠️ What This Does

1. Installs the Google Gemini Python SDK
2. Sets up an MCP server that bridges Claude Code and Gemini
3. Configures it globally (works in any directory)
4. Provides tools for collaboration between Claude and Gemini

## 🔧 Available Tools

- **ask_gemini** - Ask Gemini any question
- **gemini_code_review** - Get security/performance code reviews
- **gemini_brainstorm** - Brainstorm ideas and solutions

## 📁 Installation Location

The server is installed at: `~/.claude-mcp-servers/gemini-collab/`

## 🐛 Troubleshooting

**MCP not showing up?**
```bash
# Check if it's installed
claude mcp list

# Reinstall with global scope
claude mcp remove gemini-collab
claude mcp add --scope user gemini-collab python3 ~/.claude-mcp-servers/gemini-collab/server.py
```

**Connection errors?**
- Check your API key is valid
- Ensure Python has `google-generativeai` installed: `pip install google-generativeai`

## 🔑 Update API Key

Edit `~/.claude-mcp-servers/gemini-collab/server.py` and replace the API key.

## 📝 System Prompt Support (New Feature)

Add a system prompt to customize Gemini's behavior (like CLAUDE.md for Claude).

1. Create `~/.claude-mcp-servers/gemini-collab/GEMINI.md`
2. Add your instructions
3. Restart Claude Code

That's it! Gemini will use your instructions automatically.

## 🤖 Model Selection (New Feature)

Use different Gemini models for different tasks:

- **gemini-1.5-pro-latest** - For long documents (up to 1M tokens)
- **gemini-2.0-flash** - Default, fast and smart
- **gemini-2.0-flash-lite** - For quick responses

Just add `model: "gemini-1.5-pro-latest"` to your request!

## 🤝 Contributing

Pull requests welcome! Please keep it simple and beginner-friendly.

## 📜 License

MIT - Use freely!

---

Made with ❤️ for the Claude Code community
