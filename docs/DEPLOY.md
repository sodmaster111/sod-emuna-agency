# Deployment quickstart

Use these steps to verify the production container builds with all Python dependencies (including `pyautogen`) and starts without `ModuleNotFoundError` issues.

## Build the backend image locally
```bash
docker build -t sodmaster-backend .
```

## Run the container
```bash
docker run --rm -p 8000:8000 sodmaster-backend python main.py
```

The `Dockerfile` installs dependencies from `requirements.txt`, so the `autogen` module is available via the `pyautogen` package and the app should start without import errors.
