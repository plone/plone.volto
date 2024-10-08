from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.volto.interfaces import IVoltoSettings
from zope.component import adapter
from zope.interface import Interface


class VoltoSettingsEditForm(RegistryEditForm):
    schema = IVoltoSettings
    label = "Volto Settings"
    schema_prefix = "volto"

    def updateFields(self):
        super().updateFields()

    def updateWidgets(self):
        super().updateWidgets()


class VoltoSettingsControlPanel(ControlPanelFormWrapper):
    form = VoltoSettingsEditForm


@adapter(Interface, Interface)
class VoltoControlpanel(RegistryConfigletPanel):
    schema = IVoltoSettings
    configlet_id = "VoltoSettings"
    configlet_category_id = "plone-general"
    schema_prefix = "volto"
