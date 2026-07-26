# Ansible role: `foundata.linux.reboot`

The `foundata.linux.reboot` Ansible role (part of the `foundata.linux` Ansible collection) detects if a system reboot is required and performs it if so.



## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`reboot_linux_state`](#variable-reboot_linux_state)
  - [`reboot_linux_autoupgrade`](#variable-reboot_linux_autoupgrade)
  - [`reboot_linux_boot_time_cmd`](#variable-reboot_linux_boot_time_cmd)
  - [`reboot_linux_connect_timeout`](#variable-reboot_linux_connect_timeout)
  - [`reboot_linux_msg`](#variable-reboot_linux_msg)
  - [`reboot_linux_post_delay`](#variable-reboot_linux_post_delay)
  - [`reboot_linux_timeout`](#variable-reboot_linux_timeout)
  - [`reboot_linux_test_cmd`](#variable-reboot_linux_test_cmd)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features

Main features:

* **Automatic detection of reboot requirements** using multiple methods:
  * Debian/Ubuntu: Checks for `/var/run/reboot-required` indicator file.
  * RHEL/Fedora: Uses `needs-restarting -r` to detect pending reboots.
  * Kernel updates: Compares running kernel against newest installed kernel in `/boot`.
  * SELinux: Detects mode changes that require a reboot to take effect.
* Configurable reboot behavior (timeout, message, post-reboot delay, connection timeout).
* Container-aware: Detects containerized environments to avoid reboot issues.
* Provides result facts (`reboot_linux_result`) for post-reboot verification and reporting.
* Designed for cross-platform compatibility, working seamlessly across Debian, Ubuntu, RHEL, and Fedora.



## Example playbooks, using this role<a id="examples"></a>

Run system upgrades and reboot if needed after everything else was finished (`post_tasks` ensures it runs after all other roles and their handlers have completed):

```yaml
---

- hosts: "all"
  gather_facts: false
  tasks:

    # Upgrades might create reboot need (e.g. new kernel version)
    - name: "Upgrade all packages (Debian/Ubuntu)"
      ansible.builtin.apt:
        upgrade: "dist"
        update_cache: true
      when: ansible_os_family == "Debian"

    - name: "Upgrade all packages (RHEL/Fedora)"
      ansible.builtin.dnf:
        name: "*"
        state: "latest"
      when: ansible_os_family == "RedHat"

  post_tasks:
    - name: "Trigger invocation of the foundata.linux.reboot role (reboot if required)"
      ansible.builtin.include_role:
        name: "foundata.linux.reboot"
```


## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `reboot_linux_setup`: Manage basic resources, such as packages or service users.
- `reboot_linux_reboot`: Manage reboots.

There are also tags that are generally not intended to be called directly but are included for completeness and to cover edge cases:

- `reboot_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

Main entry point for the foundata.linux.reboot role

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `reboot_linux_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-reboot_linux_state) |
| `reboot_linux_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one). |
| `reboot_linux_boot_time_cmd` | `str` | No | `"cat '/proc/sys/kernel/random/boot_id'"` | Command to run that returns a unique string indicating the last time the system was booted.<br><br>Setting this to a command that has different output each time it is run will cause the task to fail. |
| `reboot_linux_connect_timeout` | `int` | No | `0` | Maximum seconds to wait for a successful connection to the managed hosts before trying again.<br><br>If set to 0, the default setting for the underlying connection plugin is used. |
| `reboot_linux_msg` | `str` | No | `"Reboot initiated by Ansible (foundata.linux.reboot)"` | Message to display to users before reboot. |
| `reboot_linux_post_delay` | `int` | No | `0` | Seconds to wait after the reboot command was successful before attempting to validate the system rebooted successfully.<br><br>This is useful if you want wait for something to settle despite your connection already working. |
| `reboot_linux_timeout` | `int` | No | `300` | Maximum seconds to wait for machine to reboot and respond to a test command.<br><br>This timeout is evaluated separately for both reboot verification and test command success so the maximum execution time for the module is twice this amount. |
| `reboot_linux_test_cmd` | `str` | No | `"id"` | Command to run on the rebooted host and expect success from to determine the machine is ready for further tasks. |

### `reboot_linux_state`<a id="variable-reboot_linux_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, …

Note: For this role, the required component and package set is minimal. There
are no users or services to manage and the components needed to detect a
required reboot are usually preinstalled even on hardened systems. They also
cannot be safely removed due to dependencies, so the role rarely modifies the
system beside executing reboots.

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `reboot_linux_autoupgrade`<a id="variable-reboot_linux_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `reboot_linux_boot_time_cmd`<a id="variable-reboot_linux_boot_time_cmd"></a>

[*⇑ Back to ToC ⇑*](#toc)

Command to run that returns a unique string indicating the last time the
system was booted.

Setting this to a command that has different output each time it is run will
cause the task to fail.

- **Type**: `str`
- **Required**: No
- **Default**: `"cat '/proc/sys/kernel/random/boot_id'"`



### `reboot_linux_connect_timeout`<a id="variable-reboot_linux_connect_timeout"></a>

[*⇑ Back to ToC ⇑*](#toc)

Maximum seconds to wait for a successful connection to the managed hosts
before trying again.

If set to 0, the default setting for the underlying connection plugin is
used.

- **Type**: `int`
- **Required**: No
- **Default**: `0`



### `reboot_linux_msg`<a id="variable-reboot_linux_msg"></a>

[*⇑ Back to ToC ⇑*](#toc)

Message to display to users before reboot.

- **Type**: `str`
- **Required**: No
- **Default**: `"Reboot initiated by Ansible (foundata.linux.reboot)"`



### `reboot_linux_post_delay`<a id="variable-reboot_linux_post_delay"></a>

[*⇑ Back to ToC ⇑*](#toc)

Seconds to wait after the reboot command was successful before attempting to
validate the system rebooted successfully.

This is useful if you want wait for something to settle despite your
connection already working.

- **Type**: `int`
- **Required**: No
- **Default**: `0`



### `reboot_linux_timeout`<a id="variable-reboot_linux_timeout"></a>

[*⇑ Back to ToC ⇑*](#toc)

Maximum seconds to wait for machine to reboot and respond to a test command.

This timeout is evaluated separately for both reboot verification and test
command success so the maximum execution time for the module is twice this
amount.

- **Type**: `int`
- **Required**: No
- **Default**: `300`



### `reboot_linux_test_cmd`<a id="variable-reboot_linux_test_cmd"></a>

[*⇑ Back to ToC ⇑*](#toc)

Command to run on the rebooted host and expect success from to determine the
machine is ready for further tasks.

- **Type**: `str`
- **Required**: No
- **Default**: `"id"`




<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__reboot_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
