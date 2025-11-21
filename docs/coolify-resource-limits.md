# Coolify Resource Limits & Auto-Restart Policies (SOD-COOLIFY-OPS-003)

## Recommended Limits
| Service       | CPU Limit (vCPU) | CPU Limit (milliCPU) | Memory Limit (MiB) | Auto-restart |
|---------------|------------------|----------------------|--------------------|--------------|
| backend       | 2                | 2000                 | 2048–3072          | always       |
| frontend      | 1                | 1000                 | 1024–2048          | always       |
| tg-gateway    | 0.5–1            | 500–1000             | 512–1024           | always       |
| wa-gateway    | 0.5–1            | 500–1000             | 512–1024           | always       |
| ton-service   | 0.5–1            | 500–1000             | 512–1024           | always       |
| ollama        | 6–8              | 6000–8000            | 24576–32768        | always       |
| postgres      | 2                | 2000                 | 4096–6144          | always       |
| redis         | 1                | 1000                 | 1024–2048          | always       |

> Notes
> * CPU values can be entered as fractional cores (e.g., `0.5`) or milliCPU (e.g., `500`).
> * Memory values use MiB. Use the lower bound first and raise only if monitoring shows pressure.
> * Ollama is the heavy service—ensure it stays within 6–8 vCPU and 24–32 GB RAM so the host keeps headroom for the rest.

## Coolify UI: Where to Set Limits
For each service in Coolify:
1. Open the **Service** → **Configuration** tab.
2. Scroll to **Resource Limits**.
3. Set **CPU Limit** to the value above (either fractional CPU or milliCPU).
4. Set **Memory Limit (MiB)** using the recommended range above.
5. Under **Restart Policy**, choose **always** (unless you have a specific reason to pause restarts, in which case use **unless-stopped**).
6. Save and redeploy the service.

## Healthchecks for Auto-Restart
Add Dockerfile healthchecks so Coolify can restart containers that fail their probes.

### Backend Dockerfile snippet
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8001/health || exit 1
```

### tg-gateway Dockerfile snippet
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:7000/api/status || exit 1
```

For other gateways/services, reuse the same pattern but point the URL to the service's `/api/status` endpoint.
