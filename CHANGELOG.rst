===============================================
foundata.linux Ansible collection Release Notes
===============================================

.. contents:: Topics

v1.3.0
======

Release Summary
---------------

Release Date: 2026-08-13

Feature and bugfix release.

Minor Changes
-------------

- disk role - added the new ``foundata.linux.disk`` role for managing dedicated data disks: a single partition spanning the disk, an XFS or ext4 filesystem and a mount plus ``/etc/fstab`` entry by filesystem UUID. Existing data is never reformatted or destroyed by default (declared layout verification, explicit ``on_mismatch``/``on_nonempty``/``wipe`` policies), with optional one-time content migration for populated mountpoints and online growth after disk enlargement.

Bugfixes
--------

- ``sysctl`` - Kernel modules required by profiles are now registered for boot in the fixed, role-owned ``/etc/modules-load.d/zz-managed.conf`` file. The module registration no longer follows ``sysctl_linux_config_dropin_file_name``, so changing the configurable sysctl drop-in filename cannot leave an old module-registration file active. Dropping the profile or using ``sysctl_linux_state: "absent"`` removes the registration; already loaded modules are not unloaded.
- auto_update: the reboot helper did not consult `zypper needs-rebooting`, so openSUSE hosts missed reboots that only zypper reports. Exit code 102 now schedules the reboot; any other non-zero exit is an error and never reboots.
- reboot, auto_update: on hosts with zypper, `zypper needs-rebooting` is now checked before (and instead of) `needs-restarting`. SUSE ships `needs-restarting` as a wrapper that collapses every non-zero zypper exit - the reboot hint and real errors alike - into exit code 1, which turned zypper errors into scheduled or reported reboots.
- reboot, auto_update: the reboot detection matched the running kernel release as a SUBSTRING of the newest installed `vmlinuz-*` filename, so an installed `6.1.0-30` was accepted as the running `6.1.0-3` and the required reboot was missed. Both implementations now strip the filename prefix and compare the releases exactly, ignoring rescue kernels and backup or boot-loader artifacts.

Known Issues
------------

- ``sysctl`` - Older collection versions persisted profile modules through
  one file per module, normally
  ``/etc/modules-load.d/br_netfilter.conf`` and
  ``/etc/modules-load.d/nf_conntrack.conf``. Those files have no ownership
  marker and may also have been created by an administrator or other
  software. The role therefore does not remove them automatically.

  Hosts that previously used the ``container`` or ``router`` profiles can
  inspect possible legacy registrations:

  .. code-block:: shell

     grep -RnsE '^[[:space:]]*(br_netfilter|nf_conntrack)([[:space:]]|$)' \
       /etc/modules-load.d /run/modules-load.d /usr/lib/modules-load.d 2>/dev/null

     stat /etc/modules-load.d/br_netfilter.conf \
       /etc/modules-load.d/nf_conntrack.conf 2>/dev/null

  A file named after the module and containing only that module name is
  consistent with the former role output, but is not proof of ownership.
  Check configuration-management history and whether another service still
  requires the module at boot.

  When ownership or continued use is uncertain, leave the files in place.
  Loading these modules unnecessarily normally causes only modest resource
  and attack-surface overhead, whereas removing a registration still needed
  by networking, firewall or container workloads can cause failures after
  the next reboot.

  Files confirmed to be obsolete can be removed manually:

  .. code-block:: shell

     sudo rm -f -- /etc/modules-load.d/br_netfilter.conf \
       /etc/modules-load.d/nf_conntrack.conf

  Removing these files affects future boots only. Do not unload the running
  modules solely as part of this cleanup because active workloads may depend
  on them.

v1.2.0
======

Release Summary
---------------

Release Date: 2026-08-08

Feature and bugfix release.

Minor Changes
-------------

- sysctl: new `container-rootless` profile with the per-UID inotify and kernel keyring quotas for hosts running only rootless containers with user-mode networking (Podman with pasta or slirp4netns). Such hosts never bridge or NAT container traffic, so the forwarding/bridge/conntrack keys and kernel modules of the `container` profile are unnecessary there; the `container` profile documentation now states its rootful/bridged scope.
- sysctl: new option `sysctl_linux_modules_required` (default `false`) to fail the run instead when a profile kernel module cannot be loaded (detected containers are still tolerated).

Bugfixes
--------

- ``sysctl`` - the drop-in precedence fix of an earlier release was not effective for default configurations: the documentation said ``zz-managed.conf`` but ``defaults/main.yml`` still carried ``90-managed.conf``, so distribution files like ``99-protect-links.conf`` could still override managed keys (and a ``zz-managed.conf`` from a previous run was even removed as a leftover). The default value now matches the documentation.
- ``user`` - accounts with more than one managed SSH key got their ``authorized_keys`` entries joined with a literal ``\n`` text instead of real newlines (a Jinja escape-handling pitfall), garbling the keys into a single line.
- boolean role arguments are now coerced with ``ansible.builtin.bool`` in every conditional. String values, as delivered by ``-e var=false`` command line extra-vars, were evaluated by truthiness before, so ``"false"`` enabled the gated behavior instead of disabling it.
- sysctl: kernel modules required by a profile are now loaded best effort on every platform, as documented. Previously a load failure was fatal outside of containers, which broke the `container` profile on Enterprise Linux 10 cloud images (their running kernel cannot load `br_netfilter`: the module ships in `kernel-modules-extra`, which GenericCloud images do not install). Parameters gated by an unloadable module are now skipped with a notice on any platform, keeping the rendered configuration valid.

v1.1.0
======

Release Summary
---------------

Release Date: 2026-07-30

Maintenance and bugfix release.

Minor Changes
-------------

- The Molecule ``default`` scenario now runs all platforms as QEMU/KVM virtual machines (per-platform ``type: libvirt`` backend selection via a session libvirt daemon, without root privileges): the collection manages kernel and system level state, so applied values are now verified against a real kernel on every platform instead of being skipped in containers. Commented container alternates remain in ``molecule.yml``. See ``extensions/molecule/README.md`` for requirements and usage.
- ``auto_update`` role - ``auto_update_linux_timer_settings`` and ``auto_update_linux_reboot_timer_settings`` now accept a YAML list for the repeatable systemd trigger directives (``OnCalendar``, ``OnActiveSec``, ``OnBootSec``, ``OnStartupSec``, ``OnUnitActiveSec``, ``OnUnitInactiveSec``), rendering one assignment per entry so several expressions of the same directive can be combined. An empty list drops the role's built-in default for that directive (e.g. to run a purely monotonic timer without a calendar schedule); at least one trigger must remain. The monotonic trigger directives also accept plain numbers (seconds). The boolean event trigger directives ``OnClockChange`` and ``OnTimezoneChange`` are supported and count as a trigger when ``true``, so an event-only timer is a valid configuration. Unsupported values - mappings, booleans, ``null`` or empty strings for repeatable trigger directives, non-booleans for the event trigger directives, unusable list entries, and lists for non-repeatable directives - are now rejected with an explanatory message instead of being silently rendered into an invalid unit.
- sysctl role - added a new ``container`` profile for OCI container hosts (Docker, Podman including rootless, containerd/CRI-O). See ``roles/sysctl/vars/profiles/container.md`` for the reasoning behind every value (https://github.com/foundata/ansible-collection-linux/issues/6).

Security Fixes
--------------

- ``sysctl`` role - ``sysctl_linux_config_dropin_file_name`` is now validated to be a plain filename ending in ``.conf``. A value containing path separators (such as ``../sysctl.conf``) could previously make the role write to or remove files outside of ``/etc/sysctl.d/`` with root privileges, and any suffix other than ``.conf`` is silently ignored by ``sysctl(8)``.
- ``user`` - Malformed ``user_linux_uid_min`` or ``user_linux_uid_max`` values (for example ``"1o00"``) were silently converted to ``0``, which could widen the UID range used by ``user_linux_accounts_delete_unmanaged`` and make system accounts candidates for deletion. The role now fails fast when these variables are neither empty nor a non-negative integer, and additionally fails when the effective ``UID_MIN`` is greater than the effective ``UID_MAX``.
- ``user`` role - ``user_linux_accounts[].password.hash`` is now marked ``no_log`` in the argument specification, so a failing argument validation can no longer expose the password hash.
- sudo role - a renamed rule, or a user/group removed from a rule, no longer leaves an orphaned drop-in behind that keeps granting sudo. The role now cleans up its own ``99_managed_*`` namespace authoritatively on every run, independent of ``sudo_linux_delete_unmanaged`` (which still governs foreign files only).
- user role - an empty (but defined) ``password.hash`` no longer creates a passwordless account. ``ansible.builtin.default(omit)`` only omits an *undefined* value, so an empty hash (for example from a vault lookup that returned nothing) was passed to the ``user`` module as ``password: ""``, which writes an empty crypt field and allows password-less login. The parameter is now omitted for an empty hash, leaving the account's password unmanaged.

Bugfixes
--------

- All roles - Platform-specific task files are now guaranteed to run before the shared default tasks. The former single include loop did not preserve that order with several platforms in one play: Ansible batches the includes across hosts and the insertion order depends on when results arrive (non-deterministic), so default tasks could run before platform-specific ones. The includes are now two sequential tasks, which is a hard ordering barrier.
- The comment written into neutralized distribution config files contained a stray double quote in the Debian hint (``dpkg -S '<file>'"``), so the suggested command could not be copied and pasted as-is. The quote is removed.
- ``auto_update`` role - The documentation of the ``unmanaged`` service state falsely claimed the service "will not start at boot". The role leaves the service completely alone in this state: both the running state and the boot (enablement) state stay exactly as they are. The description now documents the real behavior.
- ``reboot`` and ``sysctl`` roles - The same notice named the wrong role (``foundata.linux.run``, which does not exist) when explaining which role cleared the file. It now names the actual role.
- ``sysctl`` role - Managed values now actually take precedence over distribution ``sysctl.d`` files. ``sysctl --system`` and ``systemd-sysctl`` apply files sorted by name, and distributions ship files up to the ``99-`` prefix (e.g. ``99-protect-links.conf`` on Debian 12 and Ubuntu 22.04/24.04 setting ``fs.protected_fifos = 1``), which silently overrode managed keys from the role's former ``90-managed.conf`` drop-in on every reload and boot and made runs permanently non-idempotent with the ``hardening-default`` profile. The default drop-in is now ``/etc/sysctl.d/zz-managed.conf`` (sorts after every distribution file); a leftover ``90-managed.conf`` from earlier role versions is removed automatically. When using a custom ``sysctl_linux_config_dropin_file_name``, choose a name sorting after your distribution's files (see the updated documentation).
- ``user`` - Corrected the documentation of ``ssh_authorized_keys_delete_unmanaged``, which claimed that ``true`` was the default. The built-in default is ``false``, so keys that are present on an account but not listed in ``ssh_authorized_keys`` are kept unless the option is enabled explicitly. The previous wording suggested that unlisted keys were removed out of the box. Only the documentation was wrong, the behaviour is unchanged.
- auto_update role - ``auto_update_linux_state: absent`` no longer fails with an undefined-variable error on non-Debian platforms. The uninstall step looped over the Debian-only ``__auto_update_linux_apt_*_file_path`` variables, so the task aborted on RHEL, Fedora and openSUSE. The apt cleanup moved to a Debian-specific uninstall task file.
- auto_update role - ``service_state: disabled`` now actually stops automatic upgrades on Debian and Ubuntu. The ``APT::Periodic::Unattended-Upgrade`` flag was hard-coded to ``1``, so the apt-daily(-upgrade) timers kept running unattended-upgrades regardless of the role-managed timer; it now follows the service state.
- auto_update role - ``service_state: unmanaged`` now removes the role's systemd timer drop-in and its Debian periodic flag file instead of leaving them in place. The role fully backs off so the vendor timer schedule and the distribution defaults take over.
- auto_update role - the scheduled-reboot helper no longer reboots on a transient ``needs-restarting`` error. It treated any non-zero exit as "reboot required", so an error (e.g. a dnf/rpm failure) could schedule a production reboot. Only the documented exit code 1 now triggers one.
- auto_update role - the scheduled-reboot timer now follows ``auto_update_linux_service_state``. It was always enabled and started whenever ``auto_update_linux_reboot`` was ``scheduled``, so a host with ``service_state: disabled`` still had a running reboot timer; it is now stopped/disabled accordingly and left untouched when ``unmanaged``.
- auto_update role - the systemd timer drop-in now replaces the vendor timer's schedule instead of adding to it. ``OnCalendar`` is a list-typed systemd directive, so the drop-in's schedule accumulated on top of the vendor unit (for example ``apt-daily-upgrade.timer`` and ``dnf-automatic.timer`` at ``*-*-* 6:00``), and updates kept running on the vendor schedule regardless of ``auto_update_linux_timer_settings``. The drop-in now emits exactly one empty reset line before the configured trigger directives. All trigger directives (``OnCalendar``, ``OnActiveSec``, ``OnBootSec``, ...) share a single trigger list, so one reset per directive would make each reset wipe the triggers rendered before it and only the last configured trigger would survive.
- auto_update role - the unattended-upgrades origins on Ubuntu now apply. They were written in the ``origin:archive`` shorthand (Allowed-Origins syntax), but the role places them in ``Origins-Pattern``, where unattended-upgrades parses ``key=value`` tokens and raised "not enough values to unpack" on the colon form. They now use ``origin=${distro_id},archive=${distro_codename}-security``.
- auto_update role - the unattended-upgrades security origin on Debian now matches. The pattern used ``codename=${distro_codename}``, but the security archive's Release carries ``Codename: <codename>-security`` (e.g. ``trixie-security``), so it never matched and security updates worked only via the distribution's own default file. The pattern now uses ``codename=${distro_codename}-security``.
- reboot role - reboot detection no longer treats a transient ``needs-restarting`` failure as "reboot required". The check counted any non-zero exit as needing a reboot, so an error (for example a dnf/rpm failure) could reboot the host. Only the documented exit code 1 now counts.
- reboot role - reboot detection now runs under ``--check``. The detection command lacked ``check_mode: false``, so in check mode it was skipped and the role always concluded that no reboot was required.
- reboot role - reboot detection now works on openSUSE. The detection script had no zypper path, so on openSUSE Leap only a changed kernel was noticed; it now honours ``zypper needs-rebooting`` (exit code 102).
- reboot role - stopped installing ``needrestart`` on Debian and Ubuntu. The role never invoked it and it does not create ``/var/run/reboot-required``, so it was an unused dependency.
- reboot role - the SELinux mode check no longer depends on the ``en_US.UTF-8`` locale being present. It forces ``LC_ALL=C`` (like the auto_update role) so ``sestatus`` output parses on minimal hosts.
- reboot role - the ``reboot_linux_result`` fact now carries the correct types when the reboot is skipped (no reboot required, or a container). The ``elapsed`` and ``rebooted`` defaults were swapped, yielding ``{elapsed: false, rebooted: 0}``; ``rebooted`` is now a boolean and ``elapsed`` a number, so downstream ``when: reboot_linux_result['rebooted']`` conditionals behave correctly.
- reboot role - the container-detection fallback that inspects the ``container`` environment variable now gathers the ``env`` fact it relies on; previously that fact was never collected, leaving the fallback inert.
- sudo role - ``sudo_linux_rule_defaults`` can now supply ``commands``, ``users`` or ``groups`` as documented. The rule validation checked the raw rule entry while the drop-in builder used the rule merged with the defaults, so a required key provided only via the defaults raised a false "Invalid sudo_linux_rules entry" error. Validation and the absent-file list now both use the merged rule.
- sudo role - grantee names that are not filename-safe no longer break the grant. A user or group containing a dot (common with SSSD/AD, e.g. ``john.doe``) produced a drop-in whose name sudo silently ignores per sudoers(5), so the rule never applied. The name is now sanitized in the drop-in filename and disambiguated with a short hash of the original name; the real grantee name is unchanged in the rule itself.
- sudo role - removed the ``sudo_linux_service`` tag from the role documentation. The role has no service phase, so the tag matched no tasks.
- sysctl role - a hand-indented line in the managed drop-in no longer breaks idempotence. Parsed keys were not trimmed, so an indented key ("  net.x = 1") was misdetected as an orphan and the removal (which strips the name) deleted the managed parameter, making it flip-flop between runs. Keys are now trimmed.
- sysctl role - the "IPv6 unavailable, skipping net.ipv6.*" notice now lists the parameters that are actually skipped. It used ``rejectattr`` instead of ``selectattr``, so it printed the parameters being kept and labelled them as skipped. The notice is informational only; parameter filtering was already correct (so the bug had no operational impact).
- sysctl role - the role again removes parameters that linger in its managed drop-in but are no longer managed (for example after a key is dropped from a profile or from ``sysctl_linux_parameters``). The existing-parameter parser split the file with ``split('\n')`` inside a Jinja block scalar, where ``\n`` is two literal characters rather than a newline, so the parse always returned an empty list and orphan detection never fired. It now uses ``splitlines()``.
- user role - ``user_linux_accounts_delete_unmanaged`` no longer risks deleting and locking out the account used to connect. The connection user was derived from ``ansible_facts['user_id']``, which is the effective user and therefore ``root`` when the role runs with ``become``, so the real login user fell inside the reap candidates and could be removed with ``remove: true, force: true``. The connection user is now determined at runtime and always excluded from reaping.
- user role - an account entry with an explicit empty ``groups: []`` no longer removes the account from all of its supplementary groups. ``append`` was omitted for an empty list, so the ``user`` module fell back to ``append: false`` and treated the empty list as authoritative, stripping memberships such as ``sudo`` or ``wheel`` despite the default ``groups_append: true``. ``append`` is now sent whenever ``groups`` is defined, making an empty list a no-op unless ``groups_append: false`` is set.
- user role - reaping unmanaged accounts with ``user_linux_accounts_delete_unmanaged`` now only considers local accounts. The candidate list came from ``getent passwd`` (the full NSS view), so on SSSD/LDAP-backed hosts directory users whose UIDs fell inside the reap range became deletion candidates and ``userdel`` would fail or half-run against them. The lookup is restricted to ``/etc/passwd`` via ``service: "files"``.

v1.0.0
======

Release Summary
---------------

Release Date: 2026-06-07

First public release, providing all functionality and files.
