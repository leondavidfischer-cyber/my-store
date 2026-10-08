"""Check the new preview interactions without claiming a commerce integration."""
import os
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('PREVIEW_URL', 'http://127.0.0.1:4173')
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width':1440,'height':900})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE)
    page.get_by_role('button',name='Search',exact=True).click()
    expect(page.locator('#panel .search-results a')).to_have_count(2)
    expect(page.get_by_role('button',name='Clear search',exact=True)).to_be_hidden()
    page.get_by_role('searchbox').fill('women sunglasses')
    expect(page.locator('#panel .search-results a')).to_have_count(1)
    expect(page.locator('#panel .search-results a')).to_have_attribute('href','#/category/women/accessories/sunglasses')
    page.get_by_role('button',name='Clear search',exact=True).click()
    expect(page.get_by_role('searchbox')).to_have_value('')
    expect(page.get_by_role('searchbox')).to_be_focused()
    expect(page.locator('#panel .search-results a')).to_have_count(2)
    page.get_by_role('searchbox').fill('nonexistent-query')
    expect(page.locator('.search-empty')).to_contain_text('No matching category')
    page.keyboard.press('Escape')
    print('PASS: Search exploration, contextual results, clear/reset, focus and empty-result feedback')

    page.get_by_role('button',name='Contact us',exact=True).click()
    page.wait_for_timeout(550)
    title=page.locator('#panel-title').bounding_box()
    close=page.locator('#close').bounding_box()
    assert abs(title['y']+title['height']/2-(close['y']+close['height']/2))<2
    page.keyboard.press('Escape')
    print('PASS: Contact title and Close control align on one row')

    for width in [1440,1024,768,390,360]:
        page.set_viewport_size({'width':width,'height':900})
        page.goto(BASE)
        page.reload()
        page.goto(f'{BASE}/#/category/men/clothes/t-shirts')
        expect(page.locator('.catalog-card')).to_have_count(4)
        expect(page.locator('.archive-layout')).to_contain_text('not store inventory')
        columns=page.locator('.catalog-grid').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
        assert columns==(2 if width<=768 else 4)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto(f'{BASE}/#/product/variable')
        page.get_by_role('button',name='View product image 3 placeholder',exact=True).click()
        expect(page.locator('#product-gallery .media')).to_have_attribute('aria-label','Product image 03 · Placeholder')
        expect(page.get_by_role('button',name='View product image 3 placeholder',exact=True)).to_have_attribute('aria-pressed','true')
        expect(page.get_by_role('button',name='View product image 1 placeholder',exact=True)).to_have_attribute('aria-pressed','false')
        page.locator('.product-information summary').first.click()
        expect(page.locator('.product-information details').first).to_have_attribute('open','')
        page.locator('#size').select_option(label='M · placeholder')
        expect(page.locator('#variation-status')).to_contain_text('M · placeholder selected')
        expect(page.get_by_role('button',name='Add to Cart · not connected')).to_be_disabled()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('.footer').scroll_into_view_if_needed()
        if width<=768:
            expect(page.locator('.footer-group').first).not_to_have_attribute('open','')
            page.locator('.footer-group summary').first.click()
            expect(page.locator('.footer-group').first).to_have_attribute('open','')
            page.locator('.footer-group').first.get_by_role('link',name='FAQ',exact=True).click()
            expect(page.locator('h1')).to_have_text('FAQ')
        else:
            expect(page.locator('.footer-group').first).to_have_attribute('open','')
            expect(page.locator('.footer-group').first.get_by_role('link',name='FAQ',exact=True)).to_be_visible()
        print(f'PASS {width}px: archive layout, gallery selection, product disclosure, variation state, disabled purchase and responsive footer')
    assert not errors,errors
    print('PASS: No JavaScript errors in the refinement checks')
    browser.close()
