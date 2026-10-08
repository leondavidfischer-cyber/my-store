"""Verify the requested fades and spacing through actual rendered states."""
import os
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('PREVIEW_URL', 'http://127.0.0.1:4173')
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='no-preference')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE)
    header_opacity = lambda: page.locator('#header').evaluate('(el) => Number(getComputedStyle(el,"::before").opacity)')
    assert header_opacity() == 0
    page.evaluate('scrollTo({top:400,behavior:"instant"})')
    expect(page.locator('#header')).to_have_class('header scrolled')
    page.wait_for_timeout(120)
    assert 0 < header_opacity() < 1, 'Header should be partway through its fade-in'
    page.wait_for_timeout(450)
    assert header_opacity() == 1
    page.evaluate('scrollTo({top:0,behavior:"instant"})')
    expect(page.locator('#header')).to_have_class('header')
    page.wait_for_timeout(120)
    assert 0 < header_opacity() < 1, 'Header should be partway through its fade-out'
    page.wait_for_timeout(450)
    assert header_opacity() == 0
    print('PASS: Header visibly fades both in and out, without moving')

    for selector in ['[data-panel="menu"] svg', '[data-panel="search"] svg']:
        assert page.locator(selector).bounding_box()['height'] == 16
        assert page.locator(selector).bounding_box()['width'] == 16
    print('PASS: Menu and Search icons have matching compact proportions')

    page.get_by_role('button', name='Menu', exact=True).click()
    page.wait_for_timeout(120)
    position = page.locator('#panel').bounding_box()
    assert -position['width'] < position['x'] < -1, 'Drawer should be partway through its slide'
    opacity = page.locator('#panel').evaluate('(el) => Number(getComputedStyle(el).opacity)')
    assert 0 < opacity < 1, 'Drawer should be partway through its fade'
    page.wait_for_timeout(480)
    assert page.locator('#panel').bounding_box()['x'] == 0
    assert header_opacity() == 1
    print('PASS: Drawer slides and fades instead of appearing immediately; header also fades in')

    def check_transition(label, target_heading):
        old_heading = page.locator('#panel-title').inner_text()
        page.locator('#panel').get_by_role('button', name=label, exact=True).click()
        assert page.locator('#panel-title').inner_text() == old_heading, 'Outgoing level should stay present while fading out'
        expect(page.locator('#panel-title')).to_have_text(target_heading)
        # The incoming level is rendered transparently before completing its fade.
        opacity = page.locator('.menu-body').evaluate('(el) => Number(getComputedStyle(el).opacity)')
        assert opacity < 1, 'Incoming level should fade in'
        page.wait_for_timeout(320)
        assert page.locator('.menu-body').evaluate('(el) => Number(getComputedStyle(el).opacity)') == 1

    def check_gap():
        last = page.locator('.menu-items > *').last.bounding_box()
        view_all = page.locator('.menu-view-all').bounding_box()
        assert view_all['y'] - (last['y'] + last['height']) >= 27

    check_transition('Men', 'Men')
    check_gap()
    check_transition('Clothes', 'Men / Clothes')
    check_gap()
    page.get_by_role('button', name='Back to previous menu level').click()
    expect(page.locator('#panel-title')).to_have_text('Men')
    page.get_by_role('button', name='Back to previous menu level').click()
    expect(page.locator('#panel-title')).to_have_text('Explore Vivies')
    check_transition('Women', 'Women')
    check_gap()
    check_transition('Accessories', 'Women / Accessories')
    check_gap()
    print('PASS: Menu levels fade out/in; View all links have space on Men and Women levels')

    page.keyboard.press('Escape')
    expect(page.get_by_role('button', name='Menu', exact=True)).to_be_focused()
    # Close during an outgoing level animation; stale callbacks must not reopen it.
    page.get_by_role('button', name='Menu', exact=True).click()
    page.locator('#panel').get_by_role('button', name='Men', exact=True).click()
    page.keyboard.press('Escape')
    page.wait_for_timeout(550)
    expect(page.locator('#panel')).to_be_hidden()
    expect(page.get_by_role('button', name='Menu', exact=True)).to_be_focused()
    page.get_by_role('button', name='Menu', exact=True).click()
    expect(page.locator('#panel-title')).to_have_text('Explore Vivies')
    page.keyboard.press('Escape')
    print('PASS: Closing during a menu transition cancels it and restores focus; reopening resets the hierarchy')

    page.emulate_media(reduced_motion='reduce')
    page.get_by_role('button', name='Menu', exact=True).click()
    page.locator('#panel').get_by_role('button', name='Men', exact=True).click()
    expect(page.locator('#panel-title')).to_have_text('Men')
    assert page.locator('.menu-body').evaluate('(el) => el.getAnimations().length') == 0
    assert page.locator('#header').evaluate('(el) => getComputedStyle(el,"::before").transitionDuration') == '0s'
    page.keyboard.press('Escape')
    print('PASS: Reduced motion disables header, drawer and menu-level animation')
    assert not errors, errors
    browser.close()
