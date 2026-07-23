"""Document manipulation and workflow logic for TwistExtrude."""

import FreeCAD as App

from freecad.twistextrude.config import TwistConfig
from freecad.twistextrude.feature import TwistExtrudeFeature, ViewProviderTwistExtrude
from freecad.twistextrude.utils import get_active_body


def inject_twist_into_document(profile_obj, path_obj, config: TwistConfig):
    """Instantiates the parametric twist feature into the document."""
    active_body = get_active_body(profile_obj)
    
    mode_suffix = "PathSweep" if path_obj else "StraightExtrude"
    feat_name = f"{profile_obj.Name}_{mode_suffix}"

    # 1. Create the unified Parametric Feature
    if active_body:
        feat_obj = App.ActiveDocument.addObject("PartDesign::FeaturePython", feat_name)
        active_body.addObject(feat_obj)
        active_body.Tip = feat_obj
    else:
        feat_obj = App.ActiveDocument.addObject("Part::FeaturePython", feat_name)

    TwistExtrudeFeature(feat_obj)
    if App.GuiUp:
        ViewProviderTwistExtrude(feat_obj.ViewObject)

    # 2. Map the UI config directly to the new parametric node
    feat_obj.Profile = profile_obj
    feat_obj.Path = path_obj
    
    feat_obj.TotalHeight = config.total_height
    feat_obj.TotalAngle = config.total_angle
    feat_obj.TwistEasing = config.twist_easing
    feat_obj.NumSections = config.num_sections
    feat_obj.EquationStr = config.equation_str
    feat_obj.SketchesOnly = config.sketches_only

    # Hide the original target objects
    profile_obj.Visibility = False
    if path_obj:
        path_obj.Visibility = False
        
    # Inherit color
    if feat_obj.ViewObject and profile_obj.ViewObject:
        feat_obj.ViewObject.ShapeColor = getattr(profile_obj.ViewObject, "ShapeColor", (0.8, 0.8, 0.8))

    # 3. For Part Workbench, place it in a group for cleanliness
    if not active_body:
        group_name = "Generated_Twists"
        group = App.ActiveDocument.getObject(group_name) or App.ActiveDocument.addObject("App::DocumentObjectGroup", group_name)
        group.Label = "Generated Twists"
        group.addObject(feat_obj)

    App.ActiveDocument.recompute()
