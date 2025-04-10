from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # set to True if you don't want browser UI
    page = browser.new_page()
    page.goto("https://www.patagonia.com/shop/mens-jackets-vests", timeout=60000)

    # Wait for the products to load
    page.wait_for_selector(".product-tile__image.default.active")

    # Find all product anchor elements that are the main/default variant
    product_links = page.locator("div.product-tile__image.default.active a[itemprop='url']")

    count = product_links.count()
    print(f"Found {count} products.\n")

    for i in range(count):
        link = product_links.nth(i)
        href = link.get_attribute("href")
        title = link.get_attribute("title")
        print(f"{i + 1}. Title: {title}")
        print(f"   Href: {href}\n")

    browser.close()

