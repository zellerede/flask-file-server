
class CustomActions:
    """ Custom actions for file events.
        To stop actual processing, just raise an exception.

        The following attributes from the file server entity
        will be attached to the actually used instances:
        - ...... (todo)
    """

    def before_upload(self, filepath):
        """ Triggered before saving given file to server """
        print(f"Custom action triggered for {filepath}!")

    def after_upload(self, filepath):
        """ Triggered after saving given file to server """
        print(f"Custom action triggered for {filepath}!")

    def before_download(self, filepath):
        """ Triggered before viewing/downloading given file """

    def after_download(self, filepath):
        """ Triggered after given file downloaded """
