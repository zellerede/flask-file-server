
try:
    from custom_actions import CustomActions
    actionClasses = [CustomActions]
except ImportError:
    actionClasses = []


class DefaultActions:

    def before_mkdir(self, dirpath):
        pass

    def after_mkdir(self, dirpath):
        pass

    def before_upload(self, filepath):
        pass

    def on_chunk(self, chunk, filepath):
        pass

    def after_upload(self, filepath):
        pass

    def before_download(self, filepath):
        pass

    def after_download(self, filepath):
        pass


actionClasses.append(DefaultActions)
Actions = type('Actions', tuple(actionClasses), {})
actions = Actions()
