"""Visible, anaglyph-focused editor: exact coefficients plus live controls."""
from __future__ import annotations
from dataclasses import replace
import math
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from .matrices import BUILTINS, MAX_SAFE_VALUE, Method
from .i18n import translate_widgets
from .theme import BORDER, DANGER, DANGER_HOVER, GOLD, GOLD_HOVER, MUTED, PANEL_BG, TEXT, FONT_FAMILY, DISABLED


class NumberControl(ctk.CTkFrame):
    """The number is authoritative; moving a thumb never rounds other values."""
    def __init__(self, master, value, changed, *, slider=True, lower=-2., upper=2.,
                 step=.001, minimum=None, positive=False, horizontal=False, width=112):
        super().__init__(master, fg_color="transparent")
        self.changed = changed
        self.lower, self.upper, self.step = lower, upper, step
        self.minimum, self.positive = minimum, positive
        self.updating = False
        self.wheel_remainder = 0.
        self.var = tk.StringVar(value=repr(value))
        self.entry = ctk.CTkEntry(self, width=76 if horizontal else width, height=26, textvariable=self.var, border_color=BORDER)
        self.entry.pack(side="right" if horizontal else "top", fill="x", padx=2, pady=1)
        self.slider = None
        if slider:
            self.slider = ctk.CTkSlider(self, width=max(40, width-2), height=14, from_=lower, to=upper,
                button_color=GOLD_HOVER, button_hover_color=GOLD_HOVER, progress_color=GOLD,
                command=self._slide)
            self.slider.pack(side="left" if horizontal else "top", fill="x", expand=horizontal, padx=6, pady=3)
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
        if self.entry.cget("state") == "disabled":
            return None
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
            self.slider.configure(state="normal" if enabled else "disabled",
                                  progress_color=GOLD if enabled else BORDER,
                                  button_color=GOLD_HOVER if enabled else DISABLED)


class PresetEditor(ctk.CTkToplevel):
    def __init__(self, app, method: Method, existing=False):
        super().__init__(app)
        self.app = app
        self.title("AnaChroma – eigenes Verfahren")
        self.geometry("720x550")
        self.minsize(680, 530)
        self.configure(fg_color=PANEL_BG)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.existing = existing
        self.base = method.as_custom(existing=existing)
        if not existing:
            self.base = replace(self.base, name=self.app.t(self.base.name))
        self.original = self.base
        self.initializing = True
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=0, column=0, sticky="nsew", padx=16, pady=(12, 6))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        content = ctk.CTkFrame(body, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew")
        content.grid_columnconfigure((0, 1), weight=1, uniform="matrix")
        identity = ctk.CTkFrame(content, fg_color="transparent")
        identity.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        identity.grid_columnconfigure(1, weight=1)
        self.name = tk.StringVar(value=self.base.name)
        self.suffix = tk.StringVar(value=self.base.suffix)
        for row, label, variable in ((0, "Name", self.name), (1, "Dateinamenssuffix", self.suffix)):
            ctk.CTkLabel(identity, text=label).grid(row=row, column=0, padx=(0, 8), sticky="w")
            ctk.CTkEntry(identity, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=3)
        self.templates = {m.name: m for m in BUILTINS if m.editable}
        ctk.CTkLabel(identity, text="Vorlage").grid(row=2, column=0, sticky="w")
        self.template = ctk.CTkOptionMenu(identity, values=list(self.templates), command=self._template)
        self.template.grid(row=2, column=1, sticky="ew", pady=3)
        self.template.set(method.name if method.builtin else "Vorlage wählen…")
        self.controls = []
        for side, values in enumerate((self.base.left, self.base.right)):
            grid = ctk.CTkFrame(content, fg_color="transparent")
            grid.grid(row=1, column=side, sticky="nsew", padx=(0, 10) if side == 0 else (10, 0))
            ctk.CTkLabel(grid, text="Matrix links" if side == 0 else "Matrix rechts", font=(FONT_FAMILY, 16, "bold"))\
                .grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))
            for col, channel in enumerate(("Rot", "Grün", "Blau"), 1):
                ctk.CTkLabel(grid, text=f"Eingang {channel}", height=22, text_color=MUTED).grid(row=1, column=col)
                grid.grid_columnconfigure(col, weight=1)
            controls = []
            for row, channel in enumerate(("Rot", "Grün", "Blau")):
                ctk.CTkLabel(grid, text=f"Ausgabe\n{channel}", text_color=MUTED).grid(row=row+2, column=0, padx=(0, 4))
                cells = []
                for col in range(3):
                    cell = NumberControl(grid, values[row][col], self._changed, lower=-.5, upper=1.5, width=90)
                    cell.grid(row=row+2, column=col+1, sticky="ew", padx=2, pady=3)
                    cells.append(cell)
                controls.append(cells)
            self.controls.append(controls)
        self.linear = tk.BooleanVar(value=self.base.mode == "linear")
        ctk.CTkCheckBox(content, text="In linearem Licht berechnen", variable=self.linear,
                       command=self._changed).grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 10))
        correction = ctk.CTkFrame(content, fg_color="transparent")
        correction.grid(row=3, column=0, columnspan=2, sticky="ew")
        correction.grid_columnconfigure((0, 1, 2), weight=1)
        self.correct = tk.BooleanVar(value=self.base.correct_rgb)
        ctk.CTkCheckBox(correction, text="Farbkorrektur", variable=self.correct, command=self._changed)\
            .grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        self.powers = []
        for i, channel in enumerate(("Rot", "Grün", "Blau")):
            ctk.CTkLabel(correction, text=channel, height=22).grid(row=1, column=i, sticky="w", padx=4)
            control = NumberControl(correction, self.base.powers[i], self._changed,
                                    lower=.625, upper=1.25, positive=True, horizontal=True, width=180)
            control.grid(row=2, column=i, padx=2, sticky="ew")
            self.powers.append(control)
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.error = ctk.CTkLabel(footer, text="", height=18, text_color=DANGER, wraplength=660, justify="left")
        self.error.pack(fill="x")
        buttons = ctk.CTkFrame(footer, fg_color="transparent")
        buttons.pack(fill="x")
        ctk.CTkButton(buttons, text="Zurücksetzen", command=self.reset, width=110).pack(side="left", padx=4)
        if existing:
            ctk.CTkButton(buttons, text="Löschen", command=self.delete, width=90, border_color=DANGER, hover_color=DANGER_HOVER).pack(side="left", padx=4)
        ctk.CTkButton(buttons, text="Abbrechen", command=self.cancel, width=110).pack(side="right", padx=4)
        self.save_button = app._button(buttons, "Verfahren speichern", self.save, primary=True, width=210)
        self.save_button.pack(side="right", padx=4)
        self.name.trace_add("write", lambda *_: self._changed())
        self.suffix.trace_add("write", lambda *_: self._changed())
        self.initializing = False
        self.translate_ui()
        self._changed()
        self.lift_after = self.after(100, self.lift)

    def translate_ui(self):
        self.title("AnaChroma – " + self.app.t("Eigenes Verfahren"))
        translate_widgets(self, self.app.language, (self.error,))

    def destroy(self):
        if hasattr(self, "lift_after"):
            self.after_cancel(self.lift_after)
        super().destroy()

    def draft(self):
        matrices = [tuple(tuple(c.get() for c in row) for row in grid) for grid in self.controls]
        return replace(self.base, name=self.name.get().strip(), suffix=self.suffix.get().strip(),
                       left=matrices[0], right=matrices[1], mode="linear" if self.linear.get() else "srgb",
                       powers=tuple(c.get() for c in self.powers), correct_rgb=self.correct.get()).validate()

    def _changed(self):
        if self.initializing:
            return
        for control in self.powers:
            control.enable(self.correct.get())
        try:
            draft = self.draft()
            self.error.configure(text=self.app.t(""))
            self.save_button.configure(state="normal")
            self.app._style_primary_button(self.save_button)
            self.app.editor_preview(draft)
        except (ValueError, OverflowError) as exc:
            self.error.configure(text=self.app.t(f"{exc} Vorschau zeigt den letzten gültigen Entwurf."))
            self.save_button.configure(state="disabled")
            self.app._style_primary_button(self.save_button)

    def _template(self, name):
        template = self.templates[name].as_custom()
        existing = [m for m in self.app.custom if m.id != self.base.id]
        proposal_name, proposal_suffix = self.app.t(template.name), template.suffix
        number = 2
        while any(m.name.casefold() == proposal_name.casefold() or m.suffix == proposal_suffix for m in existing):
            proposal_name = f"{self.app.t(template.name)} ({number})"
            proposal_suffix = f"{template.suffix}_{number}"
            number += 1
        self.original = replace(template, id=self.base.id, name=proposal_name, suffix=proposal_suffix)
        self.initializing = True
        self.name.set(proposal_name)
        self.suffix.set(proposal_suffix)
        self.initializing = False
        self.reset()

    def reset(self):
        self.initializing = True
        for grid, values in zip(self.controls, (self.original.left, self.original.right)):
            for row, numbers in zip(grid, values):
                for control, value in zip(row, numbers):
                    control.set(value)
        self.linear.set(self.original.mode == "linear")
        self.correct.set(self.original.correct_rgb)
        for control, value in zip(self.powers, self.original.powers):
            control.set(value)
        self.initializing = False
        self._changed()

    def save(self):
        try:
            self.app.save_custom(self.draft())
        except (ValueError, OSError) as exc:
            messagebox.showerror(self.app.t("Verfahren speichern"), self.app.t(str(exc)), parent=self)
            return
        self.app.finish_editor()
        self.destroy()

    def cancel(self):
        self.app.finish_editor()
        self.destroy()

    def delete(self):
        if messagebox.askyesno(self.app.t("Eigenes Verfahren löschen"), self.app.t(f"„{self.base.name}“ löschen?"), parent=self):
            try:
                self.app.delete_custom(self.base.id)
            except (ValueError, OSError) as exc:
                messagebox.showerror(self.app.t("Löschen"), self.app.t(str(exc)), parent=self)
                return
            self.cancel()
