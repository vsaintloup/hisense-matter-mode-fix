"""Temporary capability fix for the Hisense AP1024TW1LA Matter thermostat."""

from __future__ import annotations

import logging
from typing import Any, cast

from homeassistant.components.climate import HVACMode
from homeassistant.core import HomeAssistant

DOMAIN = "hisense_matter_mode_fix"

# Hisense AP1024TW1LA: vendor 0x138C, product 0x3601.
HISENSE_AP1024TW1LA = (0x138C, 0x3601)

_LOGGER = logging.getLogger(__name__)


def _patch_hisense_mode_selection(matter_climate: Any) -> None:
    """Turn on this appliance when Dry or Fan-only is selected.

    The AP1024TW1LA exposes an independent Matter OnOff cluster. Its
    Thermostat SystemMode can therefore be set to Dry while the appliance is
    still powered off. Core intentionally reflects that as HVAC off. Enable
    the appliance first for the two modes added by this workaround.
    """
    climate_class = matter_climate.MatterClimate
    patch_marker = "_hisense_matter_mode_fix_original_async_set_hvac_mode"
    if hasattr(climate_class, patch_marker):
        return

    original = climate_class.async_set_hvac_mode
    setattr(climate_class, patch_marker, original)

    async def async_set_hvac_mode_with_power(
        self: Any, hvac_mode: HVACMode
    ) -> None:
        device_info = self._endpoint.node.device_info
        if (
            (device_info.vendorID, device_info.productID) == HISENSE_AP1024TW1LA
            and hvac_mode in (HVACMode.DRY, HVACMode.FAN_ONLY)
            and self.get_matter_attribute_value(
                matter_climate.clusters.OnOff.Attributes.OnOff
            ) is False
        ):
            on_off_attribute = matter_climate.clusters.OnOff.Attributes.OnOff
            await self.write_attribute(value=True, matter_attribute=on_off_attribute)
            on_off_path = matter_climate.create_attribute_path_from_attribute(
                endpoint_id=self._endpoint.endpoint_id,
                attribute=on_off_attribute,
            )
            self._endpoint.set_attribute_value(on_off_path, True)

        await original(self, hvac_mode)

    climate_class.async_set_hvac_mode = cast(Any, async_set_hvac_mode_with_power)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Add the two capabilities omitted by the appliance's Matter feature map.

    This intentionally patches only the same two Core allowlists requested in
    https://github.com/home-assistant/core/issues/176256. It does not create
    entities, send a command, or alter any other Hisense product.
    """
    try:
        from homeassistant.components.matter import climate as matter_climate

        matter_climate.SUPPORT_DRY_MODE_DEVICES.add(HISENSE_AP1024TW1LA)
        matter_climate.SUPPORT_FAN_MODE_DEVICES.add(HISENSE_AP1024TW1LA)
        _patch_hisense_mode_selection(matter_climate)
    except (AttributeError, ImportError):
        _LOGGER.exception(
            "Could not apply the Hisense Matter mode fix; Home Assistant's "
            "Matter climate internals have changed"
        )
        return False

    _LOGGER.warning(
        "Enabled Dry and Fan-only for Hisense AP1024TW1LA "
        "(Matter 0x138C/0x3601). Remove this custom integration once "
        "Home Assistant Core includes the upstream fix."
    )
    return True
