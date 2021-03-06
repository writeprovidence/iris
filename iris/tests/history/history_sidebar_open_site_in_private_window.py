# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.


from iris.test_case import *


class Test(BaseTest):

    def __init__(self, app):
        BaseTest.__init__(self, app)
        self.meta = 'This is a test that opens a page from the History sidebar using the \'Open in a New Private ' \
                    'Window\' button from the context menu.'
        self.test_case_id = '120122'
        self.test_suite_id = '2000'
        self.locales = ['en-US']

    def setup(self):
        """Test case setup

        This overrides the setup method in the BaseTest class, so that it can use a brand new profile.
        """
        BaseTest.setup(self)
        self.profile = Profile.BRAND_NEW

        return

    def run(self):
        history_sidebar_mozilla = LocalWeb.MOZILLA_BOOKMARK_SMALL
        search_history_box_pattern = Pattern('search_history_box.png')
        expand_button_history_sidebar_pattern = Pattern('expand_button_history_sidebar.png')

        # Open some pages to create some history.
        navigate(LocalWeb.MOZILLA_TEST_SITE)
        expected_1 = exists(LocalWeb.MOZILLA_LOGO, 10)
        assert_true(self, expected_1, 'Mozilla page loaded successfully.')

        new_tab()
        navigate(LocalWeb.FIREFOX_TEST_SITE)
        expected_2 = exists(LocalWeb.FIREFOX_LOGO, 10)
        assert_true(self, expected_2, 'Firefox page loaded successfully.')

        # Open the History sidebar.
        history_sidebar()
        expected_3 = exists(search_history_box_pattern, 10)
        assert_true(self, expected_3, 'Sidebar was opened successfully.')

        expected_4 = exists(expand_button_history_sidebar_pattern, 10)
        assert_true(self, expected_4, 'Expand history button displayed properly.')
        click(expand_button_history_sidebar_pattern)

        # Open a page from the History sidebar using the 'Open in a New Private Window' button from the context menu.

        expected_5 = exists(history_sidebar_mozilla, 10)
        assert_true(self, expected_5, 'Mozilla page is displayed in the History list successfully.')

        right_click(history_sidebar_mozilla, 1)
        time.sleep(Settings.FX_DELAY)
        type(text='p')

        expected_6 = exists(LocalWeb.MOZILLA_LOGO, 10)
        assert_true(self, expected_6, 'Mozilla page loaded successfully.')
