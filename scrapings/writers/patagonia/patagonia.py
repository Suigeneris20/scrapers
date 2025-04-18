import json
import time
from playwright.sync_api import sync_playwright


def get_item_links(page, url):
    # go to url
    page.goto(url)  # go to url
    #page.wait_for_selector("div[data-alpha=Indigo Dyed Light Blue Men's Organic Crew Tee]")  # wait for content to load

    parsed = []
    try:
        while True:
            item_boxes = page.query_selector(".product-tile__image-wrap .product-tile__image-container .product-tile__cover.d-block > a")
            print(item_boxes)
            href = link_element.get_attribute('href')
            print(href)
            for box in item_boxes:
                parsed.append({
                    "url": box.get_attribute("href"),
        # tags are not always present:
        #"tags": box.query_selector(".tw-tag").inner_text() if box.query_selector(".tw-tag") else None,
                })

            next_button = page.locator("//a[contains(@class, 'paginate_next')]").get_attribute("href")
            if next_button:
                next_url = f'https://wearpact.com{next_button}'
                page.goto(next_url)
                #next_button.click() #can append to link to get correct page link if "click" doesnt work
                #time.sleep(5) #Add wait time to allow next page load if necessary
            else:
                break
    
    except Exception as e:
        print(f"Error occured while collecting product links")
    print("Finished collecting links")
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

    url = "https://patagonia.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url,
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(extra_http_headers=headers)
        page = context.new_page()
        brand_name = "Patagonia"
        base_url = "https://www.patagonia.com/shop/mens"

        result = get_item_links(page, base_url)
        report = get_descriptions(page, result, brand_name)

        browser.close()

    output_file = "pact.json"
    with open(output_file, "w") as file:
        json.dump(report, file, indent=4)

    print(f"Scraped data saved to {output_file}")
    #print(report)


main()
