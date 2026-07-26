# Ansible role: `foundata.linux.sudo`

The `foundata.linux.sudo` Ansible role (part of the `foundata.linux` Ansible collection).



## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`sudo_linux_state`](#variable-sudo_linux_state)
  - [`sudo_linux_autoupgrade`](#variable-sudo_linux_autoupgrade)
  - [`sudo_linux_rules`](#variable-sudo_linux_rules)
    - [`sudo_linux_rules['name']`](#variable-sudo_linux_rules-sub-name)
    - [`sudo_linux_rules['state']`](#variable-sudo_linux_rules-sub-state)
    - [`sudo_linux_rules['users']`](#variable-sudo_linux_rules-sub-users)
    - [`sudo_linux_rules['groups']`](#variable-sudo_linux_rules-sub-groups)
    - [`sudo_linux_rules['commands']`](#variable-sudo_linux_rules-sub-commands)
    - [`sudo_linux_rules['runas']`](#variable-sudo_linux_rules-sub-runas)
    - [`sudo_linux_rules['nopassword']`](#variable-sudo_linux_rules-sub-nopassword)
    - [`sudo_linux_rules['setenv']`](#variable-sudo_linux_rules-sub-setenv)
    - [`sudo_linux_rules['noexec']`](#variable-sudo_linux_rules-sub-noexec)
    - [`sudo_linux_rules['host']`](#variable-sudo_linux_rules-sub-host)
  - [`sudo_linux_rule_defaults`](#variable-sudo_linux_rule_defaults)
  - [`sudo_linux_defaults`](#variable-sudo_linux_defaults)
  - [`sudo_linux_extra_content`](#variable-sudo_linux_extra_content)
  - [`sudo_linux_delete_unmanaged`](#variable-sudo_linux_delete_unmanaged)
  - [`sudo_linux_delete_unmanaged_exclude`](#variable-sudo_linux_delete_unmanaged_exclude)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features<a id="features"></a>

* **Declarative, validated rules**: describe who may run what in [`sudo_linux_rules`](#variable-sudo_linux_rules); each rule is rendered into a `visudo`-validated drop-in file below `/etc/sudoers.d/` (via `community.general.sudoers`), so the main `/etc/sudoers` is never edited and a malformed rule does not break sudo.
* **Per-rule grants** via [`sudo_linux_rules`](#variable-sudo_linux_rules): target one or more [`users`](#variable-sudo_linux_rules-sub-users) and/or [`groups`](#variable-sudo_linux_rules-sub-groups), allow specific [`commands`](#variable-sudo_linux_rules-sub-commands) (absolute paths or `ALL`), pick the [`runas`](#variable-sudo_linux_rules-sub-runas) identity and restrict by [`host`](#variable-sudo_linux_rules-sub-host), with `NOPASSWD`/`SETENV`/`NOEXEC` toggles ([`nopassword`](#variable-sudo_linux_rules-sub-nopassword), [`setenv`](#variable-sudo_linux_rules-sub-setenv), [`noexec`](#variable-sudo_linux_rules-sub-noexec)).
* **Defaults instead of repetition**: set common rule options (`runas`, `host`, `nopassword`, ...) once in [`sudo_linux_rule_defaults`](#variable-sudo_linux_rule_defaults); every rule inherits them unless it overrides the key.
* **Global `Defaults` directives** via [`sudo_linux_defaults`](#variable-sudo_linux_defaults): apply sudo-wide settings (`env_reset`, `secure_path`, `timestamp_timeout`, ...) through a single managed, validated drop-in file.
* **Optional authoritative cleanup** via [`sudo_linux_delete_unmanaged`](#variable-sudo_linux_delete_unmanaged): off by default, removes any drop-in not managed by this role, while keeping an internal per-platform protected list plus the names in [`sudo_linux_delete_unmanaged_exclude`](#variable-sudo_linux_delete_unmanaged_exclude) (e.g. `90-cloud-init-users`) to avoid lockouts.


## Example playbooks, using this role<a id="examples"></a>

Grant administrative access to a group and a few scoped, task-specific rules. The
`admins` group gets full root access (with a password), while a deploy user and a
monitoring group get only the exact commands they need — the deploy reloads are
passwordless because they run non-interactively from CI:

```yaml
---

- name: "Manage sudo rules"
  hosts: all
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.sudo role"
      ansible.builtin.include_role:
        name: "foundata.linux.sudo"
      vars:
        # Applied to every rule below unless it overrides the key.
        sudo_linux_rule_defaults:
          runas: "ALL"
          host: "ALL"
          nopassword: false # require a password unless a rule opts out
        sudo_linux_rules:
          # Full administrative access for the platform admin group
          # ("sudo" on Debian/Ubuntu, "wheel" on RHEL/Fedora/SUSE).
          - name: "admins"
            groups:
              - "wheel"
            commands:
              - "ALL"
          # CI deploy user: reload/restart nginx without a password.
          - name: "deploy-nginx"
            users:
              - "deploy-service-user"
            commands:
              - "/usr/bin/systemctl reload nginx"
              - "/usr/bin/systemctl restart nginx"
            nopassword: true
          # Operators may inspect services and tail the journal as root.
          - name: "ops-readonly"
            groups:
              - "ops"
            commands:
              - "/usr/bin/systemctl status *"
              - "/usr/bin/journalctl"
            runas: "root"
```

Apply hardening `Defaults` alongside the rules (these land in their own
validated drop-in file):

```yaml
---

- name: "Manage sudo defaults and rules"
  hosts: all
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.sudo role"
      ansible.builtin.include_role:
        name: "foundata.linux.sudo"
      vars:
        sudo_linux_defaults:
          - "env_reset"
          - "secure_path=\"/usr/sbin:/usr/bin:/sbin:/bin\""
          - "timestamp_timeout=15"
          - "!visiblepw"
        sudo_linux_rules:
          - name: "admins"
            groups:
              - "wheel"
            commands:
              - "ALL"
```

Take authoritative control of `/etc/sudoers.d/`: remove any drop-in not managed
by this role, but keep the cloud-init file so you do not lock yourself out
(install the latest `sudo` while at it):

```yaml
---

- name: "Reconcile sudoers.d authoritatively"
  hosts: all
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.sudo role"
      ansible.builtin.include_role:
        name: "foundata.linux.sudo"
      vars:
        sudo_linux_autoupgrade: true
        sudo_linux_rules:
          - name: "admins"
            groups:
              - "wheel"
            commands:
              - "ALL"
        sudo_linux_delete_unmanaged: true
        sudo_linux_delete_unmanaged_exclude:
          - "90-cloud-init-users"
```

Remove a single rule created by a previous run (keep the rest):

```yaml
---

- name: "Remove an obsolete sudo rule"
  hosts: all
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.sudo role"
      ansible.builtin.include_role:
        name: "foundata.linux.sudo"
      vars:
        sudo_linux_rules:
          - name: "legacy-rule"
            groups:
              - "legacy" # same grantees the rule was created with
            state: "absent"
```

Uninstall (remove the drop-in files this role manages; the `sudo` package is
intentionally kept):

```yaml
---

- name: "Initialize the foundata.linux.sudo role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.sudo role"
      ansible.builtin.include_role:
        name: "foundata.linux.sudo"
      vars:
        sudo_linux_state: "absent"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `sudo_linux_setup`: Manage basic resources, such as packages or service users.
- `sudo_linux_config`: Manage settings, such as adapting or creating configuration files.

There are also tags that are generally not intended to be called directly but are included for completeness and to cover edge cases:

- `sudo_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

Main entry point for the foundata.linux.sudo role

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `sudo_linux_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that `sudo` is installed and that the rules described in `sudo_linux_rules` (and any `sudo_linux_defaults`) are configured as drop-in files below […](#variable-sudo_linux_state) |
| `sudo_linux_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one).<br><br>This role manages the `sudo` package (it is missing from some minimal […](#variable-sudo_linux_autoupgrade) |
| `sudo_linux_rules` | `list` | No | `[]` | List of sudo rules to manage. Each entry grants one or more users and/or groups the right to run a set of commands, and is rendered into validated drop-in files below `/etc/sudoers.d/` (one file per grantee, as the underlying […](#variable-sudo_linux_rules) |
| `sudo_linux_rule_defaults` | `dict` | No | `{}` | Default values applied to every entry in `sudo_linux_rules` that does not set the corresponding key itself. The keys mirror the per-rule keys of the same name (see `sudo_linux_rules`). Any value provided here is overridden by an explicit value on the […](#variable-sudo_linux_rule_defaults) |
| `sudo_linux_defaults` | `list` | No | `[]` | Global `Defaults` directives to apply, for sudo-wide settings that are not tied to a specific rule (the per-rule mechanism cannot express `Defaults` lines). Each entry is one directive: the role prepends the `Defaults` keyword and renders one […](#variable-sudo_linux_defaults) |
| `sudo_linux_extra_content` | `str` | No | `""` | Last-resort escape hatch: raw sudoers content appended verbatim to the role's managed, `visudo`-validated drop-in file, after the lines rendered from `sudo_linux_defaults`. Use it for anything the structured variables cannot express, for example […](#variable-sudo_linux_extra_content) |
| `sudo_linux_delete_unmanaged` | `bool` | No | `false` | If `true`, the role manages `/etc/sudoers.d/` authoritatively: every drop-in file that is **not** created by this role is removed, except for<br><br>- an internal, per-platform protected list (for example the `README` shipped by the `sudo` package on […](#variable-sudo_linux_delete_unmanaged) |
| `sudo_linux_delete_unmanaged_exclude` | `list` | No | `[]` | List of drop-in file names (basenames, relative to `/etc/sudoers.d/`) that must never be removed by `sudo_linux_delete_unmanaged`, even though they are not managed by this role. Use this for files shipped by the distribution or other software that […](#variable-sudo_linux_delete_unmanaged_exclude) |

### `sudo_linux_state`<a id="variable-sudo_linux_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that `sudo` is installed and that the rules described in
`sudo_linux_rules` (and any `sudo_linux_defaults`) are configured as
drop-in files below `/etc/sudoers.d/`.

`absent` reverts changes as much as possible: the drop-in files this role
manages are removed. The `sudo` package itself is intentionally **not**
uninstalled, as it is a core component that other tooling and the system
itself rely on.

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `sudo_linux_autoupgrade`<a id="variable-sudo_linux_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each
Ansible run (e.g., when the package provider detects a newer version than
the currently installed one).

This role manages the `sudo` package (it is missing from some minimal
installations), so this variable controls whether `sudo` is merely ensured
present or upgraded to the latest available version on every run.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `sudo_linux_rules`<a id="variable-sudo_linux_rules"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of sudo rules to manage. Each entry grants one or more users and/or
groups the right to run a set of commands, and is rendered into validated
drop-in files below `/etc/sudoers.d/` (one file per grantee, as the
underlying `community.general.sudoers` module manages a single user or
group per file).

A rule with `state: present` must specify `commands` and at least one
grantee (`users` and/or `groups`); the role fails early otherwise. A rule
with `state: absent` only needs its `name` (and the same grantees it was
created with) so the corresponding drop-in files can be removed.

For options that are not set on an individual rule, the value from
`sudo_linux_rule_defaults` applies.

Security notes:

- Prefer absolute command paths over `ALL`. Granting `commands: ["ALL"]`
  is effectively full root access.
- `nopassword` defaults to `false` (a password is required). Enable it
  only for specific, non-interactive commands.
- Avoid granting sudo access to broadly powerful commands such as `chmod`,
  `chown`, `cp`, `mv`, or shell-capable tools unless the arguments are tightly
  restricted. Misconfigured sudo rules can enable privilege escalation; see
  GTFOBins for examples: https://gtfobins.org/

Example:
```yaml
sudo_linux_rules:
  # Full administrative access for the platform admin group
  # ("sudo" on Debian/Ubuntu, "wheel" on RHEL/Fedora/SUSE).
  - name: "admins"
    groups:
      - "{\{ (ansible_facts['os_family'] == 'Debian') | ternary('sudo', 'wheel') }\}"
    commands:
      - "ALL"
    runas: "ALL"
  # A deploy user may restart/reload nginx without a password
  - name: "deploy-nginx"
    users:
      - "deploy"
    groups:
      - "webops"
    commands:
      - "/usr/bin/systemctl restart nginx"
      - "/usr/bin/systemctl reload nginx"
    nopassword: true
  # Remove a rule created by a previous run
  - name: "legacy-rule"
    state: "absent"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `dict`

#### `sudo_linux_rules['name']`<a id="variable-sudo_linux_rules-sub-name"></a>

[*⇑ Back to ToC ⇑*](#toc)

Identifier for the rule. Must be unique within `sudo_linux_rules`. It
is used to build the drop-in filenames, so use only `a-z`, `A-Z`,
`0-9`, underscore (`_`) and hyphen (`-`).

Dots (`.`) are intentionally not allowed: sudo ignores any file in
`/etc/sudoers.d` whose name contains a `.`, so a dotted rule name would
silently produce a drop-in that is never applied.

- **Type**: `str`
- **Required**: Yes

#### `sudo_linux_rules['state']`<a id="variable-sudo_linux_rules-sub-state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Whether the rule should be `present` or `absent`. Setting `absent`
removes the drop-in files belonging to this rule's grantees.

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`

#### `sudo_linux_rules['users']`<a id="variable-sudo_linux_rules-sub-users"></a>

[*⇑ Back to ToC ⇑*](#toc)

User names this rule applies to. At least one entry across `users` and
`groups` is required for a `present` rule.

- **Type**: `list`
- **Required**: No
- **List Elements**: `str`

#### `sudo_linux_rules['groups']`<a id="variable-sudo_linux_rules-sub-groups"></a>

[*⇑ Back to ToC ⇑*](#toc)

Group names this rule applies to (rendered with a leading `%` in the
sudoers file but do not put `%` here in the definition). At least one entry
across `users` and `groups` is required for a `present` rule.

- **Type**: `list`
- **Required**: No
- **List Elements**: `str`

#### `sudo_linux_rules['commands']`<a id="variable-sudo_linux_rules-sub-commands"></a>

[*⇑ Back to ToC ⇑*](#toc)

Commands the grantees may run, as absolute paths or the special value
`ALL`. Required for a `present` rule.

- **Type**: `list`
- **Required**: No
- **List Elements**: `str`

#### `sudo_linux_rules['runas']`<a id="variable-sudo_linux_rules-sub-runas"></a>

[*⇑ Back to ToC ⇑*](#toc)

Target identity the commands may be run as, i.e. the `(runas)` part of the
sudoers specification (for example `ALL`, `root`, or `ALL:ALL` to also
allow selecting a group). Falls back to
`sudo_linux_rule_defaults['runas']`.

- **Type**: `str`
- **Required**: No

#### `sudo_linux_rules['nopassword']`<a id="variable-sudo_linux_rules-sub-nopassword"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, the grantees are not prompted for a password (`NOPASSWD`).
Falls back to `sudo_linux_rule_defaults['nopassword']` (which defaults to
`false`, i.e. a password is required).

- **Type**: `bool`
- **Required**: No

#### `sudo_linux_rules['setenv']`<a id="variable-sudo_linux_rules-sub-setenv"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, allow the grantees to set environment variables on the command
line (`SETENV`). Falls back to `sudo_linux_rule_defaults['setenv']`.

- **Type**: `bool`
- **Required**: No

#### `sudo_linux_rules['noexec']`<a id="variable-sudo_linux_rules-sub-noexec"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, prevent the run commands from executing further commands
(`NOEXEC`). Falls back to `sudo_linux_rule_defaults['noexec']`.

- **Type**: `bool`
- **Required**: No

#### `sudo_linux_rules['host']`<a id="variable-sudo_linux_rules-sub-host"></a>

[*⇑ Back to ToC ⇑*](#toc)

Host part of the sudoers specification, restricting the rule to matching
hosts. Falls back to `sudo_linux_rule_defaults['host']` (which defaults
to `ALL`).

- **Type**: `str`
- **Required**: No



### `sudo_linux_rule_defaults`<a id="variable-sudo_linux_rule_defaults"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default values applied to every entry in `sudo_linux_rules` that does not set
the corresponding key itself. The keys mirror the per-rule keys of the same
name (see `sudo_linux_rules`). Any value provided here is overridden by an
explicit value on the individual rule.

Only the keys you want to change need to be supplied; they are merged over the
role's built-in defaults (see `__sudo_linux_rule_defaults_builtin` in
`vars/main.yml`). The effective built-in defaults are:

```yaml
sudo_linux_rule_defaults:
  runas: "ALL"
  host: "ALL"
  nopassword: false   # require a password unless a rule opts out
  setenv: false
  noexec: false
```

Note: the built-in `nopassword: false` deliberately differs from the
`community.general.sudoers` module default (`true`), so that passwordless
sudo is always an explicit, per-rule opt-in.

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `sudo_linux_defaults`<a id="variable-sudo_linux_defaults"></a>

[*⇑ Back to ToC ⇑*](#toc)

Global `Defaults` directives to apply, for sudo-wide settings that are
not tied to a specific rule (the per-rule mechanism cannot express
`Defaults` lines). Each entry is one directive: the role prepends the
`Defaults` keyword and renders one `Defaults <entry>` line into a single
managed, `visudo`-validated drop-in file.

Provide each directive as it would appear after the `Defaults` keyword in
a sudoers file (without the leading `Defaults`).

This covers plain, global `Defaults` only. The qualified forms that attach
a specifier directly to the keyword (`Defaults:user`, `Defaults@host`,
`Defaults>runas`, `Defaults!command`) and any other raw sudoers content
(e.g. `Cmnd_Alias`, `User_Alias`) cannot be expressed here; use
`sudo_linux_extra_content` for those.

Example:
```yaml
sudo_linux_defaults:
  - "env_reset"
  - 'secure_path="/usr/sbin:/usr/bin:/sbin:/bin"'
  - "timestamp_timeout=15"
  - "!visiblepw"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `str`



### `sudo_linux_extra_content`<a id="variable-sudo_linux_extra_content"></a>

[*⇑ Back to ToC ⇑*](#toc)

Last-resort escape hatch: raw sudoers content appended verbatim to the
role's managed, `visudo`-validated drop-in file, after the lines rendered
from `sudo_linux_defaults`. Use it for anything the structured variables
cannot express, for example qualified `Defaults` (`Defaults:user`,
`Defaults@host`, `Defaults>runas`, `Defaults!command`) or alias
definitions (`Cmnd_Alias`, `User_Alias`, `Runas_Alias`).

Unlike `sudo_linux_defaults`, nothing is prepended: write complete,
syntactically valid sudoers lines (including the `Defaults` keyword where
needed). The whole drop-in is still `visudo`-validated, so malformed
content fails the run rather than corrupting sudo. Prefer
`sudo_linux_rules` and `sudo_linux_defaults` whenever possible; reach for
this only when there is no other way.

Example:
```yaml
sudo_linux_extra_content: |
  Defaults:ansible !requiretty
  Cmnd_Alias SERVICES = /usr/bin/systemctl
```

- **Type**: `str`
- **Required**: No
- **Default**: `""`



### `sudo_linux_delete_unmanaged`<a id="variable-sudo_linux_delete_unmanaged"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, the role manages `/etc/sudoers.d/` authoritatively: every
drop-in file that is **not** created by this role is removed, except for

- an internal, per-platform protected list (for example the `README`
  shipped by the `sudo` package on Debian/Ubuntu), and
- the file names listed in `sudo_linux_delete_unmanaged_exclude`.

This is a destructive operation and therefore disabled by default.

Note: regardless of this setting, the role always manages its own
`99_managed_*` drop-ins authoritatively. Renaming a rule or removing a
user/group from a rule deletes the now-orphaned drop-in on the next
run, so a revoked grant never lingers. This option only extends that
cleanup to **foreign** files in `/etc/sudoers.d/`.

WARNING: On cloud images, the file `/etc/sudoers.d/90-cloud-init-users`
typically grants the cloud/admin user passwordless sudo. With this option
enabled it would be deleted unless you add it to
`sudo_linux_delete_unmanaged_exclude`, which can lock you out of the
machine. The same applies to drop-ins shipped by other software (e.g.
SSSD/FreeIPA or vendor agents).

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `sudo_linux_delete_unmanaged_exclude`<a id="variable-sudo_linux_delete_unmanaged_exclude"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of drop-in file names (basenames, relative to `/etc/sudoers.d/`) that
must never be removed by `sudo_linux_delete_unmanaged`, even though they
are not managed by this role. Use this for files shipped by the
distribution or other software that you want to keep, for example
`90-cloud-init-users`.

This supplements the role's internal, per-platform protected list; you do
not need to repeat entries already protected there.

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `str`




<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__sudo_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
