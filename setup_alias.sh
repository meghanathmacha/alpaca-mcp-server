#!/bin/bash

# Setup Trading Alias
# ===================

CURRENT_DIR=$(pwd)
SHELL_CONFIG=""

# Detect shell config file
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    echo "⚠️  Unknown shell. You'll need to manually add the alias."
    echo "Add this line to your shell config:"
    echo "alias trade='cd $CURRENT_DIR && ./start_trading.sh'"
    exit 0
fi

# Create alias
ALIAS_LINE="alias trade='cd $CURRENT_DIR && ./start_trading.sh'"

# Check if alias already exists
if grep -q "alias trade=" "$SHELL_CONFIG" 2>/dev/null; then
    echo "🔄 Updating existing 'trade' alias..."
    # Remove old alias and add new one
    grep -v "alias trade=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp" && mv "${SHELL_CONFIG}.tmp" "$SHELL_CONFIG"
else
    echo "➕ Adding new 'trade' alias..."
fi

# Add the alias
echo "" >> "$SHELL_CONFIG"
echo "# SPY Options Trading Alias (auto-generated)" >> "$SHELL_CONFIG"
echo "$ALIAS_LINE" >> "$SHELL_CONFIG"

echo "✅ Alias added to $SHELL_CONFIG"
echo ""
echo "🎯 SETUP COMPLETE!"
echo "=================="
echo "Now you can start trading from anywhere by typing:"
echo "  trade"
echo ""
echo "To use immediately, run:"
echo "  source $SHELL_CONFIG"
echo "  trade"
echo ""
echo "The 'trade' command will:"
echo "  1. Navigate to this directory"
echo "  2. Activate the virtual environment"
echo "  3. Test API connection"
echo "  4. Start the trading session"