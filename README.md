# Agent reliability under disruption

**When does an agent built from a person's ordinary days stop being a reliable description of that person, and how much fresh evidence brings it back?**

Antoni Czolgowski, M.S. Data Science, University of Colorado Boulder. An independent study that grows out of a machine learning course project (CSCI 5612, Fall 2026).

Website with all results and figures: **[antoniczolgowski.github.io/agent-reliability-under-disruption](https://antoniczolgowski.github.io/agent-reliability-under-disruption/)**

## Why this question

Simulations of cities, epidemics and policies increasingly use agents that stand in for real people. An agent built from someone's routine can look convincing on an ordinary day and still be wrong exactly when it matters, after something changes. This project measures that gap on real data: how quickly such agents stop describing their person once a disruption arrives, for whom they fail first, and how much new evidence they need to recover.

## Data

- **[YJMob100K](https://zenodo.org/records/10836269)** (Yabe et al., Scientific Data, 2024): 25,000 anonymous people in a Japanese metropolitan area, followed for 75 days in 30-minute slots on a grid of 500 m cells, 29.4 million records. Days 60 to 74 are an emergency. The city, the dates and the nature of the event are withheld by the authors, and this project does not try to recover them. Includes counts of 85 anonymous categories of places per cell.
- **[Foursquare check-ins, Tokyo](https://sites.google.com/site/yangdingqi/home/foursquare-dataset)** (Yang et al., 2015): 573,703 check-ins at named places, used as a labelled reference for what kinds of places look like over a day.

No raw or processed data is stored here. Small samples are in `data/samples/`, and the processed tables are in the [data-v1 release](https://github.com/AntoniCzolgowski/agent-reliability-under-disruption/releases/tag/data-v1).

## What is done so far

**Data audit.** Before any modelling: the weekly rhythm of the emergency block is shifted by four days against days 0 to 59, six days behave like holidays, and people are recorded 10 to 17% less often during the emergency on every kind of day while the shape of the day stays the same. Records are mostly taken while people are out and moving, which is why being seen less and moving less have to be told apart.

**Six kinds of movers.** Each person is described by 15 traits of their ordinary weeks (range, rootedness, timing). Five principal components carry 83% of the variation, and the first one, how widely a person ranges, carries half. K-means and hierarchical clustering with cosine distance agree on six kinds: far roamers, mid-range movers, regular commuters, local regulars, weekend movers and homebodies. The population is a continuum rather than separate types, so the choice of k rests on bootstrap stability as well as the silhouette.

**A first reliability result.** With the kinds frozen on days 0 to 44, a fresh ordinary fortnight still matches a person's kind for 74% of people. During the emergency it is 59%, the same for people never used in fitting. The people with the most fixed routines change most: regular commuters drop from 76% to 56%, homebodies only from 73% to 69%. Holding recording constant leaves about three quarters of the drop, so it is mostly a change in behaviour. On emergency workdays about 17% of regular commuters are missing from their usual workplace at noon, while being recorded at noon slightly more often than usual.

**Places.** The daily rhythms of 11,858 anonymous cells, read against the named Foursquare places, sort into work-like, shop-like and evening or home-like types. Workplace-like cells lose the most activity in the emergency. These labels are inferred and reported as such.

## What comes next

- **Agents and their reliability (core study).** Simple agents of each person, from last-location and habit models to a learned mix of long-run and recent behaviour, trained on days 0 to 44, validated on 45 to 59, frozen, and tested on the emergency with 0, 1, 3 or 7 days of fresh evidence. Results reported by kind of mover rather than averaged.
- **An agent that learns when to update itself.** Under a budget of updates, an agent watches its own recent errors and decides each day whether to update. Tabular Q-learning written from scratch, trained on ordinary days only and frozen before day 60, compared with fixed schedules and a simple threshold rule. If the threshold rule is enough, that is the finding.
- **Place semantics.** Estimating a daily rhythm for each of the 85 anonymous categories, validated first on Foursquare with the names hidden.

The full design, hypotheses and leakage rules are on the [Research page](https://antoniczolgowski.github.io/agent-reliability-under-disruption/research/). Results that go against the hypotheses will be reported like any others.
