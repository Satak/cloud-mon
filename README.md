# CloudMon

Monitors URLs defined in the `data.yaml`. This is a work in progress project.

## To Do

- data to GCP datastore
- flask wrapping
- UI

## Dependencies

- `requests` library
- `yaml` library
- Access to some decryption API to decrypt passwords
  - `DECRYPTION_KEY` environment variable
  - `DECRYPTION_URL` environment variable

## `data.yaml` file

`data.yaml` file is expected to be under the `data` folder.

### Structure

```text
.
├── readme.md
├── data
│   └── data.yaml
└── src
    ├── conf.py
    ├── main.py
    └── monitor.py
```

### File

Each monitor is defined under their unique keys. Eventually this data is stored in the GCP datastore.

```yaml
monitors:
  name1:
    name: name1
    base_url: "https://some-url"
    login_path: "/api/v1/login"
    monitor_path: "/api/v1/some-route"
    username: username
    password: "encryptedPassword=="
  name2:
    name: name2
    ...
```

## Architecture

This is the implementation high level plan

![Architecure](/img/webmon.png)
