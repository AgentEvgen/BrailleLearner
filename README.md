# Braille Learner 

[![Лицензия: MIT](https://img.shields.io/badge/Лицензия-MIT-blue.svg)](./LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python)
![Kivy](https://img.shields.io/badge/Kivy-2.2%2B-ff6600?logo=kivy)

> **Braille Learner** — это приложение для изучения и практики азбуки Брайля.
> Подходит для учащихся, педагогов, лингвистов и всех, кто интересуется тактильной письменностью.

---

## Возможности

| Режим | Описание |
|-------|----------|
| **Обучение** | • Буквы и цифры разбиты по разным модулям с тестом после каждого <br> • В самом конце есть контрольный зачет по всем буквам  |
| **Практика** (3 уровня) | • *Лёгкий*: выбор из 2–10 вариантов <br> • *Средний*: ввод символов Брайля на виртуальной клавиатуре 2×3 <br> • *Сложный*: найди и исправь ошибку в слове  <br> • *Быстрое повторение*: ответ за ограниченное время |
| **Справочник** | • Полная таблица алфавита с опциональной **статистикой по каждому символу** (*верно/неверно*). |
| **Переводчик** | • Текст → Брайль <br> • Ввод точек Брайля → распознавание буквы |
| **Игры** | • Позволяет учить брайль легко и интересно <br> •  Есть игры как **МЕМО** или **Филворд**|

---

## Локализация
### Поддерживаемые алфавиты

| Код | Название |
|-----|----------|
| `en`  | English |
| `ru`  | Русский |
| `dru` | Дореволюціонный русскій |

## Добавление нового языка

Чтобы добавить новый язык, нужно:

1. Создать файл перевода интерфейса:
   - `assets/translations/<код_языка>.json`

2. Создать таблицу символов Брайля:
   - `assets/braille/<код_языка>.json`

3. При необходимости добавить список слов:
   - `assets/words/<код_языка>.txt`

После этого язык автоматически появится в настройках приложения.

---

## Быстрый старт

### Требования
- Python ≥ 3.10  
- [`kivy`](https://kivy.org/doc/stable/gettingstarted/installation.html)  
- Папка **assets** *(включена в репозиторий)*

### Сборка
Используйте файл **setup.sh**, либо проделайте эти шаги вручную:
```bash
# Скачайте необходимые зависимости
sudo apt update
sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev python3-dev python3-pip python3-setuptools python3-venv openjdk-17-jdk libtinfo6

# Скачайте данный проект
git clone https://github.com/AgentEvgen/BrailleLearner.git
cd BrailleLearner

# Создайте и активируйте виртуальное окружение (venv)
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install Cython==0.29.33 kivy buildozer
pip install --upgrade pip setuptools

# Переместите файлы из подпапки buildozer в корень проекта
mv buildozer/* .

# Запустите сборку
buildozer -v android debug
```

---

## Скриншоты

| <img src="./Screenshots/1.jpg" alt="Средний режим" /> | <img src="./Screenshots/2.jpg" alt="Сложный режим" /> | <img src="./Screenshots/3.jpg" alt="Справочник" /> |
| ----------------------------------------- | ----------------------------------------- | ----------------------------------------- |
| <img src="./Screenshots/4.jpg" alt="Переводчик" /> | <img src="./Screenshots/5.jpg" alt="Результаты теста по уроку" /> | <img src="./Screenshots/6.jpg" alt="Игра в МЕМО" /> |
