# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of standalone, single-file HTML web applications. Each app is a self-contained `.html` file with inline CSS and JavaScript — no build tools, bundlers, or package managers are used.

## Architecture

- **No build system** — files are static HTML opened directly in a browser
- **Data persistence** — apps use `localStorage` for all data storage (no backend/database)
- **Dependencies** — loaded via CDN `<script>` tags when needed (e.g., Chart.js)
- **Pattern** — each app follows: CSS in `<style>`, HTML markup, then JS in a `<script>` block at the end

## Current Apps

- `index.html` — Book Tracker 2026: reading log with charts (uses Chart.js via CDN)
- `daggerheart.html` — Daggerheart TTRPG character sheet tracker with multi-character support
- `sensitivity.html` — Financial model sensitivity analysis: upload Excel, auto-detect inputs/outputs, run tornado & scenario grid analysis (uses SheetJS, HyperFormula, Chart.js via CDN)
- `pptx-template.html` — PowerPoint template applicator: apply theme/masters/layouts from a template PPTX to a content PPTX (uses JSZip via CDN)

## Development

Open any `.html` file directly in a browser. No server or build step required.
