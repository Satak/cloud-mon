# CloudMon

Monitoring application designed to run as a GCP App Engine application. You can define your own services to be monitored.

## Authentication

Authentication is done against Google Firebase in backend with `pyrebase` and `firebase-admin` SDK libraries. So you need first create Firebase and add users there since there is no public registration functionality in this app.

## Datastore

All data is stored to Google's `Datastore` NoSQL database.

## Scheduled Monitoring

Create `cron.yaml` and deploy it to your app engine

`gcloud app deploy cron.yaml --project=<projectId>`

```yaml
cron:
- description: "Invoke monitoring"
  url: /api/invoke-monitor
  schedule: every 15 mins
```

## UI

![UI Main](/img/cloud_mon_ui.png)
![UI Form](/img/cloud_mon_ui_form.png)

## Dependencies

- Python libraries:
  - `flask`
  - `requests`
  - `fastjsonschema`
  - `google-cloud-datastore`
  - `pyrebase`
  - `firebase-admin`
- Access to some decryption API to decrypt passwords
- Environment variables:
  - `DECRYPTION_KEY`
  - `DECRYPTION_URL`
  - `NAMESPACE` (GCP datastore namespace)
  - `SENDER_EMAIL`
  - `SMTP_USERNAME`
  - `SMTP_PASSWORD`
  - `SMTP_SERVER`
  - `RECIPIENTS`
  - `FB_API_KEY`
  - `FB_AUTH_DOMAIN`
  - `FB_DB_URL`
  - `FB_PROJECT_ID`
  - `FB_STORAGE_BUCKET`
  - `FB_MESSAGE_SENDER_ID`
  - `SECRET` (`base64.b64encode(urandom(24)).decode()`)
  - `SLACK_URL`
  - `GOOGLE_APPLICATION_CREDENTIALS_FIREBASE`
  - `PRODUCTION` (boolean, for firebase auth)

## `app.yaml` Deployment file

`gcloud app deploy --project=<projectId>`

```yaml
runtime: python37
env_variables:
  DECRYPTION_KEY: <de/encryption key>
  DECRYPTION_URL: <url for cryptography service>
  SENDER_EMAIL: <sender email address>
  SMTP_USERNAME: <smtp username>
  SMTP_PASSWORD: <smtp password>
  SMTP_SERVER: <smtp server>
  RECIPIENTS: <comma separated string, receiver email address(es)>
  FB_API_KEY: <Firebase API_KEY>
  FB_AUTH_DOMAIN: <Firebase AUTH_DOMAIN>
  FB_DB_URL: <Firebase DB_URL>
  FB_PROJECT_ID: <Firebase PROJECT_ID>
  FB_MESSAGE_SENDER_ID: <Firebase MESSAGE_SENDER_ID>
  SECRET: <base64 encoded random byte array>
  SLACK_URL: <webhook url for your slack app>
  PRODUCTION: True
handlers:
- url: /static
  static_dir: static/
- url: /.*
  script: auto
```
