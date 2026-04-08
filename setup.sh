echo "--> Установка системных зависимостей..."
sudo apt update
sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev python3-dev python3-pip python3-setuptools python3-venv openjdk-17-jdk libtinfo6

echo "--> Клонирование проекта..."
git clone https://github.com/AgentEvgen/BrailleLearner.git
cd BrailleLearner

echo "--> Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "--> Установка Python библиотек..."
pip install --upgrade pip
pip install Cython==0.29.33 kivy buildozer setuptools

echo "--> Перенос конфигурации..."
mv buildozer/* .

echo "--> Запуск сборки APK..."
buildozer -v android debug

echo "--> Готово! Проверьте папку bin/"
