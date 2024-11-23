import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QPushButton, QTextEdit, 
                            QLabel, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import asyncio
import websockets
import pyaudio
import json
from datetime import datetime

class AudioThread(QThread):
    transcription_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, device_index):
        super().__init__()
        self.device_index = device_index
        self.running = False
        self.chunk = 4096
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000
        
    async def process_audio(self):
        try:
            async with websockets.connect('ws://localhost:5543', ping_interval=20) as websocket:
                self.status_changed.emit("Connected to server")
                
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.chunk
                )
                
                while self.running:
                    try:
                        data = stream.read(self.chunk, exception_on_overflow=False)
                        await websocket.send(data)
                        
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                            result = json.loads(response)
                            if result["text"].strip():
                                self.transcription_received.emit(result["text"])
                        except asyncio.TimeoutError:
                            continue
                            
                    except Exception as e:
                        self.status_changed.emit(f"Error: {str(e)}")
                        break
                
                stream.stop_stream()
                stream.close()
                p.terminate()
                
        except Exception as e:
            self.status_changed.emit(f"Connection error: {str(e)}")
    
    def run(self):
        self.running = True
        asyncio.run(self.process_audio())
    
    def stop(self):
        self.running = False

class WhisperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Call Transcription")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.audio_thread = None
        
        # Get available devices
        self.devices = []
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev.get('maxInputChannels') > 0:
                self.devices.append((i, dev.get('name')))
        
        self.setup_ui()
        self.find_blackhole_device()  # Auto-select BlackHole
    
    def find_blackhole_device(self):
        for i, dev in self.devices:
            if "BlackHole" in dev:
                self.device_combo.setCurrentText(dev)
                return
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Call Transcription")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Controls frame
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_layout = QHBoxLayout(controls_frame)
        
        # Device selection
        self.device_combo = QComboBox()
        self.device_combo.addItems([dev[1] for dev in self.devices])
        controls_layout.addWidget(QLabel("Audio Source:"))
        controls_layout.addWidget(self.device_combo)
        
        # Start/Stop button
        self.toggle_button = QPushButton("Start Transcription")
        self.toggle_button.clicked.connect(self.toggle_recording)
        controls_layout.addWidget(self.toggle_button)
        
        layout.addWidget(controls_frame)
        
        # Status label
        self.status_label = QLabel("Ready - Set your call audio output to BlackHole")
        self.status_label.setStyleSheet("color: blue;")
        layout.addWidget(self.status_label)
        
        # Transcription display
        self.transcript_display = QTextEdit()
        self.transcript_display.setReadOnly(True)
        layout.addWidget(self.transcript_display)
        
        # Buttons frame
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        # Clear button
        clear_button = QPushButton("Clear Transcript")
        clear_button.clicked.connect(self.clear_transcript)
        buttons_layout.addWidget(clear_button)
        
        # Save button
        save_button = QPushButton("Save Transcript")
        save_button.clicked.connect(self.save_transcript)
        buttons_layout.addWidget(save_button)
        
        layout.addWidget(buttons_frame)
    
    def toggle_recording(self):
        if self.audio_thread is None or not self.audio_thread.running:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        device_name = self.device_combo.currentText()
        device_index = next(dev[0] for dev in self.devices if dev[1] == device_name)
        
        self.audio_thread = AudioThread(device_index)
        self.audio_thread.transcription_received.connect(self.add_transcript)
        self.audio_thread.status_changed.connect(self.status_label.setText)
        self.audio_thread.start()
        
        self.toggle_button.setText("Stop Transcription")
        self.status_label.setText("Transcribing...")
    
    def stop_recording(self):
        if self.audio_thread:
            self.audio_thread.stop()
            self.audio_thread = None
        
        self.toggle_button.setText("Start Transcription")
        self.status_label.setText("Stopped - Set your call audio output to BlackHole")
    
    def add_transcript(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transcript_display.append(f"[{timestamp}] {text}")
    
    def clear_transcript(self):
        self.transcript_display.clear()
    
    def save_transcript(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"call_transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(self.transcript_display.toPlainText())
        self.status_label.setText(f"Transcript saved to {filename}")
    
    def closeEvent(self, event):
        self.stop_recording()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = WhisperGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()