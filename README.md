# Hisense Matter Mode Fix

Temporary HACS integration for the Hisense AP1024TW1LA portable air conditioner
when connected through Matter to Home Assistant.

Hisense firmware for this appliance exposes neither the Dry nor Fan-only
capability flag in its Matter Thermostat feature map, even though the appliance
accepts both Matter `SystemMode` values. Home Assistant Core therefore removes
those modes before the command can reach the appliance.

This repository exists because [home-assistant/core#176256](https://github.com/home-assistant/core/issues/176256),
which documents this exact device issue, has remained without a substantive
response since it was opened. It provides a practical interim workaround while
the upstream issue remains unresolved.

This integration applies the narrow workaround proposed in that issue:
it adds only `(vendor_id=0x138C, product_id=0x3601)` to Core's Dry and Fan-only
allowlists during startup. It neither creates a second climate entity nor
communicates with the appliance itself.

## Compatibility

- Home Assistant Core 2026.7 or later
- Matter integration configured and working
- Hisense AP1024TW1LA identified by Matter as vendor `0x138C`, product `0x3601`

This is deliberately a small, temporary compatibility shim that relies on an
internal Core module. Remove it as soon as the upstream fix is released. A
future Core refactor may make the integration refuse to load rather than apply
an unsafe or broad patch.

## Install with HACS

1. In HACS, open the three-dot menu, choose **Custom repositories**, add this
   repository URL, and select **Integration**.
2. Install **Hisense Matter Mode Fix** from HACS.
3. Open your `configuration.yaml` and add this exact top-level entry:

   ```yaml
   hisense_matter_mode_fix:
   ```

4. Use **Developer tools → YAML → Check configuration**, then restart Home
   Assistant.
5. Open the Hisense climate entity. Its HVAC mode selector should now contain
   `dry` and `fan_only`, in addition to `off` and `cool`.

The first restart is required: the integration changes the capability lists
before the Matter climate entity is constructed. It does not require removing,
re-adding, or recommissioning the air conditioner.

## Verify and remove

After restarting, **Developer tools → States** should show both values in the
climate entity's `hvac_modes` attribute. In **Settings → System → Logs**, one
warning line confirms that the workaround loaded.

When Home Assistant Core incorporates the device ID, remove the YAML entry,
uninstall this HACS integration, and restart once. Keeping both is harmless,
but unnecessary.

## Scope

This is not a fork of Home Assistant Core. HACS cannot replace Core's built-in
Matter integration, and maintaining a whole custom Core image would make normal
Home Assistant OS updates impractical for this two-line device capability fix.
