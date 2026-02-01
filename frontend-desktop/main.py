import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QStackedWidget, QMessageBox, QFileDialog, QHBoxLayout, QFrame, 
                             QDateEdit, QMenu, QWidgetAction, QCheckBox, QAbstractButton, QGraphicsDropShadowEffect, QScrollArea)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# --- 1. ROBUST TOGGLE SWITCH ---
class ModernToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._thumb_x = 3
        self._anim = QPropertyAnimation(self, b"thumb_pos", self)
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.OutQuad)
        self.stateChanged.connect(self.animate_switch)

    @pyqtProperty(int)
    def thumb_pos(self): return self._thumb_x
    
    @thumb_pos.setter
    def thumb_pos(self, pos):
        self._thumb_x = pos
        self.update()

    def hitButton(self, pos: QPoint): return self.contentsRect().contains(pos)

    def animate_switch(self, state):
        end_val = self.width() - 27 if state else 3
        self._anim.stop()
        self._anim.setStartValue(self._thumb_x)
        self._anim.setEndValue(end_val)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self.isChecked():
            track_color = QColor('#ff8c00')
            thumb_color = Qt.white
        else:
            track_color = QColor("#ffffff")
            thumb_color = QColor("#555")
            p.setPen(QPen(QColor("#ccc"), 1))
            
        if self.isChecked(): p.setPen(Qt.NoPen)
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(thumb_color))
        p.drawEllipse(self._thumb_x, 2, 24, 24)
        p.end()

# --- 2. STAT CARD WIDGET (FIXED COLORS) ---
class StatCard(QFrame):
    def __init__(self, title, value, color_hex):
        super().__init__()
        self.setObjectName("StatCard") # Important for CSS targeting
        
        # Specific styling for this card to override global transparency
        self.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: {color_hex};
                border-radius: 15px;
                border: none;
            }}
        """)
        self.setFixedSize(180, 120)  # Fixed size for scrollable row
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        self.val_lbl.setWordWrap(True)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; background: transparent; border: none;")
        
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.title_lbl)
        layout.addStretch()
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,40))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

# --- 3. THEME CONTROLLER ---
class ThemeControl(QWidget):
    toggled = pyqtSignal()
    def __init__(self, is_dark=True):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5); layout.setSpacing(10)
        self.sun = QLabel("☀️"); self.sun.setStyleSheet("background: transparent; border: none; font-size: 16px;")
        self.switch = ModernToggle(); self.switch.setChecked(is_dark); 
        self.switch._thumb_x = self.switch.width() - 27 if is_dark else 3
        self.switch.clicked.connect(self.toggled.emit)
        self.moon = QLabel("🌙"); self.moon.setStyleSheet("background: transparent; border: none; font-size: 16px;")
        layout.addWidget(self.sun); layout.addWidget(self.switch); layout.addWidget(self.moon); layout.addStretch(); self.setLayout(layout)

# --- 4. DYNAMIC STYLESHEET ---
def get_style(theme):
    if theme == 'dark':
        return """
        QWidget { background-color: #0F1115; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
        QFrame#GlassCard { background-color: rgba(30, 30, 35, 0.6); border-radius: 22px; border: 1px solid rgba(255, 255, 255, 0.1); }
        QLineEdit, QDateEdit { padding: 12px; border: 1px solid #333; border-radius: 8px; background-color: #1A1A1A; color: white; font-size: 14px; }
        QLineEdit:focus { border: 1px solid #ff8c00; }
        QPushButton { font-weight: bold; border-radius: 12px; padding: 12px; border: none; }
        QMenu { background-color: #121212; border: 1px solid #333; }
        QMenu::item { padding: 8px 25px; color: #e0e0e0; }
        QMenu::item:selected { background-color: #0B1220; color: #ff8c00; }
        QLabel { background-color: transparent; }
        QScrollArea { background: transparent; border: none; }
        """
    else:
        return """
        QWidget#MainApp { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ee7752, stop:0.33 #e73c7e, stop:0.66 #23a6d5, stop:1 #23d5ab); font-family: 'Segoe UI', sans-serif; color: #333; }
        QStackedWidget, QWidget#WelcomeScreen, QWidget#DashboardScreen { background: transparent; }
        QFrame#GlassCard, QFrame#LoginCard { background-color: rgba(255, 255, 255, 0.88); border-radius: 22px; border: 1px solid rgba(255, 255, 255, 0.4); }
        QLineEdit, QDateEdit { padding: 12px; border: 1px solid #ccc; border-radius: 10px; background-color: rgba(255, 255, 255, 0.6); color: #333; font-size: 14px; }
        QLineEdit:focus { border: 1px solid #ff8c00; background-color: white; }
        QPushButton { font-weight: bold; border-radius: 12px; padding: 12px; border: none; }
        QMenu { background-color: rgba(255, 255, 255, 0.95); border: 1px solid #ccc; }
        QMenu::item { padding: 8px 25px; color: #333; }
        QMenu::item:selected { background-color: #ff8c00; color: white; }
        QLabel { background-color: transparent; color: #333; }
        QLabel#WelcomeTitle { color: #222; }
        QLabel#WelcomeSub { color: #ff8c00; }
        QScrollArea { background: transparent; border: none; }
        """

# --- SCREENS ---
class WelcomeScreen(QWidget):
    def __init__(self, switch_to_login, toggle_callback, is_dark):
        super().__init__()
        self.setObjectName("WelcomeScreen"); self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(); top = QHBoxLayout(); top.addStretch(); self.theme_ctrl = ThemeControl(is_dark); self.theme_ctrl.toggled.connect(toggle_callback); top.addWidget(self.theme_ctrl); layout.addLayout(top); layout.addStretch()
        title = QLabel("Welcome to\nChemical Visualizer"); title.setObjectName("WelcomeTitle"); title.setAlignment(Qt.AlignCenter); title.setStyleSheet("font-family: 'Segoe Script'; font-size: 48px; font-weight: bold;")
        sub = QLabel("for fossee"); sub.setObjectName("WelcomeSub"); sub.setAlignment(Qt.AlignCenter); sub.setStyleSheet("font-family: 'Segoe Script'; font-size: 20px; margin-bottom: 50px;")
        btn = QPushButton("Get Started"); btn.setCursor(Qt.PointingHandCursor); btn.setFixedSize(200, 50); btn.setStyleSheet("background-color: #ff8c00; color: white; font-size: 18px; border-radius: 25px;"); btn.clicked.connect(switch_to_login)
        layout.addWidget(title); layout.addWidget(sub); layout.addWidget(btn, alignment=Qt.AlignCenter); layout.addStretch(); self.setLayout(layout)

class LoginScreen(QWidget):
    def __init__(self, to_signup, to_dash):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); layout = QVBoxLayout(); layout.setAlignment(Qt.AlignCenter)
        f = QFrame(); f.setObjectName("LoginCard"); l = QVBoxLayout(f); l.setSpacing(15); l.setContentsMargins(40,40,40,40); f.setFixedWidth(400)
        title = QLabel("🔐 Login"); title.setStyleSheet("font-size: 28px; color: #ff8c00; font-weight: bold;"); l.addWidget(title, alignment=Qt.AlignCenter)
        self.email = QLineEdit(); self.email.setPlaceholderText("Email"); self.pas = QLineEdit(); self.pas.setPlaceholderText("Password"); self.pas.setEchoMode(QLineEdit.Password)
        btn = QPushButton("Login"); btn.setStyleSheet("background: #ff8c00; color: white;"); btn.clicked.connect(lambda: self.do_login(to_dash))
        sig = QPushButton("New User? Sign Up"); sig.setFlat(True); sig.clicked.connect(to_signup)
        l.addWidget(self.email); l.addWidget(self.pas); l.addWidget(btn); l.addWidget(sig); layout.addWidget(f, alignment=Qt.AlignCenter); self.setLayout(layout)
    def do_login(self, cb):
        try:
            r = requests.post('http://127.0.0.1:8000/api/login/', json={"email": self.email.text(), "password": self.pas.text()})
            if r.status_code == 200: d=r.json(); cb(d.get("name") or d.get("username"), self.email.text(), d.get("phone"), d.get("institute"))
            else: QMessageBox.warning(self, "Failed", "Invalid Credentials")
        except: QMessageBox.critical(self, "Error", "Connection Failed")

class SignupScreen(QWidget):
    def __init__(self, to_login):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); layout = QVBoxLayout(); layout.setAlignment(Qt.AlignCenter)
        f = QFrame(); f.setObjectName("LoginCard"); l = QVBoxLayout(f); l.setSpacing(10); l.setContentsMargins(40,40,40,40); f.setFixedWidth(420)
        l.addWidget(QLabel("📝 Create Account", styleSheet="font-size: 24px; color: #10b981; font-weight: bold;"), alignment=Qt.AlignCenter)
        self.inputs = {}; fields = ["Name", "Phone", "Institute", "ID", "PIN", "Email", "Password"]; self.dob = QDateEdit(); self.dob.setDisplayFormat("yyyy-MM-dd")
        for k in fields:
            w = QLineEdit(); w.setPlaceholderText(k); l.addWidget(w); 
            if k in ["PIN", "Password"]: w.setEchoMode(QLineEdit.Password)
            self.inputs[k] = w; 
            if k == "Phone": l.addWidget(self.dob)
        btn = QPushButton("Register"); btn.setStyleSheet("background: #10b981; color: white;"); btn.clicked.connect(lambda: self.do_signup(to_login)); l.addWidget(btn); back = QPushButton("Back"); back.setFlat(True); back.clicked.connect(to_login); l.addWidget(back); layout.addWidget(f, alignment=Qt.AlignCenter); self.setLayout(layout)
    def do_signup(self, cb):
        d = { "name": self.inputs["Name"].text(), "phone": self.inputs["Phone"].text(), "dob": self.dob.date().toString("yyyy-MM-dd"), "institute": self.inputs["Institute"].text(), "college_id": self.inputs["ID"].text(), "security_pin": self.inputs["PIN"].text(), "email": self.inputs["Email"].text(), "password": self.inputs["Password"].text() }
        try: requests.post('http://127.0.0.1:8000/api/signup/', json=d); QMessageBox.information(self, "Success", "Registered!"); cb()
        except: QMessageBox.warning(self, "Error", "Failed")

class EditProfileScreen(QWidget):
    def __init__(self, to_dash):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); layout = QVBoxLayout(); layout.setAlignment(Qt.AlignCenter)
        f = QFrame(); f.setObjectName("LoginCard"); l = QVBoxLayout(f); l.setSpacing(15); l.setContentsMargins(40,40,40,40); f.setFixedWidth(400)
        l.addWidget(QLabel("👤 Edit Profile", styleSheet="font-size: 24px; font-weight: bold;"), alignment=Qt.AlignCenter)
        self.n = QLineEdit(); self.n.setPlaceholderText("Name"); self.i = QLineEdit(); self.i.setPlaceholderText("Institute"); self.p = QLineEdit(); self.p.setPlaceholderText("Phone"); self.e = QLineEdit(); self.e.setDisabled(True)
        for w in [self.n, self.i, self.p, self.e]: l.addWidget(w)
        btn = QPushButton("Save"); btn.setStyleSheet("background: #3b82f6; color: white;"); btn.clicked.connect(lambda: self.save(to_dash)); l.addWidget(btn); back = QPushButton("Cancel"); back.setFlat(True); back.clicked.connect(lambda: to_dash(None,None,None,None)); l.addWidget(back); layout.addWidget(f, alignment=Qt.AlignCenter); self.setLayout(layout)
    def load(self, u): self.cid=u['email']; self.e.setText(u['email']); self.n.setText(u['name']); self.i.setText(u['institute']); self.p.setText(u['phone'])
    def save(self, cb):
        d = { "email": self.cid, "name": self.n.text(), "institute": self.i.text(), "phone": self.p.text() }
        try: requests.post('http://127.0.0.1:8000/api/update-profile/', json=d); QMessageBox.information(self, "Success", "Updated!"); cb(d['name'], d['email'], d['phone'], d['institute'])
        except: QMessageBox.warning(self, "Error", "Failed")

class DashboardScreen(QWidget):
    def __init__(self, logout_cb, edit_cb, toggle_cb, is_dark):
        super().__init__(); self.setObjectName("DashboardScreen"); self.setAttribute(Qt.WA_TranslucentBackground)
        outer_layout = QVBoxLayout(self); outer_layout.setContentsMargins(40, 20, 40, 40)
        self.card = QFrame(); self.card.setObjectName("GlassCard")
        card_layout = QVBoxLayout(self.card); card_layout.setSpacing(20); card_layout.setContentsMargins(30, 30, 30, 30)

        # Top Bar
        top_bar = QHBoxLayout(); top_bar.setContentsMargins(0, 0, 0, 10)
        self.wel = QLabel("Welcome"); self.wel.setObjectName("WelcomeTitle"); self.wel.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.menu_btn = QPushButton("☰"); self.menu_btn.setFixedSize(40, 40); self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setStyleSheet("QPushButton { border: none; background: rgba(0,0,0,0.05); border-radius: 8px; font-size: 20px; color: #555; } QPushButton:hover { background: rgba(0,0,0,0.1); color: #000; }")
        self.menu_btn.clicked.connect(self.show_menu)
        self.menu = QMenu(); self.menu.addAction("👤 Edit Profile", edit_cb)
        theme_action = QWidgetAction(self.menu); self.theme_ctrl_menu = ThemeControl(is_dark); self.theme_ctrl_menu.toggled.connect(toggle_cb); theme_action.setDefaultWidget(self.theme_ctrl_menu); self.menu.addAction(theme_action)
        self.menu.addSeparator(); self.menu.addAction("🚪 Log Out", logout_cb)
        top_bar.addWidget(self.wel); top_bar.addStretch(); top_bar.addWidget(self.menu_btn); card_layout.addLayout(top_bar)

        # Upload Button
        self.upload_btn = QPushButton("📂 Upload Dataset (CSV/Excel/JSON)"); self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton { background-color: #ff8c00; color: white; padding: 15px; font-size: 16px; border-radius: 12px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #e67e00; }
        """)
        self.upload_btn.clicked.connect(self.upl); card_layout.addWidget(self.upload_btn)
        
        # --- DYNAMIC STATS AREA (Scrollable) ---
        self.stats_scroll = QScrollArea()
        self.stats_scroll.setFixedHeight(140)
        self.stats_scroll.setWidgetResizable(True)
        self.stats_scroll.setStyleSheet("background: transparent; border: none;")
        self.stats_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.stats_container = QWidget()
        self.stats_container.setStyleSheet("background: transparent;")
        self.stats_layout = QHBoxLayout(self.stats_container)
        self.stats_layout.setAlignment(Qt.AlignLeft)
        self.stats_layout.setSpacing(15)
        
        self.stats_scroll.setWidget(self.stats_container)
        card_layout.addWidget(self.stats_scroll)

        # Chart Section (Hidden Initially)
        self.chart_title = QLabel("Data Distribution"); self.chart_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px; color: #555;")
        self.chart_title.setAlignment(Qt.AlignCenter); self.chart_title.setVisible(False)
        card_layout.addWidget(self.chart_title)

        self.fig = plt.figure(figsize=(5, 4)); self.fig.patch.set_facecolor('none') 
        self.can = FigureCanvas(self.fig); self.can.setVisible(False)
        card_layout.addWidget(self.can)
        
        # Placeholder Text
        self.placeholder = QLabel("Upload a dataset to see stats..."); self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("background: rgba(0,0,0,0.03); border-radius: 12px; padding: 20px; color: #666; font-size: 14px;")
        card_layout.addWidget(self.placeholder)
        
        outer_layout.addWidget(self.card)

    def show_menu(self): self.menu.exec_(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))
    
    def upl(self):
        # UPDATED: Accept Any Format
        f = QFileDialog.getOpenFileName(self, 'Open', 'c:\\', "Data Files (*.csv *.xlsx *.xls *.json);;All Files (*)")[0]
        if f: 
            try: r = requests.post('http://127.0.0.1:8000/api/upload/', files={'file': open(f, 'rb')}); self.upd(r.json())
            except: QMessageBox.warning(self, "Error", "Failed to process file")

    def upd(self, d):
        is_dark = self.parent().parent().theme == 'dark'
        
        # Hide placeholder, show chart
        self.placeholder.setVisible(False)
        self.can.setVisible(True)
        self.chart_title.setVisible(True)
        
        # --- 1. CLEAR OLD STATS ---
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # --- 2. GENERATE NEW STATS DYNAMICALLY ---
        colors = ['#ef4444', '#ec4899', '#f97316', '#facc15', '#3b82f6', '#10b981'] # Red, Pink, Orange, Yellow, Blue, Green
        
        # Always add 'Total Count'
        self.stats_layout.addWidget(StatCard("TOTAL COUNT", d['total_count'], "#3b82f6")) # Blue default
        
        # Add dynamic metrics from backend
        metrics = d.get('metrics', [])
        for i, m in enumerate(metrics):
            col = colors[i % len(colors)]
            self.stats_layout.addWidget(StatCard(str(m['label']).upper(), m['value'], col))
        
        # --- 3. CHART LOGIC ---
        self.fig.clear(); ax = self.fig.add_subplot(111)
        
        chart_data = d.get('chart_data', {})
        if chart_data:
            labels = chart_data.keys()
            vals = chart_data.values()
            text_c = "white" if is_dark else "black"
            
            # Use dynamic colors
            ax.pie(vals, labels=labels, autopct='%1.1f%%', colors=colors, pctdistance=0.85, textprops={'color': text_c})
            hole_c = '#0F1115' if is_dark else 'none'; self.fig.gca().add_artist(plt.Circle((0,0), 0.70, fc=hole_c))
            ax.set_title("", color=text_c)
            
            self.chart_title.setStyleSheet(f"font-size: 18px; font-weight: bold; margin-top: 10px; color: {text_c}; background: transparent;")
            self.can.draw()

class MainApp(QWidget):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Chemical Visualizer Pro"); self.resize(950, 800); self.setObjectName("MainApp")
        self.setFont(QFont("Segoe UI", 10)) 
        self.theme = 'dark'; self.stack = QStackedWidget()
        self.wel = WelcomeScreen(self.go_login, self.toggle, True); self.log = LoginScreen(self.go_signup, self.go_dash); self.sig = SignupScreen(self.go_login); self.dash = DashboardScreen(self.go_login, self.go_edit, self.toggle, True); self.edit = EditProfileScreen(self.ret_edit)
        for s in [self.wel, self.log, self.sig, self.dash, self.edit]: self.stack.addWidget(s)
        l = QVBoxLayout(); l.addWidget(self.stack); self.setLayout(l); self.apply()
    def go_login(self): self.stack.setCurrentIndex(1)
    def go_signup(self): self.stack.setCurrentIndex(2)
    def go_dash(self, n, e, p, i): self.u = {'name': n, 'email': e, 'phone': p, 'institute': i}; self.dash.wel.setText(f"Welcome, {n}"); self.stack.setCurrentIndex(3)
    def go_edit(self): self.edit.load(self.u); self.stack.setCurrentIndex(4)
    def ret_edit(self, n, e, p, i): 
        if n: self.u = {'name': n, 'email': e, 'phone': p, 'institute': i}; self.dash.wel.setText(f"Welcome, {n}"); self.stack.setCurrentIndex(3)
    def toggle(self): 
        self.theme = 'light' if self.theme == 'dark' else 'dark'; is_dark = (self.theme == 'dark')
        for ctrl in [self.wel.theme_ctrl.switch, self.dash.theme_ctrl_menu.switch]: ctrl.blockSignals(True); ctrl.setChecked(is_dark); ctrl.animate_switch(is_dark); ctrl.blockSignals(False)
        self.apply()
    def apply(self):
        self.setStyleSheet(get_style(self.theme))
        c_bg = '#0F1115' if self.theme == 'dark' else 'none'; c_txt = 'white' if self.theme == 'dark' else '#333'
        self.dash.fig.patch.set_facecolor(c_bg); self.dash.fig.patch.set_alpha(0.0 if self.theme == 'light' else 1.0)
        
        # Update Chart Title Color
        self.dash.chart_title.setStyleSheet(f"font-size: 18px; font-weight: bold; margin-top: 10px; color: {c_txt}; background: transparent;")
        
        if self.dash.fig.axes:
            ax = self.dash.fig.axes[0]; 
            for txt in ax.texts: txt.set_color(c_txt)
            hole_c = '#0F1115' if self.theme == 'dark' else 'none'
            for art in self.dash.fig.gca().get_children():
                if isinstance(art, plt.Circle): art.set_facecolor(hole_c)
            self.dash.can.draw()

if __name__ == '__main__': app = QApplication(sys.argv); ex = MainApp(); ex.show(); sys.exit(app.exec_())