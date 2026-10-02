# Monitoring

`targets.json` contains public-code search queries. Add project-specific distinctive strings under `project_queries` only when they are useful provenance signals and do not expose secrets.

Example:

```json
{
  "name": "Distinctive implementation phrase",
  "query": "\"a sufficiently distinctive source string\" language:Rust",
  "project": "example"
}
```

Search hits are leads, not proof of infringement. The monitor classifies repositories present in `registry/projects.json` or `registry/adopters.json` as known. Unknown results still require human review of license scope, authorship, commit history, independent creation, exceptions, and private grants before escalation.
