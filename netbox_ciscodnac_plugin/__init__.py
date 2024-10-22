from netbox.plugins import PluginConfig
from .metadata import App
from .navigation import menu_items


class CiscoDNACenterConfig(PluginConfig):
    version = App._VERSION_
    name = "netbox_ciscodnac_plugin"
    verbose_name = "Cisco DNA Center Sync Plugin"
    description = App._DESC_
    author = App._AUTHOR_
    author_email = App._EMAIL_
    required_settings = []
    default_settings = {}
    base_url = "netbox_ciscodnac_plugin"
    caching_config = {}
    menu_items = menu_items

config = CiscoDNACenterConfig
