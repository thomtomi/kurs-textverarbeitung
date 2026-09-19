#!/usr/bin/env python3
"""Erzeugt Moodle-Book-Backups und die LibreOffice-Writer-Fassung.

Die MBZ-Dateien sind Moodle-5.0-Aktivitaetsbackups mit genau einer
Book-Aktivitaet. Sie enthalten keine Nutzerdaten und keine eingebetteten Dateien.
"""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
WORD_DIR = ROOT / "03-produkte" / "02-buch-word-bma"
LO_DIR = ROOT / "03-produkte" / "03-buch-libreoffice-bma"
LATEX_DIR = ROOT / "03-produkte" / "04-buch-latex-bma"
AI_DIR = ROOT / "03-produkte" / "05-buch-ki-bma"

# Kennungen und Metadaten der vom Strickhof exportierten Referenzsicherung.
# Moodle verwendet sie ausschliesslich als alte IDs und ordnet sie beim
# Wiederherstellen den neu angelegten Objekten zu.
MODULE_ID = "74066"
SECTION_ID = "11741"
BOOK_ID = "1041"
ACTIVITY_CONTEXT_ID = "125053"
COURSE_CONTEXT_ID = "125027"
BACKUP_ID = "11b6678988b8a3d0ae9bd8506ee91b4b"

CHAPTER_FILES = [
    "01-willkommen.html",
    "02-dokument-starten.html",
    "02-dokument-starten_sub.html",
    "03-text-strukturieren.html",
    "03-text-strukturieren_sub.html",
    "04-inhalte-einfuegen.html",
    "04-inhalte-einfuegen_sub.html",
    "05-verzeichnisse-fertigstellen.html",
    "05-verzeichnisse-fertigstellen_sub.html",
    "06-seiten-und-quellen.html",
    "06-seiten-und-quellen_sub.html",
    "07-schlusskontrolle.html",
    "07-schlusskontrolle_sub.html",
]

LATEX_CHAPTER_FILES = [
    "01-willkommen.html",
    "02-installation-windows.html",
    "02-installation-windows_sub.html",
    "03-editor-und-projekt.html",
    "03-editor-und-projekt_sub.html",
    "04-text-strukturieren.html",
    "04-text-strukturieren_sub.html",
    "05-inhalte-setzen.html",
    "05-inhalte-setzen_sub.html",
    "06-quellen-und-verzeichnisse.html",
    "06-quellen-und-verzeichnisse_sub.html",
    "07-schlusskontrolle.html",
    "07-schlusskontrolle_sub.html",
]

AI_CHAPTER_FILES = [
    "01-orientierung.html",
    "02-grundsaetze.html",
    "02-grundsaetze_sub.html",
    "03-datenschutz.html",
    "03-datenschutz_sub.html",
    "04-arbeitsumgebung.html",
    "04-arbeitsumgebung_sub.html",
    "05-prompten.html",
    "05-prompten_sub.html",
    "06-ueberarbeiten.html",
    "06-ueberarbeiten_sub.html",
    "07-deklarieren.html",
    "07-deklarieren_sub.html",
]


def body_of(html: str) -> str:
    match = re.search(r"<body>\s*(.*?)\s*</body>", html, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("HTML-Datei ohne body")
    return match.group(1)


def title_of(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("HTML-Datei ohne title")
    return re.sub(r"\s+", " ", match.group(1)).strip()


def chapter_title(filename: str, html: str) -> str:
    title = title_of(html)
    if not filename.endswith("_sub.html"):
        return re.sub(r"^\d+\.\s+", "", title)
    return title


def chapter_content(html: str) -> str:
    """Moodle Book zeigt den Kapiteltitel selbst; das doppelte H1 wird entfernt."""
    return re.sub(r"^\s*<h1>.*?</h1>\s*", "", body_of(html), count=1,
                  flags=re.DOTALL | re.IGNORECASE)


def xml_text(parent: ET.Element, name: str, value: object | None = "") -> None:
    child = ET.SubElement(parent, name)
    if value is not None:
        child.text = str(value)


def write_xml(path: Path, root: ET.Element) -> None:
    ET.indent(root, space="  ")
    # Moodle erkennt ein Moodle-2-Backup am exakten XML-Header. ElementTree
    # schreibt standardmaessig Kleinbuchstaben und einfache Anfuehrungszeichen,
    # was Moodles Format-Erkennung ablehnt.
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    path.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml)


def write_common_activity_files(activity_dir: Path, now: int) -> None:
    module = ET.Element("module", {"id": MODULE_ID, "version": "2025041400"})
    for key, value in (
        ("modulename", "book"), ("sectionid", SECTION_ID), ("sectionnumber", "5"),
        ("idnumber", ""), ("added", now), ("score", "0"), ("indent", "0"),
        ("visible", "1"), ("visibleoncoursepage", "1"), ("visibleold", "1"),
        ("groupmode", "0"), ("groupingid", "0"), ("completion", "0"),
        ("completiongradeitemnumber", "$@NULL@$"), ("completionpassgrade", "0"),
        ("completionview", "0"), ("completionexpected", "0"),
        ("availability", "$@NULL@$"), ("showdescription", "0"),
        ("downloadcontent", "1"), ("lang", ""),
    ):
        xml_text(module, key, value)
    ET.SubElement(module, "tags")
    write_xml(activity_dir / "module.xml", module)

    roles = ET.Element("roles")
    ET.SubElement(roles, "role_overrides")
    ET.SubElement(roles, "role_assignments")
    write_xml(activity_dir / "roles.xml", roles)

    grades = ET.Element("activity_gradebook")
    ET.SubElement(grades, "grade_items")
    ET.SubElement(grades, "grade_letters")
    write_xml(activity_dir / "grades.xml", grades)

    # Ohne eingebettete Dateien, Rollen, Gruppen oder Bewertungen bleibt das
    # Referenzdokument – wie bei Moodle selbst – leer.
    write_xml(activity_dir / "inforef.xml", ET.Element("inforef"))

    calendar = ET.Element("events")
    write_xml(activity_dir / "calendar.xml", calendar)
    history = ET.Element("grade_history")
    ET.SubElement(history, "grade_grades")
    write_xml(activity_dir / "grade_history.xml", history)
    filters = ET.Element("filters")
    ET.SubElement(filters, "filter_actives")
    ET.SubElement(filters, "filter_configs")
    write_xml(activity_dir / "filters.xml", filters)


def write_backup_metadata(destination: Path, book_name: str, filename: str, now: int) -> None:
    root = ET.Element("moodle_backup")
    info = ET.SubElement(root, "information")
    values = (
        ("name", filename), ("moodle_version", "2025041407"),
        ("moodle_release", "5.0.7 (Build: 20260420)"),
        ("backup_version", "2025041400"),
        ("backup_release", "5.0"), ("backup_date", now),
        ("mnet_remoteusers", "0"), ("include_files", "1"),
        ("include_file_references_to_external_content", "0"),
        ("original_wwwroot", "https://moodle.strickhof.ch"),
        ("original_site_identifier_hash", "d14e564e2cf125fbb06c1437250df0b7"),
        ("original_course_id", "1008"), ("original_course_format", "topics"),
        ("original_course_fullname", "Textverarbeitung-IDA-Vorlage-lamt"),
        ("original_course_shortname", "Textverarbeitung"), ("original_course_startdate", "1789941600"),
        ("original_course_enddate", "0"),
        ("original_course_contextid", COURSE_CONTEXT_ID), ("original_system_contextid", "1"),
    )
    for name, value in values:
        xml_text(info, name, value)

    details = ET.SubElement(info, "details")
    detail = ET.SubElement(details, "detail", {"backup_id": BACKUP_ID})
    for name, value in (("type", "activity"), ("format", "moodle2"), ("interactive", "1"),
                        ("mode", "70"), ("execution", "2"), ("executiontime", "0")):
        xml_text(detail, name, value)

    contents = ET.SubElement(info, "contents")
    activities = ET.SubElement(contents, "activities")
    activity = ET.SubElement(activities, "activity")
    for name, value in (("moduleid", MODULE_ID), ("sectionid", SECTION_ID), ("modulename", "book"),
                        ("title", book_name), ("directory", f"activities/book_{MODULE_ID}"),
                        ("insubsection", "")):
        xml_text(activity, name, value)

    settings = ET.SubElement(info, "settings")
    for level, activity_id, name, value in (
        ("root", "", "filename", filename), ("root", "", "users", "0"),
        ("root", "", "anonymize", "0"), ("root", "", "role_assignments", "0"),
        ("root", "", "activities", "1"), ("root", "", "blocks", "1"),
        ("root", "", "files", "1"), ("root", "", "filters", "1"),
        ("root", "", "comments", "0"), ("root", "", "badges", "1"),
        ("root", "", "calendarevents", "1"), ("root", "", "userscompletion", "0"),
        ("root", "", "logs", "0"), ("root", "", "grade_histories", "0"),
        ("root", "", "groups", "1"), ("root", "", "competencies", "0"),
        ("root", "", "customfield", "1"), ("root", "", "contentbankcontent", "1"),
        ("root", "", "xapistate", "0"), ("root", "", "legacyfiles", "1"),
        ("activity", f"book_{MODULE_ID}", f"book_{MODULE_ID}_included", "1"),
        ("activity", f"book_{MODULE_ID}", f"book_{MODULE_ID}_userinfo", "0"),
    ):
        setting = ET.SubElement(settings, "setting")
        xml_text(setting, "level", level)
        if activity_id:
            xml_text(setting, "activity", activity_id)
        xml_text(setting, "name", name)
        xml_text(setting, "value", value)
    write_xml(destination / "moodle_backup.xml", root)

    write_xml(destination / "files.xml", ET.Element("files"))
    write_xml(destination / "badges.xml", ET.Element("badges"))
    write_xml(destination / "completion.xml", ET.Element("course_completion"))
    groups = ET.Element("groups")
    ET.SubElement(groups, "groupcustomfields")
    groupings = ET.SubElement(groups, "groupings")
    ET.SubElement(groupings, "groupingcustomfields")
    write_xml(destination / "groups.xml", groups)
    write_xml(destination / "outcomes.xml", ET.Element("outcomes_definition"))
    write_xml(destination / "questions.xml", ET.Element("question_categories"))
    write_xml(destination / "roles.xml", ET.Element("roles_definition"))
    write_xml(destination / "scales.xml", ET.Element("scales_definition"))
    (destination / "moodle_backup.log").touch()


def build_mbz(source_dir: Path, output: Path, book_name: str, chapter_files: list[str] = CHAPTER_FILES) -> None:
    now = int(datetime.now(timezone.utc).timestamp())
    with TemporaryDirectory() as temporary:
        staging = Path(temporary)
        activity_dir = staging / "activities" / f"book_{MODULE_ID}"
        activity_dir.mkdir(parents=True)
        write_common_activity_files(activity_dir, now)

        book_xml = ET.Element("activity", {
            "id": BOOK_ID, "moduleid": MODULE_ID, "modulename": "book",
            "contextid": ACTIVITY_CONTEXT_ID,
        })
        book = ET.SubElement(book_xml, "book", {"id": BOOK_ID})
        for name, value in (("name", book_name), ("intro", ""), ("introformat", "1"),
                            ("numbering", "1"), ("navstyle", "1"), ("customtitles", "0"),
                            ("timecreated", now), ("timemodified", now)):
            xml_text(book, name, value)
        chapters = ET.SubElement(book, "chapters")
        for page, filename in enumerate(chapter_files, 1):
            html = (source_dir / filename).read_text(encoding="utf-8")
            chapter = ET.SubElement(chapters, "chapter", {"id": str(page)})
            for name, value in (("pagenum", page), ("subchapter", int(filename.endswith("_sub.html"))),
                                ("title", chapter_title(filename, html)),
                                ("content", chapter_content(html)), ("contentformat", "1"),
                                ("hidden", "0"), ("timemodified", now), ("importsrc", "")):
                xml_text(chapter, name, value)
        ET.SubElement(book, "chaptertags")
        write_xml(activity_dir / "book.xml", book_xml)

        write_backup_metadata(staging, book_name, output.name, now)
        output.parent.mkdir(parents=True, exist_ok=True)
        write_moodle_tgz(staging, output, now)


def write_moodle_tgz(staging: Path, output: Path, now: int) -> None:
    """Erzeugt das von der Strickhof-Installation verwendete TGZ-MBZ-Format."""
    activity = f"activities/book_{MODULE_ID}"
    entries = [
        "activities/", f"{activity}/",
        f"{activity}/grades.xml", f"{activity}/calendar.xml",
        f"{activity}/grade_history.xml", f"{activity}/roles.xml",
        f"{activity}/module.xml", f"{activity}/inforef.xml",
        f"{activity}/filters.xml", f"{activity}/book.xml",
        "badges.xml", "completion.xml", "files.xml", "groups.xml",
        "moodle_backup.xml", "outcomes.xml", "questions.xml", "roles.xml",
        "scales.xml", "moodle_backup.log",
    ]
    index = [f"Moodle archive file index. Count: {len(entries)}"]
    for name in entries:
        path = staging / name.rstrip("/")
        if name.endswith("/"):
            index.append(f"{name}\td\t0\t?")
        else:
            index.append(f"{name}\tf\t{path.stat().st_size}\t{now}")
    (staging / ".ARCHIVE_INDEX").write_text("\n".join(index) + "\n", encoding="utf-8")

    with tarfile.open(output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        ordered = [".ARCHIVE_INDEX", *entries]
        for name in ordered:
            path = staging / name.rstrip("/")
            info = archive.gettarinfo(str(path), arcname=name.rstrip("/"))
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = now
            if info.isfile():
                with path.open("rb") as handle:
                    archive.addfile(info, handle)
            else:
                archive.addfile(info)


def libreoffice_html(word_html: str) -> str:
    replacements = {
        "Deine BMA in Word": "Deine BMA in LibreOffice Writer",
        "Word-Desktop-App (Microsoft 365 unter Windows)": "LibreOffice Writer (aktuelle Desktop-Version)",
        "Word-Funktionen": "Writer-Funktionen",
        "Word-Formatvorlage": "Writer-Formatvorlage",
        "Word-Tabellen": "Writer-Tabellen",
        "Word-Funktion": "Writer-Funktion",
        "Word-Beschriftung": "Writer-Beschriftung",
        "Die finale Word-Runde": "Die finale Writer-Runde",
        "Die Word-Datei": "Die Arbeitsdatei",
        "die Word-Technik": "die Writer-Technik",
        "Word-Quellenverwaltung": "Quellenverwaltung von Writer",
        "Citavi-Word-Add-in": "Literaturverwaltung",
        "mit Word-Integration": "mit Writer-Integration",
        "in Word integriert": "in Writer integriert",
        "Word erzeugt": "Writer erzeugt",
        "von Word erzeugt": "von Writer erzeugt",
        "in Word": "in Writer",
        "Word kann": "Writer kann",
        "Word-Technik": "Writer-Technik",
        "Word-Datei": "ODT-Datei",
        ".docx": ".odt",
    }
    for old, new in replacements.items():
        word_html = word_html.replace(old, new)
    return word_html


def replace_block(html: str, old: str, new: str) -> str:
    if old not in html:
        raise ValueError(f"Zu ersetzender Text nicht gefunden: {old[:50]}")
    return html.replace(old, new)


def refine_libreoffice(filename: str, html: str) -> str:
    custom = {
        "01-willkommen.html": (
            "Dieses Buch begleitet dich von der verbindlichen Word-Vorlage bis zur finalen PDF. Du arbeitest nicht mit Leerzeichen, Tabulatoren oder manuellen Seitenzahlen, sondern mit den Writer-Funktionen, die dir später Arbeit abnehmen.",
            "Dieses Buch begleitet dich von der verbindlichen Strickhof-Vorlage bis zur finalen PDF. Du arbeitest nicht mit Leerzeichen, Tabulatoren oder manuellen Seitenzahlen, sondern mit den Writer-Funktionen, die dir später Arbeit abnehmen. Die offizielle Vorlage liegt als DOCX vor; Writer kann sie öffnen, doch die Arbeitskopie speicherst du sinnvoll als ODT und prüfst das Layout.",
        ),
        "01-willkommen.html#application": (
            "die LibreOffice Writer (aktuelle Desktop-Version)",
            "LibreOffice Writer (aktuelle Desktop-Version)",
        ),
        "01-willkommen.html#help": (
            "Nutze ein verlinktes Video nur dann, wenn ein Schritt noch nicht sitzt.",
            "Nutze bei Bedarf die integrierte Hilfe von LibreOffice oder frage deine Lehrperson.",
        ),
        "02-dokument-starten.html": (
            "Speichere die offizielle Vorlage unter einem klaren Namen, zum Beispiel <em>BMA_Nachname_Projekt.odt</em>.",
            "Öffne die offizielle DOCX-Vorlage in Writer, prüfe die Darstellung und speichere deine Arbeitskopie unter einem klaren Namen, zum Beispiel <em>BMA_Nachname_Projekt.odt</em>.",
        ),
        "02-dokument-starten.html#save": (
            "Aktiviere unter <strong>Datei → Optionen → Speichern</strong> die automatische Wiederherstellung und speichere regelmässig mit <kbd>Ctrl</kbd> + <kbd>S</kbd>.",
            "Aktiviere unter <strong>Extras → Optionen → Laden/Speichern → Allgemein</strong> die AutoWiederherstellung und bei Bedarf die Sicherungskopie. Speichere regelmässig mit <kbd>Ctrl</kbd> + <kbd>S</kbd>.",
        ),
        "02-dokument-starten_sub.html": (
            "Unter <strong>Überprüfen → Sprache → Sprache für die Korrekturhilfen festlegen</strong> wählst du die passende Dokumentsprache. Prüfe danach unter <strong>Layout → Silbentrennung</strong>, ob die automatische Silbentrennung eingestellt ist.",
            "Unter <strong>Extras → Sprache → Für alle Texte → Deutsch (Schweiz)</strong> wählst du die passende Dokumentsprache. Die automatische Silbentrennung stellst du über <strong>Format → Absatz → Textfluss</strong> ein.",
        ),
        "02-dokument-starten_sub.html#format": (
            "die aktuelle DOCX-Datei an einem verlässlichen Ort.",
            "die aktuelle ODT-Datei an einem verlässlichen Ort.",
        ),
        "03-text-strukturieren.html": (
            "Wähle unter <strong>Start → Formatvorlagen</strong> die passende Überschrift.",
            "Öffne mit <kbd>F11</kbd> die Seitenleiste <strong>Formatvorlagen</strong> und wähle die passende Überschrift.",
        ),
        "03-text-strukturieren_sub.html": (
            "Wenn die Nummerierung nicht bereits mit der Vorlage funktioniert, markiere eine Überschrift und wähle unter <strong>Start → Liste mit mehreren Ebenen</strong> eine Liste, die mit <em>Überschrift 1–3</em> verknüpft ist. Prüfe sofort an drei Ebenen, ob die Nummerierung stimmt.",
            "Wenn die Nummerierung nicht bereits mit der Vorlage funktioniert, richte sie über <strong>Extras → Kapitelnummerierung…</strong> ein und verknüpfe die Ebenen mit <em>Überschrift 1–3</em>. Prüfe sofort an drei Ebenen, ob die Nummerierung stimmt.",
        ),
        "03-text-strukturieren_sub.html#lists": (
            "Für Aufzählungen und nummerierte Schritte verwendest du <strong>Start → Aufzählungszeichen</strong> beziehungsweise <strong>Nummerierung</strong>. Passe Einzüge über die Listen- oder Absatzformatierung an, nicht über Tabulatoren und Leerzeichen.",
            "Für Aufzählungen und nummerierte Schritte verwendest du die Symbole <strong>Aufzählung</strong> beziehungsweise <strong>Nummerierung</strong> in der Symbolleiste oder <strong>Format → Aufzählungszeichen und Nummerierung…</strong>. Passe Einzüge über die Listen- oder Absatzformatierung an, nicht über Tabulatoren und Leerzeichen.",
        ),
        "03-text-strukturieren_sub.html#fix": (
            "Blende mit <strong>Start → ¶</strong> Formatierungszeichen ein.",
            "Blende mit <kbd>Ctrl</kbd> + <kbd>F10</kbd> Formatierungszeichen ein.",
        ),
        "03-text-strukturieren_sub.html#clear": (
            "Entferne direkte Formatierung mit <kbd>Ctrl</kbd> + <kbd>Leertaste</kbd> (Zeichen) oder <kbd>Ctrl</kbd> + <kbd>Q</kbd> (Absatz), falls nötig.",
            "Entferne direkte Formatierung bei Bedarf mit <kbd>Ctrl</kbd> + <kbd>M</kbd>.",
        ),
        "04-inhalte-einfuegen.html": (
            "Füge ein Bild über <strong>Einfügen → Bilder</strong> ein. Wähle ein ruhiges Layout und achte darauf, dass das Bild beim Bearbeiten nicht unkontrolliert springt. Mit einem Rechtsklick auf das Bild findest du <strong>Textumbruch</strong>; für einfache Dokumente ist «Mit Text in Zeile» oft die robusteste Wahl.",
            "Füge ein Bild über <strong>Einfügen → Bild…</strong> ein. Wähle ein ruhiges Layout und achte darauf, dass das Bild beim Bearbeiten nicht unkontrolliert springt. Mit einem Rechtsklick auf das Bild findest du <strong>Umbruch</strong>; für einfache Dokumente ist «Als Zeichen» oft die robusteste Wahl.",
        ),
        "04-inhalte-einfuegen.html#table": (
            "Für einfache Übersichten verwendest du <strong>Einfügen → Tabelle</strong>. Grössere Berechnungen oder Diagramme gehören in Excel und werden anschliessend sauber in Writer integriert. Überlege vorher: Muss die Excel-Datei verknüpft sein, oder reicht ein statischer Stand? Verknüpfungen können sich ändern und müssen kontrolliert werden.",
            "Für einfache Übersichten verwendest du <strong>Tabelle → Tabelle einfügen…</strong>. Grössere Berechnungen oder Diagramme gehören in LibreOffice Calc und werden anschliessend sauber in Writer integriert. Überlege vorher: Muss die Calc-Datei verknüpft sein, oder reicht ein statischer Stand? Verknüpfungen können sich ändern und müssen kontrolliert werden.",
        ),
        "04-inhalte-einfuegen_sub.html": (
            "Wähle <strong>Referenzen → Beschriftung einfügen</strong>.",
            "Wähle <strong>Einfügen → Beschriftung…</strong>.",
        ),
        "05-verzeichnisse-fertigstellen.html": (
            "Ein automatisches Verzeichnis wird nicht geschrieben, sondern von Writer erzeugt.",
            "Ein automatisches Verzeichnis wird nicht geschrieben, sondern von Writer aus den Formatvorlagen und Beschriftungen erzeugt.",
        ),
        "05-verzeichnisse-fertigstellen.html#toc": (
            "Die Strickhof-Vorlage enthält ein vorbereitetes Inhaltsverzeichnis. Klicke hinein, wähle <strong>Inhaltsverzeichnis aktualisieren</strong> und aktualisiere bei Strukturänderungen <strong>das gesamte Verzeichnis</strong>. Voraussetzung: Alle Kapitelüberschriften verwenden <em>Überschrift 1–3</em>.",
            "Die Strickhof-Vorlage kann in Writer ein vorbereitetes Inhaltsverzeichnis enthalten. Klicke mit der rechten Maustaste hinein und wähle <strong>Verzeichnis aktualisieren</strong>. Falls noch keines vorhanden ist, füge es über <strong>Einfügen → Verzeichnis und Tabellen → Verzeichnis…</strong> ein. Voraussetzung: Alle Kapitelüberschriften verwenden <em>Überschrift 1–3</em>.",
        ),
        "05-verzeichnisse-fertigstellen.html#figures": (
            "Diese Verzeichnisse sammeln ausschliesslich Elemente, die mit <strong>Beschriftung einfügen</strong> erfasst wurden. Aktualisiere auch sie nach grösseren Änderungen.",
            "Diese Verzeichnisse sammeln ausschliesslich Elemente, die mit <strong>Einfügen → Beschriftung…</strong> erfasst wurden. Füge sie bei Bedarf über <strong>Einfügen → Verzeichnis und Tabellen → Verzeichnis…</strong> ein und aktualisiere sie per Rechtsklick.",
        ),
        "05-verzeichnisse-fertigstellen.html#update": (
            "<strong>Schnell aktualisieren:</strong> <kbd>Ctrl</kbd> + <kbd>A</kbd>, danach <kbd>F9</kbd>. Bestätige bei Bedarf die Aktualisierung des gesamten Verzeichnisses. Prüfe das Ergebnis anschliessend visuell.",
            "<strong>Aktualisieren:</strong> Klicke mit der rechten Maustaste in jedes Verzeichnis und wähle <strong>Verzeichnis aktualisieren</strong>. Mit <kbd>F9</kbd> aktualisierst du Felder. Prüfe das Ergebnis anschliessend visuell.",
        ),
        "05-verzeichnisse-fertigstellen_sub.html": (
            "Wenn ein Index sinnvoll ist, markierst du wichtige Begriffe über <strong>Referenzen → Eintrag markieren</strong>. Writer kann daraus unter <strong>Referenzen → Index einfügen</strong> einen Index erzeugen.",
            "Wenn ein Index sinnvoll ist, markierst du wichtige Begriffe über <strong>Einfügen → Verzeichnis und Tabellen → Stichwortverzeichniseintrag…</strong>. Writer kann daraus über <strong>Einfügen → Verzeichnis und Tabellen → Verzeichnis…</strong> ein Stichwortverzeichnis erzeugen.",
        ),
        "06-seiten-und-quellen.html": (
            "Du verstehst, wofür Abschnittsumbrüche nötig sind.",
            "Du verstehst, wie Seitenvorlagen unterschiedliche Seitenbereiche steuern.",
        ),
        "06-seiten-und-quellen.html#breaks": (
            "Einen normalen Seitenumbruch setzt du über <strong>Einfügen → Seitenumbruch</strong>. Einen <strong>Abschnittsumbruch</strong> brauchst du, wenn sich zum Beispiel Ausrichtung, Kopf-/Fusszeile oder Seitennummerierung ab einer Stelle ändern sollen: <strong>Layout → Umbrüche → Nächste Seite</strong>.",
            "Einen normalen Seitenumbruch setzt du mit <kbd>Ctrl</kbd> + <kbd>Enter</kbd>. Wenn sich ab einer Stelle Ausrichtung, Kopf-/Fusszeile oder Seitennummerierung ändern sollen, verwende <strong>Einfügen → Mehr Umbrüche → Manueller Umbruch…</strong> und weise eine passende <strong>Seitenvorlage</strong> zu.",
        ),
        "06-seiten-und-quellen.html#header": (
            "Öffne danach die Kopf- oder Fusszeile. Die Schaltfläche <strong>Mit vorheriger verknüpfen</strong> entscheidet, ob der neue Abschnitt die Angaben des vorherigen Abschnitts übernimmt. Prüfe immer beide Abschnitte.",
            "Kopf- und Fusszeilen gehören in Writer zur Seitenvorlage. Aktiviere oder prüfe sie über <strong>Format → Seitenvorlage…</strong>. Prüfe immer die verwendeten Seitenvorlagen.",
        ),
        "06-seiten-und-quellen.html#footnote": (
            "Fussnoten fügst du über <strong>Referenzen → Fussnote einfügen</strong> ein.",
            "Fussnoten fügst du über <strong>Einfügen → Fussnote und Endnote → Fussnote</strong> ein.",
        ),
        "06-seiten-und-quellen_sub.html": (
            "Die Quellenverwaltung von Writer ist unter <strong>Referenzen</strong> erreichbar. Für eine längere Arbeit ist eine Literaturverwaltung wie Zotero besonders hilfreich; die BMA-Vorlage empfiehlt Zotero.",
            "Writer bringt eine einfache Datenbank für Literaturangaben mit. Für eine längere Arbeit ist eine Literaturverwaltung wie Zotero besonders hilfreich; prüfe, ob die Zotero-Erweiterung für LibreOffice installiert ist.",
        ),
        "06-seiten-und-quellen_sub.html#note": (
            "Dieses Buch erklärt die Writer-Technik. Für Fragen zu APA 7 und zur inhaltlichen Qualität deiner Quellen nutze das Moodle-Modul «Quellenangaben / Zitieren» und besprich Sonderfälle mit deiner Betreuungsperson.",
            "Dieses Buch erklärt die Writer-Technik. Für Fragen zu APA 7 und zur inhaltlichen Qualität deiner Quellen nutze das Moodle-Modul «Quellenangaben / Zitieren» und besprich Sonderfälle mit deiner Betreuungsperson.",
        ),
        "07-schlusskontrolle.html": (
            "Aktualisiere mit <kbd>Ctrl</kbd> + <kbd>A</kbd>, <kbd>F9</kbd> alle Felder und Verzeichnisse.",
            "Aktualisiere Felder mit <kbd>F9</kbd>; aktualisiere jedes Inhalts-, Abbildungs- und Tabellenverzeichnis zusätzlich per Rechtsklick mit <strong>Verzeichnis aktualisieren</strong>.",
        ),
        "07-schlusskontrolle.html#spell": (
            "Starte die Rechtschreibeprüfung mit <kbd>F7</kbd>.",
            "Starte die Rechtschreibeprüfung mit <kbd>F7</kbd>.",
        ),
        "07-schlusskontrolle.html#count": (
            "Kontrolliere die Wort- und Zeichenzahl über <strong>Überprüfen → Wörter zählen</strong>.",
            "Kontrolliere die Wort- und Zeichenzahl über <strong>Extras → Wortzählung</strong>.",
        ),
        "07-schlusskontrolle_sub.html": (
            "Die Arbeitsdatei ist gespeichert und gesichert.",
            "Die ODT-Arbeitsdatei ist gespeichert und gesichert.",
        ),
        "07-schlusskontrolle_sub.html#breaks": (
            "Alle Seitenzahlen, Kopf-/Fusszeilen und Abschnittswechsel sind plausibel.",
            "Alle Seitenzahlen, Kopf-/Fusszeilen und Wechsel der Seitenvorlage sind plausibel.",
        ),
    }
    for key, pair in custom.items():
        base = key.split("#", 1)[0]
        if base == filename:
            html = replace_block(html, *pair)
    return html


def build_libreoffice_book() -> None:
    html_dir = LO_DIR / "html-import"
    html_dir.mkdir(parents=True, exist_ok=True)
    for filename in CHAPTER_FILES:
        source = (WORD_DIR / "html-import" / filename).read_text(encoding="utf-8")
        converted = refine_libreoffice(filename, libreoffice_html(source))
        # Word-spezifische Tutorial-Links entfernen; die Schritte im Kapitel sind vollstaendig.
        converted = re.sub(r"\s*<p><a href=\"https?://(?:www\.)?(?:youtube\.com|youtu\.be).*?</p>", "",
                           converted, flags=re.DOTALL)
        (html_dir / filename).write_text(converted, encoding="utf-8")

    with ZipFile(LO_DIR / "moodle-buch-bma-libreoffice-html-import.zip", "w", ZIP_DEFLATED) as archive:
        for filename in CHAPTER_FILES:
            archive.write(html_dir / filename, filename)

    readme = """# Moodle-Buch: «Deine BMA in LibreOffice Writer»

Diese Fassung vermittelt dieselben BMA-Arbeitsschritte wie das Word-Buch,
aber mit den Funktionen von **LibreOffice Writer**. Sie eignet sich auch als
Orientierung für Apache OpenOffice Writer; Menübezeichnungen und einzelne
Funktionen können dort abweichen. Empfohlen ist LibreOffice, weil es aktiv
weiterentwickelt wird.

## Dateien

- `moodle-buch-bma-libreoffice.mbz`: Moodle-5.0-Aktivitätsbackup mit einem Buch
  und 13 Kapiteln (ohne Nutzerdaten).
- `moodle-buch-bma-libreoffice-html-import.zip`: Alternative für den nativen
  Kapitelimport in ein bereits angelegtes Moodle-Buch.

## Import der MBZ-Datei

Im Zielkurs **Mehr → Wiederherstellen** wählen, die `.mbz`-Datei hochladen und
als einzelne Aktivität in den bestehenden Kurs wiederherstellen. Die Datei
enthält keine Teilnehmenden, Bewertungen oder eingebetteten Dateien.

## Hinweis zur Vorlage

Die verbindliche Strickhof-Vorlage liegt als DOCX vor. In Writer zuerst die
Darstellung prüfen und die persönliche Arbeitskopie als ODT speichern. Für die
Abgabe gelten weiterhin die Vorgaben der BMA-Wegleitung, insbesondere das
verlangte PDF-Format.
"""
    (LO_DIR / "README.md").write_text(readme, encoding="utf-8")
    build_mbz(html_dir, LO_DIR / "moodle-buch-bma-libreoffice.mbz", "Deine BMA in LibreOffice Writer")


def build_latex_book() -> None:
    """Packt das manuell gepflegte LaTeX-Buch als HTML-Import und MBZ."""
    html_dir = LATEX_DIR / "html-import"
    missing = [name for name in LATEX_CHAPTER_FILES if not (html_dir / name).is_file()]
    if missing:
        raise ValueError(f"LaTeX-Kapitel fehlen: {missing}")

    with ZipFile(LATEX_DIR / "moodle-buch-bma-latex-html-import.zip", "w", ZIP_DEFLATED) as archive:
        for filename in LATEX_CHAPTER_FILES:
            archive.write(html_dir / filename, filename)

    readme = """# Moodle-Buch: «Deine BMA mit LaTeX»

Dieses Buch ist ein Einstieg in LaTeX für eine Berufsmaturitätsarbeit. Es
enthält die Einrichtung unter Windows und macOS, Empfehlungen für
einsteigerfreundliche Editoren, Projektstruktur, Text, Bilder, Tabellen,
Formeln, Quellen und die Schlusskontrolle.

## Empfohlene Arbeitsumgebung

- **Windows:** MiKTeX und TeXstudio.
- **macOS:** MacTeX und TeXstudio.
- **Ohne Installation:** Overleaf, falls die schulischen Datenschutzvorgaben
  die Arbeit auf externen Servern erlauben.

Die ausführliche Referenz `01-kontextwissen/lshort.pdf` ergänzt dieses Buch.

## Dateien und Import

- `moodle-buch-bma-latex.mbz`: Moodle-5-Aktivitätsbackup mit einem Buch und
  13 Kapiteln. Im Zielkurs **Mehr → Wiederherstellen** wählen und als
  Aktivität in einen bestehenden Kurs einfügen.
- `moodle-buch-bma-latex-html-import.zip`: Alternative für den nativen
  Kapitelimport in ein bereits angelegtes Moodle-Buch.
"""
    (LATEX_DIR / "README.md").write_text(readme, encoding="utf-8")
    build_mbz(html_dir, LATEX_DIR / "moodle-buch-bma-latex.mbz", "Deine BMA mit LaTeX", LATEX_CHAPTER_FILES)


def build_ai_book() -> None:
    """Packt das anbieterneutrale KI-Buch als HTML-Import und MBZ."""
    html_dir = AI_DIR / "html-import"
    missing = [name for name in AI_CHAPTER_FILES if not (html_dir / name).is_file()]
    if missing:
        raise ValueError(f"KI-Kapitel fehlen: {missing}")

    with ZipFile(AI_DIR / "moodle-buch-bma-ki-html-import.zip", "w", ZIP_DEFLATED) as archive:
        for filename in AI_CHAPTER_FILES:
            archive.write(html_dir / filename, filename)

    readme = """# Moodle-Buch: «KI für die BMA: sicher, kritisch, transparent»

Dieses Buch zeigt eine anbieterneutrale, schrittweise Arbeitsweise für den
Einsatz von generativer KI beim Formatieren und Überarbeiten einer BMA. Es ist
kein Ersatz für die wissenschaftliche Eigenleistung, die Quellenarbeit oder
die Betreuung.

## Lernziele

- KI-Aufgaben mit klaren Grenzen formulieren und datensparsam bearbeiten.
- Eine wiederverwendbare Arbeitsumgebung und robuste Prompts erstellen.
- Resultate systematisch prüfen, überarbeiten und als eigene Arbeit vertreten.
- KI-Einsatz gemäss BMA-Wegleitung deklarieren und an der Textstelle per
  Fussnote ausweisen.

## Fachliche Grundlage

- `01-kontextwissen/260709 - A2-200 Wegleitung BMA mit Bewertungsraster_rot.pdf`,
  insbesondere Kapitel 2.3, 2.6, 2.8 und 2.9 sowie Kapitel 3.8 und 3.11.
- `01-kontextwissen/A2-322 KI Einsatz im Unterricht 260630.pdf`, insbesondere
  Kapitel 6 (Datenschutz und Sicherheit), 7 (Kennzeichnung) und 8
  (Urheber- und Nutzungsrechte).

## Dateien und Import

- `moodle-buch-bma-ki.mbz`: Moodle-5-Aktivitätsbackup mit einem Buch und
  13 Kapiteln. Im Zielkurs **Mehr → Wiederherstellen** wählen und als
  Aktivität in einen bestehenden Kurs einfügen.
- `moodle-buch-bma-ki-html-import.zip`: Alternative für den nativen
  Kapitelimport in ein bereits angelegtes Moodle-Buch.
"""
    (AI_DIR / "README.md").write_text(readme, encoding="utf-8")
    build_mbz(html_dir, AI_DIR / "moodle-buch-bma-ki.mbz",
              "KI für die BMA: sicher, kritisch, transparent", AI_CHAPTER_FILES)


def update_word_readme() -> None:
    path = WORD_DIR / "README.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("## Import in Moodle 5.0.4\n", """## Dateien und Import in Moodle 5.0.4

- `moodle-buch-bma-word.mbz`: Moodle-Aktivitätsbackup mit einem Buch und allen 13 Kapiteln. Im Zielkurs **Mehr → Wiederherstellen** wählen und als Aktivität in einen bestehenden Kurs einfügen.
- `moodle-buch-bma-word-html-import.zip`: HTML-Alternative für den nativen Kapitelimport.

### HTML-Alternative
""")
    path.write_text(text, encoding="utf-8")


def validate(path: Path, chapter_files: list[str] = CHAPTER_FILES) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
        required = {
            ".ARCHIVE_INDEX", "moodle_backup.xml", "files.xml", "roles.xml",
            "groups.xml", "scales.xml", "questions.xml", "outcomes.xml",
            f"activities/book_{MODULE_ID}/book.xml", f"activities/book_{MODULE_ID}/module.xml",
            f"activities/book_{MODULE_ID}/inforef.xml", f"activities/book_{MODULE_ID}/roles.xml",
            f"activities/book_{MODULE_ID}/grades.xml", f"activities/book_{MODULE_ID}/filters.xml",
            f"activities/book_{MODULE_ID}/calendar.xml", f"activities/book_{MODULE_ID}/grade_history.xml",
        }
        missing = required - names
        if missing:
            raise ValueError(f"{path.name}: fehlende Dateien: {sorted(missing)}")
        for name in required:
            if name.endswith(".xml"):
                handle = archive.extractfile(name)
                if handle is None:
                    raise ValueError(f"{path.name}: nicht lesbar: {name}")
                ET.fromstring(handle.read())
        handle = archive.extractfile(f"activities/book_{MODULE_ID}/book.xml")
        if handle is None:
            raise ValueError(f"{path.name}: book.xml nicht lesbar")
        book = ET.fromstring(handle.read())
        if len(book.findall("./book/chapters/chapter")) != len(chapter_files):
            raise ValueError(f"{path.name}: unvollstaendige Kapitelanzahl")


def main() -> None:
    update_word_readme()
    build_mbz(WORD_DIR / "html-import", WORD_DIR / "moodle-buch-bma-word.mbz", "Deine BMA in Word")
    build_libreoffice_book()
    build_latex_book()
    build_ai_book()
    validate(WORD_DIR / "moodle-buch-bma-word.mbz")
    validate(LO_DIR / "moodle-buch-bma-libreoffice.mbz")
    validate(LATEX_DIR / "moodle-buch-bma-latex.mbz", LATEX_CHAPTER_FILES)
    validate(AI_DIR / "moodle-buch-bma-ki.mbz", AI_CHAPTER_FILES)


if __name__ == "__main__":
    main()
