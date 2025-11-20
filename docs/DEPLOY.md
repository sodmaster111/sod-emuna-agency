# Deployment quickstart

Follow these steps to confirm the production container builds with all Python dependencies (including `pyautogen`) and starts without `ModuleNotFoundError` issues.

## Build the backend image locally
```bash
docker build -t sod-emuna-agency .
```

## Run the container
```bash
docker run --rm sod-emuna-agency python main.py
```

## Verify `autogen` import inside the image
```bash
docker run --rm sod-emuna-agency python -c "import autogen; print('ok')"
```

The `Dockerfile` installs dependencies from `requirements.txt` before copying the source tree, so the `autogen` module is available via the `pyautogen` package and the app should start without import errors.
