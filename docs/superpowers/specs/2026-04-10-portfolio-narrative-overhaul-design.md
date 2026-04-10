# Portfolio Narrative Overhaul — Design Spec

**Datum:** 2026-04-10
**Ziel:** Das Portfolio von einer Demo-Sammlung zu einer kohärenten Berufsstory umbauen.
**Ansatz:** Narrative Overhaul (A) — visuelles Design bleibt 1:1, Informationsarchitektur und Inhalte werden überarbeitet.

---

## Kontext

sinanucar.com ist ein Portfolio für einen Diplom-Informatiker mit 15+ Jahren Enterprise-Erfahrung, der sich als AI Engineer / Architect positioniert. Die Zielgruppe sind:
- **HR / Recruiter** — müssen neugierig werden (Headlines, Story)
- **CTO / Engineering Lead** — müssen überzeugt werden (Demos, Case Studies, Tiefe)

Der typische Besucher kommt über LinkedIn oder eine Bewerbung und hat 30 Sekunden um zu entscheiden: *"Kann der Mann das, was er behauptet?"*

**Kernproblem heute:** Die Website zeigt *was* Sinan kann (Demos), erzählt aber nicht *wer* er ist und wie er dahin gekommen ist. Die Verbindung zwischen 15 Jahren Engineering-Disziplin und KI-Kompetenz wird nicht sichtbar.

---

## 1. Informationsarchitektur (Navigation)

### Vorher
`Home` · `Profil` · `Lebenslauf` · `AI Showcase` · `Blog` · `Kontakt`

### Nachher
`Home` · `Projekte` · `AI Showcase` · `Über mich` · `Blog` · `Kontakt`
EN: `Home` · `Projects` · `AI Showcase` · `About` · `Blog` · `Contact`

**Änderungen:**
- `Projekte` als neue prominente Seite hinzufügen
- `Profil` + `Lebenslauf` → eine Seite `Über mich` / `About`
- Reihenfolge: Projekte kommt vor AI Showcase — weil es die Frage beantwortet bevor der Besucher die Demos sieht

---

## 2. Homepage — Hero-Text

**Subtitle bleibt:** `Senior Software Architect & AI Engineer`

**Beschreibungstext (DE):**
> Meine Diplomarbeit behandelte Neuronale Netze — 2008.
> 15 Jahre Enterprise Engineering. Ich integriere LLMs nicht als Blackbox — sondern als präzises, deterministisches Werkzeug in komplexe Systemlandschaften.

**Beschreibungstext (EN):**
> My diploma thesis covered Neural Networks — 2008.
> 15 years of enterprise engineering. I don't integrate LLMs as black boxes — but as precise, deterministic tools into complex system landscapes.

**CTAs bleiben:** `Lebenslauf ansehen` + `AI Showcase` (unverändert)

**Layout:** Bleibt wie heute — Text links, ChatWidget rechts.

---

## 3. Neue Seite: Projekte / Projects

**Route:** `/projekte` (DE) · `/en/projects` (EN)

### Aufbau

**Sektion 1 — Case Study Cards (groß)**
Jede Card enthält:
- Projektnummer + Titel + Status-Badge (Live / In Entwicklung)
- Stack-Tags
- 4 Zonen: Problem · Lösung · Stack · Ergebnis
- Optional: Link zur Live-Demo oder GitHub

**Projekte:**

#### Projekt 01 — Logopädie Report Agent
- **Problem:** Logopäden verbringen Stunden mit Berichtsschreiben statt mit Patienten
- **Lösung:** Audio-Aufnahme → Whisper-Transkription → strukturierter KI-Bericht in Sekunden
- **Stack:** Next.js · FastAPI · Groq (Whisper + LLaMA) · Pydantic
- **Ergebnis:** Vollständig funktionsfähiger Prototyp; Audio-Upload → fertig formatierter Therapiebericht
- **Status:** Live (Portfolio-Projekt)

#### Projekt 02 — RealizeTogether
- **Problem:** Kollaborative Workflows fehlen klare KI-Integration die enterprise-tauglich ist
- **Lösung:** Plattform mit KI-gestützten Features auf sicherer, deterministischer Basis
- **Stack:** Next.js 16 · Supabase · FastAPI · LangChain
- **Ergebnis:** Laufende R&D-Plattform für Production-grade AI-Architektur-Muster
- **Status:** Aktiv in Entwicklung

#### Projekt 03 — Dieses Portfolio
- **Problem:** Wie baut man ein Portfolio-Backend das Multi-Provider-Resilienz demonstriert?
- **Lösung:** FastAPI mit LangChain Multi-Fallback über 4 Anbieter (Google, OpenAI, Groq, Anthropic)
- **Stack:** FastAPI · LangChain · Pydantic · Astro · Render
- **Ergebnis:** CV-Assistent, Vision-Analyse, Sentiment-Analyse, Agentic Chat — live unter sinanucar.com
- **Status:** Live

**Sektion 2 — Kompaktes Grid**
Für zukünftige weitere Projekte (kleines Format: Titel + Tags + 1-Satz-Beschreibung).
Initial leer oder mit Platzhalter "Weitere Projekte in Kürze".

---

## 4. Überarbeitete Seite: Über mich / About

**Route:** `/ueber-mich` (DE) · `/en/about` (EN)
*(Ersetzt `/profil`, `/lebenslauf`, `/en/profile`, `/en/resume`)*

### Aufbau (von oben nach unten)

**Zone 1 — Person**
Foto · Name · `Dipl.-Inf.` · `Open for Remote` · Sprachen (DE, EN, TR)

**Zone 2 — Transition-Story**
Überschrift: *"Code, Logik & KI — die logische Entwicklung"* (oder ähnlich)

> Meine Diplomarbeit 2008 an der TU Dortmund behandelte konnektionistische Systeme — neuronale Netze, maschinelles Lernen, kognitive Neurowissenschaft. Damals noch Theorie.
>
> Was folgte, waren 15 Jahre Praxis: Enterprise-Architekturen, skalierbare Backends, komplexe Systemlandschaften — und die Erkenntnis, dass gute Ingenieurpraxis und KI kein Widerspruch sind, sondern eine Einheit.
>
> **Mein Ansatz:** Ich integriere LLMs nicht als Blackbox, sondern als deterministisches Werkzeug — mit denselben Qualitätsansprüchen die ich seit 2009 an jede Codebasis stelle.

*Hinweis: Finaler Text wird von Sinan abgenommen — das ist ein Entwurf.*

**Zone 3 — Werdegang (Timeline)**
Übernommen aus aktueller `resume.astro` — unverändert, chronologisch.

**Zone 4 — Toolbox & Arbeitsweise**
Übernommen aus aktueller `profile.astro` — Skills-Tags + Soft Skills Grid.

### Redirects
Alte Routen leiten auf neue weiter:
- `/profil` → `/ueber-mich`
- `/lebenslauf` → `/ueber-mich`
- `/en/profile` → `/en/about`
- `/en/resume` → `/en/about`

---

## 5. AI Showcase — Kontextualisierung

**Route bleibt:** `/ai` · `/en/ai`

**Änderung:** Jede der drei Demo-Sektionen bekommt einen kurzen Kontext-Absatz über der Demo:

| Demo | Kontext-Text (Kurzversion) |
|---|---|
| Sentiment Analysis | *"Gebaut um strukturierte Outputs mit Pydantic zu demonstrieren — LLMs liefern keine JSON-Strings, sondern typisierte Objekte."* |
| Vision Intelligence | *"Multimodale Analyse via LangChain — zeigt wie Bild-Inputs sicher validiert und an das Modell übergeben werden."* |
| Agentic Workflows | *"Manueller Tool-Loop ohne Framework-Magie — bewusst, weil ich verstehen will was passiert bevor ich es abstrahiere."* |

---

## 6. Technische Umsetzung

**Stack bleibt unverändert:** Astro · Tailwind CSS · FastAPI Backend

**Neue Dateien:**
- `frontend/src/pages/projekte.astro` (DE)
- `frontend/src/pages/en/projects.astro` (EN)
- `frontend/src/pages/ueber-mich.astro` (DE) — ersetzt profil.astro + lebenslauf.astro
- `frontend/src/pages/en/about.astro` (EN) — ersetzt profile.astro + resume.astro
- `frontend/src/components/ProjectCard.astro` — wiederverwendbare Case Study Card
- `frontend/src/data/projects.ts` — Projektdaten als typisiertes Array

**Geänderte Dateien:**
- `frontend/src/components/Navbar.astro` — neue Nav-Struktur
- `frontend/src/pages/index.astro` + `frontend/src/pages/en/index.astro` — Hero-Text
- `frontend/src/pages/ai.astro` + `frontend/src/pages/en/ai.astro` — Kontext-Texte
- `frontend/src/pages/index.astro` (Redirects für alte Routen)

**Gelöschte Dateien:**
- `frontend/src/pages/profil.astro`
- `frontend/src/pages/lebenslauf.astro`
- `frontend/src/pages/en/profile.astro`
- `frontend/src/pages/en/resume.astro`

*(Redirects sicherstellen bevor diese gelöscht werden)*

---

## 7. Nicht in Scope

- Visuelles Redesign — Design bleibt 1:1 wie heute
- Backend-Änderungen — FastAPI bleibt unverändert
- Blog-Seite — keine Änderungen
- Kontakt-Seite — keine Änderungen
- Neue KI-Features im Backend

---

## Erfolgskriterien

1. Ein Besucher versteht in 30 Sekunden: *wer Sinan ist, was er gebaut hat, und warum KI für ihn kein Hype ist*
2. CTO findet Case Studies mit Problem/Lösung/Stack — nicht nur Demo-Links
3. HR findet die Transition-Story und kann sie weitererzählen
4. Keine 404s durch fehlende Redirects alter Routen
