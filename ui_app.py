import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import json
import os
import math

# ------------------------------
# Fields with validation rules and default values
# ------------------------------
FIELDS = {
    "⚡ Generator": [
        ("Stator Radius", "stator_radius", "float", 5.0, 0.1, 20.0),
        ("Stator Height", "stator_height", "float", 3.0, 0.1, 10.0),
        ("Rotor Radius", "rotor_radius", "float", 3.0, 0.1, 15.0),
        ("Rotor Height", "rotor_height", "float", 2.0, 0.1, 8.0),
        ("Shaft Radius", "shaft_radius", "float", 0.5, 0.1, 3.0),
        ("Shaft Height", "shaft_height", "float", 8.0, 1.0, 20.0),
        ("Base Radius", "base_radius", "float", 7.0, 1.0, 15.0),
        ("Base Height", "base_height", "float", 1.0, 0.1, 5.0),
    ],
    "🌪 Turbine": [
        ("Spiral Major Radius", "spiral_major_radius", "float", 4.0, 1.0, 10.0),
        ("Spiral Minor Radius", "spiral_minor_radius", "float", 0.8, 0.1, 3.0),
        ("Stay Vane Count", "stay_vane_count", "int", 12, 4, 24),
        ("Guide Vane Count", "guide_vane_count", "int", 16, 8, 32),
        ("Runner Radius", "runner_radius", "float", 1.5, 0.5, 5.0),
        ("Runner Depth", "runner_depth", "float", 1.0, 0.2, 3.0),
        ("Blade Count", "blade_count", "int", 6, 3, 12),
        ("Blade Radius", "blade_radius", "float", 0.3, 0.1, 1.0),
        ("Blade Depth", "blade_depth", "float", 0.4, 0.1, 2.0),
        ("Shaft Radius", "shaft_radius", "float", 0.4, 0.1, 2.0),
        ("Shaft Height", "shaft_height", "float", 6.0, 2.0, 15.0),
        ("Draft Tube Radius1", "draft_radius1", "float", 1.2, 0.5, 3.0),
        ("Draft Tube Radius2", "draft_radius2", "float", 2.0, 0.5, 5.0),
        ("Draft Tube Depth", "draft_depth", "float", 3.0, 1.0, 8.0),
    ],
    "🌊 Intake Structure": [
        ("Bay Count", "bay_count", "int", 3, 1, 10),
        ("Bay Width", "bay_width", "float", 4.0, 2.0, 10.0),
        ("Pier Thickness", "pier_thick", "float", 1.0, 0.5, 3.0),
        ("Intake Height", "intake_height", "float", 8.0, 4.0, 20.0),
        ("Sill Elevation", "sill_elev", "float", 2.0, 1.0, 6.0),
        ("Deck Elevation", "deck_elev", "float", 10.0, 6.0, 20.0),
        ("Face Thickness", "face_thick", "float", 0.5, 0.2, 2.0),
        ("Trash Bar Thickness", "trash_bar_thick", "float", 0.1, 0.05, 0.3),
        ("Trash Bar Gap", "trash_bar_gap", "float", 0.15, 0.05, 0.4),
        ("Trash Bar Rows", "trash_bar_rows", "int", 4, 1, 8),
        ("Gate Thickness", "gate_thick", "float", 0.3, 0.1, 1.0),
        ("Gate Clearance Top", "gate_clear_top", "float", 2.0, 0.5, 5.0),
        ("Tunnel Diameter", "tunnel_diam", "float", 2.5, 1.0, 6.0),
        ("Tunnel Length", "tunnel_len", "float", 10.0, 5.0, 30.0),
        ("Floor Elevation", "floor_elev", "float", 0.0, -2.0, 2.0),
        ("Upstream Water Elevation", "water_elev_up", "float", 7.0, 3.0, 15.0),
        ("Side Wall Extra", "side_wall_extra", "float", 1.0, 0.5, 3.0),
        ("Structure Depth", "struct_depth", "float", 6.0, 3.0, 12.0),
        ("Crane Gauge", "crane_gauge", "float", 2.0, 1.0, 4.0),
        ("Crane Span XPad", "crane_span_xpad", "float", 1.0, 0.5, 3.0),
    ]
}

# ------------------------------
# Modern Dashboard UI with Spinbox Controls
# ------------------------------
class HydroUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Hydro Plant AI Designer")
        self.root.geometry("1300x850")
        self.entries = {}
        self.current_comp = None
        self.validation_data = {}

        # Apply superhero theme
        style = ttk.Style("superhero")

        # Main container with better spacing
        main_container = ttk.Frame(root)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header - More compact
        header_frame = ttk.Frame(main_container, bootstyle=PRIMARY)
        header_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(
            header_frame, 
            text="⚡ Hydro Plant AI Designer", 
            font=("Segoe UI", 22, "bold"),
            bootstyle=INVERSE
        ).pack(pady=15)

        ttk.Label(
            header_frame,
            text="Advanced Parametric Hydropower Component Design System",
            font=("Segoe UI", 11),
            bootstyle=INVERSE
        ).pack(pady=(0, 15))

        # Content area - sidebar + main with better proportions
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill="both", expand=True)

        # Left Sidebar - Slightly wider for better readability
        sidebar = ttk.Frame(content_frame, width=320, bootstyle=SECONDARY)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        # Sidebar Title
        ttk.Label(
            sidebar, 
            text="🏗️ COMPONENTS", 
            font=("Segoe UI", 14, "bold"), 
            bootstyle=INVERSE
        ).pack(pady=20)

        # Component buttons - Better spacing
        for comp in FIELDS.keys():
            btn = ttk.Button(
                sidebar, 
                text=comp, 
                bootstyle=INFO, 
                width=28,
                command=lambda c=comp: self.show_component(c)
            )
            btn.pack(pady=6, padx=20)

        # Separator
        ttk.Separator(sidebar, bootstyle=INFO).pack(fill="x", pady=20, padx=15)

        # Export section - More organized
        export_section = ttk.LabelFrame(
            sidebar, 
            text="📁 EXPORT SETTINGS", 
            bootstyle=INFO
        )
        export_section.pack(fill="x", padx=15, pady=10)

        ttk.Label(export_section, text="Export Folder:", bootstyle=INVERSE).pack(anchor="w", pady=(10, 5))
        
        self.export_entry = ttk.Entry(export_section, bootstyle=SUCCESS)
        self.export_entry.pack(fill="x", padx=10, pady=5)
        
        browse_frame = ttk.Frame(export_section)
        browse_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(
            browse_frame, 
            text="📂 Browse Folder", 
            bootstyle=WARNING,
            command=self.browse_export
        ).pack(side="left")

        # Generate button section - More prominent
        generate_section = ttk.Frame(sidebar)
        generate_section.pack(fill="x", padx=15, pady=20)

        self.generate_button = ttk.Button(
            generate_section, 
            text="🚀 GENERATE 3D MODEL", 
            bootstyle=SUCCESS,
            command=self.generate_model
        )
        self.generate_button.pack(fill="x", pady=5)

        # Progress bar - More visible
        self.progress = ttk.Progressbar(
            generate_section, 
            mode="indeterminate", 
            bootstyle=SUCCESS
        )
        self.progress.pack(fill="x", pady=10)

        # Status label - Better positioning
        self.status_label = ttk.Label(
            generate_section, 
            text="✅ System Ready", 
            bootstyle=INFO,
            font=("Segoe UI", 10, "bold")
        )
        self.status_label.pack(pady=5)

        # Right Main Content Area - Better organization
        self.content = ttk.Frame(content_frame, bootstyle=DARK)
        self.content.pack(side="left", fill="both", expand=True)

        # Top section: Component info and preview side by side
        top_section = ttk.Frame(self.content)
        top_section.pack(fill="x", pady=(0, 20))

        # Left: Component info
        info_frame = ttk.Frame(top_section)
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.content_label = ttk.Label(
            info_frame, 
            text="Select a Component to Begin", 
            font=("Segoe UI", 18, "bold")
        )
        self.content_label.pack(anchor="w", pady=(0, 5))

        self.content_subtitle = ttk.Label(
            info_frame,
            text="Configure the parameters for your hydropower component",
            font=("Segoe UI", 11),
            bootstyle=SECONDARY
        )
        self.content_subtitle.pack(anchor="w", pady=(0, 10))

        # Component description
        self.desc_label = ttk.Label(
            info_frame,
            text="Choose a component from the sidebar to start designing...",
            font=("Segoe UI", 10),
            bootstyle=SECONDARY,
            wraplength=400
        )
        self.desc_label.pack(anchor="w", pady=10)

        # Right: Preview canvas
        preview_container = ttk.Frame(top_section)
        preview_container.pack(side="right", fill="y", padx=(15, 0))

        self.preview_frame = ttk.LabelFrame(
            preview_container, 
            text="🔍 COMPONENT PREVIEW", 
            bootstyle=INFO
        )
        self.preview_frame.pack(fill="both", padx=5)

        self.preview_canvas = tk.Canvas(
            self.preview_frame, 
            width=350, 
            height=180,
            bg="#2d3748",
            highlightthickness=0
        )
        self.preview_canvas.pack(pady=15, padx=15)

        # Bottom section: Parameters in a well-organized frame
        params_main_frame = ttk.LabelFrame(
            self.content, 
            text="⚙️ DESIGN PARAMETERS", 
            bootstyle=INFO
        )
        params_main_frame.pack(fill="both", expand=True, padx=5)

        # Create scrollable parameters area with better styling
        self.canvas = tk.Canvas(params_main_frame, bg="#1c2333", highlightthickness=0)
        scrollbar = ttk.Scrollbar(params_main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        self.fields_frame = self.scrollable_frame

        # Component descriptions
        self.component_descriptions = {
            "⚡ Generator": "Electrical power generation unit with stator and rotor assembly for converting mechanical energy to electrical power.",
            "🌪 Turbine": "Hydraulic turbine system with spiral casing, guide vanes, and runner blades for converting water energy to mechanical rotation.",
            "🌊 Intake Structure": "Water intake system with multiple bays, trash racks, and control gates for efficient water collection and flow management."
        }

    def create_spinbox(self, parent, key, default, min_val, max_val, dtype):
        """Create a custom spinbox with up/down arrows"""
        frame = ttk.Frame(parent)
        
        # Entry field
        entry = ttk.Entry(
            frame, 
            width=12, 
            bootstyle=SUCCESS,
            font=("Segoe UI", 10),
            justify="center"
        )
        entry.insert(0, str(default))
        entry.pack(side="left", padx=(0, 5))
        
        # Spinbox buttons frame - FIXED: Equal sized buttons
        spin_frame = ttk.Frame(frame, width=30, height=50)
        spin_frame.pack(side="left", fill="y")
        spin_frame.pack_propagate(False)
        
        # Up button - FIXED: Equal size and black text
        up_btn = tk.Button(
            spin_frame,
            text="▲",
            bg="#5bc0de",  # Light blue background
            fg="black",    # Black arrow
            font=("Arial", 10, "bold"),
            width=3,
            height=1,
            relief="raised",
            bd=1,
            command=lambda: self.increment_value(entry, key, min_val, max_val, dtype, 1)
        )
        up_btn.pack(side="top", fill="both", expand=True, pady=(2, 1), padx=2)
        
        # Down button - FIXED: Equal size and black text
        down_btn = tk.Button(
            spin_frame,
            text="▼",
            bg="#5bc0de",  # Light blue background
            fg="black",    # Black arrow
            font=("Arial", 10, "bold"),
            width=3,
            height=1,
            relief="raised",
            bd=1,
            command=lambda: self.increment_value(entry, key, min_val, max_val, dtype, -1)
        )
        down_btn.pack(side="bottom", fill="both", expand=True, pady=(1, 2), padx=2)
        
        return entry, frame

    def increment_value(self, entry, key, min_val, max_val, dtype, direction):
        """Increment or decrement the value in the entry field"""
        try:
            current_value = entry.get().strip()
            if dtype == "int":
                step = 1
                current = int(current_value) if current_value else 0
            else:  # float
                step = 0.1
                current = float(current_value) if current_value else 0.0
            
            new_value = current + (direction * step)
            
            # Apply constraints
            if new_value < min_val:
                new_value = min_val
            elif new_value > max_val:
                new_value = max_val
            
            # Update entry
            if dtype == "int":
                entry.delete(0, tk.END)
                entry.insert(0, str(int(new_value)))
            else:
                entry.delete(0, tk.END)
                entry.insert(0, f"{new_value:.1f}")
            
            # Validate the new value
            self.validate_field(key)
            
        except ValueError:
            # If current value is invalid, set to default
            if dtype == "int":
                entry.delete(0, tk.END)
                entry.insert(0, str(int((min_val + max_val) / 2)))
            else:
                entry.delete(0, tk.END)
                entry.insert(0, f"{(min_val + max_val) / 2:.1f}")

    def show_component(self, comp):
        self.current_comp = comp
        clean_name = comp.replace("⚡", "").replace("🌪", "").replace("🌊", "").strip()
        self.content_label.config(text=f"{clean_name} Design")
        self.content_subtitle.config(text=f"Configure {clean_name.lower()} parameters")
        
        # Update description
        desc = self.component_descriptions.get(comp, "Configure the design parameters for this component.")
        self.desc_label.config(text=desc)
        
        # Update preview
        self.draw_component_preview()
        
        # Clear previous fields
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        
        self.entries.clear()
        self.validation_data.clear()

        if comp in FIELDS:
            # Add a header for parameters
            header_frame = ttk.Frame(self.fields_frame)
            header_frame.pack(fill="x", pady=(10, 15), padx=10)
            
            ttk.Label(
                header_frame,
                text="Parameter Configuration",
                font=("Segoe UI", 12, "bold"),
                bootstyle=INVERSE
            ).pack(side="left")
            
            ttk.Label(
                header_frame,
                text=f"Total Parameters: {len(FIELDS[comp])}",
                font=("Segoe UI", 10),
                bootstyle=SECONDARY
            ).pack(side="right")

            for i, (label, key, dtype, default, min_val, max_val) in enumerate(FIELDS[comp]):
                # Create parameter card with alternating background for better readability
                card_style = SECONDARY if i % 2 == 0 else DARK
                card = ttk.Frame(self.fields_frame, bootstyle=card_style)
                card.pack(fill="x", pady=2, padx=5)

                # Parameter info
                info_frame = ttk.Frame(card)
                info_frame.pack(fill="x", padx=15, pady=8)

                # Label with better formatting
                label_text = f"{label}"
                range_text = f"Range: {min_val} - {max_val}"
                
                text_frame = ttk.Frame(info_frame)
                text_frame.pack(side="left", anchor="w", fill="x", expand=True)
                
                ttk.Label(
                    text_frame, 
                    text=label_text, 
                    bootstyle=INVERSE,
                    font=("Segoe UI", 10, "bold")
                ).pack(anchor="w")
                
                ttk.Label(
                    text_frame, 
                    text=range_text, 
                    bootstyle=SECONDARY,
                    font=("Segoe UI", 8)
                ).pack(anchor="w", pady=(2, 0))

                # Input field with spinbox and unit - better aligned
                input_frame = ttk.Frame(info_frame)
                input_frame.pack(side="right", anchor="e")

                # Create spinbox
                entry, spinbox_frame = self.create_spinbox(input_frame, key, default, min_val, max_val, dtype)
                spinbox_frame.pack(side="left", padx=5)

                # Unit label
                unit = "m" if any(unit in key for unit in ['radius', 'height', 'depth', 'elev', 'thick', 'width', 'length', 'diam', 'gap']) else ""
                if unit:
                    ttk.Label(
                        input_frame, 
                        text=unit, 
                        bootstyle=SECONDARY,
                        font=("Segoe UI", 9, "bold")
                    ).pack(side="left", padx=2)

                # Store validation info
                self.validation_data[key] = {
                    'dtype': dtype,
                    'min': min_val,
                    'max': max_val,
                    'default': default
                }

                # Bind validation
                entry.bind('<FocusOut>', lambda e, k=key: self.validate_field(k))
                entry.bind('<Return>', lambda e, k=key: self.validate_field(k))

                self.entries[key] = entry

    def draw_component_preview(self):
        """Draw component preview on canvas"""
        self.preview_canvas.delete("all")
        comp = self.current_comp or "⚡ Generator"
        
        w, h = 350, 180
        center_x, center_y = w // 2, h // 2
        
        if "Generator" in comp:
            # Draw generator with more detail
            self.preview_canvas.create_oval(center_x-70, center_y-35, center_x+70, center_y+35, 
                                          outline="#00d4ff", width=3)
            self.preview_canvas.create_line(center_x, center_y-35, center_x, center_y+35, 
                                          fill="#ff6b9d", width=3)
            # Base
            self.preview_canvas.create_rectangle(center_x-50, center_y+35, center_x+50, center_y+45,
                                               outline="#00ff9d", width=2)
            self.preview_canvas.create_text(center_x, h-12, text="GENERATOR ASSEMBLY", 
                                          fill="#a0aec0", font=("Arial", 10, "bold"))
            
        elif "Turbine" in comp:
            # Draw turbine with more detail
            self.preview_canvas.create_oval(center_x-55, center_y-25, center_x+55, center_y+25, 
                                          outline="#ff6b9d", width=3)
            # Blades
            for i in range(8):
                angle = i * 45
                x1 = center_x + 30 * math.cos(math.radians(angle))
                y1 = center_y + 30 * math.sin(math.radians(angle))
                x2 = center_x + 50 * math.cos(math.radians(angle))
                y2 = center_y + 50 * math.sin(math.radians(angle))
                self.preview_canvas.create_line(x1, y1, x2, y2, 
                                              fill="#00d4ff", width=2)
            # Spiral casing
            self.preview_canvas.create_arc(center_x-70, center_y-40, center_x+10, center_y+40,
                                         start=90, extent=180, outline="#00ff9d", width=2, style="arc")
            self.preview_canvas.create_text(center_x, h-12, text="TURBINE SYSTEM", 
                                          fill="#a0aec0", font=("Arial", 10, "bold"))
            
        elif "Intake" in comp:
            # Draw intake structure with more detail
            self.preview_canvas.create_rectangle(center_x-90, center_y-15, center_x+90, center_y+15, 
                                               outline="#00ff9d", width=3)
            # Bays with gates
            for i in range(3):
                x = center_x - 75 + i * 50
                self.preview_canvas.create_rectangle(x, center_y-12, x+30, center_y+12, 
                                                   outline="#00d4ff", width=2)
                # Gate
                self.preview_canvas.create_rectangle(x+10, center_y-8, x+20, center_y+8,
                                                   outline="#ff6b9d", width=1, fill="#ff6b9d")
            # Support structure
            self.preview_canvas.create_line(center_x-90, center_y+15, center_x-60, center_y+30, 
                                          fill="#00d4ff", width=2)
            self.preview_canvas.create_line(center_x+90, center_y+15, center_x+60, center_y+30, 
                                          fill="#00d4ff", width=2)
            self.preview_canvas.create_text(center_x, h-12, text="INTAKE STRUCTURE", 
                                          fill="#a0aec0", font=("Arial", 10, "bold"))

    def validate_field(self, key):
        """Validate individual field"""
        entry = self.entries[key]
        value = entry.get().strip()
        validation = self.validation_data[key]
        
        try:
            if validation['dtype'] == 'int':
                value_int = int(value)
                if value_int < validation['min'] or value_int > validation['max']:
                    raise ValueError(f"Value must be between {validation['min']} and {validation['max']}")
                # Valid
                entry.configure(bootstyle=SUCCESS)
                return True
                
            elif validation['dtype'] == 'float':
                value_float = float(value)
                if value_float < validation['min'] or value_float > validation['max']:
                    raise ValueError(f"Value must be between {validation['min']} and {validation['max']}")
                # Valid
                entry.configure(bootstyle=SUCCESS)
                return True
                
        except ValueError as e:
            # Invalid
            entry.configure(bootstyle=DANGER)
            self.show_error_tooltip(entry, str(e))
            return False
        
        return True

    def show_error_tooltip(self, widget, message):
        """Show temporary error tooltip"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{widget.winfo_rootx()}+{widget.winfo_rooty() + 25}")
        
        label = ttk.Label(
            tooltip, 
            text=message, 
            bootstyle=DANGER,
            padding=(10, 5),
            font=("Segoe UI", 9)
        )
        label.pack()
        
        widget.after(3000, tooltip.destroy)

    def browse_export(self):
        folder = filedialog.askdirectory(title="Select Export Folder")
        if folder:
            self.export_entry.delete(0, tk.END)
            self.export_entry.insert(0, folder)

    def validate_all_fields(self):
        """Validate all fields before generation"""
        valid = True
        for key in self.entries:
            if not self.validate_field(key):
                valid = False
        return valid

    def generate_model(self):
        if not self.current_comp:
            messagebox.showerror("Error", "Please select a component first!")
            return

        export_folder = self.export_entry.get()
        if not export_folder:
            messagebox.showerror("Error", "Please select an export folder")
            return

        if not self.validate_all_fields():
            messagebox.showerror("Validation Error", 
                               "Please fix all validation errors before generating.")
            return

        # Convert entries to numeric values
        values = {}
        for k, entry in self.entries.items():
            val = entry.get().strip()
            validation = self.validation_data[k]
            
            try:
                if validation['dtype'] == 'int':
                    values[k] = int(val)
                elif validation['dtype'] == 'float':
                    values[k] = float(val)
            except:
                values[k] = validation['default']

        # Clean component name for Blender
        clean_component = self.current_comp.replace("⚡", "").replace("🌪", "").replace("🌊", "").strip().lower().replace(" ", "_")

        data = {
            "component": clean_component,
            "values": values,
            "export_folder": export_folder
        }

        # Save JSON configuration
        config_path = os.path.join(export_folder, "config.json")
        try:
            with open(config_path, "w") as f:
                json.dump(data, f, indent=4)
            
            # Update UI
            self.progress.start()
            self.generate_button.config(state="disabled")
            self.status_label.config(text="🔄 Generating 3D model...")
            self.root.update()
            
            # Run Blender
            blender_path = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
            script_path = os.path.join(os.getcwd(), "hydro_master.py")

            result = subprocess.run([
                blender_path, 
                "--background", 
                "--python", script_path, 
                "--", 
                config_path
            ], capture_output=True, text=True)
            
            self.progress.stop()
            
            if result.returncode == 0:
                self.status_label.config(text="✅ Model generated successfully!")
                messagebox.showinfo(
                    "Success", 
                    f"{self.current_comp} model generated successfully!\n\n"
                    f"Location: {export_folder}"
                )
            else:
                error_msg = result.stderr if result.stderr else "Unknown Blender error"
                raise Exception(f"Blender error: {error_msg}")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="❌ Generation failed")
            messagebox.showerror("Generation Error", f"Failed to generate model:\n{str(e)}")
        finally:
            self.generate_button.config(state="normal")
            self.root.after(3000, lambda: self.status_label.config(text="✅ System Ready"))


if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = HydroUI(root)
    root.mainloop()