# Ansible role: `foundata.linux.auto_update`

The `foundata.linux.auto_update` Ansible role (part of the `foundata.linux` Ansible collection).



## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`auto_update_linux_state`](#variable-auto_update_linux_state)
  - [`auto_update_linux_autoupgrade`](#variable-auto_update_linux_autoupgrade)
  - [`auto_update_linux_service_state`](#variable-auto_update_linux_service_state)
  - [`auto_update_linux_type`](#variable-auto_update_linux_type)
  - [`auto_update_linux_apply`](#variable-auto_update_linux_apply)
  - [`auto_update_linux_timer_settings`](#variable-auto_update_linux_timer_settings)
  - [`auto_update_linux_reboot`](#variable-auto_update_linux_reboot)
  - [`auto_update_linux_reboot_timer_settings`](#variable-auto_update_linux_reboot_timer_settings)
  - [`auto_update_linux_exclude`](#variable-auto_update_linux_exclude)
  - [`auto_update_linux_notify_email`](#variable-auto_update_linux_notify_email)
  - [`auto_update_linux_extra_config`](#variable-auto_update_linux_extra_config)
    - [`auto_update_linux_extra_config['unattended-upgrades']`](#variable-auto_update_linux_extra_config-sub-unattended-upgrades)
    - [`auto_update_linux_extra_config['dnf-automatic']`](#variable-auto_update_linux_extra_config-sub-dnf-automatic)
    - [`auto_update_linux_extra_config['os-update']`](#variable-auto_update_linux_extra_config-sub-os-update)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features<a id="features"></a>

* **Cross-platform, one interface**: configures the native unattended-update mechanism of each platform behind a single set of variables — `unattended-upgrades` (Debian/Ubuntu), `dnf-automatic` / `dnf5-plugin-automatic` (RHEL/Fedora) and `os-update` (openSUSE Leap).
* **Selectable apply mode**: install, download-only or notify-only via [`auto_update_linux_apply`](#variable-auto_update_linux_apply) (backend support varies; an unsupported mode emits a notice and falls back to `install`).
* **Controlled schedule**: tune the update timer with standard systemd `[Timer]` directives via [`auto_update_linux_timer_settings`](#variable-auto_update_linux_timer_settings).
* **Flexible reboot handling** via [`auto_update_linux_reboot`](#variable-auto_update_linux_reboot):
  * `never`: never reboot automatically.
  * `immediate`: let the backend reboot right after the update run (only when a reboot is required); timing rides the update timer's randomized delay.
  * `scheduled`: reboot only when required, at a controlled time, via a role-managed cross-platform systemd reboot timer (see [`auto_update_linux_reboot_timer_settings`](#variable-auto_update_linux_reboot_timer_settings)).


## Example playbooks, using this role<a id="examples"></a>

Automatic security updates every night, without rebooting (safe operations baseline):

```yaml
---

- name: "Manage automatic updates"
  hosts: "all"
  gather_facts: false
  tasks:

    - name: "Enable nightly automatic security updates"
      ansible.builtin.include_role:
        name: "foundata.linux.auto_update"
      vars:
        auto_update_linux_type: "security"
        auto_update_linux_timer_settings:
          OnCalendar: "*-*-* 02:00:00"
        auto_update_linux_reboot: "never"
```

Security updates with a controlled, cross-platform reboot window (reboot only when a reboot is actually required, at 04:00 AM, regardless of when the update ran):

```yaml
---

- name: "Manage automatic updates"
  hosts: "all"
  gather_facts: false
  tasks:

    - name: "Automatic security updates with a scheduled reboot window"
      ansible.builtin.include_role:
        name: "foundata.linux.auto_update"
      vars:
        auto_update_linux_type: "security"
        auto_update_linux_timer_settings:
          OnCalendar: "*-*-* 00/6:00:00" # check and install every 6 hours
        auto_update_linux_reboot: "scheduled"
        auto_update_linux_reboot_timer_settings:
          OnCalendar: "*-*-* 04:00:00"
          RandomizedDelaySec: "30m"
```

All updates, download-only, with email reports (needs a configured MTA, [foundata.postfix.run](https://foundata.com/en/projects/ansible-collection-postfix/) may help) and some packages held back:

```yaml
---

- name: "Manage automatic updates"
  hosts: "all"
  gather_facts: false
  tasks:

    - name: "Download all updates and report by mail, holding back some packages"
      ansible.builtin.include_role:
        name: "foundata.linux.auto_update"
      vars:
        auto_update_linux_type: "all"
        auto_update_linux_apply: "download"
        auto_update_linux_notify_email: "ops@example.com"
        auto_update_linux_exclude:
          - "docker-ce"
          - "linux-image-*"
```

Disable automatic updates (keep the mechanism installed, but stop and disable its timer):

```yaml
---

- name: "Manage automatic updates"
  hosts: "all"
  gather_facts: false
  tasks:

    - name: "Disable automatic updates"
      ansible.builtin.include_role:
        name: "foundata.linux.auto_update"
      vars:
        auto_update_linux_service_state: "disabled"
```

Uninstall (remove managed configuration, timers and packages):

```yaml
---

- name: "Manage automatic updates"
  hosts: "all"
  gather_facts: false
  tasks:

    - name: "Remove automatic updates"
      ansible.builtin.include_role:
        name: "foundata.linux.auto_update"
      vars:
        auto_update_linux_state: "absent"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `auto_update_linux_setup`: Manage basic resources, such as packages or service users.
- `auto_update_linux_config`: Manage settings, such as adapting or creating configuration files.
- `auto_update_linux_service`: Manage services and daemons, such as running states and service boot configurations.

There are also tags that are generally not intended to be called directly but are included for completeness and to cover edge cases:

- `auto_update_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

Main entry point for the foundata.linux.auto_update role

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `auto_update_linux_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-auto_update_linux_state) |
| `auto_update_linux_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one).<br><br>Note: This only affects the packages that provide the automatic update […](#variable-auto_update_linux_autoupgrade) |
| `auto_update_linux_service_state` | `str` | No | `"enabled"` | Defines the status of the service(s).<br><br>`enabled`: Service is running and will start automatically at boot.<br><br>`disabled`: Service is stopped and will not start automatically at boot.<br><br>`running` Service is running but will not start […](#variable-auto_update_linux_service_state) |
| `auto_update_linux_type` | `str` | No | `"security"` | Selects which kinds of updates are installed automatically. Possible values:<br><br>- `security`: Only security updates are applied. This is the default and safest for unattended operation. - `all`: All available updates are applied (security and […](#variable-auto_update_linux_type) |
| `auto_update_linux_apply` | `str` | No | `"install"` | Controls what the automatic update mechanism does when new updates are available. Possible values:<br><br>- `install`: Download and install updates automatically. - `download`: Only download updates; do not install them. - `notify`: Only check and […](#variable-auto_update_linux_apply) |
| `auto_update_linux_timer_settings` | `dict` | No | `{}` | Configuration for the systemd timer that triggers the automatic update run. This dictionary controls when and how often updates are checked/applied.<br><br>These settings map to systemd timer unit directives and are applied via a drop-in override […](#variable-auto_update_linux_timer_settings) |
| `auto_update_linux_reboot` | `str` | No | `"never"` | Controls whether and when the system reboots automatically after unattended updates. Automatic updates run out-of-band (triggered by a timer, while no Ansible run is active) and require a systemd-managed host. Possible values:<br><br>- `never`: Never […](#variable-auto_update_linux_reboot) |
| `auto_update_linux_reboot_timer_settings` | `dict` | No | `{}` | Configuration for the role-managed systemd timer that performs the scheduled "reboot if needed" check. This dictionary controls when that check runs.<br><br>Only effective when `auto_update_linux_reboot` is set to `scheduled`. The settings map to […](#variable-auto_update_linux_reboot_timer_settings) |
| `auto_update_linux_exclude` | `list` | No | `[]` | List of package names (or globs/patterns) to hold back from automatic updates.<br><br>Backend support:<br><br>- Debian/Ubuntu (`unattended-upgrades`): Yes. - RHEL/Fedora (`dnf`/`dnf5` automatic): Yes. - openSUSE Leap (`os-update`): No. The role emits […](#variable-auto_update_linux_exclude) |
| `auto_update_linux_notify_email` | `str` | No | `""` | Email address that should receive automatic update reports. An empty string (the default) disables email notifications.<br><br>Backend support:<br><br>- Debian/Ubuntu (`unattended-upgrades`): Yes. - RHEL/Fedora (`dnf`/`dnf5` automatic): Yes. - […](#variable-auto_update_linux_notify_email) |
| `auto_update_linux_extra_config` | `dict` | No | `{}` | Additional, backend-native configuration written verbatim into the configuration of the active update mechanism. This is an escape hatch for advanced options not covered by the dedicated parameters above and should only by used if there is no other […](#variable-auto_update_linux_extra_config) |

### `auto_update_linux_state`<a id="variable-auto_update_linux_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, …

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `auto_update_linux_autoupgrade`<a id="variable-auto_update_linux_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

Note: This only affects the packages that provide the automatic update
mechanism itself (e.g., `unattended-upgrades`, `dnf-automatic`,
`dnf5-plugin-automatic` or `os-update`). It does not control the unattended
updates applied to the rest of the system; those are governed by
`auto_update_linux_type` and `auto_update_linux_apply`.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `auto_update_linux_service_state`<a id="variable-auto_update_linux_service_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defines the status of the service(s).

`enabled`: Service is running and will start automatically at boot.

`disabled`: Service is stopped and will not start automatically at boot.

`running` Service is running but will not start automatically at boot.
This can be used to start a service on the first Ansible run without
enabling it for boot.

`unmanaged`: Service will not start at boot, and Ansible will not manage
its running state. This is primarily useful when services are monitored
and managed by systems other than Ansible.

The singular form (`service`) is used for simplicity. However, the defined
status applies to all services if multiple are being managed by this role.

On all currently supported platforms this is currently just a systemd timer
(such as `apt-daily-upgrade.timer`, `dnf-automatic.timer`, `dnf5-automatic.timer`
or `os-update.timer`) that periodically triggers the unattended update run.
The term "service" is used generically and also covers  such timer units.
Most platforms ship the relevant timer disabled by default, so `enabled` (this
variable's default value) is required for unattended updates to actually take
place.

- **Type**: `str`
- **Required**: No
- **Default**: `"enabled"`
- **Choices**: `enabled`, `disabled`, `running`, `unmanaged`



### `auto_update_linux_type`<a id="variable-auto_update_linux_type"></a>

[*⇑ Back to ToC ⇑*](#toc)

Selects which kinds of updates are installed automatically. Possible values:

- `security`: Only security updates are applied. This is the default and safest
   for unattended operation.
- `all`: All available updates are applied (security and non-security).

Supported on all platforms.

- **Type**: `str`
- **Required**: No
- **Default**: `"security"`
- **Choices**: `security`, `all`



### `auto_update_linux_apply`<a id="variable-auto_update_linux_apply"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls what the automatic update mechanism does when new updates are available.
Possible values:

- `install`: Download and install updates automatically.
- `download`: Only download updates; do not install them.
- `notify`: Only check and notify (e.g., via email/MOTD), no download, no install.

Backend support:

- Debian/Ubuntu (`unattended-upgrades`): `install` and `download`. `notify` is
  best-effort.
- RHEL/Fedora (`dnf`/`dnf5` automatic): `install`, `download` and `notify`.
- openSUSE Leap (`os-update`): `install` only. When set to `download` or `notify`
  the role emits a notice and falls back to `install`.

- **Type**: `str`
- **Required**: No
- **Default**: `"install"`
- **Choices**: `install`, `download`, `notify`



### `auto_update_linux_timer_settings`<a id="variable-auto_update_linux_timer_settings"></a>

[*⇑ Back to ToC ⇑*](#toc)

Configuration for the systemd timer that triggers the automatic update run.
This dictionary controls when and how often updates are checked/applied.

These settings map to systemd timer unit directives and are applied via a
drop-in override file. They take highest priority, overriding internal defaults
(see `__auto_update_linux_timer_settings_defaults` in `vars/main.yml` or
platform-specific overrides in the `vars/` directory).

Use standard systemd `[Timer]` directives as keys with their corresponding
values.

Dictionary structure:

- Keys: Standard systemd `[Timer]` directives.
- Values: Corresponding configuration values. Common options include:
  - `OnCalendar`: Defines the schedule on which the update timer is triggered.
    Defaults to `daily`. An (at least) daily schedule is recommended for
    security updates. Example for everyday every 6 hours: `*-*-* 00/6:00:00`
  - `RandomizedDelaySec`: Adds a random delay before execution to avoid
    simultaneous runs across systems. Defaults to `60m`.
  - `Persistent`: Ensures missed timer runs are executed at the next boot if
    the system was powered off. Defaults to `true`.

Value contract for the six repeatable trigger directives (`OnCalendar`,
`OnActiveSec`, `OnBootSec`, `OnStartupSec`, `OnUnitActiveSec`,
`OnUnitInactiveSec`):

- They also accept a YAML list and render one assignment per entry, so
  several expressions of the same directive can be combined:
  ```yaml
  OnCalendar:
    - "Mon..Fri 03:00"
    - "Sat,Sun 05:00"
  ```
- An empty list drops the role's built-in default for that directive
  (e.g. to run a purely monotonic timer without a calendar schedule).
  At least one trigger must remain overall.
- The monotonic trigger directives (all except `OnCalendar`) also accept
  plain numbers, which systemd reads as seconds.
- The boolean event trigger directives `OnClockChange` and
  `OnTimezoneChange` are supported as well and take `true`/`false`
  only. A `true` value counts as a remaining trigger, so an
  event-only timer (all repeatable triggers dropped via empty lists)
  is a valid configuration.
- Anything else is rejected: mappings, booleans, `null` and empty strings
  for repeatable trigger directives, non-booleans for the event trigger
  directives, unusable list entries, and lists for non-repeatable
  directives (those take a single scalar).

Special cases:

- For boolean values, use `true`/`false` (these will be converted to strings
  by the role as needed).

Only effective when `auto_update_linux_service_state` is not `unmanaged`.

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `auto_update_linux_reboot`<a id="variable-auto_update_linux_reboot"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls whether and when the system reboots automatically after unattended
updates. Automatic updates run out-of-band (triggered by a timer, while no
Ansible run is active) and require a systemd-managed host. Possible values:

- `never`: Never reboot automatically because of unattended updates.
- `immediate`: Reboot immediately after the unattended update run, using the
  platform's native mechanism (`unattended-upgrades` `Automatic-Reboot`,
  `dnf`/`dnf5` automatic `reboot = when-needed`, `os-update` `REBOOT_CMD=auto`).
  The timing is uncontrolled: the reboot rides on the update timer and its
  `RandomizedDelaySec`, so it can happen at an unpredictable moment.
- `scheduled`: Reboot at a controlled time via a role-managed systemd timer
  (`auto-update-reboot.timer`) that runs a "reboot if needed" check on the
  schedule from `auto_update_linux_reboot_timer_settings`. The platform's native
  reboot is forced off so the system only reboots in the role-managed systemd
  timer window.

Both `immediate` and `scheduled` reboot *only* when a reboot is actually required
(e.g. after a kernel, glibc or systemd upgrade); an up-to-date system is never
rebooted.

- **Type**: `str`
- **Required**: No
- **Default**: `"never"`
- **Choices**: `never`, `immediate`, `scheduled`



### `auto_update_linux_reboot_timer_settings`<a id="variable-auto_update_linux_reboot_timer_settings"></a>

[*⇑ Back to ToC ⇑*](#toc)

Configuration for the role-managed systemd timer that performs the scheduled
"reboot if needed" check. This dictionary controls when that check runs.

Only effective when `auto_update_linux_reboot` is set to `scheduled`. The
settings map to systemd timer unit directives and override the internal defaults
(see `__auto_update_linux_reboot_timer_settings_defaults` in `vars/main.yml`).

Use standard systemd `[Timer]` directives as keys with their corresponding
values.

Dictionary structure:

- Keys: Standard systemd `[Timer]` directives.
- Values: Corresponding configuration values. Common options include:
  - `OnCalendar`: When the reboot check runs. Defaults to `*-*-* 04:00:00`
    (every day at 04:00 AM). Choose a time after the update window so a
    reboot triggered by updates is picked up on the same day.
  - `RandomizedDelaySec`: Random delay before execution to spread reboots
    across systems. Defaults to `30m`.
  - `Persistent`: Run a missed check at the next boot if the system was
    powered off (even though . Defaults to `true`.

Value contract for the six repeatable trigger directives (`OnCalendar`,
`OnActiveSec`, `OnBootSec`, `OnStartupSec`, `OnUnitActiveSec`,
`OnUnitInactiveSec`):

- They also accept a YAML list and render one assignment per entry, so
  several expressions of the same directive can be combined:
  ```yaml
  OnCalendar:
    - "Mon..Fri 03:00"
    - "Sat,Sun 05:00"
  ```
- An empty list drops the role's built-in default for that directive
  (e.g. to run a purely monotonic timer without a calendar schedule).
  At least one trigger must remain overall.
- The monotonic trigger directives (all except `OnCalendar`) also accept
  plain numbers, which systemd reads as seconds.
- The boolean event trigger directives `OnClockChange` and
  `OnTimezoneChange` are supported as well and take `true`/`false`
  only. A `true` value counts as a remaining trigger, so an
  event-only timer (all repeatable triggers dropped via empty lists)
  is a valid configuration.
- Anything else is rejected: mappings, booleans, `null` and empty strings
  for repeatable trigger directives, non-booleans for the event trigger
  directives, unusable list entries, and lists for non-repeatable
  directives (those take a single scalar).

Special cases:

- For boolean values, use `true`/`false` (these will be converted to strings
  by the role as needed).

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `auto_update_linux_exclude`<a id="variable-auto_update_linux_exclude"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of package names (or globs/patterns) to hold back from automatic updates.

Backend support:

- Debian/Ubuntu (`unattended-upgrades`): Yes.
- RHEL/Fedora (`dnf`/`dnf5` automatic): Yes.
- openSUSE Leap (`os-update`): No. The role emits a notice if the list is non-empty.

Example:

```yaml
auto_update_linux_exclude:
  - "linux-image-*"
  - "docker-ce"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `str`



### `auto_update_linux_notify_email`<a id="variable-auto_update_linux_notify_email"></a>

[*⇑ Back to ToC ⇑*](#toc)

Email address that should receive automatic update reports. An empty string
(the default) disables email notifications.

Backend support:

- Debian/Ubuntu (`unattended-upgrades`): Yes.
- RHEL/Fedora (`dnf`/`dnf5` automatic): Yes.
- openSUSE Leap (`os-update`): No. The role emits a notice a non-empty value is set.

Note: Sending mail requires a working local mail transport (MTA) on the managed
host; configuring one is out of scope for this role. The foundata.postfix.run role
may help you with that.

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `auto_update_linux_extra_config`<a id="variable-auto_update_linux_extra_config"></a>

[*⇑ Back to ToC ⇑*](#toc)

Additional, backend-native configuration written verbatim into the configuration
of the active update mechanism. This is an escape hatch for advanced options not
covered by the dedicated parameters above and should only by used if there is
no other way to configure what you need; values set here take precedence over
the values derived from those parameters.

The dictionary is keyed by backend, so the same variable can carry settings for
mixed-platform inventories. Only the key matching the target host's backend is
applied; the others are ignored.

Top-level keys (backends):

- `unattended-upgrades`: Debian/Ubuntu (using `apt`).
- `dnf-automatic`: RHEL/Fedora (using `dnf`).
- `os-update`: openSUSE Leap (using `zypper`).

See the option value descriptions for their syntax. Example:

```yaml
auto_update_linux_extra_config:
  unattended-upgrades:
    "Unattended-Upgrade::MinimalSteps": "true"
  dnf-automatic:
    commands:
      network_online_timeout: 120
  os-update:
    RESTART_SERVICES: "no"
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`

#### `auto_update_linux_extra_config['unattended-upgrades']`<a id="variable-auto_update_linux_extra_config-sub-unattended-upgrades"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extra `unattended-upgrades` configuration for Debian/Ubuntu. Flat
dictionary; keys are full apt option names (e.g. `Unattended-Upgrade::MinimalSteps`),
rendered verbatim as `KEY "VALUE";` lines.

- **Type**: `dict`
- **Required**: No

#### `auto_update_linux_extra_config['dnf-automatic']`<a id="variable-auto_update_linux_extra_config-sub-dnf-automatic"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extra `dnf`/`dnf5` automatic configuration for RHEL/Fedora. Dictionary keyed
by `/etc/dnf/automatic.conf` section name (`commands`, `emitters`, `email`,
`base`, ...); each value is a flat dictionary of `key: value` pairs for that
section.

- **Type**: `dict`
- **Required**: No

#### `auto_update_linux_extra_config['os-update']`<a id="variable-auto_update_linux_extra_config-sub-os-update"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extra `os-update` configuration for openSUSE Leap. Flat dictionary; keys are
os-update variable names (e.g. `RESTART_SERVICES`), rendered verbatim as
`KEY="VALUE"` lines in `/etc/os-update.conf`.

- **Type**: `dict`
- **Required**: No




<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__auto_update_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
