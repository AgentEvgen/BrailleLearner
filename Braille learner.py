from kivy.properties import StringProperty, DictProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from typing import Callable, Optional, Sequence, Tuple
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.gridlayout import GridLayout
from kivy.core.clipboard import Clipboard
from kivy.resources import resource_find
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.animation import Animation
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
import random
import json
import math
import time
import os

Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'resizable', '1')
font_path = resource_find("assets/DejaVuSans.ttf") or os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans.ttf")
LabelBase.register(name="BrailleFont", fn_regular=font_path)

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
                    text: root.training_title
                    on_press: app.switch_screen('lessons')
                BaseButton:
                    text: root.practice
                    on_press: app.switch_screen('practice_levels')
                BaseButton:
                    text: root.reference_title
                    on_press: app.switch_screen('reference')
                BaseButton:
                    text: root.translator_title
                    on_press: app.switch_screen('translator')
                BaseButton:
                    text: root.settings_title
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
            on_press: root.exit_to_practice_levels()

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
            on_press: root.exit_to_practice_levels()

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
                on_press: root.exit_to_practice_levels()

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

<MemoryCard>:
    font_size: dp(42)
    background_normal: ''
    background_disabled_normal: ''
    background_down: ''
    scale_x: 1

    canvas.before:
        PushMatrix
        Scale:
            origin: self.center
            x: self.scale_x

        Color:
            rgba:
                (0.20, 0.20, 0.20, 1) if self.face_down else (
                (0.20, 0.65, 0.20, 1) if self.is_matched else
                (0.30, 0.30, 0.30, 1))

        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

        Color:
            rgba: (0.35, 0.35, 0.35, 1) if self.face_down else (0.45, 0.45, 0.45, 1)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
            width: dp(1)

    canvas.after:
        PopMatrix

    color: (1, 1, 1, 1) if not self.face_down else (1, 1, 1, 0)
    on_press: root.on_card_click()

<MemoryGameScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(10)

        canvas.before:
            Color:
                rgba: 1, 1, 1, 0
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(50)

            Label:
                text: root.game_title
                font_size: dp(22)
                bold: True
                halign: 'left'
                size_hint_x: 0.6
                text_size: self.size
                valign: 'middle'
                color: (0.9, 0.9, 0.9, 1)

            Label:
                text: root.moves_label
                font_size: dp(18)
                halign: 'right'
                size_hint_x: 0.4
                text_size: self.size
                valign: 'middle'
                color: (0.7, 0.7, 0.7, 1)

        Widget:
            size_hint_y: None
            height: dp(2)
            canvas:
                Color:
                    rgba: 0.3, 0.3, 0.3, 1
                Rectangle:
                    pos: self.x, self.center_y
                    size: self.width, dp(1)

        GridLayout:
            id: memory_grid
            cols: 4
            spacing: dp(10)
            padding: [dp(5), dp(10)]

        BaseButton:
            text: root.back_btn
            size_hint_y: None
            height: dp(50)
            on_press: app.switch_screen('practice_levels')


<BrailleWordSearchScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(50)

            Label:
                text: root.title
                font_size: dp(22)
                bold: True
                halign: 'left'
                text_size: self.size
                valign: 'middle'
                size_hint_x: 0.65

            Label:
                text: root.status_text
                font_size: dp(16)
                halign: 'right'
                text_size: self.size
                valign: 'middle'
                size_hint_x: 0.35

        Widget:
            size_hint_y: None
            height: dp(2)
            canvas:
                Color:
                    rgba: 0.3, 0.3, 0.3, 1
                Rectangle:
                    pos: self.x, self.center_y
                    size: self.width, dp(1)


        GridLayout:
            id: ws_grid
            cols: root.grid_size
            spacing: dp(4)
            padding: [dp(8), dp(8)]
            size_hint_y: 0.65

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.30
            spacing: dp(6)
            padding: [dp(8), 0]

            Label:
                text: root.words_title
                font_size: dp(18)
                size_hint_y: None
                height: dp(24)
                halign: 'left'
                text_size: self.size
                valign: 'middle'

            ScrollView:
                bar_width: dp(6)
                do_scroll_x: False
                do_scroll_y: True
                size_hint_y: 1

                Label:
                    id: words_label
                    text: root.words_line
                    markup: True
                    font_size: dp(18)
                    size_hint_y: None
                    height: max(self.texture_size[1] + dp(12), dp(80))
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
                    color: (0.9, 0.9, 0.9, 1)

        BoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(8)

            BaseButton:
                text: root.new_game_btn
                height: dp(50)
                on_press: root.start_new_game()

            BaseButton:
                text: root.back_btn
                height: dp(50)
                on_press: app.switch_screen('practice_levels')


<SettingsSection@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(15)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 0.6
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15)]

<SettingsHeader@Label>:
    size_hint_y: None
    height: self.texture_size[1] + dp(10)
    font_size: dp(27)
    halign: 'center'
    valign: 'middle'
    bold: True
    color: 0.95, 0.95, 0.95, 1
    text_size: self.width, None


<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(10)

        Label:
            text: root.settings_title
            font_size: dp(28)
            bold: True
            size_hint_y: None
            height: dp(50)
            halign: 'center'
            valign: 'middle'

        ScrollView:
            bar_width: dp(6)
            bar_inactive_color: [0.6, 0.6, 0.6, 1]

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(20)

                SettingsSection:
                    SettingsHeader:
                        text: root.general_settings_header

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.language_label
                            size_hint_x: None
                            width: dp(100)
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Spinner:
                            id: lang_spinner
                            text: root.current_lang
                            values: root.languages.values()
                            size_hint_x: None
                            width: dp(150) if app.is_mobile else dp(200)
                            on_text: root.update_settings('language', self.text)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.use_stats
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: interval_switch
                            active: app.use_stats
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.update_update_use_stats(self.active)

                    BaseButton:
                        text: root.reset_stats_btn
                        height: dp(50)
                        on_press: root.reset_stats()

                SettingsSection:
                    SettingsHeader:
                        text: root.easy_mode_header

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.difficulty_label
                            size_hint_x: None
                            width: dp(100)
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Spinner:
                            id: difficulty_spinner
                            text: root.current_difficulty_str
                            values: root.difficulty_values
                            size_hint_x: None
                            width: dp(150) if app.is_mobile else dp(200)
                            on_text: root.update_settings('difficulty', self.text)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_letters
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: easy_letters_sw
                            active: app.easy_mode_letters
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_easy_letters(self.active)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_digits
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: easy_digits_sw
                            active: app.easy_mode_digits
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_easy_digits(self.active)

                SettingsSection:
                    SettingsHeader:
                        text: root.medium_mode_header

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.mirror_mode_label
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: mirror_switch
                            active: app.mirror_writing_mode
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.update_mirror_mode(self.active)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_letters
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: medium_letters_sw
                            active: app.medium_mode_letters
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_medium_letters(self.active)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_digits
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: medium_digits_sw
                            active: app.medium_mode_digits
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_medium_digits(self.active)

                SettingsSection:
                    SettingsHeader:
                        text: root.quick_review_header

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.time_label
                            size_hint_x: None
                            width: dp(150)
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        TextInput:
                            id: time_input
                            text: str(app.quick_review_time)
                            hint_text: root.time_hint
                            input_filter: 'int'
                            multiline: False
                            size_hint_x: None
                            width: dp(150) if app.is_mobile else dp(200)
                            padding: [dp(10), (self.height - self.line_height) / 2]
                            on_text: root.update_settings('time', self.text)

                SettingsSection:
                    SettingsHeader:
                        text: root.memory_game_title

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_letters
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: memo_letters_sw
                            active: app.memo_mode_letters
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_memo_letters(self.active)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_digits
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: memo_digits_sw
                            active: app.memo_mode_digits
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_memo_digits(self.active)

                Widget:
                    size_hint_y: None
                    height: dp(10)

        BaseButton:
            text: root.back_btn
            height: dp(50)
            on_press: app.switch_screen('menu')


<ReferenceRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(54) if root.is_header else dp(80)
    spacing: dp(0)

    canvas.before:
        Color:
            rgba: (0.2, 0.2, 0.2, 0.55) if root.is_header else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)] if root.is_header else [0]

    Label:
        text: root.symbol
        font_size: dp(26) if root.is_header else dp(56)
        bold: root.is_header
        size_hint_x: 1 if root.is_header else 0.25
        halign: 'center'
        valign: 'middle'
        text_size: self.size
        color: (0.95, 0.95, 0.95, 1)

    Label:
        text: root.stats if not root.is_header else ''
        font_size: dp(18)
        size_hint_x: 0 if root.is_header else 0.5
        opacity: 0 if root.is_header else 1
        halign: 'center'
        valign: 'middle'
        text_size: self.size
        color: (0.75, 0.75, 0.75, 1)

    Label:
        text: root.braille
        font_name: 'BrailleFont'
        font_size: dp(56)
        size_hint_x: 0 if root.is_header else 0.25
        opacity: 0 if root.is_header else 1
        halign: 'center'
        valign: 'middle'
        text_size: self.size
        color: (1, 1, 1, 1)

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
            text_size: self.width, None

        RecycleView:
            id: rv
            bar_width: dp(10)
            scroll_type: ['bars', 'content']
            do_scroll_x: False
            viewclass: 'ReferenceRow'

            RecycleBoxLayout:
                default_size: None, dp(80)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(10)
                padding: dp(5), dp(10), dp(5), dp(10)

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
                padding: [dp(10), dp(10)]
                spacing: dp(20)

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(15)
                    spacing: dp(15)

                    canvas.before:
                        Color:
                            rgba: 0.2, 0.2, 0.2, 0.6
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(15)]

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

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(15)
                    spacing: dp(15)

                    canvas.before:
                        Color:
                            rgba: 0.2, 0.2, 0.2, 0.6
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(15)]
                    Label:
                        size_hint_y: None
                        height: self.texture_size[1] + dp(10)
                        font_size: dp(27)
                        halign: 'center'
                        valign: 'middle'
                        bold: True
                        color: 0.95, 0.95, 0.95, 1
                        text_size: self.width, None
                        text: root.games

                    BaseButton:
                        text: root.memory_game_title
                        on_press: app.switch_screen('memory_game')
                    BaseButton:
                        text: root.word_search_title
                        on_press: app.switch_screen('word_search')

        BaseButton:
            text: root.back_btn
            size_hint_y: None
            height: dp(50)
            on_press: app.switch_screen('menu')
''')

braille_data = {
    'en': {
        'A': [1, 0, 0, 0, 0, 0], 'B': [1, 1, 0, 0, 0, 0], 'C': [1, 0, 0, 1, 0, 0],
        'D': [1, 0, 0, 1, 1, 0], 'E': [1, 0, 0, 0, 1, 0], 'F': [1, 1, 0, 1, 0, 0],
        'G': [1, 1, 0, 1, 1, 0], 'H': [1, 1, 0, 0, 1, 0], 'I': [0, 1, 0, 1, 0, 0],
        'J': [0, 1, 0, 1, 1, 0], 'K': [1, 0, 1, 0, 0, 0], 'L': [1, 1, 1, 0, 0, 0],
        'M': [1, 0, 1, 1, 0, 0], 'N': [1, 0, 1, 1, 1, 0], 'O': [1, 0, 1, 0, 1, 0],
        'P': [1, 1, 1, 1, 0, 0], 'Q': [1, 1, 1, 1, 1, 0], 'R': [1, 1, 1, 0, 1, 0],
        'S': [0, 1, 1, 1, 0, 0], 'T': [0, 1, 1, 1, 1, 0], 'U': [1, 0, 1, 0, 0, 1],
        'V': [1, 1, 1, 0, 0, 1], 'W': [0, 1, 0, 1, 1, 1], 'X': [1, 0, 1, 1, 0, 1],
        'Y': [1, 0, 1, 1, 1, 1], 'Z': [1, 0, 1, 0, 1, 1]
    },
    'ru': {
        'А': [1, 0, 0, 0, 0, 0], 'Б': [1, 1, 0, 0, 0, 0], 'В': [0, 1, 0, 1, 1, 1],
        'Г': [1, 1, 0, 1, 1, 0], 'Д': [1, 0, 0, 1, 1, 0], 'Е': [1, 0, 0, 0, 1, 0],
        'Ё': [1, 0, 0, 0, 0, 1], 'Ж': [0, 1, 0, 1, 1, 0], 'З': [1, 0, 1, 0, 1, 1],
        'И': [0, 1, 0, 1, 0, 0], 'Й': [1, 1, 1, 1, 0, 1], 'К': [1, 0, 1, 0, 0, 0],
        'Л': [1, 1, 1, 0, 0, 0], 'М': [1, 0, 1, 1, 0, 0], 'Н': [1, 0, 1, 1, 1, 0],
        'О': [1, 0, 1, 0, 1, 0], 'П': [1, 1, 1, 1, 0, 0], 'Р': [1, 1, 1, 0, 1, 0],
        'С': [0, 1, 1, 1, 0, 0], 'Т': [0, 1, 1, 1, 1, 0], 'У': [1, 0, 1, 0, 0, 1],
        'Ф': [1, 1, 0, 1, 0, 0], 'Х': [1, 1, 0, 0, 1, 0], 'Ц': [1, 0, 0, 1, 0, 0],
        'Ч': [1, 1, 1, 1, 1, 0], 'Ш': [1, 0, 0, 0, 1, 1], 'Щ': [1, 0, 1, 1, 0, 1],
        'Ъ': [1, 1, 1, 0, 1, 1], 'Ы': [0, 1, 1, 1, 0, 1], 'Ь': [0, 1, 1, 1, 1, 1],
        'Э': [0, 1, 0, 1, 0, 1], 'Ю': [1, 1, 0, 0, 1, 1], 'Я': [1, 1, 0, 1, 0, 1]
    },
    'dru': {
        'А': [1, 0, 0, 0, 0, 0], 'Б': [1, 1, 0, 0, 0, 0], 'В': [0, 1, 0, 1, 1, 1],
        'Г': [1, 1, 0, 1, 1, 0], 'Д': [1, 0, 0, 1, 1, 0], 'Е': [1, 0, 0, 0, 1, 0],
        'Ж': [0, 1, 0, 1, 1, 0], 'И': [0, 1, 0, 1, 0, 0], 'I': [1, 0, 1, 1, 1, 1],
        'К': [1, 0, 1, 0, 0, 0], 'Л': [1, 1, 1, 0, 0, 0], 'М': [1, 0, 1, 1, 0, 0],
        'Н': [1, 0, 1, 1, 1, 0], 'О': [1, 0, 1, 0, 1, 0], 'П': [1, 1, 1, 1, 0, 0],
        'Р': [1, 1, 1, 0, 1, 0], 'С': [0, 1, 1, 1, 0, 0], 'Т': [0, 1, 1, 1, 1, 0],
        'У': [1, 0, 1, 0, 0, 1], 'Ф': [1, 1, 0, 1, 0, 0], 'Х': [1, 1, 0, 0, 1, 0],
        'Ц': [1, 0, 0, 1, 0, 0], 'Ч': [1, 1, 1, 1, 1, 0], 'Ш': [1, 0, 0, 0, 1, 1],
        'Щ': [1, 0, 1, 1, 0, 1], 'Ъ': [1, 1, 1, 0, 1, 1], 'Ѣ': [0, 0, 1, 1, 1, 0],
        'Ы': [0, 1, 1, 1, 0, 1], 'Ь': [0, 1, 1, 1, 1, 1], 'Э': [0, 1, 0, 1, 0, 1],
        'Ю': [1, 1, 0, 0, 1, 1], 'Я': [1, 1, 0, 1, 0, 1], 'Ѳ': [1, 1, 1, 0, 0, 1],
        'Ѵ': [1, 0, 1, 0, 1, 1]
    }
}

number_sign_dots = [0, 0, 1, 1, 1, 1]  # ⠼
digits_data = {
    '1': [1, 0, 0, 0, 0, 0], '2': [1, 1, 0, 0, 0, 0], '3': [1, 0, 0, 1, 0, 0],
    '4': [1, 0, 0, 1, 1, 0], '5': [1, 0, 0, 0, 1, 0], '6': [1, 1, 0, 1, 0, 0],
    '7': [1, 1, 0, 1, 1, 0], '8': [1, 1, 0, 0, 1, 0], '9': [0, 1, 0, 1, 0, 0],
    '0': [0, 1, 0, 1, 1, 0]}

translations = {
    'en': {
        'menu_title': 'Main Menu', 'practice': 'Practice',
        'settings_title': 'Settings', 'language_label': 'Language:', 'back_btn': 'Back',
        'streak': 'Current streak: {}\nRecord: {}', 'reference_title': 'Reference',
        'difficulty_label': 'Difficulty:', 'difficulty_2': '2 options', 'difficulty_4': '4 options',
        'difficulty_6': '6 options', 'difficulty_8': '8 options', 'difficulty_10': '10 options',
        'translator_title': 'Translator', 'input_hint': 'Enter text here', 'translate_btn': 'Translate',
        'training_title': 'Training',
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
        'lessons_title': 'Lessons', 'lesson': 'Lesson', 'letters_label': 'Letters: {}', 'start': 'Start',
        'continue': 'Continue', 'locked': 'Locked', 'complete_lesson': 'Complete lesson',
        'view_all_letters': 'View all letters', 'lesson_test_title': 'Lesson Test',
        'question': 'Question {}/{}', 'test_passed': 'Test passed!', 'test_failed': 'Test failed',
        'ok': 'OK', 'completed': 'Completed', 'available': 'Available',
        'memory_game_title': 'MEMO',
        'moves_label': 'Moves: {}',
        'play_again': 'Play Again',
        'exit_menu': 'Menu',
        'you_won': 'You Won!',
        'word_search_title': 'Word Search',
        'word_search_words_title': 'Find words:',
        'word_search_new_game': 'New Game',
        'word_search_status': 'Found: {}/{}',
        'word_search_win_text': 'All words found.',
        'games': 'Games',

    },
    'ru': {
        'menu_title': 'Главное меню', 'practice': 'Практика',
        'settings_title': 'Настройки', 'language_label': 'Язык:', 'back_btn': 'Назад',
        'streak': 'Текущая серия: {}\nРекорд: {}', 'reference_title': 'Справочник',
        'difficulty_label': 'Сложность:', 'difficulty_2': '2 варианта', 'difficulty_4': '4 варианта',
        'difficulty_6': '6 вариантов', 'difficulty_8': '8 вариантов', 'difficulty_10': '10 вариантов',
        'translator_title': 'Переводчик', 'input_hint': 'Введите текст', 'translate_btn': 'Перевести',
        'training_title': 'Обучение',
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
        'lessons_title': 'Уроки', 'lesson': 'Урок', 'letters_label': 'Буквы: {}', 'start': 'Начать',
        'continue': 'Продолжить', 'locked': 'Заблокировано', 'complete_lesson': 'Завершить урок',
        'view_all_letters': 'Просмотрите все буквы', 'lesson_test_title': 'Тест по уроку',
        'question': 'Вопрос {}/{}', 'test_passed': 'Тест пройден!', 'test_failed': 'Тест не пройден',
        'ok': 'Ок', 'completed': 'Пройдено', 'available': 'Доступно',
        'memory_game_title': 'МЕМО',
        'moves_label': 'Ходы: {}',
        'play_again': 'Играть снова',
        'exit_menu': 'Меню',
        'you_won': 'Победа!',
        'word_search_title': 'Филворд',
        'word_search_words_title': 'Найди слова:',
        'word_search_new_game': 'Новая игра',
        'word_search_status': 'Найдено: {}/{}',
        'word_search_win_text': 'Все слова найдены.',
        'games': 'Игры',
    },
    'dru': {
        'menu_title': 'Главное меню', 'practice': 'Практика',
        'settings_title': 'Настройки', 'language_label': 'Языкъ:', 'back_btn': 'Назадъ',
        'streak': 'Текущая серія: {}\nРекордъ: {}', 'reference_title': 'Справочникъ',
        'difficulty_label': 'Сложность:', 'difficulty_2': '2 варіанта', 'difficulty_4': '4 варіанта',
        'difficulty_6': '6 варіантовъ', 'difficulty_8': '8 варіантовъ', 'difficulty_10': '10 варіантовъ',
        'translator_title': 'Переводчикъ', 'input_hint': 'Введите текстъ', 'translate_btn': 'Перевести',
        'training_title': 'Обученіе',
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
        'lessons_title': 'Уроки', 'lesson': 'Урокъ', 'letters_label': 'Буквы: {}', 'start': 'Начать',
        'continue': 'Продолжить', 'locked': 'Заблокировано', 'complete_lesson': 'Завершить урокъ',
        'view_all_letters': 'Просмотрите всё буквы', 'lesson_test_title': 'Тестъ по уроку',
        'question': 'Вопросъ {}/{}', 'test_passed': 'Тестъ пройденъ!', 'test_failed': 'Тестъ не пройденъ',
        'ok': 'Окъ', 'completed': 'Пройдено', 'available': 'Доступно',
        'memory_game_title': 'МЕМО',
        'moves_label': 'Ходы: {}',
        'play_again': 'Играть снова',
        'exit_menu': 'Меню',
        'you_won': 'Побѣда!',
        'word_search_title': 'Филвордъ',
        'word_search_words_title': 'Найди слова:',
        'word_search_new_game': 'Новая игра',
        'word_search_status': 'Найдено: {}/{}',
        'word_search_win_text': 'Всѣ слова найдены.',
        'games': 'Игры',
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

    def animate_correct(self, widget):
        Animation(opacity=0.6, duration=0.06) + Animation(opacity=1, duration=0.10)

    def animate_wrong(self, widget):
        anim = Animation(x=widget.x - dp(10), duration=0.05) + \
               Animation(x=widget.x + dp(20), duration=0.08) + \
               Animation(x=widget.x - dp(15), duration=0.06) + \
               Animation(x=widget.x, duration=0.05)
        anim.start(widget)

    def get_braille_char(self, dots):
        code = 0x2800
        if dots[0]: code |= 0x01
        if dots[1]: code |= 0x02
        if dots[2]: code |= 0x04
        if dots[3]: code |= 0x08
        if dots[4]: code |= 0x10
        if dots[5]: code |= 0x20
        return chr(code)

    def update_streak_text(self,  score_key: str, local_streak_attr: str = "current_streak", streak_prop: str = "streak_text",) -> None:
        lang = self.app.current_language

        is_quick = bool(getattr(self, "quick_review_mode", False))
        current_value = self.app.quick_streak if is_quick else int(getattr(self, local_streak_attr, 0))

        record_key = "quick" if is_quick else score_key
        record_value = int(self.app.high_scores.get(lang, {}).get(record_key, 0))

        setattr(self, streak_prop, self.get_translation("streak").format(current_value, record_value))

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

        lang = self.app.current_language
        stats_lang = self.app.stats.setdefault(lang, {})

        if char not in stats_lang:
            stats_lang[char] = {
                'correct': 0, 'wrong': 0, 'last_seen': 0,
                'interval': 0, 'ef': 2.5, 'reps': 0
            }
            self.app.save_stats()

        stat = stats_lang[char]

        last_seen = stat.get('last_seen', 0)
        interval = stat.get('interval', 0)

        if interval == 0 or last_seen == 0:
            return 10.0

        days_passed = (current_time - last_seen) / 86400.0
        ratio = days_passed / interval
        weight = 1.0 + (ratio ** 2) * 5.0
        return min(weight, 100.0)

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

    def show_popup( self, title: str, text: str = "", *, size=(dp(320), dp(240)), auto_dismiss: bool = False,
        buttons: Sequence[Tuple[str, Optional[Callable[[], None]]]] = (), font_size=dp(20),
        padding=dp(20), spacing=dp(12), buttons_height=dp(50), buttons_spacing=dp(10),  text_width: Optional[float] = None) -> Popup:

        root = BoxLayout(orientation="vertical", padding=padding, spacing=spacing)

        lbl = Label(
            text=text,
            font_size=font_size,
            halign="center",
            valign="middle",
            size_hint_y=1)

        def _sync(*_):
            w = lbl.width if text_width is None else text_width
            lbl.text_size = (w, None)
        lbl.bind(size=_sync, text=_sync)
        _sync()

        root.add_widget(lbl)

        popup = Popup(
            title=title,
            content=root,
            size_hint=(None, None),
            size=size,
            auto_dismiss=auto_dismiss,)

        if buttons:
            row = BoxLayout(size_hint_y=None, height=buttons_height, spacing=buttons_spacing)

            def handler(cb):
                def _(*_):
                    popup.dismiss()
                    if cb:
                        cb()
                return _

            for caption, cb in buttons:
                b = Button(text=caption)
                b.bind(on_press=handler(cb))
                row.add_widget(b)

            root.add_widget(row)

        popup.open()
        return popup

    def disable_children(self, widget):
        for ch in widget.children:
            ch.disabled = True
            ch.disabled_color = (1, 1, 1, 1)

    def show_win_popup(self, text, on_again):
        return self.show_popup(
            title=self.get_translation("you_won"),
            text=text,
            buttons=[
                (self.get_translation("play_again"), on_again),
                (self.get_translation("exit_menu"), lambda: self.app.switch_screen("practice_levels")),
            ],
            auto_dismiss=False,
        )

    def exit_to_practice_levels(self):
        self.app.stop_quick_review()
        self.quick_review_mode = False
        self.app.switch_screen("practice_levels")

    def schedule_once(self, callback, delay):
        event = Clock.schedule_once(callback, delay)
        self.scheduled_events.append(event)
        return event


class MenuScreen(BaseScreen):
    menu_title = StringProperty()
    training_title = StringProperty()
    practice = StringProperty()
    reference_title = StringProperty()
    translator_title = StringProperty()
    settings_title = StringProperty()

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

        self.training_title = self.get_translation('training_title')
        self.practice = self.get_translation('practice')
        self.reference_title = self.get_translation('reference_title')
        self.translator_title = self.get_translation('translator_title')
        self.settings_title = self.get_translation('settings_title')


class LessonsScreen(BaseScreen):
    lessons_title = StringProperty()
    current_mode = StringProperty('letters')
    letters_tab_text = StringProperty()
    digits_tab_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built_key = None

    def update_lang(self):
        super().update_lang()
        self.lessons_title = self.get_translation('lessons_title')
        self.letters_tab_text = self.get_translation('section_letters')
        self.digits_tab_text = self.get_translation('section_digits')

    def on_pre_enter(self, *args):
        self.update_lang()
        self.refresh_lessons(force=False)
        self.start_pulse_animation()

    def switch_mode(self, mode):
        self.current_mode = mode
        self.refresh_lessons(force=True)
        self.start_pulse_animation()

    def _progress_completed(self):
        app = self.app
        if self.current_mode == 'digits':
            return app.lessons_progress.get('digits_common', {}).get('completed_count', 0)
        return app.lessons_progress.get(app.current_language, {}).get('completed_count', 0)

    def _calc_built_key(self):
        app = self.app
        lang = app.current_language
        completed = self._progress_completed()
        lessons_len = len(app.get_lessons(lang, self.current_mode))
        return (lang, self.current_mode, completed, lessons_len)

    def refresh_lessons(self, force: bool = False):
        key = self._calc_built_key()
        if (not force) and self._built_key == key:
            return
        self._built_key = key
        self.populate_lessons()

    def start_pulse_animation(self):
        if hasattr(self, '_pulse_anim'):
            self._pulse_anim.cancel_all(self)

        container = self.ids.lessons_container
        target_btn = None

        for row in container.children:
            for child in row.children:
                if isinstance(child, BoxLayout):
                    btn = child.children[1]
                    if not btn.disabled and btn.text == self.get_translation('start'):
                        target_btn = btn
                        break

        if target_btn:
            self._pulse_anim = Animation(opacity=0.2, duration=0.5, t='in_out_quad') + \
                               Animation(opacity=1.2, duration=0.5, t='in_out_quad')
            self._pulse_anim.repeat = True
            self._pulse_anim.start(target_btn)

    def populate_lessons(self):
        container = self.ids.lessons_container
        container.clear_widgets()
        app = self.app
        lang = app.current_language

        lessons = app.get_lessons(lang, self.current_mode)
        completed = self._progress_completed()

        for idx, lesson in enumerate(lessons, start=1):
            is_completed = idx <= completed
            is_unlocked = idx <= completed + 1

            row = BoxLayout(orientation='vertical', size_hint_y=None,
                            padding=[dp(12), dp(8)], spacing=dp(4))

            with row.canvas.before:
                Color(0.2, 0.2, 0.2, 1)
                row.rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(10)])

            row.bind(pos=lambda inst, val: setattr(inst.rect, 'pos', val),
                     size=lambda inst, val: setattr(inst.rect, 'size', val))

            row.bind(minimum_height=row.setter('height'))

            mode = lesson['mode']
            if mode == 'study':
                mode_title = self.get_translation('training_title')
            elif mode == 'practice':
                mode_title = self.get_translation('practice')
            else:
                mode_title = self.get_translation('Test')

            title = f"{self.get_translation('lesson')} {idx}: {mode_title}"

            title_label = Label(
                text=title,
                size_hint_y=None,
                height=dp(26),
                font_size=dp(17),
                halign='left',
                valign='middle',
                bold=True
            )
            title_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            title_label.bind(texture_size=lambda inst, ts: setattr(inst, 'height', max(dp(26), ts[1])))
            row.add_widget(title_label)

            letters_text = self.get_translation('letters_label').format(' '.join(lesson['letters']))
            letters_label = Label(
                text=letters_text,
                size_hint_y=None,
                height=dp(20),
                font_size=dp(14),
                halign='left',
                valign='top',
                color=(0.75, 0.75, 0.75, 1)
            )
            letters_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            letters_label.bind(texture_size=lambda inst, ts: setattr(inst, 'height', max(dp(20), ts[1])))
            row.add_widget(letters_label)

            btn_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))

            btn = Button(
                text=self.get_translation('continue') if is_completed else self.get_translation('start'),
                size_hint_x=0.5,
                font_size=dp(15)
            )
            btn.disabled = not is_unlocked
            btn.bind(on_press=lambda inst, i=idx - 1: self.open_lesson(i))
            btn_box.add_widget(btn)

            if is_completed:
                status_text = f"[color=33aa33]{self.get_translation('completed')}[/color]"
            elif is_unlocked:
                status_text = f"[color=3333aa]{self.get_translation('available')}[/color]"
            else:
                status_text = f"[color=aa3333]{self.get_translation('locked')}[/color]"

            status_label = Label(
                text=status_text,
                markup=True,
                size_hint_x=0.5,
                halign='right',
                valign='middle',
                font_size=dp(14)
            )
            status_label.bind(size=status_label.setter('text_size'))

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

    def on_leave(self, *args):
        if hasattr(self, '_pulse_anim'):
            self._pulse_anim.cancel_all(self)


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
        mode_title = self.get_translation('training_title')
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
        self.disable_children(self.ids.answers_grid)

        if instance.answer_char == correct_char:
            instance.background_color = (0, 1, 0, 1)
            self.correct += 1
            self.app.update_char_stat(correct_char, True)
        else:
            instance.background_color = (1, 0, 0, 1)
            self.animate_wrong(instance)
            if self.correct_button:
                self.correct_button.background_color = (0, 1, 0, 1)
            self.app.update_char_stat(correct_char, False)

        self.schedule_once(self.next_question, 0.8)

    def finish_test(self):
        required_ratio = 0.9
        passed = self.correct >= math.ceil(required_ratio * self.questions_total)

        if passed:
            self.app.mark_lesson_completed(self.app.current_language, self.lesson_index, self.lesson_type)

        title = self.get_translation('test_passed') if passed else self.get_translation('test_failed')
        percent = int(self.correct / self.questions_total * 100)
        msg = f"{self.correct}/{self.questions_total} ({percent}%)"

        self.show_popup(
            title=title,
            text=msg,
            size=(dp(320), dp(200)),
            auto_dismiss=False,
            buttons=[(self.get_translation("ok"), lambda: self.app.switch_screen("lessons"))],
        )


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
        self._answer_buttons = []
        self._last_layout_key = None
        self._grid_bound = False
        super().__init__(**kwargs)
        self.bind(on_pre_enter=self.on_pre_enter)
        self.bind(on_leave=self.on_leave)

    def handle_timeout(self):
        self.timer_active = False
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        self._set_answer_buttons_enabled(False)

        if self.correct_button:
            self.correct_button.background_color = (0, 1, 0, 1)

        if self.current_symbol:
            self.app.update_char_stat(self.current_symbol, False)

        if self.quick_review_mode:
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text(score_key="practice")
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
        else:
            self.current_streak = 0
            self.update_streak_text(score_key="practice")
            self.schedule_once(lambda dt: self.reset_interface(reset_streak=False), 1.2)

    def _update_grid(self, *args):
        grid = self.ids.answers_grid
        self._ensure_answer_buttons()

        pool = []
        if self.app.easy_mode_letters:
            pool.extend(braille_data[self.app.current_language].keys())
        if self.app.easy_mode_digits:
            pool.extend(digits_data.keys())
        if not pool:
            pool = list(braille_data[self.app.current_language].keys())

        if not self.current_symbol:
            return

        k = int(self.app.current_difficulty)
        answers = [self.current_symbol]
        while len(answers) < k:
            d = random.choice(pool)
            if d not in answers:
                answers.append(d)
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

        final_row_height = max(dp(50), min(best_row_height, dp(110)))

        layout_key = (grid.width, grid.height, num_options, best_cols, final_row_height)
        if layout_key != self._last_layout_key:
            self._last_layout_key = layout_key
            grid.cols = best_cols
            grid.padding = [horizontal_padding, 0, horizontal_padding, 0]
            grid.spacing = spacing
            grid.row_default_height = final_row_height
            grid.row_force_default = True

        ns = self.get_braille_char(number_sign_dots)

        self.correct_button = None
        for i, btn in enumerate(self._answer_buttons):
            if i < num_options:
                ans = answers[i]
                btn.opacity = 1
                btn.disabled = False
                btn.height = final_row_height
                btn.answer_char = ans
                btn.background_color = (1, 1, 1, 1)

                if self.invert_mode:
                    if ans in digits_data:
                        btn.text = ns + self.get_braille_char(digits_data[ans])
                    else:
                        btn.text = self.get_braille_char(braille_data[self.app.current_language][ans])
                    btn.font_name = 'BrailleFont'
                    btn.font_size = min(dp(38), final_row_height * 0.55)
                else:
                    btn.text = ans
                    btn.font_name = 'Roboto'
                    btn.font_size = min(dp(24), final_row_height * 0.4)

                if ans == self.current_symbol:
                    self.correct_button = btn
            else:
                btn.answer_char = None
                btn.text = ""
                btn.disabled = True
                btn.opacity = 0
                btn.height = 0

    def _ensure_answer_buttons(self):
        grid = self.ids.answers_grid
        max_n = 10

        if len(self._answer_buttons) == max_n:
            return

        for _ in range(max_n):
            btn = Button(size_hint=(1, None), on_press=self.check_answer)
            btn.disabled_color = (1, 1, 1, 1)
            btn.background_disabled_normal = btn.background_normal
            btn.background_disabled_down = btn.background_down
            btn.answer_char = None
            grid.add_widget(btn)
            self._answer_buttons.append(btn)

    def on_pre_enter(self, *args):
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()
        self.update_lang()
        Clock.schedule_once(lambda dt: self.new_question(), 0)

    def on_kv_post(self, base_widget):
        self._ensure_answer_buttons()
        if not self._grid_bound:
            self.ids.answers_grid.bind(size=self._update_grid)
            self._grid_bound = True

    def on_leave(self, *args):
        super().on_leave(*args)

    def update_lang(self):
        super().update_lang()
        self.update_streak_text(score_key="practice")

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

        self._update_grid()

        if self.quick_review_mode:
            self.start_timer()

    def _set_answer_buttons_enabled(self, enabled: bool):
        for btn in self._answer_buttons:
            if btn.opacity == 0:
                continue
            btn.disabled = not enabled
            btn.disabled_color = (1, 1, 1, 1)

    def check_answer(self, instance):
        if self.timer_active:
            self.clock_event.cancel()
            self.timer_active = False

        self._set_answer_buttons_enabled(False)

        lang = self.app.current_language

        char = self.current_symbol
        chosen_char = getattr(instance, 'answer_char', instance.text)
        is_correct = (chosen_char == char)

        if is_correct:
            instance.background_color = (0, 1, 0, 1)
            self.animate_correct(instance)

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
        else:
            instance.background_color = (1, 0, 0, 1)
            self.animate_wrong(instance)
            if self.correct_button:
                self.correct_button.background_color = (0, 1, 0, 1)

            if self.quick_review_mode:
                self.app.quick_streak = max(0, self.app.quick_streak - 1)
            else:
                self.current_streak = 0

        self.app.update_char_stat(char, is_correct)

        self.update_streak_text(score_key="practice")

        delay = 0.5 if self.quick_review_mode else 0.8
        next_action = self.app.next_quick_step if self.quick_review_mode else lambda: self.reset_interface(
            chosen_char != char)
        self.schedule_once(lambda dt: next_action(), delay if chosen_char == char else delay + 0.4)

    def reset_interface(self, reset_streak=False):
        def _reset(_):
            self._set_answer_buttons_enabled(True)
            if reset_streak:
                self.current_streak = 0
                self.update_streak_text(score_key="practice")
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

        self.update_streak_text(score_key="medium_practice")
        self.new_question()

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

        if self.current_letter:
            self.app.update_char_stat(self.current_letter, False)

        if self.quick_review_mode:
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text(score_key="medium_practice")
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

        if self.quick_review_mode:
            self.start_timer()

    def on_dot_press(self, visual_index, instance):
        logical_index = self.get_logical_index(visual_index)

        self.user_input[logical_index] = 1 - self.user_input[logical_index]
        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[logical_index] else (1, 1, 1, 1)

    def show_hint(self):
        if self.hint_used or not self.current_letter:
            return

        self.hint_used = True
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

        is_correct = (self.user_input == self.current_dots)
        self._disable_and_show_correct_answer(self.user_input)

        lang = self.app.current_language

        if self.app.use_stats:
            stat_correct = is_correct and not self.hint_used
            self.app.update_char_stat(self.current_letter, stat_correct)

        if self.quick_review_mode:
            if is_correct and not self.hint_used:
                self.app.quick_streak += 1
                if self.app.quick_streak > self.app.high_scores[lang]['quick']:
                    self.app.high_scores[lang]['quick'] = self.app.quick_streak
                    self.app.save_high_scores()
            elif not is_correct:
                self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text(score_key="medium_practice")
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
            self.update_streak_text(score_key="medium_practice")
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
        self.update_streak_text(score_key="hard_practice")
        self.new_question()

    def update_lang(self):
        super().update_lang()
        self.no_errors_btn = self.get_translation('no_errors_btn')
        self.confirm_btn = self.get_translation('confirm_btn')

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
        self.update_streak_text(score_key="hard_practice")

        if self.has_error:
            self.app.update_char_stat(self.current_word[self.error_index], False)

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

    def handle_correct_answer(self):
        if self.quick_review_mode:
            self.app.quick_streak += 1
            if self.app.quick_streak > self.app.high_scores[self.app.current_language]['quick']:
                self.app.high_scores[self.app.current_language]['quick'] = self.app.quick_streak
                self.app.save_high_scores()
            self.update_streak_text(score_key="hard_practice")
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
            return

        self.current_streak += 1
        if self.current_streak > self.app.high_scores[self.app.current_language].get('hard_practice', 0):
            self.app.high_scores[self.app.current_language]['hard_practice'] = self.current_streak
            self.app.save_high_scores()
        self.update_streak_text(score_key="hard_practice")
        self.schedule_once(lambda dt: self.new_question(), 1.5)

    def handle_wrong_answer(self):
        if self.quick_review_mode:
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text(score_key="hard_practice")
            self.schedule_once(lambda dt: self.app.next_quick_step(), 2.0)
            return

        self.current_streak = 0
        self.update_streak_text(score_key="hard_practice")
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

        if self.has_error and self.error_index >= 0:
            self.app.update_char_stat(self.current_word[self.error_index], user_correct)

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
            self.disable_children(self.ids.braille_word_box)
            self.ids.no_error_btn.disabled = True
            self.ids.no_error_btn.disabled_color = (1, 1, 1, 1)

    def on_braille_char_press(self, instance):
        if self._controls_locked: return
        self.stop_timer()
        self.lock_controls()

        if self.has_error and instance.char_index == self.error_index:
            if self.sub_mode == 'A':
                instance.background_color = (0, 1, 0, 1)
                self.app.update_char_stat(self.current_word[self.error_index], True)
                self.handle_correct_answer()
            else:
                instance.background_color = (1, 0.7, 0, 1)
                self.correction_panel_visible = True
                self._controls_locked = False

        else:
            instance.background_color = (1, 0, 0, 1)
            if self.has_error:
                self.app.update_char_stat(self.current_word[self.error_index], False)
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
            self.app.update_char_stat(self.current_word[self.error_index], False)
            self.handle_wrong_answer()

    def on_correction_dot_press(self, index, instance):
        self.user_input[index] = 1 - self.user_input[index]
        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[index] else (1, 1, 1, 1)


class MemoryCard(Button):
    face_down = BooleanProperty(True)
    is_matched = BooleanProperty(False)
    content_text = StringProperty()
    is_braille = BooleanProperty(False)
    pair_id = StringProperty()
    scale_x = NumericProperty(1)

    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        self.disabled_color = (1, 1, 1, 1)
        self.background_normal = ''
        self.background_down = ''
        self.background_disabled_normal = ''
        self.background_disabled_down = ''
        self.background_color = (0, 0, 0, 0)

    def on_card_click(self):
        if not self.face_down or self.is_matched or self.screen.input_locked:
            return
        self.animate_flip(reveal=True)

    def animate_flip(self, reveal=True):
        anim = Animation(scale_x=0, duration=0.15, t='in_quad')

        def on_mid_flip(*args):
            if reveal:
                self.face_down = False
                self.text = self.content_text
                if self.is_braille:
                    self.font_name = 'BrailleFont'
                    self.font_size = dp(46)
                else:
                    self.font_name = 'Roboto'
                    self.font_size = dp(32)
            else:
                self.face_down = True
                self.text = ''

            anim_back = Animation(scale_x=1, duration=0.15, t='out_quad')
            anim_back.start(self)

            if reveal:
                self.screen.on_card_selected(self)

        anim.bind(on_complete=on_mid_flip)
        anim.start(self)

    def reveal(self):
        if self.face_down:
            self.animate_flip(reveal=True)

    def hide(self):
        if not self.face_down:
            self.animate_flip(reveal=False)

    def match_found(self):
        self.is_matched = True
        self.disabled = True


class MemoryGameScreen(BaseScreen):
    moves = NumericProperty(0)
    moves_label = StringProperty()
    game_title = StringProperty()

    def __init__(self, **kwargs):
        self.selected_cards = []
        super().__init__(**kwargs)
        self.input_locked = False
        self.pairs_count = 8

    def on_moves(self, instance, value):
        self.update_moves_text()

    def update_lang(self):
        super().update_lang()
        self.game_title = self.get_translation('memory_game_title')
        self.update_moves_text()

    def update_moves_text(self):
        fmt = self.get_translation('moves_label')
        if '{}' not in fmt:
            self.moves_label = f"{fmt}: {self.moves}"
        else:
            self.moves_label = fmt.format(self.moves)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.start_new_game()

    def start_new_game(self):
        self.input_locked = False
        self.selected_cards = []
        self.moves = 0

        grid = self.ids.memory_grid
        grid.clear_widgets()

        app = App.get_running_app()
        lang = app.current_language

        pool = []
        if app.memo_mode_letters:
            pool += list(braille_data[lang].keys())
        if app.memo_mode_digits:
            pool += list(digits_data.keys())

        if not pool:
            pool = list(braille_data[lang].keys())

        if len(pool) < self.pairs_count:
            chosen_chars = pool * (self.pairs_count // len(pool) + 1)
        else:
            chosen_chars = pool

        game_chars = random.sample(chosen_chars, self.pairs_count)

        cards_list = []

        for char in game_chars:
            card_text = MemoryCard(screen=self)
            card_text.content_text = char
            card_text.pair_id = char
            card_text.is_braille = False
            cards_list.append(card_text)

            card_braille = MemoryCard(screen=self)

            if char in digits_data:
                dots = digits_data[char]
                text_content = self.get_braille_char(number_sign_dots) + self.get_braille_char(dots)
            else:
                dots = braille_data[lang][char]
                text_content = self.get_braille_char(dots)

            card_braille.content_text = text_content
            card_braille.pair_id = char
            card_braille.is_braille = True
            cards_list.append(card_braille)

        random.shuffle(cards_list)
        for card in cards_list:
            grid.add_widget(card)

    def on_card_selected(self, card):
        if card not in self.selected_cards:
            self.selected_cards.append(card)

        if len(self.selected_cards) == 2:
            self.input_locked = True
            self.moves += 1

            card1 = self.selected_cards[0]
            card2 = self.selected_cards[1]

            if card1.pair_id == card2.pair_id:
                self.schedule_once(self.process_match, 0.5)
            else:
                self.schedule_once(self.reset_selection, 1.0)

    def process_match(self, dt):
        for card in self.selected_cards:
            card.match_found()

        self.selected_cards.clear()
        self.input_locked = False
        self.check_win()

    def reset_selection(self, dt):
        for card in self.selected_cards:
            card.hide()
        self.selected_cards.clear()
        self.input_locked = False

    def check_win(self):
        grid = self.ids.memory_grid
        if all(c.is_matched for c in grid.children):
            self.show_win_popup(self.moves_label, self.start_new_game)


class BrailleWordSearchScreen(BaseScreen):
    title = StringProperty()
    words_title = StringProperty()
    new_game_btn = StringProperty()
    status_text = StringProperty()
    grid_size = NumericProperty(8)
    words_line = StringProperty()

    def __init__(self, **kwargs):
        self.cells = []
        self.letters_grid = []
        self.target_words = []
        self.found_words = set()
        self._found_paths = []

        self._dragging = False
        self._selected_indices = []
        self._selected_set = set()

        self._dirs = [(0, 1), (1, 0)]
        super().__init__(**kwargs)

    def update_lang(self):
        super().update_lang()
        self.title = self.get_translation('word_search_title')
        self.words_title = self.get_translation('word_search_words_title')
        self.new_game_btn = self.get_translation('word_search_new_game')
        self._update_status()

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.load_braille_data()
        self.start_new_game()

    def start_new_game(self):
        self.found_words.clear()
        self._found_paths.clear()
        self._clear_selection()

        self.grid_size = 7
        self.target_words = self._pick_words()

        self.letters_grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self._place_words()
        self._fill_noise()

        self._build_grid_ui()
        self._build_words_ui()
        self._update_status()

    def _pick_words(self):
        lang = self.app.current_language
        wl = self.app.word_lists.get(lang) or []
        letters_set = set(self.braille_data.keys())

        candidates = [w for w in wl if 3 <= len(w) <= 6 and all(c in letters_set for c in w)]
        if len(candidates) < 8:
            items = list(letters_set)
            candidates = list({''.join(random.choice(items) for _ in range(random.choice([3, 4, 5, 6])))
                               for _ in range(60)})

        k = 6
        return random.sample(candidates, min(k, len(candidates)))

    def _place_words(self):
        for w in self.target_words:
            for _ in range(200):
                dr, dc = random.choice(self._dirs)
                r0 = random.randint(0, self.grid_size - 1)
                c0 = random.randint(0, self.grid_size - 1)

                r1 = r0 + dr * (len(w) - 1)
                c1 = c0 + dc * (len(w) - 1)
                if not (0 <= r1 < self.grid_size and 0 <= c1 < self.grid_size):
                    continue

                rr, cc = r0, c0
                if any(self.letters_grid[rr + dr * i][cc + dc * i] not in ('', ch) for i, ch in enumerate(w)):
                    continue

                for i, ch in enumerate(w):
                    self.letters_grid[r0 + dr * i][c0 + dc * i] = ch
                break

    def _fill_noise(self):
        pool = list(self.braille_data.keys())
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.letters_grid[r][c]:
                    self.letters_grid[r][c] = random.choice(pool)

    def _build_grid_ui(self):
        grid = self.ids.ws_grid
        grid.clear_widgets()
        grid.cols = int(self.grid_size)
        self.cells = []

        base = dp(58) if self.grid_size <= 6 else dp(52)

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                ch = self.letters_grid[r][c]
                dots = self.braille_data.get(ch)
                braille = self.get_braille_char(dots) if dots else '?'

                btn = Button(
                    text=braille,
                    font_name='BrailleFont',
                    font_size=base,
                    background_normal='',
                    background_down='',
                    background_color=(0.2, 0.2, 0.2, 1),
                    color=(1, 1, 1, 1),
                )
                btn.disabled_color = (1, 1, 1, 1)
                btn.background_disabled_normal = ''
                btn.background_disabled_down = ''
                btn.ws_index = r * self.grid_size + c
                btn.bind(on_touch_down=self._on_cell_touch_down,
                         on_touch_move=self._on_cell_touch_move,
                         on_touch_up=self._on_cell_touch_up)

                self.cells.append(btn)
                grid.add_widget(btn)

        self.schedule_once(lambda dt: self._autoscale_cells(), 0)

    def _autoscale_cells(self):
        for btn in self.cells:
            btn.font_size = max(dp(24), min(dp(72), btn.height * 0.85))

    def _build_words_ui(self):
        self._refresh_words_ui()

    def _refresh_words_ui(self):
        parts = []
        for w in self.target_words:
            if w in self.found_words:
                parts.append(f"[color=33aa33]{w}[/color]")
            else:
                parts.append(w)
        self.words_line = "  ".join(parts)

    def _update_status(self):
        fmt = self.get_translation('word_search_status')
        self.status_text = fmt.format(len(self.found_words), len(self.target_words))

    def _clear_selection(self):
        self._dragging = False
        self._selected_indices.clear()
        self._selected_set.clear()
        self._repaint()

    def _found_cells_set(self):
        s = set()
        for p in self._found_paths:
            s.update(p)
        return s

    def _repaint(self):
        found_cells = self._found_cells_set()

        base_bg = (0.2, 0.2, 0.2, 1)
        base_fg = (1, 1, 1, 1)

        selected_bg = (0.7, 0.7, 0.7, 1)
        selected_fg = (0, 0, 0, 1)

        found_bg = (0.2, 0.7, 0.2, 1)
        found_fg = (1, 1, 1, 1)

        for btn in self.cells:
            idx = btn.ws_index
            if idx in found_cells:
                btn.background_color, btn.color = found_bg, found_fg
            elif idx in self._selected_set:
                btn.background_color, btn.color = selected_bg, selected_fg
            else:
                btn.background_color, btn.color = base_bg, base_fg

    def _on_cell_touch_down(self, btn, touch):
        if not btn.collide_point(*touch.pos):
            return False
        self._dragging = True
        self._selected_indices.clear()
        self._selected_set.clear()
        self._add_to_selection(btn.ws_index)
        self._repaint()
        touch.grab(btn)
        return True

    def _on_cell_touch_move(self, btn, touch):
        if touch.grab_current is not btn or not self._dragging:
            return False
        for b in self.cells:
            if b.collide_point(*touch.pos):
                self._add_to_selection(b.ws_index)
                break
        self._repaint()
        return True

    def _on_cell_touch_up(self, btn, touch):
        if touch.grab_current is not btn:
            return False
        touch.ungrab(btn)
        if self._dragging:
            self._dragging = False
            self._finalize_selection()
        return True

    def _add_to_selection(self, idx):
        if idx in self._selected_set:
            return

        if self._selected_indices:
            last = self._selected_indices[-1]
            lr, lc = divmod(last, self.grid_size)
            cr, cc = divmod(idx, self.grid_size)
            if abs(cr - lr) + abs(cc - lc) != 1:
                return

        if len(self._selected_indices) >= 2:
            a = self._selected_indices[0]
            ar, ac = divmod(a, self.grid_size)
            cr, cc = divmod(idx, self.grid_size)
            if not (cr == ar or cc == ac):
                return

        self._selected_indices.append(idx)
        self._selected_set.add(idx)

    def _finalize_selection(self):
        if len(self._selected_indices) < 3:
            self._clear_selection()
            return

        letters = [self.letters_grid[r][c] for (r, c) in (divmod(i, self.grid_size) for i in self._selected_indices)]
        s = ''.join(letters)
        s_rev = s[::-1]

        matched = next((w for w in self.target_words if w == s or w == s_rev), None)
        if matched and matched not in self.found_words:
            self.found_words.add(matched)
            self._found_paths.append(list(self._selected_indices))
            self._refresh_words_ui()
            self._update_status()

            if len(self.found_words) == len(self.target_words):
                self.show_win_popup(self.get_translation("word_search_win_text"), self.start_new_game)

        self._clear_selection()


class PracticeLevelsScreen(BaseScreen):
    title = StringProperty()
    easy_level_btn = StringProperty()
    medium_level_btn = StringProperty()
    hard_level_btn = StringProperty()
    quick_review_btn = StringProperty()
    memory_game_title = StringProperty()
    word_search_title = StringProperty()
    games = StringProperty()

    def update_lang(self):
        super().update_lang()
        self.title = self.get_translation('practice_levels_title')
        self.easy_level_btn = self.get_translation('easy_level')
        self.medium_level_btn = self.get_translation('medium_level')
        self.hard_level_btn = self.get_translation('hard_level')
        self.games = self.get_translation('games')
        self.memory_game_title = self.get_translation('memory_game_title')
        self.word_search_title = self.get_translation('word_search_title')
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
    memory_game_title = StringProperty()

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
        self.memory_game_title = self.get_translation('memory_game_title')
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

    def toggle_mode_flag(self, attr: str, value: bool, other_attr: str, other_switch_id: str):
        setattr(self.app, attr, value)
        if not value and not getattr(self.app, other_attr):
            setattr(self.app, other_attr, True)
            Clock.schedule_once(lambda dt: setattr(self.ids[other_switch_id], "active", True))
        self.app.save_settings()

    def toggle_easy_letters(self, v):
        self.toggle_mode_flag("easy_mode_letters", v, "easy_mode_digits", "easy_digits_sw")

    def toggle_easy_digits(self, v):
        self.toggle_mode_flag("easy_mode_digits", v, "easy_mode_letters", "easy_letters_sw")

    def toggle_medium_letters(self, v):
        self.toggle_mode_flag("medium_mode_letters", v, "medium_mode_digits", "medium_digits_sw")

    def toggle_medium_digits(self, v):
        self.toggle_mode_flag("medium_mode_digits", v, "medium_mode_letters", "medium_letters_sw")

    def toggle_memo_letters(self, v):
        self.toggle_mode_flag("memo_mode_letters", v, "memo_mode_digits", "memo_digits_sw")

    def toggle_memo_digits(self, v):
        self.toggle_mode_flag("memo_mode_digits", v, "memo_mode_letters", "memo_letters_sw")

    def reset_stats(self):
        def do_reset():
            self.app.stats = {'en': {}, 'ru': {}, 'dru': {}}
            self.app.save_stats()

        self.show_popup(
            title=self.get_translation("reset_stats_title"),
            text=self.get_translation("reset_stats_text"),
            size=(dp(360), dp(260)),
            auto_dismiss=False,
            font_size=dp(18),
            text_width=dp(300),
            buttons=[
                (self.get_translation("yes"), do_reset),
                (self.get_translation("no"), None),
            ],
            buttons_height=dp(60),
            buttons_spacing=dp(20),
            padding=[dp(30), dp(20), dp(30), dp(20)],
            spacing=dp(20),
        )


class ReferenceRow(BoxLayout):
    symbol = StringProperty('')
    braille = StringProperty('')
    stats = StringProperty('')
    is_header = BooleanProperty(False)


class ReferenceScreen(BaseScreen):
    reference_title = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built_key = None

    def on_pre_enter(self, *args):
        self.app = App.get_running_app()
        self.update_lang()

        key = (self.app.current_language, bool(self.app.use_stats))
        if self._built_key != key:
            self._built_key = key
            self._build_rv_data()
        else:
            self._refresh_stats_in_rv()

    def update_lang(self):
        super().update_lang()
        self.reference_title = self.get_translation('reference_title')

    def _build_rv_data(self):
        lang = self.app.current_language
        letters_items = list(self.app.braille_data[lang].items())
        digits_items = list(digits_data.items())
        ns = self.get_braille_char(number_sign_dots)

        stats_fmt = self.get_translation('stats_label')

        data = []

        data.append({
            "is_header": True,
            "symbol": self.get_translation('section_letters'),
            "braille": "",
            "stats": "",
        })

        for ch, dots in letters_items:
            braille_char = self.get_braille_char(dots)

            if self.app.use_stats:
                st = self.app.stats[lang].get(ch, {"correct": 0, "wrong": 0})
                stats_text = stats_fmt.format(st["correct"], st["wrong"])
            else:
                stats_text = ""

            data.append({
                "viewclass": "ReferenceRow",
                "symbol": ch,
                "stats": stats_text,
                "braille": braille_char,
                "is_header": False,
            })

        data.append({
            "is_header": True,
            "symbol": self.get_translation('section_digits'),
            "braille": "",
            "stats": "",
        })

        for d, dots in digits_items:
            braille_char = ns + self.get_braille_char(dots)

            if self.app.use_stats:
                st = self.app.stats[lang].get(d, {"correct": 0, "wrong": 0})
                stats_text = stats_fmt.format(st["correct"], st["wrong"])
            else:
                stats_text = ""

            data.append({
                "viewclass": "ReferenceRow",
                "symbol": d,
                "stats": stats_text,
                "braille": braille_char,
                "is_header": False,
            })

        self.ids.rv.data = data

    def _refresh_stats_in_rv(self):
        if not self.app.use_stats:
            return

        lang = self.app.current_language
        fmt = self.get_translation('stats_label')

        data = self.ids.rv.data
        for row in data:
            if row.get("is_header"):
                continue
            key = row.get("symbol")
            st = self.app.stats[lang].get(key, {"correct": 0, "wrong": 0})
            row["stats"] = fmt.format(st["correct"], st["wrong"])

        self.ids.rv.refresh_from_data()


class TranslatorScreen(BaseScreen):
    translator_title = StringProperty()
    input_hint = StringProperty()
    input_braille_btn = StringProperty()
    confirm_btn = StringProperty()
    delete_btn = StringProperty()
    copy_btn = StringProperty()
    braille_input_active = BooleanProperty(False)
    user_braille_dots = ListProperty([0] * 6)
    dot_buttons = ListProperty([])
    _last_translated_text = StringProperty()
    full_braille_text = StringProperty()

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
    memo_mode_letters = BooleanProperty(True)
    memo_mode_digits = BooleanProperty(True)

    _screen_classes = {
        'menu': MenuScreen,
        'lessons': LessonsScreen,
        'lesson_study': LessonStudyScreen,
        'lesson_test': LessonTestScreen,
        'practice_levels': PracticeLevelsScreen,
        'practice': PracticeScreen,
        'medium_practice': MediumPracticeScreen,
        'hard_practice': HardPracticeScreen,
        'memory_game': MemoryGameScreen,
        'word_search': BrailleWordSearchScreen,
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
        sm = ScreenManager()
        self._load_screen(sm, 'menu')
        Clock.schedule_once(self._deferred_init, 0)

        return sm

    def _deferred_init(self, dt):
        self.load_lessons_progress()
        self.digits_lessons = self.build_lessons(list(digits_data.keys()), group_size=5)
        self.load_stats()
        self.load_word_list(self.current_language)
        Clock.schedule_once(self.prewarm_reference, 0)
        Clock.schedule_once(self.prewarm_lessons, 0)

    def prewarm_reference(self, dt):
        lang = self.current_language
        self._reference_cache = {
            "lang": lang,
            "letters": list(self.braille_data[lang].items()),
            "digits": list(digits_data.items()),
            "ns": chr(0x2800 | 0b111100),
        }

    def prewarm_lessons(self, dt):
        lang = self.current_language
        self.lessons_config.setdefault(lang, self.build_lessons(list(self.braille_data[lang].keys()), 4))
        if not hasattr(self, "digits_lessons") or not self.digits_lessons:
            self.digits_lessons = self.build_lessons(list(digits_data.keys()), 5)

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

        stat = self.stats[lang].setdefault(char, {
            'correct': 0, 'wrong': 0, 'last_seen': 0,
            'interval': 0, 'ef': 2.5, 'reps': 0
        })

        if is_correct:
            q = 5
        else:
            q = 0

        ef = stat.get('ef', 2.5)
        reps = stat.get('reps', 0)
        interval = stat.get('interval', 0)

        if q >= 3:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 6
            else:
                interval = math.ceil(interval * ef)
            reps += 1
        else:
            reps = 0
            interval = 1

        ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if ef < 1.3:
            ef = 1.3

        stat['interval'] = interval
        stat['ef'] = ef
        stat['reps'] = reps
        stat['last_seen'] = time.time()

        if is_correct:
            stat['correct'] += 1
        else:
            stat['wrong'] += 1

        self.save_stats()

    def build_lessons(self, items, group_size):
        lessons, learned = [], []
        for i in range(0, len(items), group_size):
            chunk = items[i:i + group_size]
            lessons += [{"mode": "study", "letters": chunk}]
            if i: lessons += [{"mode": "practice", "letters": chunk}]
            learned += chunk
            lessons += [{"mode": "practice", "letters": learned[:]}]
        lessons += [{"mode": "exam", "letters": items}]
        return lessons

    def get_lessons(self, lang, lesson_type='letters'):
        if lesson_type == 'digits':
            return self.digits_lessons
        if lang not in self.lessons_config:
            self.lessons_config[lang] = self.build_lessons(list(self.braille_data[lang].keys()), 5)
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

    def load_word_list(self, lang: str) -> None:
        path = resource_find(f"assets/words/{lang}.txt")

        if not path:
            self.word_lists[lang] = None
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                words = [line.strip().upper() for line in f if line.strip()]
            words = [w for w in words if all(c in braille_data[lang] for c in w)]
            self.word_lists[lang] = words if words else None
        except Exception as e:
            print(f"Error loading words for {lang} from {path}: {e}")
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
            self.memo_mode_letters = data.get('memo_mode_letters', True)
            self.memo_mode_digits = data.get('memo_mode_digits', True)
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
                'memo_mode_letters': self.memo_mode_letters,
                'memo_mode_digits': self.memo_mode_digits,
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
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        for lang in ("en", "ru", "dru"):
            data.setdefault(lang, {})

        self.stats = data

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
                'memory_game': 'practice_levels',
                'word_search': 'practice_levels',
                'reference': 'menu',
                'translator': 'menu',
                'settings': 'menu',
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
