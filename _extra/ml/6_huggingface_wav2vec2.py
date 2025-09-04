# Using pre-trained wav2vec2 model from Hugging Face for keyword spotting.
# Uses pytorch instead of tensorflow.
# Predicts on a sample of yes/no wav files from samples/ directory.

import os
import numpy as np
import torch
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import librosa
import glob

def load_audio(file_path, target_sr=16000):
    """Load audio file and resample to target sampling rate."""
    audio, sr = librosa.load(file_path, sr=target_sr)
    return audio

def predict_audio(model, feature_extractor, audio_data, device):
    """Make prediction on audio data."""
    # Process the audio
    inputs = feature_extractor(audio_data, sampling_rate=16000, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Make prediction
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

    return predictions.cpu().numpy()

def main():
    print("Loading wav2vec2 keyword spotting model from Hugging Face...")

    # Model from Hugging Face: https://huggingface.co/anton-l/wav2vec2-base-ft-keyword-spotting
    model_name = "anton-l/wav2vec2-base-ft-keyword-spotting"

    # Load feature extractor and model
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
    model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    print(f"Model loaded on device: {device}")
    print(f"Model config: {model.config}")
    print(f"Number of labels: {model.config.num_labels}")

    # Get label mappings if available
    if hasattr(model.config, 'id2label'):
        id2label = model.config.id2label
        label2id = model.config.label2id
        print(f"Labels: {list(id2label.values())}")
    else:
        print("No label mapping found in model config")
        id2label = {i: f"class_{i}" for i in range(model.config.num_labels)}

    # Test directories
    sample_dirs = {
        'yes': 'samples/yes/',
        'no': 'samples/no/'
    }

    print("\n" + "="*60)
    print("TESTING AUDIO SAMPLES")
    print("="*60)

    all_results = []

    for expected_label, dir_path in sample_dirs.items():
        if not os.path.exists(dir_path):
            print(f"Directory {dir_path} not found!")
            continue

        wav_files = glob.glob(os.path.join(dir_path, "*.wav"))
        print(f"\nTesting {len(wav_files)} files from '{expected_label}' directory:")
        print("-" * 50)

        for wav_file in wav_files:
            filename = os.path.basename(wav_file)

            # Load audio
            try:
                audio_data = load_audio(wav_file)
                audio_duration = len(audio_data) / 16000  # duration in seconds

                # Make prediction
                predictions = predict_audio(model, feature_extractor, audio_data, device)

                # Get top prediction
                predicted_class_id = np.argmax(predictions[0])
                confidence = predictions[0][predicted_class_id]
                predicted_label = id2label.get(predicted_class_id, f"class_{predicted_class_id}")

                # Display results
                print(f"File: {filename}")
                print(f"  Duration: {audio_duration:.2f}s")
                print(f"  Expected: {expected_label}")
                print(f"  Predicted: {predicted_label} (confidence: {confidence:.4f})")

                # Show top 3 predictions
                top_3_indices = np.argsort(predictions[0])[-3:][::-1]
                print(f"  Top 3 predictions:")
                for i, idx in enumerate(top_3_indices):
                    label = id2label.get(idx, f"class_{idx}")
                    conf = predictions[0][idx]
                    print(f"    {i+1}. {label}: {conf:.4f}")

                # Store result for summary
                all_results.append({
                    'file': filename,
                    'expected': expected_label,
                    'predicted': predicted_label,
                    'confidence': confidence,
                    'correct': expected_label.lower() == predicted_label.lower()
                })

                print()

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if all_results:
        correct_predictions = sum(1 for r in all_results if r['correct'])
        total_predictions = len(all_results)
        accuracy = correct_predictions / total_predictions

        print(f"Total files tested: {total_predictions}")
        print(f"Correct predictions: {correct_predictions}")
        print(f"Accuracy: {accuracy:.2%}")

        print(f"\nDetailed results:")
        for result in all_results:
            status = "✅" if result['correct'] else "❌"
            print(f"  {status} {result['file']}: {result['expected']} → {result['predicted']} ({result['confidence']:.3f})")
    else:
        print("No results to summarize.")

if __name__ == "__main__":
    # Check dependencies
    try:
        import transformers
        import librosa
        import torch
        print(f"Dependencies loaded successfully:")
        print(f"  - transformers: {transformers.__version__}")
        print(f"  - torch: {torch.__version__}")
        print(f"  - librosa: {librosa.__version__}")
        print()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install missing packages:")
        print("pip install transformers torch librosa")
        exit(1)

    main()
