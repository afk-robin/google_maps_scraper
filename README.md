Google Maps Business Scraper (Python + Playwright)
This is a Python project to scrape business information from Google Maps.
It uses **Playwright** to automate Google Maps and extract:
- Name
- Phone Number
- Email Address (from website)

The results are saved into a **Excel file (.xlsx)**.

--How to Use

Install dependencies
pip install playwright pandas

Install Playwright browsers
python -m playwright install

Run the scraper
python ggyou.py -s "your search term" -t no_of_searches

How It Works
Open Google Maps:
The script first opens [Google Maps](https://www.google.com/maps) in a Chromium browser window.
Enter Search Term:
It enters your search term (example: `"companies in Gurgaon"`) into the search bar, just like a human would type.
Load Business Listings:
It scrolls the left-side panel in Google Maps , this loads more and more businesses.
You can tell it how many businesses to scrape with:
python ggyou.py -s "your search" -t 50
