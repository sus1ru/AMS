class UrlRouter:
    URL_MAPPINGS = {}

    @classmethod
    def add(cls, path, method, view):
        cls.URL_MAPPINGS[path] = (view, method)

    @classmethod
    def map_url(cls, path):
        return cls.URL_MAPPINGS.get(path)

url_router = UrlRouter()