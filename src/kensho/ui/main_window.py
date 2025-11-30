import customtkinter as ctk
from typing import Dict, Any
from .views.dashboard import DashboardView

class MainWindow(ctk.CTk):
    def __init__(self, app_state: Dict[str, Any], on_save_state: Any):
        super().__init__()

        self.app_state = app_state
        self.on_save_state = on_save_state

        self.app_state_data = app_state # Renamed from self.state to avoid conflict
        self.on_save_state = on_save_state
        self.minimal_mode = False
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Window Setup
        self.title("Kenshō")
        self.geometry("360x500")
        self.minsize(300, 400)
        
        # Theme Setup
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._init_sidebar()
        self._init_content_area()
        
        # Show default view
        self.show_dashboard()

    def _init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=60, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="K", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=10, pady=(20, 10))

        self.nav_dashboard = self._create_nav_button("Home", self.show_dashboard, 1)
        self.nav_history = self._create_nav_button("Hist", self.show_history, 2)
        self.nav_settings = self._create_nav_button("Set", self.show_settings, 3)
        
        # Widget Mode Toggle
        self.nav_widget = ctk.CTkButton(
            self.sidebar,
            text="⤢",
            command=self.toggle_minimal_mode,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="center",
            width=50,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        self.nav_widget.grid(row=4, column=0, padx=5, pady=20, sticky="s")

    def _create_nav_button(self, text: str, command: Any, row: int) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            command=command,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="center",
            width=50,
            height=40
        )
        btn.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        return btn

    def _init_content_area(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Restore Button (Hidden by default)
        self.restore_btn = ctk.CTkButton(
            self,
            text="⤡",
            width=30,
            height=30,
            fg_color="transparent",
            text_color="gray50",
            command=self.toggle_minimal_mode,
            font=ctk.CTkFont(size=16)
        )

    def toggle_minimal_mode(self):
        if not getattr(self, "minimal_mode", False):
            # Enter Widget Mode
            self.minimal_mode = True
            self.overrideredirect(True) # Remove frame
            
            # IMPORTANT: Update minsize BEFORE geometry to allow shrinking
            self.minsize(220, 280)
            self.geometry("220x280")
            self.attributes("-topmost", True) # Keep widget on top
            
            self.sidebar.grid_remove()
            self.content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.content_frame.grid_columnconfigure(0, weight=1)
            
            # Show Restore Button overlay
            self.restore_btn.place(relx=0.9, rely=0.05, anchor="ne")
            
            # Enable Dragging
            self.bind("<Button-1>", self._start_drag)
            self.bind("<B1-Motion>", self._do_drag)
            
            # Notify Dashboard to compact itself
            if hasattr(self, 'dashboard_view'):
                self.dashboard_view.set_compact(True)
                
        else:
            # Exit Widget Mode
            self.minimal_mode = False
            self.overrideredirect(False)
            self.attributes("-topmost", False) # Disable always on top
            
            # Restore standard minsize
            self.minsize(300, 400)
            self.geometry("360x500")
            
            self.sidebar.grid()
            self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            
            self.restore_btn.place_forget()
            
            # Disable Dragging
            self.unbind("<Button-1>")
            self.unbind("<B1-Motion>")
            
            if hasattr(self, 'dashboard_view'):
                self.dashboard_view.set_compact(False)

    def _start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _do_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")

    def show_dashboard(self):
        self._clear_content()
        self.dashboard_view = DashboardView(
            self.content_frame, 
            self.app_state, 
            self.on_save_state,
            on_focus_mode=self.toggle_minimal_mode
        )
        self.dashboard_view.pack(fill="both", expand=True)
        self._highlight_nav(self.nav_dashboard)

    def show_history(self):
        self._clear_content()
        label = ctk.CTkLabel(self.content_frame, text="History & Analytics (Coming Soon)", font=ctk.CTkFont(size=20))
        label.pack(expand=True)
        self._highlight_nav(self.nav_history)

    def show_settings(self):
        self._clear_content()
        label = ctk.CTkLabel(self.content_frame, text="Settings (Coming Soon)", font=ctk.CTkFont(size=20))
        label.pack(expand=True)
        self._highlight_nav(self.nav_settings)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _highlight_nav(self, active_btn: ctk.CTkButton):
        # Reset all
        for btn in [self.nav_dashboard, self.nav_history, self.nav_settings]:
            btn.configure(fg_color="transparent")
        
        # Highlight active
        active_btn.configure(fg_color=("gray75", "gray25"))
