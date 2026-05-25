You are reviewing a Terraform module against Trivy config-scan findings. For each finding, produce one section in this format:

```
### <finding ID> — <severity>

**What:** <one sentence>

**Patch:** ```hcl
<minimal HCL change>
```

**Why:** <one sentence rationale>
```

Skip findings that are duplicates or already addressed by the surrounding HCL. Output only those sections, in order of severity (CRITICAL first).

Trivy findings JSON:

```json
{{trivy_findings_json}}
```

Current HCL (may be empty):

```hcl
{{hcl_text}}
```
