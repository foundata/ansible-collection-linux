# Ansible role: `foundata.linux.user`

The `foundata.linux.user` Ansible role (part of the `foundata.linux` Ansible collection).

Manage local user accounts on Linux systems.


## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`user_linux_account_defaults`](#variable-user_linux_account_defaults)
  - [`user_linux_accounts`](#variable-user_linux_accounts)
    - [`user_linux_accounts['name']`](#variable-user_linux_accounts-sub-name)
    - [`user_linux_accounts['state']`](#variable-user_linux_accounts-sub-state)
    - [`user_linux_accounts['uid']`](#variable-user_linux_accounts-sub-uid)
    - [`user_linux_accounts['comment']`](#variable-user_linux_accounts-sub-comment)
    - [`user_linux_accounts['shell']`](#variable-user_linux_accounts-sub-shell)
    - [`user_linux_accounts['umask']`](#variable-user_linux_accounts-sub-umask)
    - [`user_linux_accounts['system']`](#variable-user_linux_accounts-sub-system)
    - [`user_linux_accounts['local']`](#variable-user_linux_accounts-sub-local)
    - [`user_linux_accounts['seuser']`](#variable-user_linux_accounts-sub-seuser)
    - [`user_linux_accounts['group']`](#variable-user_linux_accounts-sub-group)
    - [`user_linux_accounts['groups']`](#variable-user_linux_accounts-sub-groups)
    - [`user_linux_accounts['groups_append']`](#variable-user_linux_accounts-sub-groups_append)
    - [`user_linux_accounts['expires']`](#variable-user_linux_accounts-sub-expires)
    - [`user_linux_accounts['home']`](#variable-user_linux_accounts-sub-home)
      - [`user_linux_accounts['home']['path']`](#variable-user_linux_accounts-sub-home-sub-path)
      - [`user_linux_accounts['home']['create']`](#variable-user_linux_accounts-sub-home-sub-create)
      - [`user_linux_accounts['home']['move']`](#variable-user_linux_accounts-sub-home-sub-move)
      - [`user_linux_accounts['home']['skeleton']`](#variable-user_linux_accounts-sub-home-sub-skeleton)
    - [`user_linux_accounts['password']`](#variable-user_linux_accounts-sub-password)
      - [`user_linux_accounts['password']['hash']`](#variable-user_linux_accounts-sub-password-sub-hash)
      - [`user_linux_accounts['password']['lock']`](#variable-user_linux_accounts-sub-password-sub-lock)
      - [`user_linux_accounts['password']['update']`](#variable-user_linux_accounts-sub-password-sub-update)
      - [`user_linux_accounts['password']['expire_min']`](#variable-user_linux_accounts-sub-password-sub-expire_min)
      - [`user_linux_accounts['password']['expire_max']`](#variable-user_linux_accounts-sub-password-sub-expire_max)
      - [`user_linux_accounts['password']['expire_warn']`](#variable-user_linux_accounts-sub-password-sub-expire_warn)
    - [`user_linux_accounts['ssh_authorized_keys']`](#variable-user_linux_accounts-sub-ssh_authorized_keys)
      - [`user_linux_accounts['ssh_authorized_keys']['key']`](#variable-user_linux_accounts-sub-ssh_authorized_keys-sub-key)
      - [`user_linux_accounts['ssh_authorized_keys']['options']`](#variable-user_linux_accounts-sub-ssh_authorized_keys-sub-options)
      - [`user_linux_accounts['ssh_authorized_keys']['state']`](#variable-user_linux_accounts-sub-ssh_authorized_keys-sub-state)
    - [`user_linux_accounts['ssh_authorized_keys_delete_unmanaged']`](#variable-user_linux_accounts-sub-ssh_authorized_keys_delete_unmanaged)
  - [`user_linux_group_defaults`](#variable-user_linux_group_defaults)
  - [`user_linux_groups`](#variable-user_linux_groups)
    - [`user_linux_groups['name']`](#variable-user_linux_groups-sub-name)
    - [`user_linux_groups['state']`](#variable-user_linux_groups-sub-state)
    - [`user_linux_groups['gid']`](#variable-user_linux_groups-sub-gid)
    - [`user_linux_groups['system']`](#variable-user_linux_groups-sub-system)
  - [`user_linux_accounts_delete_unmanaged`](#variable-user_linux_accounts_delete_unmanaged)
  - [`user_linux_accounts_delete_unmanaged_exclude`](#variable-user_linux_accounts_delete_unmanaged_exclude)
  - [`user_linux_uid_min`](#variable-user_linux_uid_min)
  - [`user_linux_uid_max`](#variable-user_linux_uid_max)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features<a id="features"></a>

* **Local accounts and groups in one place**: declare groups via [`user_linux_groups`](#variable-user_linux_groups) and accounts via [`user_linux_accounts`](#variable-user_linux_accounts); groups are always created before accounts so they can be used as primary or supplementary groups in the same run.
* **Defaults instead of repetition**: set login shell, umask, group-append behaviour, password update policy and more once in [`user_linux_account_defaults`](#variable-user_linux_account_defaults); every account inherits them unless it overrides the individual key.
* **Home directory handling** via [`home`](#variable-user_linux_accounts-sub-home): choose the `path`, decide whether to `create` it, `move` it when the path changes, and pick the `skeleton` used to populate it.
* **Safe password management** via [`password`](#variable-user_linux_accounts-sub-password): only pre-hashed crypt strings are accepted (plain-text is rejected), with `lock`, an `on_create`-vs-`always` `update` policy, and password aging (`expire_min`/`expire_max`/`expire_warn`).
* **SSH `authorized_keys` management** via [`ssh_authorized_keys`](#variable-user_linux_accounts-sub-ssh_authorized_keys): install keys with optional per-key OpenSSH `options` (e.g. `from=`, `command=`, `restrict`), managed either authoritatively or additively via [`ssh_authorized_keys_delete_unmanaged`](#variable-user_linux_accounts-sub-ssh_authorized_keys_delete_unmanaged). An empty/unset key list never wipes an existing `authorized_keys`.
* **Optional reaping of unmanaged accounts** via [`user_linux_accounts_delete_unmanaged`](#variable-user_linux_accounts_delete_unmanaged): off by default and guarded — only regular accounts inside the `UID_MIN`..`UID_MAX` range are candidates, while `root`, the current Ansible connection user, system accounts and every name in [`user_linux_accounts_delete_unmanaged_exclude`](#variable-user_linux_accounts_delete_unmanaged_exclude) are always protected.


## Example playbooks, using this role<a id="examples"></a>

Use `user_linux_account_defaults` to set a common policy once, then declare a
small admin team. Each account inherits the defaults and only specifies what is
unique to it (note how the password hashes come from a vault, password aging and
SSH key restrictions are applied per account):

```yaml
---

- name: "Manage local users and groups"
  hosts: all
  tasks:

    - name: "Trigger invocation of the foundata.linux.user role"
      ansible.builtin.include_role:
        name: "foundata.linux.user"
      vars:
        # Applied to every account below unless it overrides the key.
        user_linux_account_defaults:
          shell: "/bin/bash"
          umask: "0027"
          groups_append: true
          password:
            update: "on_create"
            expire_max: 365
            expire_warn: 14

        user_linux_groups:
          - name: "webops"
            gid: 4200

        user_linux_accounts:
          - name: "ahaerter"
            comment: "A. Haerter (foundata)"
            groups:
              - "{{ (ansible_facts['os_family'] == 'Debian') | ansible.builtin.ternary('sudo', 'wheel') }}" # 'sudo' on Debian/Ubuntu, 'wheel' elsewhere
              - "webops"
            password:
              hash: "{{ lookup('ansible.builtin.unvault', 'secrets/ahaerter-hash.vault') | ansible.builtin.trim }}"
            ssh_authorized_keys:
              - key: "ssh-ed25519 AAAAC3Nz... foo@example.com"

          - name: "jdoe"
            comment: "J. Doe"
            groups:
              - "webops"
            password:
              hash: "{{ lookup('ansible.builtin.unvault', 'secrets/jdoe-hash.vault') | ansible.builtin.trim }}"
            ssh_authorized_keys:
              # Only allow this key from the office network.
              - key: "ssh-ed25519 AAAAC3Nz... jdoe@example.com"
                options: 'from="10.0.0.0/8"'
```

Create a non-login service account with a fixed UID, a custom home and a
restricted, command-forced backup key (the account has no usable password and
cannot open an interactive shell):

```yaml
---

- name: "Manage a backup service account"
  hosts: all
  tasks:

    - name: "Trigger invocation of the foundata.linux.user role"
      ansible.builtin.include_role:
        name: "foundata.linux.user"
      vars:
        user_linux_accounts:
          - name: "backup"
            comment: "Restic backup runner"
            uid: 6000
            shell: "/usr/sbin/nologin"
            home:
              path: "/srv/backup"
              create: true
            password:
              lock: true
            ssh_authorized_keys:
              - key: "ssh-ed25519 AAAAC3Nz... backup@example.com"
                options: 'restrict,command="/usr/bin/rrsync -ro /srv/backup",from="10.0.0.0/8"'
```

Disable an account without losing its data: lock the password, switch to a
non-interactive shell, make `groups` authoritative so stale memberships are
dropped, and revoke SSH access by replacing the listed key with `state: absent`
(needed because an empty `ssh_authorized_keys` list is intentionally left
untouched and would not remove existing keys):

```yaml
---

- name: "Disable a leaver without deleting data"
  hosts: all
  tasks:

    - name: "Trigger invocation of the foundata.linux.user role"
      ansible.builtin.include_role:
        name: "foundata.linux.user"
      vars:
        user_linux_accounts:
          - name: "jack"
            comment: "Former employee (disabled)"
            shell: "/usr/sbin/nologin"
            groups: [] # authoritative: remove all supplementary memberships
            groups_append: false
            password:
              lock: true
            # Authoritatively drop every key not listed; the explicit
            # 'absent' entry makes the intent (revoke this key) clear.
            ssh_authorized_keys:
              - key: "ssh-ed25519 AAAAC3Nz... jack@example.com"
                state: "absent"
            ssh_authorized_keys_delete_unmanaged: true
```

Remove a specific account and reap any other unmanaged regular accounts (the
connection user, `root` and system accounts are always protected):

```yaml
---

- name: "Remove and reap local users"
  hosts: all
  tasks:

    - name: "Trigger invocation of the foundata.linux.user role"
      ansible.builtin.include_role:
        name: "foundata.linux.user"
      vars:
        user_linux_accounts:
          - name: "ahaerter"
            # ... kept as above ...
          - name: "jdoe"
            # ... kept as above ...
          - name: "obsolete"
            state: "absent"
        user_linux_accounts_delete_unmanaged: true
        user_linux_accounts_delete_unmanaged_exclude:
          - "backup"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `user_linux_config`: Manage the local groups, user accounts and SSH `authorized_keys`.

There are also tags that are generally not intended to be called directly but are included for completeness and to cover edge cases:

- `user_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

Main entry point for the foundata.linux.user role

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `user_linux_account_defaults` | `dict` | No | `{}` | Default values applied to every entry in `user_linux_accounts` that does not set the corresponding key itself. This avoids repeating common settings (login shell, umask, ...) on each account.<br><br>The keys mirror the per-account keys of the same […](#variable-user_linux_account_defaults) |
| `user_linux_accounts` | `list` | No | `[]` | List of local user accounts to manage. Each entry describes one account as a dictionary; `name` is mandatory, all other keys are optional and fall back to `user_linux_account_defaults` (where noted) or to the underlying platform defaults (when […](#variable-user_linux_accounts) |
| `user_linux_group_defaults` | `dict` | No | `{}` | Default values applied to every entry in `user_linux_groups` that does not set the corresponding key itself. The keys mirror the per-group keys of the same name (see `user_linux_groups`); any value provided here is overridden by an explicit value on […](#variable-user_linux_group_defaults) |
| `user_linux_groups` | `list` | No | `[]` | List of local groups to manage. Each entry describes one group as a dictionary; `name` is mandatory, all other keys are optional.<br><br>Groups are created before the accounts in `user_linux_accounts` (so they can be referenced as primary or […](#variable-user_linux_groups) |
| `user_linux_accounts_delete_unmanaged` | `bool` | No | `false` | If `true`, local user accounts that are not listed in `user_linux_accounts` are removed (together with their data). Only regular accounts are considered: an account is a candidate for removal only if its UID is within the `UID_MIN`..`UID_MAX` range […](#variable-user_linux_accounts_delete_unmanaged) |
| `user_linux_accounts_delete_unmanaged_exclude` | `list` | No | `[]` | List of account names that must never be removed by `user_linux_accounts_delete_unmanaged`, even if they are not declared in `user_linux_accounts` and fall within the regular UID range. Useful for break-glass or automation accounts.<br><br>`root` and […](#variable-user_linux_accounts_delete_unmanaged_exclude) |
| `user_linux_uid_min` | `raw` | No | `""` | Lower bound (inclusive) of the UID range that `user_linux_accounts_delete_unmanaged` considers to be regular user accounts. An empty string (the default) means the value is read from `UID_MIN` in `/etc/login.defs` (falling back to `1000` if it cannot […](#variable-user_linux_uid_min) |
| `user_linux_uid_max` | `raw` | No | `""` | Upper bound (inclusive) of the UID range that `user_linux_accounts_delete_unmanaged` considers to be regular user accounts. An empty string (the default) means the value is read from `UID_MAX` in `/etc/login.defs` (falling back to `60000` if it […](#variable-user_linux_uid_max) |

### `user_linux_account_defaults`<a id="variable-user_linux_account_defaults"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default values applied to every entry in `user_linux_accounts` that does not
set the corresponding key itself. This avoids repeating common  settings
(login shell, umask, ...) on each account.

The keys mirror the per-account keys of the same name (see
`user_linux_accounts`). Any value provided here is overridden by an explicit
value on the individual account.

Only the keys you want to change need to be supplied; they are deep-merged
over the role's built-in defaults (see
`__user_linux_account_defaults_builtin` in `vars/main.yml`). The
effective built-in defaults are:

```yaml
user_linux_account_defaults:
  state: "present"
  comment: ""
  shell: "/bin/bash"
  umask: "0027"
  system: false
  local: false
  groups_append: true
  expires: -1
  home:
    create: true
    move: true
  password:
    update: "on_create"
  ssh_authorized_keys_delete_unmanaged: false
```

Supported keys are all known by `user_linux_accounts`.

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `user_linux_accounts`<a id="variable-user_linux_accounts"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of local user accounts to manage. Each entry describes one account
as a dictionary; `name` is mandatory, all other keys are optional and
fall back to `user_linux_account_defaults` (where noted) or to the
underlying platform defaults (when completely undefined).

To remove an account, set its `state` to `absent`: this deletes the user
together with its data (home directory and mail spool). There is intentionally
no option to keep the data while deleting the account. To disable login while
preserving all data, do not delete the account; you could instead set
something like `password['lock']: true` and a non-interactive `shell` like
`/usr/sbin/nologin`).

Example:
```yaml
user_linux_accounts:
  - name: "ahaerter"
    state: "present"
    comment: "Andreas Haerter (foundata)"
    groups:
      # 'sudo' on Debian/Ubuntu, 'wheel' elsewhere
      - "{\{ ((ansible_facts['os_family'] | ansible.builtin.lower) == 'debian') | ansible.builtin.ternary('sudo', 'wheel') }\}"
    password:
      hash: "{\{ lookup('ansible.builtin.unvault', 'secrets/ahaerter-hash.vault') | ansible.builtin.trim }\}"
      update: "always"
    ssh_authorized_keys:
      - key: "ssh-ed25519 AAAAC3Nz..."
  - name: "obsoleteUserToWipe"
    state: "absent"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `dict`

#### `user_linux_accounts['name']`<a id="variable-user_linux_accounts-sub-name"></a>

[*⇑ Back to ToC ⇑*](#toc)

Login name of the account. Must be unique within `user_linux_accounts`.
Use only characters accepted by the platform's `useradd`.

There is no single universal Linux username regex, but the clearest written
rules are in `man useradd`,` `man adduser.conf`, and your local
`/etc/adduser.conf` (if existing).

Typically safe are usernames matching the `^[a-z_][a-z0-9_-]*\$?$` regex:
lowercase letters, digits, underscores and hyphens, not starting with a
hyphen or digit, no dots).

- **Type**: `str`
- **Required**: Yes

#### `user_linux_accounts['state']`<a id="variable-user_linux_accounts-sub-state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Whether the account should be `present` or `absent`. Setting `absent`
deletes the user and its data (home directory and mail spool).

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`

#### `user_linux_accounts['uid']`<a id="variable-user_linux_accounts-sub-uid"></a>

[*⇑ Back to ToC ⇑*](#toc)

Numeric user ID (UID) to assign. If unset, the next free UID in the
platform's range is chosen automatically.

- **Type**: `int`
- **Required**: No

#### `user_linux_accounts['comment']`<a id="variable-user_linux_accounts-sub-comment"></a>

[*⇑ Back to ToC ⇑*](#toc)

GECOS field, usually the full name or a description of the account.

- **Type**: `str`
- **Required**: No

#### `user_linux_accounts['shell']`<a id="variable-user_linux_accounts-sub-shell"></a>

[*⇑ Back to ToC ⇑*](#toc)

Login shell for the account. Falls back to
`user_linux_account_defaults['shell']`.

- **Type**: `str`
- **Required**: No

#### `user_linux_accounts['umask']`<a id="variable-user_linux_accounts-sub-umask"></a>

[*⇑ Back to ToC ⇑*](#toc)

Umask used when the account's home directory is created. Falls back
to `user_linux_account_defaults['umask']`. Octal string, e.g. `0027`.

- **Type**: `str`
- **Required**: No

#### `user_linux_accounts['system']`<a id="variable-user_linux_accounts-sub-system"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, create the account as a system account (UID below the
`UID_MIN` from `/etc/login.defs`). System accounts are never targeted
by `user_linux_accounts_delete_unmanaged`.

- **Type**: `bool`
- **Required**: No

#### `user_linux_accounts['local']`<a id="variable-user_linux_accounts-sub-local"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, manage the account in the local files only (using
`luseradd`/`lusermod`/`luserdel`), bypassing NSS lookups. Relevant
only on hosts whose NSS is backed by a directory (SSSD, LDAP, ...),
where it prevents collisions with directory users; ignored otherwise.
Passed through to `ansible.builtin.user`.

- **Type**: `bool`
- **Required**: No

#### `user_linux_accounts['seuser']`<a id="variable-user_linux_accounts-sub-seuser"></a>

[*⇑ Back to ToC ⇑*](#toc)

SELinux user mapping for the account (the SELinux user the Linux user
is confined to, e.g. `staff_u`). Relevant on SELinux-enforcing platforms
(RHEL/Fedora), ignored on others. Passed through to `ansible.builtin.user`.

- **Type**: `str`
- **Required**: No

#### `user_linux_accounts['group']`<a id="variable-user_linux_accounts-sub-group"></a>

[*⇑ Back to ToC ⇑*](#toc)

Primary group of the account. If unset, the platform creates a
user-private group named after the account.

- **Type**: `str`
- **Required**: No

#### `user_linux_accounts['groups']`<a id="variable-user_linux_accounts-sub-groups"></a>

[*⇑ Back to ToC ⇑*](#toc)

Supplementary, additional groups the account is a member of. As groups
must already exist: declare them either in `user_linux_groups` (which is
applied before `user_linux_accounts` automatically so you do not have to
care about the order) or ensure they are present by other means.

- **Type**: `list`
- **Required**: No
- **List Elements**: `str`

#### `user_linux_accounts['groups_append']`<a id="variable-user_linux_accounts-sub-groups_append"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, the supplementary `groups` are added to the account's
existing memberships. If `false`, `groups` becomes authoritative and
memberships not listed are removed.

- **Type**: `bool`
- **Required**: No

#### `user_linux_accounts['expires']`<a id="variable-user_linux_accounts-sub-expires"></a>

[*⇑ Back to ToC ⇑*](#toc)

Account expiration date as a UNIX timestamp (seconds since the
epoch). After this date the account is disabled. Use `-1` to remove
an existing expiration. This is the account expiry (`chage -E`), not
password aging (see `password.expire_*`).

- **Type**: `float`
- **Required**: No

#### `user_linux_accounts['home']`<a id="variable-user_linux_accounts-sub-home"></a>

[*⇑ Back to ToC ⇑*](#toc)

Home directory settings for the account.

- **Type**: `dict`
- **Required**: No

##### `user_linux_accounts['home']['path']`<a id="variable-user_linux_accounts-sub-home-sub-path"></a>

[*⇑ Back to ToC ⇑*](#toc)

Absolute path of the home directory. Defaults to the platform's
convention (usually `/home/<name>`).

- **Type**: `str`
- **Required**: No

##### `user_linux_accounts['home']['create']`<a id="variable-user_linux_accounts-sub-home-sub-create"></a>

[*⇑ Back to ToC ⇑*](#toc)

Whether to create the home directory for new accounts. Falls back
to `user_linux_account_defaults['home']['create']`.

- **Type**: `bool`
- **Required**: No

##### `user_linux_accounts['home']['move']`<a id="variable-user_linux_accounts-sub-home-sub-move"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true` and `path` differs from the account's current home, the
existing home directory is moved to the new location.

- **Type**: `bool`
- **Required**: No

##### `user_linux_accounts['home']['skeleton']`<a id="variable-user_linux_accounts-sub-home-sub-skeleton"></a>

[*⇑ Back to ToC ⇑*](#toc)

Skeleton directory whose contents are copied into a newly created
home directory (defaults to the platform's `/etc/skel`).

- **Type**: `str`
- **Required**: No


#### `user_linux_accounts['password']`<a id="variable-user_linux_accounts-sub-password"></a>

[*⇑ Back to ToC ⇑*](#toc)

Password and password-aging settings for the account.

- **Type**: `dict`
- **Required**: No

##### `user_linux_accounts['password']['hash']`<a id="variable-user_linux_accounts-sub-password-sub-hash"></a>

[*⇑ Back to ToC ⇑*](#toc)

Pre-hashed password in crypt format (for example a `$6$...` SHA-512
hash). Plain-text passwords are rejected by the role.

Generate a hash on the command line with
`mkpasswd --method=sha-512` (Debian/Ubuntu: package `whois`;
RHEL/Fedora: `mkpasswd`), or within Ansible via the
`ansible.builtin.password_hash` filter, e.g.
`{\{ 'mysecret' | ansible.builtin.password_hash('sha512') }\}`.

- **Type**: `str`
- **Required**: No
- **Sensitive**: Yes (`no_log`, values are masked in logs)

##### `user_linux_accounts['password']['lock']`<a id="variable-user_linux_accounts-sub-password-sub-lock"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, lock the account's password (the hash is kept but login via
password is disabled).

- **Type**: `bool`
- **Required**: No

##### `user_linux_accounts['password']['update']`<a id="variable-user_linux_accounts-sub-password-sub-update"></a>

[*⇑ Back to ToC ⇑*](#toc)

When the password hash is applied: `on_create` only sets it for new
accounts, `always` enforces it on every run. Falls back to
`user_linux_account_defaults['password']['update']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `on_create`, `always`

##### `user_linux_accounts['password']['expire_min']`<a id="variable-user_linux_accounts-sub-password-sub-expire_min"></a>

[*⇑ Back to ToC ⇑*](#toc)

Minimum number of days between password changes (`chage -m`).

- **Type**: `int`
- **Required**: No

##### `user_linux_accounts['password']['expire_max']`<a id="variable-user_linux_accounts-sub-password-sub-expire_max"></a>

[*⇑ Back to ToC ⇑*](#toc)

Maximum number of days a password remains valid (`chage -M`).

- **Type**: `int`
- **Required**: No

##### `user_linux_accounts['password']['expire_warn']`<a id="variable-user_linux_accounts-sub-password-sub-expire_warn"></a>

[*⇑ Back to ToC ⇑*](#toc)

Number of days of warning before a password expires (`chage -W`).

- **Type**: `int`
- **Required**: No


#### `user_linux_accounts['ssh_authorized_keys']`<a id="variable-user_linux_accounts-sub-ssh_authorized_keys"></a>

[*⇑ Back to ToC ⇑*](#toc)

SSH public keys to install in the account's `authorized_keys` file. Each
entry is a dictionary with the key itself and optional restrictions.

Whether keys not listed here are removed is controlled by
`ssh_authorized_keys_delete_unmanaged`. It is `false` by default, so keys
that are already present but not listed here are kept; set it to `true` to
make the listed keys authoritative. As a safety measure, an account with an
empty or unset `ssh_authorized_keys` is left untouched, so omitting the
key list never wipes an existing `authorized_keys`.

Example:
```yaml
ssh_authorized_keys:
  - key: "ssh-ed25519 AAAAC3Nz... u1337@foundata.com"
  - key: "ssh-ed25519 AAAAC3Nz... backup@foundata.com"
    options: 'restrict,command="/usr/bin/rrsync -ro /srv/backup",from="10.0.0.0/8"'
```

- **Type**: `list`
- **Required**: No
- **List Elements**: `dict`

##### `user_linux_accounts['ssh_authorized_keys']['key']`<a id="variable-user_linux_accounts-sub-ssh_authorized_keys-sub-key"></a>

[*⇑ Back to ToC ⇑*](#toc)

A single SSH public key, in the usual `authorized_keys` form
(`<type> <base64> [comment]`).

- **Type**: `str`
- **Required**: Yes

##### `user_linux_accounts['ssh_authorized_keys']['options']`<a id="variable-user_linux_accounts-sub-ssh_authorized_keys-sub-options"></a>

[*⇑ Back to ToC ⇑*](#toc)

Optional OpenSSH `authorized_keys` option string prepended to the key,
restricting how it may be used (for example `from="10.0.0.0/8"`,
`command="..."`, `restrict`, `expiry-time="..."`). See the
`AUTHORIZED_KEYS FILE FORMAT` section of `man sshd` for the full list.

- **Type**: `str`
- **Required**: No

##### `user_linux_accounts['ssh_authorized_keys']['state']`<a id="variable-user_linux_accounts-sub-ssh_authorized_keys-sub-state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Whether the key should be `present` or `absent`. Only meaningful when
`ssh_authorized_keys_delete_unmanaged` is `false` (otherwise unlisted
keys are removed regardless).

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`


#### `user_linux_accounts['ssh_authorized_keys_delete_unmanaged']`<a id="variable-user_linux_accounts-sub-ssh_authorized_keys_delete_unmanaged"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, the account's `authorized_keys` is managed authoritatively:
keys not present in `ssh_authorized_keys` are removed. If `false` (the
built-in default), listed keys are ensured present but other keys are left
in place. Falls back to
`user_linux_account_defaults['ssh_authorized_keys_delete_unmanaged']`.

- **Type**: `bool`
- **Required**: No



### `user_linux_group_defaults`<a id="variable-user_linux_group_defaults"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default values applied to every entry in `user_linux_groups` that does not
set the corresponding key itself. The keys mirror the per-group keys of the
same name (see `user_linux_groups`); any value provided here is overridden by
an explicit value on the individual group.

Only the keys you want to change need to be supplied; they are deep-merged
over the role's built-in defaults (see `__user_linux_group_defaults_builtin`
in `vars/main.yml`). The effective built-in defaults are:

```yaml
user_linux_group_defaults:
  state: "present"
  system: false
```

Supported keys are all known by `user_linux_groups`.

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `user_linux_groups`<a id="variable-user_linux_groups"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of local groups to manage. Each entry describes one group as a
dictionary; `name` is mandatory, all other keys are optional.

Groups are created before the accounts in `user_linux_accounts` (so they
can be referenced as primary or supplementary groups) and groups set to
`absent` are removed after the accounts.

Note: When a user is deleted, its user-private group (a group with the
same name as the user, created together with the account) is removed
automatically by the platform if no other user still uses it. You only
need to list groups here that you want to manage explicitly.

Example:
```yaml
user_linux_groups:
  - name: "webops"
    gid: 4200
  - name: "legacy"
    state: "absent"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `dict`

#### `user_linux_groups['name']`<a id="variable-user_linux_groups-sub-name"></a>

[*⇑ Back to ToC ⇑*](#toc)

Name of the group. Must be unique within `user_linux_groups`.

- **Type**: `str`
- **Required**: Yes

#### `user_linux_groups['state']`<a id="variable-user_linux_groups-sub-state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Whether the group should be `present` or `absent`.

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`

#### `user_linux_groups['gid']`<a id="variable-user_linux_groups-sub-gid"></a>

[*⇑ Back to ToC ⇑*](#toc)

Numeric group ID (GID) to assign. If unset, the next free GID is
chosen automatically.

- **Type**: `int`
- **Required**: No

#### `user_linux_groups['system']`<a id="variable-user_linux_groups-sub-system"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, create the group as a system group (GID below the
platform's range for regular groups).

- **Type**: `bool`
- **Required**: No



### `user_linux_accounts_delete_unmanaged`<a id="variable-user_linux_accounts_delete_unmanaged"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, local user accounts that are not listed in
`user_linux_accounts` are removed (together with their data). Only regular
accounts are considered: an account is a candidate for removal only if its UID
is within the `UID_MIN`..`UID_MAX` range (see `user_linux_uid_min` /
`user_linux_uid_max`), so system accounts are never touched.

The following accounts are always protected, even when not listed in
`user_linux_accounts`: `root`, the account Ansible is currently connected as,
and every name in `user_linux_accounts_delete_unmanaged_exclude`.

This is a destructive operation and therefore disabled by default.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `user_linux_accounts_delete_unmanaged_exclude`<a id="variable-user_linux_accounts_delete_unmanaged_exclude"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of account names that must never be removed by
`user_linux_accounts_delete_unmanaged`, even if they are not declared in
`user_linux_accounts` and fall within the regular UID range. Useful for
break-glass or automation accounts.

`root` and the current Ansible connection user are always protected and do not
need to be listed here.

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `str`



### `user_linux_uid_min`<a id="variable-user_linux_uid_min"></a>

[*⇑ Back to ToC ⇑*](#toc)

Lower bound (inclusive) of the UID range that
`user_linux_accounts_delete_unmanaged` considers to be regular user accounts.
An empty string (the default) means the value is read from `UID_MIN` in
`/etc/login.defs` (falling back to `1000` if it cannot be determined).
Any other value must be a non-negative integer; the role fails on
malformed values instead of silently misinterpreting them.

- **Type**: `raw`
- **Required**: No
- **Default**: `""`



### `user_linux_uid_max`<a id="variable-user_linux_uid_max"></a>

[*⇑ Back to ToC ⇑*](#toc)

Upper bound (inclusive) of the UID range that
`user_linux_accounts_delete_unmanaged` considers to be regular user
accounts. An empty string (the default) means the value is read from
`UID_MAX` in `/etc/login.defs` (falling back to `60000` if it cannot be
determined). Any other value must be a non-negative integer; the role
fails on malformed values instead of silently misinterpreting them.

- **Type**: `raw`
- **Required**: No
- **Default**: `""`




<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__user_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
