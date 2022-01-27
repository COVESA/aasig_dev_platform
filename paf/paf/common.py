'''
Created on Dec 28, 2021

@author: vladyslav_goncharuk
'''

import os
import io
import sys
import fcntl
import struct
import termios
import glob
import imp

def has_fileno(stream):
    """
    Cleanly determine whether ``stream`` has a useful ``.fileno()``.
    .. note::
        This function helps determine if a given file-like object can be used
        with various terminal-oriented modules and functions such as `select`,
        `termios`, and `tty`. For most of those, a fileno is all that is
        required; they'll function even if ``stream.isatty()`` is ``False``.
    :param stream: A file-like object.
    :returns:
        ``True`` if ``stream.fileno()`` returns an integer, ``False`` otherwise
        (this includes when ``stream`` lacks a ``fileno`` method).
    .. versionadded:: 1.0
    """
    try:
        return isinstance(stream.fileno(), int)
    except (AttributeError, io.UnsupportedOperation):
        return False

def isatty(stream):
    """
    Cleanly determine whether ``stream`` is a TTY.
    Specifically, first try calling ``stream.isatty()``, and if that fails
    (e.g. due to lacking the method entirely) fallback to `os.isatty`.
    .. note::
        Most of the time, we don't actually care about true TTY-ness, but
        merely whether the stream seems to have a fileno (per `has_fileno`).
        However, in some cases (notably the use of `pty.fork` to present a
        local pseudoterminal) we need to tell if a given stream has a valid
        fileno but *isn't* tied to an actual terminal. Thus, this function.
    :param stream: A file-like object.
    :returns:
        A boolean depending on the result of calling ``.isatty()`` and/or
        `os.isatty`.
    .. versionadded:: 1.0
    """
    # If there *is* an .isatty, ask it.
    if hasattr(stream, "isatty") and callable(stream.isatty):
        return stream.isatty()
    # If there wasn't, see if it has a fileno, and if so, ask os.isatty
    elif has_fileno(stream):
        return os.isatty(stream.fileno())
    # If we got here, none of the above worked, so it's reasonable to assume
    # the darn thing isn't a real TTY.
    return False

def bytes_to_read(input_):
    """
    Query stream ``input_`` to see how many bytes may be readable.
    .. note::
        If we are unable to tell (e.g. if ``input_`` isn't a true file
        descriptor or isn't a valid TTY) we fall back to suggesting reading 1
        byte only.
    :param input: Input stream object (file-like).
    :returns: `int` number of bytes to read.
    .. versionadded:: 1.0
    """
    # NOTE: we have to check both possibilities here; situations exist where
    # it's not a tty but has a fileno, or vice versa; neither is typically
    # going to work re: ioctl().
    if not os.name == 'nt' and isatty(input_) and has_fileno(input_):
        fionread = fcntl.ioctl(input_, termios.FIONREAD, "  ")
        return struct.unpack("h", fionread)[0]
    return 1

def load_module(absolute_path):

    print(f"Attempt to load module - {absolute_path}")

    import importlib.util
    module_name, _ = os.path.splitext(os.path.split(absolute_path)[-1])
    try:
        py_mod = imp.load_source(module_name, absolute_path)
    except ImportError as e:
        if "No module named" not in e.msg:
            raise e

        missing_module = e.name
        module_root = os.path.dirname(absolute_path)

        if missing_module + ".py" not in os.listdir(module_root):
            msg = "Could not find '{}' in '{}'"
            raise ImportError(msg.format(missing_module, module_root))

        print("Could not directly load module, including dir: {}".format(module_root))
        sys.path.append(module_root)
        spec = importlib.util.spec_from_file_location(module_name, absolute_path)
        py_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(py_mod)
    return module_name, py_mod

def load_all_modules_in_dir(module_root_dir):

    if not os.path.isdir(module_root_dir):
        raise Exception(f"Provided path '{module_root_dir}' is not a directory!")

    found_python_files = glob.glob(f"{module_root_dir}/*.py")

    result = {}

    for found_python_file in found_python_files:
        if os.path.isfile(found_python_file) and not found_python_file.endswith('__init__.py'):
            loaded_module_name, loaded_module = load_module(found_python_file)

            if loaded_module:
                result[loaded_module_name] = loaded_module

    return result

def load_all_modules_in_dirs(module_paths):
    result = {}
    for module_path in module_paths:
        result.update(load_all_modules_in_dir(module_path))
    return result

def create_class_instance(full_class_name, loaded_modules):
    _, module_name, class_name = full_class_name.rsplit('.', 2)
    module = loaded_modules.get(module_name)

    result = None

    if module:
        result = getattr(module, class_name)
    else:
        raise Exception(f"Module '{module_name}' is not loaded.")

    return result

def get_terminal_dimensions():
    if isatty(sys.stdout):
        s = struct.pack('HHHH', 0, 0, 0, 0)
        t = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
        winsize = struct.unpack('hhhh', t)
        return winsize[1], winsize[0]
    else:
        return None, None

def exec_command(
        paramiko_ssh_client,
        command,
        bufsize=-1,
        timeout=None,
        environment=None,
        terminal_width = 80,
        terminal_height = 24
    ):
    chan = paramiko_ssh_client._transport.open_session(timeout=timeout)
    if isatty(sys.stdout):
        chan.get_pty(width=terminal_width, height=terminal_height)
    chan.settimeout(timeout)
    if environment:
        chan.update_environment(environment)
    chan.exec_command(command)
    stdin = chan.makefile_stdin("wb", bufsize)
    stdout = chan.makefile("r", bufsize)
    stderr = chan.makefile_stderr("r", bufsize)
    return stdin, stdout, stderr