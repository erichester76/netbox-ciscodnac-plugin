from django.shortcuts import get_object_or_404
from dnacentersdk import api
from ..models import Settings


class CiscoDNAC:

    # Get all tenants from Settings
    __tenants = Settings.objects.all()

    def __init__(self, **kwargs):
        """
        Cisco DNA Center API Instance
        """
        self.dnac = {}
        self.dnac_status = {}

        # Single Cisco DNA Center Instance
        if "pk" in kwargs and isinstance(kwargs["pk"], int) is True:

            # Verify that the Tenant exist based on the `pk`
            tenant = get_object_or_404(Settings, pk=kwargs["pk"])

            # Create Cisco DNA Center API Object
            obj = self.auth(tenant)

            # Check that Auth is successful
            if obj[0]:
                self.dnac[tenant.hostname] = obj[1]
            return

        for tenant in self.__tenants:
            self.dnac_status[tenant.hostname] = "disabled"

            # Create Cisco DNA Center API Object if enabled
            if tenant.status is True:

                # Create Cisco DNA Center API Object
                obj = self.auth(tenant)

                # Check that Auth is successful
                if obj:
                    self.dnac[tenant.hostname] = obj[1]
        return

    def auth(self, tenant):
        """
        Cisco DNA Center API Object
        """
        try:
            obj = api.DNACenterAPI(
                username=tenant.username,
                password=tenant.password,
                base_url="https://" + tenant.hostname,
                # version="2.1.2",  # TODO
                verify=bool(tenant.verify),
            )
            self.dnac_status[tenant.hostname] = "success"
            return True, obj
        except Exception as error_msg:
            print("Error for {}: {}".format(tenant, error_msg))
            self.dnac_status[tenant.hostname] = error_msg
            return False, None

    def get_paginated_data(self, tenant, api_call, **kwargs):
        """
        Generic method to handle paginated API responses from Cisco DNA Center.
        Args:
            tenant: The tenant object containing authentication info.
            api_call: The specific API call to execute (e.g., tenant.devices.get_device_list).
            **kwargs: Additional parameters for the API call (like filters).
        Returns:
            A list of all items returned by the paginated API.
        """
        items = []
        start_index = 1  # Start with the first page
        max_results = 500  # Default max results per page

        while True:
            response = api_call(start_index=start_index, **kwargs).response
            items.extend(response)

            # If the response length is less than max_results, we've retrieved all data
            if len(response) < max_results:
                break

            # Increase start_index for next page of results
            start_index += max_results

        return items

    def devices(self, tenant):
        """
        Get all Devices from Cisco DNA Center (handles pagination).
        """
        return self.get_paginated_data(tenant, tenant.devices.get_device_list)

    def sites(self, tenant):
        """
        Get all Sites from Cisco DNA Center (handles pagination).
        """
        return self.get_paginated_data(tenant, tenant.sites.get_site)

    def sites_count(self, tenant):
        """
        Get Sites count from Cisco DNA Center
        """
        return tenant.sites.get_site_count().response

    @classmethod
    def devices_to_sites(cls, tenant):
        """
        Map Device Serial Number to Site ID from Cisco DNA Center
        """
        results = {}
        for site in tenant.sites.get_site().response:
            for members in tenant.sites.get_membership(site_id=site.id).device:
                for device in members.response:
                    results[device.serialNumber] = site.id
        return results
