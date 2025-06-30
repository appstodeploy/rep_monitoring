# 📡 Reportage Monitoring Tool

This is a Streamlit web app for monitoring backlinks (reportages) on publisher websites. It reads data from a private Google Sheet and analyzes each listed URL for the presence of expected backlinks and anchor texts. Ideal for SEO specialists, digital PR teams, and link-building analysts.

---

## ✨ Features

- ✅ Connects securely to a **private Google Sheet**
- 🔗 Checks for up to **3 backlinks per page**
- 🕵️‍♀️ Validates:
  - Anchor text accuracy
  - `rel` attribute (e.g. `nofollow`, `sponsored`)
  - HTTP status code
  - Canonical and robots meta tags
  - Page title
- 📥 Download results as CSV
- ☁️ Streamlit Cloud ready (uses `secrets.toml` for credentials)

---

## 🧰 Tech Stack

- Python
- [Streamlit](https://streamlit.io)
- [gspread](https://gspread.readthedocs.io)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Google Sheets API](https://developers.google.com/sheets/api)

---

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/reportage-monitoring-tool.git
cd reportage-monitoring-tool
```

### 2. Set up virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your credentials

Create a `.streamlit/secrets.toml` file and paste your **Google Service Account** credentials.

```
reportage-monitoring-tool/
├── app.py
└── .streamlit/
    └── secrets.toml
```

**Example `secrets.toml` content:**

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\\nMIIEv...\\n-----END PRIVATE KEY-----\\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "1234567890"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

⚠️ **Never commit `secrets.toml` to GitHub. Keep it secret!**

### 5. Run the app

```bash
streamlit run app.py
```

---

## 📊 Input Format (Google Sheet)

The input Google Sheet must contain the following columns:

- `Page URL`
- `TARGET PAGE 1`, `ANCHOR 1`
- `TARGET PAGE 2`, `ANCHOR 2`
- `TARGET PAGE 3`, `ANCHOR 3`

**Example:**

| Page URL                   | TARGET PAGE 1              | ANCHOR 1       | TARGET PAGE 2              | ANCHOR 2       |
|----------------------------|----------------------------|----------------|----------------------------|----------------|
| https://example.com/article | https://yourdomain.com/page1 | example anchor | https://yourdomain.com/page2 | second anchor  |

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and deploy your app.
3. In your app's **Settings > Secrets**, paste the content of your `secrets.toml`.

---

## 📃 License

MIT License. Free to use and modify.

---

## 🤝 Contributing

Suggestions and contributions are welcome!  
Feel free to open issues or pull requests.
