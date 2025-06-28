import streamlit as st
import pandas as pd
import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class RealWebScraper:
    def __init__(self):
        self.driver = None

    def _init_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    def scrape_urls(self, url_list, keyword, country):
        self._init_driver()
        leads = []

        for url in url_list:
            try:
                self.driver.get(url)
                time.sleep(2)
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                emails = list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", soup.get_text())))
                phones = list(set(re.findall(r"\+?\d[\d\s()-]{8,}\d", soup.get_text())))

                leads.append({
                    "name": url.split("//")[-1].split("/")[0],
                    "website": url,
                    "email": emails[0] if emails else None,
                    "phone": phones[0] if phones else None,
                    "country": country,
                    "industry": keyword
                })
            except Exception as e:
                print("❌ Error scraping", url, e)
                continue

        self.driver.quit()
        return leads

st.set_page_config(page_title="Real Lead Finder", page_icon="🔍")
st.title("🕵️‍♂️ Real Business Lead Finder")
st.subheader("🔍 Scrape contact info from real websites")

with st.form("lead_scraper_form"):
    st.markdown("✍️ **Enter details and URLs below:**")
    name = st.text_input("Name (optional)")
    contact = st.text_input("Contact (optional)")
    email = st.text_input("Email (optional)")
    country = st.text_input("Country (e.g., India, USA)")
domain = st.text_input("Domain / Industry (e.g., Software, Restaurants)")
urls_text = st.text_area(
    "Enter one URL per line (starting with http or https)",
    value="https://www.zoho.com\nhttps://www.freshworks.com\nhttps://www.tcs.com"
)
submitted = st.form_submit_button("🔍 Start Scraping")

if submitted:
    url_list = [u.strip() for u in urls_text.strip().splitlines() if u.strip().startswith("http")]

    if not url_list:
        st.warning("⚠️ Please enter at least one valid URL starting with http or https.")
    else:
        st.info("⏳ Scraping websites... Please wait. This may take a few seconds.")
        scraper = RealWebScraper()
        leads = scraper.scrape_urls(url_list, domain, country)

        if leads:
            df = pd.DataFrame(leads)
            st.success(f"✅ Found {len(df)} leads from given URLs")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Leads CSV", csv, "real_leads.csv", "text/csv")
        else:
            st.warning("⚠️ No contact info found on the given websites.")