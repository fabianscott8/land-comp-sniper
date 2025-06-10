from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# Function to scrape Zillow for land comps
def scrape_zillow_comps(address_or_zip):
    # Set up Chrome options for headless Browse (runs in background)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox") # Required for some environments (like Render)
    chrome_options.add_argument("--disable-dev-shm-usage") # Required for some environments (like Render)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # User-Agent to mimic a real browser

    # Path to chromedriver (webdriver_manager will handle this)
    # On Render, the PATH for Chrome will be set by the buildpack
    service = Service() # webdriver_manager handles finding the chromedriver

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Construct the Zillow URL for land comps
    # This is a simplified URL construction and might need adjustment for specific searches
    # For a real-world app, you'd want to be more precise with filters (e.g., lot size, sold date)
    # Zillow's URL structure is complex, so a direct search or advanced filtering might be needed.
    # For now, we'll aim for a broad search and filter later.
    search_url = f"https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isManufactured%22%3A%7B%22value%22%3Afalse%7D%2C%22isMultiFamily%22%3A%7B%22value%22%3Afalse%7D%2C%22isCondo%22%3A%7B%22value%22%3Afalse%7D%2C%22isLotLand%22%3A%7B%22value%22%3Atrue%7D%2C%22isTownhouse%22%3A%7B%22value%22%3Afalse%7D%2C%22isApartment%22%3A%7B%22value%22%3Afalse%7D%2C%22isHome%22%3A%7B%22value%22%3Atrue%7D%2C%22isSoldWithHome%22%3A%7B%22value%22%3Afalse%7D%2C%22isAuction%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleByAgent%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleByOwner%22%3A%7B%22value%22%3Afalse%7D%2C%22isNewConstruction%22%3A%7B%22value%22%3Afalse%7D%2C%22isComingSoon%22%3A%7B%22value%22%3Afalse%7D%2C%22isPreForeclosure%22%3A%7B%22value%22%3Afalse%7D%2C%22isBankOwned%22%3A%7B%22value%22%3Afalse%7D%2C%22isForRent%22%3A%7B%22value%22%3Afalse%7D%2C%22isForSaleForeclosure%22%3A%7B%22value%22%3Afalse%7D%2C%22isAllHomes%22%3A%7B%22value%22%3Afalse%7D%2C%22sort%22%3A%7B%22value%22%3A%22days%22%7D%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-77.1%2C%22east%22%3A-76.5%2C%22south%22%3A38.5%2C%22north%22%3A39.0%7D%2C%22isMapVisible%22%3Atrue%2C%22regionSelection%22%3A%5B%7B%22regionType%22%3A6%2C%22lat%22%3A38.7%2C%22lon%22%3A-76.8%2C%22radius%22%3A%2210mi%22%7D%5D%2C%22zoom%22%3A9%2C%22isListVisible%22%3Atrue%7D"

    # Replace with a more dynamic way to generate Zillow URLs based on address/zip
    # For your specific addresses, you'd typically go to Zillow, search for the address,
    # then apply the "Lots/Land" filter and "Sold" filter, and copy that URL.
    # We will use a placeholder for now for demonstration and address it in the next iteration.

    # Example: If you search for "Waldorf, MD" and filter for "Lots/Land", "Sold":
    # The URL might look like: https://www.zillow.com/waldorf-md/sold/lots_land/
    # We'll need to parameterize this. For now, let's use a more general search approach.

    try:
        driver.get(f"https://www.zillow.com/homes/for_sale/{address_or_zip}/")
        time.sleep(3) # Give some time for the page to load

        # Apply "Lots/Land" filter if available in the initial search results
        # This part is highly dependent on Zillow's current UI.
        # It's better to construct the URL with filters pre-applied if possible.
        # For simplicity, let's assume we're already on a page that can show land listings.
        # We need to click "Sold" first, then "Lot/Land"
        
        # Click on "For Sale" dropdown to reveal "Sold" option
        try:
            for_sale_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "category-dropdown-icon"))
            )
            for_sale_button.click()
            time.sleep(1) # wait for dropdown to appear

            sold_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sold')]"))
            )
            sold_option.click()
            time.sleep(3) # Wait for results to update after selecting Sold

            # Now, apply the "Lots/Land" filter
            # This XPath might need adjustment if Zillow's UI changes
            lot_land_filter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Lot/Land filter']"))
            )
            lot_land_filter_button.click()
            time.sleep(3) # Wait for results to update after selecting Lot/Land

        except Exception as e:
            print(f"Could not apply filters, proceeding with general search: {e}")
            # If filters can't be clicked, we might rely on the initial search results
            # or try a different approach to construct the URL with filters.


        # Extract data
        comps = []
        # Zillow often uses specific classes for listings. These XPATHS are examples and may need adjustment.
        # You'll need to inspect Zillow's page source for the most up-to-date element selectors.
        
        # Look for property cards
        # Example selector for a list of homes/properties. Zillow's structure changes often.
        # You'll likely find elements like <li class="StyledPropertyCardDataArea-c11n-8-84-3__sc-ro2x2b-0">
        
        # The following XPATHs are illustrative and likely need to be updated by inspecting the live Zillow page
        property_cards = driver.find_elements(By.XPATH, "//div[@class='StyledPropertyCardDataArea-c11n-8-84-3__sc-ro2x2b-0']")
        if not property_cards: # Try another common pattern
             property_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'property-card-data')]")

        print(f"Found {len(property_cards)} property cards.")

        for card in property_cards[:5]: # Limit to first few for quick testing
            try:
                address_elem = card.find_element(By.CSS_SELECTOR, 'address')
                address = address_elem.text if address_elem else "N/A"

                price_elem = card.find_element(By.CSS_SELECTOR, '.PropertyCardWrapper__StyledPrice-c11n-8-84-3__sc-1s47b5n-0')
                price = price_elem.text if price_elem else "N/A"
                price = float(price.replace('$', '').replace(',', '').strip()) if isinstance(price, str) and price != "N/A" else 0

                # Look for lot size (acres/sqft) - this is often tricky on Zillow
                # It might be in a span with text like "0.5 acres" or "21,780 sqft"
                lot_size_elem = card.find_element(By.XPATH, ".//span[contains(text(), 'acres')]") # More specific
                if not lot_size_elem: # Try a more general search for lot size info
                    lot_size_elem = card.find_element(By.XPATH, ".//li[contains(text(), 'lot size') or contains(text(), 'acres') or contains(text(), 'sqft')]")

                lot_size_text = lot_size_elem.text if lot_size_elem else "N/A"
                acres = 0.0
                if 'acres' in lot_size_text.lower():
                    try:
                        acres = float(lot_size_text.lower().replace('acres', '').strip())
                    except ValueError:
                        pass
                elif 'sqft' in lot_size_text.lower():
                    try:
                        sqft = float(lot_size_text.lower().replace('sqft', '').replace(',', '').strip())
                        acres = sqft / 43560  # Convert sqft to acres
                    except ValueError:
                        pass
                
                # Sold Date is also tricky. It might be in a small text element.
                # Example: "Sold X days ago" or "Sold on MM/DD/YYYY"
                sold_date_elem = card.find_element(By.XPATH, ".//div[contains(text(), 'Sold')]") # Look for text containing "Sold"
                sold_date = sold_date_elem.text if sold_date_elem else "N/A"


                if price > 0 and acres > 0: # Only add valid comps
                    comps.append({
                        "Address": address,
                        "Acres": acres,
                        "Sold Price": price,
                        "Sold Date": sold_date,
                        "Price per Acre": round(price / acres, 2)
                    })
            except Exception as e:
                print(f"Error parsing comp card: {e}")
                continue
    finally:
        driver.quit()
    return comps

@app.route('/', methods=['GET', 'POST'])
def home():
    comps = []
    target_offer_low = target_offer_high = profit_target = avg_price_per_acre = 0
    message = "" # To display any messages to the user

    if request.method == 'POST':
        address = request.form.get('address')
        
        # Try to scrape Zillow data
        try:
            comps = scrape_zillow_comps(address)
            if comps:
                # Filter comps for relevance (e.g., within 6-12 months, similar size, etc.)
                # This is a place where you'd add more sophisticated filtering.
                
                valid_comps = [c for c in comps if c['Price per Acre'] > 0]
                if valid_comps:
                    avg_price_per_acre = sum([c['Price per Acre'] for c in valid_comps]) / len(valid_comps)
                    target_offer_low = round(avg_price_per_acre * 0.30, 2)
                    target_offer_high = round(avg_price_per_acre * 0.45, 2)
                    profit_target = 7000
                    message = f"Found {len(valid_comps)} relevant comps."
                else:
                    message = "No valid comps found after scraping and initial filtering. Try a different address or broaden criteria."
            else:
                message = "No comps found for the given address/ZIP on Zillow. This might be due to no results, or scraping issues."
        except Exception as e:
            message = f"Error during scraping: {e}. Zillow's anti-bot measures might be active, or elements have changed. Try again later or adjust parameters."
            print(f"Scraping error: {e}")

    return render_template('index.html', comps=comps,
                           target_offer_low=target_offer_low,
                           target_offer_high=target_offer_high,
                           avg_price_per_acre=round(avg_price_per_acre, 2),
                           profit_target=profit_target,
                           message=message) # Pass message to template

@app.route('/download', methods=['POST'])
def download():
    # Retrieve data from session or pass it from the form submission
    # For now, let's assume `comps` can be recreated or passed.
    # A more robust solution would involve storing comps in a session or database.
    # For this example, we'll need to re-scrape or get the data from the request.
    # Let's simplify and make it download the currently displayed comps (if any)
    # This needs to be improved to actually get the 'comps' data that was generated for the current view.
    # As a workaround, we'll pass the `comps` data via a hidden input or session.
    
    # For simplicity, we'll pass data via a form post (hidden field) which is not ideal for large data,
    # but serves the purpose for this example.
    
    # This part needs refinement. We'll use a placeholder.
    # In a real app, you'd store the 'comps' in a session or query parameters to download
    
    # For now, the download button will only download the *last scraped* (or mocked) data.
    # To properly download, the `comps` data needs to be accessible here.
    # Let's assume `request.form.get('comps_json')` passes it.
    
    # Re-simulating for download for now, or you can add a hidden field in index.html to pass comps_json
    comps_data = request.form.get('comps_json')
    if comps_data:
        comps_df = pd.read_json(comps_data)
    else:
        # Fallback if no JSON is passed, this should ideally not happen if data is passed
        return "No data to download. Please generate comps first.", 400

    output_file = "Land_Comp_Analysis.xlsx"
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        comps_df.to_excel(writer, sheet_name='Land Comps', index=False)
    
    return send_file(output_file, as_attachment=True, download_name=output_file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
