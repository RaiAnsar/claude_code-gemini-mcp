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

Or simply ask claude code to correlate with Gemini, it is not a rocket sciene... (Author's note) 
```

## 🛠️ What This Does

1. Installs the Google Gemini Python SDK
2. Sets up an MCP server that bridges Claude Code and Gemini
3. Configures it globally (works in any directory)
4. Sets up persistent environment variable for secure API key storage
5. Provides tools for collaboration between Claude and Gemini

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
- Verify environment variable is set: `echo $CLAUDE_GEMINI_MCP_API_KEY`

## 🔑 Update API Key

To update your API key, add it to your shell profile:

```bash
# For bash users
echo 'export CLAUDE_GEMINI_MCP_API_KEY="your_new_api_key"' >> ~/.bashrc
source ~/.bashrc

# For zsh users  
echo 'export CLAUDE_GEMINI_MCP_API_KEY="your_new_api_key"' >> ~/.zshrc
source ~/.zshrc
```

Or simply re-run the setup script with your new API key.

## 🔄 Upgrading Gemini Model

To upgrade to a newer Gemini model version, edit the server file:

```bash
# Edit the server file
nano ~/.claude-mcp-servers/gemini-collab/server.py

# Find this line (around line 36):
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# Replace with your desired model, for example:
model = genai.GenerativeModel('gemini-2.5-flash')
model = genai.GenerativeModel('gemini-1.5-pro')
model = genai.GenerativeModel('gemini-1.5-flash')
```

After editing, restart Claude Code to apply changes.

## 🤝 Contributing

Pull requests welcome! Please keep it simple and beginner-friendly.

## 📜 License

MIT - Use freely!

---

Made with ❤️ for the Claude Code community
