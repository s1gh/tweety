import fnmatch
import os
import datetime
import discord
import random
import json
import logging
import subprocess
import sys

log = logging.getLogger(__name__)

class Embed(discord.Embed):
    def __init__(self, **kvargs):
        super().__init__(**kvargs, color=random.randint(0x000000, 0xffffff))  # Create an embed with a random color

class LinesOfCode:
    def walk(self, root='.', recurse=True, pattern='*'):
        for path, subdirs, files in os.walk(root):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
            if not recurse:
                break

    def loc(self, root, recurse=True):
        count_mini, count_maxi = 0, 0
        for fspec in self.walk(root, recurse, '*.py'):
            skip = False
            for line in open(fspec, encoding="utf-8").readlines():
                count_maxi += 1

                line = line.strip()
                if line:
                    if line.startswith('#'):
                        continue
                    if line.startswith('"""'):
                        skip = not skip
                        continue
                    if not skip:
                        count_mini += 1
        return count_maxi

class Uptime:
    def __init__(self, start : datetime):
        self.s = int((datetime.datetime.utcnow() - start).total_seconds())

    def uptime(self):
        m, s = divmod(self.s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        return '{:2d} days, {:0d} hours, {:2d} minutes and {:2d} seconds'.format(d, h, m, s)

class Birthday:
    def __init__(self, created_at : datetime):
        self.birthday = created_at.strftime('%B {S}').replace('{S}', str(created_at.day) + self.__suffix(created_at.day))

    def get_birthday(self):
        return self.birthday

    def __suffix(self, d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

def git_repair():
    process = subprocess.Popen(['git', 'reset', '--hard'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutput, stderroutput = process.communicate()

    if process.returncode == 0:
        log.warning('Tweety has been repaired successfully. All files are now reset to the last commit.')
    else:
        log.critical('Repair procedure failed.')
        sys.exit(-1)

def splash_screen():
    print(" _________________________________________")
    print("< I wonder what that puddy tat up to now? >")
    print(" -----------------------------------------")
    print("    \\")
    print("     \\")
    print("      \\")
    print("                    ___")
    print("                _.-'   ```'--.._")
    print("              .'                `-._")
    print("             /                      `.")
    print("            /                         `.")
    print("           /                            `.")
    print("          :       (                       \\")
    print("          |    (   \_                  )   `.")
    print("          |     \__/ '.               /  )  ;")
    print("          |   (___:    \            _/__/   ;")
    print("          :       | _  ;          .'   |__) :")
    print("           :      |` \ |         /     /   /")
    print("            \     |_  ;|        /`\   /   /")
    print("             \    ; ) :|       ;_  ; /   /")
    print("              \_  .-''-.       | ) :/   /")
    print("             .-         `      .--.'   /")
    print("            :         _.----._     `  <")
    print("            :       -'........'-       `.")
    print("             `.        `''''`           ;")
    print("               `'-.__                  ,'")
    print("                     ``--.   :'-------'")
    print("                         :   :")
    print("                        .'   '.")
    print("---------------------------------------------------------------")
    print("_______        _______ _____ _______   __ __     _______  ___  ")
    print("|_   _\ \      / / ____| ____|_   _\ \ / / \ \   / /___ / / _ \\")
    print("  | |  \ \ /\ / /|  _| |  _|   | |  \ V /   \ \ / /  |_ \| | | |")
    print("  | |   \ V  V / | |___| |___  | |   | |     \ V /  ___) | |_| |")
    print("  |_|    \_/\_/  |_____|_____| |_|   |_|      \_/  |____(_)___/ ")
    print("\n---------------------------------------------------------------")
