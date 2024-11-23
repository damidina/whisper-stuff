#!/bin/bash

# Create and save this as setup.sh
echo "Setting up Whisper Transcription..."

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python if not installed
brew install python@3.11

# Install BlackHole for audio routing
brew install blackhole-2ch

# Install pyenv for Python version management
brew install pyenv

# Setup Python environment
echo "Setting up Python environment..."
pyenv install 3.11.7
pyenv global 3.11.7

# Create project directory
mkdir -p whisper_project
cd whisper_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install faster-whisper
pip install websockets
pip install pyaudio
pip install PyQt5

echo "Setup complete! Now copy the Python files and run the application."