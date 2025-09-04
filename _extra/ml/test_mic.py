#!/usr/bin/env python3
"""
Simple microphone test for keyword spotting.
Records a few seconds of audio and processes it through the model.
"""

import numpy as np
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import sounddevice as sd
import time

def test_microphone_recording():
    """Test basic microphone recording functionality."""
    print("Testing microphone recording...")

    # Record 3 seconds of audio
    duration = 3  # seconds
    sample_rate = 16000

    print(f"Recording {duration} seconds of audio at {sample_rate} Hz...")
    print("Say 'yes' now!")

    # Record audio
    audio_data = sd.rec(int(duration * sample_rate),
                       samplerate=sample_rate,
                       channels=1,
                       dtype=np.float32)
    sd.wait()  # Wait until recording is finished

    print("Recording finished.")

    # Convert to 1D array
    audio_data = audio_data.flatten()

    print(f"Recorded audio shape: {audio_data.shape}")
    print(f"Audio duration: {len(audio_data) / sample_rate:.2f} seconds")
    print(f"Audio level (RMS): {np.sqrt(np.mean(audio_data**2)):.4f}")

    return audio_data

def test_model_prediction(audio_data):
    """Test model prediction on recorded audio."""
    print("\nLoading model...")

    model_name = "anton-l/wav2vec2-base-ft-keyword-spotting"
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
    model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    print(f"Model loaded on: {device}")

    # Get label mappings
    id2label = model.config.id2label
    print(f"Available labels: {list(id2label.values())}")

    # Process audio through model
    print("\nProcessing audio...")

    try:
        # Process the audio
        inputs = feature_extractor(
            audio_data,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Make prediction
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        predictions = predictions.cpu().numpy()[0]

        # Get top 3 predictions
        top_3_indices = np.argsort(predictions)[-3:][::-1]

        print("Top 3 predictions:")
        for i, idx in enumerate(top_3_indices):
            label = id2label.get(str(idx), f"class_{idx}")
            confidence = predictions[idx]
            print(f"  {i+1}. {label}: {confidence:.4f}")

        # Check specifically for "yes"
        yes_class_id = None
        for class_id, label in id2label.items():
            if label.lower() == "yes":
                yes_class_id = int(class_id)
                break

        if yes_class_id is not None:
            yes_confidence = predictions[yes_class_id]
            print(f"\n'YES' confidence: {yes_confidence:.4f}")

            if yes_confidence > 0.5:
                print("🎉 'YES' detected with good confidence!")
            elif yes_confidence > 0.3:
                print("👀 'YES' detected with medium confidence")
            else:
                print("❌ 'YES' not detected")

    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Microphone Keyword Spotting Test")
    print("="*40)

    # Check dependencies
    try:
        import transformers
        import torch
        import sounddevice
        print(f"Dependencies OK:")
        print(f"  - transformers: {transformers.__version__}")
        print(f"  - torch: {torch.__version__}")
        print(f"  - sounddevice: {sounddevice.__version__}")
        print()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return

    # Show available audio devices
    print("Available audio devices:")
    devices = sd.query_devices()
    print(devices)
    print()

    # Test microphone recording
    try:
        audio_data = test_microphone_recording()

        # Test model prediction
        test_model_prediction(audio_data)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
