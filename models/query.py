import common


class Query:

    def __init__(self, b64):
        try:
            self.b64 = b64
            self.query = common.url_base64_decode(b64)
            self.hostname = common.get_hostname(self.query)
            self.bare = common.get_bare_hostname(self.query)
            self.err = False
        except Exception:
            self.err = True