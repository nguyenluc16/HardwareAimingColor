
# Colorbot - Aimbot/Triggerbot with OpenCV and Arduino

## Overview
The **Colorbot** project is an automated aiming (aimbot) and shooting (triggerbot) system for video games, leveraging the **OpenCV** image processing library and an **Arduino Leonardo** (or Pro Micro) microcontroller combined with a **USB Host Shield**. The primary goal is to create a peripheral (HMI) solution that detects in-game objects via screen image processing and sends mouse simulation commands through Arduino, minimizing direct game memory interference and reducing detection by anti-cheat systems.

### Key Features
- **Object Detection**: Uses OpenCV with HSV filtering and contour detection to identify enemies based on color (e.g., purple outlines).
- **Mouse Simulation**: Arduino Leonardo emulates a HID (Human Interface Device) mouse to move and click.
- **HID Spoofing**: Modifies VID/PID to mimic a legitimate mouse and evade anti-cheat detection.
- **USB Host Shield Support**: Enables interaction with real mice or other peripherals.

### Hardware Requirements
- **PC**: ROG laptop i5 9300H, GTX 1050 4GB VRAM, Windows 11 Home (or equivalent).
- **Arduino**: Leonardo or Pro Micro (ATmega32u4).
- **USB Host Shield**: Optional for hooking real mouse input.
- **External Power**: 5V or 3.3V (recommended to avoid Bootloader mode).

### Software Requirements
- **Python**: 3.8 (recommended) or 3.12.
- **OpenCV**: Image processing library.
- **Arduino IDE**: For uploading firmware to Arduino.
- **Python Libraries**: `mss`, `pyserial`, `numpy`.

---

## Installation

### 1. Hardware Setup
1. **Connect Arduino Leonardo**:
   - Connect the Arduino to the PC via USB or use an external power source (5V/3.3V).
   - Ensure the Arduino does not enter Bootloader mode when powered directly via USB.
2. **USB Host Shield** (optional):
   - If used, solder the 5V and 3.3V power ports on the USB Host Shield for stable operation.
   - Refer to this setup video: [USB Host Shield Setup](https://www.youtube.com/watch?v=nBttwvgNOr8).

### 2. Software Setup
1. **Install Python**:
   - Download Python 3.8 from [python.org](https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe) or a newer version (e.g., 3.12).
   - Install and add Python to your PATH.
2. **Install Python Libraries**:
   - Open a terminal in the project directory and run:
     ```bash
     pip install -r requirements.txt
     ```
   - Required libraries: `opencv-python`, `mss`, `pyserial`, `numpy`.
3. **Install Arduino IDE**:
   - Download from [arduino.cc](https://www.arduino.cc/en/software).
   - Open the `arduino/Arduino.ino` file.

### 3. Upload Firmware to Arduino
1. Connect the Arduino Leonardo to your PC.
2. Open Arduino IDE, select the `Arduino Leonardo` board and the appropriate port.
3. Upload the `arduino/Arduino.ino` file to the Arduino.
   - This file uses the `Mouse.h` library to simulate mouse actions.

### 4. Run the Program
1. Ensure the Arduino is connected and firmware is uploaded.
2. Open a terminal in the project directory and run:
   ```bash
   python main.py
   ```
3. The program will start capturing the screen, detecting objects, and sending commands to the Arduino.

---

## Usage
1. **Configure FOV**: Adjust the Field of View (FOV) in `main.py` to match your game’s screen.
2. **Tune Color Thresholds**: Modify HSV values in `main.py` to detect the enemy’s distinctive color (e.g., purple outline).
3. **Launch the Game**: Run the game in windowed or borderless mode for accurate screen capture.
4. **Test**: Observe mouse movement and automatic shooting behavior in-game.

---

## Directory Structure
```
C:.
├───Client/            
├───Host/               
└───README.md           # This file
```

---

## Enhancements to Avoid Detection
To minimize detection by anti-cheat systems (e.g., Vanguard, Ricochet, EAC), consider these improvements:
1. **Natural Mouse Movement**:
   - Add random delays and Bezier curve trajectories in `Arduino.ino`.
2. **Dynamic VID/PID Spoofing**:
   - Change Arduino’s VID/PID in real-time to mimic various legitimate devices.
3. **Script Obfuscation**:
   - Convert `main.py` to an executable using PyInstaller:
     ```bash
     pyinstaller --onefile --hidden-import=opencv main.py
     ```
4. **Optimized Communication**:
   - Switch from Serial to custom USB HID using the `HID-Project` library.

Refer to the discussion section of the paper for detailed enhancement strategies.

---

## Notes
- **Risks**: This system is not guaranteed to be undetectable. Modern anti-cheat solutions may analyze mouse patterns or detect unusual HID devices, potentially leading to account or hardware (HWID) bans.
- **Compatibility**: Some mice (e.g., Logitech G Pro Superlight 2) may experience latency with the USB Host Shield. Update firmware or tweak HID settings as needed.
- **Legal**: Using aimbots/triggerbots violates the terms of service of most online games. Use this project for research purposes or in non-competitive environments only.

---

## References
- [OpenCV Documentation](https://docs.opencv.org/)
- [Arduino HID Project](https://github.com/NicoHood/HID)
- [Setup Video Guide](https://www.youtube.com/watch?v=NlUyUGYHMAc)

---

## Author
- **Nguyen Hieu Luc**  
- **Release Date**: April 03, 2025

---
