# Monitoring

`targets.json` contains public-code search queries. Add project-specific distinctive strings under `project_queries` only when they are useful provenance signals and do not expose secrets.

Example project query:

```json
{
  "name": "Example distinctive implementation phrase",
  "query": "\"a sufficiently distinctive source string\" language:Rust",
  "project": "example"
}
```

Search hits are leads, not proof of infringement. Review license scope, authorship, commit history, independent creation, exceptions, and any private grants before escalation.
