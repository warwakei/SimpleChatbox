# SimpleChatbox                 
VRChat chatbox utility that displays currently playing media from your PC and system information. 
Integrates with [warwakei Media Engine](https://github.com/warwakei/MediaEngine) to fetch track information and sends it to VRChat via OSC protocol.


<img width="348" height="711" alt="image" src="https://github.com/user-attachments/assets/b311590f-082c-4f36-90ce-62cb397a31a4" />



## Features

- Real-time display of currently playing media
- System information display (CPU, RAM, temperatures)
- Customizable message format (multiple layout options)
- Custom status icons (playing/paused)
- Auto-send functionality with configurable delay
- PyQt5 GUI for easy configuration
- OSC integration with VRChat
- Persistent configuration storage
- Combine music and system info in one message

## What's New in v0.0.2

- **Time Display (TimeMSG)**: Show current time or custom time with auto-increment in messages
- **Status Message (StatusMSG)**: Add custom status messages with flexible positioning
- **Improved UI**: Better tab organization with CFG tab for configuration management
- **Save All Settings**: One-click button to save all current settings to config
- **Enhanced Button Styling**: Better visibility on hover with accent color highlighting
- **Simplified Time Controls**: Auto PC time or custom time with Enter-to-start functionality

## Requirements

- Windows 10 or later
- VRChat with OSC enabled (port 9000)
- **[warwakei Media Engine](https://github.com/warwakei/MediaEngine)** - Required for fetching media information
- Python 3.8+ (for running from source)

## Installation

### From Source

1. Install Python 3.8 or later
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

### From Executable

Simply run `SimpleChatbox.exe`

## Quick Start Guide

### Step 1: Install Media Engine

1. Download [warwakei Media Engine](https://github.com/warwakei/MediaEngine)
2. Run `MediaEngine.exe`
3. Select option `1` to install
4. The engine will be installed to `C:\Users\[YourUsername]\AppData\Roaming\warwakei\utility\`
5. It will automatically start in the background

### Step 2: Enable VRChat OSC

1. Open VRChat
2. Go to Wheel → Options → OSC → Turn it on
<img width="609" height="461" alt="image" src="https://github.com/user-attachments/assets/86e55ea7-5a57-4941-b70c-17dafff1c882" />

3. Make sure OSC is enabled (port 9000)

### Step 3: Run SimpleChatbox

1. Run `SimpleChatbox.exe` (or `python main.py` if from source)
2. Wait for connection to MediaEngine (should show "✓ Connected to MediaEngine")
3. Configure your preferences in the Settings tab
4. Click "Send to VRChat" or enable "Auto-send"

### Step 4: Enjoy

Your current track will now appear in VRChat chatbox!

## Configuration

The application stores settings in `config.json`. You can customize:

### Music Settings (MusicMSG Tab)
- **Message Format**: Choose how track info is displayed
  - Display (from API)
  - Artist - Track
  - Track - Artist
  - Track by Artist
  - Track only
- **Status Icons**: Customize playing/paused indicators
  - Default: ▶ (playing), ⏸ (paused)

### System Settings (SysMSG Tab)
- **Show System Info**: Enable/disable system information in messages
- **Message Separator**: Custom separator between music and system info
- **Display Options**:
  - CPU Usage (%)
  - RAM Usage (GB and %)
  - CPU Temperature (°C)
  - GPU Temperature (°C)

### Advanced Settings
- MediaEngine URL
- VRChat IP and Port

## Usage

1. Start MediaEngine
2. Run SimpleChatbox
3. Click "Send to VRChat" to send current track
4. Or enable "Auto-send" for automatic updates

## License

MIT License
