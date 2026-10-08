/* Design prototype only. WooCommerce will supply the catalog, cart and orders. */
(() => {
  'use strict';
  // Temporary homepage selections. These become native Elementor controls in WordPress.
  const cardDestinations = ['men/clothes/t-shirts', 'women/bags', 'men/shoes', 'women/accessories', 'women/clothes', 'men/bags', 'women/heels', 'men/accessories'];
  const featuredDestinations = ['men', 'women', 'men/clothes', 'women/clothes'];
  const navigation = [
    { name: 'Men', slug: 'men', children: [
      { name: 'Clothes', slug: 'clothes', children: ['T-Shirts', 'Polos', 'Long Sleeve Shirts', 'Hoodies', 'Shorts', 'Jeans', 'Casual Pants', 'Suit Set', 'Jackets', 'Gile'] },
      { name: 'Shoes', slug: 'shoes' }, { name: 'Bags', slug: 'bags' },
      { name: 'Accessories', slug: 'accessories', children: ['Belts', 'Hats', 'Sunglasses'] }
    ] },
    { name: 'Women', slug: 'women', children: [
      { name: 'Accessories', slug: 'accessories', children: ['Belts', 'Bracelets', 'Rings', 'Earrings', 'Scarfs', 'Sunglasses'] },
      { name: 'Bags', slug: 'bags' }, { name: 'Shoes', slug: 'shoes' }, { name: 'Heels', slug: 'heels' },
      { name: 'Clothes', slug: 'clothes', children: ['T-Shirts', 'Tank Tops', 'Vests', 'Sweaters', 'Skirts', 'Trousers', 'Jeans', 'Dress', 'Jackets'] }
    ] }
  ];
  const slugify = name => name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const categories = [];
  function normalize(nodes, parent = []) {
    return nodes.map(item => {
      const node = typeof item === 'string' ? { name: item, slug: slugify(item) } : { ...item };
      node.trail = [...parent, { name: node.name, slug: node.slug }];
      node.path = node.trail.map(x => x.slug).join('/');
      if (node.children) node.children = normalize(node.children, node.trail);
      categories.push(node);
      return node;
    });
  }
  const tree = normalize(navigation);
  const escape = text => String(text).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const main = document.querySelector('#main');
  const header = document.querySelector('#header');
  const panel = document.querySelector('#panel');
  const panelContent = document.querySelector('#panel-content');
  const overlay = document.querySelector('#overlay');
  const site = document.querySelector('#site');
  const back = document.querySelector('#back');
  const close = document.querySelector('#close');
  const notes = `<h2 id="panel-title">About this preview</h2><p class="small-note">An interactive design prototype for approval. This is not an Elementor template or a functioning WooCommerce store.</p><ul class="notes-list"><li>Your original transparent Vivies logo is used unchanged in the header and footer.</li><li>All media areas are neutral placeholders. No reference campaign imagery is reused.</li><li>The eight category-card names and destinations are temporary selections. Final choices remain yours.</li><li>The contact email and informational pages await your content.</li><li>Category hierarchy and separate Men/Women routes follow your brief.</li><li>Search currently explores category names only. Product search requires the WooCommerce catalog.</li><li>Product layouts, cart, and checkout are unconnected preview views. No prices, payments, orders or cart data are simulated.</li></ul><div class="contact-links"><a href="#/product/simple">View simple product layout →</a><a href="#/product/variable">View variable product layout →</a><a href="#/checkout">View checkout placeholder →</a></div>`;
  let panelType = null;
  let menuTrail = [];
  let opener = null;
  let closeTimer;
  let panelRevision = 0;
  let menuRevision = 0;
  let menuAnimation = null;
  let menuChanging = false;
  const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const categoryLink = node => `#/category/${node.path}`;
  const media = label => `<div class="media" role="img" aria-label="${escape(label)}"><span class="media-label">${escape(label)}</span></div>`;
  function home() {
    return `<section class="hero" aria-labelledby="hero-heading"><div class="hero-label"><span class="eyebrow">Campaign image · Placeholder</span><h1 id="hero-heading">Your campaign title</h1><button class="text-link hero-link" data-panel="menu">Explore categories</button></div></section>
      <section class="section categories-section"><h2 class="section-title">Shop by Category</h2><p class="section-note">Temporary card labels, imagery and category selections</p><div class="category-grid">${cardDestinations.map((path, i) => `<a class="tile category-card" href="#/category/${path}">${media(`Image ${String(i + 1).padStart(2, '0')} · Placeholder`)}<span class="tile-title">Category ${String(i + 1).padStart(2, '0')}</span></a>`).join('')}</div></section>
      <section class="editorial first" aria-label="First featured image placeholder"><div><span class="eyebrow">Editorial media · Placeholder 01</span><h2>Your featured photograph</h2><p>Replaceable image area</p></div></section>
      <section class="section featured"><h2 class="section-title">Featured selections</h2><p class="section-note">Temporary section title, imagery, captions and destinations</p><div class="feature-grid">${featuredDestinations.map((path, i) => `<a class="tile feature-card" href="#/category/${path}">${media(`Feature ${String(i + 1).padStart(2, '0')} · Placeholder`)}<span class="tile-title">Featured tile ${String(i + 1).padStart(2, '0')}</span></a>`).join('')}</div><div class="shop-button"><button class="button" data-panel="menu">Shop Now</button></div></section>
      <section class="editorial second" aria-label="Second featured image placeholder"><div><span class="eyebrow">Editorial media · Placeholder 02</span><h2>Your next featured photograph</h2><p>Replaceable image area</p></div></section>`;
  }
  function categoryPage(path) {
    const node = categories.find(x => x.path === path);
    if (!node) return missingPage();
    const breadcrumbs = node.trail.map((part, i) => `<a href="#/category/${node.trail.slice(0, i + 1).map(x => x.slug).join('/')}">${escape(part.name)}</a>`).join('<span aria-hidden="true">/</span>');
    return `<section class="page"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="#/">Home</a><span aria-hidden="true">/</span>${breadcrumbs}</nav><h1>${escape(node.name)}</h1><p class="page-intro">${escape(node.trail.map(x => x.name).join(' / '))} · Category archive preview</p>${node.children ? `<nav class="subcategories" aria-label="Subcategories">${node.children.map(x => `<a href="${categoryLink(x)}">${escape(x.name)}</a>`).join('')}</nav>` : ''}<div class="empty-state"><span class="eyebrow">Catalog not connected</span><h2>Your collection will appear here</h2><p>In WordPress, products assigned to this WooCommerce category will load automatically.</p><div class="page-actions"><button class="button" data-panel="menu">Explore categories</button><a class="text-link" href="#/product/simple">View product layout</a></div></div></section>`;
  }
  function productPage(type) {
    const variable = type === 'variable';
    return `<section class="page"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="#/">Home</a><span>/</span><span>Product layout preview</span></nav><div class="preview-tabs"><a href="#/product/simple">Simple product layout</a><a href="#/product/variable">Variable product layout</a></div><div class="product-preview"><div>${media('Product photography · Placeholder')}<p class="notice">Gallery imagery and thumbnails will come from WooCommerce.</p></div><div class="product-details"><span class="eyebrow">${variable ? 'Variable' : 'Simple'} product · Layout preview</span><h1>Product name placeholder</h1><p class="small-note">Price and stock will come from WooCommerce. No real product or inventory is shown.</p><p>Product description placeholder. Final content will be editable in the WordPress dashboard.</p>${variable ? '<label for="size">Size · demonstration control</label><select id="size"><option value="">Choose a size</option><option>S · placeholder</option><option>M · placeholder</option><option>L · placeholder</option></select><p class="small-note" id="variation-status" aria-live="polite">Select a size to preview the selection state.</p>' : ''}<label for="quantity">Quantity · demonstration control</label><input id="quantity" type="number" min="1" max="99" value="1" aria-label="Quantity"><button class="button" disabled>Add to Cart · not connected</button><p class="small-note">Purchasing stays disabled in this prototype. The WordPress implementation will use native WooCommerce variation, availability and cart validation.</p></div></div></section>`;
  }
  function commercePage(checkout) {
    return `<section class="page"><span class="eyebrow">Design prototype</span><h1>${checkout ? 'Checkout' : 'Shopping bag'}</h1><p class="page-intro">WooCommerce is not connected in this preview.</p><div class="empty-state"><h2>${checkout ? 'Checkout awaits WooCommerce' : 'Your shopping bag is empty'}</h2><p>${checkout ? 'Addresses, shipping, totals and payment methods will be handled by WooCommerce. No personal or payment details are collected here.' : 'Real products, quantities, totals and cart-count updates will be available in the WordPress implementation.'}</p><div class="page-actions"><button class="button" data-panel="menu">Explore categories</button>${checkout ? '<a class="text-link" href="#/cart">Back to shopping bag</a>' : '<a class="text-link" href="#/checkout">View checkout placeholder</a>'}</div></div></section>`;
  }
  const pages = { contact: 'Contact us', faq: 'FAQ', shipping: 'Shipping & Returns', privacy: 'Privacy Policy', terms: 'Terms & Conditions' };
  function infoPage(key) {
    if (!pages[key]) return missingPage();
    return `<section class="page"><span class="eyebrow">Editable content placeholder</span><h1>${escape(pages[key])}</h1><p class="page-intro">This page is awaiting your approved content. No company information or policy claims have been invented.</p>${key === 'contact' ? '<button class="button" data-panel="contact">Open contact panel</button>' : '<a class="text-link" href="#/">Return to homepage</a>'}</section>`;
  }
  function matchingCategories(query) {
    const tokenize = value => value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(/\s+/).filter(Boolean);
    const words = tokenize(query);
    return words.length ? categories.filter(node => {
      const tokens = tokenize(node.trail.map(x => x.name).join(' '));
      return words.every(word => tokens.some(token => token.startsWith(word)));
    }) : [];
  }
  function resultsMarkup(query) {
    const matches = matchingCategories(query);
    return `<p class="small-note" role="status">${query.trim() ? `${matches.length} category ${matches.length === 1 ? 'result' : 'results'}` : 'Enter a category name to explore the navigation.'}</p><div class="search-results">${matches.map(node => `<a href="${categoryLink(node)}">${escape(node.name)}<small>${escape(node.trail.map(x => x.name).join(' / '))}</small></a>`).join('')}</div>`;
  }
  function searchForm(query = '') {
    return `<form class="search-form" role="search"><input class="search-input" type="search" name="q" value="${escape(query)}" aria-label="Search categories in this preview" placeholder="Search the preview" autocomplete="off"><button type="submit" aria-label="Show search results"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></svg></button></form>`;
  }
  function searchPage(query) {
    return `<section class="page"><h1>Search</h1>${searchForm(query)}<p class="small-note">Category search demonstration. Product search will use your real WooCommerce catalog after integration.</p><div class="search-output">${resultsMarkup(query)}</div></section>`;
  }
  function missingPage() { return '<section class="page"><h1>Page not found</h1><a class="text-link" href="#/">Return to homepage</a></section>'; }
  function renderRoute(focus = true) {
    closePanel(false);
    const route = location.hash.slice(1) || '/';
    let content;
    if (route === '/') content = home();
    else if (route.startsWith('/category/')) content = categoryPage(route.slice(10));
    else if (route === '/product/simple' || route === '/product/variable') content = productPage(route.split('/')[2]);
    else if (route === '/cart' || route === '/checkout') content = commercePage(route === '/checkout');
    else if (route.startsWith('/page/')) content = infoPage(route.slice(6));
    else if (route.startsWith('/search')) content = searchPage(new URLSearchParams(route.split('?')[1] || '').get('q') || '');
    else content = missingPage();
    main.innerHTML = content;
    header.classList.toggle('solid', route !== '/');
    document.title = `${main.querySelector('h1')?.textContent || 'Vivies'} — VIVIES design preview`;
    window.scrollTo({ top: 0, behavior: 'instant' });
    if (focus) main.focus({ preventScroll: true });
  }
  function activeNodes() { return menuTrail.length ? menuTrail[menuTrail.length - 1].children : tree; }
  function paintMenu(focus, direction) {
    const parent = menuTrail[menuTrail.length - 1];
    back.hidden = !parent;
    back.disabled = false;
    panelContent.innerHTML = `<div class="menu-body"><h2 id="panel-title">${parent ? escape(menuTrail.map(x => x.name).join(' / ')) : 'Explore Vivies'}</h2><nav class="menu-items" aria-label="${parent ? escape(parent.name) : 'Main'} categories">${activeNodes().map(node => node.children ? `<button class="menu-item" data-menu="${node.path}">${escape(node.name)}<span class="menu-chevron" aria-hidden="true">›</span></button>` : `<a class="menu-item" href="${categoryLink(node)}">${escape(node.name)}<span class="menu-chevron" aria-hidden="true">›</span></a>`).join('')}</nav>${parent ? `<a class="text-link menu-view-all" href="${categoryLink(parent)}">View all ${escape(parent.name)}</a>` : ''}<p class="menu-caption">${parent ? 'Choose a category to continue.' : 'Men and Women · Complete category navigation'}</p></div>`;
    menuChanging = false;
    panelContent.inert = false;
    if (focus && !reducedMotion()) {
      menuAnimation = panelContent.firstElementChild.animate([
        { opacity: 0, transform: `translateX(${direction * 10}px)` },
        { opacity: 1, transform: 'translateX(0)' }
      ], { duration: 280, easing: 'cubic-bezier(.2,.65,.3,1)' });
    }
    if (focus) panelContent.querySelector('.menu-item')?.focus({ preventScroll: true });
  }
  function renderMenu(focus = false, direction = 1) {
    const revision = ++menuRevision;
    const outgoing = panelContent.querySelector('.menu-body');
    const outgoingStyle = outgoing ? getComputedStyle(outgoing) : null;
    const startingOpacity = outgoingStyle?.opacity || '1';
    const startingTransform = outgoingStyle?.transform || 'none';
    menuAnimation?.cancel();
    if (!focus || !outgoing || reducedMotion()) { paintMenu(focus, direction); return; }
    menuChanging = true;
    panelContent.inert = true;
    back.disabled = true;
    close.focus({ preventScroll: true });
    menuAnimation = outgoing.animate([
      { opacity: startingOpacity, transform: startingTransform },
      { opacity: 0, transform: `translateX(${-direction * 6}px)` }
    ], { duration: 140, easing: 'ease-in', fill: 'forwards' });
    menuAnimation.finished.then(() => {
      if (revision === menuRevision && panelType === 'menu') paintMenu(focus, direction);
    }).catch(() => { /* Closing or replacing a panel intentionally cancels the transition. */ });
  }
  function openPanel(type, trigger) {
    clearTimeout(closeTimer);
    const revision = ++panelRevision;
    ++menuRevision;
    menuAnimation?.cancel();
    menuChanging = false;
    panelContent.inert = false;
    opener = trigger || document.activeElement;
    panelType = type;
    menuTrail = [];
    panel.className = `panel ${type === 'menu' ? 'menu' : 'right'}`;
    panel.hidden = false;
    panel.inert = false;
    panel.removeAttribute('aria-hidden');
    back.hidden = true;
    back.disabled = false;
    if (type === 'menu') renderMenu();
    else if (type === 'contact') panelContent.innerHTML = '<h2 id="panel-title">Contact us</h2><button class="contact-email" disabled><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14"/><path d="m3 6 9 7 9-7"/></svg>Email</button><p class="contact-notice">Contact email awaiting configuration.</p><hr><nav class="contact-links" aria-label="Contact links"><a href="#/page/contact">Contact us</a><a href="#/page/faq">FAQ</a></nav>';
    else if (type === 'search') panelContent.innerHTML = `<h2 id="panel-title">Search</h2>${searchForm()}<p class="small-note">Explore the category hierarchy. Product search awaits your WooCommerce catalog.</p><div class="search-output">${resultsMarkup('')}</div>`;
    else panelContent.innerHTML = notes;
    site.inert = true;
    document.body.style.overflow = 'hidden';
    document.querySelectorAll('[data-panel]').forEach(button => button.setAttribute('aria-expanded', String(button === trigger)));
    header.classList.add('panel-active');
    // Give the closed drawer a painted frame. A layout read alone can skip the
    // opening animation when a previously hidden dialog becomes visible.
    const reveal = () => {
      if (revision !== panelRevision || panelType !== type) return;
      panel.classList.add('open');
      overlay.classList.add('open');
    };
    if (reducedMotion()) reveal();
    else requestAnimationFrame(() => requestAnimationFrame(reveal));
    (type === 'search' ? panel.querySelector('input') : close).focus();
  }
  function closePanel(restore = true) {
    if (!panelType) return;
    panelType = null;
    ++panelRevision;
    ++menuRevision;
    menuAnimation?.cancel();
    menuChanging = false;
    back.disabled = false;
    panelContent.inert = false;
    panel.inert = true;
    panel.setAttribute('aria-hidden', 'true');
    panel.classList.remove('open'); overlay.classList.remove('open');
    header.classList.remove('panel-active');
    site.inert = false;
    document.body.style.overflow = '';
    document.querySelectorAll('[data-panel]').forEach(button => button.setAttribute('aria-expanded', 'false'));
    if (restore && opener?.isConnected) opener.focus({ preventScroll: true });
    closeTimer = setTimeout(() => { if (!panelType) { panel.hidden = true; panelContent.innerHTML = ''; } }, reducedMotion() ? 0 : 480);
  }
  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-panel]');
    if (trigger) { openPanel(trigger.dataset.panel, trigger); return; }
    const menuButton = event.target.closest('[data-menu]');
    if (menuButton && !menuChanging) { menuTrail.push(categories.find(x => x.path === menuButton.dataset.menu)); renderMenu(true); return; }
    // Same-route links still close a panel and return focus to the content.
    const link = event.target.closest('a[href^="#/"]');
    if (link && link.getAttribute('href') === (location.hash || '#/')) { closePanel(false); main.focus(); }
  });
  close.addEventListener('click', () => closePanel());
  overlay.addEventListener('click', () => closePanel());
  back.addEventListener('click', () => { if (!menuChanging) { menuTrail.pop(); renderMenu(true, -1); } });
  document.addEventListener('keydown', event => {
    if (!panelType) return;
    if (event.key === 'Escape') { event.preventDefault(); closePanel(); return; }
    if (event.key !== 'Tab') return;
    const controls = [...panel.querySelectorAll('button:not([disabled]),a[href],input,select')].filter(x => x.getClientRects().length && !x.closest('[inert]'));
    const first = controls[0], last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  document.addEventListener('input', event => {
    if (event.target.matches('.search-input')) {
      event.target.closest('.search-form').parentElement.querySelector('.search-output').innerHTML = resultsMarkup(event.target.value);
    }
  });
  document.addEventListener('change', event => {
    if (event.target.id === 'size') document.querySelector('#variation-status').textContent = event.target.value ? `${event.target.value} selected. Purchasing remains unavailable in this preview.` : 'Select a size to preview the selection state.';
  });
  document.addEventListener('submit', event => {
    if (!event.target.matches('.search-form')) return;
    event.preventDefault();
    const query = new FormData(event.target).get('q') || '';
    const route = `#/search?q=${encodeURIComponent(query)}`;
    if (location.hash === route) renderRoute();
    else location.hash = route;
  });
  window.addEventListener('hashchange', () => renderRoute());
  window.addEventListener('scroll', () => header.classList.toggle('scrolled', window.scrollY > 12), { passive: true });
  renderRoute(false);
})();
