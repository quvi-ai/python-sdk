# QUVIAI Python SDK

Official Python SDK for the [QUVIAI](https://quvi.ai) AI rendering API.
Zero external dependencies — pure Python 3.10+ stdlib.

## Installation

```bash
pip install quviai
```

Or directly from source:

```bash
git clone https://github.com/quvi-ai/python-sdk.git
pip install -e python-sdk/
```

## Authentication

Log in with your QUVIAI account credentials:

```python
from quviai import QuviClient

# Email + password (tokens are stored on the returned client)
client = QuviClient.login("you@example.com", "password")

# Reuse saved tokens (e.g. from a previous session)
client = QuviClient.from_tokens(
    access_token="...",
    refresh_token="...",   # optional but recommended
)
```

Tokens are automatically refreshed on 401 responses. Check `client.access_token` after any call to persist an updated token.

## 3D Render (render-td)

```python
from pathlib import Path
from quviai import QuviClient

client = QuviClient.login("you@example.com", "password")

result = client.render_3d(
    prompt="modern glass office building surrounded by trees",
    style="Modern",
    render_type="exterior",   # exterior | interior | site
    day_time="day",            # day | night
    weather="sunny",           # sunny | cloudy | rainy | snowy | windy | foggy
    image=Path("viewport.png"),
)

with open("result.png", "wb") as f:
    f.write(client.download_result(result))
```

### Progress callbacks

```python
def on_status(status):
    print(f"Queue: {status.queue_position}  ETA: {status.eta_formatted}  {status.progress_percentage}%")

result = client.render_3d(prompt="...", image="viewport.png", on_status=on_status)
```

### Non-blocking: submit now, poll later

```python
task_id = client.submit_render_3d(prompt="...", image="viewport.png")
# ... do other work ...
result = client.poll_task(task_id)
```

## Text-to-Image

```python
result = client.generate_image(
    prompt="photorealistic forest cabin at dusk",
    style="Cinematic",
)
image_bytes = client.download_result(result)
```

## Canvas / Sketch

```python
result = client.generate_canvas(
    image=Path("sketch.png"),
    prompt="convert sketch to modern living room",
    is_sketch=True,
)
```

## Background Removal

```python
result = client.remove_background(image=Path("photo.jpg"))
```

## Account Info

```python
data = client.get_user_data()   # full profile dict
credits = client.get_credits()  # int, or -1 on failure
```

## Error Handling

```python
from quviai import (
    QuviClient,
    TokenExpiredError,
    InsufficientCreditsError,
    RateLimitError,
    ContentModerationError,
    TaskTimeoutError,
    TaskFailedError,
)

try:
    result = client.render_3d(prompt="...", image="viewport.png")
except TokenExpiredError:
    print("Session expired — log in again")
except InsufficientCreditsError:
    print("Not enough credits — top up at quvi.ai")
except RateLimitError:
    print("Too many concurrent requests — wait and retry")
except ContentModerationError as exc:
    print(f"Content blocked: {exc.reason} ({exc.category})")
except TaskFailedError as exc:
    print(f"Task {exc.task_id} failed: {exc}")
except TaskTimeoutError as exc:
    print(f"Timed out after {exc.timeout}s")
```

## Configuration

```python
client = QuviClient.from_tokens(
    access_token="...",
    base_url="https://quvi.ai",   # default
    timeout=120,                   # HTTP read timeout in seconds
    poll_interval=2.0,             # seconds between status polls
    poll_timeout=900.0,            # max total polling time in seconds
)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
