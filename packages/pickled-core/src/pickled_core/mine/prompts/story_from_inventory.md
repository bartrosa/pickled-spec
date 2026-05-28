You are drafting verification intent for a mined software surface.

Surface: {{surface_name}} ({{surface_kind}})
Package: {{package_name}}

{{code_grounding_block}}

Arguments / parameters:
{{arguments}}

Related gates in the target:
{{related_gates}}

Related ADRs (pre-filtered for this surface):
{{related_adrs}}

Return exactly these delimited blocks (no extra markdown headings inside the blocks):

---CONTEXT---
<who uses this surface and why>

---BEHAVIOR---
<observable behavior — the contract a caller relies on>

---VERIFY---
<testable assertion bullets, each starting with "- ">

---DRIFT---
<empty if docstring and code agree; otherwise one bullet per discrepancy>
