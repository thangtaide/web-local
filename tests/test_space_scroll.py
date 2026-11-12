"""Real Chrome key-hold regressions, using only generated local image fixtures."""
from tests.test_web import BrowserCase


class SpaceScrollTests(BrowserCase):
    def open_reader(self, smooth=True):
        story=self.data['stories'][0];chapter=story['chapters'][0]
        self.page.goto(self.url+f"#/read/{story['id']}/{chapter['id']}?start=1")
        self.page.wait_for_function("document.querySelector('.reader-stage')?.getAttribute('aria-busy') === 'false'")
        self.page.evaluate('(smooth)=>MANGA_CONFIG.SMOOTH_SCROLL=smooth',smooth)

    def y(self):return self.page.evaluate('scrollY')

    def test_tap_still_scrolls_one_page_and_finishes_smoothly(self):
        self.open_reader();self.page.keyboard.press('Space');self.page.wait_for_timeout(650)
        self.assertAlmostEqual(self.y(),720,delta=3)
        self.page.wait_for_timeout(200);self.assertAlmostEqual(self.y(),720,delta=3)

    def test_holding_without_repeat_scrolls_beyond_one_page(self):
        self.open_reader();self.page.keyboard.down('Space')
        self.page.wait_for_timeout(1300);self.page.keyboard.up('Space')
        self.assertGreater(self.y(),1200)

    def test_repeat_events_do_not_restart_smooth_animation(self):
        self.open_reader();self.page.keyboard.down('Space')
        for _ in range(40):
            self.page.wait_for_timeout(30);self.page.keyboard.down('Space')
        self.page.keyboard.up('Space');stopped=self.y()
        self.assertGreater(stopped,1200)
        self.page.wait_for_timeout(250);self.assertAlmostEqual(self.y(),stopped,delta=2)

    def test_shift_can_reverse_direction_while_space_is_held(self):
        self.open_reader();self.page.evaluate("scrollTo({top:2200,behavior:'instant'})")
        self.page.keyboard.down('Space');self.page.wait_for_timeout(500);turn=self.y()
        self.page.keyboard.down('Shift');self.page.wait_for_timeout(450);up=self.y()
        self.assertLess(up,turn-300)
        self.page.keyboard.up('Shift');self.page.wait_for_timeout(400);self.page.keyboard.up('Space')
        self.assertGreater(self.y(),up+300)

    def test_home_cancels_hold_and_repeat_does_not_restart_it(self):
        self.open_reader();self.page.keyboard.down('Space');self.page.wait_for_timeout(450)
        self.page.keyboard.press('Home')
        for _ in range(4):
            self.page.keyboard.down('Space');self.page.wait_for_timeout(40)
        self.assertAlmostEqual(self.y(),0,delta=2);self.page.keyboard.up('Space')

    def test_blur_and_hidden_tab_stop_motion_without_waiting_for_keyup(self):
        self.open_reader()
        for event in ('blur','hidden'):
            self.page.keyboard.down('Space');self.page.wait_for_timeout(250)
            if event=='blur':self.page.evaluate("window.dispatchEvent(new Event('blur'))")
            else:self.page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
            stopped=self.y();self.page.wait_for_timeout(250)
            self.assertAlmostEqual(self.y(),stopped,delta=2)
            self.page.keyboard.up('Space')
            if event=='hidden':self.page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:false})")

    def test_route_change_cancels_motion_and_does_not_change_chapter_at_end(self):
        self.open_reader();self.page.keyboard.down('Space');self.page.wait_for_timeout(300)
        self.page.evaluate("location.hash='/library'");self.page.wait_for_selector('.story-card')
        self.page.wait_for_timeout(200);self.assertAlmostEqual(self.y(),0,delta=2);self.page.keyboard.up('Space')
        self.open_reader();url=self.page.url;self.page.keyboard.press('End')
        self.page.keyboard.down('Space');self.page.wait_for_timeout(350);self.page.keyboard.up('Space')
        self.assertEqual(self.page.url,url)

    def test_editable_focus_cancels_hold_without_hijacking_typing(self):
        self.open_reader();self.page.keyboard.down('Space');self.page.wait_for_timeout(250)
        self.page.evaluate("let input=document.createElement('input');input.id='hold-input';input.style='position:fixed;top:100px';document.body.append(input);input.focus({preventScroll:true})")
        stopped=self.y();self.page.wait_for_timeout(250);self.assertAlmostEqual(self.y(),stopped,delta=2)
        self.page.keyboard.up('Space');self.page.keyboard.press('Space')
        self.assertEqual(self.page.locator('#hold-input').input_value(),' ')

    def test_instant_scroll_config_retains_page_step_and_supports_hold(self):
        self.open_reader(smooth=False);self.page.keyboard.press('Space');self.assertAlmostEqual(self.y(),720,delta=2)
        self.page.keyboard.down('Shift');self.page.keyboard.down('Space');self.page.wait_for_timeout(1100)
        self.page.keyboard.up('Space');self.page.keyboard.up('Shift');self.assertAlmostEqual(self.y(),0,delta=2)
