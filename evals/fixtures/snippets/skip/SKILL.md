---
name: skip
description: Fixture skill with one runnable snippet and one skipped snippet, used by the snippet runner self-test.
---
# Skipped block

```python
print("this block runs")
```

```python
# qskill: skip
print("this block needs credentials and must never run")
```
