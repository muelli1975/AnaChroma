"""Local German/English UI strings. No service or translation requests."""
from __future__ import annotations
import re
from string import Formatter

EN = {
    "Hochwertige Anaglyphen aus SBS-Bildern": "High-quality anaglyphs from SBS images",
    "Eingabe": "Input", "Ausgabe": "Output", "Anaglyph": "Anaglyph", "Verarbeitung": "Processing",
    "Einzelbild…": "Single image…", "Bildordner…": "Image folder…", "Einzelbild": "Single image",
    "Keine Bilder gewählt": "No images selected", "Kein Bild geladen": "No image loaded",
    "Unterordner mitverarbeiten": "Include subfolders",
    "Unterordner im Programmordner verwenden": "Use subfolder in program folder",
    "Eigener Ausgabeordner": "Custom output folder",
    "Ausgabeziel": "Output destination",
    "Kein eigener Ausgabeordner gewählt": "No custom output folder selected",
    "Auswählen": "Choose",
    "Unterordner im Input-Ordner\nverwenden": "Use subfolder in\ninput folder",
    "output im Eingabeordner": "output in input folder",
    "Eigenen Ausgabeordner wählen…": "Choose custom output folder…",
    "Ausgabeordner wählen": "Choose output folder",
    "JPEG-Qualität 95 für Druck/Archiv": "JPEG quality 95 for print/archive",
    "Eigenes Verfahren anlegen…": "Create custom method…", "Verfahren": "Method", "Größe": "Size",
    "Bearbeiten…": "Edit…", "Original": "Original", "2048 lange Seite": "2048 long edge",
    "Benutzerdefiniert": "Custom", "lange Seite": "long edge", "kurze Seite": "short edge",
    "Bild speichern": "Save image", "Aktuelles Bild speichern": "Save current image",
    "Alle verarbeiten": "Process all", "Abbrechen": "Cancel", "Vorheriges Bild": "Previous image",
    "Nächstes Bild": "Next image", "Datei oder Ordner laden": "Load a file or folder",
    "Bereit.": "Ready.", "Suche SBS-Bilder...": "Finding SBS images...",
    "CIELab-Vorschau wird erzeugt...": "Creating CIELab preview...",
    "Berechne Vorschau...": "Calculating preview...", "Vorschau bereit.": "Preview ready.",
    "Abbruch wird ausgeführt...": "Cancelling...", "AnaChroma wird geschlossen...": "Closing AnaChroma...",
    "CIELab nicht gefunden.\nBitte ein anderes Verfahren wählen.": "CIELab not found.\nPlease select another method.",
    "CIELab nicht gefunden. Andere Verfahren sind verfügbar.": "CIELab not found. Other methods are available.",
    "Alle Bilder verarbeiten...": "Processing all images...", "Speichere aktuelles Bild...": "Saving current image...",
    "Lade SBS...": "Loading SBS...", "Berechne Anaglyphe...": "Calculating anaglyph...",
    "Speichere JPEG...": "Saving JPEG...", "Übernehme Metadaten...": "Copying metadata...",
    "Abgebrochen.": "Cancelled.", "Fertig.": "Done.", "Eigene Verfahren": "Custom methods",
    "Eigenes Verfahren": "Custom method", "Name": "Name", "Dateinamenssuffix": "Filename suffix",
    "Vorlage": "Template", "Vorlage wählen…": "Choose template…", "Matrix links": "Left matrix",
    "Matrix rechts": "Right matrix", "Rot": "Red", "Grün": "Green", "Blau": "Blue",
    "Eingang Rot": "Input red", "Eingang Grün": "Input green", "Eingang Blau": "Input blue",
    "Ausgabe\nRot": "Output\nred", "Ausgabe\nGrün": "Output\ngreen", "Ausgabe\nBlau": "Output\nblue",
    "In linearem Licht berechnen": "Calculate in linear light", "Bildanpassung": "Image adjustment",
    "Helligkeit": "Brightness", "Kontrast": "Contrast", "Farbkorrektur": "Colour correction",
    "Zurücksetzen": "Reset", "Löschen": "Delete", "Verfahren speichern": "Save method",
    "SBS-Bild laden": "Load an SBS image", "Eigene Variante": "Custom variant",
    "Bitte einen Ausgabeordner auswählen.": "Please choose an output folder.",
    "CIELab ist nicht installiert. Externes Programm unter tools/cielab bereitstellen.":
        "CIELab is not installed. Place its executable in tools/cielab.",
    "Dieses Spezialverfahren benötigt zusätzliche Rechenschritte.\nDer Editor beginnt stattdessen mit der einfachen Color-Matrix.":
        "This method requires additional processing steps.\nThe editor will start with the simple Color matrix.",
    "Die vorhandene Preset-Datei ist ungültig und wird nicht überschrieben.": "The existing preset file is invalid and will not be overwritten.",
    "Die vorhandene Preset-Datei wird nicht überschrieben.": "The existing preset file will not be overwritten.",
    "Die Datei bleibt unverändert; Speichern ist bis zur Klärung gesperrt.": "The file is unchanged; saving is disabled until the problem is resolved.",
    "Bitte einen endlichen, berechenbaren Zahlenwert eingeben.": "Please enter a finite, computable number.",
    "Kanalpotenzen müssen größer als 0 sein.": "Channel powers must be greater than 0.",
    "Bitte einen Namen mit höchstens 120 Zeichen eingeben.": "Please enter a name of up to 120 characters.",
    "Suffix: Kleinbuchstaben, Ziffern und Unterstriche; mit Buchstabe beginnen.":
        "Suffix: lowercase letters, digits and underscores; start with a letter.",
    "Matrixwerte müssen endlich und in Float32 berechenbar sein.": "Matrix values must be finite and computable in Float32.",
    "Kanalpotenzen müssen positiv und endlich sein.": "Channel powers must be positive and finite.",
    "Helligkeits-/Kontrastfaktoren müssen endlich und mindestens 0 sein.": "Brightness/contrast factors must be finite and at least 0.",
    "Bildbreite ist nicht gerade – SBS kann nicht sauber geteilt werden.": "Image width is odd – SBS cannot be split evenly.",
    "Keine unterstützten Bilder gefunden.": "No supported images found.",
    "Der Eingabeordner existiert nicht.": "The input folder does not exist.",
    "SBS-Bild wählen": "Choose SBS image", "SBS-Bildordner wählen": "Choose SBS image folder",
    "SBS-Bilder": "SBS images", "Alle Dateien": "All files",
    "Ungültige Kennung oder Rechenfolge eines eigenen Verfahrens.": "Invalid identifier or processing order for a custom method.",
    "Name, Kennung oder Dateinamenssuffix ist bereits vergeben.": "Name, identifier or filename suffix is already in use.",
    "Unbekannte Preset-Version; Datei wurde nicht verändert.": "Unknown preset version; the file was not changed.",
    "Dieses Eingabeformat wird nicht unterstützt.": "This input format is not supported.",
    "Das SBS-Bild ist zu schmal.": "The SBS image is too narrow.",
    "ExifTool nicht gefunden; JPEG wurde ohne Originalmetadaten gespeichert.": "ExifTool not found; JPEG saved without original metadata.",
    "Eine positive Pixelzahl und lange/kurze Seite wählen.": "Choose a positive pixel count and long/short edge.",
    "Eine Ausgabedatei würde ein ausgewähltes Original überschreiben.": "An output file would overwrite a selected original.",
}

FORMATS = (
    ("Bildordner · {count} Bilder", "Image folder · {count} images"),
    ("AnaChroma · Beispielbild", "AnaChroma · Sample image"),
    ("Eigene: {name}", "Custom: {name}"), ("Entwurf · {name}", "Draft · {name}"),
    ("{name} – eigene Variante", "{name} – custom variant"),
    ("Datei {index}/{total} · {name} · {status}", "File {index}/{total} · {name} · {status}"),
    ("{state} {count} Bilder verarbeitet, {errors} Fehler.", "{state} {count} images processed, {errors} errors."),
    ("{text} {count} Metadatenwarnungen.", "{text} {count} metadata warnings."),
    ("Bereit. Externe Tools nicht gefunden: {tools}.", "Ready. External tools not found: {tools}."),
    ("Einstellungen konnten nicht gespeichert werden: {detail}", "Could not save settings: {detail}"),
    ("{detail} Vorschau zeigt den letzten gültigen Entwurf.", "{detail} Preview shows the last valid draft."),
    ("Der Faktor muss mindestens {value} sein.", "The factor must be at least {value}."),
    ("„{name}“ löschen?", "Delete “{name}”?"),
    ("Metadaten konnten nicht übernommen werden: {detail}", "Could not copy metadata: {detail}"),
    ("Metadaten konnten nicht vollständig übernommen werden: {detail}", "Could not copy all metadata: {detail}"),
    ("Mehrere Eingaben würden dieselbe Ausgabedatei erzeugen: {name}", "Multiple inputs would create the same output file: {name}"),
    ("Eigene Verfahren konnten nicht geladen werden: {detail}", "Could not load custom methods: {detail}"),
    ("CIELab konnte das Bild nicht berechnen: {detail}", "CIELab could not calculate the image: {detail}"),
    ("{filename}: {detail}", "{filename}: {detail}"),
)


def _pattern(template):
    parts = []
    for literal, field, _, _ in Formatter().parse(template):
        parts.append(re.escape(literal))
        if field:
            parts.append(f"(?P<{field}>.+?)")
    return re.compile("".join(parts), re.DOTALL)


PATTERNS = tuple((_pattern(source), target) for source, target in FORMATS)


def translate(text, language):
    if language != "en" or not isinstance(text, str):
        return text
    if text in EN:
        return EN[text]
    if "\n" in text:
        return "\n".join(translate(line, language) for line in text.split("\n"))
    for pattern, target in PATTERNS:
        match = pattern.fullmatch(text)
        if match:
            return target.format(**{k: translate(v, language) if k in {"status", "state", "detail", "text"} else v
                                    for k, v in match.groupdict().items()})
    return text


def translate_widgets(root, language, skip=()):
    """Remember static widget labels so language changes are reversible."""
    import customtkinter as ctk
    for widget in root.winfo_children():
        if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton, ctk.CTkCheckBox, ctk.CTkRadioButton)) and widget not in skip:
            if not hasattr(widget, "_anachroma_label"):
                widget._anachroma_label = widget.cget("text")
            widget.configure(text=translate(widget._anachroma_label, language))
        translate_widgets(widget, language, skip)
