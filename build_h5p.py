#!/usr/bin/env python3
"""Erstellt und prüft das H5P-Paket «Toolwahl».

Die Prüfung deckt die Pflichtfelder der Paketdefinition ab. Damit wird ein
unvollständiges h5p.json (insbesondere ohne ``embedTypes``) nicht erneut
verpackt.
"""

import json
import sys
import zipfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent / "03-produkte" / "01-h5p-toolwahl"
H5P_FILE = BASE_DIR / "01-h5p-toolwahl.h5p"
H5P_JSON = BASE_DIR / "h5p.json"
CONTENT_JSON = BASE_DIR / "content.json"
LIBRARY_DIR = BASE_DIR / "libraries" / "H5P.PersonalityQuiz-1.0"


def load_json(path: Path) -> dict:
    """Lädt eine JSON-Datei oder beendet den Build mit einer klaren Meldung."""
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        sys.exit(f"Fehler in {path}: {error}")
    if not isinstance(data, dict):
        sys.exit(f"Fehler in {path}: Es wird ein JSON-Objekt erwartet.")
    return data


def validate_h5p_json(metadata: dict) -> None:
    """Prüft die Pflichtfelder gemäss H5P-Paketdefinition."""
    required_strings = ("title", "language", "mainLibrary")
    missing = [key for key in required_strings if not isinstance(metadata.get(key), str) or not metadata[key]]
    if missing:
        sys.exit(f"Ungültiges h5p.json: fehlende oder ungültige Pflichtfelder: {', '.join(missing)}")

    embed_types = metadata.get("embedTypes")
    if not isinstance(embed_types, list) or not embed_types or not set(embed_types).issubset({"div", "iframe"}):
        sys.exit("Ungültiges h5p.json: embedTypes muss ['div'], ['iframe'] oder beide Werte enthalten.")

    dependencies = metadata.get("preloadedDependencies")
    if not isinstance(dependencies, list) or not dependencies:
        sys.exit("Ungültiges h5p.json: preloadedDependencies muss mindestens die Hauptbibliothek enthalten.")

    main_library_found = False
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            sys.exit("Ungültiges h5p.json: Jeder Eintrag in preloadedDependencies muss ein Objekt sein.")
        valid = (
            isinstance(dependency.get("machineName"), str)
            and isinstance(dependency.get("majorVersion"), int)
            and isinstance(dependency.get("minorVersion"), int)
        )
        if not valid:
            sys.exit("Ungültiges h5p.json: Abhängigkeiten benötigen machineName, majorVersion und minorVersion.")
        if dependency["machineName"] == metadata["mainLibrary"]:
            main_library_found = True
    if not main_library_found:
        sys.exit("Ungültiges h5p.json: Die Hauptbibliothek fehlt in preloadedDependencies.")


def validate_content_json(content: dict) -> None:
    """Prüft die für den Personality Quiz benötigte Inhaltsstruktur."""
    def validate_image_group(item: dict, label: str) -> None:
        """Die Legacy-Bibliothek erwartet ein Bildgruppen-Objekt, nie null."""
        image = item.get("image")
        if not isinstance(image, dict):
            sys.exit(f"Ungültiges content.json: {label} benötigt image als Objekt ({{}}), nicht null.")
        if "file" in image and not isinstance(image["file"], dict):
            sys.exit(f"Ungültiges content.json: {label}.image.file muss fehlen oder ein Dateiobjekt sein.")

    personalities = content.get("personalities")
    questions = content.get("questions")
    if not isinstance(personalities, list) or not 2 <= len(personalities) <= 10:
        sys.exit("Ungültiges content.json: Es werden zwei bis zehn Persönlichkeiten erwartet.")
    if not isinstance(questions, list) or not questions:
        sys.exit("Ungültiges content.json: Es wird mindestens eine Frage erwartet.")

    names = set()
    for personality in personalities:
        name = personality.get("name") if isinstance(personality, dict) else None
        description = personality.get("description") if isinstance(personality, dict) else None
        if not isinstance(name, str) or not name or not isinstance(description, str) or not description:
            sys.exit("Ungültiges content.json: Jede Persönlichkeit benötigt Name und Beschreibung.")
        if name in names:
            sys.exit(f"Ungültiges content.json: Persönlichkeit {name!r} ist doppelt vorhanden.")
        validate_image_group(personality, f"Persönlichkeit {name!r}")
        names.add(name)

    for question_number, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            sys.exit(f"Ungültiges content.json: Frage {question_number} ist kein Objekt.")
        answers = question.get("answers")
        if not isinstance(question.get("text"), str) or not question["text"] or not isinstance(answers, list) or not 2 <= len(answers) <= 6:
            sys.exit(f"Ungültiges content.json: Frage {question_number} benötigt Text und zwei bis sechs Antworten.")
        validate_image_group(question, f"Frage {question_number}")
        for answer in answers:
            if not isinstance(answer, dict):
                sys.exit(f"Ungültiges content.json: Antwort in Frage {question_number} ist kein Objekt.")
            linked = answer.get("personality")
            if not isinstance(answer.get("text"), str) or not answer["text"] or not isinstance(linked, str) or not linked:
                sys.exit(f"Ungültiges content.json: Antwort in Frage {question_number} ist unvollständig.")
            validate_image_group(answer, f"Antwort in Frage {question_number}")
            unknown = {name.strip() for name in linked.split(",")} - names
            if unknown:
                sys.exit(f"Ungültiges content.json: Unbekannte Persönlichkeit in Frage {question_number}: {', '.join(sorted(unknown))}")

    title_screen = content.get("titleScreen")
    if not isinstance(title_screen, dict):
        sys.exit("Ungültiges content.json: titleScreen fehlt.")
    validate_image_group(title_screen, "titleScreen")


def validate_main_library(metadata: dict) -> None:
    """Prüft die mitgelieferte Hauptbibliothek gegen die Paketmetadaten."""
    library_json = LIBRARY_DIR / "library.json"
    required_assets = (
        library_json,
        LIBRARY_DIR / "semantics.json",
        LIBRARY_DIR / "js" / "personalityQuiz.js",
        LIBRARY_DIR / "js" / "wheelAnimation.js",
        LIBRARY_DIR / "css" / "personalityQuiz.css",
    )
    missing_assets = [str(path.relative_to(BASE_DIR)) for path in required_assets if not path.is_file()]
    if missing_assets:
        sys.exit(f"Die H5P-Hauptbibliothek ist unvollständig: {', '.join(missing_assets)}")

    library = load_json(library_json)
    for key in ("machineName", "majorVersion", "minorVersion", "embedTypes"):
        if key not in library:
            sys.exit(f"Ungültiges library.json: Pflichtfeld {key} fehlt.")
    if (
        library["machineName"] != metadata["mainLibrary"]
        or library["majorVersion"] != 1
        or library["minorVersion"] != 0
    ):
        sys.exit("Die mitgelieferte Hauptbibliothek passt nicht zu h5p.json.")
    if not isinstance(library["embedTypes"], list) or not library["embedTypes"]:
        sys.exit("Ungültiges library.json: embedTypes fehlt oder ist leer.")
    if not set(metadata["embedTypes"]).issubset(library["embedTypes"]):
        sys.exit("h5p.json nennt einen Embed-Typ, den die Hauptbibliothek nicht unterstützt.")


metadata = load_json(H5P_JSON)
content = load_json(CONTENT_JSON)
validate_h5p_json(metadata)
validate_content_json(content)
validate_main_library(metadata)

with zipfile.ZipFile(H5P_FILE, "w", zipfile.ZIP_DEFLATED) as h5p:
    h5p.write(H5P_JSON, arcname="h5p.json")
    h5p.write(CONTENT_JSON, arcname="content/content.json")
    for library_file in LIBRARY_DIR.rglob("*"):
        if library_file.is_file():
            h5p.write(library_file, arcname=str(library_file.relative_to(LIBRARY_DIR.parent)))

with zipfile.ZipFile(H5P_FILE) as h5p:
    errors = h5p.testzip()
    required_files = {
        "h5p.json",
        "content/content.json",
        "H5P.PersonalityQuiz-1.0/library.json",
        "H5P.PersonalityQuiz-1.0/semantics.json",
        "H5P.PersonalityQuiz-1.0/js/personalityQuiz.js",
        "H5P.PersonalityQuiz-1.0/js/wheelAnimation.js",
        "H5P.PersonalityQuiz-1.0/css/personalityQuiz.css",
    }
    archive_files = set(h5p.namelist())
    if errors or not required_files.issubset(archive_files):
        sys.exit("Fehler: Das erzeugte H5P-Archiv ist unvollständig oder beschädigt.")

print(f"✓ H5P-Paket erstellt und geprüft: {H5P_FILE}")
print(f"  Grösse: {H5P_FILE.stat().st_size} Bytes")
