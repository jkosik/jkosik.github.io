# Using pre-trained wav2vec2 model from Hugging Face for keyword spotting.
# Uses pytorch instead of tensorflow.
# Reacts on microphone input and detects the word "go"

import numpy as np
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import sounddevice as sd
import queue
import threading
import time
import subprocess
from collections import deque

class RealTimeKeywordSpotter:
    def __init__(self, model_name="anton-l/wav2vec2-base-ft-keyword-spotting"):
        self.model_name = model_name
        self.sample_rate = 16000
        self.chunk_duration = 1.0  # seconds
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.overlap_duration = 0.5  # seconds overlap between chunks
        self.overlap_size = int(self.sample_rate * self.overlap_duration)

        # Detection parameters
        self.go_threshold = 0.7  # confidence threshold for "go" detection
        self.detection_cooldown = 1.0  # seconds to wait after detection
        self.last_detection_time = 0

        # Audio buffer
        self.audio_buffer = deque(maxlen=self.chunk_size * 2)
        self.audio_queue = queue.Queue()

        # Model components
        self.device = None
        self.model = None
        self.feature_extractor = None

        # Threading
        self.recording_thread = None
        self.processing_thread = None
        self.stop_event = threading.Event()

        # Load model
        self._load_model()

    def _load_model(self):
        """Load the wav2vec2 model and feature extractor."""
        print("Loading wav2vec2 keyword spotting model...")

        # Load feature extractor and model
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(self.model_name)
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(self.model_name)

        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        print(f"Model loaded on device: {self.device}")
        print(f"Target keyword: 'go' (threshold: {self.go_threshold})")

        # Get label mappings
        self.id2label = self.model.config.id2label
        self.go_class_id = None
        for class_id, label in self.id2label.items():
            if label.lower() == "go": # this is the word we want to detect
                self.go_class_id = int(class_id)
                break

        if self.go_class_id is None:
            raise ValueError("'go' class not found in model labels")

        print(f"'go' class ID: {self.go_class_id}")

    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio recording."""
        if status:
            print(f"Audio callback status: {status}")

        # Add audio data to queue
        audio_chunk = indata[:, 0]  # Convert to mono
        self.audio_queue.put(audio_chunk.copy())

    def _recording_worker(self):
        """Worker thread for audio recording."""
        print(f"Starting audio recording at {self.sample_rate} Hz...")

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                blocksize=1024,  # Small blocks for low latency
                dtype=np.float32
            ):
                while not self.stop_event.is_set():
                    time.sleep(0.1)
        except Exception as e:
            print(f"Recording error: {e}")

    def _predict_audio(self, audio_data):
        """Make prediction on audio data."""
        if len(audio_data) == 0:
            return None

        # Ensure audio is the right length (pad or truncate)
        if len(audio_data) < self.chunk_size:
            # Pad with zeros
            padded_audio = np.zeros(self.chunk_size, dtype=np.float32)
            padded_audio[:len(audio_data)] = audio_data
            audio_data = padded_audio
        elif len(audio_data) > self.chunk_size:
            # Truncate
            audio_data = audio_data[:self.chunk_size]

        try:
            # Process the audio
            inputs = self.feature_extractor(
                audio_data,
                sampling_rate=self.sample_rate,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Make prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            return predictions.cpu().numpy()[0]
        except Exception as e:
            print(f"Prediction error: {e}")
            return None

    def _processing_worker(self):
        """Worker thread for audio processing."""
        print("Starting audio processing...")

        while not self.stop_event.is_set():
            try:
                # Get audio chunk from queue (with timeout)
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Add to rolling buffer
                self.audio_buffer.extend(audio_chunk)

                # Process when we have enough audio
                if len(self.audio_buffer) >= self.chunk_size:
                    # Get audio data for processing
                    audio_data = np.array(list(self.audio_buffer)[-self.chunk_size:])

                    # Make prediction
                    predictions = self._predict_audio(audio_data)

                    if predictions is not None:
                        # Check for "go" detection
                        go_confidence = predictions[self.go_class_id]

                        # Get top prediction for monitoring
                        top_class_id = np.argmax(predictions)
                        top_confidence = predictions[top_class_id]
                        top_label = self.id2label.get(str(top_class_id), f"class_{top_class_id}")

                        # Print current prediction (only if confidence > 0.3)
                        if top_confidence > 0.3:
                            current_time = time.time()
                            print(f"\rCurrent: {top_label} ({top_confidence:.3f}) | "
                                  f"GO: {go_confidence:.3f}", end="", flush=True)

                        # Check for "go" detection
                        current_time = time.time()
                        if (go_confidence > self.go_threshold and
                            current_time - self.last_detection_time > self.detection_cooldown):

                            print(f"\n🚀 GO DETECTED! Confidence: {go_confidence:.3f}")
                            self.last_detection_time = current_time

                            # Optional: Play a sound or trigger an action
                            self._on_go_detected(go_confidence)

                    # Remove overlap amount from buffer to create sliding window
                    if len(self.audio_buffer) > self.overlap_size:
                        for _ in range(len(self.audio_buffer) - self.overlap_size):
                            self.audio_buffer.popleft()

            except Exception as e:
                print(f"Processing error: {e}")
                time.sleep(0.1)

    def _on_go_detected(self, confidence):
        """Called when 'go' is detected. Executes macOS command."""
        try:
            print("🌐 Opening Chrome browser...")

            # macOS command to open Chrome browser
            subprocess.run(["open", "-a", "Google Chrome"], check=True)

            print("✅ Chrome opened successfully!")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to open Chrome: {e}")

            # Fallback: try alternative Chrome names or open any browser
            try:
                print("🔄 Trying fallback: opening default browser...")
                subprocess.run(["open", "https://google.com"], check=True)
                print("✅ Default browser opened!")
            except subprocess.CalledProcessError as fallback_e:
                print(f"❌ Fallback failed too: {fallback_e}")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        # Add other actions here if needed:
        # subprocess.run(["say", "Go command detected"])  # Text-to-speech
        # subprocess.run(["open", "-a", "Finder"])        # Open Finder
        # subprocess.run(["open", "/Applications"])       # Open Applications folder

    def start(self):
        """Start real-time keyword spotting."""
        print("\n" + "="*60)
        print("REAL-TIME 'GO' DETECTION")
        print("="*60)
        print("Say 'go' into your microphone to open Chrome browser...")
        print("Press Ctrl+C to stop")
        print("="*60)

        # Start threads
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.processing_thread = threading.Thread(target=self._processing_worker)

        self.recording_thread.start()
        self.processing_thread.start()

        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            self.stop()

    def stop(self):
        """Stop real-time keyword spotting."""
        self.stop_event.set()

        if self.recording_thread:
            self.recording_thread.join(timeout=2)
        if self.processing_thread:
            self.processing_thread.join(timeout=2)

        print("Stopped.")

def main():
    # Check dependencies
    try:
        import transformers
        import torch
        import sounddevice
        print(f"Dependencies loaded successfully:")
        print(f"  - transformers: {transformers.__version__}")
        print(f"  - torch: {torch.__version__}")
        print(f"  - sounddevice: {sounddevice.__version__}")
        print()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install missing packages:")
        print("pip install transformers torch sounddevice")
        exit(1)

    # List available audio devices
    print("Available audio devices:")
    print(sd.query_devices())
    print()

    # Create and start keyword spotter
    spotter = RealTimeKeywordSpotter()
    spotter.start()

if __name__ == "__main__":
    main()
