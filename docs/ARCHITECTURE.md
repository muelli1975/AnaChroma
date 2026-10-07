# AnaChroma – Geplante Architektur

Stand: 7. Oktober 2026. Dies ist die vorgesehene Struktur, keine Beschreibung bereits implementierter Module.

## Aufbau

Ein kleiner Launcher startet das Paket `anachroma` unter `src/`. Die reine Verarbeitung ist unabhängig von GUI und Packaging.

| Bereich | Aufgabe |
| --- | --- |
| `color_transfer.py` | Vorhandene sRGB-Funktionen aus SplatTricia unverändert übernehmen |
| `matrices.py` | Verfahren, Anzeigenamen, Suffixe, Matrizen und Verarbeitungsmodi |
| `engine.py` | Reine RGB-Paarverarbeitung; gemeinsame Mathematik für Vorschau und Export |
| `inputs.py` | Bildliste, orientiertes RGB-Laden und sauberes SBS-Teilen |
| `export.py` | Größenberechnung, Lanczos, JPEG 90/95 und sichere Zieldateien |
| `metadata.py` | ExifTool-Suche, Metadatenübernahme und verständliche Warnungen |
| `cielab.py` | Externer Prozess mit separaten Halbbildern, Zeitlimit und Abbruch |
| `worker.py` | Jobs, Nachrichtenqueue und Abbruchsignale |
| `gui.py` / `theme.py` | Kompakte Oberfläche und gemeinsame Gestaltungswerte |
| `settings.py` | Kleine JSON-Persistenz für Pfade und Unterordneroption |

Weitere Trennungen erfolgen nur, wenn der tatsächliche Code sie benötigt. Keine StereoFine-Justage-, Disparitäts-, Sidecar- oder SHARP-Module übernehmen.

## Auftragszustand

Ein Exportauftrag erhält eine feste Bildliste und eine Kopie der gewählten Einstellungen. Laufende Aufträge lesen keine veränderlichen Tk-Variablen. Vorschauaufträge tragen Kennungen; Ergebnisse überholter Anforderungen werden verworfen.

Der GUI-Thread verwaltet Widgets und liest die Nachrichtenqueue über `after()`. Worker melden Status, Ergebnis, Fehler oder Abbruch. Regelmäßige Abbruchprüfungen erfolgen in der streifenweisen Engine; externe Prozesse benötigen zusätzlich eine eigene Beendigung.

## Verarbeitung und Ausgabe

Ein normaler Export berechnet die Anaglyphe und skaliert anschließend. CIELab erhält bereits skalierte linke/rechte PNGs in einem auftragseigenen temporären Verzeichnis. Beide Wege verwenden dieselben Ausgabegrößen, JPEG-Parameter und Metadatenregeln.

Ein fertiges JPEG wird zunächst temporär geschrieben, mit Metadaten versehen und erst danach am endgültigen Ziel ersetzt. Fehler beim Berechnen oder Schreiben dürfen eine vorhandene fertige Datei nicht beschädigen. Metadatenfehler bleiben als gesonderte Warnung sichtbar.

## Ressourcen und Packaging

- `assets/`: eigener nachgelieferter Icon-Satz und unveränderte `ready.wav`.
- `tools/`: lokale bzw. mit Releases gebündelte ExifTool-/CIELab-Distributionen; Binärdateien gehören nicht unkontrolliert in das Quellrepository.
- `docs/`: Spezifikation und technische Quellen.
- `tests/`: später gezielte Engine-, Pfad-, Metadaten- und Abbruchprüfungen.
- Build-Skripte und GitHub Actions folgen, sobald eine lauffähige Basis vorhanden ist.

Die Plattformunterschiede bleiben möglichst auf Ressourcenpfade, externe Tools, Soundwiedergabe und Packaging begrenzt. Kein Release wird als geprüft bezeichnet, bevor die betreffende Plattform tatsächlich getestet wurde.
