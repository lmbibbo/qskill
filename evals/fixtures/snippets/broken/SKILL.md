---
name: broken
description: Fixture skill with a failing snippet, used by the snippet runner self-test to verify the failure path.
---
# Broken snippets

```python
value = 1 + 1
raise RuntimeError("deliberate failure for the snippet runner self-test")
```
