import FreeCAD as App
import FreeCADGui as Gui

from freecad.twistextrude.ui.task_panel import SmartTwistTaskPanel

class TwistExtrudeCommand:
    Name = "TwistExtrude_Generate"

    def GetResources(self):
        return {
            "Pixmap": "TwistExtrude",
            "MenuText": "Twist Extrude",
            "ToolTip": "Generate a smart twist extrusion or swept path loft"
        }

    def Activated(self):
        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        sel = Gui.Selection.getSelection()
        if not sel or not hasattr(sel[0], "TypeId") or "Sketcher::SketchObject" not in sel[0].TypeId:
            App.Console.PrintError("Error: The first selected object must be a Sketch (Profile).\n")
            return
            
        prof_obj = sel[0]
        pth_obj = sel[1] if len(sel) >= 2 else None
        
        panel = SmartTwistTaskPanel(prof_obj, pth_obj)
        Gui.Control.showDialog(panel)

    def IsActive(self):
        return App.ActiveDocument is not None

    @classmethod
    def Install(cls):
        if App.GuiUp:
            Gui.addCommand(cls.Name, cls())
