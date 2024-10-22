from django.shortcuts import get_object_or_404
from dnacentersdk import api
from ..models import Settings
from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache


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

    def get_paginated_data(self, tenant, api_call, limit=500, **kwargs):
        """
        Generic method to handle paginated API responses from Cisco DNA Center.
        Args:
            tenant: The tenant object containing authentication info.
            api_call: The specific API call to execute (e.g., tenant.devices.get_device_list).
            limit: Maximum number of results per page (default is 500).
            **kwargs: Additional parameters for the API call (like filters).
        Returns:
            A list of all items returned by the paginated API.
        """
        items = []
        offset = 1  # Start with the first page

        while True:
            # Fetch the current page of results
            response = api_call(offset=offset, limit=limit, **kwargs).response
            items.extend(response)

            # If the number of results is less than the limit, we've retrieved all data
            if len(response) < limit:
                break

            # Increment the offset for the next page of results
            offset += limit

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
    from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache

def devices_to_sites(cls, tenant):
    """
    Map Device Serial Number to Site ID from Cisco DNA Center, with caching.
    """
    results = {}

    # Cache key to store sites list
    cache_key_sites = f'dnac_sites_{tenant.hostname}'
    cached_sites = cache.get(cache_key_sites)

    if cached_sites is None:
        # Fetch sites from DNA Center in batches and cache the result
        sites = cls.get_paginated_data(tenant.sites.get_site, tenant)
        cache.set(cache_key_sites, sites, timeout=300)  # Cache for 5 minutes
    else:
        sites = cached_sites

    def process_site(site):
        # Cache key for site membership
        cache_key_membership = f'dnac_membership_{site.id}'
        cached_membership = cache.get(cache_key_membership)

        if cached_membership is None:
            # Fetch membership for the site and cache it
            membership = tenant.sites.get_membership(site_id=site.id)
            cache.set(cache_key_membership, membership, timeout=300)  # Cache for 5 minutes
        else:
            membership = cached_membership

        site_devices = {}
        if membership and hasattr(membership, 'device'):
            for members in membership.device:
                for device in members.response:
                    site_devices[device.serialNumber] = site.id
        return site_devices

    # Process sites in parallel to fetch membership data
    with ThreadPoolExecutor(max_workers=10) as executor:
        site_device_maps = list(executor.map(process_site, sites))

    # Combine results from all processed sites
    for site_device_map in site_device_maps:
        results.update(site_device_map)

    return results


