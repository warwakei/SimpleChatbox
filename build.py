import subprocess
import sys
import os

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"✗ Ошибка при выполнении: {description}")
        sys.exit(1)
    print(f"✓ {description} завершено")

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Установка зависимостей
run_command(
    f"{sys.executable} -m pip install --upgrade pip",
    "Обновление pip"
)

run_command(
    f"{sys.executable} -m pip install -r requirements.txt",
    "Установка зависимостей из requirements.txt"
)

run_command(
    f"{sys.executable} -m pip install pyinstaller",
    "Установка PyInstaller"
)

# Сборка с PyInstaller
print(f"\n{'='*60}")
print("▶ Сборка приложения с PyInstaller")
print(f"{'='*60}")

result = subprocess.run([
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--name=SimpleChatbox',
    '--distpath=./dist',
    '--workpath=./build',
    '--specpath=./build',
    '--collect-all=PyQt5',
    '--hidden-import=PyQt5.sip',
    'main.py'
])

if result.returncode == 0:
    print(f"\n{'='*60}")
    print("✓ Сборка успешно завершена!")
    print(f"✓ Exe находится в: ./dist/SimpleChatbox.exe")
    print(f"{'='*60}\n")
else:
    print(f"\n{'='*60}")
    print("✗ Ошибка при сборке")
    print(f"{'='*60}\n")

sys.exit(result.returncode)

