from kivy.properties import StringProperty, DictProperty, BooleanProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.clipboard import Clipboard
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
LabelBase.register(name='BrailleFont', fn_regular='assets/DejaVuSans.ttf')

Builder.load_string('''
<StreakHeader@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(45)
    spacing: dp(5)
    streak_text: ''
    time_left: 0
    quick_review_mode: False

    Label:
        text: root.streak_text.split('\\n')[0] if '\\n' in root.streak_text else root.streak_text
        font_size: dp(16)
        halign: 'left'
        valign: 'middle'
        size_hint_x: 0.4

    Label:
        text: str(root.time_left) if root.quick_review_mode else ''
        font_size: dp(20)
        halign: 'right'
        size_hint_x: 0.0001

    Label:
        text: root.streak_text.split('\\n')[1] if '\\n' in root.streak_text else ''
        font_size: dp(16)
        halign: 'right'
        valign: 'middle'
        size_hint_x: 0.4

<BaseButton@Button>:
    font_size: dp(22)
    size_hint_y: None
    height: dp(80)
    padding: dp(10), dp(10)

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
                    on_press: app.switch_screen('lessons')
                BaseButton:
                    id: practice_btn
                    text: root.practice_btn
                    on_press: app.switch_screen('practice_levels')
                BaseButton:
                    text: root.reference_btn
                    on_press: app.switch_screen('reference')
                BaseButton:
                    text: root.translator_btn
                    on_press: app.switch_screen('translator')
                BaseButton:
                    text: root.settings_btn
                    on_press: app.switch_screen('settings')
        Widget:
            size_hint_y: None
            height: dp(15)


<LessonsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(10)

        Label:
            text: root.lessons_title
            font_size: dp(26)
            size_hint_y: None
            height: dp(50)
            halign: 'center'
            valign: 'middle'

        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            padding: [dp(10), 0]

            Button:
                text: root.letters_tab_text
                background_color: (1.5, 1.5, 1.5, 1) if root.current_mode == 'letters' else (1, 1, 1, 1)
                on_press: root.switch_mode('letters')

            Button:
                text: root.digits_tab_text
                background_color: (1.5, 1.5, 1.5, 1) if root.current_mode == 'digits' else (1, 1, 1, 1)
                on_press: root.switch_mode('digits')

        ScrollView:
            bar_width: dp(8)
            BoxLayout:
                id: lessons_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: [dp(10), dp(10)]

        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: app.switch_screen('menu')

<LessonStudyScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)

        Label:
            text: root.lesson_title
            font_size: dp(20)
            size_hint_y: None
            height: dp(42)
            text_size: self.width, None
            halign: 'center'

        ScrollView:
            bar_width: dp(8)
            GridLayout:
                id: study_grid
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                padding: dp(10)
                row_default_height: dp(80)

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)

            BaseButton:
                text: root.finish_btn_text
                height: dp(50)
                on_press: root.finish_lesson()

            BaseButton:
                text: root.back_btn
                height: dp(50)
                on_press: app.switch_screen('lessons')

<LessonTestScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(10)

        Label:
            text: root.test_title
            font_size: dp(22)
            size_hint_y: None
            height: dp(42)

        Label:
            text: root.counter_label
            font_size: dp(16)
            size_hint_y: None
            height: dp(28)

        Label:
            text: root.prompt_text
            font_name: 'BrailleFont' if root.prompt_is_braille else 'Roboto'
            font_size: dp(80) if root.prompt_is_braille else dp(48)
            size_hint_y: 0.35
            halign: 'center'
            valign: 'middle'

        GridLayout:
            id: answers_grid
            cols: 2
            spacing: dp(8)
            size_hint_y: 0.45
            row_default_height: dp(72)
            padding: dp(6)

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(8)

            BaseButton:
                text: root.back_btn
                height: dp(50)
                on_press: app.switch_screen('lessons')

<PracticeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(45)
            spacing: dp(5)
            StreakHeader:
                streak_text: root.streak_text
                time_left: root.time_left
                quick_review_mode: root.quick_review_mode

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
                app.switch_screen('practice_levels')

<MediumPracticeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(45)
            spacing: dp(5)
            StreakHeader:
                streak_text: root.streak_text
                time_left: root.time_left
                quick_review_mode: root.quick_review_mode

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
                id: hint_btn
                text: root.hint_btn
                size_hint: 0.45, None
                height: dp(50)
                on_press: root.show_hint()
                background_disabled_normal: self.background_normal
                background_disabled_down: self.background_down

        BaseButton:
            text: root.back_btn
            size_hint: 1, None
            height: dp(50)
            pos_hint: {'center_x': 0.5}
            on_press:
                root.quick_review_mode = False
                app.stop_quick_review()
                app.switch_screen('practice_levels')

<HardPracticeScreen>:
    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)

            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(45)
                spacing: dp(5)
                StreakHeader:
                    streak_text: root.streak_text
                    time_left: root.time_left
                    quick_review_mode: root.quick_review_mode

            Label:
                id: word_label
                text: root.current_word_text
                font_size: dp(48)
                size_hint_y: 0.25
                halign: 'center'
                valign: 'middle'

            BoxLayout:
                id: braille_word_box
                orientation: 'horizontal'
                size_hint_y: 0.2
                size_hint_x: None
                width: self.minimum_width
                spacing: dp(5)
                padding: dp(5)
                pos_hint: {'center_x': 0.5}

            Widget:
                size_hint_y: 0.3

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: 0.15
                spacing: dp(10)
                padding: [dp(40), 0]
                BaseButton:
                    id: no_error_btn
                    text: root.no_errors_btn
                    on_press: root.on_no_error_press()
                    height: dp(50)
                    background_disabled_normal: self.background_normal

            BaseButton:
                text: root.back_btn
                size_hint: 1, None
                height: dp(50)
                on_press: 
                    root.quick_review_mode = False
                    app.stop_quick_review()
                    app.switch_screen('practice_levels')

        BoxLayout:
            id: correction_panel
            orientation: 'vertical'
            size_hint: (0.8, None)
            height: self.minimum_height
            pos_hint: {'center_x': 0.5, 'y': 0.2} if root.correction_panel_visible else {'x': 2}

            opacity: 1 if root.correction_panel_visible else 0
            disabled: not root.correction_panel_visible

            padding: dp(20) 
            spacing: dp(15)

            canvas.before:
                Color:
                    rgba: 0.2, 0.2, 0.2, 0.95 if self.opacity > 0 else 0
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(15)]

            GridLayout:
                cols: 2
                rows: 3
                spacing: dp(20)
                size_hint: None, None
                width: self.minimum_width
                height: self.minimum_height
                pos_hint: {'center_x': 0.5}
                id: correction_grid

            BaseButton:
                text: root.confirm_btn
                size_hint: 0.6, None
                height: dp(50)
                pos_hint: {'center_x': 0.5}
                on_press: root.confirm_correction()


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

                Label:
                    text: root.general_settings_header
                    font_size: dp(20)
                    size_hint_y: None
                    height: dp(35)
                    halign: 'left'
                    bold: True
                    color: 0.8, 0.8, 0.8, 1

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

                Widget:
                    size_hint_y: None
                    height: dp(15)

                Label:
                    text: root.easy_mode_header
                    font_size: dp(20)
                    size_hint_y: None
                    height: dp(35)
                    halign: 'left'
                    bold: True
                    color: 0.8, 0.8, 0.8, 1

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
                        text: root.include_letters
                        size_hint_x: None
                        width: dp(250)
                    Switch:
                        id: easy_letters_sw
                        active: app.easy_mode_letters
                        on_active: root.toggle_easy_letters(self.active)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.include_digits
                        size_hint_x: None
                        width: dp(250)
                    Switch:
                        id: easy_digits_sw
                        active: app.easy_mode_digits
                        on_active: root.toggle_easy_digits(self.active)

                Widget:
                    size_hint_y: None
                    height: dp(15)


                Label:
                    text: root.medium_mode_header
                    font_size: dp(20)
                    size_hint_y: None
                    height: dp(35)
                    halign: 'left'
                    bold: True
                    color: 0.8, 0.8, 0.8, 1

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.mirror_mode_label
                        size_hint_x: None
                        width: dp(250)
                    Switch:
                        id: mirror_switch
                        active: app.mirror_writing_mode
                        on_active: root.update_mirror_mode(self.active)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.include_letters
                        size_hint_x: None
                        width: dp(250)
                    Switch:
                        id: medium_letters_sw
                        active: app.medium_mode_letters
                        on_active: root.toggle_medium_letters(self.active)

                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    Label:
                        text: root.include_digits
                        size_hint_x: None
                        width: dp(250)
                    Switch:
                        id: medium_digits_sw
                        active: app.medium_mode_digits
                        on_active: root.toggle_medium_digits(self.active)

                Widget:
                    size_hint_y: None
                    height: dp(15)


                Label:
                    text: root.quick_review_header
                    font_size: dp(20)
                    size_hint_y: None
                    height: dp(35)
                    halign: 'left'
                    bold: True
                    color: 0.8, 0.8, 0.8, 1

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

        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: app.switch_screen('menu')

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
                id: reference_container
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
            on_press: app.switch_screen('menu')

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
            height: dp(120)
            multiline: True
            padding: dp(12)
            on_text: root.live_translate()

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(5)
            padding: 0

            BaseButton:
                id: copy_btn
                text: root.copy_btn
                size_hint: (1, 1)
                height: dp(60)
                on_press: root.copy_braille_result()

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
                    id: braille_output_box
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
                    padding: dp(10)

            BoxLayout:
                id: braille_input_panel
                orientation: 'vertical'
                size_hint: (0.8, 0.8)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                padding: dp(10)
                opacity: 0
                disabled: True
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 0.9 if root.opacity > 0 else 0
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(10)]

                BoxLayout:
                    size_hint_y: 0.25
                    spacing: dp(5)
                    padding: dp(5)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(0)
                        id: dot1_trans
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(3)
                        id: dot4_trans
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
                        id: dot2_trans
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(4)
                        id: dot5_trans
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
                        id: dot3_trans
                        size_hint: 1, 1
                        width: dp(80)
                        height: dp(80)
                        font_size: dp(30)

                    Button:
                        text: '*'
                        on_press: root.on_braille_dot_press(5)
                        id: dot6_trans
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
            on_press:
                root.close_braille_input()
                app.switch_screen('menu')

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
                    on_press: root.start_hard_level()
                BaseButton:
                    text: root.quick_review_btn
                    on_press: root.start_quick_review()
        BaseButton:
            text: root.back_btn
            size_hint_y: None
            height: dp(50)
            on_press: app.switch_screen('menu')
''')

braille_data = {
    'en': OrderedDict([
        ('A', [1, 0, 0, 0, 0, 0]), ('B', [1, 1, 0, 0, 0, 0]), ('C', [1, 0, 0, 1, 0, 0]),
        ('D', [1, 0, 0, 1, 1, 0]), ('E', [1, 0, 0, 0, 1, 0]), ('F', [1, 1, 0, 1, 0, 0]),
        ('G', [1, 1, 0, 1, 1, 0]), ('H', [1, 1, 0, 0, 1, 0]), ('I', [0, 1, 0, 1, 0, 0]),
        ('J', [0, 1, 0, 1, 1, 0]), ('K', [1, 0, 1, 0, 0, 0]), ('L', [1, 1, 1, 0, 0, 0]),
        ('M', [1, 0, 1, 1, 0, 0]), ('N', [1, 0, 1, 1, 1, 0]), ('O', [1, 0, 1, 0, 1, 0]),
        ('P', [1, 1, 1, 1, 0, 0]), ('Q', [1, 1, 1, 1, 1, 0]), ('R', [1, 1, 1, 0, 1, 0]),
        ('S', [0, 1, 1, 1, 0, 0]), ('T', [0, 1, 1, 1, 1, 0]), ('U', [1, 0, 1, 0, 0, 1]),
        ('V', [1, 1, 1, 0, 0, 1]), ('W', [0, 1, 0, 1, 1, 1]), ('X', [1, 0, 1, 1, 0, 1]),
        ('Y', [1, 0, 1, 1, 1, 1]), ('Z', [1, 0, 1, 0, 1, 1])
    ]),
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
        ('А', [1, 0, 0, 0, 0, 0]), ('Б', [1, 1, 0, 0, 0, 0]), ('В', [0, 1, 0, 1, 1, 1]),
        ('Г', [1, 1, 0, 1, 1, 0]), ('Д', [1, 0, 0, 1, 1, 0]), ('Е', [1, 0, 0, 0, 1, 0]),
        ('Ж', [0, 1, 0, 1, 1, 0]), ('И', [0, 1, 0, 1, 0, 0]), ('I', [1, 0, 1, 1, 1, 1]),
        ('К', [1, 0, 1, 0, 0, 0]), ('Л', [1, 1, 1, 0, 0, 0]), ('М', [1, 0, 1, 1, 0, 0]),
        ('Н', [1, 0, 1, 1, 1, 0]), ('О', [1, 0, 1, 0, 1, 0]), ('П', [1, 1, 1, 1, 0, 0]),
        ('Р', [1, 1, 1, 0, 1, 0]), ('С', [0, 1, 1, 1, 0, 0]), ('Т', [0, 1, 1, 1, 1, 0]),
        ('У', [1, 0, 1, 0, 0, 1]), ('Ф', [1, 1, 0, 1, 0, 0]), ('Х', [1, 1, 0, 0, 1, 0]),
        ('Ц', [1, 0, 0, 1, 0, 0]), ('Ч', [1, 1, 1, 1, 1, 0]), ('Ш', [1, 0, 0, 0, 1, 1]),
        ('Щ', [1, 0, 1, 1, 0, 1]), ('Ъ', [1, 1, 1, 0, 1, 1]), ('Ѣ', [0, 0, 1, 1, 1, 0]),
        ('Ы', [0, 1, 1, 1, 0, 1]), ('Ь', [0, 1, 1, 1, 1, 1]), ('Э', [0, 1, 0, 1, 0, 1]),
        ('Ю', [1, 1, 0, 0, 1, 1]), ('Я', [1, 1, 0, 1, 0, 1]), ('Ѳ', [1, 1, 1, 0, 0, 1]),
        ('Ѵ', [1, 0, 1, 0, 1, 1])
    ])
}

number_sign_dots = [0, 0, 1, 1, 1, 1]  # ⠼
digits_data = OrderedDict([
    ('1', [1, 0, 0, 0, 0, 0]), ('2', [1, 1, 0, 0, 0, 0]), ('3', [1, 0, 0, 1, 0, 0]),
    ('4', [1, 0, 0, 1, 1, 0]), ('5', [1, 0, 0, 0, 1, 0]), ('6', [1, 1, 0, 1, 0, 0]),
    ('7', [1, 1, 0, 1, 1, 0]), ('8', [1, 1, 0, 0, 1, 0]), ('9', [0, 1, 0, 1, 0, 0]),
    ('0', [0, 1, 0, 1, 1, 0])
])

translations = {
    'en': {
        'menu_title': 'Main Menu', 'practice_btn': 'Practice', 'reference_btn': 'Reference', 'settings_btn': 'Settings',
        'translator_btn': 'Translator',
        'settings_title': 'Settings', 'language_label': 'Language:', 'back_btn': 'Back',
        'streak': 'Current streak: {}\nRecord: {}', 'reference_title': 'Reference',
        'difficulty_label': 'Difficulty:', 'difficulty_2': '2 options', 'difficulty_4': '4 options',
        'difficulty_6': '6 options', 'difficulty_8': '8 options', 'difficulty_10': '10 options',
        'translator_title': 'Translator', 'input_hint': 'Enter text here', 'translate_btn': 'Translate',
        'training_btn': 'Training',
        'practice_levels_title': 'Practice Levels', 'easy_level': 'Easy Level', 'medium_level': 'Medium Level',
        'hard_level': 'Hard Level', 'quick_review': 'Quick Review',
        'coming_soon': 'Coming Soon!', 'time_label': 'Time per answer (sec):', 'time_hint': 'Enter time',
        'prev': 'Previous', 'next': 'Next',
        'use_stats': 'Use Statistics', 'reset_stats_btn': 'Reset Statistics', 'reset_stats_title': 'Reset Statistics',
        'reset_stats_text': 'Are you sure you want to reset all statistics?',
        'yes': 'Yes', 'no': 'No', 'stats_label': 'Correct: {} \n Wrong: {}', "confirm_btn": "Confirm",
        "hint_btn": "Hint", 'input_braille_btn': 'Input Braille', 'delete_btn': 'Delete',
        'no_errors_btn': 'No errors', 'general_settings_header': 'General Settings',
        'easy_mode_header': 'Easy Mode Settings',
        'quick_review_header': 'Quick Review Settings',
        'medium_mode_header': 'Medium Mode Settings',
        'mirror_mode_label': 'Mirror Writing',
        'copy_result': 'Copy',
        'include_letters': 'Include letters',
        'include_digits': 'Include digits',
        'section_letters': 'Letters',
        'section_digits': 'Digits',
        'Test': 'Test',
        'lessons_title': 'Lessons', 'study': 'Study',
        'practice_only': 'Practice', 'lesson': 'Lesson', 'letters_label': 'Letters: {}', 'start': 'Start',
        'continue': 'Continue', 'locked': 'Locked', 'complete_lesson': 'Complete lesson',
        'view_all_letters': 'View all letters', 'lesson_test_title': 'Lesson Test',
        'question': 'Question {}/{}', 'test_passed': 'Test passed!', 'test_failed': 'Test failed',
        'ok': 'OK', 'completed': 'Completed', 'available': 'Available',

    },
    'ru': {
        'menu_title': 'Главное меню', 'practice_btn': 'Практика', 'reference_btn': 'Справочник',
        'settings_btn': 'Настройки', 'translator_btn': 'Переводчик',
        'settings_title': 'Настройки', 'language_label': 'Язык:', 'back_btn': 'Назад',
        'streak': 'Текущая серия: {}\nРекорд: {}', 'reference_title': 'Справочник',
        'difficulty_label': 'Сложность:', 'difficulty_2': '2 варианта', 'difficulty_4': '4 варианта',
        'difficulty_6': '6 вариантов', 'difficulty_8': '8 вариантов', 'difficulty_10': '10 вариантов',
        'translator_title': 'Переводчик', 'input_hint': 'Введите текст', 'translate_btn': 'Перевести',
        'training_btn': 'Обучение',
        'practice_levels_title': 'Уровни практики', 'easy_level': 'Простой уровень', 'medium_level': 'Средний уровень',
        'hard_level': 'Сложный уровень', 'quick_review': 'Быстрое повторение',
        'coming_soon': 'Скоро будет!', 'time_label': 'Время на ответ (сек):', 'time_hint': 'Введите время',
        'prev': 'Предыдущий', 'next': 'Следующий',
        'use_stats': 'Использовать статистику', 'reset_stats_btn': 'Сбросить статистику',
        'reset_stats_title': 'Сброс статистики', 'reset_stats_text': 'Вы уверены, что хотите сбросить всю статистику?',
        'yes': 'Да', 'no': 'Нет', 'stats_label': 'Правильно: {} \n Ошибок: {}', "confirm_btn": "Подтвердить",
        "hint_btn": "Подсказка", 'input_braille_btn': 'Ввод Брайля', 'delete_btn': 'Удалить',
        'no_errors_btn': 'Ошибок нет',
        'general_settings_header': 'Общие настройки',
        'easy_mode_header': 'Настройки простого режима',
        'quick_review_header': 'Настройки быстрого повторения',
        'medium_mode_header': 'Настройки среднего режима',
        'mirror_mode_label': 'Зеркальное письмо',
        'copy_result': 'Копировать',
        'include_letters': 'Включать буквы',
        'include_digits': 'Включать цифры',
        'section_letters': 'Буквы',
        'section_digits': 'Цифры',
        'Test': 'Зачёт',
        'lessons_title': 'Уроки', 'study': 'Обучение',
        'practice_only': 'Практика', 'lesson': 'Урок', 'letters_label': 'Буквы: {}', 'start': 'Начать',
        'continue': 'Продолжить', 'locked': 'Заблокировано', 'complete_lesson': 'Завершить урок',
        'view_all_letters': 'Просмотрите все буквы', 'lesson_test_title': 'Тест по уроку',
        'question': 'Вопрос {}/{}', 'test_passed': 'Тест пройден!', 'test_failed': 'Тест не пройден',
        'ok': 'Ок', 'completed': 'Пройдено', 'available': 'Доступно',
    },
    'dru': {
        'menu_title': 'Главное меню', 'practice_btn': 'Практика', 'reference_btn': 'Справочникъ',
        'settings_btn': 'Настройки', 'translator_btn': 'Переводчикъ',
        'settings_title': 'Настройки', 'language_label': 'Языкъ:', 'back_btn': 'Назадъ',
        'streak': 'Текущая серія: {}\nРекордъ: {}', 'reference_title': 'Справочникъ',
        'difficulty_label': 'Сложность:', 'difficulty_2': '2 варіанта', 'difficulty_4': '4 варіанта',
        'difficulty_6': '6 варіантовъ', 'difficulty_8': '8 варіантовъ', 'difficulty_10': '10 варіантовъ',
        'translator_title': 'Переводчикъ', 'input_hint': 'Введите текстъ', 'translate_btn': 'Перевести',
        'training_btn': 'Обученіе',
        'practice_levels_title': 'Уровни практики', 'easy_level': 'Простой уровень', 'medium_level': 'Средній уровень',
        'hard_level': 'Сложный уровень', 'quick_review': 'Быстрое повтореніе',
        'coming_soon': 'Скоро будетъ!', 'time_label': 'Время на отвѣтъ (сѣкъ):', 'time_hint': 'Введите время',
        'prev': 'Предыдущій', 'next': 'Слѣдующій',
        'use_stats': 'Использовать статистику', 'reset_stats_btn': 'Сбросить статистику',
        'reset_stats_title': 'Сбросъ статистики', 'reset_stats_text': 'Вы увѣрены, что хотите сбросить всю статистику?',
        'yes': 'Да', 'no': 'Нѣтъ', 'stats_label': 'Правильно: {} \n Ошибокъ: {}', "confirm_btn": "Подтвердить",
        "hint_btn": "Подсказка", 'input_braille_btn': 'Вводъ Брайля', 'delete_btn': 'Удалить',
        'no_errors_btn': 'Ошибокъ нѣтъ', 'general_settings_header': 'Общіе настройки',
        'easy_mode_header': 'Настройки простого режима',
        'quick_review_header': 'Настройки быстраго повторенія',
        'medium_mode_header': 'Настройки средняго режима',
        'mirror_mode_label': 'Зеркальное письмо',
        'copy_result': 'Копировать',
        'include_letters': 'Включать буквы',
        'include_digits': 'Включать цифры',
        'section_letters': 'Буквы',
        'section_digits': 'Цифры',
        'Test': 'Зачетъ',
        'lessons_title': 'Уроки', 'study': 'Обученіе',
        'practice_only': 'Практика', 'lesson': 'Урокъ', 'letters_label': 'Буквы: {}', 'start': 'Начать',
        'continue': 'Продолжить', 'locked': 'Заблокировано', 'complete_lesson': 'Завершить урокъ',
        'view_all_letters': 'Просмотрите всё буквы', 'lesson_test_title': 'Тестъ по уроку',
        'question': 'Вопросъ {}/{}', 'test_passed': 'Тестъ пройденъ!', 'test_failed': 'Тестъ не пройденъ',
        'ok': 'Окъ', 'completed': 'Пройдено', 'available': 'Доступно',

    }
}

LANGUAGES = {'en': 'English', 'ru': 'Русский', 'dru': 'Дореволюціонный русскій'}


class BaseScreen(Screen):
    back_btn = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock_event = None
        self.scheduled_events = []
        self.timer_active = False
        self.app = App.get_running_app()
        self.update_lang()

    def on_pre_enter(self, *args):
        self.app = App.get_running_app()
        self.update_lang()

    def update_lang(self):
        self.back_btn = self.get_translation('back_btn')

    def get_translation(self, key):
        lang = self.app.current_language if hasattr(self.app, 'current_language') else 'en'
        return translations.get(lang, translations['en']).get(key, key)

    def load_braille_data(self):
        self.braille_data = self.app.braille_data[self.app.current_language]

    def get_braille_char(self, dots):
        code = 0x2800
        if dots[0]: code |= 0x01
        if dots[1]: code |= 0x02
        if dots[2]: code |= 0x04
        if dots[3]: code |= 0x08
        if dots[4]: code |= 0x10
        if dots[5]: code |= 0x20
        return chr(code)

    def start_timer(self, duration=None):
        self.stop_timer()
        if duration is None:
            duration = self.app.quick_review_time

        self.time_left = duration
        self.timer_active = True
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def stop_timer(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        self.timer_active = False

    def update_timer(self, dt):
        self.time_left -= 1
        if self.time_left <= 0:
            self.stop_timer()
            self.handle_timeout()

    def calculate_weight(self, char, current_time):
        if not getattr(self.app, 'use_stats', True):
            return 1.0

        stat = self.app.stats[self.app.current_language].get(char,
                                                             {'correct': 0, 'wrong': 0, 'last_seen': 0, 'hints': 0})
        last_seen = stat.get('last_seen', 0) or (current_time - 3600)
        hints_used = stat.get('hints', 0)
        hint_penalty = hints_used * 0.5
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
        global_error_rate = (all_wrong + alpha) / (
                total_attempts_global + 2 * alpha) if total_attempts_global > 0 else 0.5
        base_weight = 1.5 + global_error_rate
        total_shows = stat.get('correct', 0) + stat.get('wrong', 0)
        frequency_factor = 1.0 / (1.0 + math.log1p(total_shows))
        hours_since_seen = (current_time - last_seen) / 3600.0
        time_factor = min(1.0 + (hours_since_seen / 24.0), 3.0)
        novelty_boost = 0.4 if total_shows < 3 else 0.0
        weight = (base_weight + error_rate * 3.5 + novelty_boost + hint_penalty) * time_factor * frequency_factor
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

    def on_leave(self, *args):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()
        self.timer_active = False

    def show_coming_soon(self):
        popup = Popup(title='',
                      content=Label(text=self.get_translation('coming_soon')),
                      size_hint=(None, None), size=(dp(300), dp(200)))
        popup.open()

    def schedule_once(self, callback, delay):
        event = Clock.schedule_once(callback, delay)
        self.scheduled_events.append(event)
        return event


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


class LessonsScreen(BaseScreen):
    lessons_title = StringProperty()
    current_mode = StringProperty('letters')
    letters_tab_text = StringProperty()
    digits_tab_text = StringProperty()

    def update_lang(self):
        super().update_lang()
        self.lessons_title = self.get_translation('lessons_title')
        self.letters_tab_text = self.get_translation('section_letters')
        self.digits_tab_text = self.get_translation('section_digits')

    def on_pre_enter(self, *args):
        self.update_lang()
        self.populate_lessons()

    def switch_mode(self, mode):
        self.current_mode = mode
        self.populate_lessons()

    def populate_lessons(self):
        container = self.ids.lessons_container
        container.clear_widgets()
        app = self.app
        lang = app.current_language

        lessons = app.get_lessons(lang, self.current_mode)

        if self.current_mode == 'digits':
            completed = app.lessons_progress.get('digits_common', {}).get('completed_count', 0)
        else:
            completed = app.lessons_progress.get(lang, {}).get('completed_count', 0)

        for idx, lesson in enumerate(lessons, start=1):
            is_completed = idx <= completed
            is_unlocked = idx <= completed + 1

            row = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(110),
                            padding=[dp(6), dp(6)], spacing=dp(6))

            mode = lesson['mode']
            if mode == 'study':
                mode_title = self.get_translation('study')
            elif mode == 'practice':
                mode_title = self.get_translation('practice_only')
            else:
                mode_title = self.get_translation('Test')

            title = f"{self.get_translation('lesson')} {idx}: {mode_title}"
            row.add_widget(Label(text=title, size_hint_y=None, height=dp(28), font_size=dp(18),
                                 halign='left', valign='middle'))

            letters_text = self.get_translation('letters_label').format(
                ' '.join(lesson['letters']))
            row.add_widget(Label(text=letters_text, size_hint_y=None, height=dp(24), font_size=dp(16),
                                 halign='left', valign='middle'))

            btn_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
            btn = Button(text=self.get_translation('continue') if is_completed else self.get_translation('start'),
                         size_hint_x=0.5)
            btn.disabled = not is_unlocked
            btn.bind(on_press=lambda inst, i=idx - 1: self.open_lesson(i))
            btn_box.add_widget(btn)

            if is_completed:
                status_text = f"[color=33aa33]{self.get_translation('completed')}[/color]"
            elif is_unlocked:
                status_text = f"[color=3333aa]{self.get_translation('available')}[/color]"
            else:
                status_text = f"[color=aa3333]{self.get_translation('locked')}[/color]"

            status_label = Label(text=status_text, markup=True, size_hint_x=0.5, halign='right', valign='middle')
            btn_box.add_widget(status_label)

            row.add_widget(btn_box)
            container.add_widget(row)

    def open_lesson(self, lesson_index):
        app = self.app
        lang = app.current_language
        lesson = app.get_lessons(lang, self.current_mode)[lesson_index]

        if lesson['mode'] == 'study':
            scr = app.get_screen('lesson_study')
            scr.set_lesson(lesson_index, lesson['letters'], self.current_mode)
            app.switch_screen('lesson_study')
        else:
            scr = app.get_screen('lesson_test')
            is_exam = lesson.get('mode') == 'exam'
            scr.set_lesson(lesson_index, lesson['letters'], is_final_exam=is_exam, lesson_type=self.current_mode)
            app.switch_screen('lesson_test')


class LessonStudyScreen(BaseScreen):
    lesson_title = StringProperty()
    finish_btn_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lesson_index = 0
        self.letters = []
        self.lesson_type = 'letters'

    def update_lang(self):
        super().update_lang()
        self.finish_btn_text = self.get_translation('complete_lesson')

    def set_lesson(self, lesson_index, letters, lesson_type='letters'):
        self.lesson_index = lesson_index
        self.letters = letters[:]
        self.lesson_type = lesson_type
        self.update_lang()
        mode_title = self.get_translation('study')
        self.lesson_title = f"{self.get_translation('lesson')} {lesson_index + 1}: {mode_title}"
        self._populate_grid()

    def _populate_grid(self):
        grid = self.ids.study_grid
        grid.clear_widgets()

        is_digits = (self.lesson_type == 'digits')
        ns = self.get_braille_char(number_sign_dots)

        for char in self.letters:
            if is_digits:
                dots = digits_data[char]
                braille_char = ns + self.get_braille_char(dots)
            else:
                dots = self.app.braille_data[self.app.current_language][char]
                braille_char = self.get_braille_char(dots)

            letter_label = Label(text=char, font_size=dp(48))
            braille_label = Label(text=braille_char, font_name='BrailleFont', font_size=dp(52))

            grid.add_widget(letter_label)
            grid.add_widget(braille_label)

    def finish_lesson(self):
        self.app.mark_lesson_completed(self.app.current_language, self.lesson_index, self.lesson_type)
        self.app.switch_screen('lessons')


class LessonTestScreen(BaseScreen):
    test_title = StringProperty()
    counter_label = StringProperty()
    prompt_text = StringProperty()
    prompt_is_braille = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lesson_index = 0
        self.letters = []
        self.questions_total = 0
        self.question_list = []
        self.q_index = 0
        self.correct = 0
        self.invert_mode = False
        self.correct_button = None
        self.scheduled_events = []
        self.lesson_type = 'letters'

    def schedule_once(self, func, delay):
        ev = Clock.schedule_once(func, delay)
        self.scheduled_events.append(ev)
        return ev

    def on_leave(self, *args):
        for ev in self.scheduled_events:
            ev.cancel()
        self.scheduled_events.clear()

    def update_lang(self):
        super().update_lang()
        self.test_title = self.get_translation('lesson_test_title')

    def set_lesson(self, lesson_index, letters, is_final_exam=False, lesson_type='letters'):
        self.lesson_index = lesson_index
        self.letters = letters[:]
        self.lesson_type = lesson_type

        if is_final_exam:
            self.questions_total = len(self.letters) * 3
            self.question_list = self.letters * 3
        else:
            self.questions_total = max(8, len(self.letters) * 2)
            self.question_list = self.letters * 2
            while len(self.question_list) < self.questions_total:
                self.question_list.append(random.choice(self.letters))

        random.shuffle(self.question_list)

        self.q_index = 0
        self.correct = 0
        self.update_lang()
        self.next_question()

    def next_question(self, *_):
        grid = self.ids.answers_grid
        grid.clear_widgets()
        self.correct_button = None

        if self.q_index >= len(self.question_list):
            self.finish_test()
            return

        self.q_index += 1
        self.counter_label = self.get_translation('question').format(self.q_index, self.questions_total)

        char = self.question_list[self.q_index - 1]
        is_digits = (self.lesson_type == 'digits')
        ns = self.get_braille_char(number_sign_dots)

        if is_digits:
            dots = digits_data[char]
        else:
            dots = self.app.braille_data[self.app.current_language][char]

        self.invert_mode = random.random() < 0.5

        if self.invert_mode:
            self.prompt_text = char
            self.prompt_is_braille = False
        else:
            if is_digits:
                self.prompt_text = ns + self.get_braille_char(dots)
            else:
                self.prompt_text = self.get_braille_char(dots)
            self.prompt_is_braille = True

        options_count = min(4, len(self.letters))
        answers = [char]
        while len(answers) < options_count:
            c = random.choice(self.letters)
            if c not in answers:
                answers.append(c)
        random.shuffle(answers)

        for a in answers:
            btn = Button(size_hint=(1, None), height=dp(72), font_size=dp(24))
            btn.background_disabled_normal = btn.background_normal
            btn.background_disabled_down = btn.background_down
            btn.disabled_color = (1, 1, 1, 1)
            btn.answer_char = a

            if self.invert_mode:
                if is_digits:
                    btn.text = ns + self.get_braille_char(digits_data[a])
                else:
                    btn.text = self.get_braille_char(self.app.braille_data[self.app.current_language][a])
                btn.font_name = 'BrailleFont'
                btn.font_size = dp(36)
            else:
                btn.text = a
                btn.font_name = 'Roboto'

            btn.bind(on_press=lambda inst, correct_char=char: self.check_answer(inst, correct_char))
            grid.add_widget(btn)
            if a == char:
                self.correct_button = btn

    def check_answer(self, instance, correct_char):
        for ch in self.ids.answers_grid.children:
            ch.disabled = True
            ch.disabled_color = (1, 1, 1, 1)

        if instance.answer_char == correct_char:
            instance.background_color = (0, 1, 0, 1)
            self.correct += 1
            self.app.update_char_stat(correct_char, True)
        else:
            instance.background_color = (1, 0, 0, 1)
            if self.correct_button:
                self.correct_button.background_color = (0, 1, 0, 1)
            self.app.update_char_stat(correct_char, False)

        self.schedule_once(self.next_question, 0.8)

    def finish_test(self):
        required_ratio = 0.9
        passed = self.correct >= math.ceil(required_ratio * self.questions_total)
        title = self.get_translation('test_passed') if passed else self.get_translation('test_failed')
        popup = Popup(title=title, size_hint=(None, None), size=(dp(320), dp(200)))

        def close_and_back(*_):
            popup.dismiss()
            self.app.switch_screen('lessons')

        if passed:
            self.app.mark_lesson_completed(self.app.current_language, self.lesson_index, self.lesson_type)

        percent = int(self.correct / self.questions_total * 100)
        btn = Button(text=self.get_translation('ok'), size_hint=(1, None), height=dp(50))
        btn.bind(on_press=close_and_back)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"{self.correct}/{self.questions_total} ({percent}%)", size_hint=(1, 1)))
        layout.add_widget(btn)
        popup.content = layout
        popup.open()


class PracticeScreen(BaseScreen):
    streak_text = StringProperty()
    braille_char = StringProperty()
    time_left = NumericProperty(5)
    timer_active = BooleanProperty(False)
    quick_review_mode = BooleanProperty(False)
    invert_mode = BooleanProperty(False)
    current_symbol = StringProperty('')

    def __init__(self, **kwargs):
        self.current_streak = 0
        self.correct_button = None
        self.clock_event = None
        self.scheduled_events = []
        super().__init__(**kwargs)
        self.bind(on_pre_enter=self.on_pre_enter)
        self.bind(on_leave=self.on_leave)

    def update_streak_text(self):
        lang = self.app.current_language
        record_type = 'quick' if self.quick_review_mode else 'practice'
        current_value = self.app.quick_streak if self.quick_review_mode else self.current_streak
        self.streak_text = self.get_translation('streak').format(
            current_value,
            self.app.high_scores[lang][record_type])

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
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
        else:
            self.current_streak = 0
            self.update_streak_text()
            self.schedule_once(lambda dt: self.reset_interface(reset_streak=False), 1.2)

    def _update_grid(self, instance, value):
        grid = self.ids.answers_grid
        grid.clear_widgets()

        pool = []
        if self.app.easy_mode_letters:
            pool.extend(braille_data[self.app.current_language].keys())
        if self.app.easy_mode_digits:
            pool.extend(digits_data.keys())

        if not pool:
            pool = list(braille_data[self.app.current_language].keys())

        if not self.current_symbol:
            return

        answers = [self.current_symbol]

        while len(answers) < int(self.app.current_difficulty):
            distractor = random.choice(pool)
            if distractor not in answers:
                answers.append(distractor)
        random.shuffle(answers)

        horizontal_padding = dp(20)
        spacing = dp(5)
        available_width = grid.width - (2 * horizontal_padding)
        available_height = grid.height
        num_options = len(answers)
        min_btn_width = dp(80)
        max_cols_by_width = max(1, int(available_width // (min_btn_width + spacing)))
        best_cols = 1
        best_row_height = 0

        for c in range(1, min(max_cols_by_width, num_options) + 1):
            rows = math.ceil(num_options / c)
            h = (available_height - (rows - 1) * spacing) / rows

            if h > best_row_height:
                best_row_height = h
                best_cols = c

        final_row_height = min(best_row_height, dp(110))
        final_row_height = max(final_row_height, dp(50))
        grid.cols = best_cols
        grid.padding = [horizontal_padding, 0, horizontal_padding, 0]
        grid.spacing = spacing
        grid.row_default_height = final_row_height
        grid.row_force_default = True
        ns = self.get_braille_char(number_sign_dots)

        for answer in answers:
            btn = Button(
                size_hint=(1, None),
                height=final_row_height,
                on_press=self.check_answer)

            btn.background_disabled_normal = btn.background_normal
            btn.background_disabled_down = btn.background_down
            btn.disabled_color = (1, 1, 1, 1)

            if self.invert_mode:
                if answer in digits_data:
                    btn.text = ns + self.get_braille_char(digits_data[answer])
                else:
                    btn.text = self.get_braille_char(braille_data[self.app.current_language][answer])
                btn.font_name = 'BrailleFont'
                btn.font_size = min(dp(38), final_row_height * 0.55)
            else:
                btn.text = answer
                btn.font_name = 'Roboto'
                btn.font_size = min(dp(24), final_row_height * 0.4)

            btn.background_color = (1, 1, 1, 1)
            btn.answer_char = answer

            if answer == self.current_symbol:
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
        super().on_leave(*args)
        self.ids.answers_grid.unbind(size=self._update_grid)

    def update_lang(self):
        super().update_lang()
        self.update_streak_text()

    def new_question(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.timer_active = False

        current_time = time.time()

        pool = []
        if self.app.easy_mode_letters:
            pool.extend(braille_data[self.app.current_language].keys())
        if self.app.easy_mode_digits:
            pool.extend(digits_data.keys())

        if not pool:
            return

        weights = [self.calculate_weight(ch, current_time) for ch in pool]

        if hasattr(self, 'current_symbol') and self.current_symbol in pool:
            idx = pool.index(self.current_symbol)
            weights[idx] *= 0.2

        self.current_symbol = self.weighted_choice(pool, weights)
        self.is_digit = self.current_symbol in digits_data

        if self.is_digit:
            self.current_dots = digits_data[self.current_symbol]
        else:
            self.current_dots = braille_data[self.app.current_language][self.current_symbol]

        self.invert_mode = random.random() < 0.5

        ns = self.get_braille_char(number_sign_dots)
        if self.invert_mode:
            self.braille_char = self.current_symbol
        else:
            if self.is_digit:
                self.braille_char = ns + self.get_braille_char(self.current_dots)
            else:
                self.braille_char = self.get_braille_char(self.current_dots)

        lang = self.app.current_language
        self.app.stats[lang].setdefault(self.current_symbol, {'correct': 0, 'wrong': 0, 'last_seen': 0, 'hints': 0})
        self.app.stats[lang][self.current_symbol]['last_seen'] = current_time
        self.app.save_stats()

        self.ids.answers_grid.clear_widgets()
        self._update_grid(None, None)

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

        char = self.current_symbol
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
                self.app.quick_streak = max(0, self.app.quick_streak - 1)
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
    hint_btn = StringProperty()
    quick_review_mode = BooleanProperty(False)
    time_left = NumericProperty(5)
    timer_active = BooleanProperty(False)
    clock_event = None
    hint_used = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_buttons = []
        self.score = 0
        self.current_streak = 0
        self.scheduled_events = []
        self.hint_used = False
        self.current_letter = ''

    def _enable_controls(self):
        if self.dot_buttons:
            for btn in self.dot_buttons:
                btn.disabled = False
        if 'confirm_btn' in self.ids:
            self.ids.confirm_btn.disabled = False
        if 'hint_btn' in self.ids:
            self.ids.hint_btn.disabled = False

    def update_lang(self):
        super().update_lang()
        self.confirm_btn = self.get_translation('confirm_btn')
        self.hint_btn = self.get_translation('hint_btn')

    def on_pre_enter(self, *args):
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()

        self.update_lang()
        self.load_braille_data()

        if not self.dot_buttons:
            self.dot_buttons = [
                self.ids.dot1, self.ids.dot2, self.ids.dot3,
                self.ids.dot4, self.ids.dot5, self.ids.dot6]

        self.update_streak_text()
        self.new_question()

    def update_streak_text(self):
        if self.quick_review_mode:
            current_value = self.app.quick_streak
            record = self.app.high_scores[self.app.current_language].get('quick', 0)
        else:
            current_value = self.current_streak
            record = self.app.high_scores[self.app.current_language].get('medium_practice', 0)
        self.streak_text = self.get_translation('streak').format(current_value, record)

    def get_logical_index(self, visual_index):
        if self.app.mirror_writing_mode:
            mapping = {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
            return mapping.get(visual_index, visual_index)
        return visual_index

    def handle_timeout(self):
        self.timer_active = False
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        self._disable_and_show_correct_answer()

        if self.quick_review_mode:
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
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
        self.ids.hint_btn.disabled = True

        for visual_index, btn in enumerate(self.dot_buttons):
            logical_index = self.get_logical_index(visual_index)

            correct = self.current_dots[logical_index]
            user = user_input[logical_index]

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
        self.hint_used = False
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)
            btn.state = 'normal'

        current_time = time.time()

        pool = []
        if self.app.medium_mode_letters:
            pool.extend(braille_data[self.app.current_language].keys())
        if self.app.medium_mode_digits:
            pool.extend(digits_data.keys())

        if not pool:
            return

        weights = [self.calculate_weight(ch, current_time) for ch in pool]

        if hasattr(self, 'current_symbol') and self.current_symbol in pool:
            idx = pool.index(self.current_symbol)
            weights[idx] *= 0.2

        self.current_symbol = self.weighted_choice(pool, weights)

        if self.current_symbol in digits_data:
            self.current_dots = digits_data[self.current_symbol]
        else:
            self.current_dots = braille_data[self.app.current_language][self.current_symbol]

        self.current_letter = self.current_symbol

        lang = self.app.current_language
        self.app.stats[lang].setdefault(self.current_symbol, {'correct': 0, 'wrong': 0, 'last_seen': 0, 'hints': 0})
        self.app.stats[lang][self.current_symbol]['last_seen'] = current_time
        self.app.save_stats()

        if self.quick_review_mode:
            self.start_timer()

    def on_dot_press(self, visual_index, instance):
        logical_index = self.get_logical_index(visual_index)

        self.user_input[logical_index] = 1 - self.user_input[logical_index]
        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[logical_index] else (1, 1, 1, 1)

    def show_hint(self):
        if not self.hint_used and self.current_letter:
            self.hint_used = True

            lang = self.app.current_language
            self.app.stats[lang].setdefault(self.current_letter, {}).setdefault('hints', 0)
            self.app.stats[lang][self.current_letter]['hints'] += 1
            self.app.save_stats()

            self.ids.hint_btn.disabled = True

            for visual_index, btn in enumerate(self.dot_buttons):
                logical_index = self.get_logical_index(visual_index)

                correct = self.current_dots[logical_index]
                user = self.user_input[logical_index]

                if correct and not user:
                    btn.background_color = (0.5, 1, 0.5, 1)
                elif not correct and user:
                    btn.background_color = (1, 0.5, 0.5, 1)
                elif correct and user:
                    btn.background_color = (0, 1, 0, 1)

    def confirm_answer(self):
        if not self.current_letter:
            return

        if self.timer_active:
            self.clock_event.cancel()
            self.timer_active = False

        is_correct = self.user_input == self.current_dots
        self._disable_and_show_correct_answer(self.user_input)

        lang = self.app.current_language

        if self.current_letter not in self.app.stats[lang]:
            self.app.stats[lang][self.current_letter] = {'correct': 0, 'wrong': 0, 'last_seen': 0, 'hints': 0}

        # if self.hint_used:
        #     if is_correct:
        #         self.app.stats[lang][self.current_letter]['correct'] += 0.5
        #         self.app.stats[lang][self.current_letter]['wrong'] += 0.5
        #     else:
        #         self.app.stats[lang][self.current_letter]['wrong'] += 1
        if is_correct:
            self.app.stats[lang][self.current_letter]['correct'] += 1
        else:
            self.app.stats[lang][self.current_letter]['wrong'] += 1

        self.app.stats[lang][self.current_letter]['last_seen'] = time.time()
        self.app.save_stats()

        if self.quick_review_mode:
            if is_correct and not self.hint_used:
                self.app.quick_streak += 1
                if self.app.quick_streak > self.app.high_scores[lang]['quick']:
                    self.app.high_scores[lang]['quick'] = self.app.quick_streak
                    self.app.save_high_scores()
            elif not is_correct:
                self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
        else:
            if is_correct:
                if not self.hint_used:
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


class HardPracticeScreen(BaseScreen):
    streak_text = StringProperty(" \n ")
    current_word_text = StringProperty()
    no_errors_btn = StringProperty()
    confirm_btn = StringProperty()
    current_streak = NumericProperty(0)
    current_word = ''
    correct_braille_word = ListProperty()
    displayed_braille_word = ListProperty()
    has_error = BooleanProperty(False)
    error_index = NumericProperty(-1)
    sub_mode = StringProperty('A')
    correction_panel_visible = BooleanProperty(False)
    user_input = ListProperty([0] * 6)
    _controls_locked = BooleanProperty(False)
    quick_review_mode = BooleanProperty(False)
    time_left = NumericProperty(5)
    timer_active = BooleanProperty(False)
    clock_event = None

    def __init__(self, **kwargs):
        self.correction_dot_buttons = []
        self.scheduled_events = []
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        grid = self.ids.correction_grid
        if not grid.children:
            for i in [0, 3, 1, 4, 2, 5]:
                btn = Button(
                    text='*', font_size=dp(24), width=dp(60), height=dp(60),
                    size_hint=(None, None),
                )
                btn.bind(on_press=lambda instance, index=i: self.on_correction_dot_press(index, instance))
                self.correction_dot_buttons.append(btn)
                grid.add_widget(btn)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()

        self.load_braille_data()
        self.update_streak_text()
        self.new_question()

    def update_lang(self):
        super().update_lang()
        self.no_errors_btn = self.get_translation('no_errors_btn')
        self.confirm_btn = self.get_translation('confirm_btn')

    def update_streak_text(self):
        if self.quick_review_mode:
            current_value = self.app.quick_streak
            record = self.app.high_scores[self.app.current_language].get('quick', 0)
        else:
            current_value = self.current_streak
            record = self.app.high_scores[self.app.current_language].get('hard_practice', 0)
        self.streak_text = self.get_translation('streak').format(current_value, record)

    def generate_word(self, length=None):
        lang = self.app.current_language
        word_list = self.app.word_lists.get(lang)

        if word_list:
            if length:
                filtered = [w for w in word_list if len(w) == length]
                if filtered:
                    return random.choice(filtered)
            return random.choice(word_list)

        current_time = time.time()
        items = list(self.braille_data.keys())
        weights = [self.calculate_weight(ch, current_time) for ch in items]
        length = length if length else random.randint(3, 6)
        word_list = [self.weighted_choice(items, weights) for _ in range(length)]
        return "".join(word_list)

    def handle_timeout(self):
        self.timer_active = False
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        self.lock_controls()
        if self.has_error:
            for btn in self.ids.braille_word_box.children:
                if btn.char_index == self.error_index:
                    btn.background_color = (0, 1, 0, 1)
                    break
        else:
            self.ids.no_error_btn.background_color = (0, 1, 0, 1)

        self.app.quick_streak = max(0, self.app.quick_streak - 1)
        self.update_streak_text()

        if self.has_error:
            self._update_char_stats(self.current_word[self.error_index], correct=False)

        self.schedule_once(lambda dt: self.app.next_quick_step(), 1.5)

    def new_question(self):
        self.reset_ui_state()
        self.load_braille_data()

        current_time = time.time()
        items = list(self.braille_data.keys())
        weights = [self.calculate_weight(ch, current_time) for ch in items]

        if self.quick_review_mode:
            length = random.choice([3, 4])
            self.sub_mode = 'A'
            self.has_error = random.random() < 0.92
        else:
            length = random.randint(3, 6)
            self.sub_mode = random.choice(['A', 'B'])  # A - find / B - correct
            self.has_error = random.random() < 0.85

        self.current_word = self.generate_word(length)
        self.current_word_text = self.current_word

        lang = self.app.current_language
        for ch in set(self.current_word):
            self.app.stats[lang].setdefault(ch, {'correct': 0, 'wrong': 0, 'last_seen': 0, 'hints': 0})
            self.app.stats[lang][ch]['last_seen'] = current_time
        self.app.save_stats()

        self.correct_braille_word = [self.braille_data[ch] for ch in self.current_word]
        self.displayed_braille_word = [list(dots) for dots in self.correct_braille_word]

        self.error_index = -1
        if self.has_error:
            self.error_index = random.randint(0, len(self.current_word) - 1)
            wrong_char = random.choice([c for c in self.braille_data.keys()
                                        if c != self.current_word[self.error_index]])
            self.displayed_braille_word[self.error_index] = self.braille_data[wrong_char]

        self.update_braille_display()

        if self.quick_review_mode:
            self.start_timer()

    def _update_char_stats(self, char, correct):

        lang = self.app.current_language
        stat = self.app.stats[lang].setdefault(char, {'correct': 0, 'wrong': 0, 'last_seen': 0, 'hints': 0})
        if correct:
            stat['correct'] += 1
        else:
            stat['wrong'] += 1
        stat['last_seen'] = time.time()
        self.app.save_stats()

    def handle_correct_answer(self):
        if self.quick_review_mode:
            self.app.quick_streak += 1
            if self.app.quick_streak > self.app.high_scores[self.app.current_language]['quick']:
                self.app.high_scores[self.app.current_language]['quick'] = self.app.quick_streak
                self.app.save_high_scores()
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
            return

        self.current_streak += 1
        if self.current_streak > self.app.high_scores[self.app.current_language].get('hard_practice', 0):
            self.app.high_scores[self.app.current_language]['hard_practice'] = self.current_streak
            self.app.save_high_scores()
        self.update_streak_text()
        self.schedule_once(lambda dt: self.new_question(), 1.5)

    def handle_wrong_answer(self):
        if self.quick_review_mode:
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text()
            self.schedule_once(lambda dt: self.app.next_quick_step(), 2.0)
            return

        self.current_streak = 0
        self.update_streak_text()
        self.schedule_once(lambda dt: self.new_question(), 2.5)

    def confirm_correction(self):
        if self._controls_locked:
            return
        self.stop_timer()
        self.lock_controls(lock_all=False)
        self.correction_panel_visible = False

        correct_dots = self.correct_braille_word[self.error_index]
        user_correct = self.user_input == correct_dots

        for btn in self.ids.braille_word_box.children:
            if btn.char_index == self.error_index:
                btn.background_color = (0, 1, 0, 1) if user_correct else (1, 0, 0, 1)
                break

        if user_correct:
            self.handle_correct_answer()
        else:
            self.handle_wrong_answer()

    def reset_ui_state(self):
        self._controls_locked = False
        if hasattr(self.ids, 'braille_word_box'):
            self.ids.braille_word_box.clear_widgets()
        self.correction_panel_visible = False
        if hasattr(self.ids, 'no_error_btn'):
            self.ids.no_error_btn.disabled = False
            self.ids.no_error_btn.background_color = (1, 1, 1, 1)
        self.user_input = [0] * 6
        for btn in self.correction_dot_buttons:
            btn.background_color = (1, 1, 1, 1)

    def update_braille_display(self):
        box = self.ids.braille_word_box
        box.clear_widgets()
        for i, dots in enumerate(self.displayed_braille_word):
            braille_char = self.get_braille_char(dots)
            btn = Button(text=braille_char, font_name='BrailleFont', font_size=dp(42), size_hint=(None, 1),
                         width=dp(50))
            btn.char_index = i
            btn.bind(on_press=self.on_braille_char_press)
            btn.background_disabled_normal = btn.background_normal
            box.add_widget(btn)

    def lock_controls(self, lock_all=True):
        self._controls_locked = True
        if lock_all:
            for child in self.ids.braille_word_box.children:
                child.disabled = True
                child.disabled_color = (1, 1, 1, 1)
            self.ids.no_error_btn.disabled = True
            self.ids.no_error_btn.disabled_color = (1, 1, 1, 1)

    def on_braille_char_press(self, instance):
        if self._controls_locked: return
        self.stop_timer()
        self.lock_controls()

        if self.has_error and instance.char_index == self.error_index:
            if self.sub_mode == 'A':
                instance.background_color = (0, 1, 0, 1)
                self.handle_correct_answer()
            else:
                instance.background_color = (1, 0.7, 0, 1)
                self.correction_panel_visible = True
                self._controls_locked = False

        else:
            instance.background_color = (1, 0, 0, 1)
            if self.has_error:
                for btn in self.ids.braille_word_box.children:
                    if btn.char_index == self.error_index:
                        btn.background_color = (0, 1, 0, 1)
                        break
            else:
                self.ids.no_error_btn.background_color = (0, 1, 0, 1)

            self.handle_wrong_answer()

    def on_no_error_press(self):
        if self._controls_locked: return
        self.stop_timer()
        self.lock_controls()

        if not self.has_error:
            self.ids.no_error_btn.background_color = (0, 1, 0, 1)
            self.handle_correct_answer()
        else:
            self.ids.no_error_btn.background_color = (1, 0, 0, 1)
            for btn in self.ids.braille_word_box.children:
                if btn.char_index == self.error_index:
                    btn.background_color = (0, 1, 0, 1)
                    break
            self.handle_wrong_answer()

    def on_correction_dot_press(self, index, instance):
        self.user_input[index] = 1 - self.user_input[index]
        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[index] else (1, 1, 1, 1)


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
        scr = self.app.get_screen('medium_practice')
        scr.quick_review_mode = False
        self.app.switch_screen('medium_practice')

    def start_easy_level(self):
        scr = self.app.get_screen('practice')
        scr.quick_review_mode = False
        self.app.switch_screen('practice')
        scr.new_question()

    def start_hard_level(self):
        self.app.switch_screen('hard_practice')


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
    general_settings_header = StringProperty()
    easy_mode_header = StringProperty()
    quick_review_header = StringProperty()
    medium_mode_header = StringProperty()
    mirror_mode_label = StringProperty()
    include_letters = StringProperty()
    include_digits = StringProperty()

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
        self.general_settings_header = self.get_translation('general_settings_header')
        self.easy_mode_header = self.get_translation('easy_mode_header')
        self.quick_review_header = self.get_translation('quick_review_header')
        self.medium_mode_header = self.get_translation('medium_mode_header')
        self.mirror_mode_label = self.get_translation('mirror_mode_label')
        self.include_letters = self.get_translation('include_letters')
        self.include_digits = self.get_translation('include_digits')
        self.current_lang = LANGUAGES[lang]
        self.difficulty_values = [
            self.get_translation(f'difficulty_{d}')
            for d in ['2', '4', '6', '8', '10']]
        self.current_difficulty_str = self.get_translation(
            f'difficulty_{self.app.current_difficulty}')

    def update_settings(self, key, value):
        if key == 'language':
            lang_code = next((k for k, v in LANGUAGES.items() if v == value), 'en')
            self.app.current_language = lang_code
            self.app.load_word_list(lang_code)
            self.current_lang = LANGUAGES[lang_code]
        elif key == 'difficulty':
            diff_code = next((k.split('_')[1] for k, v in translations[self.app.current_language].items()
                              if v == value and k.startswith('difficulty_')), '4')
            self.app.current_difficulty = diff_code
        elif key == 'time':
            try:
                t = int(value) if value else 5
                if 1 <= t <= 25:
                    self.app.quick_review_time = t
                else:
                    self.app.quick_review_time = 5
            except ValueError:
                self.app.quick_review_time = 5
        self.app.save_settings()
        self.app.update_all_screens()

    def update_mirror_mode(self, active):
        self.app.mirror_writing_mode = active
        self.app.save_settings()

    def update_update_use_stats(self, active):
        self.app.use_stats = active
        self.app.save_settings()
        if 'reference' in self.app._loaded_screens:
            ref_screen = self.app.get_screen('reference')
            if hasattr(ref_screen, 'update_reference'):
                ref_screen.update_reference()

    def _prevent_both_off(self, mode):
        if mode == 'easy':
            if not self.app.easy_mode_letters and not self.app.easy_mode_digits:
                return True
        elif mode == 'medium':
            if not self.app.medium_mode_letters and not self.app.medium_mode_digits:
                return True
        return False

    def toggle_easy_letters(self, value):
        self.app.easy_mode_letters = value
        if not value and not self.app.easy_mode_digits:
            self.app.easy_mode_digits = True
            Clock.schedule_once(lambda dt: setattr(self.ids.easy_digits_sw, 'active', True))
        self.app.save_settings()

    def toggle_easy_digits(self, value):
        self.app.easy_mode_digits = value
        if not value and not self.app.easy_mode_letters:
            self.app.easy_mode_letters = True
            Clock.schedule_once(lambda dt: setattr(self.ids.easy_letters_sw, 'active', True))
        self.app.save_settings()

    def toggle_medium_letters(self, value):
        self.app.medium_mode_letters = value
        if not value and not self.app.medium_mode_digits:
            self.app.medium_mode_digits = True
            Clock.schedule_once(lambda dt: setattr(self.ids.medium_digits_sw, 'active', True))
        self.app.save_settings()

    def toggle_medium_digits(self, value):
        self.app.medium_mode_digits = value
        if not value and not self.app.medium_mode_letters:
            self.app.medium_mode_letters = True
            Clock.schedule_once(lambda dt: setattr(self.ids.medium_letters_sw, 'active', True))
        self.app.save_settings()

    def reset_stats(self):
        popup = Popup(
            title=self.get_translation('reset_stats_title'),
            size_hint=(None, None),
            size=(dp(360), dp(260)),
            auto_dismiss=False)

        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(30), dp(20), dp(30), dp(20)])

        label = Label(
            text=self.get_translation('reset_stats_text'),
            size_hint_y=None,
            height=dp(80),
            text_size=(dp(300), None),
            halign='center',
            valign='middle',
            font_size=dp(18), )
        label.bind(texture_size=lambda inst, val: setattr(label, 'height', val[1] + dp(30)))

        content.add_widget(label)

        btns = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(20))

        def do_reset(*_):
            self.app.stats = {'en': {}, 'ru': {}, 'dru': {}}
            self.app.save_stats()
            popup.dismiss()

        btn_yes = Button(text=self.get_translation('yes'))
        btn_no = Button(text=self.get_translation('no'))

        btn_yes.bind(on_press=do_reset)
        btn_no.bind(on_press=popup.dismiss)

        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
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
        container = self.ids.reference_container
        container.clear_widgets()

        header_letters = Label(
            text=self.get_translation('section_letters'),
            font_size=dp(22),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle',
            bold=True,
            color=(0.8, 0.8, 0.8, 1))
        header_letters.bind(size=header_letters.setter('text_size'))
        container.add_widget(header_letters)

        grid_letters = GridLayout(cols=2, spacing=dp(20), size_hint_y=None)
        grid_letters.bind(minimum_height=grid_letters.setter('height'))

        for letter, dots in self.all_chars:
            braille_char = self.get_braille_char(dots)
            self._add_item_to_grid(grid_letters, letter, braille_char, letter)

        container.add_widget(grid_letters)

        container.add_widget(Widget(size_hint_y=None, height=dp(20)))

        header_digits = Label(
            text=self.get_translation('section_digits'),
            font_size=dp(22),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle',
            bold=True,
            color=(0.8, 0.8, 0.8, 1))
        header_digits.bind(size=header_digits.setter('text_size'))
        container.add_widget(header_digits)

        grid_digits = GridLayout(cols=2, spacing=dp(20), size_hint_y=None)
        grid_digits.bind(minimum_height=grid_digits.setter('height'))

        ns = self.get_braille_char(number_sign_dots)
        for digit, dots in digits_data.items():
            braille_char = ns + self.get_braille_char(dots)
            self._add_item_to_grid(grid_digits, digit, braille_char, digit)

        container.add_widget(grid_digits)

    def _add_item_to_grid(self, grid, display_text, braille_text, stats_key):
        label_text = Label(
            text=display_text,
            font_size=dp(45),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle')
        grid.add_widget(label_text)

        label_braille = Label(
            text=braille_text,
            font_name='BrailleFont',
            font_size=dp(45),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle')
        grid.add_widget(label_braille)

        if self.app.use_stats:
            stat = self.app.stats[self.app.current_language].get(stats_key, {'correct': 0, 'wrong': 0})
            stats_label = Label(
                text=self.get_translation('stats_label').format(stat['correct'], stat['wrong']),
                font_size=dp(18),
                size_hint_y=None,
                height=dp(40),
                halign='center',
                valign='middle',
                color=(0.7, 0.7, 0.7, 1))
            grid.add_widget(stats_label)
            grid.add_widget(Widget(size_hint_y=None, height=dp(10)))


class TranslatorScreen(BaseScreen):
    translator_title = StringProperty()
    input_hint = StringProperty()
    input_braille_btn = StringProperty()
    confirm_btn = StringProperty()
    delete_btn = StringProperty()
    copy_btn = StringProperty('')
    braille_input_active = BooleanProperty(False)
    user_braille_dots = ListProperty([0] * 6)
    dot_buttons = ListProperty([])
    _last_translated_text = StringProperty('')
    full_braille_text = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.braille_to_char = {}
        self.input_number_mode = False

    def on_kv_post(self, base_widget):
        self.dot_buttons = [
            self.ids.dot1_trans, self.ids.dot2_trans, self.ids.dot3_trans,
            self.ids.dot4_trans, self.ids.dot5_trans, self.ids.dot6_trans]

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.load_braille_data()
        self.braille_to_char = {tuple(v): k for k, v in self.braille_data.items()}
        Clock.schedule_once(lambda dt: self.live_translate(), 0.1)

    def update_lang(self):
        super().update_lang()
        self.translator_title = self.get_translation('translator_title')
        self.input_hint = self.get_translation('input_hint')
        self.input_braille_btn = self.get_translation('input_braille_btn')
        self.confirm_btn = self.get_translation('confirm_btn')
        self.delete_btn = self.get_translation('delete_btn')
        self.copy_btn = self.get_translation('copy_result')

    def live_translate(self, *args):
        text = self.ids.input_text.text.upper()
        if text == self._last_translated_text:
            return

        result = []
        current_data = self.braille_data
        in_number_mode = False
        ns = self.get_braille_char(number_sign_dots)

        for char in text:
            if char == '\n':
                result.append('\n')
                in_number_mode = False
                continue

            if char.isdigit():
                if not in_number_mode:
                    result.append(ns)
                    in_number_mode = True
                if char in digits_data:
                    result.append(self.get_braille_char(digits_data[char]))
                else:
                    result.append('?')
                continue

            in_number_mode = False
            if char == ' ':
                result.append(chr(0x2800))
            elif char in current_data:
                result.append(self.get_braille_char(current_data[char]))
            else:
                result.append('?')

        braille_text = ''.join(result)
        self.full_braille_text = braille_text
        self._last_translated_text = text

        output_box = self.ids.braille_output_box
        output_box.clear_widgets()

        chunk_size = 500
        if not braille_text:
            chunks = []
        else:
            chunks = [braille_text[i:i + chunk_size] for i in range(0, len(braille_text), chunk_size)]

        for chunk in chunks:
            lbl = Label(
                text=chunk,
                font_name='BrailleFont',
                font_size=dp(32),
                size_hint_y=None,
                color=(1, 1, 1, 1),
                halign='center',
                valign='top'
            )
            lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))

            output_box.add_widget(lbl)

    def copy_braille_result(self):
        text = self.full_braille_text
        if text and text != chr(0x2800):
            Clipboard.copy(text)

    def on_braille_dot_press(self, index):
        self.user_braille_dots[index] = 1 - self.user_braille_dots[index]
        btn = self.dot_buttons[index]
        btn.background_color = (0.7, 0.7, 0.7, 1) if self.user_braille_dots[index] else (1, 1, 1, 1)

    def open_braille_input(self):
        self.braille_input_active = not self.braille_input_active
        panel = self.ids.braille_input_panel
        if self.braille_input_active:
            panel.opacity = 1
            panel.disabled = False
            self.clear_braille_input()
            self.input_number_mode = False
            self.ids.input_text.focus = False
        else:
            panel.opacity = 0
            panel.disabled = True

    def close_braille_input(self):
        self.braille_input_active = False
        if self.ids:
            panel = self.ids.get('braille_input_panel')
            if panel:
                panel.opacity = 0
                panel.disabled = True

    def confirm_braille_input(self):
        input_dots = tuple(self.user_braille_dots)

        if all(d == 0 for d in input_dots):
            self.ids.input_text.text += ' '
            self.input_number_mode = False
            self.clear_braille_input()
            return

        if input_dots == tuple(number_sign_dots):
            self.input_number_mode = True
            self.clear_braille_input()
            return

        char = '?'
        if self.input_number_mode:
            found_digit = False
            for digit, dots in digits_data.items():
                if tuple(dots) == input_dots:
                    char = digit
                    found_digit = True
                    break
            if not found_digit:
                char = self.braille_to_char.get(input_dots, '?')
        else:
            char = self.braille_to_char.get(input_dots, '?')

        self.ids.input_text.text += char
        self.clear_braille_input()

    def delete_last_char(self):
        text = self.ids.input_text.text
        if text:
            self.ids.input_text.text = text[:-1]

    def clear_braille_input(self):
        self.user_braille_dots = [0] * 6
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)

    def on_leave(self, *args):
        super().on_leave(*args)
        self.close_braille_input()


class BrailleApp(App):
    current_language = StringProperty('en')
    current_difficulty = StringProperty('4')
    quick_review_time = NumericProperty(5)
    is_mobile = BooleanProperty(False)
    stats = DictProperty({'en': {}, 'ru': {}, 'dru': {}})
    use_stats = BooleanProperty(True)
    quick_streak = NumericProperty(0)
    quick_active = BooleanProperty(False)
    quick_mode_weights = DictProperty({'easy': 40, 'medium': 30, 'hard': 30})
    mirror_writing_mode = BooleanProperty(False)
    word_lists = DictProperty({})
    easy_mode_letters = BooleanProperty(True)
    easy_mode_digits = BooleanProperty(True)
    medium_mode_letters = BooleanProperty(True)
    medium_mode_digits = BooleanProperty(True)
    lessons_config = DictProperty({})
    lessons_progress = DictProperty({})

    _screen_classes = {
        'menu': MenuScreen,
        'lessons': LessonsScreen,
        'lesson_study': LessonStudyScreen,
        'lesson_test': LessonTestScreen,
        'practice_levels': PracticeLevelsScreen,
        'practice': PracticeScreen,
        'medium_practice': MediumPracticeScreen,
        'hard_practice': HardPracticeScreen,
        'reference': ReferenceScreen,
        'translator': TranslatorScreen,
        'settings': SettingsScreen,
    }

    _loaded_screens = set()

    def build(self):
        self.is_mobile = platform in ('android', 'ios')
        self.braille_data = braille_data
        self.load_settings()
        self.load_high_scores()
        self.load_lessons_progress()
        self.load_stats()
        self.load_word_list(self.current_language)
        self.digits_lessons = self.build_digits_lessons()
        sm = ScreenManager()
        self._load_screen(sm, 'menu')

        return sm

    def _load_screen(self, sm, screen_name):
        if screen_name in self._loaded_screens:
            return True

        if screen_name not in self._screen_classes:
            print(f"Unknown screen: {screen_name}")
            return False

        screen_class = self._screen_classes[screen_name]
        screen = screen_class(name=screen_name)
        sm.add_widget(screen)
        self._loaded_screens.add(screen_name)

        return True

    def switch_screen(self, screen_name):
        if self.root:
            self._load_screen(self.root, screen_name)
            self.root.current = screen_name

    def get_screen(self, screen_name):
        if self.root:
            self._load_screen(self.root, screen_name)
            return self.root.get_screen(screen_name)
        return None

    def update_all_screens(self):
        if self.root:
            for screen_name in self._loaded_screens:
                try:
                    screen = self.root.get_screen(screen_name)
                    if hasattr(screen, 'update_lang'):
                        screen.update_lang()
                except:
                    pass

    def choose_quick_mode(self):
        modes = ['easy', 'medium', 'hard']
        weights = [self.quick_mode_weights.get(m, 1) for m in modes]
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        for m, w in zip(modes, weights):
            upto += w
            if upto >= r:
                return m
        return 'easy'

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
            scr = self.get_screen('practice')
            scr.quick_review_mode = True
            self.switch_screen('practice')
            scr.new_question()
        elif mode == 'medium':
            scr = self.get_screen('medium_practice')
            scr.quick_review_mode = True
            self.switch_screen('medium_practice')
            scr.new_question()
        else:
            scr = self.get_screen('hard_practice')
            scr.quick_review_mode = True
            self.switch_screen('hard_practice')
            scr.new_question()

    def update_char_stat(self, char, is_correct):
        if not self.use_stats:
            return
        lang = self.current_language
        self.stats.setdefault(lang, {})
        self.stats[lang].setdefault(char, {'correct': 0, 'wrong': 0, 'last_seen': 0})
        if is_correct:
            self.stats[lang][char]['correct'] += 1
        else:
            self.stats[lang][char]['wrong'] += 1
        self.stats[lang][char]['last_seen'] = time.time()
        self.save_stats()

    def build_lessons_for_lang(self, lang, group_size=4):
        letters = list(self.braille_data[lang].keys())
        lessons = []
        learned = []
        for i in range(0, len(letters), group_size):
            chunk = letters[i:i + group_size]
            lessons.append({'mode': 'study', 'letters': chunk})

            if i > 0:
                lessons.append({'mode': 'practice', 'letters': chunk})

            learned.extend(chunk)
            lessons.append({'mode': 'practice', 'letters': learned[:]})

        lessons.append({'mode': 'exam', 'letters': letters})
        return lessons

    def build_digits_lessons(self):
        digits = list(digits_data.keys())
        lessons = []
        group_size = 5
        learned = []

        for i in range(0, len(digits), group_size):
            chunk = digits[i:i + group_size]
            lessons.append({'mode': 'study', 'letters': chunk})
            if i > 0:
                lessons.append({'mode': 'practice', 'letters': chunk})
            learned.extend(chunk)
            lessons.append({'mode': 'practice', 'letters': learned[:]})

        lessons.append({'mode': 'exam', 'letters': digits})
        return lessons

    def get_lessons(self, lang, lesson_type='letters'):
        if lesson_type == 'digits':
            return self.digits_lessons
        if lang not in self.lessons_config:
            self.lessons_config[lang] = self.build_lessons_for_lang(lang)
        return self.lessons_config[lang]

    def mark_lesson_completed(self, lang, idx, lesson_type):
        progress_key = 'digits_common' if lesson_type == 'digits' else lang
        prog = self.lessons_progress.setdefault(progress_key, {'completed_count': 0})
        if idx + 1 > prog.get('completed_count', 0):
            prog['completed_count'] = idx + 1
            self.save_lessons_progress()

    def load_lessons_progress(self):
        try:
            with open(self._path("lessons_progress.json"), "r", encoding="utf-8") as f:
                self.lessons_progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.lessons_progress = {}

    def save_lessons_progress(self):
        with open(self._path("lessons_progress.json"), "w", encoding="utf-8") as f:
            json.dump(self.lessons_progress, f, ensure_ascii=False, indent=2)

    def _path(self, filename):
        return os.path.join(self.user_data_dir, filename)

    def load_word_list(self, lang):
        path = os.path.join("assets", "words", f"{lang}.txt")
        if not os.path.exists(path):
            self.word_lists[lang] = None
            return
        try:
            with open(path, encoding='utf-8') as f:
                words = [line.strip().upper() for line in f if line.strip()]
                words = [w for w in words if all(c in braille_data[lang] for c in w)]
                self.word_lists[lang] = words if words else None
        except Exception as e:
            print(f"Error loading words for {lang}: {e}")
            self.word_lists[lang] = None

    def load_settings(self):
        try:
            with open(self._path("settings.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.current_language = data.get('language', 'en')
            self.current_difficulty = data.get('difficulty', '4')
            self.quick_review_time = data.get('quick_review_time', 5)
            self.use_stats = data.get('use_stats', True)
            self.mirror_writing_mode = data.get('mirror_writing_mode', False)
            self.easy_mode_letters = data.get('easy_mode_letters', True)
            self.easy_mode_digits = data.get('easy_mode_digits', True)
            self.medium_mode_letters = data.get('medium_mode_letters', True)
            self.medium_mode_digits = data.get('medium_mode_digits', True)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save_settings(self):
        with open(self._path("settings.json"), "w", encoding="utf-8") as f:
            json.dump({
                'language': self.current_language,
                'difficulty': self.current_difficulty,
                'quick_review_time': self.quick_review_time,
                'use_stats': self.use_stats,
                'mirror_writing_mode': self.mirror_writing_mode,
                'easy_mode_letters': self.easy_mode_letters,
                'easy_mode_digits': self.easy_mode_digits,
                'medium_mode_letters': self.medium_mode_letters,
                'medium_mode_digits': self.medium_mode_digits,
            }, f, ensure_ascii=False, indent=2)
        self.save_high_scores()
        self.save_stats()

    def load_high_scores(self):
        try:
            with open(self._path("highscores.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
            for lang in ['en', 'ru', 'dru']:
                if not isinstance(data.get(lang), dict):
                    data[lang] = {}
                data[lang].setdefault('practice', 0)
                data[lang].setdefault('medium_practice', 0)
                data[lang].setdefault('hard_practice', 0)
                data[lang].setdefault('quick', 0)
            self.high_scores = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.high_scores = {
                lang: {'practice': 0, 'medium_practice': 0, 'hard_practice': 0, 'quick': 0}
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
        if not self.use_stats:
            return
        with open(self._path("stats.json"), "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def on_start(self):
        Window.bind(on_keyboard=self.on_back_btn)

    def on_back_btn(self, window, key, *args):
        if key == 27:
            current = self.root.current

            back_map = {
                'lessons': 'menu',
                'lesson_study': 'lessons',
                'lesson_test': 'lessons',
                'practice_levels': 'menu',
                'practice': 'practice_levels',
                'medium_practice': 'practice_levels',
                'hard_practice': 'practice_levels',
                'reference': 'menu',
                'translator': 'menu',
                'settings': 'menu'
            }

            if current in back_map:
                screen = self.root.current_screen
                if hasattr(screen, 'quick_review_mode') and screen.quick_review_mode:
                    self.stop_quick_review()
                    self.switch_screen('practice_levels')
                if current == 'translator':
                    tr = self.get_screen('translator')
                    if tr.braille_input_active:
                        tr.close_braille_input()
                        return True
                    self.switch_screen('menu')
                else:
                    self.switch_screen(back_map[current])
                return True

            if current == 'menu':
                return False

        return False


if __name__ == '__main__':
    BrailleApp().run()
