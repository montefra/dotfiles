#!/usr/bin/env python3

import argparse as ap
import contextlib
import signal
import subprocess as sp


@contextlib.contextmanager
def mute_unmute():
    """Mute and then make sure to unmute, whatever happened"""
    sinks = get_running_sinks()

    silenced = [sp.call(['pactl', 'set-sink-mute', s, 'true']) for s in sinks]

    try:
        yield sinks, silenced
    finally:
        for s, silence in zip(sinks, silenced):
            sp.call(['pactl', 'set-sink-mute', s, 'false'])


def get_running_sinks():
    """call and parse ``pactl list sinks short`` to get the index of running
    sinks

    Returns
    -------
    sinks_id : list of int
        ids of the active sinks
    """
    pactl = sp.check_output(['pactl', 'list', 'sinks', 'short'],
                            universal_newlines=True)

    sinks_id = [i.split()[0] for i in pactl.split('\n') if 'RUNNING' in i]
    return sinks_id


class TimeOutError(Exception):
    pass


@contextlib.contextmanager
def time_out(timeout):
    """Context manager that times out"""
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
    p = ap.ArgumentParser(formatter_class=ap.ArgumentDefaultsHelpFormatter)

    p.add_argument("name", help="""Name of the notification to monitor""")
    p.add_argument('-s', '--seconds', default=30, type=int,
                   help='number of seconds before unmuting')

    return p.parse_args(args=argv)


def main(argv=None):
    args = parser(argv=argv)

    try:
        with time_out(args.seconds), mute_unmute():
            monitor_notification(args.name)
        print("Notification for {} fired".format(args.name))
    except TimeOutError:
        print("Timeout {} reached before getting the required"
              " notification".format(args.seconds))


if __name__ == "__main__":
    main()
