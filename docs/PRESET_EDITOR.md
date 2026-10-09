# AnaChroma – Eigene Anaglyphenverfahren

Der Menüpunkt **Eigenes Verfahren anlegen…** öffnet zwei 3×3-Matrizen mit Zahlenfeldern und Reglern; die große Hauptvorschau zeigt den Entwurf. Als Ausgangspunkt dient das gewählte Verfahren. Eigene Verfahren erscheinen anschließend in derselben Auswahlliste; **Bearbeiten…** öffnet sie erneut.

## Matrixwerte verstehen und übernehmen

Die **Spalten** sind die Eingangsfarben Rot/Grün/Blau des jeweiligen Halbbilds, die **Zeilen** die ausgegebenen Farben. Beispiel: Zeile „Ausgabe Rot“, Spalte „Eingang Grün“ bestimmt den Beitrag des grünen Eingangskanals zum roten Ausgabekanal. Je eine Matrix gehört zum linken und rechten Auge.

`0` bedeutet keinen Beitrag, `1` den unveränderten Beitrag. Negative Werte dienen unter anderem zur Farbkorrektur; Gewichte über 1 kommen in etablierten Anaglyphenmatrizen vor. Eine Zeilensumme von 1 wird nicht erzwungen.

Die Felder zeigen **direkte Koeffizienten**, keine Prozentwerte. `0.4561` bzw. `0,4561` kann direkt eingetippt werden. Veröffentlichungen verwenden unterschiedliche Orientierungen: Bei einer transponierten Matrix müssen Zeilen und Spalten vor der Eingabe getauscht werden. Auch Augenreihenfolge und vorausgesetzter Farbraum gehören zur Rechenanleitung der Quelle.

| Einstellung | Neutralwert / Startbereich | Schritt und Grundlage |
| --- | --- | --- |
| Matrixkoeffizienten | 0 = kein Beitrag, 1 = voller Beitrag; Regler −2 bis +2 | 0,001 beim Ziehen/Mausrad, entsprechend SPMs Tausendstel-Darstellung. Endpunkte als praktische Kanalgewichtung wie Photoshop −200 % bis +200 %, keine physikalische Grenze. |
| Rot/Grün/Blau, Kanalpotenz | Neutral 1; Regler 0,625 bis 1,25 | 0,001; umfasst die im vereinfachten Editor darstellbaren Potenzen der Batch. |

Direkte Eingaben außerhalb des Anfangsbereichs erweitern den jeweiligen Regler sichtbar. Feinere Zahlen werden gespeichert; Reglerbewegungen runden ausschließlich den veränderten Wert auf dessen Schrittweite. Technische Grenzen verhindern Float32-Überlauf bzw. nicht darstellbare Kanalpotenzen; sie sind keine sinnvollen fotografischen Einstellbereiche. NaN, Unendlich und unvollständige Eingaben sind ungültig.

Das Mausrad verändert nur das fokussierte Zahlenfeld bzw. den ausgewählten Regler. Es blättert dann weder Bilder weiter noch scrollt es zugleich den Dialog. Ungültige Eingaben bekommen einen roten Rahmen; Speichern bleibt gesperrt und die Vorschau zeigt den letzten gültigen Entwurf.

## Linearisierung und Farbkanäle

**In linearem Licht berechnen** decodiert sRGB vor der Matrixrechnung und codiert das Ergebnis danach wieder nach sRGB. Dies entsprechend der Matrixquelle auswählen. Beispielsweise benötigen die Dubois-Vorlagen diesen Schritt; eine beliebige sRGB-Matrix wird durch Einschalten nicht automatisch besser.

**Farbkorrektur** wendet nach der Farbmischung auf die normierten sRGB-Kanäle `x` jeweils `x^p` an. `p=1` verändert nichts, `p<1` hellt Zwischenwerte auf, `p>1` dunkelt sie ab. Die bekannte Rotkorrektur lautet **Rot 0,75; Grün/Blau 1**. Der Editor bietet alle drei Farben, leitet jedoch keine passenden Werte allein aus der Brillenfarbkombination ab. Ausgeschaltete Korrektur erhält die gespeicherten Werte, wendet sie aber nicht an.

## Versionierte Rechenfolge

Preset-Schema **1** beschreibt diese feste Reihenfolge:

1. Beide Ansichten nach sRGB-RGB mit Werten von 0 bis 1 laden.
2. Optional sRGB linearisieren.
3. Linke/rechte Matrix anwenden und jeden Beitrag separat auf 0 bis 1 begrenzen; Beiträge addieren und erneut begrenzen.
4. Bei linearer Berechnung wieder nach sRGB wandeln.
5. Optionale R/G/B-Potenzen anwenden und nach 8-Bit RGB runden.

Vorschau und Export verwenden dieselbe Engine. Die Vorschau verkleinert die Halbbilder passend zur Fensterfläche auf höchstens 1600 px (CIELab: 1024 px); der normale Export berechnet die volle Auflösung und skaliert danach. Clipping und nichtlineare Operationen können daher kleine Unterschiede zur verkleinerten Vorschau verursachen.

## Vorlagen und Speicherung

Die 18 eingebauten Verfahren behalten ihre Rechenfolge. 14 lassen sich vollständig als Vorlagen aus zwei Matrizen, optionaler Linearisierung und RGB-Potenzen darstellen. Rendepth 1/2, iaian7 und CIELab haben zusätzliche bzw. externe Rechenschritte und werden nicht als vereinfachte Vorlagen angeboten. Bei diesen Ausgangspunkten beginnt der Editor mit Color.

**Zurücksetzen** stellt sämtliche Rechenwerte der übernommenen Vorlage wieder her. Name und Suffix bleiben beim Zurücksetzen erhalten. Der Wechsel zu einer anderen Vorlage aktualisiert auch den Namens- und Suffixvorschlag; vorhandene eigene Verfahren werden bei der Vorschlagsbildung berücksichtigt. **Verfahren speichern** validiert und speichert den Entwurf; **Abbrechen** stellt das zuvor gewählte Verfahren wieder her.

`presets.json` speichert Schema, stabile Kennung, Name, Suffix, beide Matrizen, Farbraum, Potenzen. Name/Suffix müssen unter eigenen Presets eindeutig sein; eingebaute Suffixe sind reserviert. Eine beschädigte oder unbekannte Preset-Datei wird gemeldet und nicht überschrieben. Nutzerdateien gehören nicht ins Repository.

Ältere Entwicklungs-Presets mit nichtneutraler Helligkeit/Kontrast werden beim Start namentlich gemeldet. Version 1.0 übernimmt ihre Matrizen und RGB-Potenzen, wendet die entfernten Anpassungen jedoch nicht mehr an. Beim ersten Speichern wird die ursprüngliche Datei bytegetreu als `presets.json.pre-1.0.bak` gesichert. Vorhandene Sicherungen werden nicht überschrieben.

Die Quellen und der Bezug zur Anaglyphenverarbeitung stehen in [REFERENCE_BASELINE.md](REFERENCE_BASELINE.md#regler-und-referenzprogramme).
