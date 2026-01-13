# al_context.py

class ALContext:
    def __init__(self):
        self.last_app = None
        self.last_role = None
        self.last_action = None

    def remember_app(self, app):
        self.last_app = app

    def remember_role(self, role):
        self.last_role = role

    def remember_action(self, action):
        self.last_action = action

    def clear(self):
        self.__init__()
