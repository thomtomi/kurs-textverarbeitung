# reveal.js-Präsentation: Textverarbeitung für die BMA

Eine lernendenorientierte Einführung von rund 20 Minuten. Die Präsentation
deckt Textverarbeitung, Struktur und Formatierung, Werkzeugwahl,
verantwortungsvollen KI-Einsatz, Unterstützung und weiterführende Links ab.

## Dateien

- `textverarbeitung-bma.md`: die vollständige Präsentation als reveal.js-Markdown,
  inklusive Moderationsnotizen.
- `index.html`: Startdatei mit dem Theme **solarized**.
- `reveal.js/`: lokal mitgelieferte Reveal.js-Dateien. Die Präsentation braucht
  nach dem Upload in Moodle keine externe CDN-Verbindung.
- `textverarbeitung-bma-revealjs-moodle.zip`: uploadfertiges Paket für Moodle.

## Präsentieren

Für eine lokale Vorschau wird die Markdown-Datei über einen lokalen Webserver
geladen. Im Präsentationsordner ausführen:

```bash
python3 -m http.server 8000
```

Danach im Browser `http://localhost:8000` öffnen. Navigieren mit Pfeiltasten
oder Leertaste; mit `S` öffnen sich die Moderationsnotizen in einem zweiten
Fenster.

Für ein dunkles Erscheinungsbild in `index.html` `solarized.css` durch
`moon.css` ersetzen.

## Upload in Moodle

1. Im Kurs eine Aktivität oder Ressource **Datei** anlegen.
2. `textverarbeitung-bma-revealjs-moodle.zip` hochladen.
3. Die ZIP-Datei in Moodle entpacken und `index.html` als Hauptdatei wählen.
4. Speichern. Moodle öffnet beim Aufruf direkt die Präsentation.

Die Präsentation kann bei Bedarf in einem Textfeld per `iframe` eingebettet
werden. Dafür die URL der hochgeladenen Ressource mit `/index.html#/` als
`src` verwenden.

## Inhaltliche Grundlage

- BMA-Wegleitung, insbesondere wissenschaftliche Arbeitsweise,
  Quellenarbeit, Deklaration und KI-Einsatz.
- Richtlinie A2-322 «KI-Einsatz im Unterricht», insbesondere Datenschutz,
  Sicherheit und Kennzeichnung.
- Die Moodle-Bücher zu Word, LibreOffice Writer, LaTeX und KI für die BMA.
