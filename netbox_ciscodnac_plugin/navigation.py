from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu


menu_items = (
    PluginMenuItem(
        link="plugins:netbox_ciscodnac_plugin:status",
        link_text="Status",
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_ciscodnac_plugin:sync_full",
                title="Settings",
                icon_class="mdi mdi-all-inclusive",
            ),
            PluginMenuButton(
                link="plugins:netbox_ciscodnac_plugin:settings",
                title="Settings",
                icon_class="mdi mdi-cog",
            ),
        ),
    ),
)
