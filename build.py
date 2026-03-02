import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=SimpleChatbox',
    '--icon=NONE',
    '--distpath=./dist',
    '--workpath=./build',
    '--specpath=./build',
])

