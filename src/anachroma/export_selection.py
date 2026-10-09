"""Small local checklist; preview selection and export selection are independent."""
import tkinter as tk
import customtkinter as ctk
from .theme import SECONDARY_BG, MUTED


class ExportSelection(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title(app.t("Ausgabeverfahren"))
        self.geometry("520x600")
        self.minsize(440, 420)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.current = tk.BooleanVar(value=app.export_ids is None)
        ctk.CTkCheckBox(self, text=app.t("Aktuelles Verfahren verwenden"), variable=self.current,
                       command=self._state).grid(row=0, column=0, sticky="w", padx=18, pady=16)
        listing = ctk.CTkScrollableFrame(self, fg_color=SECONDARY_BG)
        listing.grid(row=1, column=0, sticky="nsew", padx=18)
        listing.grid_columnconfigure(0, weight=1)
        selected = app.export_ids or (app.selected_method().id,)
        self.choices = []
        for label, method in app.methods.items():
            variable = tk.BooleanVar(value=method.id in selected)
            box = ctk.CTkCheckBox(listing, text=label, variable=variable, command=self._state)
            box.grid(row=len(self.choices), column=0, sticky="w", padx=8, pady=5)
            self.choices.append((method.id, variable, box))
        self.note = ctk.CTkLabel(self, text="", text_color=MUTED)
        self.note.grid(row=2, column=0, sticky="ew", padx=18, pady=8)
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 16))
        app._button(buttons, app.t("Abbrechen"), self.cancel, width=140).pack(side="right", padx=4)
        self.apply_button = app._button(buttons, app.t("Übernehmen"), self.apply, primary=True, width=160)
        self.apply_button.pack(side="right", padx=4)
        self._state()
        self.grab_set()

    def _state(self):
        for _, _, box in self.choices:
            box.configure(state="disabled" if self.current.get() else "normal")
        count = sum(variable.get() for _, variable, _ in self.choices)
        self.note.configure(text=self.app.t("Aktuelles Verfahren" if self.current.get() else f"{count} Verfahren gewählt"))
        self.apply_button.configure(state="normal" if self.current.get() or count else "disabled")

    def apply(self):
        selected = tuple(identifier for identifier, variable, _ in self.choices if variable.get())
        if not self.current.get() and not selected:
            return
        self.app.export_ids = None if self.current.get() else selected
        self.app._refresh_export_selection()
        self.cancel()

    def cancel(self):
        self.app.export_dialog = None
        self.destroy()
