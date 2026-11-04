"""
=============================================================================
             JAINAGAR CHUNAV 2026 - ANDROID MOBILE APPLICATION
 Offline Election Campaign & Voter Directory for Rajasthan Panchayat Chunav
 Candidate: Pradhyumna Nagar (प्रद्युम्न नागर)
=============================================================================
"""

import os
import sys
import webbrowser
from typing import List, Dict, Any, Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configure Kivy Window for mobile simulation on Desktop
from kivy.config import Config
Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '820')
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty,
    ListProperty, DictProperty, ObjectProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Local Modules
from database import Database
from promotion_data import CANDIDATE, generate_voter_slip_text, get_whatsapp_share_url

# Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(APP_DIR, "assets", "fonts")
REGULAR_FONT = os.path.join(FONTS_DIR, "NotoSansDevanagari-Regular.ttf")
BOLD_FONT = os.path.join(FONTS_DIR, "NotoSansDevanagari-Bold.ttf")

# Register Devanagari Hindi Fonts
if os.path.exists(REGULAR_FONT):
    LabelBase.register(name="Hindi", fn_regular=REGULAR_FONT, fn_bold=BOLD_FONT)
else:
    LabelBase.register(name="Hindi", fn_regular=None)

# Initialize Database
db = Database(os.path.join(APP_DIR, "jainagar_chunav.db"))


# =============================================================================
# KV STYLES & INTERFACE LAYOUT
# =============================================================================
KV_CODE = """
#:import dp kivy.metrics.dp

<VoterCardWidget>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(145)
    padding: [dp(12), dp(10), dp(12), dp(10)]
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: (0.97, 0.98, 1.0, 1) if root.voter_status == 'supporter' else ((0.93, 1.0, 0.93, 1) if root.voter_status == 'voted' else (1, 1, 1, 1))
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12),]
        Color:
            rgba: (0.13, 0.58, 0.95, 1) if root.voter_status == 'supporter' else ((0.18, 0.75, 0.35, 1) if root.voter_status == 'voted' else (0.85, 0.88, 0.92, 1))
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
            width: dp(1.2)

    # Top Row: Serial Badge + Ward Badge + EPIC Number
    BoxLayout:
        size_hint_y: None
        height: dp(26)
        spacing: dp(6)
        
        Label:
            text: f"#{root.serial_no}"
            font_name: "Hindi"
            font_size: "14sp"
            bold: True
            color: (1, 1, 1, 1)
            size_hint_x: None
            width: dp(45)
            canvas.before:
                Color:
                    rgba: (0.08, 0.39, 0.75, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(6),]

        Label:
            text: f"वार्ड {root.ward_number}"
            font_name: "Hindi"
            font_size: "13sp"
            color: (0.1, 0.3, 0.6, 1)
            size_hint_x: None
            width: dp(65)
            bold: True

        Widget:
            # Spacer

        Label:
            text: root.epic_number
            font_size: "13sp"
            bold: True
            color: (0.2, 0.25, 0.35, 1)
            size_hint_x: None
            width: dp(115)
            halign: "right"

    # Middle Row: Voter Name (Hindi + English)
    BoxLayout:
        size_hint_y: None
        height: dp(28)
        Label:
            text: f"{root.name_hindi} ({root.name_english})"
            font_name: "Hindi"
            font_size: "16sp"
            bold: True
            color: (0.05, 0.1, 0.2, 1)
            text_size: self.size
            valign: 'middle'
            halign: 'left'

    # Relative Row
    BoxLayout:
        size_hint_y: None
        height: dp(22)
        Label:
            text: f"{root.relative_type}: {root.relative_hindi} ({root.relative_english})"
            font_name: "Hindi"
            font_size: "13sp"
            color: (0.35, 0.4, 0.48, 1)
            text_size: self.size
            valign: 'middle'
            halign: 'left'

    # Bottom Row: House No, Age, Gender + View Slip Button
    BoxLayout:
        size_hint_y: None
        height: dp(32)
        spacing: dp(8)
        
        Label:
            text: f"मकान: {root.house_number} | आयु: {root.age} | {root.gender_hindi}"
            font_name: "Hindi"
            font_size: "12sp"
            color: (0.4, 0.45, 0.52, 1)
            text_size: self.size
            valign: 'middle'
            halign: 'left'

        Button:
            text: "वोटर पर्ची ➔"
            font_name: "Hindi"
            font_size: "13sp"
            bold: True
            size_hint_x: None
            width: dp(95)
            background_normal: ''
            background_color: (0.9, 0.32, 0.05, 1)
            color: (1, 1, 1, 1)
            on_release: root.open_slip()


<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (0.95, 0.96, 0.98, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        # Top Header Bar
        BoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(16), dp(8)]
            canvas.before:
                Color:
                    rgba: (0.08, 0.39, 0.75, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Label:
                text: "🗳️ ग्राम पंचायत जयनगर चुनाव 2026"
                font_name: "Hindi"
                font_size: "20sp"
                bold: True
                color: (1, 1, 1, 1)
                halign: "left"
                valign: "middle"
                text_size: self.size

        # Main Scrollable Content
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(14)
                spacing: dp(14)

                # Hero Campaign Banner
                Image:
                    source: root.banner_path
                    size_hint_y: None
                    height: dp(160)
                    allow_stretch: True
                    keep_ratio: True

                # Candidate Appeal Card
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(160)
                    padding: dp(12)
                    spacing: dp(4)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]
                        Color:
                            rgba: (0.9, 0.32, 0.05, 1)
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
                            width: dp(1.5)

                    Label:
                        text: "🌟 सरपंच पद हेतु लोकप्रिय उम्मीदवार"
                        font_name: "Hindi"
                        font_size: "13sp"
                        bold: True
                        color: (0.9, 0.32, 0.05, 1)
                        size_hint_y: None
                        height: dp(20)

                    Label:
                        text: "प्रद्युम्न नागर  (संरक्षक: राजेन्द्र नागर)"
                        font_name: "Hindi"
                        font_size: "18sp"
                        bold: True
                        color: (0.08, 0.39, 0.75, 1)
                        size_hint_y: None
                        height: dp(26)

                    Label:
                        text: "शिक्षित, युवा, संघर्षशील, ईमानदार, सेवाभावी उम्मीदवार"
                        font_name: "Hindi"
                        font_size: "12sp"
                        color: (0.3, 0.35, 0.4, 1)
                        size_hint_y: None
                        height: dp(18)

                    Label:
                        text: "« सबका साथ, सबका विकास — सेवा और विकास के लिए »"
                        font_name: "Hindi"
                        font_size: "12sp"
                        bold: True
                        color: (0.7, 0.2, 0.05, 1)
                        size_hint_y: None
                        height: dp(20)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(34)
                        spacing: dp(10)

                        Button:
                            text: "प्रत्याशी संकल्प पत्र ➔"
                            font_name: "Hindi"
                            font_size: "13sp"
                            bold: True
                            background_normal: ''
                            background_color: (0.08, 0.39, 0.75, 1)
                            color: (1, 1, 1, 1)
                            on_release: app.go_to_candidate()

                        Button:
                            text: "प्रचार शेयर करें 📲"
                            font_name: "Hindi"
                            font_size: "13sp"
                            bold: True
                            background_normal: ''
                            background_color: (0.18, 0.65, 0.35, 1)
                            color: (1, 1, 1, 1)
                            on_release: app.share_candidate_appeal()

                # Quick Stats Counter Card
                BoxLayout:
                    size_hint_y: None
                    height: dp(75)
                    padding: dp(8)
                    spacing: dp(8)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10),]

                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: "3,568"
                            font_size: "20sp"
                            bold: True
                            color: (0.08, 0.39, 0.75, 1)
                        Label:
                            text: "कुल मतदाता"
                            font_name: "Hindi"
                            font_size: "12sp"
                            color: (0.4, 0.45, 0.5, 1)

                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: "9"
                            font_size: "20sp"
                            bold: True
                            color: (0.9, 0.32, 0.05, 1)
                        Label:
                            text: "कुल वार्ड"
                            font_name: "Hindi"
                            font_size: "12sp"
                            color: (0.4, 0.45, 0.5, 1)

                    BoxLayout:
                        orientation: 'vertical'
                        Label:
                            text: f"{root.polled_count}"
                            font_size: "20sp"
                            bold: True
                            color: (0.18, 0.65, 0.35, 1)
                        Label:
                            text: "मतदान (वोटेड)"
                            font_name: "Hindi"
                            font_size: "12sp"
                            color: (0.4, 0.45, 0.5, 1)

                # Ward Quick Navigation Grid
                Label:
                    text: "वार्ड अनुसार मतदाता सूची (Ward Selector):"
                    font_name: "Hindi"
                    font_size: "15sp"
                    bold: True
                    color: (0.1, 0.15, 0.25, 1)
                    size_hint_y: None
                    height: dp(26)
                    halign: 'left'
                    text_size: self.size

                GridLayout:
                    cols: 3
                    size_hint_y: None
                    height: dp(150)
                    spacing: dp(10)

                    Button:
                        text: "वार्ड 1 (326)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(1)

                    Button:
                        text: "वार्ड 2 (326)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(2)

                    Button:
                        text: "वार्ड 3 (441)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(3)

                    Button:
                        text: "वार्ड 4 (440)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(4)

                    Button:
                        text: "वार्ड 5 (406)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(5)

                    Button:
                        text: "वार्ड 6 (334)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(6)

                    Button:
                        text: "वार्ड 7 (414)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(7)

                    Button:
                        text: "वार्ड 8 (419)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(8)

                    Button:
                        text: "वार्ड 9 (462)"
                        font_name: "Hindi"
                        background_normal: ''
                        background_color: (1, 1, 1, 1)
                        color: (0.08, 0.39, 0.75, 1)
                        bold: True
                        on_release: app.open_ward(9)

                # Full Search CTA Button
                Button:
                    text: "🔍 सभी 3,568 मतदाताओं में खोजें ➔"
                    font_name: "Hindi"
                    font_size: "16sp"
                    bold: True
                    size_hint_y: None
                    height: dp(50)
                    background_normal: ''
                    background_color: (0.08, 0.39, 0.75, 1)
                    color: (1, 1, 1, 1)
                    on_release: app.go_to_search()

        # Bottom Navigation Bar
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: (0.85, 0.88, 0.92, 1)
                Line:
                    points: [self.x, self.top, self.right, self.top]
                    width: dp(1)

            Button:
                text: "🏠 मुख्य"
                font_name: "Hindi"
                font_size: "13sp"
                bold: True
                color: (0.08, 0.39, 0.75, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_home()

            Button:
                text: "🔍 खोजें"
                font_name: "Hindi"
                font_size: "13sp"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_search()

            Button:
                text: "👤 प्रत्याशी"
                font_name: "Hindi"
                font_size: "13sp"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_candidate()

            Button:
                text: "📊 आँकड़े"
                font_name: "Hindi"
                font_size: "13sp"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_analytics()


<SearchScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (0.95, 0.96, 0.98, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        # Top Bar
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: [dp(10), dp(8)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: (0.08, 0.39, 0.75, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "◀"
                font_size: "18sp"
                size_hint_x: None
                width: dp(40)
                background_normal: ''
                background_color: (0.08, 0.39, 0.75, 1)
                color: (1, 1, 1, 1)
                on_release: app.go_to_home()

            Label:
                text: "मतदाता खोजें (Voter Search)"
                font_name: "Hindi"
                font_size: "18sp"
                bold: True
                color: (1, 1, 1, 1)
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        # Search Controls Card
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(105)
            padding: [dp(12), dp(8)]
            spacing: dp(6)
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size

            # Search Input Box
            TextInput:
                id: search_input
                hint_text: "नाम (हिंदी/Eng), वोटर ID, मकान नं, क्रम नं..."
                font_name: "Hindi"
                font_size: "15sp"
                size_hint_y: None
                height: dp(44)
                multiline: False
                padding: [dp(10), dp(10)]
                background_normal: ''
                background_color: (0.94, 0.95, 0.97, 1)
                on_text: root.on_search_query_change(self.text)

            # Filter Badges Row
            BoxLayout:
                size_hint_y: None
                height: dp(34)
                spacing: dp(8)

                Label:
                    text: root.filter_label_text
                    font_name: "Hindi"
                    font_size: "13sp"
                    bold: True
                    color: (0.08, 0.39, 0.75, 1)
                    text_size: self.size
                    valign: 'middle'

                Button:
                    text: "वार्ड बदलें ▾"
                    font_name: "Hindi"
                    font_size: "12sp"
                    size_hint_x: None
                    width: dp(85)
                    background_normal: ''
                    background_color: (0.9, 0.93, 0.97, 1)
                    color: (0.08, 0.39, 0.75, 1)
                    on_release: root.open_ward_selector()

                Button:
                    text: "रीसेट"
                    font_name: "Hindi"
                    font_size: "12sp"
                    size_hint_x: None
                    width: dp(55)
                    background_normal: ''
                    background_color: (0.95, 0.9, 0.9, 1)
                    color: (0.7, 0.2, 0.2, 1)
                    on_release: root.reset_filters()

        # Results Count Bar
        BoxLayout:
            size_hint_y: None
            height: dp(26)
            padding: [dp(14), 0]
            Label:
                text: root.status_text
                font_name: "Hindi"
                font_size: "12sp"
                color: (0.4, 0.45, 0.5, 1)
                text_size: self.size
                valign: 'middle'

        # Voter Cards RecycleView
        RecycleView:
            id: rv
            viewclass: 'VoterCardWidget'
            RecycleBoxLayout:
                default_size: None, dp(145)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(10)
                padding: [dp(12), dp(6), dp(12), dp(12)]

        # Bottom Bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: (0.85, 0.88, 0.92, 1)
                Line:
                    points: [self.x, self.top, self.right, self.top]
                    width: dp(1)

            Button:
                text: "🏠 मुख्य पृष्ठ"
                font_name: "Hindi"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_home()

            Button:
                text: "👤 प्रत्याशी परिचय"
                font_name: "Hindi"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_candidate()


<CandidateScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (0.95, 0.96, 0.98, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        # Top Bar
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: [dp(10), dp(8)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: (0.08, 0.39, 0.75, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "◀"
                font_size: "18sp"
                size_hint_x: None
                width: dp(40)
                background_normal: ''
                background_color: (0.08, 0.39, 0.75, 1)
                color: (1, 1, 1, 1)
                on_release: app.go_to_home()

            Label:
                text: "प्रत्याशी परिचय व संकल्प पत्र"
                font_name: "Hindi"
                font_size: "18sp"
                bold: True
                color: (1, 1, 1, 1)
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(14)
                spacing: dp(14)

                # Candidate Photo + Title Header
                BoxLayout:
                    size_hint_y: None
                    height: dp(145)
                    spacing: dp(14)
                    padding: dp(10)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(12),]

                    Image:
                        source: root.photo_path
                        size_hint_x: None
                        width: dp(105)
                        allow_stretch: True
                        keep_ratio: True

                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(3)
                        Label:
                            text: "प्रद्युम्न नागर"
                            font_name: "Hindi"
                            font_size: "22sp"
                            bold: True
                            color: (0.68, 0.08, 0.34, 1)
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "संरक्षक: श्री राजेन्द्र नागर"
                            font_name: "Hindi"
                            font_size: "14sp"
                            bold: True
                            color: (0.08, 0.39, 0.75, 1)
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "सरपंच पद हेतु लोकप्रिय उम्मीदवार"
                            font_name: "Hindi"
                            font_size: "13sp"
                            bold: True
                            color: (0.9, 0.32, 0.05, 1)
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "ग्राम पंचायत जयनगर"
                            font_name: "Hindi"
                            font_size: "13sp"
                            color: (0.2, 0.25, 0.3, 1)
                            text_size: self.size
                            halign: 'left'
                        Label:
                            text: "हांपाहेड़ी • भौराजेड़ी • जयनगर • गोविन्दपुरा"
                            font_name: "Hindi"
                            font_size: "11sp"
                            color: (0.4, 0.45, 0.5, 1)
                            text_size: self.size
                            halign: 'left'

                # Slogan Card
                BoxLayout:
                    size_hint_y: None
                    height: dp(70)
                    padding: dp(8)
                    canvas.before:
                        Color:
                            rgba: (1, 0.96, 0.9, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(8),]
                        Color:
                            rgba: (0.9, 0.32, 0.05, 1)
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
                            width: dp(1.2)

                    Label:
                        text: "🚩 सबका साथ, सबका विकास — सेवा और विकास के लिए\\n'प्रद्युम्न नागर को अपना अमूल्य मत देकर विजयी बनावें'"
                        font_name: "Hindi"
                        font_size: "13sp"
                        bold: True
                        color: (0.8, 0.25, 0.05, 1)
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'

                # Official Campaign Poster Card
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(380)
                    padding: dp(8)
                    spacing: dp(4)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10),]
                    Label:
                        text: "📜 आधिकारिक चुनाव प्रचार पोस्टर:"
                        font_name: "Hindi"
                        font_size: "14sp"
                        bold: True
                        color: (0.08, 0.39, 0.75, 1)
                        size_hint_y: None
                        height: dp(22)
                        halign: 'left'
                        text_size: self.size
                    Image:
                        source: root.poster_path
                        size_hint_y: None
                        height: dp(340)
                        allow_stretch: True
                        keep_ratio: True

                # Manifesto Header
                Label:
                    text: "📋 प्रमुख चुनावी संकल्प (Manifesto):"
                    font_name: "Hindi"
                    font_size: "16sp"
                    bold: True
                    color: (0.1, 0.15, 0.25, 1)
                    size_hint_y: None
                    height: dp(26)
                    halign: 'left'
                    text_size: self.size

                # 6 Manifesto Points
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(330)
                    padding: dp(10)
                    spacing: dp(10)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10),]

                    Label:
                        text: "1. स्वच्छ पेयजल: हर ढाणी-वार्ड में नल-जल योजना का सुदृढ़ीकरण।"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.15, 0.2, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "2. पक्की सड़कें: मुख्य मार्गों से लेकर हर गली में सीसी रोड व पक्की नालियां।"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.15, 0.2, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "3. आधुनिक शिक्षा: सरकारी विद्यालयों में लाइब्रेरी व स्मार्ट क्लासरूम।"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.15, 0.2, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "4. स्वास्थ्य सेवाएं: उप-स्वास्थ्य केंद्र में 24 घंटे बुनियादी दवाएं व जांच।"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.15, 0.2, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "5. युवा व किसान: खेल मैदान, ओपन जिम व खाद-बीज की सुगम उपलब्धता।"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.15, 0.2, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "6. पारदर्शी पंचायत: किसी भी कार्य के लिए किसी ग्रामीण को चक्कर न काटने पड़ें।"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.15, 0.2, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                # Contact / Office Card
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(90)
                    padding: dp(10)
                    spacing: dp(4)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10),]

                    Label:
                        text: "📍 मुख्य चुनाव कार्यालय:"
                        font_name: "Hindi"
                        font_size: "13sp"
                        bold: True
                        color: (0.08, 0.39, 0.75, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "मुख्य बस स्टैंड चौराहा, ग्राम पंचायत जयनगर"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.3, 0.35, 0.4, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "📞 संपर्क / WhatsApp: 9636556851"
                        font_size: "14sp"
                        bold: True
                        color: (0.18, 0.65, 0.35, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "🤝 निवेदक: समस्त ग्राम पंचायत वासी हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा"
                        font_name: "Hindi"
                        font_size: "11sp"
                        color: (0.4, 0.45, 0.5, 1)
                        text_size: self.size
                        halign: 'left'

                # Action Buttons
                Button:
                    text: "📲 WhatsApp पर चुनाव प्रचार संदेश भेजें"
                    font_name: "Hindi"
                    font_size: "15sp"
                    bold: True
                    size_hint_y: None
                    height: dp(48)
                    background_normal: ''
                    background_color: (0.18, 0.65, 0.35, 1)
                    color: (1, 1, 1, 1)
                    on_release: app.share_candidate_appeal()

                Button:
                    text: "🔍 मतदाता सूची में नाम देखें"
                    font_name: "Hindi"
                    font_size: "15sp"
                    bold: True
                    size_hint_y: None
                    height: dp(48)
                    background_normal: ''
                    background_color: (0.08, 0.39, 0.75, 1)
                    color: (1, 1, 1, 1)
                    on_release: app.go_to_search()


<AnalyticsScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (0.95, 0.96, 0.98, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        # Top Bar
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: [dp(10), dp(8)]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: (0.08, 0.39, 0.75, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "◀"
                font_size: "18sp"
                size_hint_x: None
                width: dp(40)
                background_normal: ''
                background_color: (0.08, 0.39, 0.75, 1)
                color: (1, 1, 1, 1)
                on_release: app.go_to_home()

            Label:
                text: "वार्ड एवं मतदाता सांख्यिकी (Analytics)"
                font_name: "Hindi"
                font_size: "18sp"
                bold: True
                color: (1, 1, 1, 1)
                halign: 'left'
                valign: 'middle'
                text_size: self.size

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(14)
                spacing: dp(14)

                # Overall Summary Card
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(115)
                    padding: dp(12)
                    spacing: dp(6)
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(10),]

                    Label:
                        text: "कुल पंचायत मतदाता: 3,568"
                        font_name: "Hindi"
                        font_size: "17sp"
                        bold: True
                        color: (0.08, 0.39, 0.75, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "👨 पुरुष: 1,788 (50.1%)  |  👩 महिला: 1,779 (49.9%)"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.2, 0.25, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                    Label:
                        text: "🎂 औसत आयु: 40.6 वर्ष  |  🌟 युवा मतदाता (18-25): 709"
                        font_name: "Hindi"
                        font_size: "13sp"
                        color: (0.2, 0.25, 0.3, 1)
                        text_size: self.size
                        halign: 'left'

                # Ward Breakdown Header
                Label:
                    text: "वार्डवार मतदाता विवरण (Ward Breakdown):"
                    font_name: "Hindi"
                    font_size: "15sp"
                    bold: True
                    color: (0.1, 0.15, 0.25, 1)
                    size_hint_y: None
                    height: dp(26)
                    halign: 'left'
                    text_size: self.size

                # Ward Table Container
                BoxLayout:
                    id: ward_table_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(6)

        # Bottom Bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            canvas.before:
                Color:
                    rgba: (1, 1, 1, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: (0.85, 0.88, 0.92, 1)
                Line:
                    points: [self.x, self.top, self.right, self.top]
                    width: dp(1)

            Button:
                text: "🏠 मुख्य पृष्ठ"
                font_name: "Hindi"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_home()

            Button:
                text: "🔍 मतदाता खोजें"
                font_name: "Hindi"
                bold: True
                color: (0.3, 0.35, 0.45, 1)
                background_normal: ''
                background_color: (1, 1, 1, 1)
                on_release: app.go_to_search()
"""

Builder.load_string(KV_CODE)


# =============================================================================
# WIDGET & SCREEN IMPLEMENTATIONS
# =============================================================================
class VoterCardWidget(RecycleDataViewBehavior, BoxLayout):
    """Card item rendered inside RecycleView for fast, smooth scrolling."""
    index = NumericProperty(0)
    voter_id = NumericProperty(0)
    serial_no = NumericProperty(0)
    ward_number = NumericProperty(0)
    epic_number = StringProperty("")
    name_hindi = StringProperty("")
    name_english = StringProperty("")
    relative_type = StringProperty("पिता")
    relative_hindi = StringProperty("")
    relative_english = StringProperty("")
    house_number = StringProperty("")
    age = NumericProperty(0)
    gender_hindi = StringProperty("")
    gender_english = StringProperty("")
    voter_status = StringProperty("unmarked")

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.voter_id = data.get("id", 0)
        self.serial_no = data.get("serial_no", 0)
        self.ward_number = data.get("ward_number", 0)
        self.epic_number = data.get("epic_number", "")
        self.name_hindi = data.get("name_hindi", "")
        self.name_english = data.get("name_english", "")
        self.relative_type = data.get("relative_type", "पिता")
        self.relative_hindi = data.get("relative_hindi", "")
        self.relative_english = data.get("relative_english", "")
        self.house_number = str(data.get("house_number", ""))
        self.age = data.get("age") or 0
        self.gender_hindi = data.get("gender_hindi", "")
        self.gender_english = data.get("gender_english", "")
        self.voter_status = data.get("voter_status", "unmarked")
        return super().refresh_view_attrs(rv, index, data)

    def open_slip(self):
        App.get_running_app().show_voter_slip(self.voter_id)


class HomeScreen(Screen):
    banner_path = StringProperty(os.path.join(APP_DIR, "assets", "candidate", "candidate_banner.png"))
    polled_count = NumericProperty(0)

    def on_enter(self):
        stats = db.get_overall_stats()
        self.polled_count = stats.get("total_polled", 0)


class SearchScreen(Screen):
    status_text = StringProperty("कुल 3,568 मतदाता उपलब्ध")
    filter_label_text = StringProperty("सभी 9 वार्ड")
    current_ward = NumericProperty(0)
    current_query = StringProperty("")

    def on_enter(self):
        if not hasattr(self, "_loaded_once"):
            self._loaded_once = True
            self.refresh_search()

    def on_search_query_change(self, text):
        self.current_query = text
        # Debounced search refresh
        Clock.unschedule(self._do_search)
        Clock.schedule_once(self._do_search, 0.15)

    def _do_search(self, dt=None):
        ward_filter = self.current_ward if self.current_ward > 0 else None
        results = db.search_voters(query=self.current_query, ward=ward_filter, limit=120)
        self.ids.rv.data = results
        self.status_text = f"खोज परिणाम: {len(results)} मतदाता मिले"

    def refresh_search(self):
        self._do_search()

    def set_ward_filter(self, ward_num: int):
        self.current_ward = ward_num
        self.filter_label_text = f"वार्ड {ward_num}" if ward_num > 0 else "सभी 9 वार्ड"
        self.refresh_search()

    def reset_filters(self):
        self.ids.search_input.text = ""
        self.current_query = ""
        self.current_ward = 0
        self.filter_label_text = "सभी 9 वार्ड"
        self.refresh_search()

    def open_ward_selector(self):
        """Show ward picker modal."""
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))

        grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        popup = Popup(
            title="वार्ड चुनें (Select Ward)",
            title_font="Hindi",
            content=content,
            size_hint=(0.88, 0.55),
            auto_dismiss=True
        )

        def pick_ward(w):
            popup.dismiss()
            self.set_ward_filter(w)

        all_btn = Button(
            text="सभी 9 वार्ड (3568)",
            font_name="Hindi",
            size_hint_y=None,
            height=dp(42),
            background_normal='',
            background_color=(0.08, 0.39, 0.75, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        all_btn.bind(on_release=lambda x: pick_ward(0))
        content.add_widget(all_btn)

        ward_counts = [326, 326, 441, 440, 406, 334, 414, 419, 462]
        for w in range(1, 10):
            btn = Button(
                text=f"वार्ड {w}\n({ward_counts[w-1]})",
                font_name="Hindi",
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.94, 0.95, 0.97, 1),
                color=(0.1, 0.15, 0.25, 1),
                bold=True
            )
            btn.bind(on_release=lambda x, w_val=w: pick_ward(w_val))
            grid.add_widget(btn)

        content.add_widget(grid)
        popup.open()


class CandidateScreen(Screen):
    photo_path = StringProperty(os.path.join(APP_DIR, "assets", "candidate", "candidate_photo.png"))
    poster_path = StringProperty(os.path.join(APP_DIR, "assets", "candidate", "campaign_poster.jpg"))


class AnalyticsScreen(Screen):
    def on_enter(self):
        self.populate_ward_table()

    def populate_ward_table(self):
        container = self.ids.ward_table_container
        container.clear_widgets()

        wards = db.get_ward_summary()
        for w in wards:
            box = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(10), dp(6)], spacing=dp(8))
            # Background
            with box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(8),])

            lbl_w = Label(
                text=f"वार्ड {w['ward_number']}",
                font_name="Hindi",
                font_size="15sp",
                bold=True,
                color=(0.08, 0.39, 0.75, 1),
                size_hint_x=None,
                width=dp(70)
            )

            lbl_stats = Label(
                text=f"कुल: {w['total_voters']}  (पुरुष: {w['male_count']} | महिला: {w['female_count']})",
                font_name="Hindi",
                font_size="13sp",
                color=(0.2, 0.25, 0.3, 1),
                halign='left',
                valign='middle'
            )
            lbl_stats.bind(size=lbl_stats.setter('text_size'))

            box.add_widget(lbl_w)
            box.add_widget(lbl_stats)
            container.add_widget(box)


# =============================================================================
# MAIN APPLICATION CONTROLLER
# =============================================================================
class JainagarChunavApp(App):
    title = "JAINAGAR CHUNAV 2026"
    icon = os.path.join(APP_DIR, "assets", "candidate", "app_icon.png")

    def build(self):
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        self.home_screen = HomeScreen(name="home")
        self.search_screen = SearchScreen(name="search")
        self.candidate_screen = CandidateScreen(name="candidate")
        self.analytics_screen = AnalyticsScreen(name="analytics")

        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.search_screen)
        self.sm.add_widget(self.candidate_screen)
        self.sm.add_widget(self.analytics_screen)

        return self.sm

    def go_to_home(self):
        self.sm.transition.direction = "right"
        self.sm.current = "home"

    def go_to_search(self):
        self.sm.transition.direction = "left"
        self.sm.current = "search"

    def go_to_candidate(self):
        self.sm.transition.direction = "left"
        self.sm.current = "candidate"

    def go_to_analytics(self):
        self.sm.transition.direction = "left"
        self.sm.current = "analytics"

    def open_ward(self, ward_num: int):
        self.search_screen.set_ward_filter(ward_num)
        self.go_to_search()

    def share_candidate_appeal(self):
        """Open universal WhatsApp share appeal for Pradhyumna Nagar."""
        msg = f"""🌟 *ग्राम पंचायत जयनगर चुनाव 2026* 🌟
*(हांपाहेड़ी, भौराजेड़ी, जयनगर, गोविन्दपुरा)*
━━━━━━━━━━━━━━━━━━
🤝 *सरपंच पद प्रत्याशी: {CANDIDATE['name_hindi']}*
*(संरक्षक: {CANDIDATE['mentor_hindi']})*
🚩 *नारा:* "{CANDIDATE['slogan']}"
✨ *{CANDIDATE['tagline']}*

📋 *हमारा संकल्प — विकसित जयनगर:*
✔ 100% शुद्ध पेयजल (हर घर नल-जल योजना)
✔ पक्की सीसी सड़कें व सुरक्षित जल निकासी
✔ स्कूलों में आधुनिक शिक्षा व लाइब्रेरी सुविधा
✔ 24x7 प्राथमिक चिकित्सा व स्वास्थ्य सेवाएं
✔ युवाओं के लिए खेल मैदान, ओपन जिम व रोजगार मार्गदर्शन
✔ पारदर्शी, ईमानदार व जनहितैषी ग्राम पंचायत प्रशासन

📍 मुख्य कार्यालय: {CANDIDATE['office']}
📞 संपर्क सूत्र: {CANDIDATE['phone']}

🙏 *आप सभी ग्रामवासियों से प्रद्युम्न नागर को अपना अमूल्य मत एवं समर्थन देकर भारी मतों से विजयी बनाने की विनम्र अपील!*
🤝 *निवेदक:* {CANDIDATE['nivedak']}"""
        import urllib.parse
        url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg)}"
        webbrowser.open(url)

    def show_voter_slip(self, voter_id: int):
        """Show full digital voter slip dialog with candidate footer and WhatsApp share."""
        v = db.get_voter_by_id(voter_id)
        if not v:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12))

        # Voter Slip Card Container
        slip_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(280), padding=dp(10), spacing=dp(5))
        with slip_box.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=slip_box.pos, size=slip_box.size, radius=[dp(10),])
            Color(0.08, 0.39, 0.75, 1)
            Line(rounded_rectangle=[slip_box.x, slip_box.y, slip_box.width, slip_box.height, dp(10)], width=dp(1.5))

        # Title
        t_lbl = Label(
            text="📋 ग्राम पंचायत जयनगर - मतदाता पर्ची 2026",
            font_name="Hindi",
            font_size="15sp",
            bold=True,
            color=(0.08, 0.39, 0.75, 1),
            size_hint_y=None,
            height=dp(24)
        )
        slip_box.add_widget(t_lbl)

        # Field lines
        fields = [
            f"• ग्राम पंचायत: {v.get('panchayat_name', 'जयनगर')} | वार्ड नं: {v.get('ward_number')}",
            f"• क्रम संख्या (Serial No): #{v.get('serial_no')}",
            f"• मतदाता का नाम: {v.get('name_hindi')} ({v.get('name_english')})",
            f"• {v.get('relative_type', 'पिता')}: {v.get('relative_hindi')} ({v.get('relative_english')})",
            f"• पहचान पत्र (EPIC): {v.get('epic_number')}",
            f"• मकान संख्या: {v.get('house_number')} | आयु: {v.get('age')} वर्ष | लिंग: {v.get('gender_hindi')}",
            f"• मतदान केंद्र: राजकीय विद्यालय, जयनगर"
        ]

        for f_text in fields:
            lbl = Label(
                text=f_text,
                font_name="Hindi",
                font_size="12sp",
                color=(0.15, 0.2, 0.25, 1),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            lbl.bind(size=lbl.setter('text_size'))
            slip_box.add_widget(lbl)

        # Candidate branding banner inside slip
        c_banner = BoxLayout(size_hint_y=None, height=dp(52), orientation='vertical', padding=dp(3))
        with c_banner.canvas.before:
            Color(0.9, 0.32, 0.05, 0.12)
            RoundedRectangle(pos=c_banner.pos, size=c_banner.size, radius=[dp(6),])

        c_banner.add_widget(Label(
            text="🌟 सौजन्य: प्रद्युम्न नागर (सरपंच पद प्रत्याशी) 🌟",
            font_name="Hindi",
            font_size="12sp",
            bold=True,
            color=(0.9, 0.32, 0.05, 1)
        ))
        c_banner.add_widget(Label(
            text="संरक्षक: श्री राजेन्द्र नागर  |  Mob: 9636556851",
            font_name="Hindi",
            font_size="11sp",
            bold=True,
            color=(0.08, 0.39, 0.75, 1)
        ))
        c_banner.add_widget(Label(
            text="« सबका साथ, सबका विकास — सेवा और विकास के लिए »",
            font_name="Hindi",
            font_size="10sp",
            color=(0.2, 0.25, 0.3, 1)
        ))
        slip_box.add_widget(c_banner)

        content.add_widget(slip_box)

        # Karyakarta Status Marking Buttons
        status_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))

        voted_btn = Button(
            text="✔ मतदान किया",
            font_name="Hindi",
            font_size="12sp",
            bold=True,
            background_normal='',
            background_color=(0.18, 0.75, 0.35, 1) if v.get('voter_status') == 'voted' else (0.85, 0.88, 0.92, 1),
            color=(1, 1, 1, 1) if v.get('voter_status') == 'voted' else (0.2, 0.25, 0.3, 1)
        )

        supporter_btn = Button(
            text="⭐ समर्थक",
            font_name="Hindi",
            font_size="12sp",
            bold=True,
            background_normal='',
            background_color=(0.13, 0.58, 0.95, 1) if v.get('voter_status') == 'supporter' else (0.85, 0.88, 0.92, 1),
            color=(1, 1, 1, 1) if v.get('voter_status') == 'supporter' else (0.2, 0.25, 0.3, 1)
        )

        popup = Popup(
            title=f"मतदाता पर्ची - #{v.get('serial_no')} {v.get('name_hindi')}",
            title_font="Hindi",
            content=content,
            size_hint=(0.94, 0.78),
            auto_dismiss=True
        )

        def mark_status(new_stat):
            curr = v.get('voter_status')
            set_stat = "unmarked" if curr == new_stat else new_stat
            db.update_voter_status(v['id'], set_stat)
            popup.dismiss()
            self.search_screen.refresh_search()
            self.home_screen.on_enter()

        voted_btn.bind(on_release=lambda x: mark_status('voted'))
        supporter_btn.bind(on_release=lambda x: mark_status('supporter'))
        status_row.add_widget(voted_btn)
        status_row.add_widget(supporter_btn)
        content.add_widget(status_row)

        # WhatsApp Share Button
        share_btn = Button(
            text="📲 WhatsApp पर मतदाता पर्ची भेजें",
            font_name="Hindi",
            font_size="14sp",
            bold=True,
            size_hint_y=None,
            height=dp(44),
            background_normal='',
            background_color=(0.18, 0.65, 0.35, 1),
            color=(1, 1, 1, 1)
        )

        def do_share(instance):
            url = get_whatsapp_share_url(v)
            webbrowser.open(url)

        share_btn.bind(on_release=do_share)
        content.add_widget(share_btn)

        # Close button
        close_btn = Button(
            text="बंद करें (Close)",
            font_name="Hindi",
            font_size="13sp",
            size_hint_y=None,
            height=dp(36),
            background_normal='',
            background_color=(0.9, 0.92, 0.95, 1),
            color=(0.2, 0.25, 0.3, 1)
        )
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()


if __name__ == "__main__":
    JainagarChunavApp().run()
