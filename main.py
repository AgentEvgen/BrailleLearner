from kivy.properties import StringProperty, DictProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.bubble import Bubble, BubbleContent, BubbleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import Label as CoreLabel
from kivy.core.clipboard import Clipboard
from kivy.resources import resource_find
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.config import Config
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.app import App
from functools import lru_cache
import random
import json
import math
import time
import os

Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'resizable', '1')
font_path = resource_find("assets/Quivira-mod.ttf") or os.path.join(os.path.dirname(__file__), "assets",
                                                                    "Quivira-mod.ttf")
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
                    font_name: 'BrailleFont'
                    on_press: app.switch_screen('lessons')
                BaseButton:
                    text: root.practice
                    font_name: 'BrailleFont'
                    on_press: app.switch_screen('practice_levels')
                BaseButton:
                    text: root.reference_title
                    font_name: 'BrailleFont'
                    on_press: app.switch_screen('reference')
                BaseButton:
                    text: root.translator_title
                    font_name: 'BrailleFont'
                    on_press: app.switch_screen('translator')
                BaseButton:
                    text: root.settings_title
                    font_name: 'BrailleFont'
                    on_press: app.switch_screen('settings')
        Widget:
            size_hint_y: None
            height: dp(15)

<LessonRow>:
    orientation: 'vertical'
    size_hint_y: None
    height: root.row_height
    padding: [dp(12), dp(8), dp(12), dp(8)]
    spacing: dp(4)

    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

    Label:
        text: root.title
        size_hint_y: None
        height: dp(24)
        font_size: dp(17)
        font_name: 'BrailleFont'
        halign: 'left'
        valign: 'middle'
        bold: True
        text_size: self.width, None

    Label:
        text: root.letters_text
        size_hint_y: None
        height: root.letters_height
        font_size: dp(14)
        font_name: 'BrailleFont'
        halign: 'left'
        valign: 'top'
        color: (0.75, 0.75, 0.75, 1)
        text_size: self.width, self.height 

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)

        Button:
            text: root.btn_text
            size_hint_x: 0.5
            font_size: dp(15)
            font_name: 'BrailleFont'
            disabled: not root.is_unlocked
            on_press: app.get_screen('lessons').open_lesson(root.lesson_index)

        Label:
            text: root.status_markup
            font_name: 'BrailleFont'
            markup: True
            size_hint_x: 0.5
            halign: 'right'
            valign: 'middle'
            font_size: dp(14)
            font_name: 'BrailleFont'
            text_size: self.size

<LessonsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(10), dp(20)]
        spacing: dp(10)

        Label:
            text: root.lessons_title
            font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
                background_color: (1.5, 1.5, 1.5, 1) if root.current_mode == 'letters' else (1, 1, 1, 1)
                on_press: root.switch_mode('letters')

            Button:
                text: root.digits_tab_text
                font_name: 'BrailleFont'
                background_color: (1.5, 1.5, 1.5, 1) if root.current_mode == 'digits' else (1, 1, 1, 1)
                on_press: root.switch_mode('digits')

        RecycleView:
            id: lessons_rv
            bar_width: dp(8)
            viewclass: 'LessonRow'
            scroll_type: ['bars', 'content']
            do_scroll_x: False

            RecycleBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: [dp(10), dp(10)]
                default_size: None, dp(110)
                default_size_hint: 1, None

        BaseButton:
            text: root.back_btn
            font_name: 'BrailleFont'
            height: dp(50)
            on_press: app.switch_screen('menu')

<LessonStudyScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(12)

        Label:
            text: root.lesson_title
            font_size: dp(20)
            font_name: 'BrailleFont'
            size_hint_y: None
            height: dp(42)
            text_size: self.width, None
            halign: 'center'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.8

            BoxLayout:
                id: study_panel
                orientation: 'vertical'
                opacity: 1 if root.is_learning_active else 0
                disabled: not root.is_learning_active
                size_hint_y: None
                height: self.parent.height if root.is_learning_active else 0

                Label:
                    id: study_symbol
                    text: root.current_symbol
                    font_name: 'BrailleFont'
                    font_size: min(dp(72), self.height * 0.6) if self.height > 0 else dp(40)
                    size_hint_y: 0.35
                    halign: 'center'
                    valign: 'middle'
                    text_size: self.size

                FloatLayout:
                    size_hint_y: 0.65

                    GridLayout:
                        id: dots_grid
                        cols: 2
                        rows: 3
                        spacing: [dp(20), dp(20)]
                        padding: dp(10)
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        size_hint: None, None
                        width: self.minimum_width
                        height: self.minimum_height

                        Button:
                            id: d1
                            text: '*'
                            font_size: dp(24)
                            width: dp(70)
                            height: dp(70)
                            size_hint: None, None
                            on_press: root.on_dot_press(0)

                        Button:
                            id: d4
                            text: '*'
                            font_size: dp(24)
                            width: dp(70)
                            height: dp(70)
                            size_hint: None, None
                            on_press: root.on_dot_press(3)

                        Button:
                            id: d2
                            text: '*'
                            font_size: dp(24)
                            width: dp(70)
                            height: dp(70)
                            size_hint: None, None
                            on_press: root.on_dot_press(1)

                        Button:
                            id: d5
                            text: '*'
                            font_size: dp(24)
                            width: dp(70)
                            height: dp(70)
                            size_hint: None, None
                            on_press: root.on_dot_press(4)

                        Button:
                            id: d3
                            text: '*'
                            font_size: dp(24)
                            width: dp(70)
                            height: dp(70)
                            size_hint: None, None
                            on_press: root.on_dot_press(2)

                        Button:
                            id: d6
                            text: '*'
                            font_size: dp(24)
                            width: dp(70)
                            height: dp(70)
                            size_hint: None, None
                            on_press: root.on_dot_press(5)

            ScrollView:
                id: letters_scroll
                bar_width: dp(8)
                opacity: 1 if not root.is_learning_active else 0
                scroll_y: 1.0
                disabled: root.is_learning_active
                size_hint_y: None
                height: self.parent.height if not root.is_learning_active else 0

                GridLayout:
                    id: letters_grid
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(10)
                    padding: [dp(10), dp(5), dp(10), dp(5)]
                    row_default_height: dp(80)
                    valign: 'top'

        BoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)

            BaseButton:
                id: back_finish_btn
                text: root.back_btn if root.is_learning_active else root.finish_btn_text
                font_name: 'BrailleFont'
                height: dp(50)
                on_press: app.switch_screen('lessons') if root.is_learning_active else root.finish_lesson()

<LessonTestScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12)
        spacing: dp(10)

        Label:
            text: root.test_title
            font_name: 'BrailleFont'
            font_size: dp(22)
            size_hint_y: None
            height: dp(42)

        Label:
            text: root.counter_label
            font_name: 'BrailleFont'
            font_size: dp(16)
            size_hint_y: None
            height: dp(28)

        Label:
            text: root.prompt_text
            font_name: 'BrailleFont'
            font_size: min(dp(72), self.height * 0.6) if self.height > 0 else dp(40)
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
                font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
                time_left: root.time_left
                quick_review_mode: root.quick_review_mode

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.3
            padding: dp(10)
            Label:
                text: root.braille_char
                font_name: 'BrailleFont'
                font_size: min(dp(72), self.height * 0.6) if self.height > 0 else dp(40)
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
            font_name: 'BrailleFont'
            height: dp(50)
            on_press: root.exit_to_practice_levels()

<EasyWordsPracticeScreen>:
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
                font_name: 'BrailleFont'
                time_left: root.time_left
                quick_review_mode: root.quick_review_mode

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.3
            padding: dp(10)

            Label:
                text: root.prompt_text
                font_name: 'BrailleFont'
                font_size: min(dp(56), self.height * 0.42) if self.height > 0 else dp(32)
                size_hint: (0.95, 0.95)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                halign: 'center'
                valign: 'middle'
                text_size: self.size

        GridLayout:
            id: answers_grid
            cols: 1
            spacing: dp(5)
            size_hint_y: 0.6
            padding: [dp(20), 0, dp(20), 0]
            row_default_height: dp(80)

        BaseButton:
            text: root.back_btn
            font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
            font_size: min(dp(72), self.height * 0.6) if self.height > 0 else dp(40)
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
                    width: dp(70)
                    height: dp(70)
                    size_hint: None, None
                    on_press: root.on_dot_press(0, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot1

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(70)
                    height: dp(70)
                    size_hint: None, None
                    on_press: root.on_dot_press(3, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot4

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(70)
                    height: dp(70)
                    size_hint: None, None
                    on_press: root.on_dot_press(1, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot2

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(70)
                    height: dp(70)
                    size_hint: None, None
                    on_press: root.on_dot_press(4, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot5

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(70)
                    height: dp(70)
                    size_hint: None, None
                    on_press: root.on_dot_press(2, self)
                    background_disabled_normal: self.background_normal
                    background_disabled_down: self.background_down
                    id: dot3

                Button:
                    text: '*'
                    font_size: dp(24)
                    width: dp(70)
                    height: dp(70)
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
                font_name: 'BrailleFont'
                size_hint: 0.45, None
                height: dp(50)
                on_press: root.confirm_answer()
                background_disabled_normal: self.background_normal
                background_disabled_down: self.background_down

            BaseButton:
                id: hint_btn
                text: root.hint_btn
                font_name: 'BrailleFont'
                size_hint: 0.45, None
                height: dp(50)
                on_press: root.show_hint()
                background_disabled_normal: self.background_normal
                background_disabled_down: self.background_down

        BaseButton:
            text: root.back_btn
            font_name: 'BrailleFont'
            height: dp(50)
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
                font_name: 'BrailleFont'
                font_size: min(dp(72), self.height * 0.6) if self.height > 0 else dp(40)
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
                    font_name: 'BrailleFont'
                    on_press: root.on_no_error_press()
                    height: dp(50)
                    background_disabled_normal: self.background_normal

            BaseButton:
                text: root.back_btn
                font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
                font_size: dp(22)
                bold: True
                halign: 'left'
                size_hint_x: 0.6
                text_size: self.size
                valign: 'middle'
                color: (0.9, 0.9, 0.9, 1)

            Label:
                text: root.moves_label
                font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
                font_size: dp(22)
                bold: True
                halign: 'left'
                text_size: self.size
                valign: 'middle'
                size_hint_x: 0.65

            Label:
                text: root.status_text
                font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
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
                    font_name: 'BrailleFont'
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
                text: root.back_btn
                font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.language_label
                            font_name: 'BrailleFont'
                            size_hint_x: None
                            width: dp(100)
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Spinner:
                            id: lang_spinner
                            text: root.current_lang
                            font_name: 'BrailleFont'
                            values: root.language_values
                            size_hint_x: 1
                            on_text: root.update_settings('language', self.text)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.use_stats
                            font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'
                        height: dp(50)
                        on_press: root.reset_stats()
                    BaseButton:
                        text: root.reset_lessons_btn
                        font_name: 'BrailleFont'
                        height: dp(50)
                        on_press: root.reset_lessons_progress()

                SettingsSection:
                    SettingsHeader:
                        text: root.easy_mode_header
                        font_name: 'BrailleFont'

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.difficulty_label
                            font_name: 'BrailleFont'
                            size_hint_x: None
                            width: dp(100)
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Spinner:
                            id: difficulty_spinner
                            text: root.current_difficulty_str
                            font_name: 'BrailleFont'
                            values: root.difficulty_values
                            size_hint_x: 1
                            width: dp(150)
                            on_text: root.update_settings('difficulty', self.text)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_letters
                            font_name: 'BrailleFont'
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
                            font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.mirror_mode_label
                            font_name: 'BrailleFont'
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
                            font_name: 'BrailleFont'
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
                            font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.time_label
                            font_name: 'BrailleFont'
                            size_hint_x: None
                            width: dp(150)
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        TextInput:
                            id: time_input
                            font_name: 'BrailleFont'
                            text: str(app.quick_review_time)
                            font_name: 'BrailleFont'
                            hint_text: root.time_hint
                            input_filter: 'int'
                            multiline: False
                            size_hint_x: 1
                            width: dp(150)
                            padding: [dp(10), (self.height - self.line_height) / 2]
                            on_text: root.update_settings('time', self.text)
                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.quick_mode_easy_label
                            font_name: 'BrailleFont'
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: quick_easy_sw
                            active: app.quick_mode_easy
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_quick_easy(self.active)
                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.quick_mode_easy_words_label
                            font_name: 'BrailleFont'
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: quick_easy_words_sw
                            active: app.quick_mode_easy_words
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_quick_easy_words(self.active)
                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.quick_mode_medium_label
                            font_name: 'BrailleFont'
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: quick_medium_sw
                            active: app.quick_mode_medium
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_quick_medium(self.active)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.quick_mode_hard_label
                            font_name: 'BrailleFont'
                            halign: 'left'
                            text_size: self.width, None
                            valign: 'middle'
                        Switch:
                            id: quick_hard_sw
                            active: app.quick_mode_hard
                            size_hint_x: None
                            width: dp(60)
                            on_active: root.toggle_quick_hard(self.active)

                SettingsSection:
                    SettingsHeader:
                        text: root.memory_game_title
                        font_name: 'BrailleFont'

                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        Label:
                            text: root.include_letters
                            font_name: 'BrailleFont'
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
                            font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
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
        font_name: 'BrailleFont'
        font_size: dp(26) if root.is_header else dp(56)
        bold: root.is_header
        size_hint_x: 1 if root.is_header else 0.25
        halign: 'center'
        valign: 'middle'
        text_size: self.size
        color: (0.95, 0.95, 0.95, 1)

    Label:
        text: root.stats if not root.is_header else ''
        font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
            height: dp(50)
            on_press: app.switch_screen('menu')

<TranslatorScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        Label:
            text: root.translator_title
            font_name: 'BrailleFont'
            font_size: dp(26)
            size_hint_y: None
            height: dp(45)
            halign: 'center'
            valign: 'middle'

        TextInput:
            id: input_text
            font_name: 'BrailleFont'
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
                font_name: 'BrailleFont'
                size_hint: (1, 1)
                height: dp(60)
                on_press: root.copy_braille_result()

            BaseButton:
                text: root.input_braille_btn
                font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'
                        size_hint: 0.5, 1
                        height: dp(60)
                        on_press: root.confirm_braille_input()

                    BaseButton:
                        text: root.delete_btn
                        font_name: 'BrailleFont'
                        size_hint: 0.5, 1
                        height: dp(60)
                        on_press: root.delete_last_char()

        BaseButton:
            text: root.back_btn
            font_name: 'BrailleFont'
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
            font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'
                        on_press: root.start_easy_level()
                    BaseButton:
                        text: root.easy_words_level_btn
                        font_name: 'BrailleFont'
                        on_press: root.start_easy_words_level()
                    BaseButton:
                        text: root.medium_level_btn
                        font_name: 'BrailleFont'
                        on_press: root.start_medium_level()
                    BaseButton:
                        text: root.hard_level_btn
                        font_name: 'BrailleFont'
                        on_press: root.start_hard_level()
                    BaseButton:
                        text: root.quick_review_btn
                        font_name: 'BrailleFont'
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
                        font_name: 'BrailleFont'

                    BaseButton:
                        text: root.memory_game_title
                        font_name: 'BrailleFont'
                        on_press: app.switch_screen('memory_game')
                    BaseButton:
                        text: root.word_search_title
                        font_name: 'BrailleFont'
                        on_press: app.switch_screen('word_search')

        BaseButton:
            text: root.back_btn
            font_name: 'BrailleFont'
            height: dp(50)
            on_press: app.switch_screen('menu')
''')

number_sign_dots = [0, 0, 1, 1, 1, 1]  # ⠼
digits_data = {
    '1': [1, 0, 0, 0, 0, 0], '2': [1, 1, 0, 0, 0, 0], '3': [1, 0, 0, 1, 0, 0],
    '4': [1, 0, 0, 1, 1, 0], '5': [1, 0, 0, 0, 1, 0], '6': [1, 1, 0, 1, 0, 0],
    '7': [1, 1, 0, 1, 1, 0], '8': [1, 1, 0, 0, 1, 0], '9': [0, 1, 0, 1, 0, 0],
    '0': [0, 1, 0, 1, 1, 0]}


def load_translations():
    translations_dir = resource_find("assets/translations") or os.path.join(
        os.path.dirname(__file__), "assets", "translations"
    )

    loaded_translations = {}
    loaded_languages = {}

    if not os.path.isdir(translations_dir):
        print(f"Translations directory not found: {translations_dir}")
        return {"en": {}}, {"en": "English"}

    for filename in os.listdir(translations_dir):
        if not filename.endswith(".json"):
            continue

        lang_code = os.path.splitext(filename)[0]
        path = os.path.join(translations_dir, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "strings" in data:
                loaded_translations[lang_code] = data.get("strings", {})
                loaded_languages[lang_code] = data.get("language_name", lang_code)
            elif isinstance(data, dict):
                loaded_translations[lang_code] = data
                loaded_languages[lang_code] = lang_code

        except Exception as e:
            print(f"Error loading translation file {path}: {e}")

    valid_codes = [code for code in loaded_translations if code in braille_data]
    loaded_translations = {code: loaded_translations[code] for code in valid_codes}
    loaded_languages = {code: loaded_languages[code] for code in valid_codes}

    if "en" not in loaded_translations:
        loaded_translations["en"] = {}
        loaded_languages["en"] = "English"

    return loaded_translations, loaded_languages


def load_braille_data():
    braille_dir = resource_find("assets/braille") or os.path.join(
        os.path.dirname(__file__), "assets", "braille"
    )

    loaded = {}

    if not os.path.isdir(braille_dir):
        print(f"Braille directory not found: {braille_dir}")
        return loaded

    for filename in os.listdir(braille_dir):
        if not filename.endswith(".json"):
            continue

        lang_code = os.path.splitext(filename)[0]
        path = os.path.join(braille_dir, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"Invalid braille file format: {path}")
                continue

            valid_lang_map = {}
            for char, dots in data.items():
                if (
                        isinstance(char, str)
                        and len(char) >= 1
                        and isinstance(dots, list)
                        and len(dots) == 6
                        and all(x in (0, 1) for x in dots)
                ):
                    valid_lang_map[char] = dots
                else:
                    print(f"Invalid braille entry in {path}: {char} -> {dots}")

            if valid_lang_map:
                loaded[lang_code] = valid_lang_map

        except Exception as e:
            print(f"Error loading braille file {path}: {e}")

    return loaded


braille_data = load_braille_data()
translations, LANGUAGES = load_translations()


# _original_bubble_button_init = BubbleButton.__init__
#
#
# def _update_bubble_text(instance, value):
#     defaults = {
#         'Copy': 'copy_popup',
#         'Cut': 'cut_popup',
#         'Paste': 'paste_popup',
#         'Select All': 'select_all_popup'
#     }
#
#     if value in defaults:
#         app = App.get_running_app()
#         if not app: return
#         lang = getattr(app, 'current_language', 'en')
#
#         if 'translations' in globals():
#             tr_data = globals()['translations']
#             t_dict = tr_data.get(lang, tr_data['en'])
#             key = defaults[value]
#             if key in t_dict and t_dict[key] != value:
#                 instance.text = t_dict[key]
#
#
# def _update_bubble_width_tree(instance, size):
#     new_btn_width = size[0] + dp(40)
#
#     if instance.width != new_btn_width:
#         instance.width = new_btn_width
#
#     content = instance.parent
#     if content and isinstance(content, BubbleContent):
#         content.size_hint_x = None
#         content.width = content.minimum_width
#
#         bubble = content.parent
#         if bubble and isinstance(bubble, Bubble):
#             bubble.size_hint_x = None
#             bubble.width = content.width + dp(32)
#
#
# def _localized_bubble_button_init(self, **kwargs):
#     _original_bubble_button_init(self, **kwargs)
#
#     if self.text:
#         _update_bubble_text(self, self.text)
#     self.bind(text=_update_bubble_text)
#
#     self.size_hint_x = None
#
#     self.bind(texture_size=_update_bubble_width_tree)
#
#     if self.texture_size:
#         Clock.schedule_once(lambda dt: _update_bubble_width_tree(self, self.texture_size), 0)
#
# BubbleButton.__init__ = _localized_bubble_button_init


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
        lang_dict = translations.get(lang, {})
        en_dict = translations.get('en', {})
        return lang_dict.get(key, en_dict.get(key, key))

    def load_braille_data(self):
        self.braille_data = self.app.braille_data[self.app.current_language]

    def animate_correct(self, widget):
        Animation.cancel_all(widget, "font_size", "background_color")

        original_size = float(widget.font_size)

        anim = (
                Animation(font_size=original_size * 1.6, duration=0.15, t="out_back")
                + Animation(font_size=original_size, duration=0.10, t="out_quad")
        )
        anim.start(widget)

    def animate_wrong(self, widget):
        Animation.cancel_all(widget, "x")

        x0 = widget.x
        d = dp(10)

        anim = (
                Animation(x=x0 - d, duration=0.04)
                + Animation(x=x0 + d, duration=0.04)
                + Animation(x=x0 - d * 0.6, duration=0.04)
                + Animation(x=x0 + d * 0.6, duration=0.04)
                + Animation(x=x0, duration=0.05)
        )
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

    def update_streak_text(self, score_key, local_streak_attr="current_streak",
                           streak_prop="streak_text", ):
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
        self.stop_timer()
        self.cancel_all_events()
        self.timer_active = False

    def cancel_all_events(self):
        for event in self.scheduled_events:
            event.cancel()
        self.scheduled_events.clear()

    def show_popup(self, title, text="", *, size=(dp(320), dp(240)), auto_dismiss=False,
                   buttons=(), font_size=dp(20), font_name=None,
                   padding=dp(20), spacing=dp(12), buttons_height=dp(50), buttons_spacing=dp(10),
                   text_width=None):

        root = BoxLayout(orientation="vertical", padding=padding, spacing=spacing)

        lbl = Label(
            text=text,
            font_size=font_size,
            font_name=font_name,
            halign="center",
            valign="middle",
            size_hint_y=1,
            markup=True, )

        def _sync(*_):
            w = lbl.width if text_width is None else text_width
            lbl.text_size = (w, None)

        lbl.bind(size=_sync, text=_sync)
        _sync()

        root.add_widget(lbl)

        popup = Popup(
            title=title,
            title_font=font_name,
            content=root,
            size_hint=(None, None),
            size=size,
            auto_dismiss=auto_dismiss, )

        if buttons:
            row = BoxLayout(size_hint_y=None, height=buttons_height, spacing=buttons_spacing)

            def handler(cb):
                def _(*_):
                    popup.dismiss()
                    if cb:
                        cb()

                return _

            for caption, cb in buttons:
                b = Button(text=caption, font_name=font_name)
                b.bind(on_press=handler(cb))
                row.add_widget(b)

            root.add_widget(row)

        popup.open()
        return popup

    def disable_children(self, widget):
        for ch in widget.children:
            ch.disabled = True
            if hasattr(ch, "disabled_color"):
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

    def dots_for_symbol(self, sym):
        if sym in digits_data:
            return digits_data[sym]
        return self.app.braille_data[self.app.current_language][sym]

    def hamming(self, a, b):
        return sum(1 for ai, bi in zip(a, b) if ai != bi)

    def build_answers_hamming(self, correct_sym, pool, k):

        if k <= 1:
            return [correct_sym]

        try:
            correct_dots = self.dots_for_symbol(correct_sym)
        except KeyError:
            answers = [correct_sym] + [p for p in pool if p != correct_sym]
            random.shuffle(answers)
            return answers[:k]

        candidates = []
        for s in pool:
            if s == correct_sym:
                continue
            try:
                d = self.dots_for_symbol(s)
            except KeyError:
                continue
            dist = self.hamming(correct_dots, d)
            candidates.append((dist, s))

        candidates.sort(key=lambda x: x[0])

        answers = [correct_sym]
        need = k - 1

        need_close = min(len(candidates), int(round(need * 0.7)))
        need_rand = need - need_close

        close = [s for _, s in candidates[:max(10, k * 3)]]
        random.shuffle(close)
        answers.extend(close[:need_close])

        remaining = [s for _, s in candidates if s not in answers]
        random.shuffle(remaining)
        answers.extend(remaining[:need_rand])

        if len(answers) < k:
            extra = [s for s in pool if s not in answers]
            random.shuffle(extra)
            answers.extend(extra[:(k - len(answers))])

        answers = answers[:k]
        random.shuffle(answers)
        return answers


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
                lang_map = self.app.braille_data.get(self.app.current_language, {})
                if char in lang_map:
                    dots = lang_map[char]
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


class LessonRow(BoxLayout):
    lesson_index = NumericProperty(0)
    title = StringProperty('')
    letters_text = StringProperty('')
    btn_text = StringProperty('')
    status_markup = StringProperty('')
    is_unlocked = BooleanProperty(True)

    _height_cache = {}

    row_height = NumericProperty(dp(110))
    letters_height = NumericProperty(dp(20))

    _pad_y = dp(8) * 2
    _spacing_y = dp(4) * 2
    _title_h = dp(24)
    _buttons_h = dp(40)
    _min_letters_h = dp(20)

    def on_kv_post(self, base_widget):
        self.bind(width=self._trigger_recalc)
        self.bind(letters_text=self._trigger_recalc)
        Clock.schedule_once(lambda dt: self._recalc_heights(), 0)

    def _trigger_recalc(self, *args):
        Clock.schedule_once(lambda dt: self._recalc_heights(), 0)

    def _recalc_heights(self):
        wrap_w = max(1, self.width - dp(12) * 2)
        fs = int(dp(14))
        key = (int(wrap_w), self.letters_text, fs)

        cached = self._height_cache.get(key)
        if cached:
            letters_h, row_h = cached
            if self.letters_height != letters_h:
                self.letters_height = letters_h
            if self.row_height != row_h:
                self.row_height = row_h
            return

        cl = CoreLabel(text=self.letters_text, font_size=dp(14))
        cl.text_size = (wrap_w, None)
        cl.refresh()

        letters_h = max(self._min_letters_h, cl.texture.size[1])
        row_h = self._pad_y + self._spacing_y + self._title_h + letters_h + self._buttons_h

        self._height_cache[key] = (letters_h, row_h)
        self.letters_height = letters_h
        self.row_height = row_h


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
        self.refresh_lessons(force=True)

    def switch_mode(self, mode):
        self.current_mode = mode
        self.refresh_lessons(force=True)

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

    def populate_lessons(self):
        app = self.app
        lang = app.current_language
        lessons = app.get_lessons(lang, self.current_mode)
        data = []
        is_previous_completed = True

        for idx, lesson in enumerate(lessons):
            stars = app.get_lesson_stars(lang, idx, self.current_mode)
            is_unlocked = is_previous_completed
            is_previous_completed = (stars > 0)

            mode = lesson['mode']

            if mode == 'study':
                mode_title = self.get_translation('training_title')
            elif mode == 'practice':
                mode_title = self.get_translation('practice')
            elif mode == 'review':
                mode_title = self.get_translation('review')
            else:
                mode_title = self.get_translation('Test')

            title = f"{self.get_translation('lesson')} {idx + 1}: {mode_title}"
            letters_text = self.get_translation('letters_label').format(' '.join(lesson['letters']))

            if stars > 0:
                if mode == 'study':
                    status_text = f"[color=33aa33]{self.get_translation('completed')}[/color]"
                    btn_text = self.get_translation('retry')
                else:
                    filled_star = "[color=FFD700]★[/color]"
                    empty_star = "[color=555555]★[/color]"
                    stars_visual = (filled_star * stars) + (empty_star * (5 - stars))
                    status_text = f"[font=BrailleFont]{stars_visual}[/font]"
                    btn_text = self.get_translation('retry')

            elif is_unlocked:
                status_text = f"[color=3333aa]{self.get_translation('available')}[/color]"
                btn_text = self.get_translation('start')
            else:
                status_text = f"[color=aa3333]{self.get_translation('locked')}[/color]"
                btn_text = self.get_translation('start')

            data.append({
                "lesson_index": idx,
                "title": title,
                "letters_text": letters_text,
                "btn_text": btn_text,
                "status_markup": status_text,
                "is_unlocked": is_unlocked,
            })

        self.ids.lessons_rv.data = data

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
            scr.set_lesson(
                lesson_index,
                lesson['letters'],
                lesson_mode=lesson.get('mode', 'practice'),
                is_final_exam=is_exam,
                lesson_type=self.current_mode
            )
            app.switch_screen('lesson_test')


class LessonStudyScreen(BaseScreen):
    lesson_title = StringProperty()
    finish_btn_text = StringProperty()
    current_symbol = StringProperty('')
    is_learning_active = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lesson_index = 0
        self.letters = []
        self.lesson_type = 'letters'
        self._i = 0
        self._target_dots = [0] * 6
        self._pressed = [0] * 6
        self._dot_btns = []
        self._pulse_anims = {}
        self._locked = False
        self._letters_table_widgets = []
        self._phase = 'learn'
        self._practice_indices = []

    def update_lang(self):
        super().update_lang()
        self.finish_btn_text = self.get_translation('complete_lesson')

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

    def set_lesson(self, lesson_index, letters, lesson_type='letters'):
        self.lesson_index = lesson_index
        self.letters = letters[:]
        self.lesson_type = lesson_type
        self.is_learning_active = True
        self._phase = 'learn'
        self._i = 0

        self.update_lang()
        mode_title = self.get_translation('training_title')
        self.lesson_title = f"{self.get_translation('lesson')} {lesson_index + 1}: {mode_title}"

        Clock.schedule_once(lambda dt: self._show_current(), 0)

    def _dots_for_symbol(self, sym):
        if self.lesson_type == 'digits':
            return digits_data[sym]
        return self.app.braille_data[self.app.current_language][sym]

    def _reset_buttons_visual(self):
        for b in self._dot_btns:
            b.background_color = (1, 1, 1, 1)
            b.disabled = False
            b.disabled_color = (1, 1, 1, 1)

    def _stop_all_pulses(self):
        for btn in self._dot_btns:
            Animation.cancel_all(btn, "background_color")
            Animation.cancel_all(btn, "x")
            if hasattr(btn, "_is_animating"):
                btn._is_animating = False
        self._pulse_anims.clear()

    def _start_pulses_for_targets(self):
        for idx, need in enumerate(self._target_dots):
            if not need:
                continue
            btn = self._dot_btns[idx]
            Animation.cancel_all(btn, "background_color")
            btn.background_color = (0.7, 0.9, 1.0, 1)

            anim = (
                    Animation(background_color=(0.4, 0.7, 1.0, 1), duration=0.55)
                    + Animation(background_color=(0.7, 0.9, 1.0, 1), duration=0.55)
            )
            anim.repeat = True
            anim.start(btn)
            self._pulse_anims[idx] = anim

    def _ensure_dot_buttons(self):
        if len(self._dot_btns) == 6:
            return True
        if not self.ids:
            return False
        try:
            self._dot_btns = [self.ids.d1, self.ids.d2, self.ids.d3, self.ids.d4, self.ids.d5, self.ids.d6]
            return True
        except Exception:
            return False

    def _show_current(self):
        if not self._ensure_dot_buttons():
            Clock.schedule_once(lambda dt: self._show_current(), 0)
            return

        if self._phase == 'learn':
            self._show_learn_phase()
        elif self._phase == 'practice':
            self._show_practice_phase()
        else:
            self._show_review_phase()

    def _show_learn_phase(self):
        if self._i >= len(self.letters):
            self._phase = 'practice'
            self._practice_indices = list(range(len(self.letters)))
            random.shuffle(self._practice_indices)
            self._i = 0
            self._show_current()
            return

        self._locked = False
        self.current_symbol = self.letters[self._i]
        self._target_dots = self._dots_for_symbol(self.current_symbol)
        self._pressed = [0] * 6

        self._stop_all_pulses()
        self._reset_buttons_visual()
        self._start_pulses_for_targets()

        lbl = self.ids.study_symbol
        Animation.cancel_all(lbl, "opacity")
        lbl.opacity = 0
        Animation(opacity=1, duration=0.25).start(lbl)

    def _show_practice_phase(self):
        if self._i >= len(self._practice_indices):
            self._phase = 'review'
            self._i = 0
            self._show_current()
            return

        idx = self._practice_indices[self._i]
        self._locked = False
        self.current_symbol = self.letters[idx]
        self._target_dots = self._dots_for_symbol(self.current_symbol)
        self._pressed = [0] * 6

        self._stop_all_pulses()
        self._reset_buttons_visual()

        lbl = self.ids.study_symbol
        Animation.cancel_all(lbl, "opacity")
        lbl.opacity = 0
        Animation(opacity=1, duration=0.25).start(lbl)

    def _show_review_phase(self):
        self.is_learning_active = False
        self.current_symbol = ""
        self._stop_all_pulses()
        self._locked = True
        for b in self._dot_btns:
            b.disabled = True
        self._show_letters_table()

    def _show_letters_table(self):
        grid = self.ids.letters_grid

        need_pairs = len(self.letters)

        while len(self._letters_table_widgets) < need_pairs:
            letter_label = Label(
                text="",
                font_size=dp(58),
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(80)
            )
            braille_label = Label(
                text="",
                font_name='BrailleFont',
                font_size=dp(62),
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(80)
            )
            self._letters_table_widgets.append((letter_label, braille_label))

        if len(grid.children) != need_pairs * 2:
            grid.clear_widgets()
            for i in range(need_pairs):
                ll, bl = self._letters_table_widgets[i]
                grid.add_widget(ll)
                grid.add_widget(bl)

        is_digits = (self.lesson_type == 'digits')
        ns = self.get_braille_char(number_sign_dots)

        for i, char in enumerate(self.letters):
            if is_digits:
                dots = digits_data[char]
                braille_char = ns + self.get_braille_char(dots)
            else:
                dots = self.app.braille_data[self.app.current_language][char]
                braille_char = self.get_braille_char(dots)

            ll, bl = self._letters_table_widgets[i]
            ll.text = char
            bl.text = braille_char

        grid.height = grid.minimum_height

        scroll_view = self.ids.letters_scroll
        scroll_view.opacity = 0
        scroll_view.disabled = True
        scroll_view.scroll_y = 1.0

        study_panel = self.ids.study_panel
        Animation(opacity=0, duration=0.2).start(study_panel)

        def show_table(dt):
            Animation(opacity=1, duration=0.3).start(scroll_view)
            scroll_view.disabled = False
            scroll_view.scroll_y = 1.0

        Clock.schedule_once(show_table, 0.2)

    def on_dot_press(self, dot_index: int):
        if not self._ensure_dot_buttons():
            return
        if self._locked or not self.current_symbol or not self.is_learning_active:
            return

        btn = self._dot_btns[dot_index]

        if getattr(btn, '_is_animating', False):
            return

        need = bool(self._target_dots[dot_index])

        if not need:
            if self._phase == 'practice':
                self._reset_pressed_on_error()

            btn._is_animating = True

            Animation.cancel_all(btn, "background_color")
            Animation.cancel_all(btn, "x")

            btn.background_color = (1, 0.4, 0.4, 1)

            original_x = btn.x
            anim = (
                    Animation(x=original_x - dp(10), duration=0.05)
                    + Animation(x=original_x + dp(10), duration=0.1)
                    + Animation(x=original_x - dp(10) * 0.6, duration=0.04)
                    + Animation(x=original_x + dp(10) * 0.6, duration=0.04)
                    + Animation(x=original_x, duration=0.05)
            )

            def on_anim_complete(*args):
                btn._is_animating = False
                btn.background_color = (1, 1, 1, 1)

                if self._phase == 'learn':
                    self._restore_dot_color(dot_index)

            anim.bind(on_complete=on_anim_complete)
            anim.start(btn)
            return

        if self._pressed[dot_index]:
            return

        self._pressed[dot_index] = 1

        if dot_index in self._pulse_anims:
            Animation.cancel_all(btn, "background_color")
            del self._pulse_anims[dot_index]

        btn.background_color = (0.2, 0.85, 0.2, 1)
        self.animate_correct(btn)

        if self._is_completed():
            self._go_next()

    def _reset_pressed_on_error(self):
        self._pressed = [0] * 6

        self._pulse_anims.clear()

        for i in range(6):
            btn = self._dot_btns[i]
            Animation.cancel_all(btn, "background_color")
            btn.background_color = (1, 1, 1, 1)

    def _restore_dot_color(self, dot_index: int):
        if self._locked or not self.is_learning_active:
            return

        if dot_index >= len(self._dot_btns):
            return

        btn = self._dot_btns[dot_index]

        if getattr(btn, '_is_animating', False):
            Clock.schedule_once(lambda dt: self._restore_dot_color(dot_index), 0.05)
            return

        Animation.cancel_all(btn, "background_color")

        if self._target_dots[dot_index] and not self._pressed[dot_index]:
            if self._phase == 'learn':
                btn.background_color = (0.7, 0.9, 1.0, 1)
                anim = (
                        Animation(background_color=(0.4, 0.7, 1.0, 1), duration=0.55)
                        + Animation(background_color=(0.7, 0.9, 1.0, 1), duration=0.55)
                )
                anim.repeat = True
                anim.start(btn)
                self._pulse_anims[dot_index] = anim
        else:
            btn.background_color = (1, 1, 1, 1)

    def _is_completed(self):
        for i in range(6):
            if self._target_dots[i] and not self._pressed[i]:
                return False
        return True

    def _go_next(self):
        self._locked = True
        self._stop_all_pulses()

        lbl = self.ids.study_symbol
        anim = Animation(opacity=0, duration=0.18)

        def _after(*_):
            self._i += 1
            self._locked = False
            self._show_current()

        anim.bind(on_complete=lambda *a: self.schedule_once(lambda dt: _after(), 0.05))
        anim.start(lbl)

    def finish_lesson(self):
        if self.is_learning_active:
            return

        self.app.mark_lesson_completed(self.app.current_language, self.lesson_index, self.lesson_type, 5)
        self.app.switch_screen('lessons')

    def on_kv_post(self, base_widget):
        self._dot_btns = [self.ids.d1, self.ids.d2, self.ids.d3, self.ids.d4, self.ids.d5, self.ids.d6]
        for b in self._dot_btns:
            b._is_animating = False
            b._restore_token = 0
            b._x0 = b.x

    def on_leave(self, *args):
        super().on_leave(*args)
        self._stop_all_pulses()
        self._locked = True


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
        self.lesson_type = 'letters'

    def on_leave(self, *args):
        super().on_leave(*args)
        for ev in self.scheduled_events:
            ev.cancel()
        self.scheduled_events.clear()

    def update_lang(self):
        super().update_lang()
        self.test_title = self.get_translation('lesson_test_title')

    def set_lesson(self, lesson_index, letters, *, lesson_mode='practice', is_final_exam=False, lesson_type='letters'):
        self.lesson_index = lesson_index
        self.letters = letters[:]
        self.lesson_type = lesson_type
        self.lesson_mode = lesson_mode

        if is_final_exam or lesson_mode == "exam":
            self.questions_total = len(self.letters) * 3
            self.question_list = self.letters * 3

        elif lesson_mode == "review":
            self.question_list = self.letters[:]
            random.shuffle(self.question_list)
            self.questions_total = len(self.question_list)

        else:
            self.questions_total = max(8, len(self.letters) * 2)
            self.question_list = self.letters * 2
            while len(self.question_list) < self.questions_total:
                self.question_list.append(random.choice(self.letters))
            random.shuffle(self.question_list)

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
                btn.font_name = 'BrailleFont'

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
            self.animate_correct(instance)
        else:
            instance.background_color = (1, 0, 0, 1)
            self.animate_wrong(instance)
            if self.correct_button:
                self.correct_button.background_color = (0, 1, 0, 1)
            self.app.update_char_stat(correct_char, False)

        self.schedule_once(self.next_question, 0.8)

    def finish_test(self):
        max_stars = getattr(self.app, "LESSON_STARS_MAX", 5)
        ratio = (self.correct / self.questions_total) if self.questions_total else 0.0

        stars = int(math.floor(ratio * max_stars + 1e-9))
        stars = max(0, min(stars, max_stars))

        if stars >= 1:
            self.app.mark_lesson_completed(self.app.current_language, self.lesson_index, self.lesson_type, stars=stars)

        percent = int(ratio * 100)
        stars_line = f"[font=BrailleFont]{'★' * stars + '☆' * (max_stars - stars)}[/font]"
        msg = f"{self.correct}/{self.questions_total} ({percent}%)\n{stars_line}"

        title = self.get_translation('lesson_test_title')

        self.show_popup(
            title=title,
            text=msg,
            size=(dp(340), dp(220)),
            auto_dismiss=False,
            buttons=[(self.get_translation("ok"), lambda: self.app.switch_screen("lessons"))],
        )


class PracticeLevelsScreen(BaseScreen):
    title = StringProperty()
    easy_level_btn = StringProperty()
    easy_words_level_btn = StringProperty()
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
        self.easy_words_level_btn = self.get_translation('easy_words_level')
        self.medium_level_btn = self.get_translation('medium_level')
        self.hard_level_btn = self.get_translation('hard_level')
        self.games = self.get_translation('games')
        self.memory_game_title = self.get_translation('memory_game_title')
        self.word_search_title = self.get_translation('word_search_title')
        self.quick_review_btn = self.get_translation('quick_review')

    def start_easy_level(self):
        scr = self.app.get_screen('practice')
        scr.quick_review_mode = False
        self.app.switch_screen('practice')
        scr.new_question()

    def start_easy_words_level(self):
        scr = self.app.get_screen('easy_words_practice')
        scr.quick_review_mode = False
        self.app.switch_screen('easy_words_practice')
        scr.new_question()

    def start_medium_level(self):
        scr = self.app.get_screen('medium_practice')
        scr.quick_review_mode = False
        self.app.switch_screen('medium_practice')

    def start_hard_level(self):
        self.app.switch_screen('hard_practice')

    def start_quick_review(self):
        App.get_running_app().start_quick_review()


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
        self._answer_buttons = []
        self._last_layout_key = None
        self._grid_bound = False
        super().__init__(**kwargs)

    def handle_timeout(self):
        self.stop_timer()

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

        if self.current_symbol in digits_data:
            pool = [s for s in pool if s in digits_data]
        else:
            pool = [s for s in pool if s not in digits_data]

        k = int(self.app.current_difficulty)
        k = max(2, min(k, len(pool)))

        answers = self.build_answers_hamming(self.current_symbol, pool, k)

        horizontal_padding = dp(20)
        spacing = dp(5)
        num_options = len(answers)

        layout_cache_key = (grid.width, grid.height, num_options)

        if layout_cache_key != self._last_layout_key:
            self._last_layout_key = layout_cache_key

            available_width = grid.width - (2 * horizontal_padding)
            available_height = grid.height
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

            grid.cols = best_cols
            grid.padding = [horizontal_padding, 0, horizontal_padding, 0]
            grid.spacing = spacing
            grid.row_default_height = final_row_height
            grid.row_force_default = True

            self._cached_row_height = final_row_height
        else:
            final_row_height = self._cached_row_height

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
                    btn.font_name = 'BrailleFont'
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
        self.cancel_all_events()
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
        self.stop_timer()

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
        self.stop_timer()

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


class EasyWordsPracticeScreen(BaseScreen):
    streak_text = StringProperty()
    prompt_text = StringProperty()
    prompt_is_braille = BooleanProperty(False)
    time_left = NumericProperty(5)
    timer_active = BooleanProperty(False)
    quick_review_mode = BooleanProperty(False)
    OPTIONS_COUNT = 4

    def __init__(self, **kwargs):
        self.current_streak = 0
        self.correct_button = None
        self.current_word = ""
        self._answer_buttons = []
        self._last_layout_key = None
        self._grid_bound = False
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.cancel_all_events()
        self.update_lang()
        Clock.schedule_once(lambda dt: self.new_question(), 0)

    def on_kv_post(self, base_widget):
        self._ensure_answer_buttons()
        if not self._grid_bound:
            self.ids.answers_grid.bind(size=self._update_grid)
            self._grid_bound = True

    def update_lang(self):
        super().update_lang()
        self.update_streak_text(score_key="easy_words_practice")

    def _ensure_answer_buttons(self):
        grid = self.ids.answers_grid
        if len(self._answer_buttons) == self.OPTIONS_COUNT:
            return

        for _ in range(self.OPTIONS_COUNT):
            btn = Button(size_hint=(1, None), on_press=self.check_answer)
            btn.disabled_color = (1, 1, 1, 1)
            btn.background_disabled_normal = btn.background_normal
            btn.background_disabled_down = btn.background_down
            btn.answer_word = None
            btn.font_name = 'BrailleFont'
            btn.halign = 'center'
            btn.valign = 'middle'
            btn.bind(size=lambda inst, value: setattr(
                inst, 'text_size', (inst.width - dp(20), inst.height - dp(10))
            ))
            grid.add_widget(btn)
            self._answer_buttons.append(btn)

    def _get_word_pool(self):
        lang = self.app.current_language
        wl = self.app.word_lists.get(lang) or []
        allowed_letters = set(self.app.braille_data[lang].keys())

        valid = []
        for w in wl:
            up = w.strip().upper()
            if 2 <= len(up) <= 8 and all(c in allowed_letters for c in up):
                valid.append(up)

        if len(valid) < 4:
            letters = list(allowed_letters)
            generated = set(valid)
            while len(generated) < 24:
                generated.add("".join(random.choice(letters) for _ in range(random.randint(3, 5))))
            valid = list(generated)

        return valid

    def _word_to_braille(self, word: str) -> str:
        out = []
        ns = self.get_braille_char(number_sign_dots)
        in_number_mode = False

        for ch in word.upper():
            if ch == '\n':
                out.append('\n')
                in_number_mode = False
                continue

            if ch == ' ':
                out.append(chr(0x2800))
                in_number_mode = False
                continue

            if ch.isdigit():
                if not in_number_mode:
                    out.append(ns)
                    in_number_mode = True
                out.append(self.get_braille_char(digits_data[ch]))
                continue

            in_number_mode = False
            dots = self.app.braille_data[self.app.current_language].get(ch)
            out.append(self.get_braille_char(dots) if dots else ch)

        return ''.join(out)

    def _build_answers(self):
        pool = self._get_word_pool()
        answers = [self.current_word]

        distractors = [w for w in pool if w != self.current_word]

        similar = [w for w in distractors if abs(len(w) - len(self.current_word)) <= 1]
        other = [w for w in distractors if w not in similar]

        random.shuffle(similar)
        random.shuffle(other)

        answers.extend(similar[:self.OPTIONS_COUNT - 1])

        if len(answers) < self.OPTIONS_COUNT:
            answers.extend(other[:self.OPTIONS_COUNT - len(answers)])

        answers = answers[:self.OPTIONS_COUNT]

        remaining = [w for w in pool if w not in answers]
        random.shuffle(remaining)
        while len(answers) < self.OPTIONS_COUNT and remaining:
            answers.append(remaining.pop())

        random.shuffle(answers)
        return answers

    def new_question(self):
        self.stop_timer()

        pool = self._get_word_pool()
        if not pool:
            self.prompt_text = ""
            return

        self.current_word = random.choice(pool)
        self.invert_mode = random.random() < 0.5

        if self.invert_mode:
            self.prompt_text = self.current_word
            self.prompt_is_braille = False
        else:
            self.prompt_text = self._word_to_braille(self.current_word)
            self.prompt_is_braille = True

        self._update_grid()

        if self.quick_review_mode:
            self.start_timer()

    def _update_grid(self, *args):
        if not self.current_word:
            return

        answers = self._build_answers()
        grid = self.ids.answers_grid

        grid.cols = 1
        grid.spacing = dp(5)
        grid.padding = [dp(20), 0, dp(20), 0]

        available_height = grid.height
        row_h = (available_height - dp(5) * (self.OPTIONS_COUNT - 1)) / self.OPTIONS_COUNT
        row_h = max(dp(60), min(row_h, dp(110)))

        grid.row_default_height = row_h
        grid.row_force_default = True

        self.correct_button = None

        for i, btn in enumerate(self._answer_buttons):
            if i < len(answers):
                ans = answers[i]
                btn.opacity = 1
                btn.disabled = False
                btn.height = row_h
                btn.answer_word = ans
                btn.background_color = (1, 1, 1, 1)

                if self.invert_mode:
                    btn.text = self._word_to_braille(ans)
                    btn.font_name = 'BrailleFont'
                    btn.font_size = min(dp(30), row_h * 0.42)
                else:
                    btn.text = ans
                    btn.font_name = 'BrailleFont'
                    btn.font_size = min(dp(22), row_h * 0.28)

                if ans == self.current_word:
                    self.correct_button = btn
            else:
                btn.answer_word = None
                btn.text = ""
                btn.disabled = True
                btn.opacity = 0
                btn.height = 0

    def _set_answer_buttons_enabled(self, enabled: bool):
        for btn in self._answer_buttons:
            if btn.opacity == 0:
                continue
            btn.disabled = not enabled
            btn.disabled_color = (1, 1, 1, 1)

    def _apply_word_stats(self, is_correct: bool):
        for ch in self.current_word:
            if ch != ' ':
                self.app.update_char_stat(ch, is_correct)

    def handle_timeout(self):
        self.stop_timer()
        self._set_answer_buttons_enabled(False)

        if self.correct_button:
            self.correct_button.background_color = (0, 1, 0, 1)

        if self.current_word:
            self._apply_word_stats(False)

        if self.quick_review_mode:
            self.app.quick_streak = max(0, self.app.quick_streak - 1)
            self.update_streak_text(score_key="easy_words_practice")
            self.schedule_once(lambda dt: self.app.next_quick_step(), 1.2)
        else:
            self.current_streak = 0
            self.update_streak_text(score_key="easy_words_practice")
            self.schedule_once(lambda dt: self.new_question(), 1.2)

    def check_answer(self, instance):
        self.stop_timer()
        self._set_answer_buttons_enabled(False)

        lang = self.app.current_language
        chosen_word = getattr(instance, 'answer_word', instance.text)
        is_correct = (chosen_word == self.current_word)

        if is_correct:
            instance.background_color = (0, 1, 0, 1)
            self.animate_correct(instance)

            self._apply_word_stats(True)

            if self.quick_review_mode:
                self.app.quick_streak += 1
                if self.app.quick_streak > self.app.high_scores[lang]['quick']:
                    self.app.high_scores[lang]['quick'] = self.app.quick_streak
                    self.app.save_high_scores()
            else:
                self.current_streak += 1
                if self.current_streak > self.app.high_scores[lang].get('easy_words_practice', 0):
                    self.app.high_scores[lang]['easy_words_practice'] = self.current_streak
                    self.app.save_high_scores()
        else:
            instance.background_color = (1, 0, 0, 1)
            self.animate_wrong(instance)

            if self.correct_button:
                self.correct_button.background_color = (0, 1, 0, 1)

            self._apply_word_stats(False)

            if self.quick_review_mode:
                self.app.quick_streak = max(0, self.app.quick_streak - 1)
            else:
                self.current_streak = 0

        self.update_streak_text(score_key="easy_words_practice")

        if self.quick_review_mode:
            self.schedule_once(lambda dt: self.app.next_quick_step(), 0.9 if is_correct else 1.3)
        else:
            self.schedule_once(lambda dt: self.new_question(), 0.9 if is_correct else 1.3)


class MediumPracticeScreen(BaseScreen):
    braille_char = StringProperty()
    current_letter = StringProperty()
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
    hint_used = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_buttons = []
        self.current_streak = 0
        self.hint_used = False
        self.current_letter = ''
        self._pulse_anims = {}

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
        self.cancel_all_events()
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
        self.stop_timer()

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
                self.animate_correct(btn)
            elif correct and not user:
                btn.background_color = (1, 0.7, 0, 1)
                self.animate_correct(btn)
            elif not correct and user:
                btn.background_color = (1, 0, 0, 1)
            else:
                btn.background_color = (1, 1, 1, 1)

    def new_question(self):
        self._stop_all_pulses()
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
        if visual_index in self._pulse_anims:
            Animation.cancel_all(instance, "background_color")
            del self._pulse_anims[visual_index]

        logical_index = self.get_logical_index(visual_index)
        self.user_input[logical_index] = 1 - self.user_input[logical_index]

        instance.background_color = (0.7, 0.7, 0.7, 1) if self.user_input[logical_index] else (1, 1, 1, 1)

    def _stop_all_pulses(self):
        for idx, btn in enumerate(self.dot_buttons):
            Animation.cancel_all(btn, "background_color")
            logical_idx = self.get_logical_index(idx)
            if self.user_input[logical_idx]:
                btn.background_color = (0.7, 0.7, 0.7, 1)
            else:
                btn.background_color = (1, 1, 1, 1)
        self._pulse_anims.clear()

    def show_hint(self):
        if self.hint_used or not self.current_letter:
            return

        self.hint_used = True
        self.ids.hint_btn.disabled = True

        for visual_index, btn in enumerate(self.dot_buttons):
            logical_index = self.get_logical_index(visual_index)

            is_target = self.current_dots[logical_index] == 1
            is_pressed = self.user_input[logical_index] == 1

            if is_target and not is_pressed:
                btn.background_color = (0.7, 0.9, 1.0, 1)

                anim = (
                        Animation(background_color=(0.4, 0.7, 1.0, 1), duration=0.55) +
                        Animation(background_color=(0.7, 0.9, 1.0, 1), duration=0.55)
                )
                anim.repeat = True
                anim.start(btn)
                self._pulse_anims[visual_index] = anim

            elif not is_target and is_pressed:
                btn.background_color = (1, 0.6, 0.6, 1)

    def confirm_answer(self):
        if not self.current_letter:
            return

        self._stop_all_pulses()

        self.stop_timer()

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
                    self.current_streak += 1
                    if self.current_streak > self.app.high_scores[lang].get('medium_practice', 0):
                        self.app.high_scores[lang]['medium_practice'] = self.current_streak
                        self.app.save_high_scores()
            else:
                self.current_streak = 0
            self.update_streak_text(score_key="medium_practice")
            self.schedule_once(lambda dt: self.new_question(), 2)

    def on_leave(self, *args):
        self._stop_all_pulses()
        super().on_leave(*args)


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

    def __init__(self, **kwargs):
        self.correction_dot_buttons = []
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
        self.cancel_all_events()
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
        self.stop_timer()

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

        if 'braille_word_box' in self.ids:
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
                    self.font_name = 'BrailleFont'
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
        self._cards_pool = []
        self._grid_built = False

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

        if (not self._grid_built) or (len(self._cards_pool) != self.pairs_count * 2):
            grid.clear_widgets()
            self._cards_pool = []
            for _ in range(self.pairs_count * 2):
                card = MemoryCard(screen=self)
                card.face_down = True
                card.is_matched = False
                card.disabled = False
                card.text = ''
                card.scale_x = 1
                self._cards_pool.append(card)
                grid.add_widget(card)
            self._grid_built = True

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

        new_defs = []
        ns = self.get_braille_char(number_sign_dots)

        for char in game_chars:
            new_defs.append((char, False, char))

            if char in digits_data:
                dots = digits_data[char]
                braille_txt = ns + self.get_braille_char(dots)
            else:
                dots = braille_data[lang][char]
                braille_txt = self.get_braille_char(dots)

            new_defs.append((braille_txt, True, char))

        random.shuffle(new_defs)

        for card, (content_text, is_braille, pair_id) in zip(self._cards_pool, new_defs):
            card.screen = self
            card.content_text = content_text
            card.pair_id = pair_id
            card.is_braille = is_braille

            card.face_down = True
            card.is_matched = False
            card.disabled = False
            card.text = ''
            card.scale_x = 1
            card.font_name = 'BrailleFont'
            card.font_size = dp(32)

        shuffled_cards = self._cards_pool[:]
        random.shuffle(shuffled_cards)

        for c in shuffled_cards:
            grid.remove_widget(c)
        for c in shuffled_cards:
            grid.add_widget(c)

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
    status_text = StringProperty()
    grid_size = NumericProperty(8)
    words_line = StringProperty()

    def __init__(self, **kwargs):

        self.cells: list[Button] = []

        self._cells_n = 0

        self._n: int = 7
        self.letters_grid: list[str] = []
        self.target_words: list[str] = []
        self.target_set: set[str] = set()
        self.found_words: set[str] = set()

        self._found_paths: list[list[int]] = []
        self._found_cells_cache: set[int] = set()
        self._dragging: bool = False
        self._selected_indices: list[int] = []
        self._selected_set: set[int] = set()

        self._occ: int = 0
        self._paths_by_len: dict[int, tuple[tuple[int, ...], ...]] = {}

        self._braille_char_map: dict[str, str] = {}

        self._ws_geom = None
        self._ws_pad = dp(8)
        self._ws_sp = dp(4)

        super().__init__(**kwargs)

    def update_lang(self):
        super().update_lang()
        self.title = self.get_translation("word_search_title")
        self.words_title = self.get_translation("word_search_words_title")
        self._update_status()

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.load_braille_data()
        self._braille_char_map = {ch: self.get_braille_char(dots) for ch, dots in self.braille_data.items()}
        self.start_new_game()

    def start_new_game(self):
        self._found_cells_cache.clear()
        self.found_words.clear()
        self._found_paths.clear()
        self._clear_selection()

        self.grid_size = 7
        self._n = int(self.grid_size)

        self.target_words = self._pick_words()
        self.target_set = set(self.target_words)

        self._occ = 0
        self._paths_by_len = {L: self.all_paths(self._n, L) for L in range(3, 7)}

        self.letters_grid = [""] * (self._n * self._n)

        self._place_words_fast()
        self._fill_noise_fast()

        self._build_grid_ui_fast()
        self._build_words_ui()
        self._update_status()

    def _pick_words(self):
        lang = self.app.current_language
        wl = self.app.word_lists.get(lang) or []
        letters_set = set(self.braille_data.keys())

        candidates = list(set([w for w in wl if 3 <= len(w) <= 6 and all(c in letters_set for c in w)]))

        if len(candidates) < 8:
            items = list(letters_set)
            random_words = {
                "".join(random.choice(items) for _ in range(random.choice([3, 4, 5, 6])))
                for _ in range(60)
            }
            candidates = list(set(candidates) | random_words)

        k = 6
        return random.sample(candidates, min(k, len(candidates)))

    def _fill_noise_fast(self):
        pool = list(self.braille_data.keys())
        n2 = self._n * self._n
        for i in range(n2):
            if not self.letters_grid[i]:
                self.letters_grid[i] = random.choice(pool)

    @staticmethod
    @lru_cache(maxsize=None)
    def all_paths(n, length):
        def idx(r, c):
            return r * n + c

        paths = []

        for r in range(n):
            for c0 in range(0, n - length + 1):
                paths.append([idx(r, c0 + i) for i in range(length)])

        for r in range(n):
            for c0 in range(length - 1, n):
                paths.append([idx(r, c0 - i) for i in range(length)])

        for c in range(n):
            for r0 in range(0, n - length + 1):
                paths.append([idx(r0 + i, c) for i in range(length)])

        for c in range(n):
            for r0 in range(length - 1, n):
                paths.append([idx(r0 - i, c) for i in range(length)])

        if length >= 3:
            dirs = [
                ((0, 1), (1, 0)), ((0, 1), (-1, 0)),
                ((0, -1), (1, 0)), ((0, -1), (-1, 0)),
                ((1, 0), (0, 1)), ((1, 0), (0, -1)),
                ((-1, 0), (0, 1)), ((-1, 0), (0, -1)),
            ]

            for a in range(1, length - 1):
                b = (length - 1) - a
                for (dr1, dc1), (dr2, dc2) in dirs:
                    for r0 in range(n):
                        for c0 in range(n):
                            cells = [(r0, c0)]
                            r, c = r0, c0
                            ok = True

                            for _ in range(a):
                                r += dr1
                                c += dc1
                                if not (0 <= r < n and 0 <= c < n):
                                    ok = False
                                    break
                                cells.append((r, c))
                            if not ok:
                                continue

                            for _ in range(b):
                                r += dr2
                                c += dc2
                                if not (0 <= r < n and 0 <= c < n):
                                    ok = False
                                    break
                                cells.append((r, c))

                            if ok and len(cells) == length and len(set(cells)) == length:
                                paths.append([idx(rr, cc) for rr, cc in cells])

        if length >= 4:
            configs = [
                ((0, 1), (1, 0), (0, -1)),
                ((0, 1), (-1, 0), (0, -1)),
                ((0, -1), (1, 0), (0, 1)),
                ((0, -1), (-1, 0), (0, 1)),
            ]
            for a in range(1, length - 2):
                for b in range(1, (length - 1) - a):
                    c3 = (length - 1) - a - b
                    if c3 < 1:
                        continue
                    for (dr1, dc1), (dr2, dc2), (dr3, dc3) in configs:
                        for r0 in range(n):
                            for c0 in range(n):
                                cells = [(r0, c0)]
                                r, c = r0, c0
                                ok = True

                                for _ in range(a):
                                    r += dr1
                                    c += dc1
                                    if not (0 <= r < n and 0 <= c < n):
                                        ok = False
                                        break
                                    cells.append((r, c))
                                if not ok:
                                    continue

                                for _ in range(b):
                                    r += dr2
                                    c += dc2
                                    if not (0 <= r < n and 0 <= c < n):
                                        ok = False
                                        break
                                    cells.append((r, c))
                                if not ok:
                                    continue

                                for _ in range(c3):
                                    r += dr3
                                    c += dc3
                                    if not (0 <= r < n and 0 <= c < n):
                                        ok = False
                                        break
                                    cells.append((r, c))

                                if ok and len(cells) == length and len(set(cells)) == length:
                                    paths.append([idx(rr, cc) for rr, cc in cells])

        return tuple(tuple(p) for p in paths)

    def _can_place_word_on_path(self, word, path):
        occ = self._occ
        for idx in path:
            if (occ >> idx) & 1:
                return False
        return True

    def _place_word_on_path_1d(self, word, path):
        for ch, idx in zip(word, path):
            self.letters_grid[idx] = ch
            self._occ |= (1 << idx)

    def _place_words_fast(self):
        words = sorted(self.target_words, key=len, reverse=True)
        placed = []

        for w in words:
            paths = self._paths_by_len.get(len(w), ())
            if not paths:
                continue

            start = random.randrange(len(paths))

            for k in range(len(paths)):
                path = paths[(start + k) % len(paths)]
                if self._can_place_word_on_path(w, path):
                    self._place_word_on_path_1d(w, path)
                    placed.append(w)
                    break

        self.target_words = placed
        self.target_set = set(placed)

    def _ensure_grid_ui(self):
        grid = self.ids.ws_grid
        need = self._n * self._n

        if self._cells_n == need and len(self.cells) == need:
            return

        grid.clear_widgets()
        self.cells = []
        grid.cols = int(self._n)
        self._cells_n = need

        for idx in range(need):
            btn = Button(
                font_name="BrailleFont",
                background_normal="",
                background_down="",
                background_color=(0.2, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                padding=(0, 0),
                halign="center",
                valign="middle",
            )
            btn.ws_index = idx

            btn.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

            btn.bind(
                on_touch_down=self._on_cell_touch_down,
                on_touch_move=self._on_cell_touch_move,
                on_touch_up=self._on_cell_touch_up,
            )

            self.cells.append(btn)
            grid.add_widget(btn)

    def _build_grid_ui_fast(self):
        self._ensure_grid_ui()
        self.ids.ws_grid.cols = int(self._n)

        m = self._braille_char_map
        for idx, ch in enumerate(self.letters_grid):
            btn = self.cells[idx]
            btn.text = m.get(ch, "?")

        Clock.schedule_once(lambda dt: self._autoscale_cells(), 0)

        self._repaint()

    def _autoscale_cells(self):
        for btn in self.cells:
            side = min(btn.width, btn.height)
            btn.font_size = max(dp(18), min(dp(72), side * 0.75))

    def _build_words_ui(self):
        self._refresh_words_ui()

    def _refresh_words_ui(self):
        parts = []
        for w in self.target_words:
            if w in self.found_words:
                parts.append(f"[color=33aa3388]{w}[/color]")
            else:
                parts.append(w)
        self.words_line = "  ".join(parts)

    def _update_status(self):
        fmt = self.get_translation("word_search_status")
        self.status_text = fmt.format(len(self.found_words), len(self.target_words))

    def _clear_selection(self):
        self._dragging = False
        old = set(self._selected_set)
        self._selected_indices.clear()
        self._selected_set.clear()
        if old:
            self._repaint_delta(old_removed=old, new_added=set())

    def _repaint(self):
        found_cells = self._found_cells_cache

        base_bg, base_fg = (0.2, 0.2, 0.2, 1), (1, 1, 1, 1)
        sel_bg, sel_fg = (0.7, 0.7, 0.7, 1), (0, 0, 0, 1)
        found_bg, found_fg = (0.2, 0.7, 0.2, 1), (1, 1, 1, 1)

        for btn in self.cells:
            idx = btn.ws_index
            if idx in found_cells:
                btn.background_color, btn.color = found_bg, found_fg
            elif idx in self._selected_set:
                btn.background_color, btn.color = sel_bg, sel_fg
            else:
                btn.background_color, btn.color = base_bg, base_fg

    def _repaint_delta(self, *, old_removed: set[int], new_added: set[int]):
        found = self._found_cells_cache

        base_bg, base_fg = (0.2, 0.2, 0.2, 1), (1, 1, 1, 1)
        sel_bg, sel_fg = (0.7, 0.7, 0.7, 1), (0, 0, 0, 1)
        found_bg, found_fg = (0.2, 0.7, 0.2, 1), (1, 1, 1, 1)

        def apply(idx: int):
            btn = self.cells[idx]
            if idx in found:
                btn.background_color, btn.color = found_bg, found_fg
            elif idx in self._selected_set:
                btn.background_color, btn.color = sel_bg, sel_fg
            else:
                btn.background_color, btn.color = base_bg, base_fg

        for idx in old_removed:
            apply(idx)
        for idx in new_added:
            apply(idx)

    def _on_cell_touch_down(self, btn, touch):
        if not btn.collide_point(*touch.pos):
            return False

        self._dragging = True

        old = set(self._selected_set)
        self._selected_indices.clear()
        self._selected_set.clear()

        idx = self._index_from_pos(*touch.pos)
        if idx is None:
            idx = btn.ws_index

        self._selected_indices.append(idx)
        self._selected_set.add(idx)

        self._repaint_delta(old_removed=old, new_added={idx})

        touch.grab(btn)
        return True

    def _on_cell_touch_move(self, btn, touch):
        if touch.grab_current is not btn or not self._dragging:
            return False

        idx = self._index_from_pos(*touch.pos)
        if idx is not None:
            self._add_to_selection(idx)
        return True

    def _on_cell_touch_up(self, btn, touch):
        if touch.grab_current is not btn:
            return False
        touch.ungrab(btn)
        if self._dragging:
            self._dragging = False
            self._finalize_selection()
        return True

    def _add_to_selection(self, idx: int):
        if idx in self._selected_set:
            return

        if self._selected_indices:
            last = self._selected_indices[-1]
            lr, lc = divmod(last, self._n)
            cr, cc = divmod(idx, self._n)
            if abs(cr - lr) + abs(cc - lc) != 1:
                return

        self._selected_indices.append(idx)
        self._selected_set.add(idx)
        self._repaint_delta(old_removed=set(), new_added={idx})

    def _finalize_selection(self):
        if len(self._selected_indices) < 3:
            self._clear_selection()
            return

        letters = [self.letters_grid[i] for i in self._selected_indices]
        s = "".join(letters)
        s_rev = s[::-1]

        matched = s if s in self.target_set else (s_rev if s_rev in self.target_set else None)
        if matched and matched not in self.found_words:
            self.found_words.add(matched)
            self._found_paths.append(list(self._selected_indices))
            self._found_cells_cache.update(self._selected_indices)

            self._refresh_words_ui()
            self._update_status()

            if len(self.found_words) == len(self.target_words):
                self.show_win_popup(self.get_translation("word_search_win_text"), self.start_new_game)

        self._clear_selection()

    def on_kv_post(self, *a):
        self._ws_geom = None
        self.ids.ws_grid.bind(pos=self._invalidate_ws_geom, size=self._invalidate_ws_geom)

    def _invalidate_ws_geom(self, *a):
        self._ws_geom = None

    def _ensure_ws_geom(self):
        if self._ws_geom is not None:
            return

        grid = self.ids.ws_grid
        n = int(self._n)

        pad = self._ws_pad
        sp = self._ws_sp

        inner_w = grid.width - 2 * pad
        inner_h = grid.height - 2 * pad
        if inner_w <= 0 or inner_h <= 0:
            self._ws_geom = None
            return

        cell_w = (inner_w - sp * (n - 1)) / n
        cell_h = (inner_h - sp * (n - 1)) / n

        self._ws_geom = (pad, sp, n, n, cell_w, cell_h, grid.x, grid.y)

    def _index_from_pos(self, x, y):
        grid = self.ids.ws_grid
        if not grid.collide_point(x, y):
            return None

        self._ensure_ws_geom()
        g = self._ws_geom
        if not g:
            return None

        pad, sp, cols, rows, cell_w, cell_h, gx, gy = g

        lx = x - gx
        ly = y - gy

        local_x = lx - pad
        local_y = ly - pad
        if local_x < 0 or local_y < 0:
            return None

        col = int(local_x // (cell_w + sp))
        row_from_bottom = int(local_y // (cell_h + sp))
        if not (0 <= col < cols and 0 <= row_from_bottom < rows):
            return None

        x_in = local_x - col * (cell_w + sp)
        y_in = local_y - row_from_bottom * (cell_h + sp)
        if x_in > cell_w or y_in > cell_h:
            return None

        row = (rows - 1) - row_from_bottom
        return row * cols + col


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

        key = self.app.current_language
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

            st = self.app.stats[lang].get(ch, {"correct": 0, "wrong": 0})
            stats_text = stats_fmt.format(st["correct"], st["wrong"])

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

            st = self.app.stats[lang].get(d, {"correct": 0, "wrong": 0})
            stats_text = stats_fmt.format(st["correct"], st["wrong"])

            data.append({
                "viewclass": "ReferenceRow",
                "symbol": d,
                "stats": stats_text,
                "braille": braille_char,
                "is_header": False,
            })

        self.ids.rv.data = data

    def _refresh_stats_in_rv(self):
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
    ns_char = StringProperty("")
    reverse_letters = {}
    reverse_digits = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_number_mode = False

    def on_kv_post(self, base_widget):
        self.dot_buttons = [
            self.ids.dot1_trans, self.ids.dot2_trans, self.ids.dot3_trans,
            self.ids.dot4_trans, self.ids.dot5_trans, self.ids.dot6_trans]

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.load_braille_data()
        self.ns_char = self.get_braille_char(number_sign_dots)
        self.reverse_letters = {
            self.get_braille_char(dots): char
            for char, dots in self.braille_data.items()
        }

        self.reverse_digits = {
            self.get_braille_char(dots): digit
            for digit, dots in digits_data.items()
        }

        Clock.schedule_once(lambda dt: self.live_translate(), 0.1)

    def update_lang(self):
        super().update_lang()
        self.translator_title = self.get_translation('translator_title')
        self.input_hint = self.get_translation('input_hint')
        self.input_braille_btn = self.get_translation('input_braille_btn')
        self.confirm_btn = self.get_translation('confirm_btn')
        self.delete_btn = self.get_translation('delete_btn')
        self.copy_btn = self.get_translation('copy')

    def _contains_braille(self, s):
        return any(0x2800 <= ord(ch) <= 0x28FF for ch in s)

    def _translate_text_to_braille(self, text):
        text = text.upper()
        result = []
        in_number_mode = False

        ns = self.ns_char

        for char in text:
            if char == '\n':
                result.append('\n')
                in_number_mode = False
                continue

            if char.isdigit():
                if not in_number_mode:
                    result.append(ns)
                    in_number_mode = True
                result.append(self.get_braille_char(digits_data.get(char, [0, 0, 0, 0, 0, 0])))
                continue

            in_number_mode = False
            if char == ' ':
                result.append(chr(0x2800))
            elif char in self.braille_data:
                result.append(self.get_braille_char(self.braille_data[char]))
            else:
                result.append(char)

        return ''.join(result)

    def _translate_braille_to_text(self, s):
        out = []
        number_mode = False
        ns = self.ns_char

        for ch in s:
            if ch == '\n':
                out.append('\n')
                number_mode = False
                continue

            if ch == ' ' or ord(ch) == 0x2800:
                out.append(' ')
                number_mode = False
                continue

            if not (0x2800 <= ord(ch) <= 0x28FF):
                out.append(ch)
                number_mode = False
                continue

            if ch == ns:
                number_mode = True
                continue

            decoded = '?'

            if number_mode:
                if ch in self.reverse_digits:
                    decoded = self.reverse_digits[ch]
                else:
                    decoded = self.reverse_letters.get(ch, '?')
                    number_mode = False
            else:
                decoded = self.reverse_letters.get(ch, '?')

            out.append(decoded)

        return ''.join(out)

    def live_translate(self, *args):
        raw = self.ids.input_text.text
        if raw == self._last_translated_text:
            return

        if self._contains_braille(raw):
            plain = self._translate_braille_to_text(raw)
            out_text = plain
            fs = dp(28)
            self.full_braille_text = raw
        else:
            braille_text = self._translate_text_to_braille(raw)
            self.full_braille_text = braille_text
            out_text = braille_text
            fs = dp(32)

        self._last_translated_text = raw

        output_box = self.ids.braille_output_box
        output_box.clear_widgets()

        chunk_size = 500
        chunks = [out_text[i:i + chunk_size] for i in range(0, len(out_text), chunk_size)] if out_text else []

        for chunk in chunks:
            lbl = Label(
                text=chunk,
                font_name='BrailleFont',
                font_size=fs,
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
            self.ids.input_text.insert_text(chr(0x2800))
            self.clear_braille_input()
            return

        braille_char = self.get_braille_char(list(input_dots))
        self.ids.input_text.insert_text(braille_char)
        self.clear_braille_input()

    def delete_last_char(self):
        self.ids.input_text.do_backspace()

    def clear_braille_input(self):
        self.user_braille_dots = [0] * 6
        for btn in self.dot_buttons:
            btn.background_color = (1, 1, 1, 1)

    def on_leave(self, *args):
        super().on_leave(*args)
        self.close_braille_input()


class SettingsScreen(BaseScreen):
    settings_title = StringProperty()
    language_label = StringProperty()
    difficulty_label = StringProperty()
    current_lang = StringProperty()
    current_difficulty_str = StringProperty()
    language_values = ListProperty([])
    difficulty_values = ListProperty()
    time_label = StringProperty()
    time_hint = StringProperty()
    use_stats = StringProperty()
    reset_stats_btn = StringProperty()
    reset_lessons_btn = StringProperty()
    general_settings_header = StringProperty()
    easy_mode_header = StringProperty()
    quick_review_header = StringProperty()
    medium_mode_header = StringProperty()
    mirror_mode_label = StringProperty()
    quick_mode_easy_label = StringProperty()
    quick_mode_easy_words_label = StringProperty()
    quick_mode_medium_label = StringProperty()
    quick_mode_hard_label = StringProperty()
    include_letters = StringProperty()
    include_digits = StringProperty()
    memory_game_title = StringProperty()

    def update_lang(self):
        super().update_lang()
        lang = self.app.current_language
        self.language_values = list(LANGUAGES.values())
        self.current_lang = LANGUAGES.get(lang, 'English')
        self.settings_title = self.get_translation('settings_title')
        self.language_label = self.get_translation('language_label')
        self.difficulty_label = self.get_translation('difficulty_label')
        self.use_stats = self.get_translation('use_stats')
        self.reset_stats_btn = self.get_translation('reset_stats_btn')
        self.reset_lessons_btn = self.get_translation('reset_lessons_btn')
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
        self.quick_mode_easy_label = self.get_translation('easy_level')
        self.quick_mode_easy_words_label = self.get_translation('easy_words_level')
        self.quick_mode_medium_label = self.get_translation('medium_level')
        self.quick_mode_hard_label = self.get_translation('hard_level')
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

    def toggle_quick_easy(self, v: bool):
        self.app.quick_mode_easy = v
        if (
                (not v)
                and (not self.app.quick_mode_easy_words)
                and (not self.app.quick_mode_medium)
                and (not self.app.quick_mode_hard)
        ):
            self.app.quick_mode_easy_words = True
            Clock.schedule_once(lambda dt: setattr(self.ids["quick_easy_words_sw"], "active", True), 0)
        self.app.save_settings()

    def toggle_quick_easy_words(self, v: bool):
        self.app.quick_mode_easy_words = v

        if (
                (not v)
                and (not self.app.quick_mode_easy)
                and (not self.app.quick_mode_medium)
                and (not self.app.quick_mode_hard)
        ):
            self.app.quick_mode_medium = True
            Clock.schedule_once(lambda dt: setattr(self.ids["quick_medium_sw"], "active", True), 0)

        self.app.save_settings()

    def toggle_quick_medium(self, v: bool):
        self.app.quick_mode_medium = v
        if (
                (not v)
                and (not self.app.quick_mode_easy)
                and (not self.app.quick_mode_easy_words)
                and (not self.app.quick_mode_hard)
        ):
            self.app.quick_mode_hard = True
            Clock.schedule_once(lambda dt: setattr(self.ids["quick_hard_sw"], "active", True), 0)
        self.app.save_settings()

    def toggle_quick_hard(self, v: bool):
        self.app.quick_mode_hard = v
        if (
                (not v)
                and (not self.app.quick_mode_easy)
                and (not self.app.quick_mode_easy_words)
                and (not self.app.quick_mode_medium)
        ):
            self.app.quick_mode_easy = True
            Clock.schedule_once(lambda dt: setattr(self.ids["quick_easy_sw"], "active", True), 0)
        self.app.save_settings()

    def toggle_memo_letters(self, v):
        self.toggle_mode_flag("memo_mode_letters", v, "memo_mode_digits", "memo_digits_sw")

    def toggle_memo_digits(self, v):
        self.toggle_mode_flag("memo_mode_digits", v, "memo_mode_letters", "memo_letters_sw")

    def reset_stats(self):
        lang = self.app.current_language

        def do_reset():
            self.app.stats[lang] = {}
            self.app.save_stats()

        self.show_popup(
            title=self.get_translation("reset_stats_title"),
            text=self.get_translation("reset_stats_text"),
            size=(dp(360), dp(260)),
            auto_dismiss=False,
            font_size=dp(18),
            font_name='BrailleFont',
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

    def reset_lessons_progress(self):
        def do_reset():
            lang = self.app.current_language

            for key in (lang, "digits_common"):
                if key in self.app.lessons_progress:
                    self.app.lessons_progress[key] = {"completed_count": 0, "progress": {}}

            self.app.save_lessons_progress()

            if "lessons" in self.app._loaded_screens:
                scr = self.app.get_screen("lessons")
                scr._built_key = None
                scr.refresh_lessons(force=True)

        self.show_popup(
            title=self.get_translation("reset_lessons_title"),
            text=self.get_translation("reset_lessons_text"),
            size=(dp(360), dp(260)),
            auto_dismiss=False,
            font_size=dp(18),
            font_name='BrailleFont',
            text_width=dp(320),
            buttons=[
                (self.get_translation("yes"), do_reset),
                (self.get_translation("no"), None),
            ],
            buttons_height=dp(60),
            buttons_spacing=dp(20),
            padding=[dp(30), dp(20), dp(30), dp(20)],
            spacing=dp(20),
        )


class BrailleApp(App):
    current_language = StringProperty('en')
    current_difficulty = StringProperty('4')
    quick_review_time = NumericProperty(5)
    stats = DictProperty({})
    use_stats = BooleanProperty(True)
    quick_streak = NumericProperty(0)
    quick_active = BooleanProperty(False)
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
    quick_mode_easy = BooleanProperty(True)
    quick_mode_easy_words = BooleanProperty(True)
    quick_mode_medium = BooleanProperty(True)
    quick_mode_hard = BooleanProperty(True)
    LESSON_STARS_MAX = 5

    _screen_classes = {
        'menu': MenuScreen,
        'lessons': LessonsScreen,
        'lesson_study': LessonStudyScreen,
        'lesson_test': LessonTestScreen,
        'practice_levels': PracticeLevelsScreen,
        'practice': PracticeScreen,
        'easy_words_practice': EasyWordsPracticeScreen,
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
        global braille_data, translations, LANGUAGES

        braille_data = load_braille_data()
        translations, LANGUAGES = load_translations()

        print(self.user_data_dir)
        self.braille_data = braille_data
        self.load_settings()
        sm = ScreenManager()
        self._load_screen(sm, 'menu')
        Clock.schedule_once(self._deferred_init, 0.05)

        return sm

    def _deferred_init(self, dt):
        self.load_high_scores()
        self.load_lessons_progress()
        self.digits_lessons = self.build_lessons(list(digits_data.keys()), group_size=5)
        self.load_stats()
        self.load_word_list(self.current_language)
        Clock.schedule_once(self.prewarm_lessons, 0)

    def prewarm_lessons(self, dt):
        lang = self.current_language
        self.lessons_config.setdefault(lang, self.build_lessons(list(self.braille_data[lang].keys()), 5))

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

    def get_available_languages(self):
        return list(LANGUAGES.keys())

    def default_high_score_entry(self):
        return {
            'practice': 0,
            'easy_words_practice': 0,
            'medium_practice': 0,
            'hard_practice': 0,
            'quick': 0
        }

    def choose_quick_mode(self):
        enabled = []
        if self.quick_mode_easy:
            enabled.append("easy")
        if self.quick_mode_easy_words:
            enabled.append("easy_words")
        if self.quick_mode_medium:
            enabled.append("medium")
        if self.quick_mode_hard:
            enabled.append("hard")

        if not enabled:
            enabled = ["easy"]

        return random.choice(enabled)

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

        elif mode == 'easy_words':
            scr = self.get_screen('easy_words_practice')
            scr.quick_review_mode = True
            self.switch_screen('easy_words_practice')
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

            lessons.append({"mode": "study", "letters": chunk})

            lessons.append({"mode": "practice", "letters": chunk})

            learned += chunk

            if i > 0:
                lessons.append({"mode": "review", "letters": learned[:]})

        lessons.append({"mode": "exam", "letters": items})
        return lessons

    def get_lessons(self, lang, lesson_type='letters'):
        if lesson_type == 'digits':
            return self.digits_lessons
        if lang not in self.lessons_config:
            self.lessons_config[lang] = self.build_lessons(list(self.braille_data[lang].keys()), 5)
        return self.lessons_config[lang]

    def mark_lesson_completed(self, lang, idx, lesson_type, stars: int = 1):
        self.set_lesson_stars(lang, idx, lesson_type, stars)

    def load_lessons_progress(self):
        try:
            with open(self._path("lessons_progress.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.lessons_progress = data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.lessons_progress = {}

        for k, v in list(self.lessons_progress.items()):
            if not isinstance(v, dict):
                self.lessons_progress[k] = {"completed_count": 0, "progress": {}}
                continue
            v.setdefault("completed_count", 0)
            v.setdefault("progress", {})

    def _progress_key(self, lang, lesson_type):
        return "digits_common" if lesson_type == "digits" else lang

    def get_lesson_stars(self, lang: str, lesson_index, lesson_type):
        pk = self._progress_key(lang, lesson_type)
        prog = self.lessons_progress.setdefault(pk, {"completed_count": 0, "progress": {}})
        per = prog.setdefault("progress", {})
        return int(per.get(f"lesson_{lesson_index}", 0))

    def set_lesson_stars(self, lang, lesson_index, lesson_type, stars):
        pk = self._progress_key(lang, lesson_type)
        prog = self.lessons_progress.setdefault(pk, {"completed_count": 0, "progress": {}})
        per = prog.setdefault("progress", {})

        stars = max(0, min(int(stars), int(self.LESSON_STARS_MAX)))
        key = f"lesson_{lesson_index}"
        old = int(per.get(key, 0))
        if stars > old:
            per[key] = stars

        cc = 0
        while per.get(f"lesson_{cc}", 0) >= 1:
            cc += 1
        prog["completed_count"] = cc

        self.save_lessons_progress()

    def save_lessons_progress(self):
        self._atomic_json_dump("lessons_progress.json", self.lessons_progress)

    def _path(self, filename):
        return os.path.join(self.user_data_dir, filename)

    def load_word_list(self, lang):
        if lang in self.word_lists:
            return

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

    def _atomic_json_dump(self, filename, data):
        path = self._path(filename)
        tmp = path + ".tmp"

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass

        os.replace(tmp, path)

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
            self.quick_mode_easy = data.get('quick_mode_easy', True)
            self.quick_mode_easy_words = data.get('quick_mode_easy_words', True)
            self.quick_mode_medium = data.get('quick_mode_medium', True)
            self.quick_mode_hard = data.get('quick_mode_hard', True)
            self.memo_mode_letters = data.get('memo_mode_letters', True)
            self.memo_mode_digits = data.get('memo_mode_digits', True)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        if self.current_language not in braille_data:
            self.current_language = 'en'

    def save_settings(self):
        data = {
            'language': self.current_language,
            'difficulty': self.current_difficulty,
            'quick_review_time': self.quick_review_time,
            'use_stats': self.use_stats,
            'mirror_writing_mode': self.mirror_writing_mode,
            'easy_mode_letters': self.easy_mode_letters,
            'easy_mode_digits': self.easy_mode_digits,
            'medium_mode_letters': self.medium_mode_letters,
            'medium_mode_digits': self.medium_mode_digits,
            'quick_mode_easy': self.quick_mode_easy,
            'quick_mode_easy_words': self.quick_mode_easy_words,
            'quick_mode_medium': self.quick_mode_medium,
            'quick_mode_hard': self.quick_mode_hard,
            'memo_mode_letters': self.memo_mode_letters,
            'memo_mode_digits': self.memo_mode_digits,
        }
        self._atomic_json_dump("settings.json", data)

    def load_high_scores(self):
        langs = self.get_available_languages()

        try:
            with open(self._path("highscores.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        for lang in langs:
            if not isinstance(data.get(lang), dict):
                data[lang] = {}
            for key, value in self.default_high_score_entry().items():
                data[lang].setdefault(key, value)

        self.high_scores = data

    def save_high_scores(self):
        self._atomic_json_dump("highscores.json", self.high_scores)

    def load_stats(self):
        try:
            with open(self._path("stats.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        for lang in self.get_available_languages():
            data.setdefault(lang, {})

        self.stats = data

    def save_stats(self):
        if not self.use_stats:
            return
        self._atomic_json_dump("stats.json", self.stats)

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
                'easy_words_practice': 'practice_levels',
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
