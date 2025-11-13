from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, DictProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.utils import platform
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from collections import OrderedDict
import json
import random
import math
import time

# Основные настройки
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'resizable', '1')
LabelBase.register(name='BrailleFont', fn_regular='DejaVuSans.ttf')

# KV-описание интерфейса
Builder.load_string('''
<BaseButton@Button>:
    font_size: dp(22)
    size_hint_y: None
    height: dp(80)
    padding: dp(10), dp(10)

<BaseScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(8)
        Label:
            text: root.menu_title
            font_size: dp(26)
            font_name: 'BrailleFont' 
            size_hint_y: None
            height: dp(45)
            halign: 'center'
            valign: 'middle'
        ScrollView:
            size_hint_y: 1
            bar_width: dp(6)
            bar_inactive_color: [0.6, 0.6, 0.6, 1]
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(20), dp(10)]
                spacing: dp(15)
                BaseButton:
                    text: root.training_btn
                    on_press: root.manager.current = 'learning'
                BaseButton:
                    id: practice_btn
                    text: root.practice_btn
                    on_press: root.manager.current = 'practice_levels'
                BaseButton:
                    text: root.reference_btn
                    on_press: root.manager.current = 'reference'
                BaseButton:
                    text: root.translator_btn
                    on_press: root.manager.current = 'translator'
                BaseButton:
                    text: root.settings_btn
                    on_press: root.manager.current = 'settings'
        Widget:
            size_hint_y: None
            height: dp(15)


<LearningScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)
        Label:
            text: root.current_letter
            font_size: dp(48)
            size_hint_y: None
            height: dp(80)
            halign: 'center'
            valign: 'middle'
        Label:
            text: root.braille_char
            font_name: 'BrailleFont'
            font_size: dp(120)
            size_hint_y: 0.6
            halign: 'center'
            valign: 'middle'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(60)
            spacing: dp(20)
            BaseButton:
                text: '<< ' + root.prev_btn
                on_press: root.prev_character()
            Label:
                text: f'{root.current_index + 1}/{root.total_chars}'
                font_size: dp(18)
                size_hint_x: None
                width: dp(80)
                halign: 'center'
                valign: 'middle'
            BaseButton:
                text: root.next_btn + ' >>'
                on_press: root.next_character()
        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: root.manager.current = 'menu'

<PracticeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(45)
            spacing: dp(10)
            Label:
                text: root.streak_text.split('\\n')[0] if '\\n' in root.streak_text else root.streak_text
                font_size: dp(16)
                halign: 'left'
            Label:
                text: root.streak_text.split('\\n')[1] if '\\n' in root.streak_text else ''
                font_size: dp(16)
                halign: 'right'
            Label:
                text: str(root.time_left) if root.quick_review_mode else ''
                font_size: dp(20)
                halign: 'right'
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.3
            padding: dp(10)
            Label:
                text: root.braille_char
                font_name: 'BrailleFont'
                font_size: dp(80) if self.height > dp(600) else dp(50)
                size_hint: (0.8, 0.8)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        GridLayout:
            id: answers_grid
            cols: 1
            spacing: dp(5)
            size_hint_y: 0.6
            padding: dp(5)
            row_default_height: dp(80)
        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: root.manager.current = 'practice_levels'

<MediumPracticeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        Label:
            text: root.streak_text
            font_size: dp(18)
            size_hint_y: None
            height: dp(45)
            halign: 'center'
            valign: 'middle'

        Label:
            text: root.current_letter
            font_size: dp(48)
            size_hint_y: 0.15
            halign: 'center'
            valign: 'middle'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.4
            spacing: dp(15)

            GridLayout:
                cols: 2
                rows: 3
                spacing: dp(20)
                padding: dp(10)
                size_hint: None, None
                width: self.minimum_width
                height: self.minimum_height
                pos_hint: {'center_x': 0.5}

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(60)
                    height: dp(60)
                    size_hint: None, None
                    on_press: root.on_dot_press(0, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot1

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(60)
                    height: dp(60)
                    size_hint: None, None
                    on_press: root.on_dot_press(3, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot4

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(60)
                    height: dp(60)
                    size_hint: None, None
                    on_press: root.on_dot_press(1, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot2

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(60)
                    height: dp(60)
                    size_hint: None, None
                    on_press: root.on_dot_press(4, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot5

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(60)
                    height: dp(60)
                    size_hint: None, None
                    on_press: root.on_dot_press(2, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot3

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(60)
                    height: dp(60)
                    size_hint: None, None
                    on_press: root.on_dot_press(5, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot6

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15
            spacing: dp(30)
            padding: [dp(40), 0]

            BaseButton:
                id: confirm_btn
                text: root.confirm_btn
                size_hint: 0.45, None
                height: dp(50)
                on_press: root.confirm_answer()
                background_disabled_normal: self.background_normal
                background_disabled_down: self.background_down

            BaseButton:
                id: clear_btn
                text: root.clear_btn
                size_hint: 0.45, None
                height: dp(50)
                on_press: root.clear_input()
                background_disabled_normal: self.background_normal
                background_disabled_down: self.background_down

        BoxLayout:
            size_hint_y: 0.1
            padding: [dp(40), dp(10), dp(40), 0]

            BaseButton:
                text: root.back_btn
                size_hint: 1, None
                height: dp(50)
                pos_hint: {'center_x': 0.5}
                on_press: 
                    root.manager.current = 'practice_levels'

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        Label:
            text: root.settings_title
            font_size: dp(24)
            size_hint_y: None
            height: dp(45)
            halign: 'center'

        ScrollView:
            bar_width: dp(6)
            bar_inactive_color: [0.6, 0.6, 0.6, 1]
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(15)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.language_label
                        size_hint_x: None
                        width: dp(100)
                    Spinner:
                        id: lang_spinner
                        text: root.current_lang
                        values: root.languages.values()
                        size_hint_x: None
                        width: dp(150) if app.is_mobile else dp(200)
                        on_text: root.update_settings('language', self.text)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.difficulty_label
                        size_hint_x: None
                        width: dp(100)
                    Spinner:
                        id: difficulty_spinner
                        text: root.current_difficulty_str
                        values: root.difficulty_values
                        size_hint_x: None
                        width: dp(150) if app.is_mobile else dp(200)
                        on_text: root.update_settings('difficulty', self.text)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.time_label
                        size_hint_x: None
                        width: dp(150)
                    TextInput:
                        id: time_input
                        text: str(app.quick_review_time)
                        hint_text: root.time_hint
                        input_filter: 'int'
                        size_hint_x: None
                        width: dp(150) if app.is_mobile else dp(200)
                        on_text: root.update_settings('time', self.text)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.use_stats
                        size_hint_x: None
                        width: dp(250)
                    Switch:
                        id: interval_switch
                        active: app.use_stats
                        on_active: root.update_update_use_stats(self.active)

                BaseButton:
                    text: root.reset_stats_btn
                    height: dp(50)
                    on_press: root.reset_stats()

        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: root.manager.current = 'menu'

<ReferenceScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        Label:
            text: root.reference_title
            font_size: dp(28)
            size_hint_y: None
            height: dp(45)
            halign: 'center'
            valign: 'middle'
        ScrollView:
            bar_width: dp(10)
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(20), dp(10)]
                GridLayout:
                    id: reference_grid
                    cols: 2
                    spacing: dp(20)
                    size_hint_y: None
                    height: self.minimum_height
        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: root.manager.current = 'menu'

<TranslatorScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)
        
        Label:
            text: root.translator_title
            font_size: dp(26)
            size_hint_y: None
            height: dp(45)
            halign: 'center'
            valign: 'middle'

        TextInput:
            id: input_text
            hint_text: root.input_hint
            size_hint_y: None
            height: dp(100)
            multiline: True
            padding: dp(10)

        # Горизонтальный контейнер для кнопок
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(5)
            padding: 0

            # Кнопка "Перевести"
            BaseButton:
                text: root.translate_btn
                size_hint: (1, 1)
                height: dp(60)
                on_press: root.translate_text()

            # Кнопка "Ввод Брайля"
            BaseButton:
                text: root.input_braille_btn
                size_hint: (1, 1)
                height: dp(60)
                on_press: root.open_braille_input()

        # Единый контейнер для вывода Брайля и панели ввода
        FloatLayout:
            size_hint_y: 0.45  

            # Область вывода Брайля
            ScrollView:
                id: braille_output_container
                size_hint: (0.95, 0.9) 
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                bar_width: dp(10)

                BoxLayout:
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'

                    Label:
                        id: braille_output
                        text: ''
                        font_name: 'BrailleFont'
                        font_size: dp(32)
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: (self.width, None)
                        halign: 'center'
                        valign: 'top'
                        padding: dp(10), dp(10)
                        pos_hint: {'center_x': 0.5}
                        width: self.parent.width  # Растягивается по ширине контейнера

            # Панель ввода Брайля (поверх вывода)
            BoxLayout:
                id: braille_input_panel
                orientation: 'vertical'
                size_hint: (0.8, 0.8)  # Занимает 80% ширины и высоты FloatLayout
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}  # Центрирование
                opacity: 0
                disabled: True

                # Строки кнопок
                BoxLayout:
                    size_hint_y: 0.25
                    spacing: dp(5)
                    padding: dp(5)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(0)
                        id: dot1
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(3)
                        id: dot4
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                BoxLayout:
                    size_hint_y: 0.25
                    spacing: dp(5)
                    padding: dp(5)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(1)
                        id: dot2
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(4)
                        id: dot5
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                BoxLayout:
                    size_hint_y: 0.25
                    spacing: dp(5)
                    padding: dp(5)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(2)
                        id: dot3
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(5)
                        id: dot6
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                # Кнопки управления
                BoxLayout:
                    size_hint_y: 0.25
                    spacing: dp(10)
                    padding: dp(5)

                    BaseButton:
                        text: root.confirm_btn
                        size_hint: 0.5, 1
                        height: dp(60)
                        on_press: root.confirm_braille_input()

                    BaseButton:
                        text: root.clear_btn
                        size_hint: 0.5, 1
                        height: dp(60)
                        on_press: root.clear_braille_input()

        # Кнопка "Назад"
        BaseButton:
            text: root.back_btn
            size_hint_y: None
            height: dp(50)
            on_press: root.manager.current = 'menu'

<PracticeLevelsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(8)
        Label:
            text: root.title
            font_size: dp(26)
            size_hint_y: None
            height: dp(60)
            halign: 'center'
            valign: 'middle'
        ScrollView:
            size_hint_y: 1
            bar_width: dp(6)
            bar_inactive_color: [0.6, 0.6, 0.6, 1]
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(20), dp(10)]
                spacing: dp(15)
                BaseButton:
                    text: root.easy_level_btn
                    on_press: root.start_easy_level()
                BaseButton:
                    text: root.medium_level_btn
                    on_press: root.start_medium_level()
                BaseButton:
                    text: root.hard_level_btn
                    on_press: root.show_coming_soon()
                BaseButton:
                    text: root.quick_review_btn
                    on_press: root.start_quick_review()
        BaseButton:
            text: root.back_btn
            size_hint_y: None
            height: dp(50)
            on_press: root.manager.current = 'menu'
''')

# Данные Брайля
braille_data = {
    'en': OrderedDict(sorted({
                                 'A': [1, 0, 0, 0, 0, 0], 'B': [1, 1, 0, 0, 0, 0], 'C': [1, 0, 0, 1, 0, 0],
                                 'D': [1, 0, 0, 1, 1, 0], 'E': [1, 0, 0, 0, 1, 0], 'F': [1, 1, 0, 1, 0, 0],
                                 'G': [1, 1, 0, 1, 1, 0], 'H': [1, 1, 0, 0, 1, 0], 'I': [0, 1, 0, 1, 0, 0],
                                 'J': [0, 1, 0, 1, 1, 0], 'K': [1, 0, 1, 0, 0, 0], 'L': [1, 1, 1, 0, 0, 0],
                                 'M': [1, 0, 1, 1, 0, 0], 'N': [1, 0, 1, 1, 1, 0], 'O': [1, 0, 1, 0, 1, 0],
                                 'P': [1, 1, 1, 1, 0, 0], 'Q': [1, 1, 1, 1, 1, 0], 'R': [1, 1, 1, 0, 1, 0],
                                 'S': [0, 1, 1, 1, 0, 0], 'T': [0, 1, 1, 1, 1, 0], 'U': [1, 0, 1, 0, 0, 1],
                                 'V': [1, 1, 1, 0, 0, 1], 'W': [0, 1, 0, 1, 1, 1], 'X': [1, 0, 1, 1, 0, 1],
                                 'Y': [1, 0, 1, 1, 1, 1], 'Z': [1, 0, 1, 0, 1, 1]}.items())),
    'ru': OrderedDict([
        ('А', [1, 0, 0, 0, 0, 0]), ('Б', [1, 1, 0, 0, 0, 0]), ('В', [0, 1, 0, 1, 1, 1]),
        ('Г', [1, 1, 0, 1, 1, 0]), ('Д', [1, 0, 0, 1, 1, 0]), ('Е', [1, 0, 0, 0, 1, 0]),
        ('Ё', [1, 0, 0, 0, 0, 1]), ('Ж', [0, 1, 0, 1, 1, 0]), ('З', [1, 0, 1, 0, 1, 1]),
        ('И', [0, 1, 0, 1, 0, 0]), ('Й', [1, 1, 1, 1, 0, 1]), ('К', [1, 0, 1, 0, 0, 0]),
        ('Л', [1, 1, 1, 0, 0, 0]), ('М', [1, 0, 1, 1, 0, 0]), ('Н', [1, 0, 1, 1, 1, 0]),
        ('О', [1, 0, 1, 0, 1, 0]), ('П', [1, 1, 1, 1, 0, 0]), ('Р', [1, 1, 1, 0, 1, 0]),
        ('С', [0, 1, 1, 1, 0, 0]), ('Т', [0, 1, 1, 1, 1, 0]), ('У', [1, 0, 1, 0, 0, 1]),
        ('Ф', [1, 1, 0, 1, 0, 0]), ('Х', [1, 1, 0, 0, 1, 0]), ('Ц', [1, 0, 0, 1, 0, 0]),
        ('Ч', [1, 1, 1, 1, 1, 0]), ('Ш', [1, 0, 0, 0, 1, 1]), ('Щ', [1, 0, 1, 1, 0, 1]),
        ('Ъ', [1, 1, 1, 0, 1, 1]), ('Ы', [0, 1, 1, 1, 0, 1]), ('Ь', [0, 1, 1, 1, 1, 1]),
        ('Э', [0, 1, 0, 1, 0, 1]), ('Ю', [1, 1, 0, 0, 1, 1]), ('Я', [1, 1, 0, 1, 0, 1])]),
    'dru': OrderedDict([
    ('А', [1, 0, 0, 0, 0, 0]), ('Б', [1, 1, 0, 0, 0, 0]),
    ('В', [0, 1, 0, 1, 1, 1]), ('Г', [1, 1, 0, 1, 1, 0]), ('Д', [1, 0, 0, 1, 1, 0]),
    ('Е', [1, 0, 0, 0, 1, 0]), ('Ж', [0, 1, 0, 1, 1, 0]), ('З', [1, 0, 1, 0, 1, 1]),
    ('И', [0, 1, 0, 1, 0, 0]), ('І', [1, 0, 1, 0, 1, 1]), ('К', [1, 0, 1, 0, 0, 0]),
    ('Л', [1, 1, 1, 0, 0, 0]), ('М', [1, 0, 1, 1, 0, 0]), ('Н', [1, 0, 1, 1, 1, 0]),
    ('О', [1, 0, 1, 0, 1, 0]), ('П', [1, 1, 1, 1, 0, 0]), ('Р', [1, 1, 1, 0, 1, 0]),
    ('С', [0, 1, 1, 1, 0, 0]), ('Т', [0, 1, 1, 1, 1, 0]), ('У', [1, 0, 1, 0, 0, 1]),
    ('Ф', [1, 1, 0, 1, 0, 0]), ('Х', [1, 1, 0, 0, 1, 0]), ('Ц', [1, 0, 0, 1, 0, 0]),
    ('Ч', [1, 1, 1, 1, 1, 0]), ('Ш', [1, 0, 0, 0, 1, 1]), ('Щ', [1, 0, 1, 1, 0, 1]),
    ('Ъ', [1, 1, 1, 0, 1, 1]), ('Ы', [0, 1, 1, 1, 0, 1]), ('Ь', [0, 1, 1, 1, 1, 1]),
    ('Э', [0, 1, 0, 1, 0, 1]), ('Ю', [1, 1, 0, 0, 1, 1]), ('Я', [1, 1, 0, 1, 0, 1]),
    ('Ѳ', [1, 1, 0, 1, 1, 1]), ('Ѵ', [1, 0, 0, 0, 1, 0])    ])
}

# Переводы
translations = {
    'en': {
        'menu_title': 'Main Menu',
        'practice_btn': 'Practice',
        'reference_btn': 'Reference',
        'settings_btn': 'Settings',
        'translator_btn': 'Translator',
        'settings_title': 'Settings',
        'language_label': 'Language:',
        'back_btn': 'Back',
        'streak': 'Current streak: {}\nRecord: {}',
        'reference_title': 'Reference',
        'difficulty_label': 'Difficulty:',
        'difficulty_2': '2 options',
        'difficulty_4': '4 options',
        'difficulty_6': '6 options',
        'difficulty_8': '8 options',
        'difficulty_10': '10 options',
        'translator_title': 'Translator',
        'input_hint': 'Enter text here',
        'translate_btn': 'Translate',
        'training_btn': 'Training',
        'practice_levels_title': 'Practice Levels',
        'easy_level': 'Easy Level',
        'medium_level': 'Medium Level',
        'hard_level': 'Hard Level',
        'quick_review': 'Quick Review',
        'coming_soon': 'Coming Soon!',
        'time_label': 'Time per answer (sec):',
        'time_hint': 'Enter time',
        'prev': 'Previous',
        'next': 'Next',
        'use_stats': 'Use Statistics',
        'reset_stats_btn': 'Reset Statistics',
        'reset_stats_title': 'Reset Statistics',
        'reset_stats_text': 'Are you sure you want to reset all statistics?',
        'yes': 'Yes',
        'no': 'No',
        'stats_label': 'Correct: {} \n Wrong: {}',
        "confirm_btn": "Confirm",
        "clear_btn": "Clear",
        'input_braille_btn': 'Input Braille',
    },
    'ru': {
        'menu_title': 'Главное меню',
        'practice_btn': 'Практика',
        'reference_btn': 'Справочник',
        'settings_btn': 'Настройки',
        'translator_btn': 'Переводчик',
        'settings_title': 'Настройки',
        'language_label': 'Язык:',
        'back_btn': 'Назад',
        'streak': 'Текущая серия: {}\nРекорд: {}',
        'reference_title': 'Справочник',
        'difficulty_label': 'Сложность:',
        'difficulty_2': '2 варианта',
        'difficulty_4': '4 варианта',
        'difficulty_6': '6 вариантов',
        'difficulty_8': '8 вариантов',
        'difficulty_10': '10 вариантов',
        'translator_title': 'Переводчик',
        'input_hint': 'Введите текст',
        'translate_btn': 'Перевести',
        'training_btn': 'Обучение',
        'practice_levels_title': 'Уровни практики',
        'easy_level': 'Простой уровень',
        'medium_level': 'Средний уровень',
        'hard_level': 'Сложный уровень',
        'quick_review': 'Быстрое повторение',
        'coming_soon': 'Скоро будет!',
        'time_label': 'Время на ответ (сек):',
        'time_hint': 'Введите время',
        'prev': 'Предыдущий',
        'next': 'Следующий',
        'use_stats': 'Использовать статистику',
        'reset_stats_btn': 'Сбросить статистику',
        'reset_stats_title': 'Сброс статистики',
        'reset_stats_text': 'Вы уверены, что хотите сбросить всю статистику?',
        'yes': 'Да',
        'no': 'Нет',
        'stats_label': 'Правильно: {} \n Ошибок: {}',
        "confirm_btn": "Подтвердить",
        "clear_btn": "Очистить",
        'input_braille_btn': 'Ввод Брайля',
    },
    'dru': {
    'menu_title': 'Главное меню',
    'practice_btn': 'Практика',
    'reference_btn': 'Справочникъ',
    'settings_btn': 'Настройки',
    'translator_btn': 'Переводчикъ',
    'settings_title': 'Настройки',
    'language_label': 'Языкъ:',
    'back_btn': 'Назадъ',
    'streak': 'Текущая серія: {}\nРекордъ: {}',
    'reference_title': 'Справочникъ',
    'difficulty_label': 'Сложность:',
    'difficulty_2': '2 варіанта',
    'difficulty_4': '4 варіанта',
    'difficulty_6': '6 варіантовъ',
    'difficulty_8': '8 варіантовъ',
    'difficulty_10': '10 варіантовъ',
    'translator_title': 'Переводчикъ',
    'input_hint': 'Введите текстъ',
    'translate_btn': 'Перевести',
    'training_btn': 'Обученіе',
    'practice_levels_title': 'Уровни практики',
    'easy_level': 'Простой уровень',
    'medium_level': 'Средній уровень',
    'hard_level': 'Сложный уровень',
    'quick_review': 'Быстрое повтореніе',
    'coming_soon': 'Скоро будетъ!',
    'time_label': 'Время на отвѣтъ (сѣкъ):',
    'time_hint': 'Введите время',
    'prev': 'Предыдущій',
    'next': 'Слѣдующій',
    'use_stats': 'Использовать статистику',
    'reset_stats_btn': 'Сбросить статистику',
    'reset_stats_title': 'Сбросъ статистики',
    'reset_stats_text': 'Вы увѣрены, что хотите сбросить всю статистику?',
    'yes': 'Да',
    'no': 'Нѣтъ',
    'stats_label': 'Правильно: {} \n Ошибокъ: {}',
    "confirm_btn": "Подтвердить",
    "clear_btn": "Очистить",
    'input_braille_btn': 'Вводъ ​Брайля​',
    }
}

LANGUAGES = {'en': 'English', 'ru': 'Русский', 'dru': 'Дореволюціонный русскій'}


class BaseScreen(Screen):
    back_btn = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.update_lang()

    def on_pre_enter(self, *args):
        self.app = App.get_running_app()
        self.update_lang()

    def update_lang(self):
        self.back_btn = self.get_translation('back_btn')

    def get_translation(self, key):
        return translations[self.app.current_language][key]

    def load_braille_data(self):
        self.braille_data = self.app.braille_data[self.app.current_language]

    def get_braille_char(self, dots):
        code = 0x2800
        for i, val in enumerate(dots):
            if val:
                code += 2 ** i
        return chr(code)

    def calculate_weight(self, char, current_time):
        stat = self.app.stats[self.app.current_language].get(char, {'correct': 0, 'wrong': 0, 'last_seen': 0})
        last_seen = stat.get('last_seen', 0)

        if last_seen == 0:
            last_seen = current_time - 3600

        days_passed = (current_time - last_seen) / 86400
        decay = 0.9 ** days_passed
        decayed_wrong = stat['wrong'] * decay
        decayed_correct = stat['correct'] * decay

        total_attempts = decayed_correct + decayed_wrong
        error_rate = decayed_wrong / total_attempts if total_attempts > 0 else 0.5

        total_stats = self.app.stats[self.app.current_language]
        all_wrong = sum(stat['wrong'] for stat in total_stats.values())
        all_correct = sum(stat['correct'] for stat in total_stats.values())
        total_attempts_global = all_correct + all_wrong
        global_error_rate = all_wrong / total_attempts_global if total_attempts_global > 0 else 0.5
        base_weight = 2 + (global_error_rate * 1)

        total_shows = stat['correct'] + stat['wrong']
        frequency_factor = 1 / (1 + math.log(1 + total_shows))

        time_passed = (current_time - last_seen) / 3600
        time_factor = min(1 + (time_passed / 24), 3)

        weight = max(1,
                     (base_weight + error_rate * 4 - decayed_correct * 0.1)
                     * time_factor
                     * frequency_factor
                     )

        return weight

    def show_coming_soon(self):
        popup = Popup(title='',
                      content=Label(text=self.get_translation('coming_soon')),
                      size_hint=(None, None), size=(dp(300), dp(200)))
        popup.open()


class MenuScreen(BaseScreen):
    menu_title = StringProperty()
    training_btn = StringProperty()
    practice_btn = StringProperty()
    reference_btn = StringProperty()
    translator_btn = StringProperty()
    settings_btn = StringProperty()

    def update_lang(self):
        super().update_lang()
        original_title = self.get_translation('menu_title')

        if random.random() < 0.01:
            braille_title = ''
            for char in original_title.upper():
                if char in braille_data[self.app.current_language]:
                    dots = braille_data[self.app.current_language][char]
                    braille_title += self.get_braille_char(dots)
                else:
                    braille_title += ' '
            self.menu_title = braille_title
        else:
            self.menu_title = original_title

        self.training_btn = self.get_translation('training_btn')
        self.practice_btn = self.get_translation('practice_btn')
        self.reference_btn = self.get_translation('reference_btn')
        self.translator_btn = self.get_translation('translator_btn')
        self.settings_btn = self.get_translation('settings_btn')


class LearningScreen(BaseScreen):
    current_index = NumericProperty(0)
    total_chars = NumericProperty(0)
    current_letter = StringProperty()
    braille_char = StringProperty()
    prev_btn = StringProperty()
    next_btn = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chars = []

    def update_lang(self):
        super().update_lang()
        self.prev_btn = self.get_translation('prev')
        self.next_btn = self.get_translation('next')

    def on_pre_enter(self, *args):
        self.update_lang()
        self.load_characters()
        self.show_current_character()

    def load_characters(self):
        lang = self.app.current_language
        self.chars = list(braille_data[lang].items())
        self.total_chars = len(self.chars)
        if self.current_index >= self.total_chars:
            self.current_index = 0

    def show_current_character(self):
        if self.chars:
            letter, dots = self.chars[self.current_index]
            self.current_letter = letter
            self.braille_char = self.get_braille_char(dots)

    def next_character(self):
        if self.current_index < self.total_chars - 1:
            self.current_index += 1
            self.show_current_character()

    def prev_character(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_character()


class PracticeScreen(BaseScreen):
    streak_text = StringProperty()
    braille_char = StringProperty()
    time_left = NumericProperty(5)
    timer_active = BooleanProperty(False)
    quick_review_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.current_streak = 0
        self.correct_button = None
        self.clock_event = None
        super().__init__(**kwargs)
        self.bind(on_pre_enter=self.on_pre_enter)
        self.bind(on_leave=self.on_leave)

    def update_streak_text(self):
        record_type = 'quick' if self.quick_review_mode else 'practice'
        self.streak_text = self.get_translation('streak').format(
            self.current_streak,
            self.app.high_scores[self.app.current_language][record_type]
        )

    def start_timer(self):
        if self.clock_event:
            self.clock_event.cancel()
        self.time_left = self.app.quick_review_time
        self.timer_active = True
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        if self.time_left <= 0:
            self.handle_timeout()

    def handle_timeout(self):
        self.timer_active = False
        self.clock_event.cancel()
        self.current_streak -= 1
        self.update_streak_text()
        self.correct_button.background_color = (0, 1, 0, 1)
        Clock.schedule_once(lambda dt: self.reset_interface(reset_streak=False), 1)

    def _update_grid(self, instance, value):
        grid = self.ids.answers_grid
        grid.clear_widgets()
        current_braille = braille_data[self.app.current_language]
        answers = [self.current_letter]
        while len(answers) < int(self.app.current_difficulty):
            letter = random.choice(list(current_braille.keys()))
            if letter not in answers:
                answers.append(letter)
        random.shuffle(answers)
        available_width = grid.width - dp(5) * (int(self.app.current_difficulty) - 1)
        min_btn_width = dp(100)
        max_btn_width = dp(300)
        cols = max(1, min(int(available_width // min_btn_width), int(self.app.current_difficulty)))
        btn_width = (available_width - dp(5) * (cols - 1)) / cols
        btn_width = max(min_btn_width, min(btn_width, max_btn_width))
        grid.cols = cols
        for answer in answers:
            btn = Button(
                text=answer,
                font_size=dp(18),
                disabled_color=(1, 1, 1, 1),
                size_hint=(None, None),
                size=(btn_width, dp(80)),
                on_press=self.check_answer
            )
            if answer == self.current_letter:
                self.correct_button = btn
            grid.add_widget(btn)

    def on_pre_enter(self, *args):
        self.update_lang()
        self.new_question()
        self.ids.answers_grid.bind(size=self._update_grid)

    def on_leave(self, *args):
        self.ids.answers_grid.unbind(size=self._update_grid)

    def update_lang(self):
        super().update_lang()
        self.update_streak_text()

    def new_question(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.timer_active = False

        current_time = time.time()
        current_braille = braille_data[self.app.current_language]
        weighted_chars = []

        if hasattr(self, 'current_letter'):
            lang = self.app.current_language
            if self.current_letter in self.app.stats[lang]:
                self.app.stats[lang][self.current_letter]['last_seen'] = current_time
            else:
                self.app.stats[lang][self.current_letter] = {'correct': 0, 'wrong': 0, 'last_seen': current_time}
            self.app.save_stats()

        for char, dots in current_braille.items():
            weight = self.calculate_weight(char, current_time)
            weighted_chars.extend([char] * int(weight))

        if hasattr(self, 'current_letter') and self.current_letter in weighted_chars:
            weighted_chars = [c for c in weighted_chars if c != self.current_letter]

        if not weighted_chars:
            weighted_chars = list(current_braille.keys()) * 3

        self.current_letter = random.choice(weighted_chars)
        self.current_dots = current_braille[self.current_letter]
        self.braille_char = self.get_braille_char(self.current_dots)

        lang = self.app.current_language
        if self.current_letter in self.app.stats[lang]:
            self.app.stats[lang][self.current_letter]['last_seen'] = current_time
        else:
            self.app.stats[lang][self.current_letter] = {'correct': 0, 'wrong': 0, 'last_seen': current_time}
        self.app.save_stats()

        num_answers = min(int(self.app.current_difficulty), len(current_braille))
        answers = [self.current_letter]
        added_chars = {self.current_letter}

        if self.app.use_stats:
            all_chars = []
            for char, dots in current_braille.items():
                stat = self.app.stats[self.app.current_language].get(char, {})
                correct = stat.get('correct', 0)
                wrong = stat.get('wrong', 0)
                weight = self.calculate_weight(char, current_time)
                all_chars.append((char, weight))
            all_chars.sort(key=lambda x: x[1], reverse=True)
            while len(answers) < num_answers:
                for char, weight in all_chars:
                    if len(answers) >= num_answers:
                        break
                    if char not in added_chars and random.random() < (weight / 10):
                        answers.append(char)
                        added_chars.add(char)
                        if len(answers) == len(current_braille):
                            added_chars = {self.current_letter}
        else:
            while len(answers) < num_answers:
                letter = random.choice(list(current_braille.keys()))
                if letter not in answers:
                    answers.append(letter)
        random.shuffle(answers)
        self.ids.answers_grid.clear_widgets()
        self._update_grid(None, self.ids.answers_grid.size)

    def check_answer(self, instance):
        if self.timer_active:
            self.clock_event.cancel()
            self.timer_active = False

        for child in self.ids.answers_grid.children:
            child.disabled = True

        lang = self.app.current_language
        char = self.current_letter

        if instance.text == char:
            instance.background_color = (0, 1, 0, 1)
            self.current_streak += 1

            self.app.stats[lang][char] = {
                'correct': self.app.stats[lang].get(char, {}).get('correct', 0) + 1,
                'wrong': self.app.stats[lang].get(char, {}).get('wrong', 0)
            }

            record_type = 'quick' if self.quick_review_mode else 'practice'
            if self.current_streak > self.app.high_scores[lang][record_type]:
                self.app.high_scores[lang][record_type] = self.current_streak
                self.app.save_high_scores()
        else:
            instance.background_color = (1, 0, 0, 1)
            self.correct_button.background_color = (0, 1, 0, 1)

            self.app.stats[lang][char] = {
                'correct': self.app.stats[lang].get(char, {}).get('correct', 0),
                'wrong': self.app.stats[lang].get(char, {}).get('wrong', 0) + 1
            }

            self.current_streak = 0

        self.app.save_stats()
        self.update_streak_text()
        Clock.schedule_once(lambda dt: self.reset_interface(reset_streak=not instance.text == char),
                            1 if instance.text == char else 2)

    def reset_interface(self, reset_streak=False):
        def _reset(_):
            if self.clock_event:
                self.clock_event.cancel()
            for child in self.ids.answers_grid.children:
                child.disabled = False
            if reset_streak:
                self.current_streak = 0
                self.update_streak_text()
            self.new_question()
            if self.quick_review_mode:
                self.start_timer()

        Clock.schedule_once(_reset, 0)


class MediumPracticeScreen(BaseScreen):
    braille_char = StringProperty()
    current_letter = StringProperty()
    score = NumericProperty(0)
    current_dots = ListProperty([])
    user_input = ListProperty([0] * 6)
    dot_buttons = ListProperty([])
    current_streak = NumericProperty(0)
    streak_text = StringProperty()
    confirm_btn = StringProperty()
    clear_btn = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_buttons = []
        self.score = 0
        self.current_streak = 0

    def update_lang(self):
        super().update_lang()
        self.confirm_btn = self.get_translation('confirm_btn')
        self.clear_btn = self.get_translation('clear_btn')

    def on_pre_enter(self, *args):
        self.update_lang()
        self.load_braille_data()
        self.update_streak_text()
        self.new_question()

        # Инициализация списка кнопок точек
        if not self.dot_buttons:
            self.dot_buttons = [
                self.ids.dot1,  # точка 1 (индекс 0)
                self.ids.dot2,  # точка 2 (индекс 1)
                self.ids.dot3,  # точка 3 (индекс 2)
                self.ids.dot4,  # точка 4 (индекс 3)
                self.ids.dot5,  # точка 5 (индекс 4)
                self.ids.dot6  # точка 6 (индекс 5)
            ]

    def update_streak_text(self):
        if not hasattr(self.app, 'high_scores'):
            self.streak_text = self.get_translation('streak').format(0, 0)
            return

        record_type = 'medium_practice'
        record = self.app.high_scores[self.app.current_language].get(record_type, 0)

        if self.current_streak > record:
            record = self.current_streak

        self.streak_text = self.get_translation('streak').format(
            self.current_streak, record
        )

    def new_question(self):
        self.user_input = [0] * 6
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)
            btn.state = 'normal'

        current_time = time.time()
        current_braille = self.braille_data
        weighted_chars = []

        if hasattr(self, 'current_letter'):
            lang = self.app.current_language
            if self.current_letter in self.app.stats[lang]:
                self.app.stats[lang][self.current_letter]['last_seen'] = current_time
            else:
                self.app.stats[lang][self.current_letter] = {'correct': 0, 'wrong': 0, 'last_seen': current_time}
            self.app.save_stats()

        # Формируем список символов с учетом веса
        for char, dots in current_braille.items():
            weight = self.calculate_weight(char, current_time)
            weighted_chars.extend([char] * int(weight))

        # Удаляем последний показанный символ из списка
        if hasattr(self, 'current_letter') and self.current_letter in weighted_chars:
            weighted_chars = [c for c in weighted_chars if c != self.current_letter]

        # Если список пуст, восстанавливаем его
        if not weighted_chars:
            weighted_chars = list(current_braille.keys()) * 3

        # Выбираем новый символ
        self.current_letter = random.choice(weighted_chars)
        self.current_dots = current_braille[self.current_letter]

        # Обновляем время последнего показа
        lang = self.app.current_language
        if self.current_letter in self.app.stats[lang]:
            self.app.stats[lang][self.current_letter]['last_seen'] = current_time
        else:
            self.app.stats[lang][self.current_letter] = {'correct': 0, 'wrong': 0, 'last_seen': current_time}
        self.app.save_stats()

    def on_dot_press(self, index, instance):
        # Переключение состояния точки
        self.user_input[index] = 1 - self.user_input[index]
        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[index] else (1, 1, 1, 1)

    def confirm_answer(self):
        for btn in self.dot_buttons:
            btn.disabled = True
            btn.disabled_color = (1, 1, 1, 1)
        self.ids.confirm_btn.disabled = True
        self.ids.confirm_btn.disabled_color = (1, 1, 1, 1)
        self.ids.clear_btn.disabled = True
        self.ids.clear_btn.disabled_color = (1, 1, 1, 1)

        # Сравнение ответа пользователя с правильным
        is_correct = self.user_input == self.current_dots

        # Подсветка всех точек с учетом правильного ответа
        for i, btn in enumerate(self.dot_buttons):
            correct = self.current_dots[i]
            user = self.user_input[i]

            if correct == 1 and user == 1:
                btn.background_color = (0, 1, 0, 1)  # Зеленый для правильных точек
            elif correct == 1 and user == 0:
                btn.background_color = (1, 0.7, 0, 1)  # Оранжевый для пропущенных
            elif correct == 0 and user == 1:
                btn.background_color = (1, 0, 0, 1)  # Красный для лишних
            else:
                btn.background_color = (1, 1, 1, 1)  # Белый для не выбранных неправильных точек

        # Обновление счета
        if is_correct:
            self.score += 1
            self.current_streak += 1

            # Обновление рекорда для среднего уровня
            record_type = 'medium_practice'
            if self.current_streak > self.app.high_scores[self.app.current_language].get(record_type, 0):
                self.app.high_scores[self.app.current_language][record_type] = self.current_streak
                self.app.save_high_scores()

            # Обновление статистики
            lang = self.app.current_language
            self.app.stats[lang][self.current_letter] = {
                'correct': self.app.stats[lang].get(self.current_letter, {}).get('correct', 0) + 1,
                'wrong': self.app.stats[lang].get(self.current_letter, {}).get('wrong', 0)
            }
        else:
            self.score -= 1
            self.current_streak = 0

            # Обновление статистики
            lang = self.app.current_language
            self.app.stats[lang][self.current_letter] = {
                'correct': self.app.stats[lang].get(self.current_letter, {}).get('correct', 0),
                'wrong': self.app.stats[lang].get(self.current_letter, {}).get('wrong', 0) + 1
            }

        self.app.save_stats()
        self.update_streak_text()

        # Переход к следующему вопросу через 3 секунды
        Clock.schedule_once(lambda dt: self.next_question(), 3)

    def next_question(self):
        # Включение кнопок
        for btn in self.dot_buttons:
            btn.disabled = False
        self.ids.confirm_btn.disabled = False  # Включаем кнопку "Подтвердить"
        self.ids.clear_btn.disabled = False  # Включаем кнопку "Очистить"

        # Новый вопрос
        self.new_question()

    def clear_input(self):
        # Очистка ввода пользователя
        self.user_input = [0] * 6
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)
            btn.state = 'normal'


class PracticeLevelsScreen(BaseScreen):
    title = StringProperty()
    easy_level_btn = StringProperty()
    medium_level_btn = StringProperty()
    hard_level_btn = StringProperty()
    quick_review_btn = StringProperty()

    def update_lang(self):
        super().update_lang()
        self.title = self.get_translation('practice_levels_title')
        self.easy_level_btn = self.get_translation('easy_level')
        self.medium_level_btn = self.get_translation('medium_level')
        self.hard_level_btn = self.get_translation('hard_level')
        self.quick_review_btn = self.get_translation('quick_review')

    def start_quick_review(self):
        practice_screen = self.manager.get_screen('practice')
        practice_screen.quick_review_mode = True
        self.manager.current = 'practice'
        practice_screen.new_question()
        practice_screen.start_timer()

    def start_medium_level(self):
        screen_manager = self.manager
        if 'medium_practice' not in screen_manager.screen_names:
            screen_manager.add_widget(MediumPracticeScreen(name='medium_practice'))

        screen_manager.current = 'medium_practice'

    def start_easy_level(self):
        practice_screen = self.manager.get_screen('practice')
        self.manager.current = 'practice'
        practice_screen.quick_review_mode = False
        practice_screen.new_question()


class SettingsScreen(BaseScreen):
    settings_title = StringProperty()
    language_label = StringProperty()
    difficulty_label = StringProperty()
    current_lang = StringProperty()
    current_difficulty_str = StringProperty()
    languages = DictProperty(LANGUAGES)
    difficulty_values = ListProperty()
    time_label = StringProperty()
    time_hint = StringProperty()
    use_stats = StringProperty()
    reset_stats_btn = StringProperty()

    def update_lang(self):
        super().update_lang()
        lang = self.app.current_language
        self.settings_title = self.get_translation('settings_title')
        self.language_label = self.get_translation('language_label')
        self.difficulty_label = self.get_translation('difficulty_label')
        self.use_stats = self.get_translation('use_stats')
        self.reset_stats_btn = self.get_translation('reset_stats_btn')
        self.time_label = self.get_translation('time_label')
        self.time_hint = self.get_translation('time_hint')
        self.current_lang = LANGUAGES[lang]
        self.difficulty_values = [
            self.get_translation(f'difficulty_{d}')
            for d in ['2', '4', '6', '8', '10']]
        self.current_difficulty_str = self.get_translation(
            f'difficulty_{self.app.current_difficulty}'
        )

    def update_settings(self, key, value):
        if key == 'language':
            lang_code = next((k for k, v in LANGUAGES.items() if v == value), 'en')
            self.app.current_language = lang_code
            self.current_lang = LANGUAGES[lang_code]
        elif key == 'difficulty':
            diff_code = next((k.split('_')[1] for k, v in translations[self.app.current_language].items()
                              if v == value and k.startswith('difficulty_')), '4')
            self.app.current_difficulty = diff_code
        elif key == 'time':
            try:
                time = int(value) if value else 5
                if 1 <= time <= 300:
                    self.app.quick_review_time = time
                else:
                    self.app.quick_review_time = 5
            except ValueError:
                self.app.quick_review_time = 5
        self.app.save_settings()
        self.app.update_all_screens()

    def update_update_use_stats(self, active):
        self.app.use_stats = active
        self.app.save_settings()
        ref_screen = self.app.root.get_screen('reference')
        if hasattr(ref_screen, 'update_reference'):
            ref_screen.update_reference()

    def reset_stats(self):
        popup = Popup(
            title=self.get_translation('reset_stats_title'),
            content=Label(text=self.get_translation('reset_stats_text')),
            size_hint=(None, None),
            size=(dp(300), dp(200))
        )

        def confirm(instance):
            self.app.stats = {'en': {}, 'ru': {}, 'dru': {}}
            self.app.save_stats()
            popup.dismiss()

        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        yes_btn = Button(text=self.get_translation('yes'), on_press=confirm)
        no_btn = Button(text=self.get_translation('no'), on_press=popup.dismiss)
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        popup.content = btn_layout
        popup.open()


class ReferenceScreen(BaseScreen):
    reference_title = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_chars = []

    def on_pre_enter(self, *args):
        self.app = App.get_running_app()
        self.update_lang()
        self.load_braille_data()
        self.update_reference()

    def update_lang(self):
        super().update_lang()
        self.reference_title = self.get_translation('reference_title')

    def load_braille_data(self):
        self.all_chars = list(self.app.braille_data[self.app.current_language].items())

    def update_reference(self):
        grid = self.ids.reference_grid
        grid.clear_widgets()

        for letter, dots in self.all_chars:
            braille_char = self.get_braille_char(dots)

            # Добавляем только букву и Брайль
            label_letter = Label(
                text=letter,
                font_size=dp(45),
                size_hint_y=None,
                height=dp(60),
                halign='center',
                valign='middle'
            )
            grid.add_widget(label_letter)

            label_braille = Label(
                text=braille_char,
                font_name='BrailleFont',
                font_size=dp(45),
                size_hint_y=None,
                height=dp(60),
                halign='center',
                valign='middle'
            )
            grid.add_widget(label_braille)

            if self.app.use_stats:
                stat = self.app.stats[self.app.current_language].get(letter, {'correct': 0, 'wrong': 0})
                stats_label = Label(
                    text=self.get_translation('stats_label').format(stat['correct'], stat['wrong']),
                    font_size=dp(18),
                    size_hint_y=None,
                    height=dp(40),
                    halign='center',
                    valign='middle',
                    color=(0.7, 0.7, 0.7, 1)
                )
                grid.add_widget(stats_label)
                grid.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Отступ между записями


class TranslatorScreen(BaseScreen):
    translator_title = StringProperty()
    input_hint = StringProperty()
    translate_btn = StringProperty()
    input_braille_btn = StringProperty()
    confirm_btn = StringProperty()
    clear_btn = StringProperty()
    braille_input_active = BooleanProperty(False)
    user_braille_dots = ListProperty([0] * 6)
    dot_buttons = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.braille_input_panel.opacity = 0
        self.ids.braille_input_panel.disabled = True

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.update_lang()
        self.load_braille_data()
        # Инициализация списка кнопок точек
        if not self.dot_buttons:
            self.dot_buttons = [
                self.ids.dot1,  # точка 1 (индекс 0)
                self.ids.dot2,  # точка 2 (индекс 1)
                self.ids.dot3,  # точка 3 (индекс 2)
                self.ids.dot4,  # точка 4 (индекс 3)
                self.ids.dot5,  # точка 5 (индекс 4)
                self.ids.dot6  # точка 6 (индекс 5)
            ]

    def update_lang(self):
        super().update_lang()
        self.translator_title = self.get_translation('translator_title')
        self.input_hint = self.get_translation('input_hint')
        self.translate_btn = self.get_translation('translate_btn')
        self.input_braille_btn = self.get_translation('input_braille_btn')
        self.confirm_btn = self.get_translation('confirm_btn')
        self.clear_btn = self.get_translation('clear_btn')

    def translate_text(self):
        braille_text = []
        for char in self.ids.input_text.text.upper():
            if char == ' ':
                braille_text.append(chr(0x2800))  # Пробел в Брайле
            elif char in self.braille_data:
                braille_text.append(self.get_braille_char(self.braille_data[char]))
            else:
                braille_text.append('?')

        self.ids.braille_output.text = '|'.join(braille_text)

    def on_braille_dot_press(self, index):
        self.user_braille_dots[index] = 1 - self.user_braille_dots[index]
        button = self.dot_buttons[index]
        button.background_color = (0.7, 0.7, 0.7, 1) if self.user_braille_dots[index] else (1, 1, 1, 1)

    def open_braille_input(self):
        self.braille_input_active = not self.braille_input_active
        if self.braille_input_active:
            self.ids.braille_input_panel.opacity = 1
            self.ids.braille_input_panel.disabled = False
            self.user_braille_dots = [0] * 6
        else:
            self.ids.braille_input_panel.opacity = 0
            self.ids.braille_input_panel.disabled = True

    def confirm_braille_input(self):
        lang = self.app.current_language
        for char, char_dots in self.braille_data.items():
            if char_dots == self.user_braille_dots:
                current_text = self.ids.input_text.text
                self.ids.input_text.text = current_text + char
                return
        self.ids.input_text.text += '?'

    def clear_braille_input(self):
        self.user_braille_dots = [0] * 6
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)


class BrailleApp(App):
    current_language = StringProperty('en')
    current_difficulty = StringProperty('4')
    quick_review_time = NumericProperty(5)
    is_mobile = BooleanProperty(False)
    stats = DictProperty({'en': {}, 'ru': {}, 'dru': {}})
    use_stats = BooleanProperty(True)

    def build(self):
        self.is_mobile = platform in ('android', 'ios')
        self.braille_data = braille_data
        self.load_settings()
        self.load_high_scores()
        self.load_stats()
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LearningScreen(name='learning'))
        sm.add_widget(PracticeLevelsScreen(name='practice_levels'))
        sm.add_widget(PracticeScreen(name='practice'))
        sm.add_widget(MediumPracticeScreen(name='medium_practice'))
        sm.add_widget(ReferenceScreen(name='reference'))
        sm.add_widget(TranslatorScreen(name='translator'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def load_settings(self):
        try:
            with open("settings.json") as f:
                data = json.load(f)
                self.current_language = data.get('language', 'en')
                self.current_difficulty = data.get('difficulty', '4')
                self.quick_review_time = data.get('quick_review_time', 5)
                self.use_stats = data.get('use_stats', True)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_settings(self):
        with open("settings.json", "w") as f:
            json.dump({
                'language': self.current_language,
                'difficulty': self.current_difficulty,
                'quick_review_time': self.quick_review_time,
                'use_stats': self.use_stats
            }, f)
        self.save_high_scores()
        self.save_stats()

    def load_high_scores(self):
        try:
            with open("highscores.json", "r") as f:
                data = json.load(f)
            for lang in ['en', 'ru', 'dru']:
                if not isinstance(data.get(lang), dict):
                    data[lang] = {'practice': 0, 'medium_practice': 0, 'quick': 0}
            self.high_scores = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.high_scores = {
                lang: {'practice': 0, 'medium_practice': 0, 'quick': 0}
                for lang in ['en', 'ru', 'dru']
            }

    def save_high_scores(self):
        with open("highscores.json", "w") as f:
            json.dump(self.high_scores, f)

    def load_stats(self):
        try:
            with open("stats.json", "r") as f:
                data = json.load(f)
            for lang in ['en', 'ru', 'dru']:
                if lang not in data:
                    data[lang] = {}
                for char in braille_data[lang]:
                    if char not in data[lang]:
                        data[lang][char] = {'correct': 0, 'wrong': 0, 'last_seen': time.time()}
                    else:
                        stat = data[lang][char]
                        if isinstance(stat, dict):
                            if 'last_seen' not in stat:
                                stat['last_seen'] = time.time()
                        else:
                            data[lang][char] = {'correct': 0, 'wrong': stat, 'last_seen': time.time()}
            self.stats = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.stats = {'en': {}, 'ru': {}, 'dru': {}}

    def save_stats(self):
        with open("stats.json", "w") as f:
            json.dump(self.stats, f)

    def update_all_screens(self):
        if self.root and hasattr(self.root, 'screens'):
            for screen in self.root.screens:
                if hasattr(screen, 'update_lang'):
                    screen.update_lang()


if __name__ == '__main__':

    BrailleApp().run()
