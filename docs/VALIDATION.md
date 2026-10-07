# AnaChroma – Prüfstand 0.1.0.dev2

Stand: 7. Oktober 2026. Diese Datei unterscheidet automatisierte technische Prüfungen von noch ausstehender stereoskopischer Praxisprüfung.

Lokaler Gesamtlauf: **65 Tests bestanden**, einschließlich GUI, tatsächlichem ExifTool, aller 17 internen FFmpeg-Referenzpipelines, echter nativer CIELab-Berechnung und SBS-Startvorschau. Auch das gepackte Linux-Programm hat die Startvorschau berechnet und angezeigt; sein gebündeltes CIELab bestand den Unicode-/RGB8-/Größentest.

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
| GUI unter virtueller Linux-Anzeige | Zahleneingabe mit Dezimalkomma/hoher Präzision, Reglererweiterung, fokussiertes Mausrad, Validierung, Preset-Rundlauf, Abbrechen, Navigation und Einzelbildexport. |
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

Der Linux-Build aus unveränderten Original-Rechenquellen verarbeitet das mitgelieferte SBS-Bild mit 1024 × 576 Ausgabepixeln hier in etwa 2,7 Sekunden. Das ist eine Messung auf dieser Entwicklungsmaschine, keine allgemeine Laufzeitzusage. Echte RGB8-Berechnung, Wiederholbarkeit, Größenprüfung, Unicode-Pfade, Skalierung vor CIELab und JPEG 4:4:4 werden separat geprüft. Windows vergleicht Zufallsfarben, Graustufen, Farbfelder und das verkleinerte SBS-Beispiel direkt mit der Binärdatei aus Batch 1.0. Bericht und verlustfreie Vergleichsbilder werden als CI-Artefakt gespeichert.

Die aufgezeichneten verlustfreien Ausgaben der tatsächlichen Batch-1.0-Datei liegen als hashgeprüfte PNG-Testdaten in `tests/fixtures/cielab_reference.json`. Sie werden auf jeder Plattform gegen den neu gebauten CIELab-Prozess geprüft. Mit präzisen Compileroptionen stimmen hier unter Linux alle vier Referenzfälle pixelgenau überein. Fast-Math verursachte einzelne Abweichungen und wird deshalb nicht verwendet.
