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

This project aims to improve accessibility for visually impaired individuals by combining camera-based image recognition, OCR text extraction, generative AI analysis, and speech interaction.

Users can select operating modes using a rotary encoder and push button, and all results are delivered through TTS voice guidance without requiring a screen.

---

## 🎯 Development Purpose

Visually impaired users often experience difficulties in reading printed materials and recognizing surrounding objects in daily life.

Existing assistive devices are mostly limited to digital environments or specific use cases.

**Visionary AI** was developed as an all-in-one embedded AI assistive system capable of:

- Reading physical books
- Summarizing documents
- Understanding nearby environments
- Answering spoken questions

through a simple and intuitive voice-based interface.

---

## 🧩 Main Features

### 📖 OCR-based Book Reading
Capture printed text using the camera and convert it into voice output.

### 📝 AI Book Summary
Recognize document text and summarize the core content using Gemini API.

### 🌍 Surrounding Environment Recognition
Analyze nearby objects, people, and spaces through camera vision and provide voice descriptions.

### ❓ Question Answering Mode
Recognize user speech, generate AI-based answers, and respond through TTS.

### 🔊 Voice Guidance System
Provides STT/TTS interaction for completely screen-free operation.

### 🎛 Accessible User Interface
Rotary encoder, push buttons, and tactile controls enable easy mode selection.

---

## 🎬 Demo Videos

| Mode | Verified Operation | Demo Link |
|------|--------------------|-----------|
| Question Mode | Voice question → AI response → TTS output | [Watch Video](https://www.youtube.com/watch?v=l_isw-CAqvM&list=PLOjdgAZ8zigZPNQvOKNYUYLnqQgklHo9C) |
| Environment Recognition | Camera input → Scene analysis → Voice guidance | [Watch Video](https://www.youtube.com/watch?v=1s9kkLBiONs&list=PLOjdgAZ8zigZPNQvOKNYUYLnqQgklHo9C&index=2) |
| Book Summary Mode | Book capture → AI summary → TTS output | [Watch Video](https://www.youtube.com/watch?v=e7Ha-5QWRIQ&list=PLOjdgAZ8zigZPNQvOKNYUYLnqQgklHo9C&index=3) |
| Book Reading Mode | OCR text extraction → Voice reading | [Watch Video](https://www.youtube.com/watch?v=5utNRFC141A&list=PLOjdgAZ8zigZPNQvOKNYUYLnqQgklHo9C&index=4) |

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

🔄 Operation Flow
User selects a mode using the rotary encoder.
Presses the button to execute the selected function.
Camera or microphone collects input data.
OCR / Gemini API analyzes the information.
Result is converted into TTS voice.
Speaker provides voice guidance to the user.
👥 Team
Role	Responsibility
Team Leader	Project planning & system architecture
Hardware Integration	Raspberry Pi integration & device connection
AI / Software	OCR, Gemini API, STT/TTS implementation
Product Design	3D modeling & case design
System Test	Camera integration & total system verification
🙋‍♂️ My Role

Team Leader | 5 Members

Overall project planning
System architecture design
Raspberry Pi function integration
Camera module testing
3D printed case modeling
Hardware assembly
Final system integration test

✅ Expected Effects
Improved reading accessibility for visually impaired users
Better daily environment recognition assistance
Intuitive screen-free voice interaction
Practical low-cost embedded assistive device possibility
Experience in integrating AI Vision + OCR + STT/TTS + Embedded System
📅 Project Period

2025.09 ~ 2025.12

📎 Demo Playlist

▶ Full Demo Playlist
https://www.youtube.com/playlist?list=PLOjdgAZ8zigZPNQvOKNYUYLnqQgklHo9C

📝 License

This project was developed for educational and capstone design purposes.
