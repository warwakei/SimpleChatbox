# SimpleChatbox

VRChat chatbox utility that displays currently playing media from your PC. Integrates with MediaEngine to fetch track information and sends it to VRChat via OSC protocol.

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
- MediaEngine running on localhost:5000

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
