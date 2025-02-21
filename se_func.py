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
            item_boxes = page.locator(".product-link").all()
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



def get_descriptions(page, list_of_links):
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
            
            sustainability_info = list(sustainability_info)
            items.append({
                "item name": item_name,
                "item description": description_text,
                "item sustainablibilty info": sustainability_info,
                "item gallery": image_gallery
            })

        except Exception as e:
            print(f"Error scraping {cloth}: {e}")

    return items


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
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        base_url = "https://wearpact.com/women/new"

        result = get_item_links(page, base_url)
        report = get_descriptions(page, result)

        browser.close()

    output_file = "pact.json"
    with open(output_file, "w") as file:
        json.dump(report, file, indent=4)

    print(f"Scraped data saved to {output_file}")
    #print(report)


main()
