import platform

def get_os_type():
    os_type = platform.system()
    if os_type == "Darwin":
        return "mac"
    elif os_type == "Windows":
        return "windows"
    elif os_type == 'Linux':
        return "linux"