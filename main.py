# main.py
# Personal Trading Analyzer - Kivy mobile app

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
import threading

from core_logic import analyze

# ---- Color palette ----
BG_DARK = (0.07, 0.09, 0.12, 1)      # near-black navy
CARD_BG = (0.12, 0.14, 0.18, 1)
ACCENT = (0.30, 0.65, 0.95, 1)       # blue accent
GREEN = (0.20, 0.78, 0.45, 1)
RED = (0.92, 0.30, 0.30, 1)
GREY = (0.55, 0.58, 0.62, 1)
TEXT_PRIMARY = (0.95, 0.96, 0.97, 1)
TEXT_SECONDARY = (0.65, 0.68, 0.72, 1)

Window.clearcolor = BG_DARK


class RoundedCard(BoxLayout):
    """A simple card with rounded background, used as a container."""
    def __init__(self, bg_color=CARD_BG, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def make_label(text, size_sp=16, color=TEXT_PRIMARY, bold=False, halign='left'):
    lbl = Label(
        text=text,
        font_size=f"{size_sp}sp",
        color=color,
        bold=bold,
        halign=halign,
        valign='middle',
        size_hint_y=None,
    )
    lbl.bind(width=lambda *_: lbl.setter('text_size')(lbl, (lbl.width, None)))
    lbl.bind(texture_size=lambda *_: lbl.setter('height')(lbl, lbl.texture_size[1] + dp(4)))
    return lbl


class PillButton(Button):
    """Flat button with rounded background and no default Kivy styling."""
    def __init__(self, bg_color=ACCENT, text_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        self.font_size = "16sp"
        self.bold = True
        self.size_hint_y = None
        self.height = dp(52)
        self._bg_color = bg_color
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ===================== HOME SCREEN =====================
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))

        title = make_label("Trading Analyzer", size_sp=28, bold=True)
        subtitle = make_label("Stocks & Forex — quick technical signal", size_sp=14, color=TEXT_SECONDARY)
        root.add_widget(title)
        root.add_widget(subtitle)
        root.add_widget(BoxLayout(size_hint_y=None, height=dp(12)))  # spacer

        btn_stocks = PillButton(text="Indian Stocks", bg_color=ACCENT)
        btn_stocks.bind(on_release=lambda *_: self.go_to_input('stock'))

        btn_forex = PillButton(text="Forex Pairs", bg_color=(0.45, 0.35, 0.85, 1))
        btn_forex.bind(on_release=lambda *_: self.go_to_input('forex'))

        root.add_widget(btn_stocks)
        root.add_widget(btn_forex)

        root.add_widget(BoxLayout())  # flexible spacer pushes footer down

        footer = make_label(
            "Disclaimer: Educational tool only, not financial advice.",
            size_sp=12, color=TEXT_SECONDARY
        )
        root.add_widget(footer)

        self.add_widget(root)

    def go_to_input(self, mode):
        self.manager.get_screen('input').set_mode(mode)
        self.manager.current = 'input'


# ===================== INPUT SCREEN =====================
class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'stock'
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(14))
        self.add_widget(self.root_layout)
        self._build_static()

    def _build_static(self):
        self.title_label = make_label("Indian Stocks", size_sp=24, bold=True)
        self.hint_label = make_label("", size_sp=13, color=TEXT_SECONDARY)

        self.text_input = TextInput(
            hint_text="e.g. RELIANCE.NS",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size="18sp",
            background_color=(0.15, 0.17, 0.21, 1),
            foreground_color=TEXT_PRIMARY,
            cursor_color=ACCENT,
            padding=[dp(14), dp(14), dp(14), dp(14)],
        )

        self.analyze_btn = PillButton(text="Analyze", bg_color=GREEN)
        self.analyze_btn.bind(on_release=self.on_analyze)

        self.back_btn = PillButton(text="Back", bg_color=(0.2, 0.22, 0.26, 1))
        self.back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))

        self.status_label = make_label("", size_sp=13, color=TEXT_SECONDARY)

        for w in [self.title_label, self.hint_label, self.text_input,
                  self.analyze_btn, self.status_label, self.back_btn]:
            self.root_layout.add_widget(w)

    def set_mode(self, mode):
        self.mode = mode
        self.status_label.text = ""
        self.text_input.text = ""
        if mode == 'stock':
            self.title_label.text = "Indian Stocks"
            self.hint_label.text = "Examples: RELIANCE.NS  |  SBIN.NS  |  TATAMOTORS.NS"
            self.text_input.hint_text = "e.g. RELIANCE.NS"
        else:
            self.title_label.text = "Forex Pairs"
            self.hint_label.text = "Examples: INR=X  |  EURUSD=X  |  GBPUSD=X"
            self.text_input.hint_text = "e.g. EURUSD=X"

    def on_analyze(self, *args):
        ticker = self.text_input.text.strip().upper()
        if not ticker:
            self.status_label.text = "Symbol daalein pehle."
            self.status_label.color = RED
            return

        self.status_label.text = "Fetching data..."
        self.status_label.color = TEXT_SECONDARY
        self.analyze_btn.disabled = True

        is_forex = (self.mode == 'forex')
        thread = threading.Thread(target=self._run_analysis, args=(ticker, is_forex))
        thread.daemon = True
        thread.start()

    def _run_analysis(self, ticker, is_forex):
        result = analyze(ticker, is_forex=is_forex)
        self._on_result(result, ticker)

    @mainthread
    def _on_result(self, result, ticker):
        self.analyze_btn.disabled = False
        if "error" in result:
            self.status_label.text = result["error"]
            self.status_label.color = RED
            return
        self.status_label.text = ""
        result_screen = self.manager.get_screen('result')
        result_screen.show_result(result)
        self.manager.current = 'result'


# ===================== RESULT SCREEN =====================
class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))
        self.add_widget(self.root_layout)

    def show_result(self, result):
        self.root_layout.clear_widgets()

        color_map = {"green": GREEN, "red": RED, "grey": GREY}
        signal_color = color_map.get(result["color"], GREY)

        ticker_label = make_label(result["ticker"], size_sp=22, bold=True)
        self.root_layout.add_widget(ticker_label)

        # Signal banner card
        signal_card = RoundedCard(
            bg_color=(signal_color[0], signal_color[1], signal_color[2], 0.18),
            orientation='vertical',
            size_hint_y=None,
            height=dp(90),
            padding=dp(16),
            spacing=dp(4),
        )
        signal_label = make_label(result["signal"], size_sp=22, bold=True, color=signal_color)
        reason_label = make_label(result["reason"], size_sp=13, color=TEXT_SECONDARY)
        signal_card.add_widget(signal_label)
        signal_card.add_widget(reason_label)
        self.root_layout.add_widget(signal_card)

        # Metrics card
        metrics_card = RoundedCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            padding=dp(16),
            spacing=dp(8),
        )
        metrics_card.add_widget(self._metric_row("Current Price", f"{result['current_price']:,.2f}"))
        metrics_card.add_widget(self._metric_row("20-Day Trend (SMA)", f"{result['sma_20']:,.2f}"))
        metrics_card.add_widget(self._metric_row("RSI (Momentum)", f"{result['rsi']:.1f}"))
        self.root_layout.add_widget(metrics_card)

        self.root_layout.add_widget(BoxLayout())  # spacer

        disclaimer = make_label(
            "Simple technical indicator only — not financial advice. Apni research karein.",
            size_sp=12, color=TEXT_SECONDARY
        )
        self.root_layout.add_widget(disclaimer)

        again_btn = PillButton(text="Analyze Another", bg_color=ACCENT)
        again_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'input'))

        home_btn = PillButton(text="Home", bg_color=(0.2, 0.22, 0.26, 1))
        home_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))

        self.root_layout.add_widget(again_btn)
        self.root_layout.add_widget(home_btn)

    def _metric_row(self, label_text, value_text):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(32))
        row.add_widget(make_label(label_text, size_sp=14, color=TEXT_SECONDARY))
        value_lbl = make_label(value_text, size_sp=16, bold=True, halign='right')
        row.add_widget(value_lbl)
        return row


class TradingApp(App):
    def build(self):
        self.title = "Trading Analyzer"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(InputScreen(name='input'))
        sm.add_widget(ResultScreen(name='result'))
        return sm


if __name__ == '__main__':
    TradingApp().run()
