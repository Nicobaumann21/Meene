# KI-Nutzung in diesem Projekt

## Verwendete KI-Werkzeuge

Bei der Erstellung dieser Dokumentation und von Teilen des Codes wurde **Claude (Anthropic)** als KI-Assistent eingesetzt. Konkret: Claude Opus 4.7 über die Claude-Code-CLI.

## Wofür KI eingesetzt wurde

| Bereich                          | KI-Beitrag                                                          |
|----------------------------------|---------------------------------------------------------------------|
| Setup-Anleitung (`4.1-setup.md`) | Strukturierung und Ausformulierung der Befehlssequenzen             |
| Pipeline-Code (`src/pipeline.py`) | Erstellung des Grundgerüsts (argparse, Spark-Session, Cleaning-Schritte) |
| Dokumentations-Kapitel (2.4, 3.3, 4.2, 4.5) | Strukturvorschläge, Erstentwürfe der Texte, Tabellen |
| Quellenrecherche                 | Vorschläge passender Referenzen (Harper & Konstan, Zhou et al., Koren et al.) |
| Konfigurations-Tuning            | Vorschlag der Spark-Parameter (driver-memory, partitions) für 8 GB RAM |

## Was selbst geprüft / verantwortet wurde

- Ausführung aller Befehle auf VM und Mac (Verifikation, dass alles wirklich läuft)
- Messung der konkreten Laufzeiten (95,4 s auf VM, 8,2 s lokal)
- Inhaltliche Kontrolle: stimmen die Zahlen, sind die Quellen real, ist die Argumentation plausibel
- Anpassung an die Projektanforderungen (Aufgabenstellung Person A: A1–A5)
- Auswahl und Auslegung der finalen Texte

## Stil-Hinweis

Die Dokumentation ist bewusst „plain" gehalten (gemäß Projektanforderung): pragmatisch strukturiert mit Aufzählungen und Tabellen, kein wissenschaftlicher Fließtext. KI-Vorschläge wurden in diese Form überarbeitet.

## Verantwortung

Die inhaltliche Verantwortung für die abgegebene Dokumentation und den Code liegt vollständig beim Autor.
