# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.


from iris.test_case import *


class Test(BaseTest):
    def __init__(self, app):
        BaseTest.__init__(self, app)
        self.meta = 'Bookmarks can be opened from Bookmarks menu.'
        self.test_case_id = '4095'
        self.test_suite_id = '75'

    def setup(self):
        """Test case setup

        This overrides the setup method in the BaseTest class, so that it can use a brand new profile.
        """
        BaseTest.setup(self)
        self.profile = Profile.TEN_BOOKMARKS
        return

    def run(self):
        bookmarks_menu_pattern = LibraryMenu.BOOKMARKS_OPTION
        menu_bookmark_pattern = Pattern('moz_bookmark_from_menu.png')

        right_upper_corner = Region(SCREEN_WIDTH / 2, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        navigate('about:blank')

        open_library_menu(bookmarks_menu_pattern)

        moz_bookmark_menu_right_corner_assert = right_upper_corner.exists(menu_bookmark_pattern, 10)
        assert_true(self, moz_bookmark_menu_right_corner_assert,
                    'Moz bookmark can be accessed from the Bookmarks Menu.')

        right_upper_corner.click(menu_bookmark_pattern)

        mozilla_page_assert = exists(LocalWeb.MOZILLA_LOGO, 10)
        assert_true(self, mozilla_page_assert, 'Mozilla page has been successfully accessed from the Bookmarks Menu.')