---
name: Agent reliability under disruption
description: A research report, read tab by tab, on whether agents built from people's ordinary days still describe them once an emergency starts.
colors:
  ground: "#fcfcfa"
  ink: "#14161a"
  muted: "#5b616b"
  rule: "#d9dad6"
  plate: "#ffffff"
  cobalt: "#1f4fd8"
  vermilion: "#e8412a"
  vermilion-text: "#c7321d"
  teal: "#0e9c8a"
  teal-text: "#0b7a6c"
typography:
  display:
    fontFamily: "Chivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.1rem, 5vw, 3.1rem)"
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "-0.012em"
  headline:
    fontFamily: "Chivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.55rem"
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "-0.012em"
  title:
    fontFamily: "Chivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 500
    lineHeight: 1.15
    letterSpacing: "-0.012em"
  lede:
    fontFamily: "Brygada 1918, Georgia, Times New Roman, serif"
    fontSize: "1.3rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Brygada 1918, Georgia, Times New Roman, serif"
    fontSize: "1.1875rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Chivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.2
  caption:
    fontFamily: "Chivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.5
  numeral:
    fontFamily: "Chivo Mono, ui-monospace, Consolas, monospace"
    fontSize: "0.88em"
    fontWeight: 400
    fontFeature: "\"tnum\" 1"
rounded:
  none: "0"
spacing:
  gutter: "clamp(1.1rem, 4vw, 3rem)"
  measure: "38rem"
  wide: "60rem"
  tab-measure: "62rem"
  frame: "78rem"
components:
  nav-link:
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    padding: "0.5rem 0 0.7rem"
  button-outline:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.55rem 0.8rem"
  toggle-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
    rounded: "{rounded.none}"
    padding: "0.55rem 0.8rem"
  figure-plate:
    backgroundColor: "{colors.plate}"
    rounded: "{rounded.none}"
  caption:
    textColor: "{colors.muted}"
    typography: "{typography.caption}"
  data-table:
    textColor: "{colors.ink}"
    typography: "{typography.numeral}"
    padding: "0.45rem 1rem 0.45rem 0"
  placeholder:
    textColor: "{colors.vermilion-text}"
    typography: "{typography.numeral}"
    padding: "0.35rem 0 0.35rem 0.8rem"
---

<!-- Captured on 27 Oct 2026 from site/src/styles/global.css, the layout and the components (scan mode). The North Star, the colour names and the named rules were chosen by Claude without an interview, at Antoni's request; they wait for his confirmation. -->

# Design System: Agent reliability under disruption

## Overview

**Creative North Star: "The Field Report"**

The site reads like a careful field report printed on good paper: a serif text column made for long reading, sans-serif headings that act as signposts, numbers in a monospace face so they line up and can be checked, and thin rules instead of boxes. Nothing is decorative. Colour is scarce on purpose and always carries a meaning, so a reader who has learned that blue is an ordinary day and red is the emergency can read any figure on any tab without a legend.

Density is that of a journal article with generous measure: one text column, figures as wide as the column or a little wider, numbered and captioned in two sentences. Interactive pieces (the hero on Home, the openers on Clustering and PCA) sit inside the same frame as a figure, with square controls drawn as outlines, so they read as instruments in the report rather than as an app on top of it.

The look avoids dashboards, cards, gradients, shadows, rounded pills and icon decoration. It stays light, flat and quiet so that the data figures are the loudest thing on the page.

**Key Characteristics:**
- Serif body (Brygada 1918), sans headings and interface (Chivo), monospace numbers (Chivo Mono)
- Warm off-white ground, near-black ink, 1px grey rules; flat, no shadows, square corners everywhere
- Colour by meaning only: cobalt ordinary days, vermilion emergency, teal modelled or simulated
- Numbered figures on white plates, two-sentence captions, click to enlarge
- One reading column; tab pages widen it on large screens

## Colors

A restrained neutral paper-and-ink base with three saturated colours, each reserved for one meaning across text, figures and interactive pieces.

### Primary
- **Ordinary-Day Cobalt** (#1f4fd8): ordinary days (days 0 to 59) in every figure and interactive piece; also links and the keyboard focus ring.

### Secondary
- **Emergency Vermilion** (#e8412a): the emergency (days 60 to 74) and whatever was lost in it, such as the missing noon crowd. As text it darkens to **Vermilion Ink** (#c7321d) to stay readable on the ground; the visible placeholder for Antoni's own copy uses it too.

### Tertiary
- **Model Teal** (#0e9c8a): anything modelled or simulated rather than observed. As text it darkens to **Teal Ink** (#0b7a6c).

### Neutral
- **Paper** (#fcfcfa): page ground, toggle and button fills, the full-bleed hero.
- **Ink** (#14161a): body text, headings, outlines of controls, the pressed state of toggles.
- **Pencil Grey** (#5b616b): captions, notes, footer, figure numbers, secondary readouts.
- **Rule Grey** (#d9dad6): every hairline: section rules above h2, table rows, figure borders, header and footer rules, slider tracks.
- **Plate White** (#ffffff): the background of figure images and interactive stages, so plots exported on white sit cleanly on the warmer page.

### Named Rules
**The Fixed Meaning Rule.** Cobalt is an ordinary day, vermilion is the emergency, teal is a model. A colour never changes meaning between tabs, and no other saturated colour enters the interface chrome.

**The Six Kinds Rule.** The six kinds of movers keep one colour each wherever they appear (far roamers #2a78d6, mid-range movers #4a3aa7, regular commuters #1baf7a, local regulars #eda100, weekend movers #e87ba4, homebodies #eb6834), in exported figures and interactive openers alike.

Exported matplotlib figures use a matching chart palette on a #fcfcfb ground (ordinary #2a78d6, emergency #eb6834). The figures of Parts 1 and 2 are frozen with it, so new figures keep it too.

## Typography

**Display Font:** Chivo (with Helvetica Neue, Arial)
**Body Font:** Brygada 1918 (with Georgia, Times New Roman)
**Label/Mono Font:** Chivo Mono (with ui-monospace, Consolas)

**Character:** A bookish serif for reading paired with a sober grotesque for structure; the monospace takes every number that is meant to be compared.

### Hierarchy
- **Display** (500, clamp(2.1rem, 5vw, 3.1rem), 1.15; tab pages from 64rem: clamp(2.4rem, 4vw, 3.2rem)): the tab title, at most 22 characters wide.
- **Headline** (500, 1.55rem, 1.15; 1.75rem on wide tab pages): section headings (Overview, Data, Code, Results, Conclusions), each with a rule above.
- **Title** (500, 1.15rem, 1.15; 1.3rem on wide tab pages): sub-sections.
- **Lede** (400, 1.3rem, 1.5; 1.5rem on wide tab pages): the one-paragraph opening statement of a tab.
- **Body** (400, 1.1875rem, 1.6; 1.3rem on wide tab pages): running text, kept to a 38rem measure (62rem on wide tab pages).
- **Label** (400 and 500, 0.875rem, 1.2): navigation, buttons, toggles.
- **Caption** (400, 0.9rem, 1.5): figure captions; the figure number in Chivo Mono 0.82rem, the title at 500, the explanation in Pencil Grey.

### Named Rules
**The Monospace Number Rule.** Numbers meant to be compared (tables, readouts, counters, inline values with the num class) are set in Chivo Mono with tabular figures, so columns of numbers line up.

## Layout

A centred frame of 78rem with a fluid gutter of clamp(1.1rem, 4vw, 3rem). Inside it, one reading column of 38rem; figures and tables may run to 60rem. On tab pages at 64rem and wider the column and the figures share one 62rem edge with the navigation, and the type steps up (body 1.3rem). Sections are separated by space and a hairline rule: 3.2rem above each h2 (3.8rem on wide tab pages), 2.4rem around figures. Small table images keep their own size rather than stretching to the column. Below 48rem the navigation folds behind a Menu button and stacks vertically. The Home hero and its slice run full-bleed across the window; everything else stays in the frame.

## Elevation & Depth

Flat. There are no shadows anywhere; depth comes only from the white figure plate against the warmer paper, hairline borders, and the dimmed backdrop (#14161a at 82%) behind an enlarged figure.

### Named Rules
**The No-Shadow Rule.** Separation is made with space and 1px rules, never with shadows, cards or tinted panels.

## Shapes

Square corners throughout (0 radius): buttons, toggles, selects, figure frames, dialogs, slider thumbs. Lines are 1px in Rule Grey, or 1px in Ink for controls; the current tab is marked by a 2px Ink underline. The only round shapes are data marks inside figures.

## Components

### Buttons
- **Shape:** square (0), 1px Ink outline, transparent or Paper fill.
- **Primary:** none; every button is an outline in Ink with Chivo 500 at about 0.85rem (Menu, Close in the figure dialog, play and pause).
- **Hover / Focus:** focus shows a 2px Cobalt outline offset 3px; disabled controls turn Pencil Grey with a Rule Grey outline.

### Segmented toggle
- **Style:** a row of square buttons sharing 1px Ink borders; the pressed one is filled Ink with Paper text. Used to switch between kinds of day or views in the hero and the openers.

### Cards / Containers
- **Figure plate:** the image on Plate White inside a 1px Rule Grey border, full column width, cursor zoom-in; caption below with number, title and two sentences. Clicking opens a native dialog with the full image and a Close button.
- **Opener stage:** the same plate holding a canvas or SVG, a large monospace readout at the top left, the segmented toggle at the top right, and a bar of play button and hairline scrubber below.

### Inputs / Fields
- **Select:** square, 1px Rule Grey border, Paper fill, label-size Chivo.
- **Range scrubber:** a 1px Rule Grey track with a 2 by 14px Ink thumb.

### Navigation
- Site name at the top left in Chivo 500; two lists of tabs (the course tabs, then Research and About Me) in Chivo 0.875rem, Ink, no underline. Hover shows a Rule Grey underline, the current tab a 2px Ink underline. Below 48rem a Menu button opens a stacked list with the current tab underlined.

### Data table
- Chivo Mono 0.85rem with tabular figures, sans-serif header cells at 500, left aligned, 1px Rule Grey row rules, no fills, horizontal scroll inside its own box on narrow screens.

### Placeholder for Antoni's own copy
- Chivo Mono 0.85rem in Vermilion Ink with a 2px Vermilion rule on the left; it marks text he writes himself and must not ship to a graded part unfilled.

## Do's and Don'ts

### Do:
- **Do** keep cobalt for ordinary days, vermilion for the emergency and teal for models, in figures, openers and text alike.
- **Do** number every figure within its tab and caption it in two sentences: what it shows, then what to notice.
- **Do** set compared numbers in Chivo Mono with tabular figures.
- **Do** separate sections with space and a 1px Rule Grey line above each h2.
- **Do** build new interactive pieces from the opener pattern: a white stage in a hairline frame, a monospace readout, square outline controls, and a still or reduced-motion path.

### Don't:
- **Don't** add shadows, rounded corners, cards, gradients or tinted panels.
- **Don't** introduce a new saturated colour for interface chrome, or reuse cobalt, vermilion or teal with another meaning.
- **Don't** put a basemap, place names or anything else that could locate the grid behind a figure.
- **Don't** widen running text past the column measure, or set body text in the sans.
