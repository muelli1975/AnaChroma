# AnaChroma 1.0

[English](README.md)

**Hochwertige Anaglyphen aus SBS-Bildern**

AnaChroma konvertiert Full-SBS-Stereobilder in hochwertige Anaglyphen, mit automatischer Vorschau, Bildnavigation und Einzelbild- oder Ordnerausgabe. Die Verarbeitung läuft vollständig lokal, ohne Account, Cloud oder Tracking.

## Schnellstart

1. Ein Einzelbild oder einen Bildordner öffnen. Bei einem Einzelbild stehen auch die benachbarten Bilder zur Navigation bereit.
2. Ein Anaglyphenverfahren wählen und die Vorschau prüfen.
3. Ausgabeordner und Größe wählen. Unter **Ausgabeverfahren** lassen sich mehrere Verfahren für die gleichzeitige Ausgabe auswählen.
4. **Bild speichern** oder **Alle verarbeiten** starten. Bei Ordnern können Unterordner einbezogen werden.

Unterstützt werden JPEG/JPG, PNG, TIFF/TIF, BMP und WebP. Full-SBS enthält zwei Halbbilder in voller Breite: links das linke Auge, rechts das rechte. EXIF-Orientation wird vor dem Teilen angewendet; das ausgerichtete Bild muss eine gerade Breite haben.

## Verfahren und Vorschau

18 Verfahren umfassen unter anderem Dubois LCD mit Rotkorrektur, Dubois, Compromise, Wimmer, Cosima, Rendepth, iaian7, Grey, Color, Grün/Magenta, Amber/Blau und CIELab Least Squares. Vorschau und Export verwenden dieselben Rechenregeln.

Die automatische Vorschau folgt der verfügbaren Fensterfläche bis maximal 1600 px lange Seite; CIELab verwendet maximal 1024 px. Beide nutzen dieselbe Anzeigefläche. Ein schwarzer Umraum macht vorhandene schwebende Scheinfenster sichtbar. Das originale SBS-Beispielbild mit 7680 × 2160 px ist enthalten.

**Eigenes Verfahren anlegen…** steht im Menü unter den Standardverfahren und öffnet einen kompakten Editor. Zwei 3×3-Matrizen lassen sich über präzise Zahlenfelder, Regler und das Mausrad einstellen. Dazu kommen optionale Berechnung in linearem Licht und RGB-Farbkorrektur. Änderungen erscheinen in der großen Hauptvorschau; gespeicherte Verfahren können erneut verwendet werden. Die [Editor-Anleitung](docs/PRESET_EDITOR.md) erklärt Koeffizienten und Korrekturwerte.

Tastatur: **Links/Rechts** oder **Bild auf/Bild ab** wechseln das Bild; **Strg+Links/Rechts** wechseln das Vorschauverfahren. Eingabefelder und ausgewählte Regler behalten ihre normale Bedienung.

## Ausgabe

JPEG-Qualität **90**, **4:4:4** ohne Chroma-Subsampling und optimierte Codierung. Optional **JPEG-Qualität 95 für Druck/Archiv**. Lanczos-Skalierung erhält das Seitenverhältnis.

Größen: Original; 1080p (innerhalb 1920 × 1080); 2160p (innerhalb 3840 × 2160); 2048 lange Seite; benutzerdefinierte lange oder kurze Seite.

**Unterordner im Programmordner verwenden** wählt `output` neben dem Programm. **Auswählen** bestimmt einen eigenen Ausgabeordner. **Ausgabeziel** zeigt den aktiven Pfad. Ordnerausgabe speichert direkt im Ausgabeziel und erhält die relative Unterordnerstruktur. Jedes gewählte Verfahren bekommt sein Dateinamenssuffix, etwa `bild_dubois_lcd.jpg`. Vorhandene Ergebnisse werden erst nach vollständigem Schreiben ersetzt; Namenskollisionen und das Überschreiben von Originalen werden vor dem Export abgewiesen.

ExifTool übernimmt Metadaten ohne Original-Previews, Thumbnails und Orientation. Bei einer Metadatenwarnung bleibt das exportierte Bild erhalten. Der Fortschritt zählt tatsächliche Ausgabedateien; die Verarbeitung lässt sich abbrechen.

## Portable Builds und Quellcode

| Plattform | Paket |
| --- | --- |
| Windows x64 | `AnaChroma_1.0_Windows_x64.zip` |
| Linux x64 | `AnaChroma_1.0_Linux_x64.tar.gz` |
| macOS Apple Silicon | `AnaChroma_1.0_macOS_AppleSilicon.tar.gz` |

Das vollständige [Release-Paket](https://github.com/muelli1975/AnaChroma/releases) entpacken und AnaChroma starten. Die mitgelieferten Programmdateien und Tools zusammenhalten. Windows enthält die benötigten Laufzeitkomponenten; Linux/macOS brauchen für Quellcodebetrieb Tcl/Tk und für ExifTool System-Perl. macOS-Builds sind ad-hoc signiert und nicht notarisiert.

Einstellungen und eigene Verfahren bleiben lokal in `settings.json` und `presets.json` neben dem Programm. Bei Schreibschutz wird auf den Benutzer-Konfigurationsordner ausgewichen. Pfade, Ausgabemodus, Sprache und Unterordnerwahl werden gemerkt.

Der Kern verwendet Python, Pillow und NumPy mit CustomTkinter. CIELab und ExifTool werden als separate Tools mit Lizenzen und zugehörigen Quellen gebündelt. Release-Pakete enthalten den passenden Programmquellstand unter `source`. Build-Details: [BUILD.md](docs/BUILD.md).

Quellcodebetrieb mit Python 3.10+ und Tcl/Tk:

```sh
python -m venv .venv
# .venv passend zur Plattform aktivieren.
python -m pip install -e .
python run_anachroma.py
```

## Lizenz

Copyright Christoph Müller. MIT-Lizenz für AnaChroma; Fremdkomponenten behalten ihre jeweiligen Lizenzen. Siehe [LICENSE.txt](LICENSE.txt) und [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Das Paket enthält den festen Programmordner `AnaChroma`; Versions- und Plattformangaben stehen im Namen des Downloadarchivs.
