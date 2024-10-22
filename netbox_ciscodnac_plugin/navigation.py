from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


menu_items = (
    PluginMenuItem(
        link="plugins:netbox_ciscodnac_plugin:status",
        link_text="Status",
        permissions=["netbox_ciscodnac_plugin.admin_full"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_ciscodnac_plugin:sync_full",
                title="Settings",
                icon_class="mdi mdi-all-inclusive",
                color=ButtonColorChoices.BLUE,
                permissions=["netbox_ciscodnac_plugin.admin_full"],
            ),
            PluginMenuButton(
                link="plugins:netbox_ciscodnac_plugin:settings",
                title="Settings",
                icon_class="mdi mdi-cog",
                color=ButtonColorChoices.BLUE,
                permissions=["netbox_ciscodnac_plugin.admin_full"],
            ),
        ),
    ),
)
