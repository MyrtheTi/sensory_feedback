"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-03-01 16:05:46
 * @desc Save this in boot.py on the microcontroller and reboot to give write
 access to CircuitPython. To change this again to USB write access, change the
 name of boot.py from the REPL:
 import os
 os.listdir("/")
 os.rename("/boot.py", "/booty.py")
"""

import storage

storage.remount("/", False)
