# AnaChroma

[English](README.md)

**Hochwertige Anaglyphen aus SBS-Bildern**

AnaChroma ist ein kompaktes lokales Desktop-Werkzeug in Entwicklung, das Full-SBS-Stereobilder in hochwertige Anaglyphen umwandelt. Es baut auf den bewährten Verfahren der [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch) auf und ergänzt automatische Vorschau, Bildnavigation sowie komfortable Einzelbild- und Ordnerverarbeitung.

Die Anwendung ist für vollständig lokale Verarbeitung ausgelegt: kein Account, keine Cloud, kein Tracking und keine Online-Abhängigkeiten während der Nutzung.

## Entwicklungsstand

AnaChroma befindet sich am Anfang der Entwicklung. Das Repository enthält derzeit die Projektspezifikation, technische Referenznotizen und den gemeinsamen Abschlusssound. Eine lauffähige Anwendung und herunterladbare Releases sind noch nicht verfügbar. Die folgenden Funktionen beschreiben den abgestimmten Umfang von Version 1.

## Geplanter Ablauf

1. Ein SBS-Bild öffnen oder einen Bildordner auswählen.
2. Durch die Bilder blättern und ein Anaglyphenverfahren wählen; die Vorschau aktualisiert sich automatisch.
3. Ausgabeordner und Bildgröße auswählen.
4. **Aktuelles Bild speichern** oder **Alle verarbeiten** wählen.

Beim Öffnen einer einzelnen Datei werden auch die anderen unterstützten Bilder im selben Ordner für die Navigation verfügbar. Die optionale Verarbeitung von Unterordnern erhält die Eingabeordnerstruktur in der Ausgabe.

## Unterstützte Eingabe

Version 1 ist für parallele Full-SBS-Bilder in JPEG/JPG, PNG, TIFF/TIF, BMP und WebP vorgesehen. Links steht das linke, rechts das rechte Halbbild. Beide Ansichten müssen in voller Breite vorliegen; die Entzerrung von Half-SBS gehört nicht zum aktuellen Umfang.

Die EXIF-Orientierung wird beim Laden angewendet. Das ausgerichtete Bild muss eine gerade Breite besitzen, damit es in zwei gleich große Halbbilder geteilt werden kann.

## Anaglyphenverfahren und Vorschau

Die aktuelle AnaglyphBatch liefert 18 Verfahren, darunter Dubois LCD mit Rotkanalkorrektur, Dubois, Compromise, Wimmer, Cosima 3/4, Rendepth 1/2, iaian7, Color, Half-Color, Grey, Oldschool, Frans van den Poel, John Wattie, Dubois grün/magenta, Dubois amber/blau und externes CIELab Least Squares.

Es wird jeweils ein Verfahren ausgewählt. Die Verfahren behalten ihre eigenen Rechenregeln; sRGB-Linearisierung wird nur verwendet, wo die Referenzpipeline sie verlangt. Vorschau und Export nutzen denselben Verarbeitungskern. Die automatische Vorschau ist auf maximal 1024 px lange Seite begrenzt.

## Ausgabe

Standard ist **JPEG-Qualität 90, 4:4:4 ohne Chroma-Subsampling, mit optimierter JPEG-Codierung**. Zusätzlich ist die Option **JPEG-Qualität 95 für Druck/Archiv** vorgesehen. Die Skalierung verwendet Lanczos und erhält das Seitenverhältnis.

Geplante Größen:

- Original
- 1080p: eingepasst in 1920 × 1080 px
- 2160p: eingepasst in 3840 × 2160 px
- 2048 px lange Seite
- Benutzerdefinierte lange oder kurze Seite

Die Dateinamen verwenden die aktuellen Suffixe der AnaglyphBatch, beispielsweise `bild_dubois_lcd.jpg` oder `bild_compromise.jpg`.

Metadaten werden nach Möglichkeit mit ExifTool übernommen, ohne eingebettete Originalvorschauen, Vorschaubilder und Orientation-Tags. Ein Fehler bei der Metadatenübernahme wird gemeldet, ohne ein erfolgreich geschriebenes Bild zu verwerfen.

## Funktionsumfang

AnaChroma konzentriert sich auf die Konvertierung von SBS zu Anaglyphen. Stereojustage und Korrekturen bleiben Aufgabe von [StereoFine](https://github.com/muelli1975/StereoFine); die 2D-zu-3D-Konvertierung bleibt Aufgabe von [SplatTricia](https://github.com/muelli1975/SplatTricia).

Version 1 enthält keine Erkennung separater Links/Rechts-Paare, kein MPO-Splitting, keine Scheinfensterkorrektur, keinen Matrixeditor, keine Thumbnail-Galerie, keine Ausgabe mit höherer Farbtiefe und keine Videoverarbeitung.

## Quellcode und Builds

Der geplante Kern verwendet Python, Pillow und NumPy sowie CustomTkinter für die Oberfläche. Das vorhandene sRGB-Transfermodul aus SplatTricia wird übernommen. FFmpeg wird als reguläre Verarbeitungsengine nicht benötigt.

Portable Builds sind für Windows, Linux und macOS vorgesehen. ExifTool und CIELab bleiben externe Komponenten. Plattformspezifische CIELab-Builds müssen geprüft werden, bevor ihre Verfügbarkeit in einem Release zugesagt wird.

Der abgestimmte Umfang steht in [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md), die vorgesehene Struktur in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) und die Quellgrundlage in [docs/REFERENCE_BASELINE.md](docs/REFERENCE_BASELINE.md).

## Lizenz

Der Quellcode und die ursprüngliche Dokumentation von AnaChroma, erstellt von Christoph Müller, stehen unter der **MIT-Lizenz**. Drittkomponenten behalten ihre jeweiligen eigenen Lizenzen.

Siehe [LICENSE.txt](LICENSE.txt) und [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
