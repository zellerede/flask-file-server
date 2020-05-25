
try:
    from custom_actions import CustomActions
    actionClasses = [CustomActions]
except ImportError:
    actionClasses = []


class DefaultActions:

    def before_upload(self, filepath):
        print(f"Triggered before upload for {filepath}!")  ###
        pass


actionClasses.append(DefaultActions)
Actions = type('Actions', tuple(actionClasses), {})
actions = Actions()
before_upload = actions.before_upload
# ...
