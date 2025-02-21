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
            item_boxes = page.locator("//div[contains(@class,'is_infinite')]/div[@data-alpha]")
            for box in item_boxes.element_handles():
                parsed.append({
                    "title": box.query_selector("h3").inner_text(),
                    "url": box.query_selector("a").get_attribute("href"),
        # tags are not always present:
        #"tags": box.query_selector(".tw-tag").inner_text() if box.query_selector(".tw-tag") else None,
                })

            next_button = page.locator("//a[contains(@class, 'paginate_next')]").get_attribute("href")
            if next_button:
                next_url = f'https://harvestandmill.com{next_button}'
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
        link = f'https://harvestandmill.com{link}'
        print(item_num," ", link)
        try:
            page.goto(link)
            time.sleep(2) #wait for page to load completely to get sustainability info
            #page.wait_for_load_state("networkidle")
            print(page)
            sustainability_info = get_sustain_info(page)
            print("after sus: ", page)
            image_gallery = get_img_urls(page)
            desc = page.query_selector(".product__section-details__inner--product_description .rte")
            desc_info = desc.inner_text()
            sustainability_info = list(sustainability_info)
            items.append({
                "item name": cloth['title'],
                "item description": desc_info,
                "item sustainablibilty info": sustainability_info,
                "item gallery": image_gallery
            })

        except Exception as e:
            print(f"Error scraping {cloth}: {e}")

    return items


def get_sustain_info(page):
    
    
    sustainability_info = set()
    #page.goto(link)
    metrics = page.locator(".metric")

    for metric in metrics.element_handles():
        value = metric.query_selector(".metric__value").inner_text()
        unit = metric.query_selector(".metric__unit").inner_text()
        description = metric.query_selector(".metric__description").inner_text()

        print(f'{value} {unit} {description}')
        sustainability_info.add(f'{value} {unit} {description}')

    return sustainability_info

def get_img_urls(page):

    img_elements = page.query_selector_all("#slider img")
    img_urls = [img.get_attribute("src") for img in img_elements if img_elements]

    return img_urls


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        base_url = "https://harvestandmill.com/collections/all"

        result = get_item_links(page, base_url)
        report = get_descriptions(page, result)

        browser.close()

    output_file = "harvest_and_mill.json"
    with open(output_file, "w") as file:
        json.dump(report, file, indent=4)

    print(f"Scraped data saved to {output_file}")
    #print(report)


main()
