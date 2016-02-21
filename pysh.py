#!/usr/bin/python3

import os
import pwd
import socket

def builtin_chdir(args):
    try:
        if len(args) == 0:
            os.chdir(os.path.expanduser("~"))
        else:
            os.chdir(os.path.expanduser(args[0]))
        return 0
    except FileNotFoundError:
        print("cd: %s: no such file or directory" % args[0])
        return 1
    except NotADirectoryError:
        print("cd: %s: not a directory" % args[0])
        return 1


def builtin_help():
    print("help")
    return 0


def builtin_echo(args):
    print(" ".join(args))
    return 0


def builtin_exit(args):
    exit(0)


builtins = {
    "cd":   builtin_chdir,
    "help": builtin_help,
    "exit": builtin_exit,
    "echo": builtin_echo
}


def spawn(cmd, args):
    pid = os.fork()

    if pid == 0:
        # child
        try:
            os.execvp(cmd, [cmd] + args)
        except FileNotFoundError:
            print("%s: command not found" % cmd)
        exit(1)
    elif pid < 0:
        print("Error forking")
        return 1
    else:
        while True:
            pid,status = os.waitpid(pid, os.WUNTRACED)
            if not os.WIFEXITED(status) or os.WIFSIGNALED(status):
                break
            return 0


def parse_line(line):
    tokens = line.split()
    args = []

    if len(tokens) == 0:
        return 0
    if len(tokens) > 0:
        cmd = tokens[0]
    if len(tokens) > 1:
        args = tokens[1:]

    if cmd[0] == "#":
        return 0
    if cmd in builtins:
        return builtins[cmd](args)
    else:
        return spawn(cmd, args)


status = 0
while True:
    try:
        user     = pwd.getpwuid( os.getuid() )[0]
        hostname = socket.gethostname()
        cwd      = os.getcwd()

        prompt   = "%s@%s:%s$ " % (user, hostname, cwd)
        line = input(prompt)
        status = parse_line(line)
    except EOFError:
        print()
        exit(0)
    except KeyboardInterrupt:
        pass
