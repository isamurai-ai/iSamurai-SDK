# iSamurai Python SDK

The official Python client for the [iSamurai Face Swap API](https://isamur.ai).

## Installation

### From Source (Development)
If you have the source code:
```bash
git clone https://github.com/isamurai-ai/iSamurai-SDK.git
cd iSamurai-SDK
pip install -e .
```

### From PyPI (Coming Soon)
```bash
pip install isamurai
```

## Quick Start

```python
from isamurai import Isamurai

# Initialize
client = Isamurai(api_key="your_api_key_here")

# Check Credits
info = client.get_credits()
print(f"Credits: {info['credits']}")

# Submit Job
job_id = client.process_face_swap(
    source_path="me.jpg",
    target_path="movie.mp4",
    quality="1080p"
)

# Wait for Result
result = client.wait_for_job(job_id)
print(f"Video URL: {result['output_media_url']}")
```
