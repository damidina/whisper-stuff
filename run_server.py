from faster_whisper import WhisperModel
import websockets
import asyncio
import json
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

class TranscriptionServer:
    def __init__(self, host="0.0.0.0", port=5543, model_size="small"):  # Changed port here
        self.host = host
        self.port = port
        print("Initializing Whisper model...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("Model initialized!")
        
    async def transcribe_audio(self, websocket):
        buffer = np.array([], dtype=np.float32)
        print("Client connected")
        
        try:
            async for message in websocket:
                try:
                    audio_chunk = np.frombuffer(message, dtype=np.float32)
                    buffer = np.append(buffer, audio_chunk)
                    
                    if len(buffer) >= 32000:
                        segments, _ = self.model.transcribe(buffer, language="en")
                        buffer = np.array([], dtype=np.float32)
                        
                        for segment in segments:
                            response = {
                                "text": segment.text,
                                "start": segment.start,
                                "end": segment.end
                            }
                            await websocket.send(json.dumps(response))
                except Exception as e:
                    logging.error(f"Error processing audio: {e}")
                    continue
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info("Client disconnected")
        except Exception as e:
            logging.error(f"Error: {str(e)}")
        finally:
            print("Client disconnected")

    async def start(self):
        async with websockets.serve(self.transcribe_audio, self.host, self.port):
            print(f"Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()

def main():
    server = TranscriptionServer(port=5543)  # Changed port here
    asyncio.run(server.start())

if __name__ == "__main__":
    main()