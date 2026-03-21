import argparse

from _utils import *

title("Coexist")
print("\n - Create multiple WeChat executables to use different accounts.")


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-n", "--number")
    parser.add_argument("--exe")
    parser.add_argument("--dll")
    parser.add_argument("--no-pause", action="store_true")
    return parser.parse_args()


args = parse_args()

# Number
n = args.number if args.number is not None else input(f"\n{BOLD}Wechat Number{NO_BOLD} (0~9): ")
if len(n) != 1 or not n in "0123456789":
    print(f"{RED}[ERR] Invalid number{RESET}")
    if not args.no_pause:
        pause()
    exit()

# [Weixin.exe]
if args.exe is None and args.no_pause:
    exe_input = ""
elif args.exe is None:
    exe_input = input(f"\n{BOLD}Weixin.exe{NO_BOLD} (leave blank = auto detect): ")
else:
    exe_input = args.exe
exe = exepath(exe_input)
data = load(exe)
# Redirect Weixin.dll -> Weixin.dl2
print(f"\n> Redirecting Weixin.dll -> Weixin.dl{n}")
EXE_PATTERN = "\x00".join("Weixin.dll")
EXE_REPLACE = "\x00".join(f"Weixin.dl{n}")
data = replace(data, EXE_PATTERN, EXE_REPLACE)
# Rename Weixin.exe -> Weixin2.exe
new_exe = exe.with_name(f"Weixin{n}.exe")
save(new_exe, data)

# [Weixin.dll]
if args.dll is None and args.no_pause:
    dll_input = ""
elif args.dll is None:
    dll_input = input(f"\n{BOLD}Weixin.dll{NO_BOLD} (leave blank = auto detect): ")
else:
    dll_input = args.dll
dll = dllpath(dll_input)
data = load(dll)
# Redirect global_config -> global_conf2g
# Just search 'global_config' and you'll find the pattern.
# 48 B8:     67 6C 6F 62 61 6C 5F 63   // MOV RAX, "global_c" (0x5F6C61626F6C676)
# 48 89 05: [07 78 C3 07]              // MOV [RIP+offset], RAX
# C7 05:    [05 78 C3 07] 6F 6E 66 69  // MOV dword [RIP+offset], "onfi" (0x69666E6F)
# 66 C7 05: [00 78 C3 07] 67 00        // MOV word [RIP+offset], "g\0" (0x0067)
# Change "onfi" to "onf{n}" so we have "global_conf{n}g\0"
print(f"\n> Redirecting global_config -> global_conf{n}g")
COEXIST_CONFIG_PATTERN = """
48 B8 67 6C 6F 62 61 6C 5F 63
48 89 05 ?? ?? ?? ??
C7 05 ?? ?? ?? ?? 6F 6E 66 69
66 C7 05 ?? ?? ?? ?? 67 00
"""
COEXIST_CONFIG_REPLACE = f"""
...
C7 05 ?? ?? ?? ?? 6F 6E 66 {ord(n):02X}
66 C7 05 ?? ?? ?? ?? 67 00
"""
data = wildcard_replace(data, COEXIST_CONFIG_PATTERN, COEXIST_CONFIG_REPLACE)
# Redirect host-redirect.xml -> host-redirect.xm2
# This file affects the auto-login feature.
print(f"\n> Redirecting host-redirect.xml -> host-redirect.xm{n}")
AUTOLOGIN_PATTERN = "host-redirect.xml"
AUTOLOGIN_REPLACE = f"host-redirect.xm{n}"
data = replace(data, AUTOLOGIN_PATTERN, AUTOLOGIN_REPLACE)
# Change Mutex Name
print("\n> Renaming instance mutex")
MUTEX_PATTERN = "\0".join("XWeChat_App_Instance_Identity_Mutex_Name")
MUTEX_REPLACE = "\0".join(f"XWeChat_App_Instance_Identity_Mutex_Nam{n}")
data = replace(data, MUTEX_PATTERN, MUTEX_REPLACE)
# Change Window Name
print("\n> Renaming window name")
WINDOW_PATTERN = "\0".join("xWechatWindow")
WINDOW_REPLACE = "\0".join(f"xWechatWindo{n}")
data = replace(data, WINDOW_PATTERN, WINDOW_REPLACE)
# Rename Weixin.dll -> Weixin.dl2
new_dll = dll.with_name(f"Weixin.dl{n}")
save(new_dll, data)
if not args.no_pause:
    pause()
