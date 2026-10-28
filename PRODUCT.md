# Product

<!-- impeccable:product-schema 1 -->
<!-- Written on 27 Oct 2026 from the repository, the course brief and the project notes, without an interview: Antoni asked for the design setup to be done on his behalf. Lines marked (inferred) are reasoned from that material and wait for his confirmation; everything else is stated in the repository or by him. -->

## Platform

web

## Users

- Primary: the instructor and graders of CSCI 5612 (Machine Learning for Data Science, CU Boulder, Fall 2026). They open one module tab at a time and check it against the assignment: what the method is, the data before and after preparation, a link to the code, numbered figures, results, and conclusions in plain language. They also look for work that goes beyond the minimum. (inferred: their order of reading)
- Secondary: research readers outside the course who are sent the link (collaborators, possible supervisors, other researchers of human mobility and agents). They read the Research page and the results to judge whether the study is careful, honest and reproducible. (inferred)

## Product Purpose

A course project website that is also the public record of an independent research study. One question runs through it: when does an agent built from a person's ordinary days stop being a reliable description of that person, and how much fresh evidence brings it back. Each machine learning module of the course answers a piece of that question on YJMob100K (25,000 anonymous people, 75 days in half-hour slots on a 500 m grid, days 60 to 74 an emergency). Success: every tab meets its part of the assignment, the tabs read as one deliberate study rather than separate exercises, and a careful reader can check every number.

## Positioning

The course methods are instruments of one study, not a gallery of demos: each tab takes the same people and the same question, fixes its leakage rules in advance, reports results by kind of mover rather than only on average, and reports results that go against the hypotheses like any others.

## Operating Context

- Submitted in five parts through the semester, each as one Word document that links the site and the repository. A submitted part's tabs stay as they were graded.
- Analysis runs in Jupyter notebooks on CU Boulder's Alpine cluster; figures and tables arrive as numbered PNGs (f, t and o series), with logs of every number quoted on the site.
- New parts are built on a branch (module-3 for Part 3) and checked on localhost or a preview deployment before they go live on GitHub Pages.
- Read on desktop by graders; also opened on phones from a shared link. (inferred)

## Capabilities and Constraints

- Static Astro site with MDX content, one file per tab in site/src/content/tabs; GitHub Pages under the base path /agent-reliability-under-disruption/. Interactive openers built with SVG, canvas and three.js on Home, Clustering and PCA.
- Tab names and order are set by the assignment: Introduction, DataPrep_EDA, Clustering, PCA, NaiveBayes, DecTrees, Regression, AdaBoost, GradientBoosting, XGBoost, Conclusions; plus Research and About Me. A RandomForest tab after DecTrees is planned for Part 4.
- Every module tab has Overview, Data, Code, Results and Conclusions sections. Figures are numbered within the tab, captioned in two sentences (what the figure shows, then what to notice) and carry alt text.
- Tabs already submitted are not edited, apart from changes the assignment asks for. Text that Antoni writes himself, such as the Introduction paragraphs and the line on Home, is left to him and shown as a visible placeholder until he writes it.
- The site never tries to recover the city, the dates, the event or anyone's identity, and shows no basemap that would place the grid on a real map. Place types are inferred categories and are labelled as such.
- No raw or processed data in the repository: small samples in data/samples, processed tables in a GitHub release.
- AI use is disclosed in the footer.

## Brand Commitments

- Name: "Agent reliability under disruption". Author: Antoni Czolgowski.
- Voice: plain, exact English in short declarative sentences; numbers given with what they measure; no hype, no rhetorical questions in headings; the first person for the author's own choices. (inferred from the existing copy)

## Evidence on Hand

- Data: YJMob100K (Yabe et al., 2024, CC BY 4.0) and Foursquare Tokyo check-ins (Yang et al., 2015).
- Figures f01 to f52, tables t01 to t18 and overview images o01 to o10 in site/src/assets/figures; data for the interactive figures in site/src/data (including invisible_breaks.json for the Research tab); notebooks 01 to 07 in notebooks/; logs of every Part 3 number in logs/.
- There are no users, testimonials, press or deployments, and none are to be invented.

## Product Principles

1. One question, every module: a method earns its place by answering part of the reliability question.
2. Report by kind of mover, never only the average: whom an agent fails is the result.
3. Say what is measured and what is inferred; uncertainty and negative results are shown, not smoothed over.
4. Privacy before polish: nothing on the site helps locate the city or identify a person.
5. Everything checkable: code, seeds, samples and logged numbers sit next to every claim.

## Accessibility & Inclusion

- Every figure has alt text and an enlarged view in a dialog; keyboard focus is always visible; a skip link leads to the content; animation stops under prefers-reduced-motion; text stays readable at phone width.
