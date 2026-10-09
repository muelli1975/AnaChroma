# AnaChroma – Validierung

## Version 1.0

Lokaler Abschlusslauf vom 9. Oktober 2026: **100 Kerntests und 12 isolierte GUI-Prüfungen bestanden**. Die Prüfungen decken Mehrfachausgabe/Kollisionen/Abbruch, echte CIELab- und FFmpeg-Referenzen, Metadaten mit ExifTool, EXIF-Tags 1–8 für JPEG/PNG/TIFF/WebP, modeless Editor und große Hauptvorschau, DE/EN und physische Vorschauabmessungen bei 150 % Skalierung ab. Die anschließende Erweiterung zum Hinweis und zur bytegetreuen Sicherung älterer Helligkeits-/Kontrast-Presets bestand alle 15 Preset-/Dateitests. Das originale SBS-Asset ist 7680 × 2160 px und entspricht SHA-256 `932910b06a95927c62ee9421b4971b833c985fb9b598381a990094e9627a4e32`. Plattformbuilds und Paketprüfungen werden für jeden Commit in GitHub Actions ausgeführt. Ein erfolgreicher älterer Lauf belegt nicht den aktuellen Build.

Parallel geprüfter Freeda-1.2-Stand: 110 Unit-Tests und alle zwölf auf Linux anwendbaren GUI-Skripte bestanden ohne Tk-Callback-Fehler; die Windows-Taskbar-Prüfung ist unter Linux ausdrücklich nicht anwendbar. Die portierte Anaglyphenrechnung und sRGB-Transferdatei sind bytegleich mit SplatTricias Referenz. SplatTricias unveränderter Ladeweg bestand zudem 16 synthetische Smartphone-Hochformatfälle (JPEG/HEIC, Orientierungen 1–8) einschließlich Höhenbegrenzung. Dies ist kein Nachweis anhand der früheren Original-Smartphone-Dateien. Die AnaglyphBatch-Verarbeitung wurde nicht geändert; die früheren Windows-Praxistests konnten nicht aus dem Gesprächsarchiv rekonstruiert werden.

## Historischer Stand 0.1.0.dev3

Stand: 7. Oktober 2026. Diese Datei unterscheidet automatisierte technische Prüfungen von noch ausstehender stereoskopischer Praxisprüfung.

Lokaler Gesamtlauf: **72 Tests bestanden**, einschließlich GUI, tatsächlichem ExifTool, aller 17 internen FFmpeg-Referenzpipelines, echter nativer CIELab-Berechnung und SBS-Startvorschau. Das gepackte Linux-Programm hat das SBS-Startbild angezeigt, über sein gebündeltes CIELab eine weitere Vorschau und ein JPEG erzeugt und mit dem ebenfalls gebündelten ExifTool den Artist-Tag übernommen. Sein CIELab bestand zusätzlich den Unicode-/RGB8-/Größentest.

## Automatisierte Prüfungen

Die Tests prüfen die Matrixdefinitionen unabhängig gegen die unveränderte Batch-Referenz in `tests/reference_batch.bat` (AnaglyphBatch `8ef0a5d`), nicht gegen eine zweite Kopie der Python-Konstanten.

| Prüfung | Aussage |
| --- | --- |
| Alle 18 Verfahrensdefinitionen | Modi, Suffixe und Matrixwerte entsprechen dem festgehaltenen Batch-Stand. |
| Alle 17 internen FFmpeg-Pipelines | Verlustfreie RGB-Zwischenausgaben aus tatsächlichen Batch-Filtern; maximale erlaubte Differenz 2 von 255 pro Kanal. Im geprüften Lauf eingehalten. CIELab ist separat. |
| Kanalführung und Clipping | Handprüfbare Rot/Cyan-/Grey-Fälle; getrenntes Clipping vor Addition; sRGB-/lineare Mischung unterscheiden sich wie vorgesehen. |
| Vorlagen | Alle 16 darstellbaren eingebauten Verfahren ergeben als eigene Kopie exakt dieselben Pixel. |
| Export | Lanczos-Größen, Vergrößerung, JPEG 4:4:4, sRGB-Profil, sichere Ersetzung und Schutz bei Abbruch. |
| Eingabe/Pfade | Orientierung, ungerade Breite, Alpha-Verwerfen, natürliche Navigation, Rekursion und Namenskollisionen. |
| Metadaten | Tatsächliches ExifTool: Artist erhalten, angewendete Orientierung nicht zurückkopiert, fertige EXIF-Maße und sRGB-Profil korrekt. |
| GUI unter virtueller Linux-Anzeige | Zahleneingabe mit Dezimalkomma/hoher Präzision, Reglererweiterung, fokussiertes Mausrad, Validierung, Preset-Rundlauf, Abbrechen, Navigation, Vorlagenidentität, DE/EN-Wechsel, Regler für Helligkeit/Kontrast, Wiederaufnahme nach fehlendem CIELab/ExifTool und rekursiver Ordnermodus. |
| Worker/Prozesse | Neueste Vorschau ersetzt veraltete Jobs; externe Prozesse mit umfangreicher Ausgabe, Abbruch und Zeitlimit. |
| CIELab-Adapter | Testprozess prüft separate PNGs, Eingabegrößen und temporäre Bereinigung; dies prüft nicht den echten CIELab-Algorithmus. |

Die Referenzvergleiche verwenden reproduzierbare synthetische RGB-Werte; zusätzliche handprüfbare Tests behandeln Graustufen und Kanalführung. Sie erfolgen **vor JPEG**: Pillow und cjpeg werden nicht als pixelgleiche JPEG-Encoder behandelt. Auch Lanczos-Implementierungen und Rundung zwischen Pillow und FFmpeg sind nicht als pixelidentisch zugesagt.

Der lokale Linux-PyInstaller-Build wurde erstellt und unter virtueller Anzeige erfolgreich gestartet. Die lokale Python-Distribution verwendet Tcl/Tk 9; deren Bibliotheken werden bei Bedarf ausdrücklich mitgeliefert. Konkrete CI-Ergebnisse sind bei den jeweiligen GitHub-Actions-Läufen zu sehen und dürfen nicht aus der bloßen Workflow-Datei abgeleitet werden.

## Noch erforderlich vor einem Release

- Echte SBS-Fotos mit Rot/Cyan-, Grün/Magenta- und Amber/Blau-Brillen gegen die Batch beurteilen, insbesondere gesättigte Farben, Spitzlichter, tiefe Schatten und Ghosting.
- Normalen Export und Vorschau über mehrere Auflösungen vergleichen; reduzierte Vorschau ist keine pixelgenaue Vollauflösungsansicht.
- Lange Ordnerläufe, hochauflösende Bilder und native Windows-/macOS-Bedienung prüfen.
- Den Windows-Vergleich gegen das originale CIELab-Executable aus AnaglyphBatch 1.0 und die nativen Builds anhand der jeweiligen CI-Ergebnisse bewerten; eine bloße erfolgreiche Kompilierung belegt keine Pixelgleichheit.
- Native Release-Pakete und vollständige Lizenzmaterialien prüfen.

Allgemeine Helligkeit/Kontrast und Kanalpotenzen sind kontrollierbare Bildoperationen, keine behauptete automatische Ghosting-Korrektur. Eine solche Funktion setzt ein konkret validiertes, von Brille und Wiedergabemedium abhängiges Verfahren voraus.

## Tests ausführen

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
```

Auf Linux die GUI-Prüfungen mit `xvfb-run -a python -m pytest -q` ausführen. FFmpeg und ExifTool auf PATH ermöglichen die unabhängigen Referenzprüfungen; ansonsten werden diese Tests ausdrücklich übersprungen. Die CI installiert beide im Linux-Job.

## Native CIELab-Prüfung

Der Linux-Build aus unveränderten Original-Rechenquellen verarbeitet das mitgelieferte SBS-Bild mit 1024 × 576 Ausgabepixeln hier in etwa 2,8 Sekunden. Das ist eine Messung auf dieser Entwicklungsmaschine, keine allgemeine Laufzeitzusage. Echte RGB8-Berechnung, Wiederholbarkeit, Größenprüfung, Unicode-Pfade, Skalierung vor CIELab und JPEG 4:4:4 werden separat geprüft. Windows vergleicht Zufallsfarben, Graustufen, Farbfelder und das verkleinerte SBS-Beispiel direkt mit der Binärdatei aus Batch 1.0. Bericht und verlustfreie Vergleichsbilder werden als CI-Artefakt gespeichert.

Die aufgezeichneten verlustfreien Ausgaben der tatsächlichen Batch-1.0-Datei liegen als hashgeprüfte PNG-Testdaten in `tests/fixtures/cielab_reference.json`. Sie werden auf jeder Plattform gegen den neu gebauten CIELab-Prozess geprüft. Mit präzisen Compileroptionen stimmen hier unter Linux alle vier Referenzfälle pixelgenau überein. Fast-Math verursachte einzelne Abweichungen und wird deshalb nicht verwendet.

Der Plattformlauf für **0.1.0.dev3** [37662888079](https://github.com/muelli1975/AnaChroma/actions/runs/37662888079) ist auf Windows, Linux und macOS erfolgreich abgeschlossen. Linux: 72 Tests bestanden. Windows: 55 bestanden, 17 FFmpeg-Referenztests mangels Referenzwerkzeug übersprungen. Zusätzlich haben alle drei gepackten Programme das SBS-Startbild angezeigt, CIELab berechnet und ein JPEG einschließlich ExifTool-Metadatenübernahme geschrieben. Der Windows-Vergleich mit Batch 1.0 ist in allen vier verlustfreien Referenzfällen pixelgleich (maximale Kanaldifferenz 0). Diese technischen Prüfungen ersetzen weiterhin den praktischen Vergleich realer Stereofotos mit Anaglyphenbrillen.
