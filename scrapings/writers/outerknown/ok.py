import json
import time
from playwright.sync_api import sync_playwright


def get_item_links(page, url):
    # go to url
    page.goto(url, wait_until="domcontentloaded")  # go to url
    #page.wait_for_selector("li.collection-grid__item")  # wait for content to load
    page.wait_for_selector('a.button.button--secondary[title="Load More"]')

    initial_count = int(page.locator('.collection-product-count').inner_text().split(' ')[1])
    print(initial_count)

    parsed = []
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

        # Get the new item count
        new_count = int(page.locator('.collection-product-count').inner_text().split(' ')[1])
        print("new count: ", new_count)

        # If the new count is the same as the initial count, we stop
        if new_count == initial_count:
            print("No new items loaded. All items are visible.")
            break

        # Update initial count for next iteration
        initial_count = new_count

    # Now extract product links from the loaded items
    
    product_elements = page.locator('li.collection-grid__item')

    # Loop through each product item and extract the link
    for product in product_elements.all():
        product_link = product.locator('a.card__inner')  # Adjusted selector to grab the product link
        if product_link:
            parsed.append(product_link.get_attribute('href'))

    
    print("Finished collecting links")
    print(len(parsed))
    return parsed



def get_descriptions(page, list_of_links, brand_name):
    items = []
    item_num = 0
    for cloth in list_of_links:
        item_num += 1
        link = cloth['url']
        link = f'https://wearpact.com{link}'
        print(item_num," ", link)
        try:
            page.goto(link)
            time.sleep(2) #wait for page to load completely to get sustainability info
            #page.wait_for_load_state("networkidle")
            title = page.locator('.product-title')
            item_name = title.inner_text()

            sustainability_info = get_sustain_info(page)
            image_gallery = get_img_urls(page)
            description_items = page.locator('.product-information-features ul li').all()
            description_text = " ".join([item.inner_text().strip() for item in description_items])
            price = get_price(item_name, page)
            cat = assign_cat(item_name)
            
            sustainability_info = list(sustainability_info)
            items.append({
                "brand": brand_name,
                "item name": item_name,
                "item description": description_text,
                "item sustainablibilty info": sustainability_info,
                "item gallery": image_gallery,
                "price": price,
                "category": cat
            })

        except Exception as e:
            print(f"Error scraping {cloth}: {e}")

    return items

def get_price(title, page):
    collective = ["pack", "bundle"]
    if any(word in title for word in collective):
        price = page.locator("div.product-price > div.dollar").first.inner_text()
    else:
        price = page.locator('.dollar.red').first.inner_text()
    
    if "MSRP" in price:
        price = price.partition('\n')[0]

    return price

def assign_cat(title):
    cat = ""
    types = {
            "top" : ["shirt", "hoodie", "tee", "sleeve", "top", "quarter zip", "polo", "neck"],
            "bottom" : ["pant", "short", "jogger", "bottom", "leg"],
            "under wear" : ["boxer", "brief", "under"],
            "misc" : ["socks"],
            }

    for key, val in types.items():
        for name in val:
            if name in title.lower():
                cat = key

    if cat == "":
        cat = "misc"

    return cat

def get_sustain_info(page):

    sustainability_info = set()
    categories = page.locator('.product-details-summary .text-center span').all()

    for category in categories:
        try:
            #time.sleep(2)
            title_element = category.locator('p.bold')
            value_element = category.locator('p:last-child')

            if title_element.count() > 0 and value_element.count() > 0:
                title = title_element.inner_text().replace("\n", ", ").strip()
                value = value_element.inner_text().strip()
                sustainability_info.add(f"{title}: {value}")
        except Exception as e:
            print(f"Skipping an entry due to error: {e}")


    return sustainability_info

def get_img_urls(page):

    images = page.locator('#product-images-wrapper img').all()

    image_sources = set()
    for img in images:
        src = img.get_attribute("src")
        if src and src.startswith("//"):
            src = "https:" + src  # Convert relative URLs to absolute
        image_sources.add(src)

    img_urls = list(image_sources)
    return img_urls


def main():

    url = "https://outerknown.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url,
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(extra_http_headers=headers)
        page = context.new_page()
        brand_name = "Outerknown"
        base_url = "https://www.outerknown.com/collections/mens?"

        result = get_item_links(page, base_url)
        report = get_descriptions(page, result, brand_name)

        browser.close()

    output_file = "pact.json"
    with open(output_file, "w") as file:
        json.dump(report, file, indent=4)

    print(f"Scraped data saved to {output_file}")
    #print(report)


main()
