# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.


from iris.test_case import *


class Test(BaseTest):

    def __init__(self, app):
        BaseTest.__init__(self, app)
        self.meta = 'Bookmarks can be opened from the Bookmarks Sidebar.'
        self.test_case_id = '4094'
        self.test_suite_id = '75'

    def run(self):
        url = 'www.amazon.com'
        amazon_home_pattern = Pattern('amazon.png')
        amazon_bookmark_pattern = Pattern('amazon_bookmark.png')

        navigate(url)

        amazon_banner_assert = exists(amazon_home_pattern, 10)
        assert_true(self, amazon_banner_assert, 'Amazon page has been successfully loaded.')

        nav_bar_favicon_assert = exists(Pattern('amazon_favicon.png'), 15)
        assert_true(self, nav_bar_favicon_assert, 'Page is fully loaded and favicon displayed.')

        bookmark_page()

        navigate('about:blank')

        bookmarks_sidebar('open')

        paste('amazon')

        try:
            wait(amazon_bookmark_pattern, 10)
            logger.debug('Amazon bookmark is present in the Bookmark sidebar.')
            click(amazon_bookmark_pattern)
        except FindError:
            raise FindError('Amazon bookmark is NOT present in the Bookmark sidebar, aborting.')

        amazon_banner_assert = exists(amazon_home_pattern, 10)
        assert_true(self, amazon_banner_assert, 'Amazon page has been successfully loaded.')