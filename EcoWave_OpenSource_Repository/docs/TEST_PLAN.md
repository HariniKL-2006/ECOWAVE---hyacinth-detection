# Test Plan

## Automated tests
- Invalid image raises ValueError.
- Synthetic green patch is detected.
- Output mask contains only 0/255.
- Small contours below minimum area are filtered.

Run: `pip install -r vision/requirements.txt pytest && pytest -q`

## Bench / field tests
- Startup outputs remain stopped.
- STOP disables propulsion and cutter.
- Obstacle within threshold triggers stop.
- CUTTER OFF disables cutter output.
- Emergency stop input stops outputs.
- Test in a contained water body with operator supervision, a guarded cutter, physical emergency stop, retrieval line, and manual recovery plan.
