/* All user-supplied names enter the DOM through textContent, never HTML. */
(() => {
  'use strict';
  const config = window.MANGA_CONFIG;
  const library = window.MANGA_LIBRARY;
  const stories = library && library.schema_version === 1 && Array.isArray(library.stories) ? library.stories : [];
  const root = document.getElementById('app');
  const state = {query: '', page: 1};
  document.documentElement.classList.toggle('light', !config.DARK_MODE);

  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (key === 'class') node.className = value;
      else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
      else if (value !== false && value != null) node.setAttribute(key, value === true ? '' : value);
    }
    for (const child of children.flat()) {
      if (child != null) node.append(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return node;
  }
  const storyRoute = story => '#/story/' + encodeURIComponent(story.id);
  const readRoute = (story, chapter, resume = false) => '#/read/' + encodeURIComponent(story.id) + '/' + encodeURIComponent(chapter.id) + (resume ? '?resume=1' : '?start=1');
  function cover(story) {
    const frame = el('div', {class: 'cover'});
    const image = el('img', {src: story.cover, alt: 'Bìa ' + story.name, loading: 'lazy', decoding: 'async'});
    image.addEventListener('error', () => frame.replaceChildren(el('span', {class: 'cover-placeholder'}, '冊', el('small', {}, 'Chưa tải được ảnh bìa'))), {once: true});
    frame.append(image);
    return frame;
  }
  function normalize(text) {
    let value = String(text).toLocaleLowerCase('vi').trim().replace(/\s+/g, ' ');
    if (config.SEARCH_IGNORE_ACCENTS) value = value.normalize('NFD').replace(/\p{M}/gu, '').replace(/đ/g, 'd');
    return value;
  }
  function empty(title, description) {
    return el('div', {class: 'empty'}, el('span', {class: 'empty-mark', 'aria-hidden': 'true'}, '冊'), el('h2', {}, title), el('p', {}, description));
  }
  function button(text, handler, attrs = {}) {
    return el('button', {type: 'button', onclick: handler, ...attrs}, text);
  }
  function renderLibrary() {
    document.title = 'Thư viện · Manga Reader';
    const hero = el('section', {class: 'hero'}, el('p', {class: 'eyebrow'}, 'THƯ VIỆN CÁ NHÂN'),
      el('h1', {}, 'Mỗi trang, một thế giới.'), el('p', {class: 'subtle'}, 'Chọn một câu chuyện và dành chút thời gian cho riêng bạn.'),
      el('div', {class: 'library-stats'}, el('strong', {}, stories.length), ' truyện trong thư viện', el('span', {}, '•'), 'Luôn ở đây, kể cả khi ngoại tuyến'));
    const input = el('input', {id: 'search', type: 'search', placeholder: 'Tìm tên truyện…', 'aria-label': 'Tìm tên truyện', value: state.query, autocomplete: 'off'});
    const results = el('div', {id: 'library-results', 'aria-live': 'polite'});
    const update = () => { state.query = input.value; state.page = 1; renderResults(results); };
    input.addEventListener(config.LIVE_SEARCH ? 'input' : 'change', update);
    const search = el('form', {class: 'search-bar', onsubmit: event => {event.preventDefault(); update();}}, el('label', {for: 'search'}, '⌕'), input, el('span', {class: 'search-hint'}, 'Tìm cả khi không dấu'));
    root.replaceChildren(hero);
    if (window.MangaReader) window.MangaReader.renderRecent(root);
    root.append(el('section', {class: 'collection'}, el('div', {class: 'section-title'}, el('h2', {}, 'Tất cả truyện'), el('span', {class: 'subtle'}, 'Bộ sưu tập của bạn')), search, results));
    renderResults(results);
  }
  function renderResults(container) {
    const query = normalize(state.query);
    const filtered = stories.filter(story => normalize(story.name).includes(query));
    const perPage = Math.max(1, Number(config.STORIES_PER_PAGE) || 20);
    const pages = Math.max(1, Math.ceil(filtered.length / perPage));
    state.page = Math.min(Math.max(1, state.page), pages);
    if (!filtered.length) {
      container.replaceChildren(empty(stories.length ? 'Không tìm thấy truyện' : 'Thư viện đang trống', stories.length ? 'Thử một tên khác hoặc bớt từ tìm kiếm.' : 'Mở Manga Manager, chọn thư mục cha và nhấn Mở Web Đọc Truyện.'));
      return;
    }
    const grid = el('div', {class: 'story-grid'});
    for (const story of filtered.slice((state.page - 1) * perPage, state.page * perPage)) {
      grid.append(el('a', {class: 'story-card', href: storyRoute(story)}, cover(story), el('div', {class: 'card-info'}, el('h3', {}, story.name), el('p', {}, story.chapter_count + ' tập'))));
    }
    const turn = offset => {state.page += offset; renderResults(container); container.scrollIntoView({block: 'start'});};
    container.replaceChildren(el('p', {class: 'result-count'}, filtered.length + ' truyện' + (query ? ' phù hợp' : '')), grid,
      el('nav', {class: 'pagination', 'aria-label': 'Phân trang'}, button('← Trang trước', () => turn(-1), {disabled: state.page <= 1}), el('span', {id: 'page-indicator'}, 'Trang ' + state.page + ' / ' + pages), button('Trang sau →', () => turn(1), {disabled: state.page >= pages})));
  }
  function renderStory(story) {
    document.title = story.name + ' · Manga Reader';
    const first = story.chapters[0];
    const resume = window.MangaReader ? window.MangaReader.continueRoute(story) : readRoute(story, first, true);
    root.replaceChildren(el('a', {class: 'back-link', href: '#/library'}, '← Thư viện'),
      el('section', {class: 'story-detail'}, cover(story), el('div', {}, el('p', {class: 'eyebrow'}, 'TRONG BỘ SƯU TẬP'), el('h1', {}, story.name), el('p', {class: 'subtle'}, story.chapter_count + ' tập · Đọc theo chiều dọc'), el('div', {class: 'actions'}, el('a', {class: 'button primary', href: resume}, 'Đọc tiếp →'), el('a', {class: 'button', href: readRoute(story, first)}, 'Đọc từ đầu')))),
      el('section', {class: 'chapters'}, el('div', {class: 'section-title'}, el('h2', {}, 'Danh sách tập'), el('span', {class: 'subtle'}, story.chapter_count + ' tập')),
        el('div', {class: 'chapter-list'}, story.chapters.map((chapter, index) => el('a', {class: 'chapter-link', href: readRoute(story, chapter)}, el('span', {class: 'chapter-number'}, String(index + 1).padStart(2, '0')), el('strong', {}, chapter.name), el('span', {class: 'subtle'}, chapter.image_count + ' ảnh'), el('span', {'aria-hidden': 'true'}, '→'))))));
  }
  function route() {
    if (window.MangaReader) window.MangaReader.leave();
    document.body.classList.remove('reading', 'focus-mode');
    window.scrollTo(0, 0);
    let parts;
    try { parts = (location.hash.slice(1).split('?')[0] || '/library').split('/').filter(Boolean).map(decodeURIComponent); }
    catch (_) { parts = ['invalid']; }
    const story = stories.find(item => item.id === parts[1]);
    if (!parts.length || parts[0] === 'library') return renderLibrary();
    if (parts[0] === 'story' && story) return renderStory(story);
    if (parts[0] === 'read' && story && window.MangaReader) return window.MangaReader.render(story, parts[2]);
    root.replaceChildren(el('a', {class: 'back-link', href: '#/library'}, '← Thư viện'), empty('Không tìm thấy nội dung', 'Truyện hoặc tập có thể đã đổi tên. Hãy quay về thư viện.'));
  }
  window.MangaApp = {config, stories, root, el, cover, button, storyRoute, readRoute, route};
  window.addEventListener('hashchange', route);
  window.addEventListener('DOMContentLoaded', route);
})();
