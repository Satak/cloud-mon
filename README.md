# CloudMon

Monitoring application designed to run as a GCP App Engine application. You can define your own services to be monitored. Basic authentication.

## UI

![UI Main](/img/cloud_mon_ui.png)
![UI Form](/img/cloud_mon_ui_form.png)

## Dependencies

- Python libraries:
  - `flask`
  - `Flask-BasicAuth`
  - `requests`
  - `fastjsonschema`
  - `google-cloud-datastore`
- Access to some decryption API to decrypt passwords
- Environment variables:
  - `DECRYPTION_KEY`
  - `DECRYPTION_URL`
  - `BASIC_AUTH_USERNAME`
  - `BASIC_AUTH_PASSWORD`
  - `NAMESPACE` (GCP datastore namespace)
  - `SENDER_EMAIL`
  - `SMTP_USERNAME`
  - `SMTP_PASSWORD`
  - `SMTP_SERVER`
  - `TO_EMAIL`

## `app.yaml` Deployment file

`gcloud app deploy --project=<projectId>`

```yaml
runtime: python37
env_variables:
  DECRYPTION_KEY: <de/encryption key>
  DECRYPTION_URL: <url for cryptography service>
  BASIC_AUTH_USERNAME: <username>
  BASIC_AUTH_PASSWORD: <strong password>
  SENDER_EMAIL: <sender email address>
  SMTP_USERNAME: <smtp username>
  SMTP_PASSWORD: <smtp password>
  SMTP_SERVER: <smtp server>
  TO_EMAIL: <receiver email address>
handlers:
- url: /static
  static_dir: static/
- url: /.*
  script: auto
```
