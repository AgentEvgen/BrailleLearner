import os
import subprocess
import shutil

REPO_URL = "https://github.com/AgentEvgen/BrailleLearner.git"
PROJECT_NAME = "BrailleLearner"

def run(command, shell=True):
    print(f"--> Выполняю: {command}")
    subprocess.run(command, shell=shell, check=True)

def main():
    if not os.path.exists(PROJECT_NAME):
        run(f"git clone {REPO_URL}")
    
    os.chdir(PROJECT_NAME)

    print("Установка зависимостей...")
    run("pip install kivy buildozer")

    buildozer_dir = "buildozer"
    if os.path.exists(buildozer_dir):
        print(f"Перенос файлов из {buildozer_dir} в корень...")
        for item in os.listdir(buildozer_dir):
            s = os.path.join(buildozer_dir, item)
            d = os.path.join(".", item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print("✅ Файлы конфигурации перенесены.")
    else:
        print("⚠️ Папка 'buildozer' не найдена, пропускаем перенос.")

    print("Начинаю конвертацию в APK (это может занять долгое время при первом запуске)...")
    try:
        run("buildozer -v android debug")
        print("\n" + "="*30)
        print("ГОТОВО! APK файл должен появиться в папке bin/")
        print("="*30)
    except Exception as e:
        print(f"❌ Ошибка при сборке: {e}")
        print("Убедитесь, что у вас установлены все зависимости для Buildozer (Java, Android SDK/NDK).")

if __name__ == "__main__":
    main()
