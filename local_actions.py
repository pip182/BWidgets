from actions import Actions


class LocalActions(Actions):

    def custom_greet(self):
        return "Hello from LocalActions in local_actions.py!"

    def another_custom_action(self):
        return "This is another custom action from local_actions.py."

    def greet_user(self):
        return "Overridden greeting from LocalActions."
