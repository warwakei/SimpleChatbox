import subprocess
import sys
import os

# Собрать с PyInstaller
result = subprocess.run([
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--name=SimpleChatbox',
    '--distpath=./dist',
    '--workpath=./build',
    '--specpath=./build',
    'main.py'
], cwd=os.path.dirname(os.path.abspath(__file__)))

sys.exit(result.returncode)

