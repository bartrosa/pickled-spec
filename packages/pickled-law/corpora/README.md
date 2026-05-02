# Corpora

Each subdirectory holds machine-readable YAML corpora for one
regulation or standard.

## Layout

```
corpora/
├── hipaa/
│   └── 164_312.yaml      # 45 CFR §164.312 Technical Safeguards
└── <future>/
```

## Authoring rules

1. **Canonical text is verbatim.** Copy the regulatory text exactly
   from the authoritative source. Do not paraphrase or abridge. The
   `text` field in each rule is what drift detection (v0.4) compares
   against.
2. **One file per coherent unit.** A "coherent unit" is whatever a
   regulator publishes as a single section, annex, or article group.
   Splitting too fine creates merge headaches; combining too coarse
   loses traceability granularity.
3. **`source_version` matters.** Pin to the amendment date or
   official version string. Future drift detection compares
   `source_version` to detect outdated traces.
4. **Public domain text only.** US federal law and EU regulations are
   not under copyright; commercial standards (ISO/IEC) are. For
   commercial standards, ship a structural skeleton with rule IDs and
   titles only; users provide their own licensed text via overlay.

## Adding a corpus

1. Create `corpora/<short-name>/<file>.yaml`.
2. Validate with `pickled-law validate <path>` (PR-15 ships this).
3. Add to `BUILTIN_CORPORA` in `src/pickled_law/builtin.py`.
4. Add a load test in `tests/test_<short-name>_corpus.py`.
