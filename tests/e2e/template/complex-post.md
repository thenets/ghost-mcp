# Using Playwright MCP Server with Google Chrome Flatpak on Linux

The Model Context Protocol (MCP) has revolutionized how AI assistants interact with external tools and services. One particularly powerful integration is the [Playwright MCP server](https://github.com/microsoft/playwright-mcp), which enables AI to control web browsers for automation tasks. This guide shows you the simplest way to get Playwright MCP working with Google Chrome on Linux using Flatpak.

## The Simple Solution

Instead of complex configurations, we'll use a two-step approach:
1. Install Google Chrome from Flathub
2. Create a symbolic link that Playwright expects

## Step 1: Install Google Chrome from Flathub

First, install Google Chrome using Flatpak:

```bash
flatpak install flathub com.google.Chrome
```

## Step 2: Create the Symbolic Link

Playwright expects Chrome to be located at `/opt/google/chrome/chrome`. We'll create a symbolic link pointing to the Flatpak Chrome binary:

```bash
# Create the directory structure
sudo mkdir -p /opt/google/chrome

# Create the symbolic link
sudo ln -s /var/lib/flatpak/exports/bin/com.google.Chrome /opt/google/chrome/chrome
```

## Step 3: Add to Claude Code

If you're using Claude Code, you can quickly add the Playwright MCP server:

```bash
claude mcp add playwright npx @playwright/mcp@latest
```

Or manually add this configuration to your MCP settings:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

## That's It!

Now Playwright MCP server will automatically find and use your Flatpak Chrome installation.

## Test the Setup

You can test that everything works by running a simple Playwright script:

```ini
# Start Claude Code
claude

# Ask something like
Use the playwright MCP tools to write a haiku in the https://note.thenets.org/playwright-example
# the Chrome Browser should open
```

## Why This Works

- Playwright looks for Chrome at `/opt/google/chrome/chrome` by default
- Flatpak installs Chrome at `/var/lib/flatpak/exports/bin/com.google.Chrome`
- The symbolic link bridges this gap without complex configuration
- Chrome runs with all the security benefits of Flatpak sandboxing

## Troubleshooting

If the symbolic link doesn't work, verify the Flatpak Chrome path:

```bash
ls -la /var/lib/flatpak/exports/bin/com.google.Chrome
```

If Chrome isn't at that location, find it with:

```bash
flatpak list --app | grep Chrome
which com.google.Chrome
```

## Conclusion

This simple two-step solution eliminates the complexity typically associated with using Flatpak browsers with Playwright. By creating a symbolic link, you get the best of both worlds: the security of Flatpak and the simplicity of standard Playwright configuration.