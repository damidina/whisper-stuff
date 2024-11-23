import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import websockets
import pyaudio
import json
import threading
import queue
from datetime import datetime

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Live Transcription")
        self.root.geometry("600x400")
        
        # Audio settings
        self.chunk = 4096
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000
        self.running = False
        self.audio_queue = queue.Queue()
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Get available devices
        self.devices = []
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev.get('maxInputChannels') > 0:
                self.devices.append((i, dev.get('name')))

        self.setup_gui()
        
    def setup_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Device selection
        ttk.Label(main_frame, text="Select Input Device:").grid(row=0, column=0, sticky=tk.W)
        self.device_var = tk.StringVar()
        device_combo = ttk.Combobox(main_frame, textvariable=self.device_var)
        device_combo['values'] = [dev[1] for dev in self.devices]
        device_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        device_combo.set(self.devices[0][1])  # Set default device
        
        # Start/Stop button
        self.button_text = tk.StringVar()
        self.button_text.set("Start Recording")
        self.toggle_button = ttk.Button(main_frame, textvariable=self.button_text, command=self.toggle_recording)
        self.toggle_button.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Transcription display
        self.transcript_display = scrolledtext.ScrolledText(main_frame, height=15, width=60)
        self.transcript_display.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Clear button
        clear_button = ttk.Button(main_frame, text="Clear Transcript", command=self.clear_transcript)
        clear_button.grid(row=3, column=0, columnspan=3, pady=5)

    def clear_transcript(self):
        self.transcript_display.delete(1.0, tk.END)

    def add_transcript(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transcript_display.insert(tk.END, f"[{timestamp}] {text}\n")
        self.transcript_display.see(tk.END)

    def toggle_recording(self):
        if not self.running:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.running = True
        self.button_text.set("Stop Recording")
        self.status_var.set("Recording...")
        
        # Get selected device index
        device_name = self.device_var.get()
        device_index = next(dev[0] for dev in self.devices if dev[1] == device_name)
        
        # Start audio thread
        self.audio_thread = threading.Thread(target=self.run_audio_client, args=(device_index,))
        self.audio_thread.start()

    def stop_recording(self):
        self.running = False
        self.button_text.set("Start Recording")
        self.status_var.set("Stopped")

    def run_audio_client(self, device_index):
        async def connect_websocket():
            try:
                async with websockets.connect('ws://localhost:9090', ping_interval=20) as websocket:
                    self.status_var.set("Connected to server")
                    
                    # Start audio stream
                    stream = self.p.open(
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=self.chunk
                    )
                    
                    # Audio processing loop
                    while self.running:
                        try:
                            data = stream.read(self.chunk, exception_on_overflow=False)
                            await websocket.send(data)
                            
                            # Receive transcription
                            try:
                                response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                                result = json.loads(response)
                                if result["text"].strip():
                                    self.root.after(0, self.add_transcript, result["text"])
                            except asyncio.TimeoutError:
                                continue
                                
                        except Exception as e:
                            self.status_var.set(f"Error: {str(e)}")
                            break
                    
                    # Cleanup
                    stream.stop_stream()
                    stream.close()
                    
            except Exception as e:
                self.status_var.set(f"Connection error: {str(e)}")
                self.running = False
                self.root.after(0, lambda: self.button_text.set("Start Recording"))

        # Run the async code
        asyncio.run(connect_websocket())

def main():
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()