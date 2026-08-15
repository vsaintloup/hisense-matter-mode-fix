"""Temporary capability fix for the Hisense AP1024TW1LA Matter thermostat."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

DOMAIN = "hisense_matter_mode_fix"

# Hisense AP1024TW1LA: vendor 0x138C, product 0x3601.
HISENSE_AP1024TW1LA = (0x138C, 0x3601)

_LOGGER = logging.getLogger(__name__)


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
