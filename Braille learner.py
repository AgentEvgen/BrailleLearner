from kivy.properties import StringProperty, DictProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.config import Config
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from collections import OrderedDict
import random
import json
import math
import time
import os

Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'resizable', '1')
LabelBase.register(name='BrailleFont', fn_regular='DejaVuSans.ttf')

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
                text: str(root.current_index + 1) + '/' + str(root.total_chars)
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
            padding: [dp(20), 0, dp(20), 0]
            row_default_height: dp(80)
        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press:
                root.quick_review_mode = False
                app.stop_quick_review()
                root.manager.current = 'practice_levels'

<MediumPracticeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        Label:
            text: root.streak_text + ('\\n' + str(root.time_left) if root.quick_review_mode else '')
            font_size: dp(18)
            size_hint_y: None
            height: dp(60)
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
                    root.quick_review_mode = False
                    app.stop_quick_review()
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

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(5)
            padding: 0

            BaseButton:
                text: root.translate_btn
                size_hint: (1, 1)
                height: dp(60)
                on_press: root.translate_text()

            BaseButton:
                text: root.input_braille_btn
                size_hint: (1, 1)
                height: dp(60)
                on_press: root.open_braille_input()

        FloatLayout:
            size_hint_y: 0.45

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
                        width: self.parent.width

            BoxLayout:
                id: braille_input_panel
                orientation: 'vertical'
                size_hint: (0.8, 0.8)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                opacity: 0
                disabled: True

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
                        text: root.delete_btn
                        size_hint: 0.5, 1
                        height: dp(60)
                        on_press: root.delete_last_char()

        BaseButton:
            text: root.back_btn
            size_hint_y: None
            height: dp(50)
            on_press: root.close_braille_input()
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
        'Y': [1, 0, 1, 1, 1, 1], 'Z': [1, 0, 1, 0, 1, 1]
    }.items())),
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
        ('Э', [0, 1, 0, 1, 0, 1]), ('Ю', [1, 1, 0, 0, 1, 1]), ('Я', [1, 1, 0, 1, 0, 1])
    ]),
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
        ('Ѳ', [1, 1, 0, 1, 1, 1]), ('Ѵ', [1, 0, 0, 0, 1, 0])
    ])
}


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
        'delete_btn': 'Delete'
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
        'delete_btn': 'Удалить'
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
        'input_braille_btn': 'Вводъ Брайля',
        'delete_btn': 'Удалить'
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
        lang = self.app.current_language if hasattr(self, 'app') and self.app else 'en'
        return translations.get(lang, translations['en']).get(key, translations['en'].get(key, key))

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
        last_seen = stat.get('last_seen', 0) or (current_time - 3600)

        days_passed = (current_time - last_seen) / 86400.0
        decay = 0.9 ** days_passed

        dec_wrong = stat.get('wrong', 0) * decay
        dec_corr = stat.get('correct', 0) * decay
        dec_total = dec_corr + dec_wrong

        alpha = 1.0
        error_rate = (dec_wrong + alpha) / (dec_total + 2 * alpha)

        total_stats = self.app.stats[self.app.current_language]
        all_wrong = sum(s.get('wrong', 0) for s in total_stats.values())
        all_correct = sum(s.get('correct', 0) for s in total_stats.values())
        total_attempts_global = all_correct + all_wrong
        global_error_rate = (all_wrong + alpha) / (total_attempts_global + 2 * alpha) if total_attempts_global > 0 else 0.5
        base_weight = 1.5 + global_error_rate

        total_shows = stat.get('correct', 0) + stat.get('wrong', 0)
        frequency_factor = 1.0 / (1.0 + math.log1p(total_shows))

        hours_since_seen = (current_time - last_seen) / 3600.0
        time_factor = min(1.0 + (hours_since_seen / 24.0), 3.0)

        novelty_boost = 0.4 if total_shows < 3 else 0.0

        weight = (base_weight + error_rate * 3.5 + novelty_boost) * time_factor * frequency_factor

        weight = max(0.4, min(weight, 10.0))
        return weight

    def weighted_choice(self, items, weights):
        total = sum(weights)
        if total <= 0:
            return random.choice(items)
        r = random.uniform(0, total)
        upto = 0.0
        for item, w in zip(items, weights):
            upto += w
            if upto >= r:
                return item
        return items[-1]

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
    invert_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.current_streak = 0
        self.correct_button = None
        self.clock_event = None
        self.scheduled_events = []
        super().__init__(**kwargs)
        self.bind(on_pre_enter=self.on_pre_enter)
        self.bind(on_leave=self.on_leave)

    def schedule_once(self, callback, delay):
        event = Clock.schedule_once(callback, delay)
        self.scheduled_events.append(event)
        return event

    def update_streak_text(self):
        lang = self.app.current_language
        record_type = 'quick' if self.quick_review_mode else 'practice'
        current_value = self.app.quick_streak if self.quick_review_mode else self.current_streak
        self.streak_text = self.get_translation('streak').format(
            current_value,
            self.app.high_scores[lang][record_type]
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
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        for child in self.ids.answers_grid.children:
            child.disabled = True
        if self.correct_button:
            self.correct_button.background_color = (0, 1, 0, 1)

        if self.quick_review_mode:
            self.app.quick_streak -= 1
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
        else:
            self.current_streak = 0
            self.update_streak_text()
            self.schedule_once(lambda dt: self.reset_interface(reset_streak=False), 1.2)

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
        horizontal_padding = dp(20)
        available_width = grid.width - (2 * horizontal_padding)
        min_btn_width = dp(100)
        max_btn_width = dp(300)
        num_options = int(self.app.current_difficulty)
        cols = max(1, min(int(available_width // (min_btn_width + dp(5))), num_options))
        total_spacing = dp(5) * (cols - 1)
        btn_width = (available_width - total_spacing) / cols
        btn_width = max(min_btn_width, min(btn_width, max_btn_width))

        grid.cols = cols
        grid.padding = [horizontal_padding, 0, horizontal_padding, 0]

        for answer in answers:
            btn = Button(
                size_hint=(None, None),
                size=(btn_width, dp(80)),
                on_press=self.check_answer)

            btn.background_disabled_normal = btn.background_normal
            btn.background_disabled_down = btn.background_down
            btn.disabled_color = (1, 1, 1, 1)

            if self.invert_mode:
                dots = current_braille[answer]
                btn.text = self.get_braille_char(dots)
                btn.font_name = 'BrailleFont'
                btn.font_size = dp(42)
            else:
                btn.text = answer
                btn.font_name = 'Roboto'
                btn.font_size = dp(24)

            btn.background_color = (1, 1, 1, 1)
            btn.answer_char = answer

            if answer == self.current_letter:
                self.correct_button = btn

            grid.add_widget(btn)

    def on_pre_enter(self, *args):
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()

        self.update_lang()
        self.new_question()
        self.ids.answers_grid.bind(size=self._update_grid)

    def on_leave(self, *args):
        self.ids.answers_grid.unbind(size=self._update_grid)
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()
        self.timer_active = False

    def update_lang(self):
        super().update_lang()
        self.update_streak_text()

    def new_question(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.timer_active = False

        current_time = time.time()
        current_braille = braille_data[self.app.current_language]

        items = list(current_braille.keys())
        weights = [self.calculate_weight(ch, current_time) for ch in items]
        if hasattr(self, 'current_letter') and self.current_letter in items:
            idx = items.index(self.current_letter)
            weights[idx] *= 0.2
        self.current_letter = self.weighted_choice(items, weights)
        self.current_dots = current_braille[self.current_letter]
        self.invert_mode = random.random() < 0.5
        if not self.invert_mode:
            self.braille_char = self.get_braille_char(self.current_dots)
        else:
            self.braille_char = self.current_letter

        lang = self.app.current_language
        self.app.stats.setdefault(lang, {})
        self.app.stats[lang].setdefault(self.current_letter, {'correct': 0, 'wrong': 0, 'last_seen': 0})
        self.app.stats[lang][self.current_letter]['last_seen'] = current_time
        self.app.save_stats()
        self.ids.answers_grid.clear_widgets()
        self._update_grid(None, self.ids.answers_grid.size)
        if self.quick_review_mode:
            self.start_timer()

    def check_answer(self, instance):
        if self.timer_active:
            self.clock_event.cancel()
            self.timer_active = False

        for child in self.ids.answers_grid.children:
            child.disabled = True
            child.disabled_color = (1, 1, 1, 1)

        lang = self.app.current_language
        char = self.current_letter
        chosen_char = getattr(instance, 'answer_char', instance.text)

        if chosen_char == char:
            instance.background_color = (0, 1, 0, 1)

            if self.quick_review_mode:
                self.app.quick_streak += 1
                if self.app.quick_streak > self.app.high_scores[lang]['quick']:
                    self.app.high_scores[lang]['quick'] = self.app.quick_streak
                    self.app.save_high_scores()
            else:
                self.current_streak += 1
                if self.current_streak > self.app.high_scores[lang]['practice']:
                    self.app.high_scores[lang]['practice'] = self.current_streak
                    self.app.save_high_scores()
            self.app.stats[lang][char]['correct'] += 1
        else:
            instance.background_color = (1, 0, 0, 1)
            if self.correct_button:
                self.correct_button.background_color = (0, 1, 0, 1)

            if self.quick_review_mode:
                self.app.quick_streak -= 1
            else:
                self.current_streak = 0
            self.app.stats[lang][char]['wrong'] += 1

        self.app.stats[lang][char]['last_seen'] = time.time()
        self.app.save_stats()
        self.update_streak_text()

        delay = 0.5 if self.quick_review_mode else 0.8
        next_action = self.app.next_quick_step if self.quick_review_mode else lambda: self.reset_interface(
            chosen_char != char)
        self.schedule_once(lambda dt: next_action(), delay if chosen_char == char else delay + 0.4)

    def reset_interface(self, reset_streak=False):
        def _reset(_):
            for child in self.ids.answers_grid.children:
                child.disabled = False
            if reset_streak:
                self.current_streak = 0
                self.update_streak_text()
            self.new_question()

        self.schedule_once(_reset, 0)


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
    quick_review_mode = BooleanProperty(False)
    time_left = NumericProperty(5)
    timer_active = BooleanProperty(False)
    clock_event = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_buttons = []
        self.score = 0
        self.current_streak = 0
        self.scheduled_events = []

    def schedule_once(self, callback, delay):
        event = Clock.schedule_once(callback, delay)
        self.scheduled_events.append(event)
        return event

    def _enable_controls(self):
        if self.dot_buttons:
            for btn in self.dot_buttons:
                btn.disabled = False
        if 'confirm_btn' in self.ids:
            self.ids.confirm_btn.disabled = False
        if 'clear_btn' in self.ids:
            self.ids.clear_btn.disabled = False

    def update_lang(self):
        super().update_lang()
        self.confirm_btn = self.get_translation('confirm_btn')
        self.clear_btn = self.get_translation('clear_btn')

    def on_pre_enter(self, *args):
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()

        self.update_lang()
        self.load_braille_data()

        if not self.dot_buttons:
            self.dot_buttons = [
                self.ids.dot1, self.ids.dot2, self.ids.dot3,
                self.ids.dot4, self.ids.dot5, self.ids.dot6
            ]

        self.update_streak_text()
        self.new_question()

    def on_leave(self, *args):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()
        self.timer_active = False

    def update_streak_text(self):
        if self.quick_review_mode:
            current_value = self.app.quick_streak
            record = self.app.high_scores[self.app.current_language].get('quick', 0)
        else:
            current_value = self.current_streak
            record = self.app.high_scores[self.app.current_language].get('medium_practice', 0)
        self.streak_text = self.get_translation('streak').format(current_value, record)

    def start_timer(self):
        if self.clock_event:
            self.clock_event.cancel()
        self.time_left = self.app.quick_review_time + 1
        self.timer_active = True
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        if self.time_left <= 0:
            self.handle_timeout()

    def handle_timeout(self):
        self.timer_active = False
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        self._disable_and_show_correct_answer()

        if self.quick_review_mode:
            self.app.quick_streak -= 1
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)

    def _disable_and_show_correct_answer(self, user_input=None):
        if user_input is None:
            user_input = [0] * 6

        for btn in self.dot_buttons:
            btn.disabled = True
            btn.disabled_color = (1, 1, 1, 1)
        self.ids.confirm_btn.disabled = True
        self.ids.confirm_btn.disabled_color = (1, 1, 1, 1)
        self.ids.clear_btn.disabled = True
        self.ids.clear_btn.disabled_color = (1, 1, 1, 1)

        for i, btn in enumerate(self.dot_buttons):
            correct = self.current_dots[i]
            user = user_input[i]
            if correct and user:
                btn.background_color = (0, 1, 0, 1)
            elif correct and not user:
                btn.background_color = (1, 0.7, 0, 1)
            elif not correct and user:
                btn.background_color = (1, 0, 0, 1)
            else:
                btn.background_color = (1, 1, 1, 1)

    def new_question(self):
        self._enable_controls()
        self.user_input = [0] * 6
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)
            btn.state = 'normal'

        current_time = time.time()
        current_braille = self.braille_data

        items = list(current_braille.keys())
        weights = [self.calculate_weight(ch, current_time) for ch in items]
        if hasattr(self, 'current_letter') and self.current_letter in items:
            idx = items.index(self.current_letter)
            weights[idx] *= 0.2
        self.current_letter = self.weighted_choice(items, weights)
        self.current_dots = current_braille[self.current_letter]

        lang = self.app.current_language
        self.app.stats.setdefault(lang, {})
        self.app.stats[lang].setdefault(self.current_letter, {'correct': 0, 'wrong': 0, 'last_seen': 0})
        self.app.stats[lang][self.current_letter]['last_seen'] = current_time
        self.app.save_stats()

        if self.quick_review_mode:
            self.start_timer()

    def on_dot_press(self, index, instance):
        self.user_input[index] = 1 - self.user_input[index]
        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[index] else (1, 1, 1, 1)

    def confirm_answer(self):
        if self.timer_active:
            self.clock_event.cancel()
            self.timer_active = False

        is_correct = self.user_input == self.current_dots
        self._disable_and_show_correct_answer(self.user_input)

        lang = self.app.current_language
        if is_correct:
            self.app.stats[lang][self.current_letter]['correct'] += 1
        else:
            self.app.stats[lang][self.current_letter]['wrong'] += 1

        self.app.stats[lang][self.current_letter]['last_seen'] = time.time()
        self.app.save_stats()

        if self.quick_review_mode:
            if is_correct:
                self.app.quick_streak += 1
                if self.app.quick_streak > self.app.high_scores[lang]['quick']:
                    self.app.high_scores[lang]['quick'] = self.app.quick_streak
                    self.app.save_high_scores()
            else:
                self.app.quick_streak -= 1
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
        else:
            if is_correct:
                self.score += 1
                self.current_streak += 1
                if self.current_streak > self.app.high_scores[lang].get('medium_practice', 0):
                    self.app.high_scores[lang]['medium_practice'] = self.current_streak
                    self.app.save_high_scores()
            else:
                self.score -= 1
                self.current_streak = 0
            self.update_streak_text()
            self.schedule_once(lambda dt: self.next_question(), 2)

    def next_question(self):
        self.new_question()

    def clear_input(self):
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
        App.get_running_app().start_quick_review()

    def start_medium_level(self):
        screen_manager = self.manager
        if 'medium_practice' not in screen_manager.screen_names:
            screen_manager.add_widget(MediumPracticeScreen(name='medium_practice'))
        screen_manager.current = 'medium_practice'
        screen_manager.get_screen('medium_practice').quick_review_mode = False

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
                t = int(value) if value else 5
                if 1 <= t <= 300:
                    self.app.quick_review_time = t
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
            size_hint=(None, None),
            size=(dp(320), dp(200))
        )

        def do_reset(*_):
            self.app.stats = {'en': {}, 'ru': {}, 'dru': {}}
            self.app.save_stats()
            popup.dismiss()

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=self.get_translation('reset_stats_text'),
                                 size_hint_y=None, height=dp(80)))

        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btns.add_widget(Button(text=self.get_translation('yes'), on_press=do_reset))
        btns.add_widget(Button(text=self.get_translation('no'), on_press=popup.dismiss))

        content.add_widget(btns)
        popup.content = content
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
                grid.add_widget(Widget(size_hint_y=None, height=dp(10)))


class TranslatorScreen(BaseScreen):
    translator_title = StringProperty()
    input_hint = StringProperty()
    translate_btn = StringProperty()
    input_braille_btn = StringProperty()
    confirm_btn = StringProperty()
    delete_btn = StringProperty()
    braille_input_active = BooleanProperty(False)
    user_braille_dots = ListProperty([0] * 6)
    dot_buttons = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self.ids.braille_input_panel.opacity = 0
        self.ids.braille_input_panel.disabled = True
        self.dot_buttons = [
            self.ids.dot1,
            self.ids.dot2,
            self.ids.dot3,
            self.ids.dot4,
            self.ids.dot5,
            self.ids.dot6,]

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.update_lang()
        self.load_braille_data()

    def update_lang(self):
        super().update_lang()
        self.translator_title = self.get_translation('translator_title')
        self.input_hint = self.get_translation('input_hint')
        self.translate_btn = self.get_translation('translate_btn')
        self.input_braille_btn = self.get_translation('input_braille_btn')
        self.confirm_btn = self.get_translation('confirm_btn')
        self.delete_btn = self.get_translation('delete_btn')

    def translate_text(self):
        braille_text = []
        for char in self.ids.input_text.text.upper():
            if char == ' ':
                braille_text.append(chr(0x2800))
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
            self.clear_braille_input()
        else:
            self.ids.braille_input_panel.opacity = 0
            self.ids.braille_input_panel.disabled = True

    def close_braille_input(self):
        self.ids.braille_input_panel.opacity = 0
        self.ids.braille_input_panel.disabled = True

    def confirm_braille_input(self):
        lang = self.app.current_language
        for char, char_dots in self.braille_data.items():
            if char_dots == self.user_braille_dots:
                current_text = self.ids.input_text.text
                self.ids.input_text.text = current_text + char
                self.clear_braille_input()
                return
        self.ids.input_text.text += '?'
        self.clear_braille_input()

    def delete_last_char(self):
        if self.ids.input_text.text:
            self.ids.input_text.text = self.ids.input_text.text[:-1]

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
    quick_streak = NumericProperty(0)
    quick_active = BooleanProperty(False)
    quick_mode_weights = DictProperty({'easy': 3, 'medium': 1})

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

    def choose_quick_mode(self):
        modes = ['easy', 'medium']
        weights = [self.quick_mode_weights.get('easy', 1), self.quick_mode_weights.get('medium', 1)]
        total = sum(weights) or 1
        r = random.uniform(0, total)
        upto = 0
        for m, w in zip(modes, weights):
            upto += w
            if upto >= r:
                return m
        return modes[0]

    def start_quick_review(self):
        self.quick_streak = 0
        self.quick_active = True
        self.next_quick_step()

    def stop_quick_review(self):
        self.quick_active = False

    def next_quick_step(self):
        if not self.quick_active or not self.root:
            return
        mode = self.choose_quick_mode()
        if mode == 'easy':
            scr = self.root.get_screen('practice')
            scr.quick_review_mode = True
            self.root.current = 'practice'
            scr.new_question()
        else:
            scrm = self.root.get_screen('medium_practice')
            scrm.quick_review_mode = True
            self.root.current = 'medium_practice'
            scrm.new_question()
    def _path(self, filename):
        return os.path.join(self.user_data_dir, filename)

    def load_settings(self):
        try:
            with open(self._path("settings.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.current_language = data.get('language', 'en')
            self.current_difficulty = data.get('difficulty', '4')
            self.quick_review_time = data.get('quick_review_time', 5)
            self.use_stats = data.get('use_stats', True)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_settings(self):
        with open(self._path("settings.json"), "w", encoding="utf-8") as f:
            json.dump({
                'language': self.current_language,
                'difficulty': self.current_difficulty,
                'quick_review_time': self.quick_review_time,
                'use_stats': self.use_stats
            }, f, ensure_ascii=False, indent=2)
        self.save_high_scores()
        self.save_stats()

    def load_high_scores(self):
        try:
            with open(self._path("highscores.json"), "r", encoding="utf-8") as f:
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
        with open(self._path("highscores.json"), "w", encoding="utf-8") as f:
            json.dump(self.high_scores, f, ensure_ascii=False, indent=2)

    def load_stats(self):
        try:
            with open(self._path("stats.json"), "r", encoding="utf-8") as f:
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
                            stat.setdefault('last_seen', time.time())
                        else:
                            data[lang][char] = {'correct': 0, 'wrong': stat, 'last_seen': time.time()}
            self.stats = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.stats = {'en': {}, 'ru': {}, 'dru': {}}

    def save_stats(self):
        with open(self._path("stats.json"), "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def update_all_screens(self):
        if self.root and hasattr(self.root, 'screens'):
            for screen in self.root.screens:
                if hasattr(screen, 'update_lang'):
                    screen.update_lang()


if __name__ == '__main__':
    BrailleApp().run()
