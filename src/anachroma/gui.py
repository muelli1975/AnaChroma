from __future__ import annotations
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

from . import __version__
from .engine import Cancelled
from .export import SIZE_LABELS, SizeSpec, export_jobs
from .export_selection import ExportSelection
from .inputs import discover
from .i18n import translate, translate_widgets
from .matrices import BUILTINS
from .preset_editor import PresetEditor
from .presets import load_presets, save_presets
from .resources import app_dir, find_tool, resource_dir, user_dir
from .settings import load_settings, save_settings
from .theme import (APP_BG, BORDER, DISABLED, GOLD, GOLD_HOVER, MUTED, PANEL_BG, SECONDARY_BG,
                    TEXT, HOVER_BG, FONT_FAMILY, PREVIEW_BG, configure_theme, preview_size, clear_preview)
from .worker import PreviewWorker, run_jobs


class AnaChromaApp(ctk.CTk):
    def __init__(self):
        configure_theme()
        super().__init__()
        self.title(f"AnaChroma {__version__.removesuffix('.0')}")
        icon = resource_dir() / "assets" / "anachroma.ico"
        if icon.is_file():
            import sys
            if sys.platform == "win32":
                self.iconbitmap(str(icon))
            else:
                with Image.open(icon) as source:
                    self._icon_image = ImageTk.PhotoImage(source.copy(), master=self)
                self.iconphoto(True, self._icon_image)
        self.geometry("1180x820")
        self.minsize(940, 680)
        self.configure(fg_color=APP_BG)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.events = Queue()
        self.preview_worker = PreviewWorker(self.events)
        self.preview_id = 0
        self.preview_after = None
        self.resize_after = None
        self.preview_edge = 1024
        self.preview_image = None
        self.preview_photo = None
        self.closed = False
        self.inputs = None
        self.demo_path = resource_dir() / "assets" / "anachroma.jpg"
        self.index = 0
        self.scan_id = 0
        self.scan_cancel = Event()
        self.scanning = False
        self.batch_cancel = Event()
        self.batch_running = False
        self.batch_thread = None
        self.editor = None
        self.export_ids = None
        self.export_dialog = None
        self.current_method_id = BUILTINS[0].id
        self.draft = None
        self.settings_path = user_dir()/"settings.json"
        self.presets_path = user_dir()/"presets.json"
        self.settings = load_settings(self.settings_path)
        self.language = self.settings.language
        self.presets_error = ""
        self.presets_notices = []
        try:
            self.custom = load_presets(self.presets_path, self.presets_notices)
        except (OSError, ValueError) as exc:
            self.custom = []
            self.presets_error = str(exc)
        self.method_var = tk.StringVar()
        self.size_var = tk.StringVar(value="2048 lange Seite")
        self.size_display = tk.StringVar(value="2048 lange Seite")
        self.edge_var = tk.StringVar(value="long")
        self.pixel_var = tk.StringVar(value="2048")
        self.recursive = tk.BooleanVar(value=False)
        self.quality95 = tk.BooleanVar(value=False)
        self.default_output = user_dir()/"output"
        self.use_program_output = tk.BooleanVar(value=self.settings.use_program_output)
        self.output_var = tk.StringVar(value=self.settings.output)
        self._build()
        self._translate_ui()
        self._refresh_methods(BUILTINS[0].id)
        self._state()
        self.bind("<KeyPress>", self._key)
        self.after(50, self._pump)
        self.after(200, self._startup_notes)
        self.request_preview()

    def t(self, text):
        return translate(text, self.language)

    def _translate_ui(self):
        skip = (self.input_label, self.output_label, self.output_status, self.filename, self.preview_note, self.preview_label,
                self.status, self.action_button)
        translate_widgets(self, self.language, skip)
        self.size_names = {self.t(label): label for label in SIZE_LABELS}
        self.size_menu.configure(values=list(self.size_names))
        self.size_display.set(self.t(self.size_var.get()))
        if self.editor is not None:
            self.editor.translate_ui()

    def _language_changed(self, value):
        selected = self.selected_method().id
        self.language = "en" if value == "English" else "de"
        self.settings.language = self.language
        self._persist_settings()
        self._translate_ui()
        self._refresh_methods(selected)
        self._state()
        self.request_preview()

    def _button(self, parent, text, command, primary=False, **kwargs):
        options = dict(height=32)
        if primary:
            options.update(border_color=GOLD, text_color=GOLD_HOVER,
                           hover_color=GOLD_HOVER, font=(FONT_FAMILY, 14, "bold"))
        options.update(kwargs)
        button = ctk.CTkButton(parent, text=text, command=command, **options)
        if primary:
            button.bind("<Enter>", lambda _: self.after_idle(lambda: self._style_primary_button(button, hover=True)), add="+")
            button.bind("<Leave>", lambda _: self.after_idle(lambda: self._style_primary_button(button)), add="+")
        return button

    def _style_primary_button(self, button, hover=False):
        if not button.winfo_exists():
            return
        enabled = button.cget("state") == "normal"
        hovered = enabled and hover
        button.configure(
            fg_color=GOLD_HOVER if hovered else SECONDARY_BG,
            hover_color=GOLD_HOVER if enabled else SECONDARY_BG,
            text_color=APP_BG if hovered else GOLD_HOVER if enabled else DISABLED,
            border_color=GOLD_HOVER if hovered else GOLD if enabled else BORDER,
        )

    def _section(self, parent, text):
        frame = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=10)
        frame.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(frame, text=text, font=(FONT_FAMILY, 16, "bold"), anchor="w").pack(fill="x", padx=12, pady=(8, 4))
        return frame

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        side = ctk.CTkFrame(self, width=338, fg_color=SECONDARY_BG, corner_radius=0)
        side.grid(row=0, column=0, sticky="ns")
        sidebar = ctk.CTkScrollableFrame(side, width=310, fg_color=SECONDARY_BG, corner_radius=0)
        sidebar.pack(fill="both", expand=True)
        heading = ctk.CTkFrame(sidebar, fg_color="transparent")
        heading.pack(fill="x", padx=12, pady=(12, 0))
        ctk.CTkLabel(heading, text="AnaChroma", font=(FONT_FAMILY, 26, "bold"), text_color=GOLD_HOVER).pack(side="left")
        self.language_menu = ctk.CTkOptionMenu(heading, values=["Deutsch", "English"], width=94,
                                              command=self._language_changed)
        self.language_menu.pack(side="right")
        self.language_menu.set("English" if self.language == "en" else "Deutsch")
        ctk.CTkLabel(sidebar, text="Hochwertige Anaglyphen aus SBS-Bildern", text_color=MUTED, wraplength=285, justify="left")\
            .pack(anchor="w", padx=12, pady=(0, 8))
        entry = self._section(sidebar, "Eingabe")
        load_row = ctk.CTkFrame(entry, fg_color="transparent")
        load_row.pack(fill="x", padx=12, pady=4)
        load_row.grid_columnconfigure((0, 1), weight=1)
        self.file_button = self._button(load_row, "Einzelbild…", self.open_file, width=120)
        self.file_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.folder_button = self._button(load_row, "Bildordner…", self.open_folder, width=120)
        self.folder_button.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self.input_label = ctk.CTkLabel(entry, text="Keine Bilder gewählt", anchor="w", justify="left",
                                       text_color=MUTED, wraplength=266)
        self.input_label.pack(fill="x", padx=12, pady=4)
        self.recursive_box = ctk.CTkCheckBox(entry, text="Unterordner mitverarbeiten", variable=self.recursive,
                                          fg_color=GOLD, command=self._recursive_changed)
        self.recursive_box.pack(anchor="w", padx=12, pady=(8, 12))
        output = self._section(sidebar, "Ausgabe")
        self.output_checkbox = ctk.CTkCheckBox(output, text="Unterordner im Programmordner\nverwenden",
            variable=self.use_program_output, command=self._output_changed, fg_color=GOLD)
        self.output_checkbox.pack(anchor="w", padx=12, pady=(0, 8))
        self.custom_output_label = ctk.CTkLabel(output, text="Eigener Ausgabeordner", text_color=MUTED, anchor="w")
        self.custom_output_label.pack(fill="x", padx=12, pady=(0, 3))
        self.output_button = self._button(output, "Auswählen", self.choose_output)
        self.output_button.pack(fill="x", padx=12, pady=4)
        self.output_label = ctk.CTkLabel(output, text="–", text_color=DISABLED,
                                       wraplength=270, justify="left", anchor="w")
        self.output_label.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(output, text="Ausgabeziel", anchor="w").pack(fill="x", padx=12, pady=(4, 0))
        self.output_status = ctk.CTkLabel(output, text="", text_color=TEXT,
                                        wraplength=270, justify="left", anchor="w")
        self.output_status.pack(fill="x", padx=12, pady=(0, 4))
        self.quality_box = ctk.CTkCheckBox(output, text="JPEG-Qualität 95 für Druck/Archiv", variable=self.quality95, fg_color=GOLD)
        self.quality_box.pack(anchor="w", padx=12, pady=(8, 12))
        methods = self._section(sidebar, "Anaglyph")
        ctk.CTkLabel(methods, text="Verfahren", anchor="w").pack(fill="x", padx=12)
        self.method_menu = ctk.CTkOptionMenu(methods, variable=self.method_var, values=[""],
                                           command=self._method_changed)
        self.method_menu.pack(fill="x", padx=12, pady=4)
        self.edit_button = self._button(methods, "Bearbeiten…", self.edit_custom)
        self.edit_button.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(methods, text="Größe", anchor="w").pack(fill="x", padx=12, pady=(8, 0))
        self.size_menu = ctk.CTkOptionMenu(methods, variable=self.size_display, values=list(SIZE_LABELS),
                                         command=self._size_selected)
        self.size_menu.pack(fill="x", padx=12, pady=4)
        self.custom_size = ctk.CTkFrame(methods, fg_color="transparent")
        self.long_radio = ctk.CTkRadioButton(self.custom_size, text="lange Seite", variable=self.edge_var, value="long", fg_color=GOLD)
        self.long_radio.pack(anchor="w", pady=3)
        self.short_radio = ctk.CTkRadioButton(self.custom_size, text="kurze Seite", variable=self.edge_var, value="short", fg_color=GOLD)
        self.short_radio.pack(anchor="w", pady=3)
        size_row = ctk.CTkFrame(self.custom_size, fg_color="transparent")
        size_row.pack(fill="x", pady=4)
        self.pixel_entry = ctk.CTkEntry(size_row, textvariable=self.pixel_var, width=125)
        self.pixel_entry.pack(side="left")
        ctk.CTkLabel(size_row, text="px").pack(side="left", padx=8)
        self.size_anchor = ctk.CTkFrame(methods, height=6, fg_color="transparent")
        self.size_anchor.pack(fill="x")
        jobs = self._section(side, "Verarbeitung")
        export_row = ctk.CTkFrame(jobs, fg_color="transparent")
        export_row.pack(fill="x", padx=12, pady=(0, 4))
        self.export_summary = ctk.CTkLabel(export_row, text="", anchor="w", justify="left", wraplength=175)
        self.export_summary.pack(side="left", fill="x", expand=True)
        self.export_button = self._button(export_row, "Auswählen", self.choose_export_methods, width=84)
        self.export_button.pack(side="right", padx=(4, 0))
        self.action_button = self._button(jobs, "Bild speichern", self.primary_action, primary=True, height=38)
        self.action_button.pack(fill="x", padx=12, pady=4)
        self.save_button = self._button(jobs, "Aktuelles Bild speichern", lambda: self.start_export(False))
        self.save_button.pack(fill="x", padx=12, pady=4)
        self.all_button = self.action_button
        self.cancel_button = self._button(jobs, "Abbrechen", self.cancel_job)
        self.cancel_button.pack(fill="x", padx=12, pady=(4, 12))
        right = ctk.CTkFrame(self, fg_color=APP_BG, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)
        self.filename = ctk.CTkLabel(right, text="Kein Bild geladen", anchor="w", font=(FONT_FAMILY, 16), wraplength=760)
        self.filename.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        self.preview_note = ctk.CTkLabel(right, text="", anchor="w", text_color=MUTED)
        self.preview_note.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.preview_panel = ctk.CTkFrame(right, fg_color=PREVIEW_BG, corner_radius=0)
        self.preview_panel.grid(row=2, column=0, sticky="nsew")
        self.preview_panel.grid_columnconfigure(0, weight=1)
        self.preview_panel.grid_rowconfigure(0, weight=1)
        self.preview_label = tk.Label(self.preview_panel, text="Datei oder Ordner laden", fg=MUTED, bg=PREVIEW_BG,
                                      font=(FONT_FAMILY, 13), borderwidth=0, highlightthickness=0)
        self.preview_label.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.preview_panel.bind("<Configure>", self._preview_resize)
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.preview_label.bind(sequence, self._wheel)
        nav = ctk.CTkFrame(right, fg_color="transparent")
        nav.grid(row=3, column=0, sticky="ew", pady=10)
        self.previous_button = self._button(nav, "Vorheriges Bild", lambda: self.navigate(-1), width=150)
        self.previous_button.pack(side="left")
        self.next_button = self._button(nav, "Nächstes Bild", lambda: self.navigate(1), width=150)
        self.next_button.pack(side="right")
        self.shortcuts_button = self._button(nav, "Tastenkürzel…", self.show_shortcuts, width=140, height=26,
            fg_color="transparent", border_width=0, text_color=MUTED, hover_color=SECONDARY_BG)
        self.shortcuts_button.pack(side="left", expand=True, padx=8)
        footer = ctk.CTkFrame(self, fg_color=SECONDARY_BG, corner_radius=0)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.progress = ctk.CTkProgressBar(footer, progress_color=GOLD)
        self.progress.pack(fill="x", padx=16, pady=(12, 4))
        self.progress.set(0)
        self.status = ctk.CTkLabel(footer, text="Bereit.", anchor="w", wraplength=1080, justify="left")
        self.status.pack(fill="x", padx=16, pady=(0, 10))
        ico = resource_dir()/"assets"/"anachroma.ico"
        if ico.is_file():
            try:
                self.iconbitmap(str(ico))
            except tk.TclError:
                pass

    def _startup_notes(self):
        if self.presets_error:
            messagebox.showwarning(self.t("Eigene Verfahren"), self.t(self.presets_error + "\nDie Datei bleibt unverändert; Speichern ist bis zur Klärung gesperrt."), parent=self)
        elif self.presets_notices:
            messagebox.showwarning(self.t("Eigene Verfahren"),
                self.t("Diese älteren Verfahren enthalten Helligkeits-/Kontrastanpassungen, die in Version 1.0 entfallen:")
                + "\n" + "\n".join(self.presets_notices) + "\n\n"
                + self.t("Matrizen und RGB-Korrektur bleiben erhalten. Beim Speichern wird die ursprüngliche Preset-Datei als .pre-1.0.bak gesichert."), parent=self)
        missing = [n for n in ("ExifTool" if not find_tool("exiftool") else "", "CIELab" if not find_tool("cielab") else "") if n]
        if missing:
            self.status.configure(text=self.t("Bereit. Externe Tools nicht gefunden: " + ", ".join(missing) + "."))

    def _refresh_methods(self, selected):
        self.methods = {}
        for n, method in enumerate(BUILTINS, 1):
            self.methods[f"{n}  {method.name}"] = method
        for method in self.custom:
            self.methods[self.t(f"Eigene: {method.name}")] = method
        self.method_menu.configure(values=list(self.methods)[:len(BUILTINS)]
            + [self.t("Eigenes Verfahren anlegen…")] + list(self.methods)[len(BUILTINS):])
        label = next((name for name, method in self.methods.items() if method.id == selected), next(iter(self.methods)))
        self.method_var.set(label)
        self.current_method_id = self.methods[label].id
        if self.export_ids is not None:
            valid = {m.id for m in self.methods.values()}
            self.export_ids = tuple(i for i in self.export_ids if i in valid) or None
        self._refresh_export_selection()

    def selected_method(self):
        return self.methods.get(self.method_var.get()) or next(
            m for m in self.methods.values() if m.id == self.current_method_id)

    def _method_changed(self, value=None):
        if value == self.t("Eigenes Verfahren anlegen…"):
            self._refresh_methods(self.current_method_id)
            self.create_custom()
            return
        self.current_method_id = self.selected_method().id
        self._state()
        self.request_preview()

    def _size_changed(self):
        self.size_display.set(self.t(self.size_var.get()))
        if self.size_var.get() == "Benutzerdefiniert":
            self.custom_size.pack(fill="x", padx=12, pady=4, before=self.size_anchor)
        else:
            self.custom_size.pack_forget()

    def _size_selected(self, value):
        self.size_var.set(self.size_names[value])
        self._size_changed()

    def _state(self):
        busy = self.batch_running or self.scanning
        for widget in (self.file_button, self.folder_button, self.recursive_box, self.output_checkbox,
                       self.size_menu, self.quality_box, self.pixel_entry, self.long_radio, self.short_radio,
                       self.language_menu, self.export_button, self.shortcuts_button):
            widget.configure(state="disabled" if busy else "normal")
            if isinstance(widget, ctk.CTkCheckBox):
                widget.configure(fg_color=DISABLED if busy else GOLD,
                                 hover_color=DISABLED if busy else GOLD_HOVER)
        for widget in (self.method_menu,):
            widget.configure(state="disabled" if busy or self.editor is not None else "normal")
        self.export_button.configure(state="disabled" if busy or self.editor is not None else "normal")
        self.edit_button.configure(state="normal" if not busy and self.editor is None and not self.selected_method().builtin else "disabled")
        for widget in (self.save_button, self.action_button):
            widget.configure(state="normal" if self.inputs and not busy and self.editor is None else "disabled")
        self._style_primary_button(self.action_button)
        folder_mode = self.inputs is not None and self.inputs.folder_input
        self.action_button.configure(text=self.t("Alle verarbeiten" if folder_mode else "Bild speichern"))
        if folder_mode:
            self.save_button.pack(fill="x", padx=12, pady=4, before=self.cancel_button)
        else:
            self.save_button.pack_forget()
        if self.inputs:
            mode = f"Bildordner · {len(self.inputs.files)} Bilder" if folder_mode else "Einzelbild"
            path = self.inputs.root if folder_mode else self.inputs.files[self.index]
            self.input_label.configure(text=self.t(f"{self.t(mode)}\n{path}"))
        else:
            self.input_label.configure(text=self.t("Keine Bilder gewählt"))
        self._refresh_output()
        self._refresh_export_selection()
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.previous_button.configure(state="normal" if self.inputs and self.index > 0 and not busy else "disabled")
        self.next_button.configure(state="normal" if self.inputs and self.index < len(self.inputs.files)-1 and not busy else "disabled")

    def open_file(self):
        selected = filedialog.askopenfilename(parent=self, title=self.t("SBS-Bild wählen"), initialdir=self.settings.last_input or None,
            filetypes=[(self.t("SBS-Bilder"), "*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp"), (self.t("Alle Dateien"), "*")])
        if selected:
            self.load_input(Path(selected))

    def open_folder(self):
        selected = filedialog.askdirectory(parent=self, title=self.t("SBS-Bildordner wählen"), initialdir=self.settings.last_input or None)
        if selected:
            self.load_input(Path(selected))

    def choose_output(self):
        if self.batch_running or self.scanning:
            return
        selected = filedialog.askdirectory(parent=self, title=self.t("Ausgabeordner wählen"),
            initialdir=self.output_var.get() or str(self.default_output))
        if selected:
            self.output_var.set(selected)
            self.use_program_output.set(False)
            self._output_changed()

    def _output_changed(self):
        if self.batch_running or self.scanning:
            return
        self.settings.output = self.output_var.get()
        self.settings.use_program_output = self.use_program_output.get()
        self._persist_settings()
        if self.inputs and self.inputs.folder_input:
            self.load_input(self.inputs.root)
        else:
            self._state()

    def _effective_output(self):
        if self.use_program_output.get():
            return self.default_output.resolve()
        return Path(self.output_var.get()).expanduser().resolve() if self.output_var.get().strip() else None

    def _refresh_output(self):
        text = self.output_var.get() or "–"
        self.output_label.configure(text=text)
        target = self._effective_output()
        self.output_status.configure(text=str(target) if target is not None
                                     else self.t("Kein eigener Ausgabeordner gewählt"))
        custom_active = not self.use_program_output.get() and not (self.batch_running or self.scanning)
        self.output_button.configure(state="disabled" if self.batch_running or self.scanning else "normal")
        self.custom_output_label.configure(text_color=TEXT if custom_active else DISABLED)
        self.output_label.configure(text_color=TEXT if custom_active else DISABLED)

    def primary_action(self):
        self.start_export(bool(self.inputs and self.inputs.folder_input))

    def _recursive_changed(self):
        if self.inputs:
            path = self.inputs.root if self.inputs.folder_input else self.inputs.files[self.index]
            self.load_input(path)

    def _persist_settings(self):
        self.settings.recursive = False
        try:
            save_settings(self.settings_path, self.settings)
        except OSError as exc:
            self.status.configure(text=self.t(f"Einstellungen konnten nicht gespeichert werden: {exc}"))

    def load_input(self, path):
        self.scan_id += 1
        identifier = self.scan_id
        self.scan_cancel.set()
        cancel = self.scan_cancel = Event()
        self.scanning = True
        self.preview_id += 1
        self.preview_worker.active_cancel.set()
        recursive, output = self.recursive.get(), self._effective_output()
        suffixes = tuple(m.suffix for m in self.custom)
        self.status.configure(text=self.t("Suche SBS-Bilder..."))
        self._state()
        def scan():
            try:
                found = discover(path, recursive, (output,) if output is not None else (), cancel, suffixes)
                self.events.put(("scan", identifier, found))
            except Cancelled:
                self.events.put(("scan_cancelled", identifier))
            except Exception as exc:
                self.events.put(("scan_error", identifier, str(exc)))
        Thread(target=scan, daemon=True, name="anachroma-inputs").start()

    def navigate(self, delta, absolute=None):
        if not self.inputs or self.scanning or self.batch_running:
            return
        self.index = min(max(absolute if absolute is not None else self.index+delta, 0), len(self.inputs.files)-1)
        self._state()
        self.request_preview()

    def show_shortcuts(self):
        if self.batch_running or self.scanning:
            return
        messagebox.showinfo(self.t("Tastenkürzel"), self.t("Links / Rechts oder Bild auf / Bild ab: vorheriges / nächstes Bild\nStrg + Links / Rechts: vorheriges / nächstes Vorschauverfahren"), parent=self)

    def _key(self, event):
        if event.widget.winfo_toplevel() != self or self.batch_running or self.scanning:
            return None
        widget = event.widget
        while widget != self:
            if widget.winfo_class() in {"Entry", "TEntry", "Text", "Spinbox"} or isinstance(widget, ctk.CTkSlider):
                return None
            widget = widget.master
        if event.state & 4:
            if event.keysym in {"Left", "Right"} and self.editor is None:
                methods = list(self.methods.values())
                index = next(i for i, m in enumerate(methods) if m.id == self.selected_method().id)
                selected = methods[(index + (-1 if event.keysym == "Left" else 1)) % len(methods)]
                self._refresh_methods(selected.id)
                self._method_changed()
                return "break"
            return None
        if event.state & (8 | 131072):
            return None
        mapping = {"Left": -1, "Prior": -1, "Right": 1, "Next": 1}
        if event.keysym in mapping:
            self.navigate(mapping[event.keysym])
            return "break"

    def _wheel(self, event):
        if getattr(event, "num", None) in (4, 5):
            delta = -1 if event.num == 4 else 1
        else:
            if not event.delta:
                return "break"
            delta = -1 if event.delta > 0 else 1
        self.navigate(delta)
        return "break"

    def request_preview(self):
        path = self.preview_path()
        if path is None:
            return
        if self.batch_running or self.scanning:
            return
        self.preview_id += 1  # invalidate results immediately, even during throttle
        self.filename.configure(text=self.t(f"{self.index+1}/{len(self.inputs.files)} · {path.name}" if self.inputs
                                else "AnaChroma · Beispielbild"))
        method = self.draft or self.selected_method()
        label = "Entwurf · " if self.draft is not None else ""
        self.preview_note.configure(text=self.t(label + method.name))
        if self.preview_after is None:
            self.preview_after = self.after(180, self._submit_preview)

    def preview_path(self):
        if self.inputs:
            return self.inputs.files[self.index]
        return self.demo_path if self.demo_path.is_file() else None

    def _submit_preview(self):
        self.preview_after = None
        path = self.preview_path()
        if self.closed or path is None:
            return
        method = self.draft or self.selected_method()
        if method.mode == "cielab" and find_tool("cielab") is None:
            clear_preview(self.preview_label, self.t("CIELab nicht gefunden.\nBitte ein anderes Verfahren wählen."))
            self.preview_image = None
            self.preview_photo = None
            self.status.configure(text=self.t("CIELab nicht gefunden. Andere Verfahren sind verfügbar."))
            self._state()
            return
        self.preview_edge = self._preview_limit(method)
        self.preview_worker.request(self.preview_id, path, method, self.preview_edge)
        if not self.batch_running:
            self.status.configure(text=self.t("CIELab-Vorschau wird erzeugt..." if method.mode == "cielab" else "Berechne Vorschau..."))

    def _fit_preview(self):
        if self.preview_image is None:
            return
        image = self.preview_image
        size, border = preview_size(image.size, (self.preview_panel.winfo_width(), self.preview_panel.winfo_height()))
        self.preview_label.grid_configure(padx=border, pady=border)
        self.preview_photo = ImageTk.PhotoImage(image.resize(size, Image.Resampling.LANCZOS), master=self)
        self.preview_label.configure(image=self.preview_photo, text=self.t(""))

    def _preview_limit(self, method):
        if method.mode == "cielab":
            return 1024
        if not self.preview_panel.winfo_ismapped():
            return 1024
        return min(1600, max(self.preview_panel.winfo_width(), self.preview_panel.winfo_height()))

    def _preview_resize(self, _):
        self._fit_preview()
        if self.resize_after is not None:
            self.after_cancel(self.resize_after)
        self.resize_after = self.after(180, self._preview_resized)

    def _preview_resized(self):
        self.resize_after = None
        if not self.closed and self.preview_path() is not None:
            if self._preview_limit(self.draft or self.selected_method()) != self.preview_edge:
                self.request_preview()

    def create_custom(self):
        method = self.selected_method()
        if not method.editable:
            messagebox.showinfo(self.t("Eigenes Verfahren"), self.t("Dieses Spezialverfahren benötigt zusätzliche Rechenschritte.\nDer Editor beginnt stattdessen mit der einfachen Color-Matrix."), parent=self)
            method = BUILTINS[9]
        if self.batch_running or self.scanning or self.editor is not None:
            return
        self.editor = PresetEditor(self, method)
        self._state()

    def edit_custom(self):
        if self.batch_running or self.scanning or self.editor is not None:
            return
        self.editor = PresetEditor(self, self.selected_method(), existing=True)
        self._state()

    def editor_preview(self, method):
        self.draft = method
        self.request_preview()

    def save_custom(self, method):
        if self.presets_error:
            raise ValueError("Die vorhandene Preset-Datei ist ungültig und wird nicht überschrieben.")
        methods = [m for m in self.custom if m.id != method.id] + [method]
        save_presets(self.presets_path, methods)
        self.custom = methods
        self._refresh_methods(method.id)

    def delete_custom(self, identifier):
        if self.presets_error:
            raise ValueError("Die vorhandene Preset-Datei wird nicht überschrieben.")
        methods = [m for m in self.custom if m.id != identifier]
        save_presets(self.presets_path, methods)
        self.custom = methods
        self._refresh_methods(BUILTINS[0].id)

    def finish_editor(self):
        self.editor = None
        self.draft = None
        self._state()
        self.request_preview()

    def output_methods(self):
        if self.export_ids is None:
            return (self.selected_method(),)
        chosen = set(self.export_ids)
        return tuple(m for m in self.methods.values() if m.id in chosen)

    def _refresh_export_selection(self):
        if not hasattr(self, "export_summary"):
            return
        text = "Aktuelles Verfahren" if self.export_ids is None else f"{len(self.export_ids)} Verfahren gewählt"
        self.export_summary.configure(text=self.t("Ausgabeverfahren") + ":\n" + self.t(text))

    def choose_export_methods(self):
        if self.batch_running or self.scanning or self.editor is not None or self.export_dialog is not None:
            return
        self.export_dialog = ExportSelection(self)

    def start_export(self, all_images):
        if not self.inputs or self.batch_running or self.scanning or self.editor is not None:
            return
        try:
            pixels = int(self.pixel_var.get()) if self.size_var.get() == "Benutzerdefiniert" else 2048
            size = SizeSpec(self.size_var.get(), self.edge_var.get(), pixels)
            size.dimensions((1920, 1080))  # validate custom input before the worker
            methods = self.output_methods()
            if any(m.mode == "cielab" for m in methods) and find_tool("cielab") is None:
                raise ValueError("CIELab ist nicht installiert. Externes Programm unter tools/cielab bereitstellen.")
            files = self.inputs.files if all_images else (self.inputs.files[self.index],)
            output = self._effective_output()
            if output is None:
                raise ValueError("Bitte einen Ausgabeordner auswählen.")
            jobs = export_jobs(self.inputs, files, output, methods)
        except (ValueError, OSError) as exc:
            messagebox.showerror(self.t("Verarbeitung"), self.t(str(exc)), parent=self)
            return
        self.batch_running = True
        self.preview_id += 1
        self.preview_worker.active_cancel.set()
        if self.preview_after is not None:
            self.after_cancel(self.preview_after)
            self.preview_after = None
        cancel = self.batch_cancel = Event()
        quality = 95 if self.quality95.get() else 90
        self.progress.set(0)
        self.status.configure(text=self.t("Alle Bilder verarbeiten..." if all_images else "Speichere aktuelles Bild..."))
        self._state()
        def run():
            try:
                result = run_jobs(jobs, size, quality, cancel, self.events.put)
                self.events.put(("batch_done", result))
            except Exception as exc:
                self.events.put(("batch_error", str(exc)))
        self.batch_thread = Thread(target=run, daemon=True, name="anachroma-export")
        self.batch_thread.start()

    def cancel_job(self):
        self.batch_cancel.set()
        self.scan_cancel.set()
        self.status.configure(text=self.t("Abbruch wird ausgeführt..."))

    def _pump(self):
        if self.closed:
            return
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind.startswith("scan") and event[1] == self.scan_id:
                    self.scanning = False
                    if kind == "scan":
                        self.inputs = event[2]
                        self.index = self.inputs.selected
                        self.settings.last_input = str(self.inputs.root)
                        self._persist_settings()
                        self.request_preview()
                    elif kind == "scan_error":
                        self.status.configure(text=self.t(event[2]))
                        messagebox.showerror(self.t("Eingabe"), self.t(event[2]), parent=self)
                    self._state()
                elif kind == "preview" and event[1] == self.preview_id:
                    self.preview_image = event[2]
                    self._fit_preview()
                    if not self.batch_running and not self.scanning:
                        self.status.configure(text=self.t("Vorschau bereit."))
                elif kind == "preview_error" and event[1] == self.preview_id:
                    clear_preview(self.preview_label, self.t(event[2]))
                    self.preview_image = None
                    self.preview_photo = None
                    self.preview_label.configure(wraplength=600)
                    if not self.batch_running:
                        self.status.configure(text=self.t(event[2]))
                elif kind == "batch_progress":
                    _, index, total, filename, status = event
                    self.progress.set((index-1)/total)
                    self.status.configure(text=self.t(f"Ausgabe {index}/{total} · {filename} · {status}"))
                elif kind == "batch_file_done":
                    self.progress.set(event[1]/event[2])
                elif kind == "batch_done":
                    self.batch_running = False
                    result = event[1]
                    text = f"{'Abgebrochen' if result.cancelled else 'Fertig'}. {result.processed} Ausgaben gespeichert, {len(result.errors)} Fehler."
                    if result.warnings:
                        text += f" {len(result.warnings)} Metadatenwarnungen."
                    self.status.configure(text=self.t(text))
                    self._state()
                    if result.errors or result.warnings:
                        details = list(dict.fromkeys(result.errors+result.warnings))
                        messagebox.showwarning(self.t("Verarbeitung"), self.t(text+"\n\n"+"\n".join(details[:8])+
                            ("\n…" if len(details) > 8 else "")), parent=self)
                    if result.processed and not result.cancelled and not result.errors:
                        self._play_sound()
                elif kind == "batch_error":
                    self.batch_running = False
                    self.status.configure(text=self.t(event[1]))
                    self._state()
                    messagebox.showerror(self.t("Verarbeitung"), self.t(event[1]), parent=self)
        except Empty:
            pass
        finally:
            if not self.closed:
                self.after(50, self._pump)

    def _play_sound(self):
        path = resource_dir()/"assets"/"ready.wav"
        if not path.is_file():
            return
        def play():
            try:
                import sys
                if sys.platform == "win32":
                    import winsound
                    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                else:
                    import shutil
                    tool = shutil.which("afplay" if sys.platform == "darwin" else "aplay")
                    if tool:
                        subprocess.run([tool, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            except (OSError, RuntimeError, subprocess.TimeoutExpired):
                pass
        Thread(target=play, daemon=True).start()

    def close(self):
        self.closed = True
        self.batch_cancel.set()
        self.scan_cancel.set()
        self.preview_worker.close()
        if self.preview_after is not None:
            self.after_cancel(self.preview_after)
        if self.resize_after is not None:
            self.after_cancel(self.resize_after)
        self.status.configure(text=self.t("AnaChroma wird geschlossen..."))
        self._finish_close()

    def _finish_close(self):
        if self.preview_worker.thread.is_alive() or (self.batch_thread and self.batch_thread.is_alive()):
            self.after(50, self._finish_close)
        else:
            for identifier in self.tk.call("after", "info"):
                self.after_cancel(identifier)
            self.destroy()


def main():
    app = AnaChromaApp()
    # Development package check: load the bundled SBS through the actual
    # preview worker and Tk/Pillow image bridge, then close normally.
    import sys
    smoke_failed = []
    if "--smoke-test" in sys.argv:
        from .smoke_gui import PackagedSmokeCheck
        smoke = PackagedSmokeCheck(app, smoke_failed)
        from time import monotonic
        deadline = monotonic() + 45
        def smoke_check():
            if monotonic() >= deadline:
                smoke_failed.append("Packaged GUI did not complete the preview/CIELab/metadata checks")
                app.close()
            elif smoke.poll():
                app.close()
            else:
                app.after(50, smoke_check)
        app.after(100, smoke_check)
    app.mainloop()
    if "--smoke-test" in sys.argv:
        smoke.close()
    if smoke_failed:
        raise RuntimeError(smoke_failed[0])


if __name__ == "__main__":
    main()
