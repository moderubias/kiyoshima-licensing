# Kiyoshima Open profile

Kiyoshima Open is a profile and machine-readable protocol layer, not a renamed
software license. Use a standard controlling SPDX expression such as `MIT`,
`Apache-2.0`, or `MIT OR Apache-2.0`.

Example:

```bash
klicense init-project . --profile open --open-license Apache-2.0 \
  --name YourProject --repository https://github.com/owner/repo \
  --holder "Copyright Holder"
```


By default the CLI writes only the files needed for the selected expression.
Use `--reuse`, `--notice`, or `--readme-snippet PATH` only when those additional
artifacts are wanted.
