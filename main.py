from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Line, Triangle
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivymd.toast import toast
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
import urllib.request, json, threading, time, ccxt, websocket, base64

Window.softinput_mode = 'resize'

class ProButton(Button):
    btn_color = ListProperty([0.2, 0.6, 1, 1])

KV = '''
<ProButton>:
    background_normal: ""
    background_color: 0,0,0,0
    color: 1,1,1,1
    bold: True
    canvas.before:
        Color:
            rgba: self.btn_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5]

MDBoxLayout:
    orientation: "vertical"
    md_bg_color: 0.08,0.1,0.14,1
    MDBoxLayout:
        size_hint_y: None
        height: "100dp"
        padding: "10dp"
        spacing: "10dp"
        md_bg_color: 0.11,0.14,0.18,1
        MDIconButton:
            icon: "menu"
            theme_text_color: "Custom"
            text_color: 1,1,1,1
            pos_hint: {"center_y": .5}
        MDBoxLayout:
            orientation: "vertical"
            pos_hint: {"center_y": .5}
            spacing: "4dp"
            MDTextField:
                id: symbol_search
                hint_text: "Search pair"
                multiline: False
                size_hint_x: None
                width: "160dp"
                height: "30dp"
                text_color_normal: 1,1,1,1
                text_color_focus: 1,1,1,1
                line_color_normal: 0.3,0.3,0.35,1
                line_color_focus: 0.18,0.85,0.45,1
                on_text: app.filter_symbols(self.text)
            Spinner:
                id: symbol_spinner
                text: "BTCUSDT"
                values: ["BTCUSDT"]
                size_hint: None,None
                size: "160dp","30dp"
                background_color: 0.18,0.85,0.45,1
                color: 1,1,1,1
                bold: True
                on_text: app.change_symbol(self.text)
            MDLabel:
                id: balance_label
                text: "Bal: $0.00"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.7,0.7,0.8,1
        MDLabel:
            id: live_price
            text: "Loading..."
            font_style: "H5"
            bold: True
            halign: "right"
            theme_text_color: "Custom"
            text_color: 0.18,0.85,0.45,1
    MDBottomNavigation:
        id: bottom_nav
        panel_color: 0.11,0.14,0.18,1
        selected_color_background: 0.11,0.14,0.18,1
        text_color_active: 0.9,0.7,0.1,1
        text_color_normal: 0.5,0.5,0.6,1
        MDBottomNavigationItem:
            name: 'tab_charts'
            text: 'Charts'
            icon: 'chart-box'
            MDBoxLayout:
                orientation: "vertical"
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    md_bg_color: 0.08,0.1,0.14,1
                    padding: ["10dp","5dp","10dp","5dp"]
                    spacing: "10dp"
                    ProButton:
                        id: tf_1s
                        text: "1s"
                        btn_color: 0.9,0.7,0.1,1
                        on_release: app.change_timeframe("1s")
                    ProButton:
                        id: tf_1m
                        text: "1m"
                        btn_color: 0.2,0.6,1,1
                        on_release: app.change_timeframe("1m")
                    ProButton:
                        id: tf_5m
                        text: "5m"
                        btn_color: 0.2,0.6,1,1
                        on_release: app.change_timeframe("5m")
                    ProButton:
                        id: tf_1h
                        text: "1h"
                        btn_color: 0.2,0.6,1,1
                        on_release: app.change_timeframe("1h")
                MDBoxLayout:
                    padding: "5dp"
                    canvas.before:
                        Color:
                            rgba: 0.05,0.07,0.1,1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [5]
                    Widget:
                        id: chart_widget
                MDBoxLayout:
                    size_hint_y: None
                    height: "50dp"
                    md_bg_color: 0.08,0.1,0.14,1
                    padding: ["10dp","5dp","10dp","5dp"]
                    spacing: "15dp"
                    MDIconButton:
                        icon: "arrow-left-bold"
                        theme_text_color: "Custom"
                        text_color: 0.2,0.6,1,1
                        on_release: app.pan_left()
                    MDIconButton:
                        icon: "magnify-minus-outline"
                        theme_text_color: "Custom"
                        text_color: 1,1,1,1
                        on_release: app.zoom_out()
                    MDIconButton:
                        icon: "magnify-plus-outline"
                        theme_text_color: "Custom"
                        text_color: 1,1,1,1
                        on_release: app.zoom_in()
                    MDIconButton:
                        icon: "arrow-right-bold"
                        theme_text_color: "Custom"
                        text_color: 0.2,0.6,1,1
                        on_release: app.pan_right()
                    ProButton:
                        text: "RESET"
                        size_hint_x: 1
                        btn_color: 0.18,0.85,0.45,1
                        on_release: app.reset_view()
                MDBoxLayout:
                    size_hint_y: None
                    height: "45dp"
                    md_bg_color: 0.08,0.1,0.14,1
                    padding: ["10dp","5dp","10dp","10dp"]
                    spacing: "10dp"
                    ProButton:
                        id: btn_drag_mode
                        text: "DRAG OFF"
                        size_hint_x: 0.4
                        btn_color: 0.5,0.5,0.6,1
                        on_release: app.toggle_drag_mode()
                    ProButton:
                        text: "BUY / L"
                        size_hint_x: 0.3
                        btn_color: 0.18,0.85,0.45,1
                        on_release: app.place_drag_order('buy')
                    ProButton:
                        text: "SELL / S"
                        size_hint_x: 0.3
                        btn_color: 0.85,0.2,0.25,1
                        on_release: app.place_drag_order('sell')
        MDBottomNavigationItem:
            name: 'tab_trade'
            text: 'Trade'
            icon: 'swap-horizontal'
            MDBoxLayout:
                orientation: "vertical"
                padding: "15dp"
                spacing: "15dp"
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    spacing: "10dp"
                    MDLabel:
                        text: "MARGIN / LEV:"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5,0.5,0.6,1
                        size_hint_x: 0.4
                    MDTextField:
                        id: trade_qty_input
                        text: "15"
                        hint_text: "Margin $"
                        text_color_normal: 1,1,1,1
                        size_hint_x: 0.3
                    MDTextField:
                        id: leverage_input
                        text: "10"
                        hint_text: "Leverage"
                        text_color_normal: 1,1,1,1
                        size_hint_x: 0.3
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    spacing: "10dp"
                    MDLabel:
                        text: "ENTRY PRICE:"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5,0.5,0.6,1
                        size_hint_x: 0.4
                    MDTextField:
                        id: entry_price_input
                        hint_text: "Live if empty"
                        text_color_normal: 1,1,1,1
                        size_hint_x: 0.6
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    spacing: "10dp"
                    MDLabel:
                        text: "SL / TP POINTS:"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.5,0.5,0.6,1
                        size_hint_x: 0.4
                    MDTextField:
                        id: sl_points_input
                        text: "50"
                        hint_text: "SL"
                        text_color_normal: 1,1,1,1
                        size_hint_x: 0.3
                    MDTextField:
                        id: tp_points_input
                        text: "100"
                        hint_text: "TP"
                        text_color_normal: 1,1,1,1
                        size_hint_x: 0.3
                MDBoxLayout:
                    size_hint_y: None
                    height: "50dp"
                    spacing: "15dp"
                    ProButton:
                        text: "BUY LIMIT"
                        btn_color: 0.18,0.85,0.45,1
                        on_release: app.place_manual_order('buy')
                    ProButton:
                        text: "SELL LIMIT"
                        btn_color: 0.85,0.2,0.25,1
                        on_release: app.place_manual_order('sell')
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    spacing: "15dp"
                    ProButton:
                        text: "CANCEL PENDING / CLOSE POS"
                        btn_color: 0.5,0.5,0.6,1
                        on_release: app.clear_manual_orders()
                MDBoxLayout:
                    size_hint_y: None
                    height: "40dp"
                    spacing: "15dp"
                    ProButton:
                        id: btn_start_bot
                        text: "START AUTO BOT"
                        btn_color: 0.2,0.6,1,1
                        on_release: app.start_bot()
                    ProButton:
                        id: btn_stop_bot
                        text: "STOP AUTO"
                        btn_color: 0.85,0.2,0.25,1
                        on_release: app.stop_bot()
                TextInput:
                    id: bot_code_input
                    multiline: True
                    text: ""
                    background_color: 0.05,0.07,0.1,1
                    foreground_color: 0.8,0.9,1,1
        MDBottomNavigationItem:
            name: 'tab_home'
            text: 'Logs'
            icon: 'console-line'
            MDBoxLayout:
                orientation: "vertical"
                padding: "10dp"
                spacing: "10dp"
                MDBoxLayout:
                    size_hint_y: None
                    height: "70dp"
                    md_bg_color: 0.11,0.14,0.18,1
                    padding: ["15dp","5dp","15dp","5dp"]
                    orientation: "vertical"
                    canvas.before:
                        Color:
                            rgba: 0.2,0.6,1,0.1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    MDLabel:
                        id: bot_status_label
                        text: "BOT STATUS: IDLE"
                        font_style: "Caption"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.5,0.5,0.6,1
                    MDBoxLayout:
                        MDLabel:
                            id: pos_side
                            text: "NONE"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,1
                        MDLabel:
                            id: pos_entry
                            text: "Entry: --"
                            theme_text_color: "Custom"
                            text_color: 0.8,0.8,0.8,1
                        MDLabel:
                            id: pos_pnl
                            text: "PnL: $0.00"
                            bold: True
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.5,0.5,0.6,1
                MDBoxLayout:
                    orientation: "vertical"
                    MDBoxLayout:
                        size_hint_y: None
                        height: "20dp"
                        MDLabel:
                            text: "LIVE LOGS"
                            font_style: "Caption"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.5,0.5,0.6,1
                        MDTextButton:
                            text: "CLEAR"
                            theme_text_color: "Custom"
                            text_color: 0.85,0.2,0.25,1
                            on_release: app.clear_logs()
                    TextInput:
                        id: log_console
                        multiline: True
                        text: ">>> TERMINAL READY...\\n"
                        background_color: 0.05,0.07,0.1,1
                        foreground_color: 0.18,0.85,0.45,1
                        font_size: "12sp"
        MDBottomNavigationItem:
            name: 'tab_markets'
            text: 'Settings'
            icon: 'cog'
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "15dp"
                MDLabel:
                    text: "API SETTINGS"
                    font_style: "H6"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1
                MDBoxLayout:
                    size_hint_y: None
                    height: "50dp"
                    MDLabel:
                        text: "DEMO TRADING MODE"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.9,0.7,0.1,1
                    MDSwitch:
                        id: demo_mode_switch
                        active: False
                        on_active: app.toggle_demo_mode(self.active)
                MDTextField:
                    id: api_key_input
                    hint_text: "API Key"
                    text_color_normal: 1,1,1,1
                MDTextField:
                    id: api_secret_input
                    hint_text: "API Secret"
                    password: True
                    text_color_normal: 1,1,1,1
                ProButton:
                    text: "SAVE & CONNECT"
                    btn_color: 0.2,0.6,1,1
                    size_hint_y: None
                    height: "45dp"
                    on_release: app.save_api()
                Widget:
'''

class CyberBotApp(MDApp):
    exchange = None
    market_type = 'future'
    demo_mode = BooleanProperty(False)
    demo_side = StringProperty("NONE")
    demo_balance = NumericProperty(10000.0)
    demo_entry_price = 0.0
    active_margin = 0.0
    ui_ws_app = None
    ui_viewing_symbol = "BTCUSDT"
    current_timeframe = "1s"
    all_symbols = []
    filtered_symbols = []
    symbol_search_text = ""
    all_candles = []
    visible_points = 180
    min_visible_points = 60
    max_visible_points = 1200
    view_offset = 0
    sr_zones = []
    trend_lines = []
    trade_signals = []
    bot_running = False
    bot_symbol = None
    bot_price = 0.0
    bot_ws_app = None
    last_ws_price_time = 0.0
    trade_cooldown = 3
    last_trade_time = 0.0
    current_position = 0.0
    bot_memory = {}
    visual_order = {'active': False, 'type': None, 'entry': 0.0, 'sl': 0.0, 'tp': 0.0, 'qty': 0.0}
    active_trade_sl = 0.0
    active_trade_tp = 0.0
    visual_drag_active = False
    drag_entry_price = 0.0
    chart_y_start = 0
    chart_y_end = 0
    chart_min_p = 0
    chart_price_diff = 0
    CRYPT_KEY = "CYBER_BOT_SECURE_VAULT_2026"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.store = JsonStore('bot_settings.json')
        return Builder.load_string(KV)

    def xor_cipher(self, text):
        return "".join(chr(ord(c) ^ ord(k)) for c, k in zip(text, self.CRYPT_KEY * (len(text)//len(self.CRYPT_KEY)+1)))

    def encrypt_key(self, text):
        return base64.b64encode(self.xor_cipher(text).encode()).decode() if text else ""

    def decrypt_key(self, hidden_text):
        if not hidden_text: return ""
        try: return self.xor_cipher(base64.b64decode(hidden_text.encode()).decode())
        except: return ""

    def on_start(self):
        chart = self.root.ids.chart_widget
        chart.bind(on_touch_down=self.on_chart_touch_down)
        chart.bind(on_touch_move=self.on_chart_touch_move)
        threading.Thread(target=self.fetch_all_binance_pairs, daemon=True).start()
        if self.store.exists('settings'):
            saved_data = self.store.get('settings')
            api_key = self.decrypt_key(saved_data.get('api_key', ''))
            api_secret = self.decrypt_key(saved_data.get('api_secret', ''))
            if api_key and api_secret:
                self.root.ids.api_key_input.text = api_key
                self.root.ids.api_secret_input.text = api_secret
                self.save_api()
        self.fetch_historical_data(self.ui_viewing_symbol, self.current_timeframe)
        threading.Thread(target=self.manual_trading_tracker, daemon=True).start()
        self.update_balance_display()

    def log_msg(self, msg):
        def _append(dt):
            try:
                console = self.root.ids.log_console
                console.text += f"[{time.strftime('%H:%M:%S')}] {msg}\n"
                lines = console.text.split('\n')
                if len(lines) > 100: console.text = '\n'.join(lines[-100:])
            except: pass
        Clock.schedule_once(_append)

    def clear_logs(self):
        self.root.ids.log_console.text = ">>> CYBER BOT TERMINAL CLEARED...\n"

    def toggle_demo_mode(self, active):
        self.demo_mode = active
        self.update_balance_display()
        self.log_msg(f"SYSTEM: Switched to {'DEMO' if active else 'LIVE'} Mode")

    def update_balance_display(self):
        if self.demo_mode:
            self.root.ids.balance_label.text = f"Demo Bal: ${self.demo_balance:,.2f}"
            self.root.ids.balance_label.text_color = [0.9,0.7,0.1,1]
        elif self.exchange:
            self.root.ids.balance_label.text_color = [0.7,0.7,0.8,1]
        else:
            self.root.ids.balance_label.text = "Bal: Not Connected"

    def update_dashboard(self, usdt_bal):
        if not self.demo_mode:
            self.root.ids.balance_label.text = f"Bal: ${usdt_bal:,.2f}"
        self.log_msg("CONNECTED TO BINANCE")

    def change_timeframe(self, tf):
        self.current_timeframe = tf
        colors = {"1s": [0.2,0.6,1,1], "1m": [0.2,0.6,1,1], "5m": [0.2,0.6,1,1], "1h": [0.2,0.6,1,1]}
        colors[tf] = [0.9,0.7,0.1,1]
        self.root.ids.tf_1s.btn_color = colors["1s"]
        self.root.ids.tf_1m.btn_color = colors["1m"]
        self.root.ids.tf_5m.btn_color = colors["5m"]
        self.root.ids.tf_1h.btn_color = colors["1h"]
        if self.ui_ws_app:
            self.ui_ws_app.close()
            self.ui_ws_app = None
        self.fetch_historical_data(self.ui_viewing_symbol, tf)

    def change_symbol(self, new_symbol):
        if new_symbol == "NO MATCH": return
        if self.ui_ws_app:
            self.ui_ws_app.close()
            self.ui_ws_app = None
        self.root.ids.live_price.text = "Loading..."
        self.bot_symbol = new_symbol
        self.fetch_historical_data(new_symbol, self.current_timeframe)

    def toggle_drag_mode(self):
        self.visual_drag_active = not self.visual_drag_active
        btn = self.root.ids.btn_drag_mode
        if self.visual_drag_active:
            btn.text = "DRAG ON"
            btn.btn_color = [0.9,0.7,0.1,1]
            self.drag_entry_price = self.bot_price
        else:
            btn.text = "DRAG OFF"
            btn.btn_color = [0.5,0.5,0.6,1]
        self._draw_chart()

    def on_chart_touch_down(self, instance, touch):
        if not self.visual_drag_active: return False
        if instance.collide_point(*touch.pos):
            self.update_drag_price(touch.y)
            return True
        return False

    def on_chart_touch_move(self, instance, touch):
        if not self.visual_drag_active: return False
        if instance.collide_point(*touch.pos):
            self.update_drag_price(touch.y)
            return True
        return False

    def update_drag_price(self, y):
        try:
            if self.chart_price_diff <= 0: return
            y = max(self.chart_y_start, min(self.chart_y_end, y))
            ratio = (y - self.chart_y_start) / (self.chart_y_end - self.chart_y_start)
            self.drag_entry_price = self.chart_min_p + ratio * self.chart_price_diff
            self.root.ids.entry_price_input.text = f"{self.drag_entry_price:.2f}"
            self._draw_chart()
        except: pass

    def place_drag_order(self, order_type):
        if not self.visual_drag_active:
            self.log_msg("ENABLE 'DRAG' FIRST TO SET LINE!")
            return
        self.root.ids.entry_price_input.text = f"{self.drag_entry_price:.4f}"
        self.place_manual_order(order_type)
        self.toggle_drag_mode()

    def place_manual_order(self, order_type):
        try:
            entry_str = self.root.ids.entry_price_input.text
            sl_pts = float(self.root.ids.sl_points_input.text)
            tp_pts = float(self.root.ids.tp_points_input.text)
            usd_margin = float(self.root.ids.trade_qty_input.text)
            try: leverage = float(self.root.ids.leverage_input.text)
            except: leverage = 1.0
            entry = float(entry_str) if entry_str else self.bot_price
            if entry <= 0: return
            total_trade_value = usd_margin * leverage
            coin_qty = total_trade_value / entry
            if order_type == 'buy':
                sl = entry - sl_pts
                tp = entry + tp_pts
            else:
                sl = entry + sl_pts
                tp = entry - tp_pts
            self.visual_order = {'active': True, 'type': order_type, 'entry': entry, 'sl': sl, 'tp': tp, 'qty': coin_qty}
            self.log_msg(f"PENDING {order_type.upper()} SET @ {entry} (Lev: {leverage}x)")
            self._draw_chart()
        except Exception: self.log_msg("Check your inputs.")

    def clear_manual_orders(self):
        self.visual_order['active'] = False
        self.active_trade_sl = 0.0
        self.active_trade_tp = 0.0
        self.log_msg("PENDING ORDERS CLEARED.")
        if self.current_position > 0:
            if self.demo_mode:
                if self.demo_side == "LONG":
                    self.safe_market_sell(self.current_position)
                elif self.demo_side == "SHORT":
                    self.safe_market_buy(self.current_position)
            else:
                self.safe_market_sell(self.current_position)
            self.log_msg("MANUAL CLOSE TRIGGERED.")
        self._draw_chart()

    def manual_trading_tracker(self):
        last_sync = 0
        while True:
            try:
                if time.time() - last_sync > 5:
                    self.sync_exchange_data()
                    last_sync = time.time()
                lp = self.bot_price
                if lp <= 0:
                    time.sleep(0.5)
                    continue
                if self.visual_order['active'] and self.current_position == 0:
                    vo = self.visual_order
                    if vo['type'] == 'buy' and lp <= vo['entry']:
                        if self.safe_market_buy(vo['qty']):
                            self.active_trade_sl = vo['sl']
                            self.active_trade_tp = vo['tp']
                            self.visual_order['active'] = False
                            self.log_msg(f"BUY EXECUTED @ {lp}")
                    elif vo['type'] == 'sell' and lp >= vo['entry']:
                        if self.safe_market_sell(vo['qty']):
                            self.active_trade_sl = vo['sl']
                            self.active_trade_tp = vo['tp']
                            self.visual_order['active'] = False
                            self.log_msg(f"SELL EXECUTED @ {lp}")
                if self.current_position > 0 and self.active_trade_sl > 0:
                    pos_type = self.root.ids.pos_side.text.upper()
                    if pos_type == "LONG":
                        if lp >= self.active_trade_tp:
                            self.safe_market_sell(self.current_position)
                            self.log_msg(f"TP HIT @ {lp}")
                            self.active_trade_sl = 0.0
                            self.active_trade_tp = 0.0
                        elif lp <= self.active_trade_sl:
                            self.safe_market_sell(self.current_position)
                            self.log_msg(f"SL HIT @ {lp}")
                            self.active_trade_sl = 0.0
                            self.active_trade_tp = 0.0
                    elif pos_type == "SHORT":
                        if lp <= self.active_trade_tp:
                            self.safe_market_buy(self.current_position)
                            self.log_msg(f"TP HIT @ {lp}")
                            self.active_trade_sl = 0.0
                            self.active_trade_tp = 0.0
                        elif lp >= self.active_trade_sl:
                            self.safe_market_buy(self.current_position)
                            self.log_msg(f"SL HIT @ {lp}")
                            self.active_trade_sl = 0.0
                            self.active_trade_tp = 0.0
                Clock.schedule_once(lambda dt: self._draw_chart())
            except: pass
            time.sleep(0.5)

    def fetch_historical_data(self, symbol, timeframe):
        self.ui_viewing_symbol = symbol
        self.bot_symbol = symbol
        self.root.ids.chart_widget.canvas.clear()
        self.all_candles = []
        self.view_offset = 0
        def _fetch():
            try:
                temp_history = []
                end_time = ""
                for _ in range(3):
                    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}&limit=1000"
                    if end_time: url += f"&endTime={end_time}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        data = json.loads(response.read().decode())
                        if not data: break
                        batch = [{'t': int(k[0]), 'o': float(k[1]), 'h': float(k[2]), 'l': float(k[3]), 'c': float(k[4]), 'closed': True} for k in data]
                        temp_history = batch + temp_history
                        end_time = batch[0]['t'] - 1
                self.all_candles = temp_history
                Clock.schedule_once(lambda dt: self._draw_chart())
                self.start_ui_websocket(symbol, timeframe)
            except Exception as e:
                self.log_msg(f"History fetch error: {e}")
        threading.Thread(target=_fetch, daemon=True).start()

    def start_ui_websocket(self, symbol, timeframe):
        def run_ws():
            stream_url = f"wss://stream.binance.com:9443/stream?streams={symbol.lower()}@kline_{timeframe}/{symbol.lower()}@ticker"
            def on_message(ws, message):
                try:
                    raw_data = json.loads(message)
                    stream_name = raw_data.get('stream', '')
                    data = raw_data.get('data', {})
                    if '@ticker' in stream_name:
                        live_price = float(data['c'])
                        Clock.schedule_once(lambda dt: self._update_top_price(live_price))
                    elif '@kline' in stream_name:
                        kline = data['k']
                        live_candle = {'t': int(kline['t']), 'o': float(kline['o']), 'h': float(kline['h']), 'l': float(kline['l']), 'c': float(kline['c']), 'closed': bool(kline['x'])}
                        Clock.schedule_once(lambda dt: self._update_chart_ui(live_candle))
                except: pass
            while self.ui_viewing_symbol == symbol and self.current_timeframe == timeframe:
                self.ui_ws_app = websocket.WebSocketApp(stream_url, on_message=on_message)
                self.ui_ws_app.run_forever()
                if self.ui_viewing_symbol == symbol and self.current_timeframe == timeframe:
                    time.sleep(2)
        threading.Thread(target=run_ws, daemon=True).start()

    def _update_top_price(self, price):
        try:
            self.root.ids.live_price.text = f"{price:,.4f}"
            self.bot_price = price
            self.last_ws_price_time = time.time()
            if self.demo_mode and self.current_position > 0:
                if self.demo_side == "LONG":
                    pnl = (price - self.demo_entry_price) * self.current_position
                elif self.demo_side == "SHORT":
                    pnl = (self.demo_entry_price - price) * self.current_position
                else:
                    pnl = 0.0
                self.update_pnl_ui(self.demo_side, self.demo_entry_price, pnl)
        except: pass

    def _update_chart_ui(self, candle):
        try:
            if len(self.all_candles) == 0:
                self.all_candles.append(candle)
            else:
                last_candle = self.all_candles[-1]
                if candle['t'] == last_candle['t']:
                    self.all_candles[-1] = candle
                elif candle['t'] > last_candle['t']:
                    self.all_candles.append(candle)
            if len(self.all_candles) > 3000:
                self.all_candles.pop(0)
            self._draw_chart()
        except: pass

    def zoom_in(self):
        self.visible_points = max(self.min_visible_points, int(self.visible_points * 0.8))
        self._draw_chart()

    def zoom_out(self):
        self.visible_points = min(self.max_visible_points, int(self.visible_points * 1.25))
        self.visible_points = min(self.visible_points, len(self.all_candles))
        self._draw_chart()

    def pan_left(self):
        shift = max(1, int(self.visible_points * 0.2))
        max_offset = len(self.all_candles) - self.visible_points
        if max_offset > 0:
            self.view_offset = min(max_offset, self.view_offset + shift)
            self._draw_chart()

    def pan_right(self):
        shift = max(1, int(self.visible_points * 0.2))
        self.view_offset = max(0, self.view_offset - shift)
        self._draw_chart()

    def reset_view(self):
        self.view_offset = 0
        self.visible_points = 180
        self._draw_chart()

    def _draw_chart(self):
        chart = self.root.ids.chart_widget
        chart.canvas.clear()
        total_candles = len(self.all_candles)
        if total_candles < 2: return
        end_idx = total_candles - self.view_offset
        start_idx = max(0, end_idx - self.visible_points)
        display_slice = self.all_candles[start_idx:end_idx]
        if not display_slice: return
        highs = [c['h'] for c in display_slice]
        lows = [c['l'] for c in display_slice]
        if self.visual_order['active']:
            highs.extend([self.visual_order['entry'], self.visual_order['tp'], self.visual_order['sl']])
            lows.extend([self.visual_order['entry'], self.visual_order['tp'], self.visual_order['sl']])
        if self.active_trade_sl > 0:
            highs.extend([self.active_trade_tp, self.active_trade_sl])
            lows.extend([self.active_trade_tp, self.active_trade_sl])
        max_p = max(highs)
        min_p = min(lows)
        price_diff = max_p - min_p if max_p != min_p else 1
        padding = price_diff * 0.05
        max_p += padding
        min_p -= padding
        price_diff = max_p - min_p
        x_start = chart.x + 10
        x_end = chart.right - 10
        y_start = chart.y + 10
        y_end = chart.top - 10
        self.chart_y_start = y_start
        self.chart_y_end = y_end
        self.chart_min_p = min_p
        self.chart_price_diff = price_diff
        num_points = len(display_slice)
        x_step = (x_end - x_start) / max(num_points, 1)
        candle_width = max(x_step * 0.7, 1)
        def get_y(val): return y_start + ((val - min_p) / price_diff) * (y_end - y_start)
        with chart.canvas:
            for zone in self.sr_zones:
                if min_p <= zone['price'] <= max_p:
                    top_y = get_y(zone['price'] + zone['margin'])
                    bot_y = get_y(zone['price'] - zone['margin'])
                    z_start = max(0, zone.get('start', 0) - start_idx)
                    z_end = zone.get('end', total_candles) - start_idx
                    if z_end < 0 or z_start > self.visible_points: continue
                    zx_start = max(x_start, x_start + (z_start * x_step))
                    zx_end = min(x_end, x_start + (z_end * x_step))
                    Color(*zone['color'])
                    Rectangle(pos=(zx_start, bot_y), size=(max(1, zx_end - zx_start), abs(top_y - bot_y)))
            for i, candle in enumerate(display_slice):
                o, h, l, c = candle['o'], candle['h'], candle['l'], candle['c']
                x_center = x_start + (i * x_step) + (x_step / 2)
                y_o, y_h, y_l, y_c = get_y(o), get_y(h), get_y(l), get_y(c)
                if c >= o: Color(0.18,0.85,0.45,1)
                else: Color(0.85,0.2,0.25,1)
                Line(points=[x_center, y_l, x_center, y_h], width=1)
                body_bottom = min(y_o, y_c)
                body_height = max(abs(y_o - y_c), 1)
                Rectangle(pos=(x_center - candle_width/2, body_bottom), size=(candle_width, body_height))
            for tline in self.trend_lines:
                rel_i1 = tline['x1'] - start_idx
                rel_i2 = tline['x2'] - start_idx
                x1_pos = x_start + (rel_i1 * x_step) + (x_step / 2)
                x2_pos = x_start + (rel_i2 * x_step) + (x_step / 2)
                y1_pos = get_y(tline['y1'])
                y2_pos = get_y(tline['y2'])
                Color(*tline['color'])
                Line(points=[x1_pos, y1_pos, x2_pos, y2_pos], width=1.5)
            for sig in self.trade_signals:
                if start_idx <= sig['index'] <= end_idx:
                    rel_i = sig['index'] - start_idx
                    x_center = x_start + (rel_i * x_step) + (x_step / 2)
                    if sig['type'] == 'buy':
                        y_pos = get_y(sig['price']) - 15
                        Color(0.18,0.85,0.45,1)
                        Triangle(points=[x_center, y_pos, x_center-6, y_pos-12, x_center+6, y_pos-12])
                    else:
                        y_pos = get_y(sig['price']) + 15
                        Color(0.85,0.2,0.25,1)
                        Triangle(points=[x_center, y_pos, x_center-6, y_pos+12, x_center+6, y_pos+12])
            if self.visual_order['active']:
                ey = get_y(self.visual_order['entry'])
                tpy = get_y(self.visual_order['tp'])
                sly = get_y(self.visual_order['sl'])
                Color(0.2,0.6,1,1)
                Line(points=[x_start, ey, x_end, ey], width=1.5)
                Color(0.18,0.85,0.45,1)
                Line(points=[x_start, tpy, x_end, tpy], width=1.2, dash_offset=5)
                Color(0.85,0.2,0.25,1)
                Line(points=[x_start, sly, x_end, sly], width=1.2, dash_offset=5)
            if self.active_trade_sl > 0:
                tpy = get_y(self.active_trade_tp)
                sly = get_y(self.active_trade_sl)
                Color(0.18,0.85,0.45,1)
                Line(points=[x_start, tpy, x_end, tpy], width=1.2, dash_offset=5)
                Color(0.85,0.2,0.25,1)
                Line(points=[x_start, sly, x_end, sly], width=1.2, dash_offset=5)
            if self.visual_drag_active:
                ey = get_y(self.drag_entry_price)
                Color(0.9,0.7,0.1,1)
                Line(points=[x_start, ey, x_end, ey], width=2)
                try:
                    sl_pts = float(self.root.ids.sl_points_input.text)
                    tp_pts = float(self.root.ids.tp_points_input.text)
                    tpy_buy = get_y(self.drag_entry_price + tp_pts)
                    sly_buy = get_y(self.drag_entry_price - sl_pts)
                    Color(0.18,0.85,0.45,0.5)
                    Line(points=[x_start, tpy_buy, x_end, tpy_buy], dash_offset=5)
                    Color(0.85,0.2,0.25,0.5)
                    Line(points=[x_start, sly_buy, x_end, sly_buy], dash_offset=5)
                except: pass

    def fetch_all_binance_pairs(self):
        try:
            self.log_msg("Loading symbol list...")
            req = urllib.request.Request("https://api.binance.com/api/v3/exchangeInfo", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING' and (s['symbol'].endswith('USDT') or s['symbol'].endswith('USDC') or s['symbol'].endswith('FDUSD') or s['symbol'].endswith('BUSD'))]
                symbols.sort()
                self.log_msg(f"Loaded {len(symbols)} pairs from Binance")
                Clock.schedule_once(lambda dt: self._update_spinner_values(symbols))
        except Exception as e:
            self.log_msg(f"Pair load error: {str(e)}")

    def _update_spinner_values(self, symbols):
        self.all_symbols = symbols[:]
        self.filtered_symbols = symbols[:]
        self.root.ids.symbol_spinner.values = self.filtered_symbols
        if self.ui_viewing_symbol in self.filtered_symbols:
            self.root.ids.symbol_spinner.text = self.ui_viewing_symbol
        elif self.filtered_symbols:
            self.ui_viewing_symbol = self.filtered_symbols[0]
            self.root.ids.symbol_spinner.text = self.filtered_symbols[0]

    def filter_symbols(self, text):
        q = text.strip().upper()
        self.symbol_search_text = q
        if q == "":
            self.filtered_symbols = self.all_symbols[:]
        else:
            self.filtered_symbols = [s for s in self.all_symbols if q in s]
        if not self.filtered_symbols:
            self.root.ids.symbol_spinner.values = ["NO MATCH"]
            self.root.ids.symbol_spinner.text = "NO MATCH"
            return
        self.root.ids.symbol_spinner.values = self.filtered_symbols
        self.root.ids.symbol_spinner.text = self.filtered_symbols[0]

    def to_ccxt_symbol(self, symbol):
        if not symbol: return ""
        for quote in ["USDT", "USDC", "FDUSD", "BUSD"]:
            if symbol.endswith(quote):
                return f"{symbol[:-len(quote)]}/{quote}"
        return symbol

    def sync_exchange_data(self):
        if self.demo_mode or not self.exchange or not self.bot_running: return
        try:
            ccxt_symbol = self.to_ccxt_symbol(self.bot_symbol)
            positions = self.exchange.fetch_positions([ccxt_symbol])
            found_active = False
            for p in positions:
                amt = float(p['info'].get('positionAmt', 0))
                if amt != 0:
                    entry = float(p['info'].get('entryPrice', 0))
                    upnl = float(p['info'].get('unRealizedProfit', 0))
                    side = "LONG" if amt > 0 else "SHORT"
                    self.update_pnl_ui(side, entry, upnl)
                    self.current_position = abs(amt)
                    found_active = True
                    break
            if not found_active:
                self.update_pnl_ui("NONE", 0.0, 0.0)
                self.current_position = 0.0
        except: pass

    def update_pnl_ui(self, side, entry_price, pnl_value):
        def _update(dt):
            try:
                self.root.ids.pos_side.text = str(side)
                self.root.ids.pos_entry.text = f"Entry: ${float(entry_price):,.4f}" if entry_price > 0 else "Entry: --"
                sign = "+" if pnl_value > 0 else ""
                self.root.ids.pos_pnl.text = f"PnL: {sign}${float(pnl_value):,.2f}"
                if side.upper() == "LONG": self.root.ids.pos_side.text_color = [0.18,0.85,0.45,1]
                elif side.upper() == "SHORT": self.root.ids.pos_side.text_color = [0.85,0.2,0.25,1]
                else: self.root.ids.pos_side.text_color = [1,1,1,1]
                if float(pnl_value) > 0: self.root.ids.pos_pnl.text_color = [0.18,0.85,0.45,1]
                elif float(pnl_value) < 0: self.root.ids.pos_pnl.text_color = [0.85,0.2,0.25,1]
                else: self.root.ids.pos_pnl.text_color = [0.6,0.6,0.6,1]
            except: pass
        Clock.schedule_once(_update)

    def safe_market_buy(self, amount):
        if time.time() - self.last_trade_time < self.trade_cooldown: return False
        if self.demo_mode:
            try: leverage = float(self.root.ids.leverage_input.text)
            except: leverage = 1.0
            if self.current_position > 0 and self.demo_side == "SHORT":
                pnl = (self.demo_entry_price - self.bot_price) * self.current_position
                self.demo_balance += self.active_margin + pnl
                self.log_msg(f"DEMO SHORT CLOSED. PnL: ${pnl:.2f}")
                self.current_position = 0
                self.demo_entry_price = 0
                self.active_margin = 0.0
                self.demo_side = "NONE"
                self.last_trade_time = time.time()
                self.update_balance_display()
                self.update_pnl_ui("NONE", 0, 0)
                return True
            elif self.current_position == 0:
                cost = (amount * self.bot_price) / leverage
                if cost > self.demo_balance:
                    self.log_msg("DEMO: Insufficient Balance")
                    return False
                self.demo_balance -= cost
                self.active_margin = cost
                self.demo_entry_price = self.bot_price
                self.current_position = amount
                self.demo_side = "LONG"
                self.last_trade_time = time.time()
                self.log_msg(f"DEMO LONG OPENED @ {self.bot_price} (Lev: {leverage}x)")
                self.update_balance_display()
                return True
            return False
        if self.current_position > 0: return False
        try:
            ccxt_symbol = self.to_ccxt_symbol(self.bot_symbol)
            formatted_amount = float(self.exchange.amount_to_precision(ccxt_symbol, amount))
            self.exchange.create_market_buy_order(ccxt_symbol, formatted_amount)
            self.last_trade_time = time.time()
            self.current_position += float(formatted_amount)
            self.log_msg(f"LIVE BUY EXEC: {formatted_amount} @ {self.bot_price}")
            return True
        except Exception as e:
            self.log_msg(f"Buy Error: {e}")
            return False

    def safe_market_sell(self, amount):
        if time.time() - self.last_trade_time < self.trade_cooldown: return False
        if self.demo_mode:
            try: leverage = float(self.root.ids.leverage_input.text)
            except: leverage = 1.0
            if self.current_position > 0 and self.demo_side == "LONG":
                pnl = (self.bot_price - self.demo_entry_price) * self.current_position
                self.demo_balance += self.active_margin + pnl
                self.log_msg(f"DEMO LONG CLOSED. PnL: ${pnl:.2f}")
                self.current_position = 0
                self.demo_entry_price = 0
                self.active_margin = 0.0
                self.demo_side = "NONE"
                self.last_trade_time = time.time()
                self.update_balance_display()
                self.update_pnl_ui("NONE", 0, 0)
                return True
            elif self.current_position == 0:
                cost = (amount * self.bot_price) / leverage
                if cost > self.demo_balance:
                    self.log_msg("DEMO: Insufficient Margin")
                    return False
                self.demo_balance -= cost
                self.active_margin = cost
                self.demo_entry_price = self.bot_price
                self.current_position = amount
                self.demo_side = "SHORT"
                self.last_trade_time = time.time()
                self.log_msg(f"DEMO SHORT OPENED @ {self.bot_price} (Lev: {leverage}x)")
                self.update_balance_display()
                return True
            return False
        if self.current_position <= 0: return False
        try:
            ccxt_symbol = self.to_ccxt_symbol(self.bot_symbol)
            formatted_amount = float(self.exchange.amount_to_precision(ccxt_symbol, amount))
            self.exchange.create_market_sell_order(ccxt_symbol, formatted_amount)
            self.last_trade_time = time.time()
            self.current_position -= float(formatted_amount)
            self.log_msg(f"LIVE SELL EXEC: {formatted_amount} @ {self.bot_price}")
            return True
        except Exception as e:
            self.log_msg(f"Sell Error: {e}")
            return False

    def bot_engine_loop(self):
        custom_code = self.root.ids.bot_code_input.text
        if custom_code.strip() != "":
            self.log_msg("CALCULATING HISTORY DATA...")
            self.sr_zones = []
            self.trend_lines = []
            self.trade_signals = []
            self.bot_memory = {}
            def quiet_draw_zone(zid, s_idx, e_idx, price, margin=5.0, ztype="support"):
                for z in self.sr_zones:
                    if z.get('id') == zid:
                        z['end'] = e_idx
                        return
                color = [0.18,0.85,0.45,0.25] if ztype == "support" else [0.85,0.2,0.25,0.25]
                self.sr_zones.append({'id': zid, 'start': s_idx, 'end': e_idx, 'price': price, 'margin': margin, 'color': color})
            def quiet_clear_zones(): self.sr_zones = []
            def quiet_draw_trendline(x1, y1, x2, y2, color): self.trend_lines.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'color': color})
            def quiet_clear_trendlines(): self.trend_lines = []
            def quiet_draw_signal(c_idx, price, stype="buy"): self.trade_signals.append({'index': c_idx, 'type': stype, 'price': price})
            try:
                hist_pos = 0.0
                def fake_buy(amt): nonlocal hist_pos; hist_pos += amt; return True
                def fake_sell(amt): nonlocal hist_pos; hist_pos -= amt; return True
                for i in range(len(self.all_candles)):
                    hist_slice = self.all_candles[:i+1]
                    hist_price = hist_slice[-1]['c']
                    context = {'price': hist_price, 'symbol': self.bot_symbol, 'position': hist_pos, 'trade_amount': 1.0, 'log': lambda m: None, 'buy': fake_buy, 'sell': fake_sell, 'memory': self.bot_memory, 'candles': hist_slice, 'draw_zone': quiet_draw_zone, 'clear_zones': quiet_clear_zones, 'draw_trendline': quiet_draw_trendline, 'clear_trendlines': quiet_clear_trendlines, 'draw_signal': quiet_draw_signal}
                    exec(custom_code, globals(), context)
                Clock.schedule_once(lambda dt: self._draw_chart())
                self.log_msg("HISTORY CALCULATED SUCCESSFULLY!")
            except Exception as e: self.log_msg(f"History Logic Error: {e}")
        last_sync_time = 0
        while self.bot_running:
            try:
                current_time = time.time()
                if current_time - last_sync_time > 5:
                    self.sync_exchange_data()
                    last_sync_time = current_time
                if self.bot_price > 0 and current_time - self.last_ws_price_time > 5:
                    time.sleep(2)
                    continue
                custom_code = self.root.ids.bot_code_input.text
                live_price = self.bot_price
                try: ui_usdt = float(self.root.ids.trade_qty_input.text)
                except: ui_usdt = 0.0
                try: ui_leverage = float(self.root.ids.leverage_input.text)
                except: ui_leverage = 1.0
                total_trade_value = ui_usdt * ui_leverage
                calculated_coin_qty = (total_trade_value / live_price) if live_price > 0 else 0.0
                if live_price > 0 and custom_code.strip() != "":
                    def live_zone(zid, s_idx, e_idx, price, margin=5.0, ztype="support"):
                        quiet_draw_zone(zid, s_idx, e_idx, price, margin, ztype)
                        Clock.schedule_once(lambda dt: self._draw_chart())
                    def live_clear_zones():
                        quiet_clear_zones()
                        Clock.schedule_once(lambda dt: self._draw_chart())
                    def live_tline(x1, y1, x2, y2, color):
                        quiet_draw_trendline(x1, y1, x2, y2, color)
                        Clock.schedule_once(lambda dt: self._draw_chart())
                    def live_clear_tline():
                        quiet_clear_trendlines()
                        Clock.schedule_once(lambda dt: self._draw_chart())
                    def live_signal(c_idx, price, stype="buy"):
                        quiet_draw_signal(c_idx, price, stype)
                        Clock.schedule_once(lambda dt: self._draw_chart())
                    context = {
                        'price': live_price,
                        'symbol': self.bot_symbol,
                        'position': self.current_position,
                        'trade_amount': calculated_coin_qty,
                        'log': self.log_msg,
                        'buy': self.safe_market_buy,
                        'sell': self.safe_market_sell,
                        'memory': self.bot_memory,
                        'candles': self.all_candles,
                        'draw_zone': live_zone,
                        'clear_zones': live_clear_zones,
                        'draw_trendline': live_tline,
                        'clear_trendlines': live_clear_tline,
                        'draw_signal': live_signal
                    }
                    exec(custom_code, globals(), context)
            except: pass
            time.sleep(0.1)

    def start_bot(self):
        if not self.exchange and not self.demo_mode:
            self.log_msg("CONNECT API OR ENABLE DEMO")
            return
        if self.bot_running: return
        self.root.ids.btn_start_bot.disabled = True
        self.bot_symbol = self.root.ids.symbol_spinner.text
        self.bot_running = True
        self.last_ws_price_time = time.time()
        self.current_position = 0.0
        self.root.ids.bot_status_label.text = f"BOT STATUS: RUNNING ({self.bot_symbol})"
        self.root.ids.btn_start_bot.text = "RUNNING..."
        threading.Thread(target=self.bot_engine_loop, daemon=True).start()

    def stop_bot(self):
        if not self.bot_running: return
        self.bot_running = False
        self.root.ids.btn_start_bot.disabled = False
        self.root.ids.bot_status_label.text = "BOT STATUS: IDLE"
        self.root.ids.btn_start_bot.text = "START AUTO BOT"
        self.update_pnl_ui("NONE", 0.0, 0.0)
        self.bot_symbol = None

    def save_api(self):
        api_key = self.root.ids.api_key_input.text
        api_secret = self.root.ids.api_secret_input.text
        if not api_key or not api_secret: return
        safe_key = self.encrypt_key(api_key)
        safe_secret = self.encrypt_key(api_secret)
        self.store.put('settings', api_key=safe_key, api_secret=safe_secret, market_type=self.market_type)
        threading.Thread(target=self.connect_to_binance, args=(api_key, api_secret), daemon=True).start()

    def connect_to_binance(self, key, secret):
        try:
            config = {
                'apiKey': key,
                'secret': secret,
                'enableRateLimit': True,
                'options': {'defaultType': self.market_type, 'adjustForTimeDifference': True}
            }
            self.exchange = ccxt.binance(config)
            balance = self.exchange.fetch_balance({'type': self.market_type})
            usdt_bal = balance['total'].get('USDT', 0.0)
            Clock.schedule_once(lambda dt: self.update_dashboard(usdt_bal))
        except: pass

if __name__ == "__main__":
    CyberBotApp().run()