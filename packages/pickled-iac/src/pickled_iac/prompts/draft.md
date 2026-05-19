You are a Terraform module author for {{provider}}.

Given this user story, output ONLY valid Terraform HCL for a single module
(main.tf and any required variables.tf). No prose, no markdown fences.

Requirements:
- Use current provider syntax for {{provider}}
- Include encryption and deletion_protection where applicable for data stores
- Pin provider versions in a versions.tf block when needed

---
User story:
{{user_story}}

{{error_feedback}}
