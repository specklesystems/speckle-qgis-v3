from speckle.connectors.UI.models import DocumentModelStore


class QgisDocumentStore(DocumentModelStore):
    def __init__(self):
        self.models = []
        self.is_document_init = False

    def on_project_closing(self):
        return

    def on_project_saving(self):
        return

    def host_app_save_state(self, state):
        # return super().host_app_save_state(state)
        # TODO: replace model cards written in QGIS project
        return

    def load_state(self):
        # return super().load_state()
        # TODO: get the model cards written into the document
        return
