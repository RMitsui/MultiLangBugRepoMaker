class buginfo:
    def __init__(self, num, title, body, create_at, closed_at):
        self.num = num
        self.title = title
        self.body = body
        self.create_at = create_at
        self.closed_at = closed_at
        self.fixed = []
