#!/usr/bin/env python3

import argparse
import configparser
import os
import sys
import curses

try:
    import dns.resolver
    has_dns = True
except ImportError:
    has_dns = False


# Just for fun!
slonik = r"""   ____  ______  ___
  /    )/      \/   \
 (     / __    _\    )
  \    (/ o)  ( o)   )
   \_  (_  )   \ ) _/
     \  /\_/    \)/
      \/ <//|  |\\>
            |  |
            |_/      """.splitlines()


def prompt_service(services, title='Select service to connect to'):
    selected = 0

    screen = curses.initscr()
    rows, cols = screen.getmaxyx()
    try:
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        screen.keypad(1)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        highlightText = curses.color_pair(1)
        slonikText = curses.color_pair(2)
        normalText = curses.A_NORMAL
        screen.border(0)
        curses.curs_set(0)

        if rows > 4 + len(services) + len(slonik):
            for i, l in enumerate(slonik):
                screen.addstr(i+2, (cols - 22) // 2, l, slonikText)
            firstrow = 4 + len(slonik)
        else:
            firstrow = 2

        box = curses.newwin(
            len(services) + 2,
            80,
            max(firstrow, (rows - len(services) - 2) // 2),
            (cols - 80) // 2
        )
        box.box()
        box.addstr(0, (80 - len(title) - 2) // 2, ' {} '.format(title))

        while True:
            for i, s in enumerate(services):
                box.addstr(i+1, 2, s,
                           highlightText if selected == i else normalText)
            screen.refresh()
            box.refresh()

            ch = screen.getch()
            if ch == 27:
                break
            elif ch == curses.KEY_UP:
                if selected == 0:
                    selected = len(services) - 1
                else:
                    selected -= 1
            elif ch == curses.KEY_DOWN:
                if selected == len(services) - 1:
                    selected = 0
                else:
                    selected += 1
            elif ch == ord("\n"):
                return services[selected]
    finally:
        curses.endwin()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect to a psql service')
    parser.add_argument('servicefile', type=str, nargs='?',
                        help='Name of pg_service.conf file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    if args.servicefile:
        if not os.path.isfile(args.servicefile):
            print("{} does not exist.".format(args.servicefile))
            sys.exit(1)

        servicefile = args.servicefile
    else:
        # Current directory?
        if os.path.isfile("pg_service.conf"):
            servicefile = 'pg_service.conf'
        elif os.path.isfile(os.path.expanduser("~/.pg_service.conf")):
            servicefile = os.path.expanduser("~/.pg_service.conf")
        elif os.path.isfile("/etc/pg_service.conf"):
            servicefile = "/etc/pg_service.conf"
        else:
            print("No pg_service.conf file found.")
            sys.exit(1)

    if args.verbose:
        print("Using service file {}".format(servicefile))

    cfg = configparser.ConfigParser()
    cfg.read(servicefile)

    services = cfg.sections()

    if not services:
        print("No services defined.")
        sys.exit(1)

    def _connect(servicename):
        parg = "service={}".format(servicename)
        if cfg.has_option(servicename, 'hostaddr') and \
           cfg.get(servicename, 'hostaddr').startswith('!'):
            # ! in the hostaddr means do a targeted DNS lookup instead
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [cfg.get(servicename, 'hostaddr')[1:], ]
            answers = resolver.query(cfg.get(servicename, 'host'))
            # We always use the first answer, even if we get more than one
            parg += " hostaddr='{}'".format(answers[0])

        if args.verbose:
            print("Executing: psql {}".format(parg))

        os.environ['PGSERVICEFILE'] = os.path.abspath(servicefile)
        os.execvp("psql", ["psql", parg, ])


    if len(services) == 1:
        _connect(services[0])
    else:
        # Prompt for service
        service = prompt_service(services)
        if service:
            _connect(service)
