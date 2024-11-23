# Real-time Whisper Transcription

A real-time audio transcription system using Whisper.

## Setup
1. Make sure you have Python 3.8+ installed
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Running
1. Start the server:
   ```bash
   python3 run_server.py
   ```

2. In another terminal, start the client:
   ```bash
   python3 test_client.py
   ```

3. Speak into your microphone and see the transcription in real-time
4. Press Ctrl+C to stop

## Files
- `run_server.py`: Transcription server using Whisper
- `test_client.py`: Audio recording and streaming client
- `requirements.txt`: Required Python packages
