import FreeCAD as App
import FreeCADGui as Gui

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets


class BaseTaskPanel:
    """
    A reusable base class for FreeCAD Task Panels.
    Handles UI loading, debounced previews, and safe undo transactions.
    """
    def __init__(self, ui_file_path, has_preview=True):
        self.form = Gui.PySideUic.loadUi(ui_file_path)
        self.has_preview = has_preview

        if self.has_preview:
            self.preview_timer = QtCore.QTimer()
            self.preview_timer.setSingleShot(True)
            self.preview_timer.setInterval(150)
            self.preview_timer.timeout.connect(self._trigger_preview)

            App.ActiveDocument.openTransaction("Preview Transaction")
            self.preview_obj = App.ActiveDocument.addObject("Part::Feature", "PreviewObject")

        self.setup_ui()

        if self.has_preview:
            self.queue_preview()

    def setup_ui(self):
        pass

    def queue_preview(self, *args):
        if self.has_preview:
            self.preview_timer.start()

    def _trigger_preview(self):
        if hasattr(self.form, "live_preview_cb") and not self.form.live_preview_cb.isChecked():
            return

        try:
            shape = self.calculate_preview()
            if shape and not shape.isNull() and self.preview_obj:
                self.preview_obj.Shape = shape
                self.preview_obj.recompute()
        except Exception as e:
            App.Console.PrintWarning(f"Preview calculation error: {e}\n")

    def calculate_preview(self):
        return None

    def generate_final(self):
        pass

    def getStandardButtons(self):
        return (QtWidgets.QDialogButtonBox.Ok |
                QtWidgets.QDialogButtonBox.Cancel).value

    def accept(self):
        if self.has_preview:
            App.ActiveDocument.abortTransaction()

        App.ActiveDocument.openTransaction("Apply Twist Extrude")
        try:
            self.generate_final()
            App.ActiveDocument.commitTransaction()
        except Exception as e:
            App.ActiveDocument.abortTransaction()
            App.Console.PrintError(f"Generation failed: {e}\n")

        Gui.Control.closeDialog()

    def reject(self):
        if self.has_preview:
            App.ActiveDocument.abortTransaction()
            
        Gui.Control.closeDialog()
