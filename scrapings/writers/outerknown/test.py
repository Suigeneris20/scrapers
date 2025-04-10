from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time

def scrape_all_items():
    url = "https://outerknown.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url,
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Launch browser
        context = browser.new_context(extra_http_headers=headers)
        page = context.new_page()

        stealth_sync(page)

        # Navigate to the page
        page.goto('https://www.outerknown.com/collections/mens', wait_until="domcontentloaded")

        # Wait until the "Load More" button is visible
        page.wait_for_selector('a.button.button--secondary[title="Load More"]', timeout=60000)

        # Get initial item count

        while True:
            # Wait for the "Load More" button to be visible
            load_more_button = page.locator('a.button.button--secondary[title="Load More"]')

            # Wait until the button is clickable
            #load_more_button.wait_for(state="attached", timeout=60000)
            load_more_button.wait_for(state="visible", timeout=60000)
            

            # If the button is not visible, all items are loaded
            if not load_more_button.is_visible() or not load_more_button.is_enabled():
                print("All items are loaded.")
                break

             # Handle overlay issue (iframe or modal that intercepts clicks)
            try:
                # Check if overlay exists and wait for it to disappear
                overlay = page.locator('#attentive_overlay')
                if overlay.is_visible():
                    print("Removing #attentive_overlay...")
                    page.evaluate("document.getElementById('attentive_overlay')?.remove()")
                    overlay.wait_for(state="detached", timeout=60000)

            except: pass

                    #print("Waiting for overlay to disappear...")
                    #overlay.wait_for(state="detached", timeout=60000)

            try:
                creative = page.locator("#attentive_creative")
                if creative.is_visible():
                    time.sleep(3)
                    print("Removing #attentive_creative iframe...")
                    page.evaluate("document.getElementById('attentive_creative')?.remove()")
                    creative.wait_for(state="detached", timeout=60000)

            except Exception as e:
                print(f"No overlay detected: {e}")

            # Click the "Load More" button
            load_more_button.scroll_into_view_if_needed()
            load_more_button.click()

            # Wait for the new content to load
            page.wait_for_selector('.collection-product-count')

            '''
            # Get the new item count
            new_count = int(page.locator('.collection-product-count').inner_text().split(' ')[1])
            print("new count: ", new_count)

            # If the new count is the same as the initial count, we stop
            if new_count == initial_count:
                print("No new items loaded. All items are visible.")
                break

            # Update initial count for next iteration
            initial_count = new_count
            '''
            count_text = page.locator('.collection-product-count').inner_text()
            showing_now = int(count_text.split(" ")[1])
            total_items = int(count_text.split(" ")[-1])
            print(f"Loaded {showing_now} of {total_items} items")

            if showing_now >= total_items:
                break

        # Now extract product links from the loaded items
        product_links = []
        product_elements = page.locator('li.collection-grid__item')

        # Loop through each product item and extract the link
        for product in product_elements.all():
            product_link = product.locator('a.card__inner')  # Adjusted selector to grab the product link
            if product_link:
                product_links.append(product_link.get_attribute('href'))

        # Print all product links
        print("Extracted Product Links:")
        print(len(product_links))
        for link in product_links:
            print(link)

        # Close the browser after scraping
        browser.close()

if __name__ == "__main__":
    scrape_all_items()

