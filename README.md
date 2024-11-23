# Whisper Call Transcription

Real-time call transcription using Whisper AI.

## Installation

1. Download and unzip the project
2. Open Terminal
3. Navigate to the project directory:
   ```bash
   cd path/to/whisper_project
   ```

4. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

5. Set up BlackHole:
   - Open System Settings → Sound
   - Create a Multi-Output Device:
     1. Open Audio MIDI Setup (use Spotlight to find it)
     2. Click + → Create Multi-Output Device
     3. Check both "BlackHole 2ch" and your speakers/headphones

## Running the Application

1. Open two Terminal windows
2. In both terminals, navigate to the project directory and activate the virtual environment:
   ```bash
   cd path/to/whisper_project
   source venv/bin/activate
   ```

3. In the first terminal, start the server:
   ```bash
   python3 run_server.py
   ```

4. In the second terminal, start the GUI:
   ```bash
   python3 gui_client.py
   ```

## Using the Application

1. Before your call:
   - Open System Settings → Sound
   - Set Output to your Multi-Output Device

2. Start transcribing:
   - Select "BlackHole 2ch" in the GUI dropdown
   - Click "Start Transcription"
   - Begin your call

3. Save transcripts:
   - Click "Save Transcript" to save the current session
   - Files are saved in the project directory

## Troubleshooting

If you encounter any issues:
1. Make sure BlackHole is installed and configured
2. Check that both the server and client are running
3. Verify your sound output settings
4. Try restarting the application

## Updates

To update the application:
1. Download the latest version
2. Replace the Python files
3. Run `pip install -r requirements.txt` in your virtual environment