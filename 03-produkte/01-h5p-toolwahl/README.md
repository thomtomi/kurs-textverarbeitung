# H5P Personality Quiz: Welches Textverarbeitungs-Tool passt zu dir?

## Importanleitung für Moodle 5.0.4

### Voraussetzungen

- Sie haben im Kurs das Recht, H5P-Inhalte anzulegen.

### Schritt 1: Datei vorbereiten

Die Datei `01-h5p-toolwahl.h5p` ist ein direkt importierbares H5P-Paket. Sie benötigen keine weitere Vorbereitung.

Die Datei enthält die H5P-Pflichtangabe `embedTypes`, die vollständigen Metadaten und die benötigte Hauptbibliothek `H5P.PersonalityQuiz 1.0`. Alle optionalen Bildfelder liegen als leere Objekte vor (nicht als `null`); dies verhindert einen Fehler des Personality-Quiz-Editors beim Bearbeiten.

### Schritt 2: Import in Moodle

1. Navigieren Sie in Ihrem Moodle-Kurs zu dem Thema/Abschnitt, in dem Sie die Aktivität hinzufügen möchten.
2. Klicken Sie auf "Material oder Aktivität hinzufügen".
3. Wählen Sie "H5P Content" (oder "Interactive Content" je nach Moodle-Sprache).
4. Füllen Sie die Grundinformationen aus:
   - **Name**: "Welches Textverarbeitungs-Tool passt zu mir?"
   - **Beschreibung**: Optional – z.B. "Ein Quiz, das dir hilft herauszufinden, welches Tool am besten zu deinen Anforderungen passt."
5. Laden Sie die Datei `01-h5p-toolwahl.h5p` hoch (Bereich "H5P Content File" oder ähnlich).
6. Speichern Sie die Aktivität.

### Schritt 3: Testen

Öffnen Sie die Aktivität als Student (oder im Gast-Modus) und führen Sie das Quiz durch, um das Ergebnis zu überprüfen.

## Inhaltliche Beschreibung

### Ziel

Lernende erhalten basierend auf ihren Antworten eine Empfehlung für eines der drei Textverarbeitungs-Tools:

- **MS Word**: Am weitesten verbreitet, einsteigerfreundlich, Cloud-Funktionen.
- **LibreOffice Writer**: Kostenlos, quelloffen, vergleichbar mit Word.
- **LaTeX**: Spezialisiert auf naturwissenschaftliche Arbeiten, professionelle Typografie, technisch anspruchsvoll.

### Fragenkatalog

Das Quiz umfasst 10 Fragen, die folgende Aspekte abdecken:

1. Erfahrung mit Textverarbeitungsprogrammen
2. Präferenz für kostenlose vs. kommerzielle Software
3. Bedarf an mathematischen/naturwissenschaftlichen Formeln
4. Anforderungen an Layoutqualität
5. Bedarf an Echtzeit-Zusammenarbeit
6. Bereitschaft zum Erlernen neuer Tools
7. Verfügbarkeit von Software auf dem Gerät
8. Bevorzugter Umgang mit Formatierung (grafisch vs. Code-basiert)
9. Geplante Grösse und Struktur der Maturaarbeit
10. Neugier auf neue Technologien

### Bewertung

Die Antworten sind mit den drei Persönlichkeitstypen verknüpft. Das Tool mit den meisten Übereinstimmungen wird am Ende angezeigt.

### Anwendungskontext (Thema 5 der Agenten-Instruction)

Diese Aktivität adressiert das Thema **"Word vs. LibreOffice vs. LaTeX – Entscheidungshilfe"** und bietet Lernenden eine strukturierte, interaktive Entscheidungshilfe. Sie können die Ergebnisse als Ausgangspunkt für Gruppendebatten oder für die Wahl weiterer spezifischer Lernaktivitäten (Formatvorlagen für Word, LaTeX-Syntax, Zusammenarbeit, etc.) nutzen.

## Quellen (Fact-Checking)

- [Agenten-Instruction Abschnitt 8](../../00-setup/agenten_instruction.md#8-entscheidungshilfe-word--libreoffice--latex): Kriterienraster Word/LibreOffice/LaTeX
- [Rahmenlehrplan BM (Kontext)](../../01-kontextwissen/2026_Rahmenlehrplan_BM_vollstaendig.md)
- Allgemein bekannte Eigenschaften der drei Textverarbeitungstools

## Hinweise für Betreuer/Lehrkräfte

- Dieses Quiz ist niedrigschwellig und kann in der Orientierungsphase der Maturaarbeit eingesetzt werden.
- Die Ergebnisse sind Empfehlungen, keine verbindlichen Vorgaben – Schüler können auch bewusst eine andere Wahl treffen.
- Zeilenbrechen Sie die Ergebnisse im Anschluss mit den Lernenden (z.B. in einer Diskussion oder einem Feedback-Gespräch).
- Weitere spezialisierte Lernaktivitäten zu Formatvorlagen, Zitieren, LaTeX-Syntax etc. können an die Ergebnisse dieses Quiz angeknüpft werden.

## Technische Informationen

- **Format**: H5P (ZIP-Paket)
- **Content-Type**: H5P.PersonalityQuiz 1.0
- **Moodle-Kompatibilität**: 5.0.4+
- **Sprache**: Deutsch (Schweizer Rechtschreibung)

## Version

- **Version 1.2** — September 2026
- **Erstellt für**: Berufsmaturitätsschule Strickhof, Ausrichtung NLL

---

**Fragen oder Anpassungen?** Wenden Sie sich an die Kursverantwortlichen oder nutzen Sie die Agenten-Instruction, um weitere oder spezialisierte Aktivitäten zu erstellen.
