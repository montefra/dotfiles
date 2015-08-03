Systemd scripts
===============

Tivoli backup system
--------------------

To use the tivoli backup system as a systemd service, copy or symlink
``tsm-client.service`` into ``/etc/systemd/system`` and start it with

    systemctl start tsm-client.service

To start the service at every boot issue afterwards the command

    systemctl enable tsm-client.service

Save logs before suspending
---------------------------

Before suspending the computer, the script ``save_xlog_journal`` saves into
``~/debug_x`` directory the previous three minutes of the journal, the last 30
lines of the ``/var/log/Xorg.0.log`` and of ``~/.xsession-errors`` and the
output of ``xrand --verbose``.

To use it copy or symlink the ``save_xlog_journal`` script into the
``/lib/systemd/system-sleep`` directory and create the directory ``~/debug_x``.
If the directory does not exist, the script is not run, so it can be disabled
without the need of sudo.

Note: the script assumes a single user.
