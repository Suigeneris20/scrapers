import json
import time
from playwright.sync_api import sync_playwright


def get_item_links(page, url):
    # go to url
    page.goto(url, timeout=60000)  # go to url
    page.wait_for_selector(".product-card__figure a", timeout=10000) # wait for content to load

    parsed = []
    try:
        product_links = page.eval_on_selector_all('.product-card__figure a', 'elements => elements.map(a => a.href)')
    
    except Exception as e:
        print(f"Error occured while collecting product links")
    print("Finished collecting links")
    print(product_links)
    return product_links



def get_descriptions(page, list_of_links):
    items = []
    item_num = 0
    for cloth in list_of_links:
        item_num += 1
        link = cloth
        #link = f'https://theclassictshirt.com/products{link}'
        print(item_num," ", link)
        try:
            page.goto(link, wait_until="load", timeout=60000)
            #time.sleep(2) #wait for page to load completely to get sustainability info
            #page.wait_for_selector('div.product-info__block-list')
            title = page.locator('h1.product-title')
            item_name = title.inner_text().strip()
            print(item_name)

            sustainability_info = get_sustain(page)
            image_gallery = get_img_urls(page)
            description_items = page.locator('div.product-info__block-item[data-block-type="text"]').nth(0).inner_text().strip()
            #description_text = " ".join([item.inner_text().strip() for item in description_items])
            
            sustainability_info = sustainability_info.strip()
            items.append({
                "brand": brand_name,
                "item name": item_name,
                "item description": description_items,
                "item sustainablibilty info": sustainability_info,
                "item gallery": image_gallery
            })

        except Exception as e:
            print(f"Error scraping {cloth}: {e}")

    return items

def get_sustain(page):
    text = "Sustainability information not found"
    try:
        sustainability_summary = page.locator("summary", has_text='Sustainability')
        if sustainability_summary.count() > 0:
            sustainability_summary.click()

        # Extract the whole sustainability content
        sustainability_content = page.locator("div.accordion__content:has-text('GOTS stands for Global Organic Textile Standard')")
        text = sustainability_content.text_content()

    except Exception as e:
        print(f"Failed to extract sustainability info: {e}")

    return text

def get_img_urls(page):

    images = page.locator('.product-gallery__media img')

    image_sources = set()
    for i in range(images.count()):
        src = images.nth(i).get_attribute('src')
        if src:
            # Prepend 'https:' if necessary, since Shopify sometimes omits it
            if src.startswith("//"):
                src = "https:" + src
            image_sources.add(src)

    img_urls = list(image_sources)
    return img_urls


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        brand_name = "Classic T-Shirt"
        base_url = "https://theclassictshirt.com/collections/men-all-product"

        result = get_item_links(page, base_url)
        report = get_descriptions(page, result, brand_name)

        browser.close()

    output_file = "classicT.json"
    with open(output_file, "w") as file:
        json.dump(report, file, indent=4)

    print(f"Scraped data saved to {output_file}")
    #print(report)


main()
