# EcoWave — Water Hyacinth Harvester USV

Open-source prototype starter for a low-cost unmanned surface vehicle concept to cut and collect water hyacinth in ponds and irrigation canals.

## What is included
- ESP32 Arduino firmware scaffold for propulsion output, cutter enable, ultrasonic obstacle stop, and serial commands.
- OpenCV HSV image segmentation baseline for green vegetation candidates.
- Technical architecture, test plan, synthetic sample image, tests, environment configuration, and MIT license.

**Status:** prototype software scaffold, not field-validated or safety-certified. HSV segmentation identifies green candidates, not confirmed water hyacinth. The vision pipeline is not connected to automatic cutter control.

## Hardware
Concept hardware: floating HDPE pontoon/frame, propulsion motors with suitable ESCs, guarded rotary cutter and driver, ESP32, ultrasonic sensor, GPS/camera as later integration. Pin assignments and drivers must be adapted to the actual build.

Never connect motors directly to ESP32 GPIO. Use rated drivers/ESCs, fuses, appropriate voltage conversion, waterproof enclosures, and a physical emergency stop. Test with cutter disabled first.

## Vision setup (Python 3.10+)
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r vision/requirements.txt
cp .env.example .env
python vision/segment_hyacinth.py --input data/sample/vegetation_sample.png --output mask.png
pip install pytest
pytest -q
```

## Firmware setup
1. Install Arduino IDE and ESP32 board support.
2. Open `firmware/ecowave_esp32/ecowave_esp32.ino`.
3. Check all pins and voltage levels against your circuit.
4. Test with motors disconnected, then with a current-limited driver setup.
5. Confirm obstacle stop and physical emergency stop before any water test.
6. Confirm ESC protocol: this scaffold uses generic PWM and may need replacement with manufacturer-specific control pulses/library.

Serial commands: `STOP`, `MOVE 0` through `MOVE 255`, `CUTTER ON`, `CUTTER OFF`.

## Environment variables
See `.env.example`: `ECOWAVE_H_MIN`, `ECOWAVE_H_MAX`, `ECOWAVE_S_MIN`, `ECOWAVE_V_MIN`, `ECOWAVE_MIN_AREA`. Tune with real labelled field images; lighting, glare and other plants affect HSV results.

## Repository layout
- `firmware/`: ESP32 firmware
- `vision/`: OpenCV segmentation
- `data/sample/`: synthetic smoke-test image (not field evidence)
- `tests/`: Python tests
- `docs/`: technical design and test plan
- `LICENSE`: MIT

## Safety / validation
Use a guarded cutter, physical emergency stop, battery protection, fusing, manual recovery method and supervised testing in a contained area. Ultrasonic sensors can miss soft, angled or submerged obstacles. Collect actual baseline and post-operation measurements before claiming environmental outcomes.

## Contributing
Submit issues/PRs with wiring changes, test results, and safety notes. See `docs/TECHNICAL_DESIGN.md`.
