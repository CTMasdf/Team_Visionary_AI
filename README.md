# ✨ Visionary AI
### AI-based Assistive System for the Visually Impaired

Visionary AI is an AI-powered voice guidance assistive system designed to support visually impaired users in reading books and recognizing surrounding environments.

By integrating Raspberry Pi, Camera Module, OCR, Google Gemini API, and STT/TTS technologies, the system provides:

- 📖 Book Reading
- 📝 AI Book Summary
- 🌍 Surrounding Environment Recognition
- ❓ Voice-based Question Answering

---

## 📌 Project Overview

This project aims to improve accessibility for visually impaired individuals by combining:

- Camera-based image capture
- OCR text recognition
- Generative AI analysis
- Speech input/output interaction

Users can select different operating modes using a rotary encoder and push button, and all results are delivered through TTS voice guidance without requiring a screen.

---

## 🎯 Development Purpose

Visually impaired users often face limitations in reading printed materials and identifying surrounding objects in daily life.

Existing assistive devices are usually limited to digital content or specific environments.

**Visionary AI** was developed to provide a more practical all-in-one embedded AI solution that supports:

- Reading physical books
- Summarizing documents
- Understanding nearby environments
- Answering spoken questions

through a simple voice-based interface.

---

## 🧩 Main Features

### 📖 OCR-based Book Reading
Capture printed text using the camera and convert it into voice output.

### 📝 AI Book Summary
Recognize document text and summarize key points using Gemini API.

### 🌍 Surrounding Environment Recognition
Analyze nearby objects, people, and spaces through camera vision and provide voice descriptions.

### ❓ Question Answering Mode
Recognize user speech, generate AI-based answers, and respond via TTS.

### 🔊 Voice Guidance System
Provides STT/TTS interaction for completely screen-free operation.

### 🎛 Accessible User Interface
Rotary encoder, push buttons, and tactile controls enable easy mode selection.

---

## 🎬 Demo Videos

| Mode | Verified Operation | Demo |
|------|--------------------|------|
| Question Mode | Voice question → AI response → TTS output | YouTube |
| Environment Recognition | Camera input → Scene analysis → Voice guidance | YouTube |
| Book Summary Mode | Book capture → AI summary → TTS output | YouTube |
| Book Reading Mode | OCR text extraction → Voice reading | YouTube |

---

## 🛠 Tech Stack

### 💻 Software
- Python
- Raspberry Pi OS
- Google Gemini API
- Tesseract OCR
- STT / TTS
- GPIO Control

### 🔩 Hardware
- Raspberry Pi 4
- Camera Module
- Rotary Encoder
- Push Button
- Microphone
- Speaker
- 3D Printed Case

### 🌐 Interface / Communication
- GPIO
- Wi-Fi
- Voice I/O
- Camera Input

---

## 🏗 System Architecture

```text
User Input
 ├── Voice Input
 ├── Button Input
 └── Encoder Input

Input Devices
 ├── Camera Module
 ├── Microphone
 └── Rotary Encoder / Push Button

Raspberry Pi Processing
 ├── Mode Selection Logic
 ├── OCR Processing
 ├── Gemini API Request
 ├── STT Processing
 └── TTS Output

Output
 └── Voice Guidance through Speaker
