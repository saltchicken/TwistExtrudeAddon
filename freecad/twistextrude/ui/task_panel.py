import FreeCADGui as Gui

from freecad.twistextrude.core import calculate_twist_preview_shape, generate_smart_twist
from freecad.twistextrude.resources import Resources
from freecad.twistextrude.ui.base_panel import BaseTaskPanel

class SmartTwistTaskPanel(BaseTaskPanel):
    def __init__(self, profile_obj, path_obj):
        self.profile_obj = profile_obj
        self.path_obj = path_obj
        
        ui_path = Resources._pkg.joinpath("ui/twist_panel.ui")
        super().__init__(str(ui_path), has_preview=True)
        
        self.profile_obj.Visibility = False

    def setup_ui(self):
        self.form.height_spin.valueChanged.connect(self.queue_preview)
        self.form.angle_spin.valueChanged.connect(self.queue_preview)
        self.form.easing_combo.currentIndexChanged.connect(self.queue_preview)
        self.form.sections_spin.valueChanged.connect(self.queue_preview)
        self.form.equation_input.editTextChanged.connect(self.queue_preview)
        self.form.equation_input.currentIndexChanged.connect(self.queue_preview)
        self.form.sketches_only_cb.toggled.connect(self.queue_preview)

    def calculate_preview(self):
        return calculate_twist_preview_shape(
            self.profile_obj, self.path_obj, 
            self.form.height_spin.value(), self.form.angle_spin.value(), 
            self.form.sections_spin.value(), self.form.equation_input.currentText(), 
            self.form.easing_combo.currentText(), self.form.sketches_only_cb.isChecked()
        )

    def generate_final(self):
        generate_smart_twist(
            self.profile_obj, self.path_obj, 
            self.form.height_spin.value(), self.form.angle_spin.value(), 
            self.form.sections_spin.value(), self.form.equation_input.currentText(), 
            self.form.easing_combo.currentText(), self.form.sketches_only_cb.isChecked()
        )

    def reject(self):
        self.profile_obj.Visibility = True
        super().reject()
