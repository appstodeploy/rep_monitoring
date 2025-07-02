import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time
from urllib.parse import urljoin
import tldextract

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# --- Load Google Sheet ---
def load_sheet(creds_dict, sheet_url, tab_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).worksheet(tab_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data), sheet

# --- Analyze a Single URL ---
def analyze_url(row, index, root_domain, timeout):
    result = {
        f"Link and anchor status {index}": "",
        f"REL {index}": "",
    }
    target = row.get(f"TARGET PAGE {index}", "").strip()
    anchor = row.get(f"ANCHOR {index}", "").strip()
    page_url = row.get("Page URL", "").strip()

    if not target:
        return result

    try:
        resp = requests.get(page_url, timeout=timeout, headers=headers)
        result["STATUS CODE"] = resp.status_code

        if resp.status_code != 200:
            return result

        soup = BeautifulSoup(resp.text, "lxml")
        title = soup.title.string.strip() if soup.title else ""
        result["PAGE TITLE"] = title

        # Canonical
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.get("href"):
            canonical = canonical_tag["href"].strip()
            result["CANONICAL"] = "self canonical" if canonical == page_url else canonical
        else:
            result["CANONICAL"] = "not found"

        # Robots
        robots = soup.find("meta", attrs={"name": "robots"})
        result["ROBOTS"] = robots["content"] if robots else "not found"

        # Link Check
        found = False
        root_extracted = tldextract.extract(root_domain).registered_domain
        filtered_links = []
        filtered_anchors = []
        filtered_rels = []

        for a in soup.find_all("a", href=True):
            full_link = urljoin(page_url, a["href"])
            link_domain = tldextract.extract(full_link).registered_domain

            if link_domain == root_extracted:
                filtered_links.append(full_link)
                filtered_anchors.append(a.get_text(strip=True))
                rel = a.get("rel")
                filtered_rels.append(" ".join(rel) if rel else "none")

                # Check for target match
                if target in full_link and not found:
                    actual_anchor = a.get_text(strip=True)
                    rel_val = " ".join(rel) if rel else "none"
                    result[f"REL {index}"] = rel_val

                    if anchor:
                        if actual_anchor == anchor:
                            result[f"Link and anchor status {index}"] = "true"
                        else:
                            result[f"Link and anchor status {index}"] = f"anchor mismatch (found: {actual_anchor})"
                    else:
                        result[f"Link and anchor status {index}"] = "link found, no anchor provided"
                    found = True

        if not found:
            result[f"Link and anchor status {index}"] = "link not found"

        # Save all filtered links and anchors
        result["Links to root domain"] = ", ".join(filtered_links[:30])
        result["Anchors to root domain"] = ", ".join(filtered_anchors[:30])
        result["Rel attributes to root domain"] = ", ".join(filtered_rels[:30])

    except requests.exceptions.RequestException as e:
        result[f"Link and anchor status {index}"] = f"Request error: {e}"
        result["STATUS CODE"] = "error"

    return result

# --- Analyze All Rows ---
def process_rows(df, row_limit, root_domain, timeout):
    results = []
    for idx, row in df.iterrows():
        if idx >= row_limit:
            break
        base_result = {}
        for i in range(1, 4):
            res = analyze_url(row, i, root_domain,timeout)
            base_result.update(res)
        results.append(base_result)
    return results

# --- Streamlit App ---
def main():
    st.title("📡 Reportage Monitoring Tool")

    sheet_url = st.text_input("Paste your private Google Sheet URL:")
    tab_name = st.text_input("Sheet tab name (e.g., 'Sheet1'):")
    row_limit = st.number_input("How many rows to check?", min_value=1, value=10)
    root_domain = st.text_input("Enter root domain to filter anchors (e.g., example.com):")
    timeout = st.number_input("Set request timeout (seconds)", min_value=1, max_value=60, value=25)

    if st.button("▶ Run Monitoring") and sheet_url and tab_name and root_domain:
        with st.spinner("Loading Google Sheet..."):
            try:
                creds_dict = st.secrets["gcp_service_account"]
                df, sheet = load_sheet(creds_dict, sheet_url, tab_name)
                st.success("Sheet loaded. Starting inspection...")
            except Exception as e:
                st.error(f"❌ Error loading sheet: {e}")
                return

        df = df.fillna("")
        start = time.time()
        results = process_rows(df, row_limit, root_domain, timeout)
        elapsed = time.time() - start
        st.info(f"✅ Done! Checked {row_limit} rows in {elapsed:.2f} seconds.")

        for i, r in enumerate(results):
            for k, v in r.items():
                df.at[i, k] = v

        st.dataframe(df.head(row_limit))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download results as CSV", data=csv, file_name="reportage_monitoring_results.csv")

if __name__ == "__main__":
    main()
