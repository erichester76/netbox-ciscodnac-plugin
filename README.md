# netbox_ciscodnac_plugin

![PyPI - Downloads](https://img.shields.io/pypi/dm/netbox_ciscodnac_plugin)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/netbox_ciscodnac_plugin)
![PyPI](https://img.shields.io/pypi/v/netbox_ciscodnac_plugin)

*Cisco DNA Center Integration with NetBox*

---

```netbox_ciscodnac_plugin``` is a NetBox Plugin for Cisco DNA Center.  
It uses the Cisco DNA Center Platform APIs to sync data.

## Prerequisites
- Cisco DNA Center
    - Supported release: 1.3.3+
- NetBox
    - Supported release: 4.x
        - version netbox_ciscodnac_plugin 4.0.1
    - Supported release: 3.2
        - version netbox_ciscodnac_plugin 3.2.1
    - Supported release: 3.0
        - version netbox_ciscodnac_plugin 3.0.3
    - Supported release: 2.10
        - version netbox_ciscodnac_plugin 1.0.1
- Python
  - Version: 3.3+

## Data that is synced
- [x] Sites
- [x] Devices
- [x] IP Address (/32 of Devices)

## Screenshots
### Settings  
![](./img/settings_add.png)  
![](./img/settings.png)
### Status  
![](./img/status.png)
### Sync  
![](./img/task.png)  
![](./img/sync.png)
### NetBox Inventory
![](./img/sites.png)  
![](./img/devices.png)

## Getting Started

- Install the plugin from PyPi
    - ```pip install netbox_ciscodnac_plugin```

- Enable the plugin in ```configuration.py``` of NetBox
    ```
    PLUGINS = [
        'netbox_ciscodnac_plugin',
    ]
    ```
(More details at https://netbox.readthedocs.io/en/stable/plugins/)

If using Docker with NetBox, follow instructions on https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins

## Sync your data from Cisco DNA Center to NetBox

* Add your Cisco DNA Center(s) in Settings at the netbox_ciscodnac_plugin plugin
* Check status dashboard that API calls are OK towards your Cisco DNA Center (refresh if being cached)
* Use the buttons on the Dashboard to sync (Sites is mandatory for Devices to be assigned in Netbox)

## Technologies & Frameworks Used

**Cisco Products & Services:**

- [Cisco DNA Center](https://developer.cisco.com/docs/dna-center/#!cisco-dna-center-platform-overview)

**Third-Party Products & Services:**

- [NetBox](https://github.com/netbox-community/netbox)

**Tools & Frameworks:**

- [dnacentersdk](https://github.com/cisco-en-programmability/dnacentersdk) (Python SDK)
- [django](https://www.djangoproject.com/)

## Authors & Maintainers

- Robert Csapo <rcsapo@cisco.com>

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
