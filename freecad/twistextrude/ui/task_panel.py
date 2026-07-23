import FreeCADGui as Gui

from freecad.twistextrude import workflow
from freecad.twistextrude.config import TwistConfig
from freecad.twistextrude.core import generate_twist_shape
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

    def get_config_from_ui(self) -> TwistConfig:
        return TwistConfig(
            total_height=self.form.height_spin.value(),
            total_angle=self.form.angle_spin.value(),
            twist_easing=self.form.easing_combo.currentText(),
            num_sections=self.form.sections_spin.value(),
            equation_str=self.form.equation_input.currentText(),
            sketches_only=self.form.sketches_only_cb.isChecked()
        )

    def calculate_preview(self):
        config = self.get_config_from_ui()
        return generate_twist_shape(self.profile_obj, self.path_obj, config)

    def generate_final(self):
        config = self.get_config_from_ui()
        workflow.inject_twist_into_document(self.profile_obj, self.path_obj, config)

    def reject(self):
        self.profile_obj.Visibility = True
        super().reject()
