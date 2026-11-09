import shutil
import os
import tempfile
from pathlib import Path
import unittest
from app.scanner import scan_library, write_library
from tests.web_support import create_library

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipIf(sync_playwright is None, 'Cần cài Playwright để kiểm thử browser thật')
class BrowserCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / 'test-results').mkdir(exist_ok=True)
        cls.web_temp = tempfile.TemporaryDirectory(dir=ROOT / 'test-results')
        cls.addClassCleanup(cls.web_temp.cleanup)
        cls.image_temp = tempfile.TemporaryDirectory(prefix='Truyện ngoài project # % & ')
        cls.addClassCleanup(cls.image_temp.cleanup)
        cls.web = Path(cls.web_temp.name) / 'web'
        shutil.copytree(ROOT / 'web', cls.web, ignore=shutil.ignore_patterns('library.js'))
        cls.library_root = Path(cls.image_temp.name)
        create_library(cls.library_root)
        cls.data = scan_library(cls.library_root)
        write_library(cls.web / 'js/library.js', cls.data)
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        cls.browser = cls.playwright.chromium.launch(channel=os.environ.get('MANGA_BROWSER_CHANNEL') or None)
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 900})
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.network = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('request', lambda request: self.network.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
        self.addCleanup(lambda: self.assertEqual(self.errors, [], 'Lỗi JavaScript chưa xử lý'))
        self.addCleanup(lambda: self.assertEqual(self.network, [], 'Website không được dùng Internet'))
        self.url = (self.web / 'index.html').as_uri()
        self.page.goto(self.url + '#/library')
        self.page.wait_for_selector('.story-card')


class WebTests(BrowserCase):
    def test_file_library_pagination_external_cover(self):
        self.assertTrue(self.page.url.startswith('file:///'))
        self.assertEqual(self.page.locator('.story-card').count(), 20)
        image = self.page.locator('.story-card img').first
        self.page.wait_for_function("document.querySelector('.story-card img').naturalWidth > 0")
        self.assertIn('%23', image.get_attribute('src'))
        self.assertNotIn(str(self.web), str(self.library_root))
        self.page.get_by_role('button', name='Trang sau').click()
        self.assertEqual(self.page.locator('.story-card').count(), 5)
        self.assertTrue(self.page.get_by_role('button', name='Trang sau').is_disabled())
        self.assertEqual(self.errors, [])

    def test_live_accent_search_resets_page_and_empty(self):
        self.page.get_by_role('button', name='Trang sau').click()
        self.page.locator('#search').fill('  TRUYEN   dac biet ')
        self.assertEqual(self.page.locator('.story-card').count(), 1)
        self.assertIn('Truyện Đặc Biệt', self.page.locator('.story-card').inner_text())
        self.assertEqual(self.page.locator('#page-indicator').inner_text(), 'Trang 1 / 1')
        self.page.locator('#search').fill('no result xyz')
        self.assertEqual(self.page.locator('.story-card').count(), 0)
        self.assertTrue(self.page.get_by_text('Không tìm thấy truyện', exact=True).is_visible())

    def test_story_natural_order_hash_reload_back_forward_safe_names(self):
        self.page.locator('#search').fill('dac biet')
        self.page.locator('.story-card').click()
        self.page.wait_for_selector('.chapter-link')
        self.assertEqual(self.page.locator('.chapter-link strong').all_text_contents(), ['Tập 1', 'Tập 2', 'Tập 10'])
        self.page.reload()
        self.page.wait_for_selector('.chapter-link')
        self.page.go_back()
        self.page.wait_for_selector('.story-card')
        self.page.go_forward()
        self.page.wait_for_selector('.chapter-link')
        self.assertEqual(self.errors, [])

    def test_invalid_route_and_responsive(self):
        self.page.goto(self.url + '#/story/%E0%A4%A')
        self.assertTrue(self.page.get_by_text('Không tìm thấy nội dung', exact=True).is_visible())
        self.page.goto(self.url + '#/library')
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_empty_and_cover_failure(self):
        self.page.evaluate("window.MANGA_LIBRARY.stories[0].cover = 'file:///does-not-exist.png'; MangaApp.route()")
        self.page.wait_for_selector('.cover-placeholder')
        self.assertEqual(self.errors, [])
        self.page.evaluate('MangaApp.stories.splice(0); MangaApp.route()')
        self.assertTrue(self.page.get_by_text('Thư viện đang trống', exact=True).is_visible())

    def test_alternative_library_config(self):
        self.context.add_init_script("Object.defineProperty(window,'MANGA_CONFIG',{set(value){Object.assign(value,{STORIES_PER_PAGE:7,LIVE_SEARCH:false,SEARCH_IGNORE_ACCENTS:false,DARK_MODE:false});this.testConfig=value},get(){return this.testConfig}})")
        self.page.reload()
        self.assertEqual(self.page.locator('.story-card').count(), 7)
        self.assertTrue(self.page.locator('html').evaluate("node=>node.classList.contains('light')"))
        self.page.locator('#search').fill('truyen dac biet')
        self.assertEqual(self.page.locator('.story-card').count(), 7)
        self.page.locator('#search').press('Enter')
        self.assertEqual(self.page.locator('.story-card').count(), 0)
        self.page.locator('#search').fill('Truyện Đặc Biệt')
        self.page.locator('#search').press('Enter')
        self.assertEqual(self.page.locator('.story-card').count(), 1)
