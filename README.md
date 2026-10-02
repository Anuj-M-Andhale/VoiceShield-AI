# 🛡️ VoiceShield AI

### AI-Powered Voice Cloning & Synthetic Voice Detection

VoiceShield AI is an AI-based voice security system designed to detect **AI-generated / synthetic voices and voice-cloning attempts**.

The system analyzes an audio recording using a trained **Voice Integrity CNN**, generates a synthetic-voice probability, converts it into a risk score, and presents the result through an interactive security dashboard.

---

## 🚀 Key Features

- 🎙️ **AI-generated voice detection**
- 🧠 CNN-based voice integrity analysis
- 📊 Synthetic voice probability scoring
- ⚠️ Automatic risk classification
- 🔊 Audio file upload and analysis
- 📡 Sliding-window analysis for longer recordings
- 🎚️ Mel-spectrogram based feature representation
- 📈 Real-time analysis dashboard
- 📋 Voice analysis history
- 🚨 Threat alerts
- 🔐 Privacy-focused processing interface
- 👤 Secure login interface
- 📱 Responsive web interface
- 🖥️ CPU/GPU inference support

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      User / Caller   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   VoiceShield Web UI │
                    │ HTML + CSS + JS      │
                    └──────────┬───────────┘
                               │
                     Audio Upload / Recording
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI Backend  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Audio Preprocessing │
                    │                      │
                    │ • Stereo → Mono     │
                    │ • Resampling         │
                    │ • Normalization      │
                    │ • 4-sec windows      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Mel Spectrogram    │
                    │      Extraction      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Voice Integrity CNN  │
                    │      PyTorch         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Synthetic Probability│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Risk Engine      │
                    │ Low / Medium / High  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Security Dashboard   │
                    │ Score + Alerts +     │
                    │ Analysis History     │
                    └──────────────────────┘
```

---

## 🧠 AI Detection Pipeline

### 1. Audio Input

The system accepts an uploaded audio file through the `/analyze` FastAPI endpoint.

### 2. Audio Preprocessing

Audio is processed before being passed to the neural network:

- Stereo audio is converted to mono
- Audio is resampled to **16 kHz**
- DC offset is removed
- Audio is peak-normalized
- Input is converted to a fixed **4-second** representation

For longer recordings, the system analyzes overlapping 4-second windows with a **2-second hop**. 

### 3. Mel-Spectrogram

The processed waveform is converted into a Mel-spectrogram using:

```text
Sample Rate : 16,000 Hz
N_FFT       : 1024
Hop Length  : 256
Mel Bins    : 128
```

The spectrogram is converted to dB and standardized before CNN inference.

### 4. Voice Integrity CNN

The project uses a custom PyTorch CNN consisting of four convolutional blocks followed by adaptive average pooling and fully connected classification layers.

```text
Input
  ↓
Conv2D 1 → 32
  ↓
Conv2D 32 → 64
  ↓
Conv2D 64 → 128
  ↓
Conv2D 128 → 256
  ↓
Adaptive Average Pooling
  ↓
Fully Connected Layer
  ↓
2-Class Output
```

The trained checkpoint is loaded from:

```text
best_indictts_full_voice_integrity_cnn.pth
```

The model outputs two classes, with **Class 1 representing synthetic / TTS audio**. 

---

## 📊 Risk Assessment

The model's synthetic probability is converted into a risk score from **0–100**.

| Risk Score | Risk Level | System Action |
|---:|---|---|
| `< 40` | 🟢 LOW | Continue call normally |
| `40–69.9` | 🟡 MEDIUM | Continue monitoring and consider secondary verification |
| `≥ 70` | 🔴 HIGH | Trigger secondary verification and transaction protection |

The backend returns the risk score, risk level, synthetic probability, reason, and recommended action.

---

## 🌐 Web Dashboard

VoiceShield includes a security dashboard designed for monitoring voice threats.

### Dashboard Components

- Voice Security Dashboard
- Live call monitoring
- Voice analysis
- AI authenticity score
- Synthetic voice probability
- Threat alerts
- Analysis history
- Privacy protection
- Audio upload
- Threat simulation/demo mode

The frontend provides dedicated sections for live calls, voice analysis, threat alerts, history, settings, and documentation. 

---

## 🎙️ Audio Analysis

Users can upload an audio recording from the dashboard.

```text
Select Audio
     ↓
Preview Audio
     ↓
Analyze Audio
     ↓
FastAPI Backend
     ↓
CNN Prediction
     ↓
Risk Assessment
     ↓
Dashboard Result
```

The frontend sends the audio to:

```text
POST http://127.0.0.1:8000/analyze
```

using multipart form data.

---

## 📡 Real-Time Analysis

For live analysis, the frontend maintains the latest **five predictions** and calculates a moving average to smooth the AI probability before displaying the result.

The dashboard classifies the resulting probability as:

```text
AI Probability < 40%
        ↓
    Authentic

40% – 69%
        ↓
    Suspicious

≥ 70%
        ↓
   AI Generated
```



---

## 🔐 Privacy

The dashboard includes privacy-oriented features such as:

- Temporary audio processing
- Local voice-feature processing where applicable
- Ability to delete raw recordings after analysis
- Avoiding display of sensitive caller information

These are represented in the dashboard's privacy section.

> **Note:** These are application-level design features. Actual data retention and deployment privacy depend on how the system is deployed and configured.

---

## 🛠️ Tech Stack

### AI / Machine Learning

- Python
- PyTorch
- CNN
- Librosa
- NumPy
- Mel-spectrogram

### Backend

- FastAPI
- Uvicorn
- Python Multipart
- SoundFile

### Frontend

- HTML5
- CSS3
- JavaScript
- Web Audio API

### Model

- Voice Integrity CNN
- Trained checkpoint: `best_indictts_full_voice_integrity_cnn.pth`

The Python dependencies currently specified by the project are FastAPI, Uvicorn, python-multipart, NumPy, Librosa, SoundFile, and PyTorch.

---

## 📁 Project Structure

```text
VoiceShield-AI/
│
├── main.py
├── best_indictts_full_voice_integrity_cnn.pth
├── requirements.txt
│
├── index1.html
├── login.html
├── login.css
├── login.js
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd VoiceShield-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Backend

Start the FastAPI server with:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET /health
```

Audio analysis:

```text
POST /analyze
```

The `/health` endpoint reports the service status, model name, and inference device.

---

## 🖥️ Running the Frontend

Open:

```text
login.html
```

in a browser.

After successful login, the frontend redirects to:

```text
index1.html
```

The login interface validates:

- Name
- Email
- Password

and stores the logged-in user's name and email in `sessionStorage`.

For the dashboard's backend-connected analysis to work, make sure the FastAPI server is running on:

```text
http://127.0.0.1:8000
```

---

## 🔌 API Example

### Analyze Audio

**Endpoint**

```http
POST /analyze
```

**Request**

```bash
curl -X POST \
  http://127.0.0.1:8000/analyze \
  -F "file=@voice.wav"
```

### Example Response

```json
{
  "status": "success",
  "sample_rate": 16000,
  "audio_duration": 5.42,
  "windows_analyzed": 1,
  "risk_score": 82.4,
  "risk_level": "HIGH",
  "synthetic_probability": 0.824,
  "reason": "High probability of AI-generated voice",
  "action": "Trigger secondary verification and transaction protection",
  "filename": "voice.wav"
}
```

---

## 🧪 Demo Threat Mode

The dashboard also includes a **Test Threat** function for demonstration purposes.

It generates a simulated high-risk result with a synthetic probability of 92% and adds the event to the analysis history. This mode is intended for demonstrating the dashboard's alert and risk-management UI rather than evaluating the CNN.

---

## ⚠️ Important Notes

### Model Path

The backend currently expects the trained model at the configured project path:

```text
best_indictts_full_voice_integrity_cnn.pth
```

Make sure the checkpoint is available and the `MODEL_PATH` configuration in `main.py` matches your local project directory.

### Minimum Audio Duration

Audio shorter than **0.5 seconds** is rejected as too short for reliable analysis.

### Longer Audio

Longer recordings are divided into overlapping 4-second windows, and the final synthetic probability is calculated from the mean of the window predictions.

---

## 🎯 Use Cases

VoiceShield AI can serve as a prototype for:

- Financial call protection
- Voice-based fraud detection
- Call-center security
- Identity verification
- AI voice-cloning detection
- Deepfake voice screening
- Secure voice communication
- Synthetic speech detection

---

## 🔮 Future Improvements

Potential future extensions include:

- Multi-model ensemble detection
- Speaker verification
- Anti-spoofing models
- Noise-robust detection
- Improved real-time streaming inference
- Cloud deployment
- Authentication with a real backend
- Persistent database-backed analysis history
- Advanced threat analytics
- Model confidence calibration
- Support for additional languages and TTS systems
- Integration with telephony/call-center systems

---

## 📌 Project Status

**Current Status:** Working prototype

The project combines a trained CNN inference backend with a browser-based security dashboard for demonstrating synthetic voice detection and threat monitoring.

---

## 👥 Team

**VoiceShield AI**

Developed as an AI-based voice security and synthetic voice detection project.

---

## 📜 License

Add your preferred license here, for example:

```text
MIT License
```

If this project is being submitted for an academic/hackathon evaluation, update this section according to the event's requirements.

---

## ⭐ Acknowledgements

Built using:

- PyTorch
- Librosa
- FastAPI
- NumPy
- SoundFile
- HTML
- CSS
- JavaScript

---

### 🛡️ VoiceShield AI

**Detect synthetic voices. Protect trusted communication.**
