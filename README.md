# SimpleChatbox

VRChat chatbox utility that displays currently playing media from your PC. Integrates with [warwakei Media Engine](https://github.com/warwakei/MediaEngine) to fetch track information and sends it to VRChat via OSC protocol.

## Features

- Real-time display of currently playing media
- Customizable message format (multiple layout options)
- Custom status icons (playing/paused)
- Auto-send functionality with configurable delay
- PyQt5 GUI for easy configuration
- OSC integration with VRChat
- Persistent configuration storage

## Requirements

- Windows 10 or later
- VRChat with OSC enabled (port 9000)
- **[warwakei Media Engine](https://github.com/warwakei/MediaEngine)** - Required for fetching media information

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
2. Go to Settings → OSC
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

- **Message Format**: Choose how track info is displayed
  - Display (from API)
  - Artist - Track
  - Track - Artist
  - Track by Artist
  - Track only

- **Status Icons**: Customize playing/paused indicators
  - Default: ▶ (playing), ⏸ (paused)

- **Auto-send**: Enable automatic sending with custom delay

- **Advanced Settings**:
  - MediaEngine URL
  - VRChat IP and Port

## Usage

1. Start MediaEngine
2. Run SimpleChatbox
3. Click "Send to VRChat" to send current track
4. Or enable "Auto-send" for automatic updates

## License

MIT License
