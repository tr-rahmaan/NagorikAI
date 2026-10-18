#!/usr/bin/env bash
# CivicSphere AI Local Launcher
cd "$(dirname "$0")"
export STREAMLIT_CONFIG_DIR="$(pwd)/.streamlit"
export STREAMLIT_SERVER_HEADLESS="false"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"

# Use Python 3.14 Framework binary where all packages (streamlit, gTTS, etc.) are installed
if [ -x "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3" ]; then
    PYTHON_EXEC="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_EXEC="$(command -v python3)"
else
    PYTHON_EXEC="python"
fi

echo "=================================================="
echo "🇧🇩 Starting CivicSphere AI (GovCopilot)"
echo "Using Python: $PYTHON_EXEC"
echo "=================================================="
"$PYTHON_EXEC" -m streamlit run app.py
