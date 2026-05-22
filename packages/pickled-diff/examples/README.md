# pickled-diff examples

Two tiny scripts demonstrate a passing differential check when both implementations
behave the same on a small input corpus.

## Corpus

Save as `corpus.json` in this directory:

```json
[
  {"name": "zero", "payload": "0"},
  {"name": "one", "payload": "1"},
  {"name": "ten", "payload": "10"}
]
```

## CLI

From the monorepo root (adjust paths to your clone):

```bash
uv run pickled-diff verify \
  --oracle "python packages/pickled-diff/examples/trivial_oracle.py" \
  --candidate "python packages/pickled-diff/examples/trivial_candidate.py" \
  --corpus packages/pickled-diff/examples/corpus.json
```

Expect verdict `pass` and exit code 0.

Change `trivial_candidate.py` to print `int(raw) * 3` to see a `warn` or `fail` verdict.
