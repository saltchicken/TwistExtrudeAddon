"""Parametric FeaturePython definition for TwistExtrude."""

import FreeCAD as App

from freecad.twistextrude.config import TwistConfig
from freecad.twistextrude.core import generate_twist_shape
from freecad.twistextrude.resources import Resources


class TwistExtrudeFeature:
    """Parametric FeaturePython object that generates the final Twist shape."""

    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "TwistExtrudeFeature"
        self.setup_properties(obj)

    def setup_properties(self, obj):
        # Target Links
        obj.addProperty("App::PropertyLink", "Profile", "TwistExtrude", "Base profile sketch")
        obj.addProperty("App::PropertyLink", "Path", "TwistExtrude", "Sweep path (optional)")
        
        # Dimensions
        obj.addProperty("App::PropertyLength", "TotalHeight", "Parameters", "Total height").TotalHeight = 100.0
        obj.addProperty("App::PropertyAngle", "TotalAngle", "Parameters", "Total twist angle").TotalAngle = 360.0
        
        # Enumerations
        obj.addProperty("App::PropertyEnumeration", "TwistEasing", "Parameters", "Twist easing")
        obj.TwistEasing = ["Linear", "Ease In (Quad)", "Ease Out (Quad)", "Ease In-Out (Smoothstep)", "Ease In-Out (Sine)"]
        
        # Settings
        obj.addProperty("App::PropertyInteger", "NumSections", "Parameters", "Number of sections").NumSections = 24
        obj.addProperty("App::PropertyString", "EquationStr", "Parameters", "Scale formula").EquationStr = "1.0"
        obj.addProperty("App::PropertyBool", "SketchesOnly", "Parameters", "Generate sketches only").SketchesOnly = False

    def execute(self, obj):
        try:
            if not obj.Profile:
                return

            def get_val(prop_name):
                val = getattr(obj, prop_name)
                return val.Value if hasattr(val, 'Value') else val

            config = TwistConfig(
                total_height=get_val("TotalHeight"),
                total_angle=get_val("TotalAngle"),
                twist_easing=obj.TwistEasing,
                num_sections=get_val("NumSections"),
                equation_str=obj.EquationStr,
                sketches_only=obj.SketchesOnly
            )

            final_shape = generate_twist_shape(
                profile_obj=obj.Profile,
                path_obj=obj.Path,
                config=config
            )

            if final_shape and not final_shape.isNull():
                obj.Shape = final_shape
            else:
                App.Console.PrintWarning(f"{obj.Name}: Generated shape is empty.\n")

        except Exception as e:
            import traceback
            App.Console.PrintError(f"TwistExtrude failed to execute: {e}\n{traceback.format_exc()}\n")


class ViewProviderTwistExtrude:
    """ViewProvider for the TwistExtrudeFeature to handle UI and icons."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def getIcon(self):
        return Resources.icon("TwistExtrude.svg")

    def claimChildren(self):
        children = []
        if hasattr(self.Object, "Profile") and self.Object.Profile:
            children.append(self.Object.Profile)
        if hasattr(self.Object, "Path") and self.Object.Path:
            children.append(self.Object.Path)
        return children

    def setEdit(self, vobj, mode=0):
        return False

    def doubleClicked(self, vobj):
        return False
