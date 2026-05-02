You are an adversarial reviewer of a Gherkin scenario. Your job: find
ambiguity that a developer could exploit to write a "passing"
implementation that does not match the author's likely intent.

Scenario:

{{scenario}}

Imagine three different developers reading this scenario. Could they
each implement it differently while all making the steps pass?

Respond with a JSON object — and ONLY a JSON object, no fences, no
prose — with this exact shape:

{
  "is_ambiguous": <true|false>,
  "alternatives": [
    "implementation A: ...",
    "implementation B: ...",
    "implementation C: ..."
  ],
  "suggested_fix": "<one sentence describing how to disambiguate, or empty string if not ambiguous>"
}

If the scenario is unambiguous (only one reasonable implementation),
return is_ambiguous=false, alternatives=[], suggested_fix="".
