from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import get_object_or_404
from dnacentersdk import api
from ..models import Settings
from django.core.cache import cache
import logging

# Assuming logger is set up
logger = logging.getLogger(__name__)

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

    @classmethod
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
        return self.__class__.get_paginated_data(tenant, tenant.devices.get_device_list)

    def sites(self, tenant):
        """
        Get all Sites from Cisco DNA Center (handles pagination).
        """
        return self.__class__.get_paginated_data(tenant, tenant.sites.get_site)

    def sites_count(self, tenant):
        """
        Get Sites count from Cisco DNA Center
        """
        return tenant.sites.get_site_count().response

    @classmethod
    def devices_to_sites(cls, tenant):
        """
        Map Device Serial Number to Site ID from Cisco DNA Center, with caching.
        """
        results = {}

        # Cache key to store sites list
        cache_key_sites = f'dnac_sites_cache'
        cached_sites = cache.get(cache_key_sites)

        if cached_sites is None:
            # Fetch sites from DNA Center in batches and cache the result
            sites = cls.get_paginated_data(tenant, tenant.sites.get_site)

            cache.set(cache_key_sites, sites, timeout=300)  # Cache for 5 minutes
        else:
            sites = cached_sites

    def process_site(site, tenant):
        """
        Process a site and map its devices to site IDs, with caching and error handling.
        """
        # Cache key for site membership
        cache_key_membership = f'dnac_membership_{site.id}'
        cached_membership = cache.get(cache_key_membership)

        try:
            if cached_membership is None:
                # Fetch membership for the site and cache it
                membership = tenant.sites.get_membership(site_id=site.id)
                
                # Ensure that membership is not None and cache it only if valid
                if membership:
                    cache.set(cache_key_membership, membership, timeout=300)  # Cache for 5 minutes
                else:
                    logger.warning(f"Membership for site {site.id} is None. Skipping.")
                    return {}

            else:
                membership = cached_membership

            # Initialize the device mapping
            site_devices = {}

            # Check if membership contains devices and is structured as expected
            if membership and hasattr(membership, 'device'):
                if membership.device:
                    for members in membership.device:
                        if hasattr(members, 'response') and members.response:
                            for device in members.response:
                                if hasattr(device, 'serialNumber'):
                                    site_devices[device.serialNumber] = site.id
                                else:
                                    logger.warning(f"Device in site {site.id} has no serialNumber.")
                        else:
                            logger.warning(f"No response found for membership devices in site {site.id}.")
                else:
                    logger.warning(f"Membership for site {site.id} contains no devices.")
            else:
                logger.warning(f"Membership for site {site.id} is missing 'device' attribute.")

            return site_devices

        except Exception as e:
            logger.error(f"Error processing site {site.id}: {e}", exc_info=True)
            return {}

        # Process sites in parallel to fetch membership data
        with ThreadPoolExecutor(max_workers=10) as executor:
            site_device_maps = list(executor.map(process_site, sites))

        # Combine results from all processed sites
        for site_device_map in site_device_maps:
            results.update(site_device_map)

        return results


