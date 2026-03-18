echo "--> Установка системных зависимостей..."
sudo apt update
sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev python3-dev python3-pip python3-setuptools python3-venv openjdk-17-jdk

echo "--> Клонирование проекта..."
git clone https://github.com/AgentEvgen/BrailleLearner.git
cd BrailleLearner

echo "--> Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "--> Установка Python библиотек..."
pip install --upgrade pip
pip install Cython kivy buildozer

echo "--> Перенос конфигурации..."
mv buildozer/* . 2>/dev/null || true

echo "--> Запуск сборки APK..."
buildozer -v android debug

echo "--> Готово! Проверьте папку bin/"
