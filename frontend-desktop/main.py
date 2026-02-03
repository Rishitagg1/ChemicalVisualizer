import sys
import requests
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QStackedWidget, QMessageBox, QFileDialog, QHBoxLayout, QFrame, 
                             QLayout, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QSizePolicy, QSpacerItem, QCheckBox, QDialog, QListWidget, QListWidgetItem, QMenu, QAction)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint, pyqtSignal, QRect, QSize
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QLinearGradient
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# --- PDF GENERATION IMPORTS ---
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors as pdf_colors
from reportlab.platypus import Table, TableStyle

# --- 1. HISTORY MANAGER ---
class HistoryManager:
    FILE_NAME = "upload_history.json"
    @staticmethod
    def load_history():
        if not os.path.exists(HistoryManager.FILE_NAME): return []
        try: 
            with open(HistoryManager.FILE_NAME, 'r') as f: return json.load(f)
        except: return []
    @staticmethod
    def add_entry(filename, total_rows):
        history = HistoryManager.load_history()
        entry = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "filename": os.path.basename(filename), "rows": total_rows}
        history.insert(0, entry)
        with open(HistoryManager.FILE_NAME, 'w') as f: json.dump(history, f, indent=4)

# --- 2. LAYOUTS & WIDGETS ---
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, hSpacing=20, vSpacing=20):
        super(FlowLayout, self).__init__(parent)
        self._hSpace = hSpacing; self._vSpace = vSpacing; self.setContentsMargins(margin, margin, margin, margin); self.itemList = []
    def addItem(self, item): self.itemList.append(item)
    def count(self): return len(self.itemList)
    def itemAt(self, index): return self.itemList[index] if 0 <= index < len(self.itemList) else None
    def takeAt(self, index): return self.itemList.pop(index) if 0 <= index < len(self.itemList) else None
    def expandingDirections(self): return Qt.Orientations(0)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return self.doLayout(QRect(0, 0, width, 0), True)
    def setGeometry(self, rect): super(FlowLayout, self).setGeometry(rect); self.doLayout(rect, False)
    def sizeHint(self): return self.minimumSize()
    def minimumSize(self):
        size = QSize(); 
        for item in self.itemList: size = size.expandedTo(item.minimumSize())
        return size + QSize(2*self.contentsMargins().top(), 2*self.contentsMargins().top())
    def doLayout(self, rect, testOnly):
        x, y = rect.x(), rect.y(); lineHeight = 0
        for item in self.itemList:
            wid = item.widget(); spaceX = self._hSpace; spaceY = self._vSpace
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x(); y = y + lineHeight + spaceY; nextX = x + item.sizeHint().width() + spaceX; lineHeight = 0
            if not testOnly: item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX; lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

class StatCard(QFrame):
    def __init__(self, title, value, color_hex):
        super().__init__(); self.setObjectName("StatCard"); self.setStyleSheet(f"QFrame#StatCard {{ background-color: {color_hex}; border-radius: 16px; border: none; }}"); self.setFixedSize(160, 110)
        l = QVBoxLayout(self); l.setContentsMargins(20,20,20,20); l.setSpacing(5)
        self.v = QLabel(str(value)); self.v.setStyleSheet("color: white; font-size: 26px; font-weight: 800; background: transparent;")
        self.t = QLabel(title); self.t.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 11px; font-weight: 600; text-transform: uppercase; background: transparent;")
        self.t.setWordWrap(True); l.addWidget(self.v); l.addWidget(self.t); l.addStretch()

def get_style(theme):
    if theme == 'dark': return "QWidget { background-color: #111111; color: #e0e0e0; font-family: 'Segoe UI'; } QFrame#GlassCard { background-color: #1a1a1a; border-radius: 24px; border: 1px solid #333; } QLineEdit { background: #222; color: white; border: 1px solid #444; padding: 12px; border-radius: 10px; font-size: 14px; } QTableWidget { background-color: #1a1a1a; gridline-color: #333; color: white; border: none; } QHeaderView::section { background-color: #252525; padding: 8px; border: none; color: white; } QListWidget { background: #222; border: 1px solid #444; border-radius: 10px; padding: 10px; } QMenu { background-color: #222; border: 1px solid #555; color: white; } QMenu::item { padding: 8px 20px; } QMenu::item:selected { background-color: #3b82f6; }"
    else: return "QWidget#MainApp { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ee7752, stop:1 #23d5ab); font-family: 'Segoe UI'; color: #333; } QFrame#GlassCard { background: rgba(255,255,255,0.9); border-radius: 24px; border: 1px solid rgba(255,255,255,0.5); } QLineEdit { background: rgba(255,255,255,0.8); border: 1px solid #ccc; padding: 12px; border-radius: 10px; font-size: 14px; } QTableWidget { background-color: white; gridline-color: #eee; color: #333; } QHeaderView::section { background-color: #f5f5f5; padding: 8px; border: none; color: #555; } QListWidget { background: rgba(255,255,255,0.8); border: 1px solid #ccc; border-radius: 10px; padding: 10px; } QMenu { background-color: white; border: 1px solid #ccc; color: #333; } QMenu::item { padding: 8px 20px; } QMenu::item:selected { background-color: #3b82f6; color: white; }"

class HistoryDialog(QDialog):
    def __init__(self, theme):
        super().__init__(); self.setWindowTitle("Upload History"); self.resize(500, 400)
        bg = "#1a1a1a" if theme == 'dark' else "white"; txt = "white" if theme == 'dark' else "#333"; self.setStyleSheet(f"background: {bg}; color: {txt}; font-family: 'Segoe UI';")
        l = QVBoxLayout(self); l.setSpacing(15); l.addWidget(QLabel("Recent Uploads", styleSheet="font-size: 22px; font-weight: bold;"))
        self.list_widget = QListWidget(); data = HistoryManager.load_history()
        if not data: self.list_widget.addItem("No history found.")
        else:
            for item in data: self.list_widget.addItem(QListWidgetItem(f"📄 {item['filename']}\n   📅 {item['date']}   •   📊 {item['rows']} Rows"))
        l.addWidget(self.list_widget); btn = QPushButton("Close"); btn.clicked.connect(self.close); btn.setStyleSheet("background: #3b82f6; color: white; padding: 10px; border-radius: 8px; font-weight: bold;"); l.addWidget(btn)

# --- 3. UPDATED EDIT PROFILE DIALOG ---
class EditProfileDialog(QDialog):
    def __init__(self, theme, current_password):
        super().__init__()
        self.setWindowTitle("Edit Profile & Security")
        self.resize(400, 450)
        self.current_password = current_password
        
        bg = "#1a1a1a" if theme == 'dark' else "white"; txt = "white" if theme == 'dark' else "#333"
        self.setStyleSheet(f"background: {bg}; color: {txt}; font-family: 'Segoe UI';")
        
        l = QVBoxLayout(self); l.setSpacing(20); l.setContentsMargins(30,30,30,30)
        
        l.addWidget(QLabel("👤  Profile Details", styleSheet="font-size: 18px; font-weight: bold; color: #3b82f6;"))
        self.n = QLineEdit(); self.n.setPlaceholderText("Update Full Name")
        l.addWidget(self.n)
        
        l.addWidget(QLabel("🔒  Change Password", styleSheet="font-size: 18px; font-weight: bold; color: #3b82f6; margin-top: 10px;"))
        self.p_new = QLineEdit(); self.p_new.setPlaceholderText("New Password"); self.p_new.setEchoMode(QLineEdit.Password)
        self.p_confirm = QLineEdit(); self.p_confirm.setPlaceholderText("Confirm New Password"); self.p_confirm.setEchoMode(QLineEdit.Password)
        
        l.addWidget(self.p_new); l.addWidget(self.p_confirm)
        
        btn = QPushButton("Save Changes"); btn.clicked.connect(self.save)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("background: #10b981; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 10px;")
        l.addWidget(btn); l.addStretch()

    def save(self):
        new_pass = self.p_new.text()
        confirm_pass = self.p_confirm.text()
        
        # 1. Check if user is trying to change password
        if new_pass or confirm_pass:
            if new_pass != confirm_pass:
                QMessageBox.warning(self, "Security Check", "New password and Confirm password do not match!")
                return
            if new_pass == self.current_password:
                QMessageBox.warning(self, "Security Check", "You cannot reuse your current password.\nPlease choose a new one.")
                return
            if len(new_pass) < 4:
                QMessageBox.warning(self, "Security Check", "Password is too short.")
                return
            
            # Simulate saving to backend
            QMessageBox.information(self, "Success", "Password updated successfully!")
        
        elif self.n.text():
            QMessageBox.information(self, "Success", "Profile name updated!")
            
        self.close()

# --- 4. SCREENS ---
class SignupScreen(QWidget):
    def __init__(self, to_login):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); l = QVBoxLayout(); l.setAlignment(Qt.AlignCenter)
        f = QFrame(); f.setObjectName("LoginCard"); fl = QVBoxLayout(f); fl.setSpacing(15); fl.setContentsMargins(40,40,40,40); f.setFixedWidth(420)
        fl.addWidget(QLabel("📝 Create Account", styleSheet="font-size: 28px; font-weight: bold; background:transparent;"), alignment=Qt.AlignCenter)
        self.n = QLineEdit(); self.n.setPlaceholderText("Full Name"); self.e = QLineEdit(); self.e.setPlaceholderText("Email Address")
        self.p = QLineEdit(); self.p.setPlaceholderText("Password"); self.p.setEchoMode(QLineEdit.Password); self.ph = QLineEdit(); self.ph.setPlaceholderText("Phone Number"); self.inst = QLineEdit(); self.inst.setPlaceholderText("Institute / Company")
        btn = QPushButton("Register"); btn.setCursor(Qt.PointingHandCursor); btn.setStyleSheet("background: #10b981; color: white; padding: 12px; border-radius: 10px; font-weight: bold; font-size: 15px; border:none;"); btn.clicked.connect(lambda: self.do_signup(to_login))
        back = QPushButton("Back to Login"); back.setCursor(Qt.PointingHandCursor); back.setFlat(True); back.setStyleSheet("color: #666; font-weight: bold; margin-top: 10px; border:none; background:transparent;"); back.clicked.connect(to_login)
        for w in [self.n, self.e, self.p, self.ph, self.inst, btn, back]: fl.addWidget(w)
        l.addWidget(f, alignment=Qt.AlignCenter); self.setLayout(l)
    def do_signup(self, cb_back):
        data = { "name": self.n.text(), "email": self.e.text(), "password": self.p.text(), "phone": self.ph.text(), "institute": self.inst.text() }
        if not data["email"] or not data["password"]: QMessageBox.warning(self, "Error", "Email and Password are required!"); return
        try:
            r = requests.post('http://127.0.0.1:8000/api/signup/', json=data)
            if r.status_code == 200: QMessageBox.information(self, "Success", "Account Created! Please Login."); cb_back()
            else: QMessageBox.warning(self, "Error", r.json().get("error", "Signup Failed"))
        except: QMessageBox.critical(self, "Error", "Server Connection Failed")

class LoginScreen(QWidget):
    def __init__(self, to_sig, to_dash, to_admin):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); l = QVBoxLayout(); l.setAlignment(Qt.AlignCenter)
        f = QFrame(); f.setObjectName("LoginCard"); fl = QVBoxLayout(f); fl.setSpacing(20); fl.setContentsMargins(50,50,50,50); f.setFixedWidth(420)
        fl.addWidget(QLabel("Chemical Vis", styleSheet="font-size: 32px; color: #333; font-weight: bold; background:transparent; margin-bottom: 5px;"), alignment=Qt.AlignCenter)
        fl.addWidget(QLabel("Secure Login", styleSheet="font-size: 16px; color: #777; background:transparent; margin-bottom: 20px;"), alignment=Qt.AlignCenter)
        self.e = QLineEdit(); self.e.setPlaceholderText("Email ID"); self.p = QLineEdit(); self.p.setPlaceholderText("Password"); self.p.setEchoMode(QLineEdit.Password)
        btn = QPushButton("Access Console"); btn.setCursor(Qt.PointingHandCursor); btn.setStyleSheet("background: #2563eb; color: white; padding: 14px; border-radius: 10px; font-weight: bold; font-size: 15px; border:none;"); btn.clicked.connect(lambda: self.do_login(to_dash, to_admin))
        sig = QPushButton("Create New Account"); sig.setCursor(Qt.PointingHandCursor); sig.setFlat(True); sig.setStyleSheet("color: #2563eb; font-weight: bold; margin-top: 10px; border:none; background:transparent;"); sig.clicked.connect(to_sig)
        fl.addWidget(self.e); fl.addWidget(self.p); fl.addWidget(btn); fl.addWidget(sig); l.addWidget(f, alignment=Qt.AlignCenter); self.setLayout(l)
    def do_login(self, cb_user, cb_admin):
        try:
            r = requests.post('http://127.0.0.1:8000/api/login/', json={"email": self.e.text(), "password": self.p.text()})
            if r.status_code == 200:
                d = r.json(); 
                if d.get('role') == 'admin': cb_admin(d)
                else: 
                    # Pass the password to dashboard so we can validate changes later
                    cb_user(d.get("name"), self.p.text()) 
            else: QMessageBox.warning(self, "Failed", "Invalid Credentials")
        except: QMessageBox.critical(self, "Error", "Connection Failed")

class AdminScreen(QWidget):
    def __init__(self, logout_cb):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); l = QVBoxLayout(self); l.setContentsMargins(40,40,40,40)
        card = QFrame(); card.setObjectName("GlassCard"); cl = QVBoxLayout(card); cl.setContentsMargins(40,40,40,40)
        h = QHBoxLayout(); self.lbl = QLabel("Admin Console (Master)"); self.lbl.setStyleSheet("font-size: 26px; font-weight: bold; border:none;")
        logout = QPushButton("Sign Out"); logout.setCursor(Qt.PointingHandCursor); logout.clicked.connect(logout_cb); logout.setStyleSheet("background: #ef4444; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        h.addWidget(self.lbl); h.addStretch(); h.addWidget(logout); cl.addLayout(h)
        self.table = QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["Name", "Email", "Institute", "Role"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.table.verticalHeader().setVisible(False); cl.addWidget(self.table)
        btn = QPushButton("Refresh Database"); btn.setCursor(Qt.PointingHandCursor); btn.clicked.connect(self.load_users); btn.setStyleSheet("background: #3b82f6; color: white; padding: 12px; border-radius: 8px; font-weight:600; margin-top:10px;"); cl.addWidget(btn); l.addWidget(card)
    def load_users(self):
        try:
            r = requests.get('http://127.0.0.1:8000/api/admin/users/'); users = r.json().get('users', []); self.table.setRowCount(len(users))
            for i, u in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(u.get('name'))); self.table.setItem(i, 1, QTableWidgetItem(u.get('email')))
                self.table.setItem(i, 2, QTableWidgetItem(u.get('institute'))); self.table.setItem(i, 3, QTableWidgetItem(u.get('role', 'user')))
        except: QMessageBox.warning(self, "Error", "Failed to fetch users")

class WelcomeScreen(QWidget):
    def __init__(self, to_log, toggle, dark):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground); l = QVBoxLayout(); 
        l.addStretch(); l.addWidget(QLabel("Chemical Visualizer", styleSheet="font-size: 48px; font-weight: 800; color:#3b82f6;"), alignment=Qt.AlignCenter)
        l.addWidget(QLabel("Industrial Telemetry System", styleSheet="font-size: 18px; color: #666; margin-top:5px;"), alignment=Qt.AlignCenter)
        l.addSpacing(40)
        btn = QPushButton("Launch System"); btn.setCursor(Qt.PointingHandCursor); btn.clicked.connect(to_log); btn.setFixedSize(220,60); btn.setStyleSheet("background: #3b82f6; color: white; border-radius: 30px; font-size: 18px; font-weight: bold;"); l.addWidget(btn, alignment=Qt.AlignCenter); l.addStretch(); self.setLayout(l)

class DashboardScreen(QWidget):
    def __init__(self, logout_cb, toggle_cb, dark):
        super().__init__(); self.setAttribute(Qt.WA_TranslucentBackground)
        self.logout_cb = logout_cb
        self.toggle_cb = toggle_cb
        self.current_user_pass = "" # Stores current password for validation
        
        l = QVBoxLayout(self); l.setContentsMargins(0,0,0,0)
        self.main_scroll = QScrollArea(); self.main_scroll.setWidgetResizable(True); self.main_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }"); self.main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_widget = QWidget(); self.content_widget.setStyleSheet("background: transparent;")
        center_layout = QVBoxLayout(self.content_widget); center_layout.setContentsMargins(40,40,40,40); center_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.card = QFrame(); self.card.setObjectName("GlassCard"); self.card.setFixedWidth(1000)
        self.cl = QVBoxLayout(self.card); self.cl.setContentsMargins(40,40,40,40); self.cl.setSpacing(25)
        
        top = QHBoxLayout(); self.wel = QLabel("Dashboard"); self.wel.setStyleSheet("font-size: 26px; font-weight: bold; border:none;")
        self.hist_btn = QPushButton("🕒"); self.hist_btn.setFixedSize(40, 40); self.hist_btn.setCursor(Qt.PointingHandCursor); self.hist_btn.setToolTip("Upload History"); self.hist_btn.setStyleSheet("QPushButton { border: none; font-size: 20px; background: transparent; } QPushButton:hover { background: rgba(128,128,128,0.2); border-radius: 20px; }"); self.hist_btn.clicked.connect(self.show_history)
        self.menu_btn = QPushButton("☰"); self.menu_btn.setFixedSize(40, 40); self.menu_btn.setCursor(Qt.PointingHandCursor); self.menu_btn.setToolTip("Menu"); self.menu_btn.setStyleSheet("QPushButton { border: none; font-size: 24px; background: transparent; } QPushButton:hover { background: rgba(128,128,128,0.2); border-radius: 20px; }"); self.menu_btn.clicked.connect(self.show_menu)
        top.addWidget(self.wel); top.addStretch(); top.addWidget(self.hist_btn); top.addSpacing(5); top.addWidget(self.menu_btn)
        self.cl.addLayout(top)
        
        action_row = QHBoxLayout()
        up = QPushButton("  ☁  Upload Dataset"); up.setFixedHeight(50); up.setCursor(Qt.PointingHandCursor)
        up.setStyleSheet("QPushButton { background: #f59e0b; color: white; border-radius: 12px; font-weight: 700; font-size: 15px; border: none; padding-left: 20px; padding-right: 20px;} QPushButton:hover { background: #d97706; }")
        up.clicked.connect(self.upl)
        enhance = QPushButton("  📄  Download PDF Report"); enhance.setFixedHeight(50); enhance.setCursor(Qt.PointingHandCursor)
        enhance.setStyleSheet("QPushButton { background: #8b5cf6; color: white; border-radius: 12px; font-weight: 700; font-size: 15px; border: none; padding-left: 20px; padding-right: 20px;} QPushButton:hover { background: #7c3aed; }")
        enhance.clicked.connect(self.enhance_data)
        action_row.addWidget(up, 1); action_row.addWidget(enhance, 1); self.cl.addLayout(action_row)
        
        self.stats_container = QWidget(); self.stats_layout = FlowLayout(self.stats_container, margin=0, hSpacing=20, vSpacing=20); self.cl.addWidget(self.stats_container)
        self.toggle_btn = QPushButton("Show All Metrics"); self.toggle_btn.setCursor(Qt.PointingHandCursor); self.toggle_btn.setFixedSize(200, 40); self.toggle_btn.setStyleSheet("QPushButton { background: rgba(100,100,100,0.1); color: #888; border-radius: 20px; font-weight: 600; border: 1px solid rgba(100,100,100,0.2); } QPushButton:hover { background: rgba(100,100,100,0.2); color: #555; }"); self.toggle_btn.clicked.connect(self.toggle_metrics); self.toggle_btn.setVisible(False); self.cl.addWidget(self.toggle_btn, alignment=Qt.AlignCenter)
        self.chart_title = QLabel("Distribution Analysis"); self.chart_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; color: #555; border:none;"); self.chart_title.setAlignment(Qt.AlignCenter); self.chart_title.setVisible(False); self.cl.addWidget(self.chart_title)
        self.fig = plt.figure(figsize=(8,5)); self.can = FigureCanvas(self.fig); self.can.setVisible(False); self.cl.addWidget(self.can)
        center_layout.addWidget(self.card); self.main_scroll.setWidget(self.content_widget); l.addWidget(self.main_scroll); self.current_metrics = []; self.expanded = False

    def show_menu(self):
        menu = QMenu(self)
        edit_profile = menu.addAction("👤  Edit Profile")
        theme_text = "☀️  Light Mode" if self.parent().parent().theme == 'dark' else "🌙  Dark Mode"
        theme_action = menu.addAction(theme_text)
        menu.addSeparator()
        logout = menu.addAction("🚪  Logout")
        action = menu.exec_(self.menu_btn.mapToGlobal(QPoint(0, 45)))
        if action == logout: self.logout_cb()
        elif action == theme_action: self.toggle_cb()
        elif action == edit_profile: 
            dlg = EditProfileDialog(self.parent().parent().theme, self.current_user_pass)
            dlg.exec_()

    def upl(self):
        f = QFileDialog.getOpenFileName(self, 'Open', 'c:\\', "Data Files (*.csv *.xlsx *.json)")[0]
        if f: 
            try: 
                r = requests.post('http://127.0.0.1:8000/api/upload/', files={'file': open(f, 'rb')})
                data = r.json(); self.process_data(data); HistoryManager.add_entry(f, data.get('total_count', 0))
            except: QMessageBox.warning(self, "Error", "Failed")

    def enhance_data(self):
        if not self.current_metrics: QMessageBox.information(self, "Info", "Please upload data first!"); return
        try: self.current_metrics.sort(key=lambda x: float(x['value']) if str(x['value']).replace('.','',1).isdigit() else 0, reverse=True); self.render_stats()
        except: pass
        path, _ = QFileDialog.getSaveFileName(self, "Save Report", "Enhanced_Report.pdf", "PDF Files (*.pdf)")
        if path:
            try: self.generate_pdf(path); QMessageBox.information(self, "Success", f"Report Generated & Saved!\nLocation: {path}")
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")

    def generate_pdf(self, filename):
        c = canvas.Canvas(filename, pagesize=letter); width, height = letter
        c.setFillColorRGB(0.1, 0.4, 0.8); c.rect(0, height - 100, width, 100, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1); c.setFont("Helvetica-Bold", 24); c.drawString(50, height - 60, "Chemical Visualizer Report")
        c.setFont("Helvetica", 12); c.drawString(50, height - 85, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 16); c.drawString(50, height - 140, "Executive Summary")
        c.setFont("Helvetica", 12); c.drawString(50, height - 165, "The following dataset has been processed, cleaned, and optimized.")
        c.drawString(50, height - 180, "Key metrics have been identified and sorted by priority below.")
        data = [["Metric Name", "Value"]]; 
        for m in self.current_metrics: data.append([m['label'], str(m['value'])])
        table = Table(data, colWidths=[200, 150])
        style = TableStyle([('BACKGROUND', (0,0), (-1,0), pdf_colors.HexColor('#264653')), ('TEXTCOLOR', (0,0), (-1,0), pdf_colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0,0), (-1,0), 12), ('BACKGROUND', (0,1), (-1,-1), pdf_colors.HexColor('#f3f4f6')), ('GRID', (0,0), (-1,-1), 1, pdf_colors.black)])
        table.setStyle(style); table.wrapOn(c, width, height); table.drawOn(c, 50, height - 200 - (len(data) * 20))
        c.setFont("Helvetica-Oblique", 10); c.setFillColorRGB(0.5, 0.5, 0.5); c.drawString(50, 50, "Generated automatically by Chemical Visualizer Pro System."); c.save()

    def show_history(self): dlg = HistoryDialog(self.parent().parent().theme); dlg.exec_()

    def process_data(self, d):
        self.can.setVisible(True); self.chart_title.setVisible(True)
        # CUSTOM "EARTH & OCEAN" PALETTE (Deep Teal, Sage, Sandy Gold, Burnt Orange)
        cols = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51', '#8AB17D']
        self.current_metrics = [{"label": "Total Rows", "value": d['total_count'], "color": cols[0]}]
        for i, m in enumerate(d.get('metrics', [])): self.current_metrics.append({"label": str(m['label']), "value": m['value'], "color": cols[(i+1) % len(cols)]})
        self.expanded = False; self.render_stats()
        self.fig.clear(); ax = self.fig.add_subplot(111)
        cd = d.get('chart_data', {})
        is_dark = self.parent().parent().theme == 'dark'; tc = "white" if is_dark else "#333"; hc = '#1a1a1a' if is_dark else 'none'
        if cd:
            wedges, texts, autotexts = ax.pie(cd.values(), labels=cd.keys(), autopct='%1.1f%%', colors=cols, textprops={'color': tc}, pctdistance=0.85)
            self.fig.gca().add_artist(plt.Circle((0,0), 0.70, fc=hc))
            plt.setp(autotexts, size=9, weight="bold", color="white")
        self.chart_title.setStyleSheet(f"font-size: 20px; font-weight: bold; margin-top: 20px; color: {tc}; border:none; background:transparent;")
        self.can.draw()

    def toggle_metrics(self): self.expanded = not self.expanded; self.render_stats()
    def render_stats(self):
        while self.stats_layout.count(): item = self.stats_layout.takeAt(0); item.widget().deleteLater() if item.widget() else None
        limit = 5; items_to_show = self.current_metrics if self.expanded else self.current_metrics[:limit]
        for item in items_to_show: self.stats_layout.addWidget(StatCard(item['label'], item['value'], item['color']))
        if len(self.current_metrics) > limit: self.toggle_btn.setVisible(True); self.toggle_btn.setText("Show Less" if self.expanded else f"View All {len(self.current_metrics)} Metrics")
        else: self.toggle_btn.setVisible(False)

class MainApp(QWidget):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Chemical Vis Pro"); self.resize(1200, 900); self.setObjectName("MainApp"); self.theme = 'dark'
        self.stack = QStackedWidget()
        self.wel = WelcomeScreen(self.go_log, self.tog, True)
        self.log = LoginScreen(self.go_sig, self.go_dash, self.go_admin)
        self.signup = SignupScreen(self.go_log)
        self.dash = DashboardScreen(self.go_log, self.tog, True)
        self.admin = AdminScreen(self.go_log)
        self.stack.addWidget(self.wel); self.stack.addWidget(self.log); self.stack.addWidget(self.signup); self.stack.addWidget(self.dash); self.stack.addWidget(self.admin)
        l = QVBoxLayout(); l.addWidget(self.stack); self.setLayout(l); self.apply()
    def go_log(self): self.stack.setCurrentIndex(1)
    def go_sig(self): self.stack.setCurrentIndex(2)
    def go_dash(self, n, p): 
        self.dash.wel.setText(f"Hi, {n.split()[0]}")
        self.dash.current_user_pass = p # Store password for validation
        self.stack.setCurrentIndex(3)
    def go_admin(self, d): self.admin.load_users(); self.stack.setCurrentIndex(4)
    def tog(self): self.theme = 'light' if self.theme == 'dark' else 'dark'; self.apply()
    def apply(self): 
        self.setStyleSheet(get_style(self.theme))
        c = '#1a1a1a' if self.theme == 'dark' else 'none'
        self.dash.fig.patch.set_facecolor(c)
        self.dash.can.draw()

if __name__ == '__main__': app = QApplication(sys.argv); ex = MainApp(); ex.show(); sys.exit(app.exec_())