import io
import os

import librosa
import numpy as np
import soundfile as sf
import torch
import torch.nn as nn

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# Configuration
# ============================================================

PROJECT_DIR = r"C:\Hehe\Voice Integrity"

MODEL_PATH = os.path.join(
    PROJECT_DIR,
    "best_indictts_full_voice_integrity_cnn.pth"
)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

SAMPLE_RATE = 16000

# Model expects exactly 4 seconds
NUM_SAMPLES = 64000

# Sliding-window analysis
WINDOW_HOP = 32000       # 2 seconds
MIN_AUDIO_SECONDS = 0.5

N_MELS = 128
N_FFT = 1024
HOP_LENGTH = 256


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="VoiceShield AI Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# CNN Model
# ============================================================

class VoiceIntegrityCNN(nn.Module):

    def __init__(self):
        super().__init__()

        self.features = nn.Sequential(

            nn.Conv2d(
                1, 32, 3, padding=1
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(
                32, 64, 3, padding=1
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(
                64, 128, 3, padding=1
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(
                128, 256, 3, padding=1
            ),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.pool = nn.AdaptiveAvgPool2d(
            (4, 4)
        )

        self.classifier = nn.Sequential(

            nn.Flatten(),

            nn.Linear(
                256 * 4 * 4,
                256
            ),

            nn.ReLU(),

            nn.Dropout(0.4),

            nn.Linear(
                256,
                2
            )
        )

    def forward(self, x):

        x = self.features(x)

        x = self.pool(x)

        x = self.classifier(x)

        return x


# ============================================================
# Load trained model
# ============================================================

print("==============================================")
print("Loading Voice Integrity CNN...")
print("==============================================")

print("Model path:", MODEL_PATH)
print("Device:", DEVICE)

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"Model checkpoint not found:\n{MODEL_PATH}"
    )


model = VoiceIntegrityCNN().to(DEVICE)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("CNN model loaded successfully.")
print("==============================================")


# ============================================================
# Audio preprocessing
# ============================================================

def preprocess_audio_for_cnn(
    audio,
    sr
):

    audio = np.asarray(
        audio,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # Stereo -> mono
    # --------------------------------------------------------

    if audio.ndim > 1:

        audio = np.mean(
            audio,
            axis=1
        )

    # --------------------------------------------------------
    # Remove DC offset
    # --------------------------------------------------------

    audio = audio - np.mean(audio)

    # --------------------------------------------------------
    # Resample to 16 kHz
    # --------------------------------------------------------

    if sr != SAMPLE_RATE:

        audio = librosa.resample(
            audio,
            orig_sr=sr,
            target_sr=SAMPLE_RATE
        )

    # --------------------------------------------------------
    # Fixed 4-second input
    # --------------------------------------------------------

    if len(audio) < NUM_SAMPLES:

        audio = np.pad(
            audio,
            (
                0,
                NUM_SAMPLES - len(audio)
            )
        )

    else:

        audio = audio[
            :NUM_SAMPLES
        ]

    # --------------------------------------------------------
    # Peak normalization
    # --------------------------------------------------------

    peak = np.max(
        np.abs(audio)
    )

    if peak > 1e-8:

        audio = audio / peak

    return audio


# ============================================================
# CNN inference on ONE 4-second window
# ============================================================

def predict_single_window(
    audio,
    sr
):

    audio = preprocess_audio_for_cnn(
        audio,
        sr
    )

    # --------------------------------------------------------
    # Mel spectrogram
    # --------------------------------------------------------

    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS
    )

    # --------------------------------------------------------
    # Convert to dB
    # --------------------------------------------------------

    mel = librosa.power_to_db(
        mel,
        ref=np.max
    )

    # --------------------------------------------------------
    # Per-sample standardization
    # --------------------------------------------------------

    mel = (
        mel - mel.mean()
    ) / (
        mel.std() + 1e-8
    )

    # --------------------------------------------------------
    # Tensor
    # --------------------------------------------------------

    mel_tensor = torch.tensor(
        mel,
        dtype=torch.float32
    )

    mel_tensor = (
        mel_tensor
        .unsqueeze(0)
        .unsqueeze(0)
        .to(DEVICE)
    )

    # --------------------------------------------------------
    # CNN inference
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model(
            mel_tensor
        )

        probabilities = torch.softmax(
            logits,
            dim=1
        )

    # Class 1 = synthetic / TTS

    synthetic_probability = (
        probabilities[0, 1].item()
    )

    return synthetic_probability


# ============================================================
# Sliding-window analysis
# ============================================================

def analyze_full_audio(
    audio,
    sr
):

    audio = np.asarray(
        audio,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # Convert stereo -> mono
    # --------------------------------------------------------

    if audio.ndim > 1:

        audio = np.mean(
            audio,
            axis=1
        )

    # --------------------------------------------------------
    # Resample entire audio first
    # --------------------------------------------------------

    if sr != SAMPLE_RATE:

        audio = librosa.resample(
            audio,
            orig_sr=sr,
            target_sr=SAMPLE_RATE
        )

        sr = SAMPLE_RATE

    total_samples = len(audio)

    duration = (
        total_samples / sr
    )

    # --------------------------------------------------------
    # Very short audio
    # --------------------------------------------------------

    if duration < MIN_AUDIO_SECONDS:

        raise ValueError(
            "Audio is too short for reliable analysis."
        )

    # --------------------------------------------------------
    # If <= 4 seconds:
    # analyze once with padding
    # --------------------------------------------------------

    if total_samples <= NUM_SAMPLES:

        probability = predict_single_window(
            audio,
            sr
        )

        return probability, 1

    # --------------------------------------------------------
    # Create overlapping windows
    #
    # Example:
    #
    # 0-4 sec
    # 2-6 sec
    # 4-8 sec
    # 6-10 sec
    # ...
    # --------------------------------------------------------

    probabilities = []

    start = 0

    while start + NUM_SAMPLES <= total_samples:

        window = audio[
            start:start + NUM_SAMPLES
        ]

        probability = predict_single_window(
            window,
            sr
        )

        probabilities.append(
            probability
        )

        start += WINDOW_HOP

    # --------------------------------------------------------
    # Make sure the END of the audio is also analyzed
    # --------------------------------------------------------

    last_start = (
        total_samples - NUM_SAMPLES
    )

    if (
        len(probabilities) == 0
        or start - WINDOW_HOP != last_start
    ):

        final_window = audio[
            last_start:
            last_start + NUM_SAMPLES
        ]

        probability = predict_single_window(
            final_window,
            sr
        )

        probabilities.append(
            probability
        )

    # --------------------------------------------------------
    # Combine window predictions
    #
    # Mean gives the overall synthetic probability.
    # --------------------------------------------------------

    final_probability = float(
        np.mean(probabilities)
    )

    return (
        final_probability,
        len(probabilities)
    )


# ============================================================
# Risk engine
# ============================================================

def calculate_risk(
    synthetic_probability
):

    synthetic_probability = max(
        0.0,
        min(
            1.0,
            synthetic_probability
        )
    )

    risk_score = round(
        synthetic_probability * 100,
        1
    )

    # --------------------------------------------------------
    # LOW
    # --------------------------------------------------------

    if risk_score < 40:

        risk_level = "LOW"

        action = (
            "Continue call normally"
        )

        reason = (
            "Low probability of AI-generated voice"
        )

    # --------------------------------------------------------
    # MEDIUM
    # --------------------------------------------------------

    elif risk_score < 70:

        risk_level = "MEDIUM"

        action = (
            "Continue monitoring and "
            "consider secondary verification"
        )

        reason = (
            "Moderate synthetic voice probability"
        )

    # --------------------------------------------------------
    # HIGH
    # --------------------------------------------------------

    else:

        risk_level = "HIGH"

        action = (
            "Trigger secondary verification "
            "and transaction protection"
        )

        reason = (
            "High probability of AI-generated voice"
        )

    return {

        "risk_score": risk_score,

        "risk_level": risk_level,

        "synthetic_probability": round(
            synthetic_probability,
            4
        ),

        "reason": reason,

        "action": action
    }


# ============================================================
# Analyze audio bytes
# ============================================================

def analyze_audio_bytes(
    audio_bytes
):

    # --------------------------------------------------------
    # Decode audio
    # --------------------------------------------------------

    audio_buffer = io.BytesIO(
        audio_bytes
    )

    audio, sr = sf.read(
        audio_buffer,
        dtype="float32"
    )

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    duration = (
        len(audio) / sr
    )

    # --------------------------------------------------------
    # Sliding-window CNN analysis
    # --------------------------------------------------------

    synthetic_probability, windows_analyzed = (
        analyze_full_audio(
            audio,
            sr
        )
    )

    # --------------------------------------------------------
    # Risk calculation
    # --------------------------------------------------------

    risk = calculate_risk(
        synthetic_probability
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "status": "success",

        "sample_rate": sr,

        "audio_duration": round(
            duration,
            3
        ),

        "windows_analyzed": (
            windows_analyzed
        ),

        **risk
    }


# ============================================================
# Health endpoint
# ============================================================

@app.get("/health")
def health_check():

    return {

        "status": "ok",

        "service": "VoiceShield AI",

        "model": (
            "IndicTTS Voice Integrity CNN"
        ),

        "device": str(
            DEVICE
        )
    }


# ============================================================
# Audio analysis endpoint
# ============================================================

@app.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...)
):

    audio_bytes = await file.read()

    # --------------------------------------------------------
    # Empty file check
    # --------------------------------------------------------

    if not audio_bytes:

        return {

            "status": "error",

            "message": (
                "Empty audio file"
            )
        }

    try:

        result = analyze_audio_bytes(
            audio_bytes
        )

        result["filename"] = (
            file.filename
        )

        return result

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)
        }