import FreeCAD as App
import FreeCADGui as Gui


def get_active_body(base_obj=None):
    """Finds the active PartDesign Body, falling back to the base object's parent."""
    active_body = None
    if Gui.ActiveDocument:
        active_body = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody")

    if not active_body and base_obj:
        for parent in base_obj.InList:
            if parent.isDerivedFrom("PartDesign::Body"):
                active_body = parent
                break

    if not active_body:
        App.Console.PrintWarning(
            "Warning: No Active Body found. Placing objects in root.\n")

    return active_body
