"""Visible, anaglyph-focused editor: exact coefficients plus live controls."""
from __future__ import annotations
from dataclasses import replace
import math
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image

from .matrices import BUILTINS, MAX_SAFE_VALUE, Method
from .theme import BORDER, DANGER, GOLD, GOLD_HOVER, MUTED, PANEL_BG, TEXT


class NumberControl(ctk.CTkFrame):
    """The number is authoritative; moving a thumb never rounds other values."""
    def __init__(self, master, value, changed, *, slider=True, lower=-2., upper=2.,
                 step=.001, minimum=None, positive=False):
        super().__init__(master, fg_color="transparent")
        self.changed = changed
        self.lower, self.upper, self.step = lower, upper, step
        self.minimum, self.positive = minimum, positive
        self.updating = False
        self.wheel_remainder = 0.
        self.var = tk.StringVar(value=repr(value))
        self.entry = ctk.CTkEntry(self, width=126, textvariable=self.var, border_color=BORDER)
        self.entry.pack(fill="x", padx=2, pady=2)
        self.slider = None
        if slider:
            self.slider = ctk.CTkSlider(self, width=120, height=16, from_=lower, to=upper,
                button_color=GOLD, button_hover_color=GOLD_HOVER, progress_color=GOLD,
                command=self._slide)
            self.slider.pack(fill="x", padx=6, pady=(2, 2))
            self.bounds = ctk.CTkLabel(self, text="", height=12, font=("Arial", 10), text_color=MUTED)
            self.bounds.pack(fill="x")
            self.slider.bind("<Button-1>", self._focus_slider, add="+")
            self.slider.bind("<MouseWheel>", self._wheel)
            self.slider.bind("<Button-4>", self._wheel)
            self.slider.bind("<Button-5>", self._wheel)
        self.entry.bind("<MouseWheel>", self._wheel)
        self.entry.bind("<Button-4>", self._wheel)
        self.entry.bind("<Button-5>", self._wheel)
        self.entry.bind("<Return>", lambda _: "break")
        self.var.trace_add("write", self._edited)
        self.set(value)

    def get(self):
        value = float(self.var.get().strip().replace(",", ".").replace("−", "-"))
        if not math.isfinite(value) or abs(value) > MAX_SAFE_VALUE:
            raise ValueError("Bitte einen endlichen, berechenbaren Zahlenwert eingeben.")
        if self.positive and value <= 0:
            raise ValueError("Kanalpotenzen müssen größer als 0 sein.")
        if self.minimum is not None and value < self.minimum:
            raise ValueError(f"Der Faktor muss mindestens {self.minimum:g} sein.")
        return value

    def set(self, value):
        self.updating = True
        self.var.set(repr(float(value)))
        self._position(value)
        self.entry.configure(border_color=BORDER)
        self.updating = False

    def _position(self, value):
        if self.slider is not None:
            low, high = min(self.lower, value), max(self.upper, value)
            self.slider.configure(from_=low, to=high)
            self.slider.set(value)
            self.bounds.configure(text=f"{low:g} … {high:g}")

    def _edited(self, *_):
        if self.updating:
            return
        try:
            self._position(self.get())
            self.entry.configure(border_color=BORDER)
        except ValueError:
            self.entry.configure(border_color=DANGER)
        self.changed()

    def _slide(self, value):
        quantized = round(value/self.step)*self.step
        self.set(value if self.positive and quantized <= 0 else quantized)
        self.changed()

    def _focus_slider(self, _):
        self.slider.focus_set()

    def _wheel(self, event):
        focused = self.focus_get()
        if focused is None or not (focused == self or str(focused).startswith(str(self)+".")):
            # Consume only within the focused control; otherwise normal dialog scroll.
            return None
        if getattr(event, "num", None) in (4, 5):
            steps = 1 if event.num == 4 else -1
        else:
            import sys
            delta = event.delta if sys.platform == "darwin" else event.delta/120.
            self.wheel_remainder += delta
            steps = math.trunc(self.wheel_remainder)
            self.wheel_remainder -= steps
        if steps:
            try:
                value = self.get() + steps*self.step
                if self.positive and value <= 0:
                    return "break"
                if self.minimum is not None:
                    value = max(self.minimum, value)
                self.set(float(f"{value:.12g}"))
                self.changed()
            except ValueError:
                pass
        return "break"

    def enable(self, enabled):
        self.entry.configure(state="normal" if enabled else "disabled")
        if self.slider is not None:
            self.slider.configure(state="normal" if enabled else "disabled")


class PresetEditor(ctk.CTkToplevel):
    def __init__(self, app, method: Method, existing=False):
        super().__init__(app)
        self.app = app
        self.title("AnaChroma – eigenes Verfahren")
        self.geometry("1000x790")
        self.minsize(930, 620)
        self.configure(fg_color=PANEL_BG)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.existing = existing
        self.base = method.as_custom(existing=existing)
        self.original = self.base
        self.initializing = True
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        content = ctk.CTkScrollableFrame(self, fg_color=PANEL_BG)
        content.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        content.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(content, text="Eigene Anaglyphenverfahren", font=("Arial", 20, "bold"),
                     text_color=TEXT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        ctk.CTkLabel(content, text="Matrizen bestimmen die Farbmischung beider Ansichten. Werte direkt aus einer Quelle übernehmen oder mit Vorschau einstellen.",
                     wraplength=920, justify="left", text_color=MUTED).grid(row=1, column=0, columnspan=2, sticky="w")
        identity = ctk.CTkFrame(content, fg_color="transparent")
        identity.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)
        identity.grid_columnconfigure(1, weight=1)
        self.name = tk.StringVar(value=self.base.name)
        self.suffix = tk.StringVar(value=self.base.suffix)
        ctk.CTkLabel(identity, text="Name").grid(row=0, column=0, padx=8, sticky="w")
        ctk.CTkEntry(identity, textvariable=self.name).grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        ctk.CTkLabel(identity, text="Dateinamenssuffix").grid(row=1, column=0, padx=8, sticky="w")
        ctk.CTkEntry(identity, textvariable=self.suffix).grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        self.templates = {m.name: m for m in BUILTINS if m.editable}
        ctk.CTkLabel(identity, text="Vorlage übernehmen").grid(row=2, column=0, padx=8, sticky="w")
        self.template = ctk.CTkOptionMenu(identity, values=list(self.templates), command=self._template,
                                        fg_color=BORDER, button_color=GOLD)
        self.template.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        self.template.set(method.name if method.builtin else "Vorlage wählen…")
        preview = ctk.CTkFrame(identity, fg_color="#000000", width=240, height=160)
        preview.grid(row=0, column=2, rowspan=3, padx=(12, 0), sticky="nsew")
        preview.grid_propagate(False)
        preview.grid_rowconfigure(1, weight=1)
        preview.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(preview, text="Live-Vorschau", text_color=MUTED, height=20).grid(row=0, column=0)
        self.live_preview = ctk.CTkLabel(preview, text="SBS-Bild laden", text_color=MUTED, wraplength=220)
        self.live_preview.grid(row=1, column=0, sticky="nsew")
        self.preview_image = None
        if app.preview_image is not None:
            self.show_preview(app.preview_image)
        self.controls = []
        for side, values in enumerate((self.base.left, self.base.right)):
            grid = ctk.CTkFrame(content, fg_color="transparent")
            grid.grid(row=3, column=side, sticky="nsew", padx=6)
            ctk.CTkLabel(grid, text="Matrix links" if side == 0 else "Matrix rechts", font=("Arial", 16, "bold"))\
                .grid(row=0, column=0, columnspan=4, sticky="w", pady=(4, 8))
            for col, channel in enumerate(("Rot", "Grün", "Blau"), 1):
                ctk.CTkLabel(grid, text=f"Eingang {channel}", text_color=MUTED).grid(row=1, column=col)
                grid.grid_columnconfigure(col, weight=1)
            controls = []
            for row, channel in enumerate(("Rot", "Grün", "Blau")):
                ctk.CTkLabel(grid, text=f"Ausgabe\n{channel}", text_color=MUTED).grid(row=row+2, column=0, padx=(0, 6))
                cells = []
                for col in range(3):
                    cell = NumberControl(grid, values[row][col], self._changed)
                    cell.grid(row=row+2, column=col+1, sticky="ew", padx=2, pady=4)
                    cells.append(cell)
                controls.append(cells)
            self.controls.append(controls)
        ctk.CTkLabel(content, text="Direkte Koeffizienten: 0 = kein Beitrag, 1 = voller Beitrag. Negative Werte und Werte über 1 sind zulässig.\n"
                     "Regler −2 bis +2; Zahlenfelder erhalten genauere Werte. Mausrad beim ausgewählten Feld/Regler: 0,001.",
                     justify="left", text_color=MUTED).grid(row=4, column=0, columnspan=2, sticky="w", pady=8)
        options = ctk.CTkFrame(content, fg_color="transparent")
        options.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.linear = tk.BooleanVar(value=self.base.mode == "linear")
        ctk.CTkCheckBox(options, text="In linearem Licht berechnen", variable=self.linear,
                        command=self._changed, fg_color=GOLD).grid(row=0, column=0, columnspan=4, sticky="w", pady=6)
        ctk.CTkLabel(options, text="Für Matrizen wählen, die lineares RGB voraussetzen; anschließend wird wieder nach sRGB gewandelt.",
                     text_color=MUTED).grid(row=1, column=0, columnspan=4, sticky="w")
        ctk.CTkLabel(options, text="Bildanpassung", font=("Arial", 15, "bold")).grid(row=2, column=0, sticky="w", pady=(12, 2))
        ctk.CTkLabel(options, text="Helligkeit (Faktor)").grid(row=3, column=0, sticky="w", padx=(0, 8))
        self.brightness = NumberControl(options, self.base.brightness, self._changed, slider=False, minimum=0.)
        self.brightness.grid(row=3, column=1, sticky="w")
        ctk.CTkLabel(options, text="Kontrast (Faktor)").grid(row=3, column=2, sticky="w", padx=(20, 8))
        self.contrast = NumberControl(options, self.base.contrast, self._changed, slider=False, minimum=0.)
        self.contrast.grid(row=3, column=3, sticky="w")
        ctk.CTkLabel(options, text="1 = unverändert. Gleiche Anpassung beider Ansichten; keine automatische Ghosting-Kalibrierung.",
                     text_color=MUTED).grid(row=4, column=0, columnspan=4, sticky="w")
        self.correct = tk.BooleanVar(value=self.base.correct_rgb)
        ctk.CTkCheckBox(options, text="Farbkanäle korrigieren (Kanalpotenzen)", variable=self.correct,
                        command=self._changed, fg_color=GOLD).grid(row=5, column=0, columnspan=4, sticky="w", pady=(12, 6))
        channels = ctk.CTkFrame(options, fg_color="transparent")
        channels.grid(row=6, column=0, columnspan=4, sticky="w")
        self.powers = []
        for i, channel in enumerate(("Rot", "Grün", "Blau")):
            ctk.CTkLabel(channels, text=channel).grid(row=0, column=i, sticky="w", padx=6)
            control = NumberControl(channels, self.base.powers[i], self._changed,
                                    lower=.625, upper=1.25, positive=True)
            control.grid(row=1, column=i, padx=6)
            self.powers.append(control)
        ctk.CTkLabel(options, text="1 = unverändert; kleiner als 1 hellt auf, größer als 1 dunkelt ab.\n"
                     "Bewährte Rotkorrektur: Rot 0,75; Grün/Blau 1. Reglerbereich aus den Batch-Potenzen, per Zahleneingabe erweiterbar.",
                     justify="left", text_color=MUTED).grid(row=7, column=0, columnspan=4, sticky="w", pady=6)
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.error = ctk.CTkLabel(footer, text="", text_color=DANGER, wraplength=880, justify="left")
        self.error.pack(fill="x")
        buttons = ctk.CTkFrame(footer, fg_color="transparent")
        buttons.pack(fill="x")
        ctk.CTkButton(buttons, text="Auf Vorlage zurücksetzen", command=self.reset, fg_color=BORDER).pack(side="left", padx=4)
        if existing:
            ctk.CTkButton(buttons, text="Löschen", command=self.delete, width=90, fg_color=DANGER).pack(side="left", padx=4)
        ctk.CTkButton(buttons, text="Abbrechen", command=self.cancel, fg_color=BORDER, width=110).pack(side="right", padx=4)
        self.save_button = ctk.CTkButton(buttons, text="Verfahren speichern", command=self.save, fg_color=GOLD, hover_color=GOLD_HOVER)
        self.save_button.pack(side="right", padx=4)
        self.name.trace_add("write", lambda *_: self._changed())
        self.suffix.trace_add("write", lambda *_: self._changed())
        self.initializing = False
        self._changed()
        self.lift_after = self.after(100, self.lift)

    def destroy(self):
        if hasattr(self, "lift_after"):
            self.after_cancel(self.lift_after)
        super().destroy()

    def show_preview(self, image: Image.Image | None, error="SBS-Bild laden"):
        if image is None:
            self.preview_image = None
            self.live_preview.configure(image=None, text=error)
            return
        factor = min(1., 228 / image.width, 132 / image.height)
        size = (max(1, round(image.width * factor)), max(1, round(image.height * factor)))
        self.preview_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        self.live_preview.configure(image=self.preview_image, text="")

    def draft(self):
        matrices = [tuple(tuple(c.get() for c in row) for row in grid) for grid in self.controls]
        return replace(self.base, name=self.name.get().strip(), suffix=self.suffix.get().strip(),
                       left=matrices[0], right=matrices[1], mode="linear" if self.linear.get() else "srgb",
                       powers=tuple(c.get() for c in self.powers), correct_rgb=self.correct.get(),
                       brightness=self.brightness.get(), contrast=self.contrast.get()).validate()

    def _changed(self):
        if self.initializing:
            return
        for control in self.powers:
            control.enable(self.correct.get())
        try:
            draft = self.draft()
            self.error.configure(text="")
            self.save_button.configure(state="normal")
            self.app.editor_preview(draft)
        except (ValueError, OverflowError) as exc:
            self.error.configure(text=f"{exc} Vorschau zeigt den letzten gültigen Entwurf.")
            self.save_button.configure(state="disabled")

    def _template(self, name):
        template = self.templates[name].as_custom()
        self.original = replace(template, id=self.base.id, name=self.name.get(), suffix=self.suffix.get())
        self.reset()

    def reset(self):
        self.initializing = True
        for grid, values in zip(self.controls, (self.original.left, self.original.right)):
            for row, numbers in zip(grid, values):
                for control, value in zip(row, numbers):
                    control.set(value)
        self.linear.set(self.original.mode == "linear")
        self.correct.set(self.original.correct_rgb)
        self.brightness.set(self.original.brightness)
        self.contrast.set(self.original.contrast)
        for control, value in zip(self.powers, self.original.powers):
            control.set(value)
        self.initializing = False
        self._changed()

    def save(self):
        try:
            self.app.save_custom(self.draft())
        except (ValueError, OSError) as exc:
            messagebox.showerror("Verfahren speichern", str(exc), parent=self)
            return
        self.app.finish_editor()
        self.destroy()

    def cancel(self):
        self.app.finish_editor()
        self.destroy()

    def delete(self):
        if messagebox.askyesno("Eigenes Verfahren löschen", f"„{self.base.name}“ löschen?", parent=self):
            try:
                self.app.delete_custom(self.base.id)
            except (ValueError, OSError) as exc:
                messagebox.showerror("Löschen", str(exc), parent=self)
                return
            self.cancel()
