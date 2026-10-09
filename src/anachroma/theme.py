"""Shared Stereo-Tool colors; no new font or network dependency."""
APP_BG = "#111111"
SECONDARY_BG = "#181818"
PANEL_BG = "#202020"
BORDER = "#333333"
HOVER_BG = "#282828"
TEXT = "#f2f2f2"
MUTED = "#b8b8b8"
DISABLED = "#727272"
GOLD = "#9c7c38"
GOLD_HOVER = "#c6a95e"
DANGER = "#7f3939"
DANGER_HOVER = "#944545"
PREVIEW_BG = "#000000"
import sys
FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else "Helvetica"


def configure_theme():
    """Apply the same widget palette as StereoFine and SplatTricia."""
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    theme = ctk.ThemeManager.theme
    for font in theme["CTkFont"].values():
        if isinstance(font, dict):
            font["family"] = FONT_FAMILY
    styles = {
        "CTk": dict(fg_color=APP_BG),
        "CTkToplevel": dict(fg_color=APP_BG),
        "CTkFrame": dict(fg_color=SECONDARY_BG, top_fg_color=PANEL_BG, border_color=BORDER),
        "CTkScrollableFrame": dict(label_fg_color=SECONDARY_BG),
        "CTkLabel": dict(text_color=TEXT),
        "CTkEntry": dict(fg_color=SECONDARY_BG, border_color=BORDER, text_color=TEXT,
                         placeholder_text_color=MUTED, corner_radius=8),
        "CTkButton": dict(fg_color=SECONDARY_BG, hover_color=HOVER_BG, border_color=BORDER,
                          border_width=1, text_color=TEXT, text_color_disabled=DISABLED, corner_radius=8),
        "CTkCheckBox": dict(fg_color=GOLD, hover_color=GOLD_HOVER, border_color=BORDER,
                            text_color=TEXT, text_color_disabled=DISABLED, checkmark_color=TEXT, corner_radius=4),
        "CTkRadioButton": dict(fg_color=GOLD, hover_color=GOLD_HOVER, border_color=BORDER,
                               text_color=TEXT, text_color_disabled=DISABLED),
        "CTkOptionMenu": dict(fg_color=PANEL_BG, button_color=HOVER_BG, button_hover_color=BORDER,
                              dropdown_fg_color=SECONDARY_BG, dropdown_hover_color=HOVER_BG,
                              text_color=TEXT, text_color_disabled=DISABLED, dropdown_text_color=TEXT, corner_radius=8),
        "CTkSlider": dict(fg_color=BORDER, progress_color=GOLD, button_color=GOLD_HOVER,
                          button_hover_color=GOLD_HOVER),
        "CTkProgressBar": dict(fg_color=BORDER, progress_color=GOLD, border_color=BORDER),
        "CTkScrollbar": dict(button_color=BORDER, button_hover_color=HOVER_BG),
        "DropdownMenu": dict(fg_color=SECONDARY_BG, hover_color=HOVER_BG, text_color=TEXT),
    }
    for name, style in styles.items():
        theme[name].update(style)


def preview_border_px(displayed_image_width):
    return max(16, round(max(0, displayed_image_width) * .030) + 2)


def preview_size(image_size, viewport):
    """Fit in physical display pixels, reserving the complete black surround."""
    iw, ih = image_size
    w, h = (max(1, int(n)) for n in viewport)
    # A monotone search avoids rounding oscillations around the 3% boundary.
    low, high = 0., min(w/iw, h/ih)
    for _ in range(40):
        factor = (low + high)/2
        size = (max(1, round(iw*factor)), max(1, round(ih*factor)))
        border = preview_border_px(size[0])
        if size[0] + 2*border <= w and size[1] + 2*border <= h:
            low = factor
        else:
            high = factor
    size = (max(1, round(iw*low)), max(1, round(ih*low)))
    border = preview_border_px(size[0])
    return size, border


def clear_preview(label, text):
    label.configure(image="", text=text)
