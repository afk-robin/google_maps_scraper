from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import re

@dataclass
class Business:
    name: str=None
    phone_number: str=None
    email: str=None

@dataclass
class BusinessList:
    business_list: list [ Business ] = field (default_factory = list)
    save_at = 'output'
    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list),sep = "_")
    def save_to_excel (self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs (self.save_at)
        self.dataframe().to_excel (f"output/{filename}.xlsx", index=False)

def extract_email_from_website(browser, website_url):
    try:
        browser_context = browser.new_context()
        new_page = browser_context.new_page()
        if not website_url.startswith("http"):
            website_url = "http://" + website_url
        new_page.goto(website_url, timeout=20000)
        new_page.wait_for_timeout(5000)
 
        body_text = new_page.locator("body").inner_text(timeout = 3000)
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",body_text)
        new_page.close()
        browser_context.close()

        if emails:
            return emails[0]
        
    except Exception as e:
        print ( f"Error getting email from {website_url}:{e}")
        return None
    
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s" , "--search" ,type=str)
    parser.add_argument("-t" , "--total" ,type=int)
    args = parser.parse_args()
    
    if args.search:
        search_list =[args.search]
    else:
        search_list = []
        input_file_path = os.path.join(os.getcwd(),'input.txt')
        if os.path.exists(input_file_path):
            with open(input_file_path,'r') as file:
                search_list = file.readlines()
        if len(search_list) == 0:
            print('Error: You must pass -s "your search" or add to input.txt')
            sys.exit()

    total = args.total if args.total else 1_000_000

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)
        
        for search_for_index, search_for in enumerate(search_list):
            print(f"-----\n{search_for_index} - {search_for}".strip())
            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')
            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)

                current_count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()

                if current_count >= total:
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    if current_count == previously_counted:
                        listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                        print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                        break
                    else:
                        previously_counted = current_count
                        print(f"Currently Scraped: {current_count}")

            business_list = BusinessList()

            for listing in listings:
                try:
                    listing.click()
                    page.wait_for_timeout(5000)

                    name_xpath = '//h1[contains(@class,"DUwDvf")]'
                    phone_xpath = '//button[contains(@data-tooltip, "+") or contains(@aria-label, "Phone:")]'
                    website_xpath = '//a[contains(@data-tooltip, "Website") or contains(@aria-label, "Website")]'

                    business = Business()

                    if page.locator(name_xpath).count() > 0:
                        business.name = page.locator(name_xpath).all()[0].inner_text()
                    else:
                        business.name = ""

                    if page.locator(phone_xpath).count() > 0:
                        phone_text = page.locator(phone_xpath).all()[0].get_attribute("aria-label")
                        business.phone_number = phone_text.replace("Phone: ", "").strip()
                    else:
                        business.phone_number = ""

                    if page.locator(website_xpath).count() > 0:
                        website_link = page.locator(website_xpath).all()[0].get_attribute("href")
                        email_found = extract_email_from_website(browser, website_link)
                        business.email = email_found if email_found else ""
                    else:
                        business.email = ""

                    print(f"{business.name} | {business.phone_number} | {business.email}")
                    business_list.business_list.append(business)

                except Exception as e:
                    print(f'Error: {e}')
                page.wait_for_timeout(2000)

            safe_filename = "".join([c if c.isalnum() or c in (' ', '_') else '_' for c in search_for])
            safe_filename = safe_filename.replace(' ', '_')

            business_list.save_to_excel(f"google_maps_companies_{safe_filename}")
        browser.close()

if __name__ == "__main__":
    main()



#to run type , " python ggyou.py -s "colleges in Noida" -t 10 "

