---
name: presentation-deck
description: Standards and guidelines for generating minimalist, high-impact, visual presentation decks for project defenses and executive reviews in PowerPoint (PPTX) with speaker notes and dual-theme support.
---

# Presentation Deck Architecture & Standards (SKILL.md)

This skill governs the generation of executive, academic defense, and technical presentation decks in PowerPoint format (`.pptx`).

## 1. Core Principles of Project Defense Decks

1. **The Audience Rule (Voice vs. Slide):**
   * The slides are for the audience's eyes; your voice provides the narrative.
   * Slides must NEVER contain paragraphs, walls of text, internal port numbers (`8090`, `5439`), or raw directory paths.
   * Use pure keywords and short punchy phrases (3 to 6 words per bullet).

2. **Large Typography & Legibility Hierarchy:**
   * Title: `24pt - 48pt` Bold.
   * Subtitle: `13pt - 14pt` (max 1 single sentence).
   * Card Titles: `15pt - 18pt` Bold.
   * Card Body / Bullet Points: `13pt - 14pt` (Never below `12pt`).
   * KPI Numbers: `36pt - 44pt` Bold.

3. **Dual-Theme Support (Light & Dark):**
   * **Light Deck (`presentacion_sms_sentinel_light.pptx`):** Pure White (`#FFFFFF`), subtle surfaces (`#F8F9FA`), text (`#2B2D42`).
   * **Dark Deck (`presentacion_sms_sentinel_dark.pptx`):** Deep Slate Navy (`#131524`), card slate (`#1E2238`), text (`#EDF2F4`).
   * Palette Accents: Tech Blue (`#4361EE`), Threat Red (`#EF233C`), Metric Green (`#06D6A0`), Amber (`#D97706`).

4. **Native Vector Shapes for Structural Diagrams:**
   * Do NOT use raster images with tiny text for architecture or pipeline flow diagrams.
   * Build structural slides (Architecture 3 Tiers, NLP 5 Steps) using **native PowerPoint vector shapes** (rounded rectangles, arrows, badges) with crisp, large vector typography.

5. **Mandatory Speaker Notes (`notes_slide`):**
   * Every slide MUST include comprehensive, articulate speaker notes in `slide.notes_slide.notes_text_frame.text` so the presenter has a complete speaking script in PowerPoint Presenter View.

6. **10-Slide Standard Defense Structure:**
   * Slide 1: Portada (Title & Defense Context)
   * Slide 2: El Problema (Vulnerabilidad del SMS)
   * Slide 3: La Solución (Pasarela Inteligente < 2ms)
   * Slide 4: Arquitectura del Sistema (3 Capas Nativas Desacopladas)
   * Slide 5: Procesamiento de Lenguaje Natural (Pipeline 5 Fases Nativas)
   * Slide 6: Decisión de Ingeniería (Stemming vs Lematización con Gran Gráfico)
   * Slide 7: Machine Learning (Selección de Modelos con Gran Gráfico)
   * Slide 8: Métricas y Resultados (4 KPIs Grandes y Diagnóstico)
   * Slide 9: Explicabilidad Forense (XAI - Transparencia de Coeficientes)
   * Slide 10: Conclusiones y Aportes del Proyecto (Sin Demo en Vivo, Texto Priorizado)
