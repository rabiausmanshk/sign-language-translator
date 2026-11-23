# Task checklist (copy each item into a GitHub Issue)

## Rabia - Vision/ML (folder: vision/)
- [ ] Run vision/collect_data.py, check skeleton shows
- [ ] Get Google ASL Signs subset via Kaggle notebook -> data/processed/google_asl_subset.npz
- [ ] Record own data (30 reps x 20 signs)
- [ ] Baseline model (GRU) with participant-wise split, confusion matrix
- [ ] vision/predictor.py with SignPredictor (contract 3)

## Sumaira - Context/NLP (folder: context/)
- [ ] Read + run tests for sentence_builder.py
- [ ] Add 15+ more templates and follow-up suggestions
- [ ] Use top3 to fix low-confidence guesses
- [ ] Add "sentence complete" detection (pause = end)
- [ ] LLM version (few-shot) with rule fallback

## Kainat - GUI/HCI/CG (folder: app/)
- [ ] Run app, see skeleton on webcam + mock sentence
- [ ] Wireframes (Figma) for 2 designs
- [ ] Confidence bar, Speak / Clear / Undo buttons
- [ ] Accessibility: contrast, large text, hand-not-visible hint
- [ ] Usability test plan + SUS questionnaire
