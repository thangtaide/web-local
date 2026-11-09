from tests.test_web import BrowserCase


class ReaderTests(BrowserCase):
    def open_reader(self, story_index=0, chapter_index=0):
        self.page.evaluate('MANGA_CONFIG.SMOOTH_SCROLL = false')
        story = self.data['stories'][story_index]
        chapter = story['chapters'][chapter_index]
        self.page.goto(self.url + f"#/read/{story['id']}/{chapter['id']}?start=1")
        self.ready()
        return story, chapter

    def ready(self):
        self.page.wait_for_function("() => {const stage=document.querySelector('.reader-stage'); return stage && stage.getAttribute('aria-busy') === 'false' && stage.dataset.route === location.hash.split('?')[0];}")

    def progress(self, story, chapter):
        return self.page.evaluate('([story,chapter]) => JSON.parse(localStorage.getItem("manga-reader.progress.v1"))[story].chapters[chapter]', [story['id'], chapter['id']])

    def save_at_second_image(self, ratio=.35):
        self.page.evaluate('(ratio) => {const rect = document.querySelectorAll(".reader-page")[1].getBoundingClientRect(); scrollTo(0, scrollY + rect.top + rect.height * ratio - document.querySelector(".reader-top").offsetHeight - 1);}', ratio)
        self.page.wait_for_timeout(260)

    def test_vertical_images_zero_gap_lazy_responsive_and_width(self):
        self.open_reader()
        self.assertEqual(self.page.locator('.reader-image').count(), 3)
        self.assertEqual(self.page.locator('.reader-image').first.get_attribute('loading'), 'eager')
        self.assertEqual(self.page.locator('.reader-image').last.get_attribute('loading'), 'lazy')
        sizes = self.page.evaluate('Array.from(document.querySelectorAll(".reader-page")).map(x=>{const r=x.getBoundingClientRect(); return {top:r.top,bottom:r.bottom,width:r.width,height:r.height};})')
        self.assertAlmostEqual(sizes[0]['width'], 900, delta=1)
        self.assertAlmostEqual(sizes[0]['height'] / sizes[0]['width'], 2, delta=.01)
        self.assertAlmostEqual(sizes[0]['bottom'], sizes[1]['top'], delta=1)
        self.page.keyboard.press('Equal')
        self.assertEqual(self.page.locator('.width-label').inner_text(), '1000px')
        self.page.keyboard.press('NumpadAdd')
        self.assertEqual(self.page.locator('.width-label').inner_text(), '1100px')
        self.page.get_by_role('button', name='Giảm chiều rộng').click()
        self.assertEqual(self.page.locator('.width-label').inner_text(), '1000px')
        self.page.reload(); self.ready()
        self.assertEqual(self.page.locator('.width-label').inner_text(), '1000px')
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.assertTrue(self.page.evaluate('document.querySelector(".reader-page").getBoundingClientRect().width <= innerWidth'))
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.assertEqual(self.errors, [])

    def test_focus_hides_four_controls_keeps_anchor_and_keyboard(self):
        story, chapter = self.open_reader()
        self.save_at_second_image()
        before = self.progress(story, chapter)
        self.page.keyboard.press('f')
        for selector in ['.reader-top', '.reader-bottom', '.reader-left', '.reader-right', '.chapter-end']:
            self.assertFalse(self.page.locator(selector).is_visible(), selector)
        self.assertEqual(self.page.evaluate('getComputedStyle(document.getElementById("app")).padding'), '0px')
        self.page.mouse.move(200, 200)
        self.assertFalse(self.page.locator('.reader-top').is_visible())
        after = self.progress(story, chapter)
        self.assertEqual(before['page'], after['page'])
        self.assertAlmostEqual(before['ratio'], after['ratio'], delta=.005)
        self.page.keyboard.press('Space')
        self.page.wait_for_timeout(230)
        self.assertGreater(self.progress(story, chapter)['ratio'], after['ratio'])
        self.page.keyboard.press('f')
        for selector in ['.reader-top', '.reader-bottom', '.reader-left', '.reader-right']:
            self.assertTrue(self.page.locator(selector).is_visible(), selector)
        self.page.screenshot(path='test-results/reader.png')
        self.assertEqual(self.errors, [])

    def test_shortcuts_navigation_edges_and_end_button(self):
        story, chapter = self.open_reader()
        self.assertTrue(self.page.locator('.reader-left').is_disabled())
        start_url = self.page.url
        self.page.keyboard.press('ArrowLeft')
        self.assertEqual(self.page.url, start_url)
        self.page.keyboard.press('Space')
        self.page.wait_for_timeout(50)
        self.assertAlmostEqual(self.page.evaluate('scrollY'), 720, delta=2)
        self.page.keyboard.press('Shift+Space')
        self.assertAlmostEqual(self.page.evaluate('scrollY'), 0, delta=2)
        self.page.keyboard.press('End')
        self.assertTrue(self.page.get_by_role('button', name='Đọc tập tiếp theo').is_visible())
        self.page.get_by_role('button', name='Đọc tập tiếp theo').click()
        self.ready()
        self.assertIn(story['chapters'][1]['id'], self.page.url)
        self.page.keyboard.press('ArrowRight'); self.ready()
        self.assertTrue(self.page.locator('.reader-right').is_disabled())
        self.assertEqual(self.page.get_by_role('button', name='Đọc tập tiếp theo').count(), 0)
        self.page.keyboard.press('Home')
        self.assertEqual(self.page.evaluate('scrollY'), 0)
        self.page.keyboard.press('ArrowLeft'); self.ready()
        self.page.keyboard.press('Escape')
        self.page.wait_for_selector('.chapter-link')
        self.assertEqual(self.errors, [])

    def test_progress_resume_reload_resize_width_recent_and_per_chapter(self):
        story, chapter = self.open_reader()
        self.save_at_second_image(.42)
        saved = self.progress(story, chapter)
        self.assertEqual(saved['page'], 1)
        self.assertAlmostEqual(saved['ratio'], .42, delta=.005)
        self.page.reload(); self.ready()
        restored = self.progress(story, chapter)
        self.assertEqual(saved['page'], restored['page'])
        self.assertAlmostEqual(saved['ratio'], restored['ratio'], delta=.005)
        self.page.keyboard.press('+')
        changed = self.progress(story, chapter)
        self.assertAlmostEqual(saved['ratio'], changed['ratio'], delta=.005)
        self.page.set_viewport_size({'width': 700, 'height': 900})
        self.page.wait_for_timeout(250)
        resized = self.progress(story, chapter)
        self.assertEqual(resized['page'], 1)
        self.assertAlmostEqual(resized['ratio'], .42, delta=.02)
        self.page.keyboard.press('ArrowRight'); self.ready()
        self.page.keyboard.press('Escape'); self.page.wait_for_selector('.chapter-link')
        self.page.get_by_role('link', name='Đọc tiếp', exact=False).click(); self.ready()
        self.assertIn(story['chapters'][1]['id'], self.page.url)
        self.page.keyboard.press('Escape'); self.page.wait_for_selector('.chapter-link')
        self.page.get_by_role('link', name='Thư viện', exact=False).first.click()
        self.page.wait_for_selector('.recent-card')
        self.assertEqual(self.page.locator('.recent-card').count(), 1)
        self.assertIn(story['name'], self.page.locator('.recent-card').inner_text())
        self.assertEqual(self.progress(story, chapter)['page'], 1)

    def test_unavailable_and_corrupt_storage_do_not_break_reading(self):
        self.context.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new Error('blocked')}})")
        self.page.reload()
        self.open_reader()
        self.assertTrue(self.page.locator('.storage-notice').is_visible())
        self.page.keyboard.press('f')
        self.assertFalse(self.page.locator('.storage-notice').is_visible())
        self.page.keyboard.press('f')
        self.page.keyboard.press('+')
        self.page.keyboard.press('ArrowRight'); self.ready()
        self.assertEqual(self.errors, [])

    def test_missing_image_and_chapter_fallback(self):
        story = self.data['stories'][0]
        self.page.evaluate("MangaApp.stories[0].chapters[0].images[0] = 'file:///missing-page.png'")
        self.open_reader()
        self.page.wait_for_selector('.image-error')
        self.assertEqual(self.page.locator('.reader-image').count(), 3)
        self.page.goto(self.url + f"#/read/{story['id']}/deleted-chapter?resume=1")
        self.ready()
        self.assertTrue(self.page.locator('.reader-notice').is_visible())
        self.assertIn(story['chapters'][0]['name'], self.page.locator('.reader-title').inner_text())
        self.assertEqual(self.errors, [])

    def test_modifiers_inputs_width_bounds_and_f5_not_captured(self):
        self.open_reader()
        self.page.keyboard.press('Control+f')
        self.assertTrue(self.page.locator('.reader-top').is_visible())
        self.page.evaluate("let input=document.createElement('input'); input.id='typing-test'; document.body.append(input); input.focus()")
        for key in ['f', '+', 'ArrowRight', 'Space']:
            self.page.keyboard.press(key)
        self.assertEqual(self.page.locator('.width-label').inner_text(), '900px')
        self.page.locator('#typing-test').evaluate('(node)=>node.remove()')
        for _ in range(12): self.page.keyboard.press('+')
        self.assertEqual(self.page.locator('.width-label').inner_text(), '1600px')
        for _ in range(15): self.page.keyboard.press('-')
        self.assertEqual(self.page.locator('.width-label').inner_text(), '400px')
        prevented = self.page.evaluate("() => {const event=new KeyboardEvent('keydown',{key:'F5',bubbles:true,cancelable:true}); window.dispatchEvent(event); return event.defaultPrevented;}")
        self.assertFalse(prevented)

    def test_delayed_images_restore_exact_position_without_later_jump(self):
        story, chapter = self.open_reader()
        self.save_at_second_image(.55)
        self.context.add_init_script("""(() => {const native=Element.prototype.setAttribute; Element.prototype.setAttribute=function(name,value){if(name==='src' && this.classList.contains('reader-image')) {setTimeout(()=>native.call(this,name,value),350);} else native.call(this,name,value);};})()""")
        self.page.reload(); self.ready()
        saved = self.progress(story, chapter)
        self.assertEqual(saved['page'], 1)
        self.assertAlmostEqual(saved['ratio'], .55, delta=.01)
        at = self.page.evaluate('scrollY')
        self.page.wait_for_timeout(550)
        self.assertAlmostEqual(self.page.evaluate('scrollY'), at, delta=2)
        self.assertEqual(self.errors, [])

    def test_recent_limit_no_duplicates_and_deleted_page_name_fallback(self):
        for index in range(12): self.open_reader(index)
        self.page.goto(self.url + '#/library')
        self.page.wait_for_selector('.recent-card')
        self.assertEqual(self.page.locator('.recent-card').count(), 10)
        self.assertEqual(len(set(self.page.locator('.recent-card h3').all_text_contents())), 10)
        story, chapter = self.open_reader()
        self.save_at_second_image(.25)
        self.page.keyboard.press('Escape'); self.page.wait_for_selector('.chapter-link')
        self.page.evaluate('MangaApp.stories[0].chapters[0].images.shift(); MangaApp.stories[0].chapters[0].image_sizes.shift()')
        self.page.get_by_role('link', name='Đọc tiếp', exact=False).click(); self.ready()
        self.assertEqual(self.progress(story, chapter)['page'], 0)
        self.assertAlmostEqual(self.progress(story, chapter)['ratio'], .25, delta=.01)
