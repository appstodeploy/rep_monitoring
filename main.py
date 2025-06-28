import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tldextract
from concurrent.futures import ThreadPoolExecutor, as_completed


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# ---------- Helpers ----------
def is_indexable(soup):
    tag = soup.find("meta", attrs={"name": "robots"})
    return not (tag and "noindex" in tag.get("content", "").lower())

def analyze_url(url, target_domain):
    data = {
        "URL": url,
        "Status Code": None,
        "Contains Target Link": False,
        "Target URLs": [],
        "Anchor Texts": [],
        "Rel Attributes": [],
        "Indexable": None,
        "Canonical": None,
        "Canonical Self": None,
        "Page Title": None,
        "Error": None
    }

    try:
        res = requests.get(url, timeout=60, headers=headers)
        data["Status Code"] = res.status_code
        if res.status_code != 200:
            return data

        soup = BeautifulSoup(res.text, "html.parser")
        data["Page Title"] = soup.title.string.strip() if soup.title else None
        data["Indexable"] = is_indexable(soup)

        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.get("href"):
            canonical_href = canonical_tag["href"]
            data["Canonical"] = canonical_href
            data["Canonical Self"] = canonical_href.rstrip("/") == url.rstrip("/")

        for a in soup.find_all("a", href=True):
            full_link = urljoin(url, a["href"])
            if target_domain in full_link:
                data["Contains Target Link"] = True
                data["Target URLs"].append(full_link)
                data["Anchor Texts"].append(a.get_text(strip=True))
                data["Rel Attributes"].append(", ".join(a.get("rel", [])) if a.get("rel") else "")

    except Exception as e:
        data["Error"] = str(e)

    return data

def process_urls_concurrently(urls, target_domain, max_threads=30):
    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(analyze_url, url, target_domain): url for url in urls}
        futures = as_completed(future_to_url)
        for future in stqdm(futures, total=len(urls), desc="Processing URLs"):
            result = future.result()
            results.append(result)
    return results

# ---------- Streamlit UI ----------
def main():
    st.set_page_config(page_title="Reportage Monitoring Tool", layout="wide")
    st.title("📊 Reportage Monitoring Tool")
    st.markdown("Upload a CSV of backlink URLs (one per line, no header) and monitor link presence, anchor text, indexing, and more.")

    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    domain_input = st.text_input("Enter your target domain (e.g. `example.com`)")

    if uploaded_file and domain_input:
        urls = pd.read_csv(uploaded_file, header=None)[0].dropna().tolist()
        target_domain = tldextract.extract(domain_input).registered_domain

        st.info(f"Total URLs to analyze: {len(urls)}")
        if st.button("🚀 Start Monitoring"):
            with st.spinner("Processing..."):
                results = process_urls_concurrently(urls, target_domain)
                df_result = pd.DataFrame(results)

            st.success("✅ Monitoring complete!")
            st.dataframe(df_result)
            csv = df_result.to_csv(index=False)
            st.download_button("📥 Download Full Report", csv, "reportage_monitoring_report.csv", "text/csv")

# ---------- Progress Wrapper ----------
def stqdm(iterator, total, desc=""):
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, item in enumerate(iterator):
        progress_bar.progress((i + 1) / total)
        status_text.text(f"{desc} {i+1}/{total}")
        yield item

    progress_bar.empty()
    status_text.empty()

if __name__ == "__main__":
    main()