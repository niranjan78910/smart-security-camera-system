# Smart Security Camera System

A Python computer-vision prototype for monitoring a camera feed, detecting motion and recording events.

## Project structure

```text
code/
  main_app.py          Application entry point
  motion_detector.py   Motion-detection logic
  video_processor.py   Video processing
  event_logger.py      Event logging
  requirements.txt     Python dependencies
```

## Getting started

1. Install Python and create a virtual environment.
2. Install the dependencies:

```bash
python -m venv .venv
# Activate the virtual environment for your operating system
pip install -r code/requirements.txt
```

3. Review `code/main_app.py` to configure the appropriate camera or video source.
4. Run `python code/main_app.py` in a local environment with the required camera permissions.

> The application has not been run or tested against a camera as part of this README update. Hardware requirements and exact configuration need to be verified.

## Intended workflow

Camera/video input → video processing → motion detection → event logging.

**Important limitation:** Motion detection alone does not prove that an individual is unauthorised. The project should not be described as identifying unauthorised people without a separately validated identity/authorisation mechanism.

## Next improvements

- [ ] Add an example video or screenshots (with consent and no private footage).
- [ ] Document camera configuration and supported operating systems.
- [ ] Add tests using synthetic or consented sample frames.
- [ ] Explain detection thresholds, false positives and limitations.
- [ ] Add structured logs and graceful handling when a camera is unavailable.

## Privacy

Use this prototype only where recording is lawful and appropriately disclosed. Avoid committing personal video footage.
