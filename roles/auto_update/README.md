# Ansible role: `foundata.linux.run`

The `foundata.linux.run` Ansible role (part of the `foundata.linux` Ansible collection).



## Table of contents<a id="toc"></a>

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



## Example playbooks, using this role<a id="examples"></a>

Installation with automatic upgrade:

```yaml
---

- name: "Initialize the foundata.linux.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.run role"
      ansible.builtin.include_role:
        name: "foundata.linux.run"
      vars:
        auto_update_linux_autoupgrade: true
```

Uninstall:

```yaml
---

- name: "Initialize the foundata.linux.run role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.run role"
      ansible.builtin.include_role:
        name: "foundata.linux.run"
      vars:
        auto_update_linux_state: "absent"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `auto_update_linux_setup`: Manage basic resources, such as packages or service users.
- `auto_update_linux_config`: Manage settings, such as adapting or creating configuration files.
- `auto_update_linux_service`: Manage services and daemons, such as running states and service boot configurations.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `auto_update_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `auto_update_linux_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-auto_update_linux_state) |
| `auto_update_linux_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one).<br><br>Note: This only affects the packages that provide the automatic update […](#variable-auto_update_linux_autoupgrade) |
| `auto_update_linux_service_state` | `str` | No | `"enabled"` | Defines the status of the service(s) the role needs on the target platform to perform automatic updates. On all currently supported platforms this is just a single systemd timer (such as `apt-daily-upgrade.timer`, `dnf-automatic.timer`, […](#variable-auto_update_linux_service_state) |
| `auto_update_linux_type` | `str` | No | `"security"` | Selects which kinds of updates are installed automatically. Possible values:<br><br>- `security`: Only security updates are applied. This is the recommended and safest default for unattended operation. - `all`: All available updates are applied […](#variable-auto_update_linux_type) |
| `auto_update_linux_apply` | `str` | No | `"install"` | Controls what the automatic update mechanism does when updates are available. Possible values:<br><br>- `install`: Download and install updates automatically. - `download`: Only download updates; do not install them. - `notify`: Only check and notify […](#variable-auto_update_linux_apply) |
| `auto_update_linux_timer_settings` | `dict` | No | `{}` | Configuration for the systemd timer that triggers the automatic update run. This dictionary controls when and how often updates are checked/applied.<br><br>These settings map to systemd timer unit directives and are applied via a drop-in override […](#variable-auto_update_linux_timer_settings) |
| `auto_update_linux_reboot` | `str` | No | `"never"` | Controls whether the system reboots automatically after unattended updates were applied. Because automatic updates run out-of-band (triggered by a timer, while no Ansible run is active), this reboot is performed by the platform's native mechanism, […](#variable-auto_update_linux_reboot) |
| `auto_update_linux_exclude` | `list` | No | `[]` | List of package names (or globs/patterns) to hold back from automatic updates.<br><br>Backend support:<br><br>- Debian/Ubuntu (`unattended-upgrades`): Yes. - RHEL/Fedora (`dnf`/`dnf5` automatic): Yes. - openSUSE Leap (`os-update`): No. A notice is […](#variable-auto_update_linux_exclude) |
| `auto_update_linux_notify_email` | `str` | No | `""` | Email address that should receive automatic update reports. An empty string (the default) disables email notifications.<br><br>Backend support:<br><br>- Debian/Ubuntu (`unattended-upgrades`): Yes. - RHEL/Fedora (`dnf`/`dnf5` automatic): Yes. - […](#variable-auto_update_linux_notify_email) |
| `auto_update_linux_extra_config` | `dict` | No | `{}` | Additional, backend-native configuration written verbatim into the configuration of the active update mechanism. This is an escape hatch for advanced options not covered by the dedicated parameters above; values set here take precedence over the […](#variable-auto_update_linux_extra_config) |

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

Defines the status of the service(s) the role needs on the target platform to
perform automatic updates. On all currently supported platforms this is just a
single systemd timer (such as `apt-daily-upgrade.timer`, `dnf-automatic.timer`,
`dnf5-automatic.timer` or `os-update.timer`) that periodically triggers the
unattended update run. The term "service" is used generically and also covers
such timer units.

Possible values:

- `enabled`: Service is running and will start automatically at boot.
- `disabled`: Service is stopped and will not start automatically at boot.
- `running`: Service is running but will not start automatically at boot.
  This can be used to start a service on the first Ansible run without
  enabling it for boot.
- `unmanaged`: Service will not start at boot, and Ansible will not
  manage its running state. This is primarily useful when services are
  monitored and managed by systems other than Ansible.

The singular form ("service") is used for simplicity. However, the defined
status applies to all services if multiple are being managed by this role.

Note: Most platforms ship the relevant timer disabled by default, so `enabled`
is required for unattended updates to actually take place. Only effective when
`auto_update_linux_state` is `present`.

- **Type**: `str`
- **Required**: No
- **Default**: `"enabled"`
- **Choices**: `enabled`, `disabled`, `running`, `unmanaged`



### `auto_update_linux_type`<a id="variable-auto_update_linux_type"></a>

[*⇑ Back to ToC ⇑*](#toc)

Selects which kinds of updates are installed automatically. Possible values:

- `security`: Only security updates are applied. This is the recommended and
  safest default for unattended operation.
- `all`: All available updates are applied (security and non-security).

Supported on all platforms.

- **Type**: `str`
- **Required**: No
- **Default**: `"security"`
- **Choices**: `security`, `all`



### `auto_update_linux_apply`<a id="variable-auto_update_linux_apply"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls what the automatic update mechanism does when updates are available.
Possible values:

- `install`: Download and install updates automatically.
- `download`: Only download updates; do not install them.
- `notify`: Only check and notify (e.g., via email/MOTD); do not download or
  install.

Backend support:

- Debian/Ubuntu (`unattended-upgrades`): `install` and `download`. `notify` is
  best-effort.
- RHEL/Fedora (`dnf`/`dnf5` automatic): `install`, `download` and `notify`.
- openSUSE Leap (`os-update`): `install` only. `download` and `notify` emit a
  notice and fall back to `install`.

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
(see `__auto_update_linux_timer_settings_defaults` in `vars/main.yml`) and
platform-specific overrides.

Use standard systemd `[Timer]` directives as keys with their corresponding
values.

Dictionary structure:

- Keys: Standard systemd `[Timer]` directives.
- Values: Corresponding configuration values. Common options include:
  - `OnCalendar`: Defines the schedule on which the update timer is triggered.
    Defaults to `daily`. An (at least) daily schedule is recommended for
    security updates.
  - `RandomizedDelaySec`: Adds a random delay before execution to avoid
    simultaneous runs across systems. Defaults to `60m`.
  - `Persistent`: Ensures missed timer runs are executed at the next boot if
    the system was powered off. Defaults to `true`.

Special cases:

- For boolean values, use `true`/`false` (these will be converted to strings
  by the role as needed).

Only effective when `auto_update_linux_state` is `present` and
`auto_update_linux_service_state` is not `unmanaged`.

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `auto_update_linux_reboot`<a id="variable-auto_update_linux_reboot"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls whether the system reboots automatically after unattended updates were
applied. Because automatic updates run out-of-band (triggered by a timer, while
no Ansible run is active), this reboot is performed by the platform's native
mechanism, not by the `foundata.linux.reboot` role. Possible values:

- `never`: Never reboot automatically after updates.
- `when-needed`: Reboot automatically only when a reboot is required to apply
  the updates (e.g., after a kernel, glibc or systemd upgrade).

Supported on all platforms.

Note: A `when-needed` reboot happens immediately after the timer-triggered
update run. Combined with a `RandomizedDelaySec` in
`auto_update_linux_timer_settings`, the reboot therefore occurs at an
unpredictable time, which is often unacceptable. If immediate reboots are not
acceptable, keep this at `never` and reboot in a controlled way by scheduling
the `foundata.linux.reboot` role separately (a dedicated reboot timer that
reboots only when needed is planned for that role).

- **Type**: `str`
- **Required**: No
- **Default**: `"never"`
- **Choices**: `never`, `when-needed`



### `auto_update_linux_exclude`<a id="variable-auto_update_linux_exclude"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of package names (or globs/patterns) to hold back from automatic updates.

Backend support:

- Debian/Ubuntu (`unattended-upgrades`): Yes.
- RHEL/Fedora (`dnf`/`dnf5` automatic): Yes.
- openSUSE Leap (`os-update`): No. A notice is emitted if the list is non-empty.

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
- openSUSE Leap (`os-update`): No. A notice is emitted if a value is set.

Note: Sending mail requires a working local mail transport (MTA) on the managed
host; configuring one is out of scope for this role.

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `auto_update_linux_extra_config`<a id="variable-auto_update_linux_extra_config"></a>

[*⇑ Back to ToC ⇑*](#toc)

Additional, backend-native configuration written verbatim into the configuration
of the active update mechanism. This is an escape hatch for advanced options not
covered by the dedicated parameters above; values set here take precedence over
the values derived from those parameters.

The dictionary is keyed by backend, so the same variable can carry settings for
mixed-platform inventories. Only the key matching the target host's backend is
applied; the others are ignored.

Top-level keys (backends):

- `apt`: Debian/Ubuntu (`unattended-upgrades`). A flat dictionary; keys are full
  apt option names, rendered as `KEY "VALUE";` apt configuration lines.
- `dnf`: RHEL/Fedora (`dnf`/`dnf5` automatic). A dictionary keyed by
  `automatic.conf` section name (`commands`, `emitters`, `email`, `base`, …);
  each value is a flat dictionary of that section's `key: value` pairs.
- `os_update`: openSUSE Leap (`os-update`). A flat dictionary; keys are os-update
  variable names, rendered as `KEY="VALUE"` lines in `/etc/os-update.conf`.

Example:

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
dictionary; keys are full apt option names (e.g.
`Unattended-Upgrade::MinimalSteps`), rendered verbatim as `KEY "VALUE";`
lines.

- **Type**: `dict`
- **Required**: No

#### `auto_update_linux_extra_config['dnf-automatic']`<a id="variable-auto_update_linux_extra_config-sub-dnf-automatic"></a>

[*⇑ Back to ToC ⇑*](#toc)

Extra `dnf`/`dnf5` automatic configuration for RHEL/Fedora. Dictionary keyed
by `/etc/dnf/automatic.conf` section name (`commands`, `emitters`, `email`,
`base`, …); each value is a flat dictionary of `key: value` pairs for that
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
