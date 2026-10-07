# AnaChroma

[English](README.md)

**Hochwertige Anaglyphen aus SBS-Bildern**

AnaChroma ist ein kompaktes lokales Desktop-Werkzeug in Entwicklung, das Full-SBS-Stereobilder in hochwertige Anaglyphen umwandelt. Es baut auf den bewährten Verfahren der [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch) auf und ergänzt automatische Vorschau, Bildnavigation sowie komfortable Einzelbild- und Ordnerverarbeitung.

Die Anwendung ist für vollständig lokale Verarbeitung ausgelegt: kein Account, keine Cloud, kein Tracking und keine Online-Abhängigkeiten während der Nutzung.

## Entwicklungsstand

Der erste lauffähige Entwicklungsstand ist **0.1.0.dev1**. Die deutsche Oberfläche, die gemeinsame Engine, der Editor für eigene Presets und Einzelbild-/Ordnerexport sind implementiert. Das ist ein Entwicklungsbuild, noch kein Release von Version 1. Das bereitgestellte AnaChroma-Icon ist eingebunden. Native CIELab-Builds stehen noch aus; echte Stereofotos und die native Bedienung unter Windows/macOS müssen praktisch geprüft werden.

GitHub Actions bereitet Entwicklungspakete für Windows, Linux und macOS vor. Erfolgreiches Packaging allein bestätigt weder die Bildqualität noch die native Desktop-Kompatibilität. Siehe [Build-Anleitung](docs/BUILD.md) und [Prüfstand](docs/VALIDATION.md).

## Ablauf

1. Ein SBS-Bild öffnen oder einen Bildordner auswählen.
2. Durch die Bilder blättern und ein Anaglyphenverfahren wählen; die Vorschau aktualisiert sich automatisch.
3. Ausgabeordner und Bildgröße auswählen.
4. **Aktuelles Bild speichern** oder **Alle verarbeiten** wählen.

Beim Öffnen einer einzelnen Datei werden auch die anderen unterstützten Bilder im selben Ordner für die Navigation verfügbar. Die optionale Verarbeitung von Unterordnern erhält die Eingabeordnerstruktur in der Ausgabe.

## Unterstützte Eingabe

AnaChroma ist für parallele Full-SBS-Bilder in JPEG/JPG, PNG, TIFF/TIF, BMP und WebP vorgesehen. Links steht das linke, rechts das rechte Halbbild. Beide Ansichten müssen in voller Breite vorliegen; die Entzerrung von Half-SBS gehört nicht zum aktuellen Umfang.

Die EXIF-Orientierung wird beim Laden angewendet. Das ausgerichtete Bild muss eine gerade Breite besitzen, damit es in zwei gleich große Halbbilder geteilt werden kann.

## Anaglyphenverfahren und Vorschau

Die aktuelle AnaglyphBatch liefert 18 Verfahren, darunter Dubois LCD mit Rotkanalkorrektur, Dubois, Compromise, Wimmer, Cosima 3/4, Rendepth 1/2, iaian7, Color, Half-Color, Grey, Oldschool, Frans van den Poel, John Wattie, Dubois grün/magenta, Dubois amber/blau und externes CIELab Least Squares.

Es wird jeweils ein Verfahren ausgewählt. Die Verfahren behalten ihre eigenen Rechenregeln; sRGB-Linearisierung wird nur verwendet, wo die Referenzpipeline sie verlangt. Vorschau und Export nutzen denselben Verarbeitungskern. Die automatische Vorschau ist auf maximal 1024 px lange Seite begrenzt.

Der ausdrücklich sichtbare Einstieg **Eigenes Verfahren anlegen…** öffnet den Preset-Editor. Zwei 3 × 3-Matrizen lassen sich über Zahlenfelder, Schieberegler und das Mausrad mit einer eigenen Live-Vorschau einstellen. Die Matrixregler beginnen bei −2 bis +2 mit Schritten von 0,001; direkte Zahleneingaben erhalten feinere Koeffizienten und erweitern den Regler bei Bedarf. Das ist ein praktischer Bedienbereich, keine physikalische Grenze für Anaglyphen. Eigene Presets enthalten außerdem eine optionale Berechnung in linearem Licht, Helligkeits-/Kontrastanpassungen und einzelne RGB-Korrekturwerte. Die Einstellungen stehen direkt unter den Matrizen und werden lokal gespeichert; eingebaute Verfahren behalten ihr Referenzverhalten.

## Ausgabe

Standard ist **JPEG-Qualität 90, 4:4:4 ohne Chroma-Subsampling, mit optimierter JPEG-Codierung**. Zusätzlich gibt es die Option **JPEG-Qualität 95 für Druck/Archiv**. Die Skalierung verwendet Lanczos und erhält das Seitenverhältnis.

Verfügbare Größen:

- Original
- 1080p: eingepasst in 1920 × 1080 px
- 2160p: eingepasst in 3840 × 2160 px
- 2048 px lange Seite
- Benutzerdefinierte lange oder kurze Seite

Die Dateinamen verwenden die aktuellen Suffixe der AnaglyphBatch, beispielsweise `bild_dubois_lcd.jpg` oder `bild_compromise.jpg`.

Metadaten werden nach Möglichkeit mit ExifTool übernommen, ohne eingebettete Originalvorschauen, Vorschaubilder und Orientation-Tags. Ein Fehler bei der Metadatenübernahme wird gemeldet, ohne ein erfolgreich geschriebenes Bild zu verwerfen.

## Funktionsumfang

AnaChroma konzentriert sich auf die Konvertierung von SBS zu Anaglyphen. Stereojustage und Korrekturen bleiben Aufgabe von [StereoFine](https://github.com/muelli1975/StereoFine); die 2D-zu-3D-Konvertierung bleibt Aufgabe von [SplatTricia](https://github.com/muelli1975/SplatTricia).

Version 1 enthält keine Erkennung separater Links/Rechts-Paare, kein MPO-Splitting, keine Scheinfensterkorrektur, keine Thumbnail-Galerie, keine Ausgabe mit höherer Farbtiefe und keine Videoverarbeitung. Eine gezielte Ghosting-Kompensation benötigt ein gesondert geprüftes Verfahren und gehört noch nicht zur abgestimmten Umsetzung.

## Quellcode und Builds

Der Kern verwendet Python, Pillow und NumPy sowie CustomTkinter für die Oberfläche. Das vorhandene sRGB-Transfermodul aus SplatTricia wird unverändert übernommen. FFmpeg wird als reguläre Verarbeitungsengine nicht benötigt.

Das Build-Skript erzeugt ein portables Verzeichnis für die jeweilige Plattform. ExifTool und CIELab bleiben externe Komponenten und werden in diesen ersten Entwicklungspaketen nicht gebündelt. Plattformspezifische CIELab-Builds müssen geprüft werden, bevor ihre Verfügbarkeit in einem Release zugesagt wird.

Der abgestimmte Umfang steht in [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md), die Modulstruktur in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) und die Quellgrundlage in [docs/REFERENCE_BASELINE.md](docs/REFERENCE_BASELINE.md).

## Aus dem Quellcode starten

Python 3.10 oder neuer mit Tcl/Tk verwenden (Entwicklungspakete nutzen Python 3.12). Im Repository-Verzeichnis:

```sh
python -m venv .venv
# .venv mit dem üblichen Befehl der Plattform aktivieren.
python -m pip install -e .
python run_anachroma.py
```

Unter Windows mit `.venv\Scripts\activate` aktivieren, unter Linux/macOS mit `source .venv/bin/activate`. Manche Linux-Python-Distributionen benötigen ihr separates Tk-Paket.

ExifTool wird unter `tools/exiftool.exe` (Windows), `tools/exiftool` oder im System-PATH gefunden. Begleitdateien der Windows-ExifTool-Distribution müssen neben deren Programmdatei bleiben. CIELab wird unter `tools/cielab/cielab.exe`, `tools/cielab/cielab` oder im PATH gefunden. Ohne ExifTool bleibt der Export mit einer Metadatenwarnung möglich; ohne CIELab sind die anderen 17 Verfahren nutzbar.

Standardausgabe ist `output` neben dem Programm bzw. dem Quellcheckout. Pfade und Unterordneroption stehen in `settings.json`, eigene Verfahren in `presets.json`. Bei einem schreibgeschützten Programmordner wird der Benutzer-Konfigurationsordner verwendet. Fertige Ausgaben mit gleichem Namen werden erst nach vollständigem Schreiben des neuen Bildes ersetzt; kollidierende Eingabenamen werden abgelehnt.

Die [Editorbeschreibung](docs/PRESET_EDITOR.md) erklärt Matrixrichtung, Linearisierung und Kanalkorrekturen. Bei einer aus dem Web übernommenen Matrix deren Rechenanleitung beachten: Der Editor erkennt nicht automatisch, ob sie lineares RGB voraussetzt.

## Lizenz

Der Quellcode und die ursprüngliche Dokumentation von AnaChroma, erstellt von Christoph Müller, stehen unter der **MIT-Lizenz**. Drittkomponenten behalten ihre jeweiligen eigenen Lizenzen.

Siehe [LICENSE.txt](LICENSE.txt) und [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
