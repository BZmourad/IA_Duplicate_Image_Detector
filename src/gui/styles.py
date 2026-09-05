"""
Application styles - Simple and clean design.
"""

class AppTheme:
    """Application theme."""
    
    # Simple color palette
    PRIMARY = "#2563EB"  # Blue
    PRIMARY_HOVER = "#1D4ED8"
    SUCCESS = "#16A34A"
    WARNING = "#D97706"
    ERROR = "#DC2626"
    BACKGROUND = "#FFFFFF"
    SURFACE = "#F9FAFB"
    TEXT = "#111827"
    TEXT_SECONDARY = "#6B7280"
    BORDER = "#D1D5DB"
    
    @classmethod
    def get_main_stylesheet(cls) -> str:
        """Get the main application stylesheet."""
        return f"""
        QMainWindow {{
            background-color: {cls.BACKGROUND};
        }}
        
        QWidget {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
            color: {cls.TEXT};
        }}
        
        /* Title */
        QLabel#titleLabel {{
            font-size: 22px;
            font-weight: bold;
            color: {cls.TEXT};
            padding: 15px 0px 5px 0px;
        }}
        
        QLabel#subtitleLabel {{
            font-size: 13px;
            color: {cls.TEXT_SECONDARY};
            padding-bottom: 15px;
        }}
        
        /* Input */
        QLineEdit {{
            padding: 10px;
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            background-color: white;
            font-size: 13px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {cls.PRIMARY};
        }}
        
        /* Buttons */
        QPushButton {{
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
            border: none;
        }}
        
        QPushButton#primaryButton {{
            background-color: {cls.PRIMARY};
            color: white;
            min-height: 45px;
            font-size: 14px;
        }}
        
        QPushButton#primaryButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
        }}
        
        QPushButton#primaryButton:disabled {{
            background-color: {cls.BORDER};
            color: {cls.TEXT_SECONDARY};
        }}
        
        QPushButton#secondaryButton {{
            background-color: white;
            color: {cls.TEXT};
            border: 1px solid {cls.BORDER};
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {cls.SURFACE};
        }}
        
        QPushButton#secondaryButton:disabled {{
            color: {cls.TEXT_SECONDARY};
            border-color: {cls.BORDER};
        }}
        
        /* Progress bar */
        QProgressBar {{
            border: 1px solid {cls.BORDER};
            border-radius: 4px;
            background-color: {cls.SURFACE};
            height: 20px;
            text-align: center;
            font-size: 11px;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.PRIMARY};
            border-radius: 3px;
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            background-color: white;
        }}
        
        QTabBar::tab {{
            padding: 10px 20px;
            margin-right: 2px;
            background-color: {cls.SURFACE};
            border: 1px solid {cls.BORDER};
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            color: {cls.TEXT_SECONDARY};
            font-weight: bold;
        }}
        
        QTabBar::tab:selected {{
            background-color: white;
            color: {cls.PRIMARY};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: #E5E7EB;
        }}
        
        /* Scroll area */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        /* Group box */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: white;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        
        /* Status labels */
        QLabel#statusSuccess {{
            color: {cls.SUCCESS};
            font-weight: bold;
        }}
        
        QLabel#statusError {{
            color: {cls.ERROR};
            font-weight: bold;
        }}
        
        QLabel#statusInfo {{
            color: {cls.TEXT_SECONDARY};
        }}
        """