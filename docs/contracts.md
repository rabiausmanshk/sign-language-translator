# Interface contracts (do not change without telling the team)

## 1. Prediction (Vision -> Context, GUI)
{"sign": "water", "confidence": 0.91,
 "top3": [["water",0.91],["drink",0.06],["milk",0.02]], "timestamp": 12.4}

## 2. Context output (Context -> GUI)
{"sentence": "Water, please.", "suggestions": ["thankyou"], "raw_signs": ["water","please"]}

## 3. Vision's Python entry point (A promises this exists by end of Week 1)
vision/predictor.py:  class SignPredictor:  .push_frame(features_144) -> prediction dict | None

## Feature vector (per frame) = 144 numbers
left hand 21x3 + right hand 21x3 + 6 pose points (shoulders, elbows, wrists) x3
Order matters. Defined in vision/features.py.
