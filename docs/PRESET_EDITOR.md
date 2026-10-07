# AnaChroma – Eigene Anaglyphenverfahren

Der sichtbare Button **Eigenes Verfahren anlegen…** öffnet zwei 3×3-Matrizen mit Zahlenfeldern, Reglern und einer Live-Vorschau. Als Ausgangspunkt dient das gewählte Verfahren. Eigene Verfahren erscheinen anschließend in derselben Auswahlliste; **Bearbeiten…** öffnet sie erneut.

## Matrixwerte verstehen und übernehmen

Die **Spalten** sind die Eingangsfarben Rot/Grün/Blau des jeweiligen Halbbilds, die **Zeilen** die ausgegebenen Farben. Beispiel: Zeile „Ausgabe Rot“, Spalte „Eingang Grün“ bestimmt den Beitrag des grünen Eingangskanals zum roten Ausgabekanal. Je eine Matrix gehört zum linken und rechten Auge.

`0` bedeutet keinen Beitrag, `1` den unveränderten Beitrag. Negative Werte dienen unter anderem zur Farbkorrektur; Gewichte über 1 kommen in etablierten Anaglyphenmatrizen vor. Eine Zeilensumme von 1 wird nicht erzwungen.

Die Felder zeigen **direkte Koeffizienten**, keine Prozentwerte. `0.4561` bzw. `0,4561` kann direkt eingetippt werden. Veröffentlichungen verwenden unterschiedliche Orientierungen: Bei einer transponierten Matrix müssen Zeilen und Spalten vor der Eingabe getauscht werden. Auch Augenreihenfolge und vorausgesetzter Farbraum gehören zur Rechenanleitung der Quelle.

| Einstellung | Neutralwert / Startbereich | Schritt und Grundlage |
| --- | --- | --- |
| Matrixkoeffizienten | 0 = kein Beitrag, 1 = voller Beitrag; Regler −2 bis +2 | 0,001 beim Ziehen/Mausrad, entsprechend SPMs Tausendstel-Darstellung. Endpunkte als praktische Kanalgewichtung wie Photoshop −200 % bis +200 %, keine physikalische Grenze. |
| Rot/Grün/Blau, Kanalpotenz | Neutral 1; Regler 0,625 bis 1,25 | 0,001; umfasst die im vereinfachten Editor darstellbaren Potenzen der Batch. |
| Helligkeit (Faktor) | Neutral 1; endliche Werte ab 0 | Zahlenfeld, kein ungeprüfter Reglerbereich; fokussiertes Mausrad 0,001. |
| Kontrast (Faktor) | Neutral 1; endliche Werte ab 0 | Zahlenfeld, kein ungeprüfter Reglerbereich; fokussiertes Mausrad 0,001. |

Direkte Eingaben außerhalb des Anfangsbereichs erweitern den jeweiligen Regler sichtbar. Feinere Zahlen werden gespeichert; Reglerbewegungen runden ausschließlich den veränderten Wert auf Tausendstel. Technische Grenzen verhindern Float32-Überlauf bzw. nicht darstellbare Kanalpotenzen; sie sind keine sinnvollen fotografischen Einstellbereiche. NaN, Unendlich und unvollständige Eingaben sind ungültig.

Das Mausrad verändert nur das fokussierte Zahlenfeld bzw. den ausgewählten Regler. Es blättert dann weder Bilder weiter noch scrollt es zugleich den Dialog. Ungültige Eingaben bekommen einen roten Rahmen; Speichern bleibt gesperrt und die Vorschau zeigt den letzten gültigen Entwurf.

## Linearisierung und Farbkanäle

**In linearem Licht berechnen** decodiert sRGB vor der Matrixrechnung und codiert das Ergebnis danach wieder nach sRGB. Dies entsprechend der Matrixquelle auswählen. Beispielsweise benötigen die Dubois-Vorlagen diesen Schritt; eine beliebige sRGB-Matrix wird durch Einschalten nicht automatisch besser.

**Farbkanäle korrigieren (Kanalpotenzen)** wendet nach der Farbmischung auf die normierten sRGB-Kanäle `x` jeweils `x^p` an. `p=1` verändert nichts, `p<1` hellt Zwischenwerte auf, `p>1` dunkelt sie ab. Die bekannte Rotkorrektur lautet **Rot 0,75; Grün/Blau 1**. Der Editor bietet alle drei Farben, leitet jedoch keine passenden Werte allein aus der Brillenfarbkombination ab. Ausgeschaltete Korrektur erhält die gespeicherten Werte, wendet sie aber nicht an.

## Versionierte Rechenfolge

Preset-Schema **1** beschreibt diese feste Reihenfolge:

1. Beide Ansichten nach sRGB-RGB mit Werten von 0 bis 1 laden.
2. Falls erforderlich, einen gemeinsamen Kontrastmittelpunkt bestimmen: mittlere Helligkeit beider Ansichten mit RGB-Gewichten 0,299 / 0,587 / 0,114.
3. Beide Ansichten gleich anpassen: `clip((m + (x − m) × Kontrast) × Helligkeit, 0, 1)`. Bei Kontrast 1 entfällt die Mittelwertberechnung. Diese explizite affine Formel ist AnaChromas allgemeine Bildanpassung, keine Cosima-/SPM-Ghosting-Kalibrierung.
4. Optional sRGB linearisieren.
5. Linke/rechte Matrix anwenden und **jeden Beitrag separat** auf 0 bis 1 begrenzen, wie in der Batch-Pipeline. Beiträge addieren und erneut begrenzen.
6. Bei linearer Berechnung wieder nach sRGB wandeln.
7. Optionale R/G/B-Potenzen anwenden und nach 8-Bit RGB runden.

Vorschau und Export verwenden dieselbe Engine. Die Vorschau verkleinert die Halbbilder zuvor auf höchstens 1024 px; der normale Export berechnet die volle Auflösung und skaliert danach. Clipping und nichtlineare Operationen können daher kleine Unterschiede zur verkleinerten Vorschau verursachen. Bei verändertem Kontrast kann auch der aus der jeweiligen Auflösung bestimmte Mittelwert leicht abweichen.

## Vorlagen und Speicherung

Die 18 eingebauten Verfahren bleiben unverändert. 16 sind vollständig als einfache Matrixvorlagen darstellbar, einschließlich Rendepth mit Rot-/Grünpotenz. **iaian7** hat getrennte Augenpotenzen und eine zusätzliche Abschlussmatrix; **CIELab** ist ein externer Optimierer. Diese beiden werden nicht als vereinfachte Vorlagen angeboten. Bei diesem Ausgangspunkt weist die GUI darauf hin und beginnt mit Color.

**Auf Vorlage zurücksetzen** stellt sämtliche Rechenwerte der übernommenen Vorlage wieder her. Name und Suffix bleiben erhalten. **Verfahren speichern** validiert und speichert den Entwurf; **Abbrechen** stellt das zuvor gewählte Verfahren wieder her.

`presets.json` speichert Schema, stabile Kennung, Name, Suffix, beide Matrizen, Farbraum, Potenzen und Faktoren. Name/Suffix müssen unter eigenen Presets eindeutig sein; eingebaute Suffixe sind reserviert. Eine beschädigte oder unbekannte Preset-Datei wird gemeldet und nicht überschrieben. Nutzerdateien gehören nicht ins Repository.

Die Quellen und der Bezug zur Anaglyphenverarbeitung stehen in [REFERENCE_BASELINE.md](REFERENCE_BASELINE.md#regler-und-referenzprogramme).
