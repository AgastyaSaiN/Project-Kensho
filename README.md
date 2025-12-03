<div align="center">
  <img src="src/kensho/resources/logo.png" alt="Kensho Logo" width="180">
  <h1>Kenshō</h1>
  <p><strong>Find your flow.</strong></p>
  
  ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
  ![PySide6](https://img.shields.io/badge/GUI-PySide6-green?style=for-the-badge&logo=qt)
  ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)
</div>

<br>

**Kenshō** (見性) is a Zen term meaning *"seeing one's true nature."* 
This application is a minimalist, distraction-free focus timer designed to help you enter a state of deep work and flow. Unlike traditional timers, Kenshō uses **concentric breathing rings** to visualize time, creating a calming rather than stressful experience.

---

## ⬇️ Download & Install

**The easiest way to use Kenshō is to download the installer.**

1.  Go to the [**Releases**](../../releases) (or the `dist/` folder).
2.  Download **`Kensho-1.0-win64.msi`**.
3.  Double-click to install.
4.  Launch **Kensho** from your Desktop or Start Menu.

---

## ✨ Features

### 🧘 Zen Interface
- **Concentric Rings**: Time is visualized as beautiful, anti-aliased rings that pulse gently.
- **Dark Mode**: A premium, deep-dark theme designed to reduce eye strain.
- **Distraction-Free**: No clutter, just your focus goals.

### 🪟 Widget Mode
- **Always-on-Top**: Switch to a tiny, translucent floating widget that stays above your work.
- **Interactive**: Click to expand back to the full dashboard.
- **Draggable**: Place it anywhere on your screen.

### 🎵 Soundscapes
- **Natural Notifications**: Forget jarring alarm clocks. Kenshō uses high-quality samples of real instruments:
  - 🎹 **Piano**
  - 🎸 **Guitar**
  - 🎐 **Kalimba**
  - 🎋 **Flute**
  - 🎼 **Koto**

### 📊 History & Data
- **Session Tracking**: Automatically logs every completed focus session.
- **Daily Stats**: See your total focus time for the day at a glance.
- **Persistence**: Your clocks, settings, and history are auto-saved.

---

## 🛠️ Build from Source

If you are a developer and want to modify Kenshō:

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/AgastyaSaiN/Kenshow.git
    cd Kenshow
    ```

2.  **Install Dependencies**:
    ```bash
    pip install PySide6 cx_Freeze
    ```

3.  **Run**:
    ```bash
    python run.py
    ```

4.  **Build Installer**:
    ```bash
    python setup.py bdist_msi
    ```

---

## 📂 Data Location
Your data is stored locally in your user directory:
`C:\Users\<You>\.kensho\`

---

<div align="center">
  <sub>Built with 💜 using Python & Qt</sub>
</div>
