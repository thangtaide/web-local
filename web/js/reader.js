(() => {
  'use strict';
  const {config: C, root, el, button, cover, stories, storyRoute, readRoute} = window.MangaApp;
  const PROGRESS_KEY = 'manga-reader.progress.v1';
  const WIDTH_KEY = 'manga-reader.width.v1';
  let storage = null;
  try {
    storage = window.localStorage;
    const probe = 'manga-reader.probe';
    storage.setItem(probe, '1'); storage.removeItem(probe);
  } catch (_) { storage = null; }
  function read(key, fallback) {
    let raw;
    try { raw = storage ? storage.getItem(key) : null; }
    catch (_) { storage = null; return fallback; }
    try { return JSON.parse(raw) ?? fallback; } catch (_) { return fallback; }
  }
  function write(key, value) {
    try {
      if (storage) { storage.setItem(key, JSON.stringify(value)); return; }
    } catch (_) { storage = null; }
    if (current) showStorageNotice();
  }
  const stored = read(PROGRESS_KEY, {});
  const progress = Object.create(null);
  // Validate persisted values; malformed storage must never break rendering.
  if (stored && typeof stored === 'object' && !Array.isArray(stored)) {
    for (const story of stories) {
      const record = stored[story.id];
      if (!record || typeof record !== 'object' || typeof record.chapterId !== 'string') continue;
      const chapters = Object.create(null);
      if (record.chapters && typeof record.chapters === 'object') {
        for (const chapter of story.chapters) {
          const saved = record.chapters[chapter.id];
          if (saved && Number.isInteger(saved.page) && saved.page >= 0 && Number.isFinite(saved.ratio)) {
            chapters[chapter.id] = {page: saved.page, ratio: Math.min(1, Math.max(0, saved.ratio)), imageName: String(saved.imageName || ''), time: Number(saved.time) || 0};
          }
        }
      }
      progress[story.id] = {chapterId: record.chapterId, time: Number(record.time) || 0, chapters};
    }
  }
  const clampWidth = value => Math.min(C.MAX_READER_IMAGE_WIDTH, Math.max(C.MIN_READER_IMAGE_WIDTH, value));
  const savedWidth = read(WIDTH_KEY, null);
  let width = clampWidth(Number.isFinite(savedWidth) && savedWidth > 0 ? savedWidth : C.READER_IMAGE_WIDTH);
  let current = null;
  let saveTimer = null;
  let resizeTimer = null;
  let generation = 0;
  let spaceScroll = null;
  let spaceFrame = null;

  function continueRoute(story) {
    const chapter = story.chapters.find(item => item.id === progress[story.id]?.chapterId) || story.chapters[0];
    return readRoute(story, chapter, true);
  }
  function renderRecent(container) {
    if (!C.SAVE_READING_POSITION) return;
    const recent = stories.filter(story => progress[story.id]).sort((a, b) => progress[b.id].time - progress[a.id].time).slice(0, C.RECENT_STORIES_LIMIT);
    if (!recent.length) return;
    const section = el('section', {class: 'recent-section'}, el('div', {class: 'section-title'}, el('h2', {}, 'Đọc gần đây'), el('span', {class: 'subtle'}, 'Tiếp tục câu chuyện còn dang dở')));
    const grid = el('div', {class: 'recent-grid'});
    for (const story of recent) {
      const record = progress[story.id];
      const chapter = story.chapters.find(item => item.id === record.chapterId) || story.chapters[0];
      const saved = record.chapters[chapter.id];
      grid.append(el('article', {class: 'recent-card'}, el('a', {href: storyRoute(story)}, cover(story)), el('div', {}, el('h3', {}, story.name), el('p', {class: 'subtle'}, chapter.name + (saved ? ' · Ảnh ' + Math.min(chapter.image_count, saved.page + 1) + '/' + chapter.image_count : '')), el('a', {class: 'recent-continue', href: continueRoute(story)}, 'Đọc tiếp →'))));
    }
    section.append(grid); container.append(section);
  }
  function inset() {
    return document.body.classList.contains('focus-mode') ? 0 : (document.querySelector('.reader-top')?.getBoundingClientRect().height || 0);
  }
  function anchor() {
    if (!current) return null;
    const at = inset() + 1;
    // Binary search keeps scroll handling inexpensive even for very long chapters.
    let low = 0, high = current.pages.length - 1;
    while (low < high) {
      const mid = Math.floor((low + high) / 2);
      if (current.pages[mid].getBoundingClientRect().bottom <= at) low = mid + 1;
      else high = mid;
    }
    const rect = current.pages[low].getBoundingClientRect();
    return {page: low, ratio: Math.max(0, Math.min(1, (at - rect.top) / Math.max(1, rect.height)))};
  }
  function scrollAnchor(value) {
    if (!current || !value) return;
    const index = Math.min(current.pages.length - 1, Math.max(0, value.page));
    const rect = current.pages[index].getBoundingClientRect();
    window.scrollTo({top: window.scrollY + rect.top + Math.max(0, Math.min(1, value.ratio)) * rect.height - inset() - 1, behavior: 'instant'});
    current.position = anchor();
  }
  function imageName(url) {
    try { return new URL(url).pathname.split('/').pop(); } catch (_) { return ''; }
  }
  function save() {
    clearTimeout(saveTimer);
    if (!current || current.restoring || !C.SAVE_READING_POSITION) return;
    const position = anchor();
    if (!position) return;
    current.position = position;
    const {story, chapter} = current;
    const time = Date.now();
    const record = progress[story.id] || {chapters: Object.create(null)};
    record.chapterId = chapter.id; record.time = time;
    record.chapters[chapter.id] = {...position, imageName: imageName(chapter.images[position.page]), time};
    progress[story.id] = record;
    write(PROGRESS_KEY, progress);
    updatePosition(position);
  }
  function updatePosition(position) {
    if (current && position) current.counter.textContent = 'Ảnh ' + (position.page + 1) + ' / ' + current.pages.length;
  }
  function showStorageNotice() {
    const note = document.querySelector('.storage-notice');
    if (note && note.hidden) {
      const position = current && !current.restoring ? anchor() : null;
      note.hidden = false;
      if (position) scrollAnchor(position);
    }
  }
  function leave() {
    stopSpaceScroll();
    save();
    clearTimeout(saveTimer); clearTimeout(resizeTimer);
    generation++;
    current = null;
  }
  function focus() {
    if (!current) return;
    const position = anchor();
    document.body.classList.toggle('focus-mode');
    current.focusButton.setAttribute('aria-pressed', String(document.body.classList.contains('focus-mode')));
    scrollAnchor(position);
    save();
  }
  function changeWidth(step) {
    if (!current) return;
    const position = anchor();
    width = clampWidth(width + step * C.IMAGE_WIDTH_STEP);
    current.stage.style.setProperty('--reader-width', width + 'px');
    current.widthLabel.textContent = width + 'px';
    scrollAnchor(position);
    write(WIDTH_KEY, width);
    save();
  }
  function goChapter(offset) {
    if (!current || current.navigating) return;
    const chapter = current.story.chapters[current.chapterIndex + offset];
    if (!chapter) return;
    save(); current.navigating = true;
    location.hash = readRoute(current.story, chapter);
  }
  function stopSpaceScroll(finishTap = false) {
    if (spaceFrame !== null) cancelAnimationFrame(spaceFrame);
    spaceFrame = null;
    // A short tap keeps its single page animation; a hold stops immediately.
    if (spaceScroll && (!finishTap || spaceScroll.active)) window.scrollTo({top: window.scrollY, behavior: 'instant'});
    spaceScroll = null;
  }
  function scrollByPage(direction) {
    stopSpaceScroll();
    window.scrollBy({top: direction * innerHeight * C.SPACE_SCROLL_RATIO, behavior: C.SMOOTH_SCROLL ? 'smooth' : 'instant'});
  }
  function scrollToEdge(bottom) {
    stopSpaceScroll();
    window.scrollTo({top: bottom ? document.documentElement.scrollHeight : 0, behavior: 'instant'});
  }
  function startSpaceScroll(direction) {
    scrollByPage(direction);
    spaceScroll = {direction, started: performance.now(), last: null, active: false, remainder: 0};
    const frame = now => {
      if (!spaceScroll || !current || document.hidden) {stopSpaceScroll(); return;}
      const motion = spaceScroll;
      if (now - motion.started >= 180) {
        if (!motion.active) {
          // Cancel native smooth scrolling once, never restart it on key repeat.
          window.scrollTo({top: window.scrollY, behavior: 'instant'});
          motion.active = true;
          motion.last = now;
        }
        const elapsed = Math.min(50, Math.max(0, now - motion.last));
        // One configured page per half second, independent of OS repeat/FPS.
        const distance = motion.direction * innerHeight * C.SPACE_SCROLL_RATIO * elapsed / 500;
        const maximum = Math.max(0, document.documentElement.scrollHeight - innerHeight);
        const target = Math.max(0, Math.min(maximum, window.scrollY + motion.remainder + distance));
        window.scrollTo({top: target, behavior: 'instant'});
        motion.remainder = target - window.scrollY;
        motion.last = now;
      }
      spaceFrame = requestAnimationFrame(frame);
    };
    spaceFrame = requestAnimationFrame(frame);
  }

  function waitImage(image) {
    if (image.complete && image.getAttribute('src')) return Promise.resolve();
    return new Promise(resolve => {
      let timer;
      const done = () => { clearTimeout(timer); image.removeEventListener('load', done); image.removeEventListener('error', done); resolve(); };
      image.addEventListener('load', done, {once: true}); image.addEventListener('error', done, {once: true});
      timer = setTimeout(done, 8000);
    });
  }
  async function restore(saved, token) {
    const view = current;
    const page = Math.min(view.pages.length - 1, Math.max(0, saved?.page || 0));
    // Only probe preceding unknown-size images when restoring; known-size images stay lazy.
    const unknown = view.pages.slice(0, page + 1).filter(node => node.dataset.known !== 'true');
    let cursor = 0;
    await Promise.all(Array.from({length: Math.min(4, unknown.length)}, async () => {
      while (cursor < unknown.length && token === generation) {
        const image = unknown[cursor++].querySelector('img'); image.loading = 'eager'; await waitImage(image);
      }
    }));
    if (token !== generation || !view.restoring) return;
    const target = view.pages[page].querySelector('img');
    target.loading = 'eager';
    // Move to the reserved target area so native lazy loading has a useful viewport.
    scrollAnchor({page, ratio: saved?.ratio || 0});
    await waitImage(target);
    await new Promise(requestAnimationFrame);
    if (token !== generation || !view.restoring) return;
    scrollAnchor({page, ratio: saved?.ratio || 0});
    view.restoring = false;
    view.stage.setAttribute('aria-busy', 'false');
    view.position = anchor();
    save();
  }
  function render(story, chapterId) {
    const token = generation;
    const chapter = story.chapters.find(item => item.id === chapterId) || story.chapters[0];
    if (!chapter) { location.hash = storyRoute(story); return; }
    const chapterIndex = story.chapters.indexOf(chapter);
    document.title = chapter.name + ' · ' + story.name;
    document.body.classList.add('reading');
    const stage = el('div', {class: 'reader-stage', 'data-route': location.hash.split('?')[0], 'aria-busy': 'true', style: '--reader-width:' + width + 'px;--image-gap:' + Math.max(0, C.IMAGE_GAP) + 'px'});
    const counter = el('span', {class: 'position-counter', 'aria-live': 'off'}, 'Ảnh 1 / ' + chapter.images.length);
    const widthLabel = el('span', {class: 'width-label'}, width + 'px');
    const focusButton = button('F · Ẩn giao diện', focus, {'aria-pressed': 'false', title: 'Nhấn F lần nữa để hiện lại giao diện'});
    const top = el('header', {class: 'reader-top reader-control'}, el('a', {class: 'button', href: storyRoute(story)}, '← Danh sách tập'), el('div', {class: 'reader-title'}, el('strong', {}, story.name), el('span', {}, chapter.name)), focusButton);
    const left = button('← Tập trước', () => goChapter(-1), {class: 'reader-left reader-control', disabled: chapterIndex === 0});
    const right = button('Tập sau →', () => goChapter(1), {class: 'reader-right reader-control', disabled: chapterIndex === story.chapters.length - 1});
    const bottom = el('footer', {class: 'reader-bottom reader-control'}, counter,
      el('div', {class: 'scroll-tools'}, button('Space ↓', () => scrollByPage(1), {title: 'Cuộn xuống 80% màn hình'}), button('Shift + Space ↑', () => scrollByPage(-1)), button('Home', () => scrollToEdge(false)), button('End', () => scrollToEdge(true))),
      el('div', {class: 'width-tools'}, button('−', () => changeWidth(-1), {'aria-label': 'Giảm chiều rộng (-)'}), widthLabel, button('+', () => changeWidth(1), {'aria-label': 'Tăng chiều rộng (+)'})), el('a', {class: 'escape-link', href: storyRoute(story)}, 'Esc · Danh sách tập'));
    current = {story, chapter, chapterIndex, stage, pages: [], counter, widthLabel, focusButton, restoring: true, position: null, navigating: false};
    chapter.images.forEach((url, index) => {
      const size = chapter.image_sizes?.[index];
      const known = Array.isArray(size) && size.length === 2 && size.every(value => Number.isFinite(value) && value > 0);
      const page = el('div', {class: 'reader-page', 'data-page': index, 'data-known': String(known), style: 'aspect-ratio:' + (known ? size[0] + '/' + size[1] : '2/3')});
      const image = el('img', {class: 'reader-image', alt: 'Trang ' + (index + 1), loading: C.LAZY_LOAD_IMAGES ? 'lazy' : 'eager', decoding: 'async'});
      const loaded = () => {
        if (token !== generation || !image.naturalWidth) return;
        const rect = page.getBoundingClientRect();
        const changed = Math.abs(rect.height - rect.width * image.naturalHeight / image.naturalWidth) > 1;
        const position = current.restoring || !changed ? null : anchor();
        page.style.aspectRatio = image.naturalWidth + '/' + image.naturalHeight;
        page.dataset.known = 'true';
        if (position) scrollAnchor(position);
      };
      image.addEventListener('load', loaded, {once: true});
      image.addEventListener('error', () => {
        if (token !== generation) return;
        image.hidden = true;
        page.append(el('div', {class: 'image-error', role: 'status'}, 'Không tải được ảnh ' + (index + 1), el('small', {}, 'File có thể đã bị xóa, hỏng hoặc định dạng chưa được trình duyệt hỗ trợ. Hãy quét lại từ Manga Manager.')));
      }, {once: true});
      page.append(image); stage.append(page); current.pages.push(page);
      image.setAttribute('src', url);
    });
    const end = el('section', {class: 'chapter-end reader-control'}, el('p', {class: 'eyebrow'}, 'BẠN ĐÃ ĐẾN CUỐI TẬP'), el('h2', {}, chapter.name));
    if (chapterIndex < story.chapters.length - 1) end.append(button('Đọc tập tiếp theo · ' + story.chapters[chapterIndex + 1].name + ' →', () => goChapter(1), {class: 'primary'}));
    else end.append(el('p', {class: 'subtle'}, 'Đã đọc đến tập cuối của truyện.'));
    end.append(el('a', {href: storyRoute(story), class: 'back-link'}, '← Danh sách tập'));
    const note = el('p', {class: 'storage-notice reader-control', role: 'status', hidden: !!storage}, 'Trình duyệt không cho lưu tiến độ. Bạn vẫn có thể đọc bình thường trong phiên này.');
    root.replaceChildren(top, left, right, bottom, note);
    if (chapter.id !== chapterId) root.append(el('p', {class: 'reader-notice reader-control'}, 'Tập trước đã thay đổi hoặc bị xóa. Đang mở tập đầu tiên còn lại.'));
    root.append(stage, end);
    const params = new URLSearchParams(location.hash.split('?')[1] || '');
    let saved = C.SAVE_READING_POSITION && params.get('start') !== '1' ? progress[story.id]?.chapters[chapter.id] : null;
    if (saved?.imageName) {
      const found = chapter.images.findIndex(url => imageName(url) === saved.imageName);
      if (found >= 0) saved = {...saved, page: found};
    }
    if (params.get('start') === '1') {
      // Hash-only replacement lets F5 resume while an explicit start link resets once.
      try { history.replaceState(null, '', location.hash.split('?')[0]); } catch (_) { /* Browser may restrict file history; reading still works. */ }
    }
    restore(saved, token);
  }
  window.addEventListener('scroll', () => {
    if (!current || current.restoring) return;
    current.position = anchor(); updatePosition(current.position);
    clearTimeout(saveTimer); saveTimer = setTimeout(save, 180);
  }, {passive: true});
  window.addEventListener('resize', () => {
    if (!current || current.restoring) return;
    const position = current.position;
    clearTimeout(resizeTimer); resizeTimer = setTimeout(() => {scrollAnchor(position); save();}, 100);
  });
  window.addEventListener('pagehide', () => {stopSpaceScroll(); save();});
  window.addEventListener('blur', () => {stopSpaceScroll(); save();});
  document.addEventListener('visibilitychange', () => {if (document.hidden) {stopSpaceScroll(); save();}});
  function cancelRestore() {
    if (current?.restoring) {
      current.restoring = false;
      current.stage.setAttribute('aria-busy', 'false');
      save();
    }
  }
  const editing = target => target instanceof Element && target.closest('input,textarea,select,[contenteditable]:not([contenteditable="false"])');
  const manualScroll = () => {stopSpaceScroll(); cancelRestore();};
  window.addEventListener('wheel', manualScroll, {passive: true});
  window.addEventListener('touchstart', manualScroll, {passive: true});
  window.addEventListener('focusin', event => {if (editing(event.target)) stopSpaceScroll();});
  window.addEventListener('keyup', event => {
    if (event.key === ' ' || event.code === 'Space') stopSpaceScroll(true);
    else if (spaceScroll) spaceScroll.direction = event.shiftKey ? -1 : 1;
  });
  window.addEventListener('keydown', event => {
    if (!current || event.ctrlKey || event.altKey || event.metaKey || event.isComposing || editing(event.target)) {stopSpaceScroll(); return;}
    const key = event.key.toLowerCase();
    if (spaceScroll) spaceScroll.direction = event.shiftKey ? -1 : 1;
    if (key === ' ' || event.code === 'Space') {
      event.preventDefault(); cancelRestore();
      if (!spaceScroll && !event.repeat) startSpaceScroll(event.shiftKey ? -1 : 1);
      return;
    }
    let action;
    if (key === 'arrowleft') action = () => goChapter(-1);
    else if (key === 'arrowright') action = () => goChapter(1);
    else if (key === 'home') action = () => scrollToEdge(false);
    else if (key === 'end') action = () => scrollToEdge(true);
    else if (key === 'f' && !event.repeat) action = focus;
    else if (key === '+' || key === '=' || event.code === 'NumpadAdd') action = () => changeWidth(1);
    else if (key === '-' || event.code === 'NumpadSubtract') action = () => changeWidth(-1);
    else if (key === 'escape') action = () => {save(); location.hash = storyRoute(current.story);};
    if (action) {event.preventDefault(); stopSpaceScroll(); cancelRestore(); action();}
  });
  window.MangaReader = {render, leave, continueRoute, renderRecent};
})();
