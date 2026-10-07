# AnaChroma – Projektgrundlage für Version 1

Stand: 7. Oktober 2026. Diese Spezifikation hält die Projektbibel und die anschließend bestätigten Abgleiche mit den aktuellen GitHub-Ständen fest. Sie beschreibt den vereinbarten v1-Funktionsumfang; der erste Entwicklungsstand ist implementiert, aber noch keine fertige v1. Der tatsächliche Prüfstand steht in [VALIDATION.md](VALIDATION.md).

## Name, Zweck und Grundhaltung

- Name: **AnaChroma**
- Untertitel: **Hochwertige Anaglyphen aus SBS-Bildern**
- Leitsatz: **Batch-Qualität, aber als schönes, kompaktes, lokales GUI-Werkzeug.**

AnaChroma ist ein eigenständiges, fokussiertes GUI-Werkzeug zur hochwertigen Konvertierung paralleler Full-SBS-Bilder in Anaglyphen. Die bewährte AnaglyphBatch ist die fachliche Referenz. Die Anwendung arbeitet lokal/offline, ohne Cloud, Account, Tracking, automatische Downloads oder externe Web-Abhängigkeiten zur Laufzeit. Ziel sind portable Builds für Windows, Linux und macOS.

StereoFine bleibt für Stereojustage und Korrekturen zuständig, SplatTricia für 2D-zu-3D/SBS. TransCora ist ein separates späteres Videoprojekt.

## Verbindliche Quellgrundlage

Die geprüften Quellstände sind in [REFERENCE_BASELINE.md](REFERENCE_BASELINE.md) festgehalten. Gegenüber der ursprünglichen Projektbibel sind ausdrücklich bestätigt:

- **18 Verfahren** aus der aktuellen Batch, einschließlich Cosima 3/4, Frans van den Poel und John Wattie.
- Aktuelle Reihenfolge, Namen und Dateinamenssuffixe; die erste Variante heißt **Dubois LCD (Sanders/McAllister) + rot**, Suffix **`dubois_lcd`**.
- In AnaChroma v1 wird **ein einzelnes Verfahren** ausgewählt. Die Mehrfachauswahl der heutigen Batch wird nicht übernommen.
- 1080p und 2160p bedeuten Einpassen in die entsprechenden Breite/Höhe-Grenzen.
- Bei CIELab werden die separaten Halbbilder **vor** der externen Berechnung auf Ausgabegröße gebracht, wie in der Batch.
- Das bereitgestellte Icon wird unverändert verwendet. Als Abschlusssound wird die vorhandene **`ready.wav` unverändert** übernommen.
- Der ursprünglich ausgeschlossene Matrixeditor wird als übersichtlicher Editor für **eigene Verfahren und lokal gespeicherte Presets** in v1 aufgenommen. Ein sichtbarer Einstieg, Schieberegler, Mausradbedienung und laufende Vorschau gehören dazu.

## Kern und Verarbeitung

Python, Pillow und NumPy bilden den Kern. CustomTkinter übernimmt die Oberfläche wie bei den bestehenden GUI-Werkzeugen. OpenCV ist für den Python-Kern nicht erforderlich; Abhängigkeiten einer externen CIELab-Binary sind davon getrennt. FFmpeg und cjpeg sind keine regulären Laufzeitabhängigkeiten von AnaChroma v1.

Normaler Exportablauf:

1. Bild laden und EXIF-Orientation anwenden.
2. Nach RGB konvertieren und auf gerade SBS-Breite prüfen.
3. SBS in zwei gleich große Ansichten teilen.
4. Verfahren mit seiner jeweiligen Transfer-, Matrix-, Clipping- und Korrekturlogik anwenden.
5. Fertige Anaglyphe auf die gewählte Ausgabegröße skalieren.
6. JPEG schreiben, Metadaten übernehmen und die fertige Datei am Ziel ablegen.

Die Matrixrechnung erfolgt intern mit Float-Werten. Eine streifenweise Berechnung nach dem Vorbild der bestehenden Anaglyphenmodule begrenzt den Speicherbedarf und ermöglicht regelmäßige Abbruchprüfungen. Sie darf die Formeln nicht verändern.

Die vorhandenen Funktionen `srgb_to_linear` und `linear_to_srgb` aus SplatTricia werden übernommen. Es wird keine neue Transferfunktion entwickelt. Linearisierung erfolgt nur für Verfahren mit entsprechender Referenzpipeline.

Pro Verfahren werden die Batch-Modi `linear`, `srgb`, `rendepth`, `iaian7` und `cielab` abgebildet. Die bewährte Dubois-LCD-Pipeline begrenzt die beiden Matrixbeiträge einzeln vor der Addition; die Rotkorrektur erfolgt nach der Rückwandlung nach sRGB. Rendepth und iaian7 behalten ihre speziellen Rechenfolgen. Vorschau und Export verwenden denselben fachlichen Kern.

## Eingabe und Navigation

Unterstützte Endungen: `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.bmp`, `.webp`, unabhängig von Groß-/Kleinschreibung.

- **Datei laden:** Bildliste aus dem zugehörigen Ordner aufbauen und die gewählte Datei anzeigen.
- **Ordner laden:** Bildliste aus dem Ordner aufbauen und das erste Bild anzeigen.
- **Unterordner mitverarbeiten:** optional rekursiv suchen und die Ordnerstruktur in der Ausgabe erhalten.
- Eigene Ausgabe- und temporäre Ordner dürfen nicht erneut als Eingaben eingesammelt werden.
- Die Navigationsliste wird für jeden Auftrag festgehalten; während des Exports neu erzeugte Dateien erweitern den Auftrag nicht.

Navigation: vorheriges/nächstes Bild über Buttons, Mausrad, Pfeiltasten links/rechts sowie Bild auf/Bild ab. Pos1/Ende führen zum ersten/letzten Bild. Die Buttons orientieren sich an StereoFine (`◀ Vorheriges`, `Nächstes ▶`). Dort dienen Pfeiltasten bisher der Justage; AnaChroma verwendet sie entsprechend seiner eigenen Aufgabe zum Blättern. Eingabefelder behalten ihre normale Tastaturbedienung.

Anzeige: beispielsweise `12/83 · bild012_sbs.jpg`. Keine Thumbnail-Galerie und keine Dateiverwaltungsoberfläche.

## Vorschau

- Maximal **1024 px lange Seite**, Seitenverhältnis erhalten.
- Automatische Aktualisierung bei Bildwechsel, neuer Eingabe, Verfahrenswechsel und relevanten Einstellungen.
- Einzelne Einstellungswechsel um etwa **150–250 ms** entprellen. Während fortlaufender Reglerbewegungen die neuesten Werte regelmäßig anzeigen (Startziel etwa alle **100 ms**); nicht erst nach Loslassen oder einer Bewegungspause aktualisieren.
- Alte Berechnungsergebnisse dürfen eine neu angeforderte Vorschau nicht überschreiben.
- Normale Verfahren sollen schnell reagieren; CIELab darf langsamer sein.
- CIELab zeigt einen sichtbaren Busy-Zustand: **CIELab-Vorschau wird erzeugt...**
- Berechnungen laufen außerhalb des GUI-Threads; die Oberfläche bleibt bedienbar.

Die Vorschau ist eine verkleinerte Ansicht zur Beurteilung, kein Versprechen eines pixelidentischen verkleinerten Exports. Insbesondere CIELab berechnet auf der jeweiligen Zielauflösung.

## Eigene Verfahren und Preset-Editor

Im Hauptfenster steht bei der Auswahl **Verfahren** ein ausdrücklich sichtbarer Button **Eigenes Verfahren anlegen…**. Eine eigene gespeicherte Auswahl kann zusätzlich über **Bearbeiten…** geöffnet werden. Ein Eintrag **Eigene: <Name>** macht eigene Verfahren in der Liste erkennbar. Die Möglichkeit, ein Verfahren anzulegen, darf nicht ausschließlich hinter einer unklaren Verwaltungsbezeichnung verborgen sein.

Der Editor zeigt **Matrix links** und **Matrix rechts** nebeneinander, jeweils als 3 × 3-Raster. Spalten bezeichnen die Eingangsanteile R/G/B, Zeilen die ausgegebenen R/G/B-Kanäle. Jeder Koeffizient erhält ein Zahlenfeld mit einem zugehörigen kleinen Schieberegler. Zahlenfeld und Regler bleiben synchron; der ausgewählte Wert wird deutlich hervorgehoben.

Quellenbasierte Festlegung der Regler:

- Bereiche, Neutralwerte und Schrittweiten werden pro Parameter aus dokumentierten Referenzverfahren und der tatsächlich verwendeten Formel abgeleitet. Ein gemeinsamer pauschaler Bereich für alle Regler wird nicht festgelegt. Die Quellen und noch offenen Punkte stehen in [Technische Quellgrundlage](REFERENCE_BASELINE.md#regler-und-referenzprogramme).
- Für Matrixkoeffizienten müssen negative Werte und Werte über 1 möglich bleiben. Die SPM-Hilfe zeigt beides; sie dokumentiert jedoch keine allgemeinen Eingabegrenzen. Die bereits vorhandenen Batch-Koeffizienten dürfen nicht begrenzt werden. Der Anfangsbereich **−2 bis +2** folgt der dokumentierten Kanalgewichtung in Photoshop (−200 % bis +200 %). Er deckt alle Batch-Koeffizienten ab und ist eine Bedienkonvention, keine physikalische Zulässigkeitsgrenze. Direkte Zahleneingaben erweitern den sichtbaren Bereich.
- Eine Mausrad-Schrittweite von **0,001** für Matrixkoeffizienten lässt sich aus SPMs Darstellung in ganzzahligen Tausendsteln ableiten. Das ist eine begründete Bedienentscheidung für AnaChroma, keine Behauptung über SPMs Mausradverhalten. Feinere Zahlenwerte bleiben erhalten; weitere Schrittweiten für Zusatztasten werden erst mit einer begründeten Bedienentscheidung ergänzt.
- Gamma, Kanalpotenz, Helligkeit und Kontrast sind unterschiedliche Parameter. Ein dokumentierter Bereich darf nur bei entsprechend geklärter Rechenvorschrift übertragen werden. Insbesondere ist SPMs Gamma-Bereich nicht automatisch der Bereich der bestehenden Batch-Kanalpotenzen.
- Das Mausrad verändert nur den gezielt ausgewählten Regler. Dasselbe Ereignis darf nicht gleichzeitig den Dialog scrollen oder zum nächsten Bild wechseln. Kleine Trackpad-Deltas werden plattformgerecht gesammelt, ohne willkürlich große Sprünge zu erzeugen.
- Bestehende Koeffizienten bleiben mit ihrer vorhandenen Genauigkeit erhalten. Eine Regleränderung quantisiert nicht sämtliche übrigen Matrixwerte.
- Dezimalpunkt und Dezimalkomma in einzelnen Zahlenfeldern akzeptieren. Negative Werte ausdrücklich zulassen. Ungültige oder unvollständige Eingaben nachvollziehbar markieren; sie dürfen die Berechnung nicht starten.
- Die Vorschau reagiert bereits beim Ziehen und bei Mausradschritten. Veraltete Ergebnisse werden verworfen; laufende Änderungen erzeugen keine lange Warteschlange.

Direkt unter den Matrizen stehen drei sichtbare Abschnitte, ohne aufklappbaren Bereich:

| Abschnitt | Bedienelemente und Hilfstext |
| --- | --- |
| Berechnung | **In linearem Licht berechnen**. Wandelt sRGB vor der Matrixberechnung in lineares Licht und anschließend wieder zurück; passend zur verwendeten Matrix wählen. |
| Bildanpassung | **Helligkeit (Faktor)**, **Kontrast (Faktor)**, neutral **1**. Vorerst Zahlenfelder ohne Regler; gemeinsame sRGB-Anpassung um die mittlere Helligkeit beider Halbbilder. Zurücksetzen übernimmt alle Einstellungen der Vorlage. Gemeinsame Anpassung beider Halbbilder vor der Matrixrechnung. |
| Farbkanäle | **Farbkanäle korrigieren** mit **Rot**, **Grün**, **Blau**, neutral jeweils **1,0**, Anfangsbereich **0,625 bis 1,25** aus den Batch-Potenzen, Schritt **0,001**; Zahleneingabe kann ihn erweitern. Kleinere Werte als 1 hellen auf, größere dunkeln ab. |

Die RGB-Korrektur ist eine Potenz auf den normierten Ausgabekanälen nach der Zusammenführung und gegebenenfalls der Rückwandlung nach sRGB. Die bekannte Rotkorrektur entspricht **Rot 0,75 / Grün 1,0 / Blau 1,0**. Es werden keine Korrekturwerte automatisch aus Rot/Cyan, Grün/Magenta oder Amber/Blau abgeleitet. Bei ausgeschalteter Korrektur bleiben die gespeicherten RGB-Werte sichtbar und ausgegraut. Gültige Potenzwerte müssen positiv und endlich sein.

Clipping und Operationsreihenfolge werden für eigene Verfahren intern eindeutig und versioniert festgelegt; sie erhalten keine zusätzlichen Bedienelemente. Die konkrete Rechenfolge und Formeln sind in [PRESET_EDITOR.md](PRESET_EDITOR.md) festgehalten. Farbsättigung, frei zusammengestellte Operationsketten und zusätzliche Lab-Regler sind nicht Teil des vereinfachten Editors.

Die eingebauten 18 Verfahren bleiben unveränderliche Referenzen mit ihrer vollständigen Speziallogik. Als Vorlage kopierte Verfahren müssen im vereinfachten Schema vollständig darstellbar sein. Rendepth mit zusätzlicher Grünkorrektur kann entsprechend abgebildet werden; die getrennten iaian7-Halbbildpotenzen und dessen Abschlussmatrix können hier nicht stillschweigend entfallen. CIELab wird nicht als frei bearbeitbare Matrixvorlage angeboten. Eine nicht vollständig darstellbare Vorlage wird ausdrücklich als solche behandelt, ohne versteckte Verarbeitungsschritte in ein scheinbar einfaches Preset einzubauen.

Eigene Presets werden mit Name, stabilem eindeutigen Bezeichner, Dateinamenssuffix, beiden Matrizen, Linearisierung und allen Bild-/Kanalwerten in **`presets.json`** gespeichert. Suffixe werden für Dateipfade validiert und dürfen keine eingebauten Verfahren oder anderen eigenen Presets unbeabsichtigt überschreiben. Die Datei wird sicher ersetzt, wie die Einstellungsdatei; Nutzerdaten gehören nicht in Git.

Editoränderungen sind zunächst ein Entwurf mit laufender Vorschau. **Speichern** validiert und übernimmt das gesamte Verfahren; **Abbrechen** stellt das zuvor ausgewählte Verfahren wieder her. Eingebaute Verfahren werden durch solche Entwürfe nicht überschrieben.

## Ghosting und weitere Bildanpassungen

Die [offizielle SPM-Hilfe](https://stereo.jpn.org/eng/stphmkr/help/stereo_14.htm) beschreibt zur Ghosting-Verminderung zuerst Lab-Helligkeit/-Kontrast und danach RGB-Helligkeit/-Kontrast. Sie weist auf die Abhängigkeit von Brille und Wiedergabemedium sowie mögliches erneut auftretendes Ghosting hin. Diese Beschreibung liefert keine vollständige Rechenvorschrift für eine identische Nachimplementierung.

AnaChromas allgemeine Helligkeits-/Kontrastanpassung ist deshalb kein zugesagter Algorithmus zur Ghosting-Kompensation. Ein eigener Bereich **Geisterbilder reduzieren** wird erst nach Prüfung eines konkreten Verfahrens mit realen Bildern und Betrachtungsbedingungen aufgenommen. Die [SPM-Matrixhilfe](https://stereo.jpn.org/eng/stphmkr/help/stereo_13.htm) bestätigt dagegen direkt den Ansatz gespeicherter eigener RGB-Mischungen.

## Ausgabegrößen und JPEG

Alle Größen beziehen sich auf die fertige Anaglyphe, nicht auf das gesamte SBS.

| Option | Bedeutung |
| --- | --- |
| Original | Größe eines orientierten SBS-Halbbildes |
| 1080p | Seitenverhältnis erhalten, eingepasst in 1920 × 1080 px |
| 2160p | Seitenverhältnis erhalten, eingepasst in 3840 × 2160 px |
| 2048 lange Seite | Lange Seite auf 2048 px |
| Benutzerdefiniert | Lange oder kurze Seite mit einem positiven Pixelwert; Anfangswert 2048 px |

Lange/kurze Seite sind gegenseitig ausschließende Optionen. Keine freie Breite/Höhe und keine Verzerrung. Die Berechnung erlaubt wie die Batch Vergrößerung; die Seiten werden auf den nächsten ganzen Pixel gerundet (mindestens 1). Die Engine ist keine reine Verkleinerungsfunktion.

Pillow schreibt JPEG mit **`quality=90`, `subsampling=0`, `optimize=True`**. Die Checkbox **JPEG-Qualität 95 für Druck/Archiv** ändert ausschließlich `quality` auf 95. 90 bleibt der hochwertige Standard. Lanczos betrifft die Skalierung, `optimize=True` die JPEG-Codierung.

Dateinamenssuffixe und Ordnerabbildung folgen der aktuellen Batch. Bei Ordner-Eingabe enthält deren Ausgabe auch den Namen des gewählten Quellordners, z. B. `Urlaub/Tag1/bild001.jpg` → `output/Urlaub/Tag1/bild001_dubois_lcd.jpg`.

Standard ist `output` im Programm-/Quellordner wie in der Batch; bei schreibgeschütztem Programmordner im Benutzer-Konfigurationsordner. Ein gespeicherter eigener Ausgabeordner bleibt erhalten, auch beim Wechsel der Eingabe.

Die bestehende Tool-Familie ersetzt fertige Dateien mit gleichem Zielnamen. Bei der Umsetzung werden Namenskollisionen verschiedener Quellen mit gleichem Stammnamen ausdrücklich behandelt. Fertige Dateien werden zunächst temporär vollständig geschrieben und erst danach am Ziel ersetzt.

## ExifTool und Metadaten

Metadaten werden standardmäßig übernommen; eine zusätzliche Checkbox ist nicht vorgesehen. Ausgangspunkt ist die Praxis der vorhandenen Tools:

`-overwrite_original -TagsFromFile <input> --Preview:all --Orientation <output>`

Die implementierte Befehlszeile ist mit einem tatsächlichen ExifTool-Export geprüft. Eingebettete Originalvorschauen/Thumbnails sowie bereits angewendete Orientation dürfen nicht übernommen werden. StereoFine schließt zusätzlich `--MPF:all` aus. ExifTool wird aus dem gebündelten `tools`-Ordner bzw. bei Quellcodeausführung aus einer passenden lokalen Installation gefunden.

Ein Metadatenfehler lässt eine erfolgreich geschriebene Anaglyphe bestehen und erzeugt eine nachvollziehbare Warnung. Unter Windows soll kein zusätzliches Konsolenfenster aufblitzen. Prozesse benötigen geregelte Zeitlimits und Abbruchbehandlung.

## CIELab

CIELab bleibt eine externe Berechnung und wird nicht in Python nachgebaut. Windows-Pfad: `tools/cielab/cielab.exe` mit den benötigten Begleitdateien.

Referenzablauf:

1. Orientiertes SBS teilen.
2. Beide Halbbilder auf die gewählte Zielgröße skalieren.
3. Separate PNGs in einem eigenen temporären Arbeitsverzeichnis schreiben.
4. CIELab mit linkem und rechtem Bild sowie `-o <output.png>` starten.
5. Ergebnis mit Pillow als JPEG speichern und Metadaten übernehmen.
6. Temporäre Dateien aufräumen.

Für Vorschauen ist die Zielgröße auf 1024 px lange Seite begrenzt. Abbruch muss auch laufende externe Prozesse sauber beenden können.

Neue Windows-, Linux- und macOS-Binaries können aus dem vorhandenen Upstream-Code gebaut werden. Dessen ältere OpenCV- und levmar-Abhängigkeiten sind gesondert zu prüfen. Erfolgreich getestete neue Binaries können anschließend auch AnaglyphBatch aktualisieren; Änderungen an diesem separaten Repository sind kein Bestandteil des ersten AnaChroma-Stands.

## Fortschritt, Abbruch und Fehler

- Worker-Threads für Vorschau und Verarbeitung.
- GUI-Änderungen ausschließlich im GUI-Thread, über Nachrichtenqueue und `after()`.
- Job-Kennungen verhindern die Anzeige veralteter Ergebnisse.
- Gesamtfortschritt, Datei x/y, Dateiname und konkrete Verarbeitungsschritte.
- Buttons: **Aktuelles Bild speichern**, **Alle verarbeiten**, **Abbrechen**.
- Beispielstatus: **Berechne Anaglyphe...**, **Speichere JPEG...**, **Übernehme Metadaten...**
- Abbruchprüfung zwischen Arbeitsschritten und während längerer Berechnungen.
- Einzelne Dateifehler sollen den übrigen Ordnerauftrag nicht unnötig beenden.
- Kurzer Abschluss mit getrennten Erfolgen und Fehlern, z. B. **Fertig. 83 Bilder verarbeitet, 2 Fehler.**
- Nach Abschluss, Abbruch oder Fehler die Bedienelemente und ihre Abhängigkeiten zuverlässig wiederherstellen.

## Oberfläche und Einstellungen

Links die Bereiche Eingabe, Ausgabe, Anaglyphe/Größe und Verarbeitung; rechts Bildname/Zähler, große Vorschau und Navigation. Fortschrittsbalken und Status orientieren sich an SplatTricia.

Gemeinsame Farben: Hintergrund `#111111`, weiche Fläche `#181818`, Panels `#202020`, Hover `#282828`, Rahmen `#333333`, Text `#f2f2f2`, gedämpft `#b8b8b8`, deaktiviert `#727272`, Gold `#9c7c38`, helles Gold `#c6a95e`, Vorschau schwarz. Die vollständigen Gestaltungsregeln bleiben im verlinkten SplatTricia-Designstandard nachvollziehbar.

Persistenz in einer kleinen JSON-Datei: letzter Eingabeordner, letzter Ausgabeordner und Unterordneroption. Matrix, Größe und JPEG-95 bleiben zunächst bewusst gesetzte Sitzungsoptionen; weitergehende Persistenz erfordert eine transparente Entscheidung.

Das bereitgestellte Icon ist eingebunden; die unveränderte `ready.wav` ist für den üblichen Abschlusssound vorgesehen. Plattformabhängige Soundwiedergabe darf kein zusätzliches Pflichtpaket ohne konkreten Bedarf erzeugen. Der erste Entwicklungsstand hat eine deutsche GUI; die öffentlichen READMEs liegen in beiden Sprachen vor. Eine GUI-Sprachumschaltung ist noch nicht implementiert.

## Bewusste Nicht-Ziele

Keine Stereojustage, Links/Rechts-Paarerkennung, MPO-Aufteilung, Scheinfensterkorrektur, Deviation-/Tiefenanalyse, Tiefenkarten, 2D-zu-3D-Konvertierung, Thumbnail-Galerie, komplexes ICC-Farbmanagement, PNG-16/TIFF-16-Ausgabe oder Videoverarbeitung. Kein FFmpeg als Standardengine, keine Cloud-, Account- oder Web-Funktionen. Der vereinfachte Editor für eigene Matrixverfahren ist inzwischen ausdrücklich Teil von v1; eine gesonderte Ghosting-Kompensation bleibt eine Prüffrage.

Alpha wird verworfen und RGB verwendet; keine zusätzliche Alpha-Mischung. Ungerade orientierte SBS-Breite wird mit **Bildbreite ist nicht gerade – SBS kann nicht sauber geteilt werden.** abgelehnt, ohne Pixel abzuschneiden. Für v1 wird sRGB vorausgesetzt. Der Export erhält ein erzeugtes sRGB-Profil. Alte ICC-Profile, ColorSpace, Orientation, MPF und eingebettete Vorschauen werden beim Metadatenkopieren ausgeschlossen; EXIF-Bildmaße und sRGB-ColorSpace werden für die fertige Datei gesetzt.

Für TransCora separat vormerken: Bei Anaglyph-Video 4:4:4 ernst nehmen, eingeschränkte Browser-/Hardware-Kompatibilität berücksichtigen und höhere Farbtiefe nur bei nachgewiesenem Workflow-Nutzen ergänzen.

## Entwicklungsfolge

1. Aktuelle Referenzen und Projektstruktur dokumentieren.
2. Bestehendes sRGB-Modul übernehmen und Verfahren samt Modi übertragen.
3. Kleine reine Engine zunächst für Dubois LCD und Compromise aufbauen.
4. Verlustfreie Zwischenbilder und reale SBS-Ergebnisse gegen die Batch vergleichen; JPEG-Codierung getrennt beurteilen.
5. GUI mit Dateiladen, automatischer Vorschau, Verfahrensauswahl und dem vereinfachten Preset-Editor mit Regler-/Mausradbedienung bauen.
6. Navigation, Größenwahl und Einzelbildexport ergänzen.
7. Ordnerauftrag, Unterordnerabbildung, Metadaten, Fortschritt und Abbruch ergänzen.
8. Externe CIELab-Verarbeitung und Plattform-Builds prüfen.
9. Oberfläche mit echten Bildern prüfen und Release-Builds vorbereiten.

Kleine robuste Schritte, verbindliche Matrixwerte, keine stillen Funktionsänderungen und keine unnötigen Abhängigkeiten. Das Repository bleibt die nachvollziehbare Quelle für Dokumentation, Code und spätere Releases.
