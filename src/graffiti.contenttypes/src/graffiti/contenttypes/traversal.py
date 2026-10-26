from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.publisher.interfaces.http import IHTTPRequest


class ContentProxyTraverser(DefaultPublishTraverse):
    adapts(IHTTPRequest)

    def __init__(self, context, request):
        super().__init__(context, request)

    def publishTraverse(self, request, name):
        # noinspection PyBroadException
        try:
            view = super().publishTraverse(
                request, name
            )
        except Exception:
            view = None

        if view:
            return view
        else:
            self.request = request
            self.request.set('disable_border', True)

            keywords = list()
            keyword_count = 0
            while self.has_more_names():
                if not name.startswith('@@'):
                    keywords.append(name)
                    keyword_count += 1
                name = self.next_name()

            webmirror_path = keywords
            webmirror_path.append(name)
            webmirror_path_str = '/'.join(webmirror_path)

            self.request.form = {'webmirror_path': webmirror_path_str}

            view_name = 'view'
            if 'assets/' in webmirror_path_str:
                view_name = 'webmirror_asset'

            view = getMultiAdapter(
                (self.context, self.request),
                name=view_name
            )
            return view

    def next_name(self):
        """ Pop the next name off of the traversal stack. """
        return self.request['TraversalRequestNameStack'].pop()

    def has_more_names(self):
        """ Are there names left for traversal? """
        return len(self.request['TraversalRequestNameStack']) > 0
