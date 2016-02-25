#!/usr/bin/env python3
# Mute and unmute after a timeout, when seeing a notification or both
#
# usage: mute_unmute.py -h
#
# Copyright (C) 2015 Francesco Montesano <franz.bergesund@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import argparse as ap
import contextlib
import signal
import subprocess as sp
import sys
import time


class NoSinkError(Exception):
    """No pulseaudio sink found"""
    pass


class TimeOutError(Exception):
    """Error raised when the time is out"""
    pass


@contextlib.contextmanager
def mute_unmute():
    """Mute and then make sure to unmute, whatever happened

    Raises
    ------
    NoSinkError
        if no running sink is found
    """
    sinks = get_running_sinks()

    if not sinks:
        raise NoSinkError("No running sinks found")

    silenced = [sp.call(['pactl', 'set-sink-mute', s, 'true']) for s in sinks]

    try:
        yield sinks, silenced
    finally:
        for s, silence in zip(sinks, silenced):
            sp.call(['pactl', 'set-sink-mute', s, 'false'])


def get_running_sinks():
    """Call and parse ``pactl list sinks short`` to get the index of running
    sinks.

    Returns
    -------
    sinks_id : list of strings
        ids of the active sinks
    """
    pactl = sp.check_output(['pactl', 'list', 'sinks', 'short'],
                            universal_newlines=True)

    sinks_id = [i.split()[0] for i in pactl.split('\n') if 'RUNNING' in i]
    return sinks_id


@contextlib.contextmanager
def time_out(timeout):
    """Context manager that times out. If ``timeout`` is zero, timeout gets
    disabled

    Raises
    ------
    TimeOutError
        if the timeout is reached
    """
    def _handler(signum, frame):
        raise TimeOutError("{} seconds have passed".format(timeout))

    signal.signal(signal.SIGALRM, _handler)
    signal.alarm(timeout)

    try:
        yield
    finally:
        signal.alarm(0)


def monitor_notification(name):
    """Monitor notifications with ``dbus-monitor --session
    interface='org.freedesktop.Notifications',member='Notify'``
    until the given name appears. When this appears, exit.

    Parameters
    ----------
    name : string
        name of the notification to monitor

    Returns
    -------
    string
        line containing name
    """
    cmd = ("dbus-monitor --session interface='org.freedesktop.Notifications',"
           " member='Notify'".split())
    p = sp.Popen(cmd, stdout=sp.PIPE)
    for line in p.stdout:
        if name in line.decode():
            break
    p.kill()
    return line.decode()


def parser(argv=None):
    description = """Mute the running pulseaudio sinks until a notification
                  containing ``name`` is fired or ``seconds`` time is passed.
                  If no ``name`` is provided and ``seconds`` is zero, the code
                  doesn't run."""
    p = ap.ArgumentParser(description=description,
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)

    p.add_argument('-n', "--name", help="""Name of the notification to monitor;
                   If not provided, unmute after the timout.""")
    p.add_argument('-s', '--seconds', default=30, type=int,
                   help='''Number of seconds before unmuting. Set to 0 to avoid
                   the timeout and force the code to wait for the
                   notification''')

    return p.parse_args(args=argv)


def main(argv=None):
    """Run the code"""
    args = parser(argv=argv)

    if not args.name or not args.seconds:
        print("Please provides at least the name or the seconds")
        sys.exit(1)

    try:
        with time_out(args.seconds), mute_unmute():
            if args.name:
                monitor_notification(args.name)
            else:
                time.sleep(args.seconds)
        print("Notification for {} fired".format(args.name))
    except TimeOutError:
        print("Timeout {} reached before getting the required"
              " notification".format(args.seconds))
    except NoSinkError as e:
        print("Aborting because of: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
