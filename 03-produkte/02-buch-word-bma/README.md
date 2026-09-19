# Moodle-Buch: «Deine BMA in Word»

## Inhalt

Dieses Paket enthält ein schlicht gestaltetes Moodle-Buch für Lernende der BMS Natur, Landschaft, Lebensmittel. Es vermittelt die technische Umsetzung der Berufsmaturitätsarbeit (BMA) mit der verbindlichen Word-Vorlage.

- Thema: Formatvorlagen, Gliederung, Abbildungen/Tabellen, automatische Verzeichnisse, Kopf-/Fusszeilen, Fussnoten, Quellen und Schlusskontrolle.
- Lernziele: Die Lernenden können die BMA-Vorlage technisch korrekt nutzen und eine formale Schlusskontrolle durchführen.
- Umfang: 13 HTML-Dateien als 7 Hauptkapitel mit je einem Unterkapitel (ausser der Einleitung).
- Sprache: Deutsch (Schweiz).

## Dateien und Import in Moodle 5.0.4

- `moodle-buch-bma-word.mbz`: Moodle-Aktivitätsbackup mit einem Buch und allen 13 Kapiteln. Im Zielkurs **Mehr → Wiederherstellen** wählen und als Aktivität in einen bestehenden Kurs einfügen.
- `moodle-buch-bma-word-html-import.zip`: HTML-Alternative für den nativen Kapitelimport.

### HTML-Alternative

1. Im gewünschten Kurs eine Ressource **Buch** anlegen und speichern.
2. Im Buch-Menü **Mehr → Kapitel importieren** wählen.
3. Die Datei `moodle-buch-bma-word-html-import.zip` hochladen.
4. Bei der Auswahl festlegen, dass jede HTML-Datei ein Kapitel bildet, und den Import starten.

Moodle sortiert die Kapitel alphabetisch. Die Nummerierung im Dateinamen bildet deshalb die gewünschte Reihenfolge ab. Dateien mit dem Suffix `_sub.html` werden als Unterkapitel importiert. Moodle-Bücher unterstützen genau zwei Navigationsebenen.

## Verwendete Grundlagen

- `01-kontextwissen/BMA-Word-Workshop.pdf` (Word-Workshop, 2018): technische Arbeitsschritte zu Seitenlayout, Formatvorlagen, Überschriften, Abbildungen, Tabellen, Verzeichnissen, Fussnoten, Abschnittsumbrüchen und Datensicherheit.
- `01-kontextwissen/260709 - A2-200 Wegleitung BMA mit Bewertungsraster_rot.pdf`: aktuelle formale BMA-Vorgaben, insbesondere Kapitel 3, 5 und 8.7.
- `01-kontextwissen/BMA_Vorlage_Schriftliche_Arbeit.docx`: aktuelle, verbindliche Word-Vorlage und die darin hinterlegten Hinweise.

Die verwendeten YouTube-Links führen zu deutschsprachigen Tutorials für Formatvorlagen, Inhalts-/Abbildungsverzeichnisse und Abschnittsumbrüche. Sie sind als Ergänzung vorgesehen und nicht als Ersatz für die Strickhof-Vorlage oder die BMA-Wegleitung.

## Technische Prüfung

Das Zip enthält ausschliesslich die HTML-Kapitel auf der obersten Ebene. Es ist für den nativen Kapitelimport des Moodle-Buch-Moduls vorbereitet.
