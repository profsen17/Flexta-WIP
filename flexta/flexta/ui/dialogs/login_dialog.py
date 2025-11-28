import sys
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QStackedWidget, 
    QGraphicsDropShadowEffect, QApplication, QCheckBox,
    QGraphicsOpacityEffect, QGridLayout, QScrollArea,
    QButtonGroup
)
from PySide6.QtCore import (
    Qt, Signal, QPoint, QPropertyAnimation, 
    QEasingCurve, QParallelAnimationGroup, QTimer, QSize, QRect, QAbstractAnimation
)
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPalette, QBrush, QIcon

# ==========================================
#  SHARED ANIMATION CLASS
# ==========================================
class FadeStackWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_animating = False
        self._cleanup_effects = []

    def crossfade_to_index(self, index):
        if self.is_animating or index == self.currentIndex():
            return

        self.is_animating = True
        current = self.currentWidget()
        next_widget = self.widget(index)

        self._cleanup_effects.clear()

        out_effect = QGraphicsOpacityEffect(current)
        current.setGraphicsEffect(out_effect)
        out_effect.setOpacity(1.0)

        in_effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(in_effect)
        in_effect.setOpacity(0.0)

        self.setCurrentIndex(index)

        anim_out = QPropertyAnimation(out_effect, b"opacity", self)
        anim_out.setDuration(300)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)
        anim_out.setEasingCurve(QEasingCurve.Type.OutQuad)

        anim_in = QPropertyAnimation(in_effect, b"opacity", self)
        anim_in.setDuration(300)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)
        anim_in.setEasingCurve(QEasingCurve.Type.InQuad)

        self._cleanup_effects = [out_effect, in_effect, anim_out, anim_in]

        def cleanup():
            self.is_animating = False
            current.setGraphicsEffect(None)
            next_widget.setGraphicsEffect(None)
            self._cleanup_effects.clear()

        group = QParallelAnimationGroup(self)
        group.addAnimation(anim_out)
        group.addAnimation(anim_in)
        group.finished.connect(cleanup)
        group.start()

# ==========================================
#  SETUP WIZARD (NEW INTERACTIVE MENU)
# ==========================================
class SetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Flexta Setup")
        self.setFixedSize(800, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.old_pos = None

        # --- LAYOUT ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setObjectName("WizardContainer")
        self.container.setStyleSheet("""
            QFrame#WizardContainer {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #000000);
                border-radius: 20px;
                border: 1px solid #333;
            }
        """)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.container)

        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.container.setGraphicsEffect(shadow)

        # --- HEADER (Title + Close) ---
        self.header_frame = QFrame()
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(30, 20, 30, 10)
        
        self.lbl_title = QLabel("Welcome to Flexta")
        self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("color: #888; background: transparent; border: none; font-size: 18px;")
        self.btn_close.clicked.connect(self.close)

        self.header_layout.addWidget(self.lbl_title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_close)
        self.container_layout.addWidget(self.header_frame)

        # --- CONTENT STACK ---
        self.stack = FadeStackWidget()
        self.stack.addWidget(self.create_theme_page())   # Page 0
        self.stack.addWidget(self.create_profile_page()) # Page 1
        self.stack.addWidget(self.create_settings_page())# Page 2
        
        self.stack.currentChanged.connect(self.update_nav_state)
        
        self.container_layout.addWidget(self.stack, 1)

        # --- BOTTOM NAV BAR (Arrows + Dots) ---
        self.nav_bar = QFrame()
        self.nav_layout = QHBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(40, 20, 40, 30)

        # Left Arrow
        self.btn_prev = QPushButton("←")
        self.btn_prev.setObjectName("NavArrow")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.clicked.connect(self.go_prev)

        # Dots Container
        self.dots_container = QFrame()
        self.dots_layout = QHBoxLayout(self.dots_container)
        self.dots_layout.setSpacing(10)
        self.dots = []
        for i in range(3): # 3 Pages
            dot = QLabel()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("background-color: #444; border-radius: 5px;")
            self.dots_layout.addWidget(dot)
            self.dots.append(dot)
        
        # Right Arrow
        self.btn_next = QPushButton("→")
        self.btn_next.setObjectName("NavArrow")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self.go_next)

        self.nav_layout.addWidget(self.btn_prev)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.dots_container)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.btn_next)

        self.container_layout.addWidget(self.nav_bar)

        self.update_nav_state(0) 

        # Drag Logic
        self.container.mousePressEvent = self.mousePressEvent
        self.container.mouseMoveEvent = self.mouseMoveEvent
        self.container.mouseReleaseEvent = self.mouseReleaseEvent

    # --- PAGES ---
    def create_theme_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel("Choose your Theme")
        lbl.setStyleSheet("color: #AAA; font-size: 16px; margin-bottom: 20px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        grid = QHBoxLayout()
        grid.setSpacing(40) # More space for expansion
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.theme_group = QButtonGroup(self)
        self.theme_group.setExclusive(True)
        self.theme_anims = [] # Keep refs to prevent gc

        themes = [("Dark", "#222"), ("Light", "#EEE"), ("Cyber", "#2a0a33")]
        
        for name, col in themes:
            btn = QPushButton(name)
            # Default Small Size
            btn.setMinimumSize(120, 150)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            
            # Custom properties to make stylesheet logic easier
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {col};
                    color: {'#FFF' if name != 'Light' else '#000'};
                    border: 2px solid #444;
                    border-radius: 15px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ border: 2px solid #FFF; }}
                QPushButton:checked {{ 
                    border: 2px solid #FFF; 
                    font-size: 16px; /* Bigger font when selected */
                }}
            """)
            
            self.theme_group.addButton(btn)
            grid.addWidget(btn)
            
            if name == "Dark":
                btn.setChecked(True)

        layout.addLayout(grid)

        # Logic to resize buttons on click
        def update_button_sizes():
            self.theme_anims.clear()
            
            for btn in self.theme_group.buttons():
                # Target size
                if btn.isChecked():
                    target_w, target_h = 130, 160
                else:
                    target_w, target_h = 120, 150

                current_size = btn.size()
                current_pos = btn.pos()

                # Calculate center point (remains fixed during growth)
                center_x = current_pos.x() + current_size.width() // 2
                center_y = current_pos.y() + current_size.height() // 2

                # New top-left corner to keep center fixed
                new_x = center_x - target_w // 2
                new_y = center_y - target_h // 2

                # Animate size
                anim_size = QPropertyAnimation(btn, b"size", btn)
                anim_size.setDuration(240)
                anim_size.setStartValue(current_size)
                anim_size.setEndValue(QSize(target_w, target_h))
                anim_size.setEasingCurve(QEasingCurve.Type.OutBack)

                # Animate position
                anim_pos = QPropertyAnimation(btn, b"pos", btn)
                anim_pos.setDuration(240)
                anim_pos.setStartValue(current_pos)
                anim_pos.setEndValue(QPoint(new_x, new_y))
                anim_pos.setEasingCurve(QEasingCurve.Type.OutBack)

                # Run both together
                group = QParallelAnimationGroup()
                group.addAnimation(anim_size)
                group.addAnimation(anim_pos)
                group.start(QAbstractAnimation.DeleteWhenStopped)
                
                self.theme_anims.append(group)

        # Connect Signal
        self.theme_group.buttonToggled.connect(update_button_sizes)
        
        # Trigger initial size set
        QTimer.singleShot(10, update_button_sizes)

        return page

    def create_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("Setup Profile")
        lbl.setStyleSheet("color: #AAA; font-size: 16px; margin-bottom: 20px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        avatar = QLabel("Upload\nPhoto")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(120, 120)
        avatar.setStyleSheet("""
            background-color: #222;
            color: #666;
            border: 2px dashed #444;
            border-radius: 60px; /* Circle */
            font-weight: bold;
        """)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Display Name")
        name_input.setFixedWidth(250)
        name_input.setStyleSheet("""
            background-color: #222; color: white; border: 1px solid #444; 
            border-radius: 20px; padding: 10px;
        """)

        layout.addWidget(lbl)
        layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(name_input, 0, Qt.AlignmentFlag.AlignCenter)
        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("Preferences")
        lbl.setStyleSheet("color: #AAA; font-size: 16px; margin-bottom: 20px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedWidth(300)
        vbox = QVBoxLayout(container)
        vbox.setSpacing(15)

        opts = ["Enable Auto-Save", "Show Line Numbers", "Enable Minimap", "Git Integration"]
        for opt in opts:
            chk = QCheckBox(opt)
            chk.setStyleSheet("""
                QCheckBox { color: white; font-size: 14px; spacing: 10px; }
                QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; background: #333; }
                QCheckBox::indicator:checked { background: #FFF; }
            """)
            vbox.addWidget(chk)

        layout.addWidget(lbl)
        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)
        return page

    # --- NAVIGATION ---
    def go_next(self):
        idx = self.stack.currentIndex()
        if idx < self.stack.count() - 1:
            self.stack.crossfade_to_index(idx + 1)
        else:
            print("Wizard Completed")
            self.close()

    def go_prev(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.crossfade_to_index(idx - 1)

    def update_nav_state(self, index):
        for i, dot in enumerate(self.dots):
            if i == index:
                dot.setFixedSize(20, 10) 
                dot.setStyleSheet("background-color: white; border-radius: 5px;")
            else:
                dot.setFixedSize(10, 10)
                dot.setStyleSheet("background-color: #444; border-radius: 5px;")

        if index == 0:
            self.btn_prev.setDisabled(True)
            self.btn_prev.setStyleSheet("color: #333; background: transparent; border: none; font-size: 24px;")
        else:
            self.btn_prev.setDisabled(False)
            self.btn_prev.setStyleSheet("color: white; background: transparent; border: none; font-size: 24px;")

        if index == self.stack.count() - 1:
            self.btn_next.setText("✓") 
        else:
            self.btn_next.setText("→")
        self.btn_next.setStyleSheet("color: white; background: transparent; border: none; font-size: 24px;")

    # --- DRAG LOGIC ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event):
        self.old_pos = None


# ==========================================
#  EXISTING LOGIN DIALOG (Unchanged)
# ==========================================
class GlowInput(QLineEdit):
    def __init__(self, placeholder, is_password=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        if is_password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)

class LoginDialog(QDialog):
    login_success = Signal(dict)
    guest_access = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Flexta")
        self.setFixedSize(900, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.old_pos = None

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10) 

        self.container = QFrame()
        self.container.setObjectName("Container")
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setSpacing(0)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.container)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(40, 60, 40, 60)
        self.left_layout.addSpacing(95) 
        
        self.btn_new = self.create_guest_button("Create New Project")
        self.btn_open = self.create_guest_button("Open Project")
        self.btn_import = self.create_guest_button("Import Project")
        self.btn_export = self.create_guest_button("Export Project")

        self.left_layout.addWidget(self.btn_new)
        self.left_layout.addWidget(self.btn_open)
        self.left_layout.addWidget(self.btn_import)
        self.left_layout.addWidget(self.btn_export)
        self.left_layout.addStretch()

        self.right_panel = QFrame()
        self.right_panel.setObjectName("RightPanel")
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(20, 15, 20, 40) 

        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(8)
        self.controls_layout.addStretch() 

        self.btn_min = self.create_window_btn("─", "MinBtn", self.showMinimized)
        self.btn_close = self.create_window_btn("✕", "CloseBtn", self.close)

        self.controls_layout.addWidget(self.btn_min)
        self.controls_layout.addWidget(self.btn_close)
        self.right_layout.addLayout(self.controls_layout)

        self.right_layout.addSpacing(50)

        self.right_layout.addStretch(1)
        self.lbl_header = QLabel("Login")
        self.lbl_header.setObjectName("AuthHeader")
        self.lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(self.lbl_header)
        
        self.lbl_error = QLabel(self) 
        self.lbl_error.setObjectName("ErrorLabel")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.hide()
        
        self.error_effect = QGraphicsOpacityEffect(self.lbl_error)
        self.lbl_error.setGraphicsEffect(self.error_effect)
        
        self.error_anim = QPropertyAnimation(self.error_effect, b"opacity")
        self.error_anim.setDuration(500) 
        self.error_anim.setEndValue(0.0)
        self.error_anim.setEasingCurve(QEasingCurve.Type.InQuad)
        self.error_anim.finished.connect(self.lbl_error.hide)
        
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self.error_anim.start)

        self.auth_stack = FadeStackWidget()
        
        self.page_login = QWidget()
        self.login_ui()
        self.auth_stack.addWidget(self.page_login)

        self.page_register = QWidget()
        self.register_ui()
        self.auth_stack.addWidget(self.page_register)
        
        self.right_layout.addWidget(self.auth_stack)
        self.right_layout.addStretch(1)

        self.toggle_container = QFrame()
        self.toggle_container.setObjectName("ToggleContainer")
        self.toggle_layout = QHBoxLayout(self.toggle_container)
        self.toggle_layout.setContentsMargins(5, 5, 5, 5)
        self.toggle_layout.setSpacing(0)

        self.btn_toggle_login = QPushButton("Login")
        self.btn_toggle_login.setObjectName("ToggleActive")
        self.btn_toggle_login.setCheckable(True)
        self.btn_toggle_login.setChecked(True)
        self.btn_toggle_login.clicked.connect(lambda: self.switch_view(0))

        self.btn_toggle_register = QPushButton("Register")
        self.btn_toggle_register.setObjectName("ToggleInactive")
        self.btn_toggle_register.setCheckable(True)
        self.btn_toggle_register.clicked.connect(lambda: self.switch_view(1))

        self.toggle_layout.addWidget(self.btn_toggle_login)
        self.toggle_layout.addWidget(self.btn_toggle_register)

        self.right_layout.addWidget(self.toggle_container, 0, Qt.AlignmentFlag.AlignCenter)

        self.container_layout.addWidget(self.left_panel, 4)
        self.container_layout.addWidget(self.right_panel, 6)

        self.setup_floating_logo()

        self.btn_new.clicked.connect(lambda: self.guest_access.emit("new"))
        self.btn_open.clicked.connect(lambda: self.guest_access.emit("open"))
        self.btn_import.clicked.connect(lambda: self.guest_access.emit("import"))
        self.btn_export.clicked.connect(lambda: self.guest_access.emit("export"))

        self.apply_styles()

    def setup_floating_logo(self):
        font_logo = QFont("Segoe UI", 48, QFont.Weight.Bold)
        self.lbl_fle = QLabel("Fle", self)
        self.lbl_fle.setFont(font_logo)
        self.lbl_fle.setStyleSheet("color: white; background-color: transparent;")
        self.lbl_fle.adjustSize()
        
        self.lbl_xta = QLabel("xta", self)
        self.lbl_xta.setFont(font_logo)
        self.lbl_xta.setStyleSheet("color: white; background-color: transparent;")
        self.lbl_xta.adjustSize()

        seam_x = 362
        logo_y = 25 
        self.lbl_fle.move(seam_x - self.lbl_fle.width(), logo_y)
        self.lbl_xta.move(seam_x, logo_y)
        self.lbl_fle.raise_()
        self.lbl_xta.raise_()

    def create_guest_button(self, text):
        btn = QPushButton(text)
        btn.setObjectName("GuestButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def create_window_btn(self, text, obj_name, callback):
        btn = QPushButton(text)
        btn.setObjectName(obj_name)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        return btn

    def login_ui(self):
        layout = QVBoxLayout(self.page_login)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 15, 40, 10)
        
        self.inp_login_email = GlowInput("E-mail")
        self.inp_login_pass = GlowInput("Password", is_password=True)
        self.inp_login_pass.returnPressed.connect(self.handle_login)

        aux_layout = QHBoxLayout()
        self.chk_remember = QCheckBox("Don't ask again")
        self.btn_forgot = QPushButton("Forgot Password?")
        self.btn_forgot.setObjectName("ForgotBtn")
        self.btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        
        aux_layout.addWidget(self.chk_remember)
        aux_layout.addStretch()
        aux_layout.addWidget(self.btn_forgot)

        btn_action = QPushButton("Login")
        btn_action.setObjectName("ActionBtn")
        btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_action.clicked.connect(self.handle_login)

        layout.addWidget(self.inp_login_email)
        layout.addWidget(self.inp_login_pass)
        layout.addLayout(aux_layout)
        layout.addStretch() 
        layout.addWidget(btn_action)

    def register_ui(self):
        layout = QVBoxLayout(self.page_register)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 15, 40, 10)

        self.inp_reg_name = GlowInput("First Name")
        self.inp_reg_last = GlowInput("Last Name")
        self.inp_reg_email = GlowInput("E-mail")
        self.inp_reg_pass = GlowInput("Password", is_password=True)
        self.inp_reg_pass.returnPressed.connect(self.handle_register)

        btn_action = QPushButton("Register")
        btn_action.setObjectName("ActionBtn")
        btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_action.clicked.connect(self.handle_register)

        layout.addWidget(self.inp_reg_name)
        layout.addWidget(self.inp_reg_last)
        layout.addWidget(self.inp_reg_email)
        layout.addWidget(self.inp_reg_pass)
        layout.addStretch()
        layout.addWidget(btn_action)

    def switch_view(self, index):
        self.lbl_error.hide()
        self.auth_stack.crossfade_to_index(index)
        
        if index == 0:
            self.lbl_header.setText("Login")
            self.btn_toggle_login.setChecked(True)
            self.btn_toggle_register.setChecked(False)
            self.btn_toggle_login.setObjectName("ToggleActive")
            self.btn_toggle_register.setObjectName("ToggleInactive")
        else:
            self.lbl_header.setText("Registration")
            self.btn_toggle_login.setChecked(False)
            self.btn_toggle_register.setChecked(True)
            self.btn_toggle_login.setObjectName("ToggleInactive")
            self.btn_toggle_register.setObjectName("ToggleActive")
            
        self.btn_toggle_login.style().unpolish(self.btn_toggle_login)
        self.btn_toggle_login.style().polish(self.btn_toggle_login)
        self.btn_toggle_register.style().unpolish(self.btn_toggle_register)
        self.btn_toggle_register.style().polish(self.btn_toggle_register)

    def show_error(self, message):
        self.lbl_error.setText(message)
        self.lbl_error.adjustSize()
        
        panel_pos = self.right_panel.mapTo(self, QPoint(0,0))
        panel_width = self.right_panel.width()
        label_width = self.lbl_error.width()
        x = panel_pos.x() + (panel_width - label_width) // 2
        
        stack_pos = self.auth_stack.mapTo(self, QPoint(0,0))
        stack_height = self.auth_stack.height()
        label_height = self.lbl_error.height()
        y = stack_pos.y() + (stack_height - label_height) // 2
        
        self.lbl_error.move(x, y)
        self.lbl_error.raise_()
        self.error_anim.stop()
        self.error_effect.setOpacity(1.0)
        self.lbl_error.show()
        self.error_timer.start(1000)
        
    def handle_login(self):
        email = self.inp_login_email.text()
        pwd = self.inp_login_pass.text()
        if not email or not pwd:
            self.show_error("Please fill in all fields.")
            return
        print(f"Login: {email}")
        self.accept()

    def handle_register(self):
        name = self.inp_reg_name.text()
        email = self.inp_reg_email.text()
        
        if not name or not email:
            self.show_error("Please complete the form.")
            return

        print(f"Registering: {email}")
        
        # --- NEW LOGIC: HIDE LOGIN, SHOW WIZARD ---
        self.hide()
        self.wizard = SetupWizard()
        self.wizard.show()
        # Note: We don't call self.accept() yet, we let the wizard handle the final flow

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def apply_styles(self):
        self.setStyleSheet("""
            QFrame#Container {
                background-color: transparent;
                border-radius: 20px;
            }
            QFrame#LeftPanel {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #3a3a3a, stop:1 #2D2D2D);
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
            }
            QPushButton#GuestButton {
                color: #CCCCCC; background-color: transparent; text-align: left; font-size: 15px; border: none; padding: 12px 10px; border-radius: 10px;
            }
            QPushButton#GuestButton:hover { color: #FFFFFF; background-color: rgba(255, 255, 255, 0.05); padding-left: 20px; }

            QFrame#RightPanel {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #000000);
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
            QPushButton#MinBtn { color: #888; background: transparent; border: none; font-size: 14px; border-radius: 15px; }
            QPushButton#MinBtn:hover { background-color: #333333; color: white; }
            QPushButton#CloseBtn { color: #888; background: transparent; border: none; font-size: 16px; border-radius: 15px; }
            QPushButton#CloseBtn:hover { background-color: #D32F2F; color: white; }

            QLabel#AuthHeader { color: white; font-size: 26px; font-family: 'Segoe UI', sans-serif; font-weight: 700; letter-spacing: 1px; }
            QLabel#ErrorLabel { background-color: #FF4444; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 6px 12px; }
            
            QLineEdit {
                background-color: #222222; color: #FFFFFF; border: 2px solid #333333; border-radius: 20px; padding: 10px 15px; font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #555555; background-color: #2a2a2a; }
            
            QPushButton#ActionBtn {
                background-color: #FFFFFF; color: #121212; border-radius: 20px; padding: 12px; font-weight: bold; font-size: 15px; border: 1px solid white;
            }
            QPushButton#ActionBtn:hover { background-color: #E0E0E0; border: 1px solid #CCCCCC; }
            QPushButton#ActionBtn:pressed { background-color: #BBBBBB; }

            QCheckBox { color: #AAAAAA; font-size: 12px; }
            QCheckBox::indicator { width: 15px; height: 15px; border-radius: 3px; border: 1px solid #555; background: #222; }
            QCheckBox::indicator:checked { background: #888; border: 1px solid #888; }
            
            QPushButton#ForgotBtn { color: #777777; background: transparent; border: none; font-size: 12px; }
            QPushButton#ForgotBtn:hover { color: #BBBBBB; text-decoration: underline; }

            QFrame#ToggleContainer { background-color: #222222; border-radius: 25px; min-height: 50px; max-width: 300px; border: 1px solid #333; }
            QPushButton#ToggleActive {
                background-color: #FFFFFF; color: #121212; border-radius: 20px; font-weight: bold; border: none; min-height: 40px; min-width: 100px;
            }
            QPushButton#ToggleInactive {
                background-color: transparent; color: #888888; border-radius: 20px; border: none; min-height: 40px; min-width: 100px;
            }
            QPushButton#ToggleInactive:hover { color: #FFFFFF; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginDialog()
    window.show()
    sys.exit(app.exec())