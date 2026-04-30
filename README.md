# QUVIAI Python SDK

Official Python SDK for the [QUVIAI](https://quvi.ai) AI image rendering API.
Zero external dependencies — pure Python 3.10+ stdlib.

## Installation

```bash
pip install quviai-python-sdk
```

## Quick Start

```python
from quviai import QuviClient

client = QuviClient(api_key="quvi_your_key_here")
# or: export QUVI_API_KEY=quvi_your_key_here

result = client.generate_from_image(
    "viewport_screenshot.png",
    h_angle=63,   # horizontal camera angle
    v_angle=29,   # vertical camera angle
    zoom=5.0,
)

with open("result.png", "wb") as f:
    f.write(client.download_result(result))
```

### Non-blocking (submit + poll separately)

```python
task_id = client.submit_image("screenshot.png", h_angle=90, v_angle=45, zoom=3.0)
# ... do other work ...
result = client.poll_task(task_id)
```

### Status callbacks

```python
def on_status(status):
    print(f"Position: {status.queue_position}, ETA: {status.eta_formatted}")

result = client.generate_from_image("shot.png", on_status=on_status)
```

## Error Handling

```python
from quviai import (
    AuthError,
    InsufficientCreditsError,
    ContentModerationError,
    TaskTimeoutError,
)

try:
    result = client.generate_from_image("shot.png")
except AuthError:
    print("Invalid API key")
except InsufficientCreditsError:
    print("Not enough credits")
except ContentModerationError as e:
    print(f"Blocked: {e.reason}")
except TaskTimeoutError:
    print("Render took too long")
```

## API Keys

Get your API key at [quvi.ai](https://quvi.ai).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
