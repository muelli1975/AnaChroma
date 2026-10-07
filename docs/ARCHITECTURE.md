# AnaChroma – Architektur

Stand: 7. Oktober 2026. Diese Module sind im ersten Entwicklungsstand implementiert; der praktische Plattform-Prüfstand steht in [VALIDATION.md](VALIDATION.md).

## Aufbau

Ein kleiner Launcher startet das Paket `anachroma` unter `src/`. Die reine Verarbeitung ist unabhängig von GUI und Packaging.

| Bereich | Aufgabe |
| --- | --- |
| `color_transfer.py` | sRGB-Transferfunktionen |
| `matrices.py` | Verfahren, Anzeigenamen, Suffixe, Matrizen und Verarbeitungsmodi |
| `presets.py` / `preset_editor.py` | Validierte eigene Verfahren, lokale Speicherung und Editor mit Zahlenfeldern/Reglern |
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

Beim Einstellen eigener Verfahren werden die geladenen Vorschau-Halbbilder wiederverwendet. Während kontinuierlicher Reglerbewegungen verarbeitet die Vorschau regelmäßig den neuesten gültigen Entwurf, statt auf eine Bewegungspause zu warten. Überholte Anforderungen werden zusammengefasst; eine wachsende Warteschlange ist ausgeschlossen. Eine abschließende Aktualisierung stellt den letzten Wert nach Ende der Bewegung dar.

Mausradereignisse gehören dem ausgewählten Regler und dürfen nicht zugleich Bildnavigation oder Dialogscrollen auslösen. Die Ereignisnormalisierung berücksichtigt Windows, macOS und Linux. Zahlenfeld und Regler teilen denselben Koeffizientenwert; Anzeigepräzision und Schrittweite verändern keine unberührten Preset-Werte.

Eingebaute Referenzverfahren und eigene Preset-Entwürfe werden getrennt gehalten. Ein gespeichertes eigenes Preset beschreibt ausschließlich die im Editor sichtbaren Rechenschritte; nicht darstellbare Speziallogik wird nicht versteckt in eine Vorlage übernommen.

## Verarbeitung und Ausgabe

Ein normaler Export berechnet die Anaglyphe und skaliert anschließend. CIELab erhält bereits skalierte linke/rechte PNGs in einem auftragseigenen temporären Verzeichnis. Beide Wege verwenden dieselben Ausgabegrößen, JPEG-Parameter und Metadatenregeln.

Ein fertiges JPEG wird zunächst temporär geschrieben, mit Metadaten versehen und erst danach am endgültigen Ziel ersetzt. Fehler beim Berechnen oder Schreiben dürfen eine vorhandene fertige Datei nicht beschädigen. Metadatenfehler bleiben als gesonderte Warnung sichtbar.

## Ressourcen und Packaging

- `assets/`: eigener nachgelieferter Icon-Satz und unveränderte `ready.wav`.
- `tools/`: lokale bzw. mit Releases gebündelte ExifTool-/CIELab-Distributionen; Binärdateien gehören nicht unkontrolliert in das Quellrepository.
- `docs/`: Spezifikation und technische Quellen.
- `tests/`: unabhängige Batch-Filtervergleiche sowie GUI-, Pfad-, Metadaten- und Abbruchprüfungen.
- `scripts/build.py` und `.github/workflows/build.yml`: portable Entwicklungspakete und Tests für drei Plattformen. Externe Tools werden noch nicht gebündelt.

Die Plattformunterschiede bleiben möglichst auf Ressourcenpfade, externe Tools, Soundwiedergabe und Packaging begrenzt. Kein Release wird als geprüft bezeichnet, bevor die betreffende Plattform tatsächlich getestet wurde.
