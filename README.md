# Ansible collection: `foundata.linux`

This repository contains the `foundata.linux` Ansible Collection.

It provides roles for managing common Linux host concerns: automatic updates, conditional reboots, sudo policy, kernel parameters, and local users and groups.


<div align="center" id="project-readme-header">
<br>
<br>

**⭐ Found this useful? Support open-source and star this project:**

[![GitHub repository](https://img.shields.io/github/stars/foundata/ansible-collection-linux.svg)](https://github.com/foundata/ansible-collection-linux)

<br>
</div>



## Table of contents<a id="toc"></a>

- [Included content](#content)
  - [Role: `foundata.linux.auto_update`](#content-role-auto_update)
  - [Role: `foundata.linux.reboot`](#content-role-reboot)
  - [Role: `foundata.linux.sudo`](#content-role-sudo)
  - [Role: `foundata.linux.sysctl`](#content-role-sysctl)
  - [Role: `foundata.linux.user`](#content-role-user)
- [Dependencies](#dependencies)
- [Licensing, copyright](#licensing-copyright)
- [Author information](#author-information)



## Included content<a id="content"></a>

### Role: `foundata.linux.auto_update`<a id="content-role-auto_update"></a>

Configures each supported distribution's native unattended-update service through a consistent interface, including update scope, schedules, exclusions, notifications, and controlled reboot policies.
[Its `README.md`](./roles/auto_update/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL auto_update START -->
- [Ansible role: `foundata.linux.auto_update`](roles/auto_update/README.md#ansible-role-foundatalinuxauto_update)
  - [Table of contents](roles/auto_update/README.md#toc)
  - [Features](roles/auto_update/README.md#features)
  - [Example playbooks, using this role](roles/auto_update/README.md#examples)
  - [Supported tags](roles/auto_update/README.md#tags)
  - [Role variables](roles/auto_update/README.md#variables)
    - [`auto_update_linux_state`](roles/auto_update/README.md#variable-auto_update_linux_state)
    - [`auto_update_linux_autoupgrade`](roles/auto_update/README.md#variable-auto_update_linux_autoupgrade)
    - [`auto_update_linux_service_state`](roles/auto_update/README.md#variable-auto_update_linux_service_state)
    - [`auto_update_linux_type`](roles/auto_update/README.md#variable-auto_update_linux_type)
    - [`auto_update_linux_apply`](roles/auto_update/README.md#variable-auto_update_linux_apply)
    - [`auto_update_linux_timer_settings`](roles/auto_update/README.md#variable-auto_update_linux_timer_settings)
    - [`auto_update_linux_reboot`](roles/auto_update/README.md#variable-auto_update_linux_reboot)
    - [`auto_update_linux_reboot_timer_settings`](roles/auto_update/README.md#variable-auto_update_linux_reboot_timer_settings)
    - [`auto_update_linux_exclude`](roles/auto_update/README.md#variable-auto_update_linux_exclude)
    - [`auto_update_linux_notify_email`](roles/auto_update/README.md#variable-auto_update_linux_notify_email)
    - [`auto_update_linux_extra_config`](roles/auto_update/README.md#variable-auto_update_linux_extra_config)
      - [`auto_update_linux_extra_config['unattended-upgrades']`](roles/auto_update/README.md#variable-auto_update_linux_extra_config-sub-unattended-upgrades)
      - [`auto_update_linux_extra_config['dnf-automatic']`](roles/auto_update/README.md#variable-auto_update_linux_extra_config-sub-dnf-automatic)
      - [`auto_update_linux_extra_config['os-update']`](roles/auto_update/README.md#variable-auto_update_linux_extra_config-sub-os-update)
  - [Dependencies](roles/auto_update/README.md#dependencies)
  - [Compatibility](roles/auto_update/README.md#compatibility)
  - [External requirements](roles/auto_update/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL auto_update END -->



### Role: `foundata.linux.reboot`<a id="content-role-reboot"></a>

Detects whether Linux systems require a reboot and performs it safely, with cross-platform checks and configurable connection, timeout, messaging, and readiness validation. [Its `README.md`](./roles/reboot/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL reboot START -->
- [Ansible role: `foundata.linux.reboot`](roles/reboot/README.md#ansible-role-foundatalinuxreboot)
  - [Table of contents](roles/reboot/README.md#toc)
  - [Features](roles/reboot/README.md#features)
  - [Example playbooks, using this role](roles/reboot/README.md#examples)
  - [Supported tags](roles/reboot/README.md#tags)
  - [Role variables](roles/reboot/README.md#variables)
    - [`reboot_linux_state`](roles/reboot/README.md#variable-reboot_linux_state)
    - [`reboot_linux_autoupgrade`](roles/reboot/README.md#variable-reboot_linux_autoupgrade)
    - [`reboot_linux_boot_time_cmd`](roles/reboot/README.md#variable-reboot_linux_boot_time_cmd)
    - [`reboot_linux_connect_timeout`](roles/reboot/README.md#variable-reboot_linux_connect_timeout)
    - [`reboot_linux_msg`](roles/reboot/README.md#variable-reboot_linux_msg)
    - [`reboot_linux_post_delay`](roles/reboot/README.md#variable-reboot_linux_post_delay)
    - [`reboot_linux_timeout`](roles/reboot/README.md#variable-reboot_linux_timeout)
    - [`reboot_linux_test_cmd`](roles/reboot/README.md#variable-reboot_linux_test_cmd)
  - [Dependencies](roles/reboot/README.md#dependencies)
  - [Compatibility](roles/reboot/README.md#compatibility)
  - [External requirements](roles/reboot/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL reboot END -->



### Role: `foundata.linux.sudo`<a id="content-role-sudo"></a>

Installs and configures sudo through declarative, `visudo`-validated rules and defaults, with optional authoritative cleanup of unmanaged drop-ins. [Its `README.md`](./roles/sudo/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL sudo START -->
- [Ansible role: `foundata.linux.sudo`](roles/sudo/README.md#ansible-role-foundatalinuxsudo)
  - [Table of contents](roles/sudo/README.md#toc)
  - [Features](roles/sudo/README.md#features)
  - [Example playbooks, using this role](roles/sudo/README.md#examples)
  - [Supported tags](roles/sudo/README.md#tags)
  - [Role variables](roles/sudo/README.md#variables)
    - [`sudo_linux_state`](roles/sudo/README.md#variable-sudo_linux_state)
    - [`sudo_linux_autoupgrade`](roles/sudo/README.md#variable-sudo_linux_autoupgrade)
    - [`sudo_linux_rules`](roles/sudo/README.md#variable-sudo_linux_rules)
      - [`sudo_linux_rules['name']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-name)
      - [`sudo_linux_rules['state']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-state)
      - [`sudo_linux_rules['users']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-users)
      - [`sudo_linux_rules['groups']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-groups)
      - [`sudo_linux_rules['commands']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-commands)
      - [`sudo_linux_rules['runas']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-runas)
      - [`sudo_linux_rules['nopassword']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-nopassword)
      - [`sudo_linux_rules['setenv']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-setenv)
      - [`sudo_linux_rules['noexec']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-noexec)
      - [`sudo_linux_rules['host']`](roles/sudo/README.md#variable-sudo_linux_rules-sub-host)
    - [`sudo_linux_rule_defaults`](roles/sudo/README.md#variable-sudo_linux_rule_defaults)
    - [`sudo_linux_defaults`](roles/sudo/README.md#variable-sudo_linux_defaults)
    - [`sudo_linux_extra_content`](roles/sudo/README.md#variable-sudo_linux_extra_content)
    - [`sudo_linux_delete_unmanaged`](roles/sudo/README.md#variable-sudo_linux_delete_unmanaged)
    - [`sudo_linux_delete_unmanaged_exclude`](roles/sudo/README.md#variable-sudo_linux_delete_unmanaged_exclude)
  - [Dependencies](roles/sudo/README.md#dependencies)
  - [Compatibility](roles/sudo/README.md#compatibility)
  - [External requirements](roles/sudo/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL sudo END -->



### Role: `foundata.linux.sysctl`<a id="content-role-sysctl"></a>

Manages Linux kernel parameters through `sysctl`, combining explicit overrides with stackable, resource-aware workload and security profiles. [Its `README.md`](./roles/sysctl/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL sysctl START -->
- [Ansible role: `foundata.linux.sysctl`](roles/sysctl/README.md#ansible-role-foundatalinuxsysctl)
  - [Table of contents](roles/sysctl/README.md#toc)
  - [Features](roles/sysctl/README.md#features)
  - [Example playbooks, using this role](roles/sysctl/README.md#examples)
  - [Supported tags](roles/sysctl/README.md#tags)
  - [Role variables](roles/sysctl/README.md#variables)
    - [`sysctl_linux_state`](roles/sysctl/README.md#variable-sysctl_linux_state)
    - [`sysctl_linux_autoupgrade`](roles/sysctl/README.md#variable-sysctl_linux_autoupgrade)
    - [`sysctl_linux_profile`](roles/sysctl/README.md#variable-sysctl_linux_profile)
    - [`sysctl_linux_parameters`](roles/sysctl/README.md#variable-sysctl_linux_parameters)
    - [`sysctl_linux_reload`](roles/sysctl/README.md#variable-sysctl_linux_reload)
    - [`sysctl_linux_verify`](roles/sysctl/README.md#variable-sysctl_linux_verify)
    - [`sysctl_linux_ignore_unknown_key_errors`](roles/sysctl/README.md#variable-sysctl_linux_ignore_unknown_key_errors)
    - [`sysctl_linux_modules_required`](roles/sysctl/README.md#variable-sysctl_linux_modules_required)
    - [`sysctl_linux_config_dropin_file_name`](roles/sysctl/README.md#variable-sysctl_linux_config_dropin_file_name)
  - [Dependencies](roles/sysctl/README.md#dependencies)
  - [Compatibility](roles/sysctl/README.md#compatibility)
  - [External requirements](roles/sysctl/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL sysctl END -->



### Role: `foundata.linux.user`<a id="content-role-user"></a>

Manages local users and groups declaratively, including account defaults, home directories, password policies, SSH authorized keys, and optional cleanup of unmanaged accounts. [Its `README.md`](./roles/user/README.md) covers configuration, usage examples, and more:

<!-- ANSIBLE DOCSMITH TOC-FULL user START -->
- [Ansible role: `foundata.linux.user`](roles/user/README.md#ansible-role-foundatalinuxuser)
  - [Table of contents](roles/user/README.md#toc)
  - [Features](roles/user/README.md#features)
  - [Example playbooks, using this role](roles/user/README.md#examples)
  - [Supported tags](roles/user/README.md#tags)
  - [Role variables](roles/user/README.md#variables)
    - [`user_linux_account_defaults`](roles/user/README.md#variable-user_linux_account_defaults)
    - [`user_linux_accounts`](roles/user/README.md#variable-user_linux_accounts)
      - [`user_linux_accounts['name']`](roles/user/README.md#variable-user_linux_accounts-sub-name)
      - [`user_linux_accounts['state']`](roles/user/README.md#variable-user_linux_accounts-sub-state)
      - [`user_linux_accounts['uid']`](roles/user/README.md#variable-user_linux_accounts-sub-uid)
      - [`user_linux_accounts['comment']`](roles/user/README.md#variable-user_linux_accounts-sub-comment)
      - [`user_linux_accounts['shell']`](roles/user/README.md#variable-user_linux_accounts-sub-shell)
      - [`user_linux_accounts['umask']`](roles/user/README.md#variable-user_linux_accounts-sub-umask)
      - [`user_linux_accounts['system']`](roles/user/README.md#variable-user_linux_accounts-sub-system)
      - [`user_linux_accounts['local']`](roles/user/README.md#variable-user_linux_accounts-sub-local)
      - [`user_linux_accounts['seuser']`](roles/user/README.md#variable-user_linux_accounts-sub-seuser)
      - [`user_linux_accounts['group']`](roles/user/README.md#variable-user_linux_accounts-sub-group)
      - [`user_linux_accounts['groups']`](roles/user/README.md#variable-user_linux_accounts-sub-groups)
      - [`user_linux_accounts['groups_append']`](roles/user/README.md#variable-user_linux_accounts-sub-groups_append)
      - [`user_linux_accounts['expires']`](roles/user/README.md#variable-user_linux_accounts-sub-expires)
      - [`user_linux_accounts['home']`](roles/user/README.md#variable-user_linux_accounts-sub-home)
        - [`user_linux_accounts['home']['path']`](roles/user/README.md#variable-user_linux_accounts-sub-home-sub-path)
        - [`user_linux_accounts['home']['create']`](roles/user/README.md#variable-user_linux_accounts-sub-home-sub-create)
        - [`user_linux_accounts['home']['move']`](roles/user/README.md#variable-user_linux_accounts-sub-home-sub-move)
        - [`user_linux_accounts['home']['skeleton']`](roles/user/README.md#variable-user_linux_accounts-sub-home-sub-skeleton)
      - [`user_linux_accounts['password']`](roles/user/README.md#variable-user_linux_accounts-sub-password)
        - [`user_linux_accounts['password']['hash']`](roles/user/README.md#variable-user_linux_accounts-sub-password-sub-hash)
        - [`user_linux_accounts['password']['lock']`](roles/user/README.md#variable-user_linux_accounts-sub-password-sub-lock)
        - [`user_linux_accounts['password']['update']`](roles/user/README.md#variable-user_linux_accounts-sub-password-sub-update)
        - [`user_linux_accounts['password']['expire_min']`](roles/user/README.md#variable-user_linux_accounts-sub-password-sub-expire_min)
        - [`user_linux_accounts['password']['expire_max']`](roles/user/README.md#variable-user_linux_accounts-sub-password-sub-expire_max)
        - [`user_linux_accounts['password']['expire_warn']`](roles/user/README.md#variable-user_linux_accounts-sub-password-sub-expire_warn)
      - [`user_linux_accounts['ssh_authorized_keys']`](roles/user/README.md#variable-user_linux_accounts-sub-ssh_authorized_keys)
        - [`user_linux_accounts['ssh_authorized_keys']['key']`](roles/user/README.md#variable-user_linux_accounts-sub-ssh_authorized_keys-sub-key)
        - [`user_linux_accounts['ssh_authorized_keys']['options']`](roles/user/README.md#variable-user_linux_accounts-sub-ssh_authorized_keys-sub-options)
        - [`user_linux_accounts['ssh_authorized_keys']['state']`](roles/user/README.md#variable-user_linux_accounts-sub-ssh_authorized_keys-sub-state)
      - [`user_linux_accounts['ssh_authorized_keys_delete_unmanaged']`](roles/user/README.md#variable-user_linux_accounts-sub-ssh_authorized_keys_delete_unmanaged)
    - [`user_linux_group_defaults`](roles/user/README.md#variable-user_linux_group_defaults)
    - [`user_linux_groups`](roles/user/README.md#variable-user_linux_groups)
      - [`user_linux_groups['name']`](roles/user/README.md#variable-user_linux_groups-sub-name)
      - [`user_linux_groups['state']`](roles/user/README.md#variable-user_linux_groups-sub-state)
      - [`user_linux_groups['gid']`](roles/user/README.md#variable-user_linux_groups-sub-gid)
      - [`user_linux_groups['system']`](roles/user/README.md#variable-user_linux_groups-sub-system)
    - [`user_linux_accounts_delete_unmanaged`](roles/user/README.md#variable-user_linux_accounts_delete_unmanaged)
    - [`user_linux_accounts_delete_unmanaged_exclude`](roles/user/README.md#variable-user_linux_accounts_delete_unmanaged_exclude)
    - [`user_linux_uid_min`](roles/user/README.md#variable-user_linux_uid_min)
    - [`user_linux_uid_max`](roles/user/README.md#variable-user_linux_uid_max)
  - [Dependencies](roles/user/README.md#dependencies)
  - [Compatibility](roles/user/README.md#compatibility)
  - [External requirements](roles/user/README.md#requirements)
<!-- ANSIBLE DOCSMITH TOC-FULL user END -->



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`galaxy.yml`](./galaxy.yml).



## Licensing, copyright<a id="licensing-copyright"></a>

<!--REUSE-IgnoreStart-->
Copyright (c) 2026 [foundata GmbH](https://foundata.com/) (https://foundata.com)

This project is licensed under the GNU General Public License v3.0 or later (SPDX-License-Identifier: `GPL-3.0-or-later`), see [`LICENSES/GPL-3.0-or-later.txt`](LICENSES/GPL-3.0-or-later.txt) for the full text.

The [`REUSE.toml`](REUSE.toml) file provides detailed licensing and copyright information in a human- and machine-readable format. This includes parts that may be subject to different licensing or usage terms, such as third-party components. The repository conforms to the [REUSE specification](https://reuse.software/spec/). You can use [`reuse spdx`](https://reuse.readthedocs.io/en/latest/readme.html#cli) to create a [SPDX software bill of materials (SBOM)](https://en.wikipedia.org/wiki/Software_Package_Data_Exchange).
<!--REUSE-IgnoreEnd-->

[![REUSE status](https://api.reuse.software/badge/github.com/foundata/ansible-collection-linux)](https://api.reuse.software/info/github.com/foundata/ansible-collection-linux)



## Author information<a id="author-information"></a>

This [project](https://foundata.com/en/projects/) was created and is maintained by [foundata](https://foundata.com/).

Initially based on an [Ansible skeleton](https://foundata.com/en/projects/ansible-skeletons/) developed by [foundata](https://foundata.com/).
