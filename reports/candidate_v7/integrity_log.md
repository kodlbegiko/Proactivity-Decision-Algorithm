# Candidate-v7 Integrity Log

Initial state: historical protected individual evidence accessed by Candidate-v7 runner: **NO**. Protected evidence used for development: **NO**. Candidate-v7 branch starts from the specified base SHA and creates new lineage artifacts only.

## Pre-freeze implementation preflight
Before any formal GitHub candidate freeze, draft parser behavior was exercised locally against development-only canonical and augmentation phrases to find negation/substring/parser defects. Every phrase family used in that preflight is classified as `DEVELOPMENT_LEXICON` and is eligible only for train/validation. The separately defined formal `HOLDOUT` renderer is not executed during architecture search; its rows are generated for the first time by the mission workflow only after the candidate-freeze commit exists. No protected rows were generated or scored during preflight.
