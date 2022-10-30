# lstore-put

Automatically publish packages to lStore

## Example workflow

**WARNING:** Do not enter any secrets in plain text! Add them as a env var in `settings/secrets/actions`.

```yml
name: Publish
on:
  push:
    branches:
      - main

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v3

      - name: Publish Package and create Tag and Releases
        uses: Commandcracker/lstore-put@v1
        with:
          username: ${{ secrets.LSTORE_USERNAME }}
          password: ${{ secrets.LSTORE_PASSWORD }}
          path: src
          title: example
```

## Inputs

| Input      | Description                     | Required | Default |
|------------|---------------------------------|----------|---------|
| `username` | `LevelOS username`              | `true`   |         |
| `password` | `Password for the LevelOS user` | `true`   |         |
| `path`     | `The path to the package`       | `true`   |         |
| `title`    | `The title of the package`      | `true`   |         |
