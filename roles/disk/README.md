# Ansible role: `foundata.linux.disk`

The `foundata.linux.disk` Ansible role (part of the `foundata.linux` Ansible collection) manages dedicated data disks. It takes a whole block device from raw disk to mounted filesystem a single partition spanning the disk, a filesystem (XFS or ext4) on it, and a mount plus `/etc/fstab` entry by filesystem UUID.

The role is built to never reformat or destroy existing data by default: it verifies the declared layout (partition table type, single partition, filesystem type) against the disk and fails hard on any deviation (`on_mismatch`) or mount/fstab conflicts.


## Table of contents<a id="toc"></a>

- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`disk_linux_state`](#variable-disk_linux_state)
  - [`disk_linux_autoupgrade`](#variable-disk_linux_autoupgrade)
  - [`disk_linux_device_defaults`](#variable-disk_linux_device_defaults)
    - [`disk_linux_device_defaults['state']`](#variable-disk_linux_device_defaults-sub-state)
    - [`disk_linux_device_defaults['wipe']`](#variable-disk_linux_device_defaults-sub-wipe)
    - [`disk_linux_device_defaults['on_missing']`](#variable-disk_linux_device_defaults-sub-on_missing)
    - [`disk_linux_device_defaults['on_mismatch']`](#variable-disk_linux_device_defaults-sub-on_mismatch)
    - [`disk_linux_device_defaults['partition_table']`](#variable-disk_linux_device_defaults-sub-partition_table)
    - [`disk_linux_device_defaults['grow']`](#variable-disk_linux_device_defaults-sub-grow)
    - [`disk_linux_device_defaults['filesystem']`](#variable-disk_linux_device_defaults-sub-filesystem)
      - [`disk_linux_device_defaults['filesystem']['type']`](#variable-disk_linux_device_defaults-sub-filesystem-sub-type)
      - [`disk_linux_device_defaults['filesystem']['mkfs_options']`](#variable-disk_linux_device_defaults-sub-filesystem-sub-mkfs_options)
    - [`disk_linux_device_defaults['mount']`](#variable-disk_linux_device_defaults-sub-mount)
      - [`disk_linux_device_defaults['mount']['options']`](#variable-disk_linux_device_defaults-sub-mount-sub-options)
      - [`disk_linux_device_defaults['mount']['dump']`](#variable-disk_linux_device_defaults-sub-mount-sub-dump)
      - [`disk_linux_device_defaults['mount']['passno']`](#variable-disk_linux_device_defaults-sub-mount-sub-passno)
      - [`disk_linux_device_defaults['mount']['on_nonempty']`](#variable-disk_linux_device_defaults-sub-mount-sub-on_nonempty)
      - [`disk_linux_device_defaults['mount']['selinux_relabel']`](#variable-disk_linux_device_defaults-sub-mount-sub-selinux_relabel)
  - [`disk_linux_devices`](#variable-disk_linux_devices)
    - [`disk_linux_devices['device']`](#variable-disk_linux_devices-sub-device)
    - [`disk_linux_devices['state']`](#variable-disk_linux_devices-sub-state)
    - [`disk_linux_devices['wipe']`](#variable-disk_linux_devices-sub-wipe)
    - [`disk_linux_devices['on_missing']`](#variable-disk_linux_devices-sub-on_missing)
    - [`disk_linux_devices['on_mismatch']`](#variable-disk_linux_devices-sub-on_mismatch)
    - [`disk_linux_devices['partition_table']`](#variable-disk_linux_devices-sub-partition_table)
    - [`disk_linux_devices['grow']`](#variable-disk_linux_devices-sub-grow)
    - [`disk_linux_devices['filesystem']`](#variable-disk_linux_devices-sub-filesystem)
      - [`disk_linux_devices['filesystem']['type']`](#variable-disk_linux_devices-sub-filesystem-sub-type)
      - [`disk_linux_devices['filesystem']['mkfs_options']`](#variable-disk_linux_devices-sub-filesystem-sub-mkfs_options)
    - [`disk_linux_devices['mount']`](#variable-disk_linux_devices-sub-mount)
      - [`disk_linux_devices['mount']['path']`](#variable-disk_linux_devices-sub-mount-sub-path)
      - [`disk_linux_devices['mount']['options']`](#variable-disk_linux_devices-sub-mount-sub-options)
      - [`disk_linux_devices['mount']['dump']`](#variable-disk_linux_devices-sub-mount-sub-dump)
      - [`disk_linux_devices['mount']['passno']`](#variable-disk_linux_devices-sub-mount-sub-passno)
      - [`disk_linux_devices['mount']['on_nonempty']`](#variable-disk_linux_devices-sub-mount-sub-on_nonempty)
      - [`disk_linux_devices['mount']['selinux_relabel']`](#variable-disk_linux_devices-sub-mount-sub-selinux_relabel)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Example playbooks, using this role<a id="examples"></a>

Minimal usage, one data disk with all defaults (GPT partition table, XFS, mounted by UUID):

```yaml
---

- name: "Provision a dedicated data disk"
  hosts: "example_hosts"
  tasks:

    - name: "Trigger invocation of the foundata.linux.disk role"
      ansible.builtin.include_role:
        name: "foundata.linux.disk"
      vars:
        disk_linux_devices:
          - device: "/dev/disk/by-id/virtio-data0"
            mount:
              path: "/srv/data"
```

Two dedicated disks with shared settings hoisted into the defaults dictionary:

```yaml
---

- name: "Provision dedicated disks for home directories and services"
  hosts: "example_hosts"
  tasks:

    - name: "Trigger invocation of the foundata.linux.disk role"
      ansible.builtin.include_role:
        name: "foundata.linux.disk"
      vars:
        disk_linux_device_defaults:
          mount:
            options: "defaults,noatime"
        disk_linux_devices:
          - device: "/dev/disk/by-id/virtio-home0"
            mount:
              path: "/home"
              options: "defaults,noatime,nodev"
              on_nonempty: "copy" # migrate the existing home directories onto
                                  # the new filesystem on the first mount
          - device: "/dev/disk/by-id/virtio-srv0"
            mount:
              path: "/srv"
```

Mixed filesystems, boot-time `fsck` for ext4, a legacy MBR disk, an optional per-host disk, repurposing a disk with foreign content, and decommissioning a disk including data destruction:

```yaml
---

- name: "Manage the full disk layout of a database host"
  hosts: "example_hosts"
  tasks:

    - name: "Trigger invocation of the foundata.linux.disk role"
      ansible.builtin.include_role:
        name: "foundata.linux.disk"
      vars:
        disk_linux_devices:
          - device: "/dev/disk/by-id/ata-EXAMPLE_SSD_S3Z8NB0M801151"
            grow: false # unpartitioned space at the disk end is intentional
                        # (SSD over-provisioning); do not reclaim it
            filesystem:
              type: "ext4"
              mkfs_options: "-m 1"
            mount:
              path: "/var/lib/postgresql"
              options: "defaults,noatime"
              passno: 2
          - device: "/dev/disk/by-id/virtio-legacy0"
            partition_table: "msdos" # set up by earlier automation with an MBR;
                                     # declare what is actually on the disk
            mount:
              path: "/srv/legacy"
          - device: "/dev/disk/by-id/virtio-scratch0"
            on_missing: "skip" # not every host of the group has a scratch disk
            mount:
              path: "/srv/scratch"
          - device: "/dev/disk/by-id/virtio-repurposed0"
            on_mismatch: "wipe" # disk carried a foreign filesystem: erase it and
                                # set up per declaration (DESTROYS its data);
                                # remove this line after the conversion happened
            mount:
              path: "/srv/imports"
          - device: "/dev/disk/by-id/virtio-olddata0"
            state: "absent" # unmount and remove from /etc/fstab ...
            wipe: true # ... AND destroy the data; the disk is blank afterwards
            mount:
              path: "/mnt/olddata"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `disk_linux_setup`: Manage basic resources, such as the needed partitioning and filesystem tool packages.
- `disk_linux_config`: Manage the devices: partitioning, filesystem creation, content migration, mounting and `/etc/fstab`.

There are also tags that are generally not intended to be called directly but are included for completeness and to cover edge cases:

- `disk_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

Main entry point for the foundata.linux.disk role

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `disk_linux_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-disk_linux_state) |
| `disk_linux_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one).<br><br>Note: The role installs only the tools the declared devices actually […](#variable-disk_linux_autoupgrade) |
| `disk_linux_device_defaults` | `dict` | No | `{}` | Default values applied to every entry in `disk_linux_devices` that does not set the corresponding key itself. This avoids repeating common settings (filesystem, mount options, ...) on each device.<br><br>The keys mirror the per-device keys of the […](#variable-disk_linux_device_defaults) |
| `disk_linux_devices` | `list` | No | `[]` | List of dedicated data disks to manage. Each entry describes one whole block device that is taken from raw disk to mounted filesystem: a single partition spanning the disk (kept spanning after disk enlargement, see `grow`), a filesystem on that […](#variable-disk_linux_devices) |

### `disk_linux_state`<a id="variable-disk_linux_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, …

Note: For this role, the required component and package set is minimal.
There are no users or services to manage, and the partitioning and
filesystem tools it installs (`parted`, `xfsprogs`, `e2fsprogs`,
`util-linux`) are base-system components that cannot be safely removed
due to dependencies, so the role does not uninstall them.

On `absent`, every entry in `disk_linux_devices` is treated as
`state: "absent"`: the filesystems are unmounted and their `/etc/fstab`
entries are removed, while partitions, filesystems, data and the
mountpoint directories are kept. This global `absent` is a
non-destructive override: a per-device `wipe: true` is only honored
when the entry's own effective `state` — computed from the built-in
defaults, `disk_linux_device_defaults` and the entry itself, without
this variable — is `absent`. Entries whose effective state is
`present` are never wiped through this switch, so a leftover `wipe`
setting cannot destroy data when decommissioning a host.

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `disk_linux_autoupgrade`<a id="variable-disk_linux_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

Note: The role installs only the tools the declared devices actually need
(for example `xfsprogs` only when at least one entry uses the `xfs`
filesystem). These are base-system tools; they are never uninstalled by
this role.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `disk_linux_device_defaults`<a id="variable-disk_linux_device_defaults"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default values applied to every entry in `disk_linux_devices` that does
not set the corresponding key itself. This avoids repeating common
settings (filesystem, mount options, ...) on each device.

The keys mirror the per-device keys of the same name (see
`disk_linux_devices` for the full documentation of each key), except
`device` and `mount['path']` which are always per-device. Nested keys
are deep-merged: an entry that sets only `mount['options']` still
inherits `mount['passno']` and the other `mount` defaults. Any value
provided here is overridden by an explicit value on the individual
device entry.

Only the keys you want to change need to be supplied; they are
deep-merged over the role's built-in defaults (see
`__disk_linux_device_defaults_builtin` in `vars/main.yml`). The effective
built-in defaults are:

```yaml
disk_linux_device_defaults:
  state: "present"
  wipe: false
  on_missing: "fail"
  on_mismatch: "fail"
  partition_table: "gpt"
  grow: true
  filesystem:
    type: "xfs"
    mkfs_options: ""
  mount:
    options: "defaults"
    dump: 0
    passno: 0
    on_nonempty: "fail"
    selinux_relabel: "created"
```

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`

#### `disk_linux_device_defaults['state']`<a id="variable-disk_linux_device_defaults-sub-state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['state']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `present`, `absent`

#### `disk_linux_device_defaults['wipe']`<a id="variable-disk_linux_device_defaults-sub-wipe"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['wipe']`.

- **Type**: `bool`
- **Required**: No

#### `disk_linux_device_defaults['on_missing']`<a id="variable-disk_linux_device_defaults-sub-on_missing"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['on_missing']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `fail`, `skip`

#### `disk_linux_device_defaults['on_mismatch']`<a id="variable-disk_linux_device_defaults-sub-on_mismatch"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['on_mismatch']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `fail`, `skip`, `wipe`

#### `disk_linux_device_defaults['partition_table']`<a id="variable-disk_linux_device_defaults-sub-partition_table"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['partition_table']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `gpt`, `msdos`

#### `disk_linux_device_defaults['grow']`<a id="variable-disk_linux_device_defaults-sub-grow"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['grow']`.

- **Type**: `bool`
- **Required**: No

#### `disk_linux_device_defaults['filesystem']`<a id="variable-disk_linux_device_defaults-sub-filesystem"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defaults for the per-device `filesystem` dictionary; see
`disk_linux_devices['filesystem']`.

- **Type**: `dict`
- **Required**: No

##### `disk_linux_device_defaults['filesystem']['type']`<a id="variable-disk_linux_device_defaults-sub-filesystem-sub-type"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['filesystem']['type']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `xfs`, `ext4`

##### `disk_linux_device_defaults['filesystem']['mkfs_options']`<a id="variable-disk_linux_device_defaults-sub-filesystem-sub-mkfs_options"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['filesystem']['mkfs_options']`.

- **Type**: `str`
- **Required**: No


#### `disk_linux_device_defaults['mount']`<a id="variable-disk_linux_device_defaults-sub-mount"></a>

[*⇑ Back to ToC ⇑*](#toc)

Defaults for the per-device `mount` dictionary (except `path`, which
is always per-device); see `disk_linux_devices['mount']`.

- **Type**: `dict`
- **Required**: No

##### `disk_linux_device_defaults['mount']['options']`<a id="variable-disk_linux_device_defaults-sub-mount-sub-options"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['mount']['options']`.

- **Type**: `str`
- **Required**: No

##### `disk_linux_device_defaults['mount']['dump']`<a id="variable-disk_linux_device_defaults-sub-mount-sub-dump"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['mount']['dump']`.

- **Type**: `int`
- **Required**: No
- **Choices**: `0`, `1`

##### `disk_linux_device_defaults['mount']['passno']`<a id="variable-disk_linux_device_defaults-sub-mount-sub-passno"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['mount']['passno']`.

- **Type**: `int`
- **Required**: No
- **Choices**: `0`, `2`

##### `disk_linux_device_defaults['mount']['on_nonempty']`<a id="variable-disk_linux_device_defaults-sub-mount-sub-on_nonempty"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['mount']['on_nonempty']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `fail`, `copy`, `hide`

##### `disk_linux_device_defaults['mount']['selinux_relabel']`<a id="variable-disk_linux_device_defaults-sub-mount-sub-selinux_relabel"></a>

[*⇑ Back to ToC ⇑*](#toc)

Default for the per-device key of the same name; see
`disk_linux_devices['mount']['selinux_relabel']`.

- **Type**: `str`
- **Required**: No
- **Choices**: `never`, `created`, `first_mount`




### `disk_linux_devices`<a id="variable-disk_linux_devices"></a>

[*⇑ Back to ToC ⇑*](#toc)

List of dedicated data disks to manage. Each entry describes one whole
block device that is taken from raw disk to mounted filesystem: a single
partition spanning the disk (kept spanning after disk enlargement, see
`grow`), a filesystem on that partition, and a mount (plus `/etc/fstab`
entry) by filesystem UUID. `device` and `mount['path']` are mandatory;
all other keys are optional and fall back to
`disk_linux_device_defaults`.

Both `device` and `mount['path']` must be unique across the list.
Entries may nest (for example `/srv` and `/srv/data`); the role orders
the work by mount dependency automatically: `present` entries are
processed parent-first, `absent` entries child-first, independent of
the list order. A parent that is effectively `absent` while a child
below it is `present` fails validation; when a parent entry is skipped
(`on_missing`/`on_mismatch`: `skip`), all entries below its path are
skipped too, with a notice — mounting them would land on the wrong
filesystem.

The declared layout (partition table type, single partition, filesystem
type) is verified against the disk. Existing data is never reformatted
or destroyed by default: the role only partitions blank disks and
creates filesystems only on partitions it created itself during the
same run; any other deviation of a non-blank disk from the declaration
is handled according to `on_missing` and `on_mismatch` (both default
to failing hard before any change). After every change to
`/etc/fstab`, the role validates the result with `findmnt --verify`
and fails before a broken table can surface at the next boot.

Safety invariants, guaranteed before any change to any disk (not
configurable): every existing `device` path is resolved to its
canonical block device identity, and the role rejects two entries
addressing the same disk through different aliases, paths that are
not a whole disk (a partition or a device-mapper child), and disks
backing the running system (`/`, `/boot`, the EFI system partition,
active swap). All entries are preflighted before the first one is
changed. Entries whose device is missing are exempt from the
block-device identity checks - they are handled by `on_missing` and
the absent-state cleanup, and still participate in the mount-path
and `/etc/fstab` validation.

Conflicting environments make the role fail before any change, without
a bypass option: the mountpoint already carrying a mount from a
different source, an active mount below the entry's path that mounting
it would hide, the declared filesystem being mounted somewhere else,
`/etc/fstab` lines not managed by the role conflicting by source or
target, and duplicate filesystem UUIDs (for example from cloned disks)
are all treated as errors that need a human decision - the role never
resolves them by unmounting or replacing anything automatically.

Example:
```yaml
disk_linux_devices:
  - device: "/dev/disk/by-id/virtio-home0"
    mount:
      path: "/home"
      options: "defaults,noatime,nodev"
      on_nonempty: "copy"
  - device: "/dev/disk/by-id/virtio-olddata0"
    mount:
      path: "/mnt/olddata"
    state: "absent"
```

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **List Elements**: `dict`

#### `disk_linux_devices['device']`<a id="variable-disk_linux_devices-sub-device"></a>

[*⇑ Back to ToC ⇑*](#toc)

Absolute path to the whole disk to manage (not a partition). A stable
path below `/dev/disk/by-id/` is strongly recommended (for example
`/dev/disk/by-id/virtio-data0` for a virtio disk with serial
`data0`); kernel names like `/dev/vdb` work but may change between
boots.

The role derives the partition device from this path (partition 1)
and always mounts by filesystem UUID, so the path is only used to
find the disk and is never written to `/etc/fstab`.

- **Type**: `path`
- **Required**: Yes

#### `disk_linux_devices['state']`<a id="variable-disk_linux_devices-sub-state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Whether the device should be `present` (partitioned, formatted,
mounted and in `/etc/fstab`) or `absent`. Setting `absent` unmounts
the filesystem and removes its `/etc/fstab` entry, but keeps the
mountpoint directory, the partition, the filesystem and all data on
it, so the entry can be re-enabled later. This cleanup also works
when the disk itself has already been detached (see `on_missing`).
To also destroy the on-disk data, additionally set `wipe: true`.
Falls back to `disk_linux_device_defaults['state']` (built-in
default `present`).

- **Type**: `str`
- **Required**: No
- **Choices**: `present`, `absent`

#### `disk_linux_devices['wipe']`<a id="variable-disk_linux_devices-sub-wipe"></a>

[*⇑ Back to ToC ⇑*](#toc)

Destructive, only honored when the entry's effective `state` is
`absent` (ignored with a notice otherwise): after unmounting and
removing the `/etc/fstab` entry, the filesystem signature of the
partition and the partition table of the disk are erased
(`wipefs`). This is logical destruction, not secure erasure: only
the recognizable signatures are removed, the data blocks are not
overwritten. The disk is blank to the system afterwards (no
recovery of the destroyed structures except from backup, and a
later run with `state: present` would set it up again from
scratch), but considerable data may remain forensically
recoverable. Before disposing of or handing over media, use
dedicated secure-erase tooling (for example `blkdiscard`,
`shred`, or a cryptographic erase).

The effective `state` is computed from the built-in defaults,
`disk_linux_device_defaults` and the entry itself. Inherited values
count: declaring `state: "absent"` together with `wipe: true` in
`disk_linux_device_defaults` wipes every listed device. The
role-global `disk_linux_state: "absent"` however never enables
wiping (see its description).

To repurpose a disk with conflicting content in a single run (wipe
and set up according to the declaration), use `on_mismatch: "wipe"`
instead. Falls back to `disk_linux_device_defaults['wipe']`
(built-in default `false`).

- **Type**: `bool`
- **Required**: No

#### `disk_linux_devices['on_missing']`<a id="variable-disk_linux_devices-sub-on_missing"></a>

[*⇑ Back to ToC ⇑*](#toc)

What to do when the configured `device` path does not exist on the
host. Applies to `state: present` and to the destructive part of
`state: absent` (`wipe: true`):

- `fail`: abort the play. A missing dedicated disk usually is a
  provisioning error that should be noticed (default).
- `skip`: skip the affected actions without an error, useful for
  group inventories where only some hosts have the optional disk
  attached.

The non-destructive cleanup of `state: absent` (unmounting and
removing the `/etc/fstab` entry) always proceeds regardless of the
device's presence - a detached disk is the normal decommissioning
case. With `wipe: true` and a missing device, `skip` performs the
cleanup but skips the wipe with a notice, while `fail` aborts.

Falls back to `disk_linux_device_defaults['on_missing']` (built-in
default `fail`).

- **Type**: `str`
- **Required**: No
- **Choices**: `fail`, `skip`

#### `disk_linux_devices['on_mismatch']`<a id="variable-disk_linux_devices-sub-on_mismatch"></a>

[*⇑ Back to ToC ⇑*](#toc)

What to do when the disk exists, is not blank, and its content
contradicts the declared layout. A mismatch is any of: a partition
table of a different type than `partition_table`; a filesystem or
other signature directly on the whole disk (no partition table); a
partition layout other than exactly one partition numbered 1; a
filesystem on the partition that differs from `filesystem['type']`;
a pre-existing partition without any recognizable filesystem
signature (an existing partition is evidence the disk was in use,
and a missing signature does not prove the absence of data - the
role only creates filesystems on partitions it created itself
during the same run); or a layout that would require shrinking a
partition or filesystem (shrinking is never performed). A blank
disk is not a mismatch (normal setup), and neither is an
undersized partition after the disk was enlarged - that is
reconciled or tolerated according to `grow`.

- `fail`: abort with a message describing the difference. A mismatch
  usually means the `device` path points at the wrong disk or the
  disk carries foreign data; failing is the only safe reaction
  (default).
- `skip`: leave the disk untouched and skip this entry with a
  notice. Useful when foreign disks are expected and should stay
  unmanaged.
- `wipe`: destructive. Erase the conflicting structures (`wipefs`;
  unmounting the old filesystem first if needed) and set the disk up
  from scratch according to the declaration. All existing data on
  the disk becomes inaccessible (logical destruction as with
  `wipe`: signatures are removed, data blocks are not overwritten
  and may remain forensically recoverable); there is no recovery
  except from backup.
  Intended for deliberately repurposing disks - remove the setting
  again once the conversion has happened. The role emits a warning
  whenever this branch actually wipes something.

  `wipe` repurposes INACTIVE disks only: it does not tear down
  mounted LUKS, LVM, MD RAID or other foreign storage stacks.
  The whole device tree is checked before mutation; any mounted
  descendant or an `/etc/fstab` reference to a UUID anywhere in
  the tree aborts the run. Unmount the tree and remove its
  foreign persistence first.

Note that the partition table type is part of the declared layout on
purpose: for existing disks set up with an `msdos` label by earlier
automation, declare `partition_table: "msdos"` so the inventory
states what is actually on the disk, instead of the role silently
tolerating a layout the inventory does not describe.

Falls back to `disk_linux_device_defaults['on_mismatch']` (built-in
default `fail`).

- **Type**: `str`
- **Required**: No
- **Choices**: `fail`, `skip`, `wipe`

#### `disk_linux_devices['partition_table']`<a id="variable-disk_linux_devices-sub-partition_table"></a>

[*⇑ Back to ToC ⇑*](#toc)

Partition table type (disk label) of the disk. Part of the declared
layout: on blank disks a table of this type is created; a non-blank
disk whose existing table type differs is a mismatch and handled
according to `on_mismatch`. The role never re-labels a disk outside
of the explicit `on_mismatch: "wipe"` path (a re-label destroys the
existing partition table).

Use `msdos` when legacy tooling requires an MBR - and for existing
disks that were set up with an `msdos` label by earlier automation,
so the declaration matches the disk. Falls back to
`disk_linux_device_defaults['partition_table']` (built-in default
`gpt`).

- **Type**: `str`
- **Required**: No
- **Choices**: `gpt`, `msdos`

#### `disk_linux_devices['grow']`<a id="variable-disk_linux_devices-sub-grow"></a>

[*⇑ Back to ToC ⇑*](#toc)

If `true`, an undersized layout after the disk was enlarged (for
example a grown virtual disk) is reconciled without data loss:
partition 1 is extended to span the disk again and the filesystem is
grown to the partition size. Both happen online; no unmount is
needed for `xfs` or `ext4`. If `false`, an undersized partition is
tolerated and left unchanged, which allows keeping unpartitioned
space at the end of the disk on purpose (for example SSD
over-provisioning).

Shrinking is never performed, regardless of this setting; a layout
that would require it is a mismatch (see `on_mismatch`). Falls back
to `disk_linux_device_defaults['grow']` (built-in default `true`).

- **Type**: `bool`
- **Required**: No

#### `disk_linux_devices['filesystem']`<a id="variable-disk_linux_devices-sub-filesystem"></a>

[*⇑ Back to ToC ⇑*](#toc)

Filesystem configuration for the disk's single partition. The keys
are deep-merged over `disk_linux_device_defaults['filesystem']`, so
partially set dictionaries inherit the remaining defaults.

- **Type**: `dict`
- **Required**: No

##### `disk_linux_devices['filesystem']['type']`<a id="variable-disk_linux_devices-sub-filesystem-sub-type"></a>

[*⇑ Back to ToC ⇑*](#toc)

Filesystem to create on the partition and to use for mounting.
Falls back to
`disk_linux_device_defaults['filesystem']['type']` (built-in
default `xfs`).

Only used when creating the filesystem: an existing filesystem
of this type is left untouched (including all of its
creation-time parameters), and the role only ever creates
filesystems on partitions it created itself during the same
run. A different existing filesystem is a mismatch, as is a
pre-existing partition without any recognizable signature (see
`on_mismatch`) - so changing the type of an already set up
device requires either
`on_mismatch: "wipe"` (single run) or a wipe-and-recreate cycle
(one run with `state: absent` plus `wipe: true`, then a run
with `state: present`). Both destroy the data on the disk.

- **Type**: `str`
- **Required**: No
- **Choices**: `xfs`, `ext4`

##### `disk_linux_devices['filesystem']['mkfs_options']`<a id="variable-disk_linux_devices-sub-filesystem-sub-mkfs_options"></a>

[*⇑ Back to ToC ⇑*](#toc)

Additional command line options passed to the `mkfs` call when
the filesystem is created (for example `-m 1` to lower the
reserved-blocks percentage of `ext4`). Only applied at creation
time; changing this value later has no effect on an existing
filesystem. Falls back to
`disk_linux_device_defaults['filesystem']['mkfs_options']`
(built-in default: empty string).

- **Type**: `str`
- **Required**: No


#### `disk_linux_devices['mount']`<a id="variable-disk_linux_devices-sub-mount"></a>

[*⇑ Back to ToC ⇑*](#toc)

Mount configuration: where and how the filesystem is mounted (and
written to `/etc/fstab`), plus the behaviors tied to the very first
mount. `path` is mandatory; the other keys are deep-merged over
`disk_linux_device_defaults['mount']`, so partially set dictionaries
inherit the remaining defaults.

- **Type**: `dict`
- **Required**: Yes

##### `disk_linux_devices['mount']['path']`<a id="variable-disk_linux_devices-sub-mount-sub-path"></a>

[*⇑ Back to ToC ⇑*](#toc)

Absolute path of the directory the filesystem is mounted on
(also used for the `/etc/fstab` entry). Created if missing. Must
be unique across `disk_linux_devices`.

- **Type**: `path`
- **Required**: Yes

##### `disk_linux_devices['mount']['options']`<a id="variable-disk_linux_devices-sub-mount-sub-options"></a>

[*⇑ Back to ToC ⇑*](#toc)

Mount options for the filesystem as a comma-separated string,
written to the fourth `/etc/fstab` field and used for mounting.
Falls back to `disk_linux_device_defaults['mount']['options']`
(built-in default `defaults`).

- **Type**: `str`
- **Required**: No

##### `disk_linux_devices['mount']['dump']`<a id="variable-disk_linux_devices-sub-mount-sub-dump"></a>

[*⇑ Back to ToC ⇑*](#toc)

`dump(8)` backup flag, written to the fifth `/etc/fstab` field.
Almost always `0` (dump is not used on modern systems). Falls
back to `disk_linux_device_defaults['mount']['dump']` (built-in
default `0`).

- **Type**: `int`
- **Required**: No
- **Choices**: `0`, `1`

##### `disk_linux_devices['mount']['passno']`<a id="variable-disk_linux_devices-sub-mount-sub-passno"></a>

[*⇑ Back to ToC ⇑*](#toc)

`fsck` order at boot, written to the sixth `/etc/fstab` field.
`0` disables the boot-time filesystem check. `2` is conventional
for `ext4` data filesystems; keep `0` for `xfs` (its boot-time
`fsck.xfs` is a no-op by design). `1` is not permitted: it is
reserved for the root filesystem by convention, and a root disk
is outside this role's scope. Falls back to
`disk_linux_device_defaults['mount']['passno']` (built-in
default `0`).

- **Type**: `int`
- **Required**: No
- **Choices**: `0`, `2`

##### `disk_linux_devices['mount']['on_nonempty']`<a id="variable-disk_linux_devices-sub-mount-sub-on_nonempty"></a>

[*⇑ Back to ToC ⇑*](#toc)

What to do when the mountpoint directory already contains files
at the time of the very first mount (once the filesystem has
been mounted, later runs are unaffected):

- `fail`: abort before mounting, with a message naming this
  option (default). Mounting would hide the existing content -
  stopping is the only safe reaction without knowing whether
  that content matters. Mounting a fresh filesystem over a
  populated `/home`, for example, hides every existing home
  directory including `.ssh/authorized_keys`, breaking SSH
  public key authentication for the whole host in the middle of
  the play.
- `copy`: one-time migration of the existing content onto the
  new filesystem. Before the real mount, the new filesystem is
  temporarily mounted at a staging path and the current content
  is copied onto it with attributes preserved (`cp --archive`).
  The copy is confined to the mountpoint's own filesystem:
  nested mountpoints below it are recreated as empty
  directories, never descended into. Free space on the new
  filesystem is checked before copying. The role does not stop
  any services; quiescing writers below the path (databases,
  applications) is the caller's responsibility.

  The copy never merges: it only targets a filesystem that is
  empty, or that contains nothing but the remains of an
  earlier migration attempt by this role (recognized by an
  in-progress marker the role places before copying and
  removes after completion; such remains are cleared and the
  copy restarts from scratch, so the result is always an
  exact snapshot of the source). A populated mountpoint
  combined with an adopted filesystem that already carries
  other data is an error - existing data is never overlaid.
  An aborted copy leaves the system unchanged: the real mount
  only happens after a completed copy.

  Limit: `copy` is refused when another managed mountpoint
  below this entry's path is not mounted yet and its
  directory is populated. Migrating nested unmounted trees
  in one pass would either duplicate the nested data onto
  the parent filesystem or hide it before the nested
  migration can read it; supporting this is deliberately out
  of scope for a provisioning role. Escape: apply the nested
  entry first (its own migration mounts it), then run again
  for the parent - a mounted nested mountpoint is recreated
  empty and never descended into.
- `hide`: mount anyway. The existing content stays on the
  parent filesystem, hidden below the new mount, and keeps
  occupying its space there.

Falls back to
`disk_linux_device_defaults['mount']['on_nonempty']` (built-in
default `fail`).

- **Type**: `str`
- **Required**: No
- **Choices**: `fail`, `copy`, `hide`

##### `disk_linux_devices['mount']['selinux_relabel']`<a id="variable-disk_linux_devices-sub-mount-sub-selinux_relabel"></a>

[*⇑ Back to ToC ⇑*](#toc)

Controls the one-time SELinux relabel (`restorecon`) of the
mountpoint directly after the initial mount by this role.
Every value names an inherently one-time event - a
filesystem is created once, a first mount happens once - so
no setting ever repeats the relabel on later runs: a
recurring relabel would be an idempotence leak and can
actively harm workloads that maintain their own labels below
the mountpoint (for example rootless container storage under
`/home`). The relabel does not cross filesystem boundaries
(nested mounts stay untouched). No-op on systems without
active SELinux.

- `never`: no relabeling.
- `created` (default): relabel only filesystems the role
  created during this run, covering content migrated by
  `on_nonempty: "copy"`. Adopted, already existing
  filesystems are not relabeled - their data, including the
  security-context attributes, stays untouched.
- `first_mount`: additionally relabel an adopted, existing
  filesystem once, right after the first time this role
  mounts it. Use when adopting disks whose labels are known
  to be wrong for the new mountpoint.

Falls back to
`disk_linux_device_defaults['mount']['selinux_relabel']`
(built-in default `created`).

- **Type**: `str`
- **Required**: No
- **Choices**: `never`, `created`, `first_mount`





<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__disk_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
