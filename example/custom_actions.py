class CustomActions:

    def before_upload(self, filepath):
        print(f"Custom action triggered for {filepath}!")
