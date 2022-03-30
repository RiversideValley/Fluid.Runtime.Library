import contextlib
import itertools
import os
import re
import subprocess
import sys
import sysconfig
import tempfile
import textwrap
import unittest
from pathlib import Path
from test import support

if sys.platform != "win32":
    raise unittest.SkipTest("test only applies to Windows")

# Get winreg after the platform check
import winreg


PY_EXE = "py.exe"
if sys.executable.casefold().endswith("_d.exe".casefold()):
    PY_EXE = "py_d.exe"

# Registry data to create. On removal, everything beneath top-level names will
# be deleted.
TEST_DATA = {
    "PythonTestSuite": {
        "DisplayName": "Python Test Suite",
        "SupportUrl": "https://www.python.org/",
        "3.100": {
            "DisplayName": "X.Y version",
            "InstallPath": {
                None: sys.prefix,
                "ExecutablePath": "X.Y.exe",
            }
        },
        "3.100-32": {
            "DisplayName": "X.Y-32 version",
            "InstallPath": {
                None: sys.prefix,
                "ExecutablePath": "X.Y-32.exe",
            }
        },
        "3.100-arm64": {
            "DisplayName": "X.Y-arm64 version",
            "InstallPath": {
                None: sys.prefix,
                "ExecutablePath": "X.Y-arm64.exe",
                "ExecutableArguments": "-X fake_arg_for_test",
            }
        },
        "ignored": {
            "DisplayName": "Ignored because no ExecutablePath",
            "InstallPath": {
                None: sys.prefix,
            }
        },
    }
}

TEST_PY_COMMANDS = textwrap.dedent("""
    [defaults]
    py_python=PythonTestSuite/3.100
    py_python2=PythonTestSuite/3.100-32
    py_python3=PythonTestSuite/3.100-arm64
""")


def create_registry_data(root, data):
    def _create_registry_data(root, key, value):
        if isinstance(value, dict):
            # For a dict, we recursively create keys
            with winreg.CreateKeyEx(root, key) as hkey:
                for k, v in value.items():
                    _create_registry_data(hkey, k, v)
        elif isinstance(value, str):
            # For strings, we set values. 'key' may be None in this case
            winreg.SetValueEx(root, key, None, winreg.REG_SZ, value)
        else:
            raise TypeError("don't know how to create data for '{}'".format(value))

    for k, v in data.items():
        _create_registry_data(root, k, v)


def enum_keys(root):
    for i in itertools.count():
        try:
            yield winreg.EnumKey(root, i)
        except OSError as ex:
            if ex.winerror == 259:
                break
            raise


def delete_registry_data(root, keys):
    ACCESS = winreg.KEY_WRITE | winreg.KEY_ENUMERATE_SUB_KEYS
    for key in list(keys):
        with winreg.OpenKey(root, key, access=ACCESS) as hkey:
            delete_registry_data(hkey, enum_keys(hkey))
        winreg.DeleteKey(root, key)


def is_installed(tag):
    key = rf"Software\Python\PythonCore\{tag}\InstallPath"
    for root, flag in [
        (winreg.HKEY_CURRENT_USER, 0),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
    ]:
        try:
            winreg.CloseKey(winreg.OpenKey(root, key, access=winreg.KEY_READ | flag))
            return True
        except OSError:
            pass
    return False


class PreservePyIni:
    def __init__(self, path, content):
        self.path = Path(path)
        self.content = content
        self._preserved = None

    def __enter__(self):
        try:
            self._preserved = self.path.read_bytes()
        except FileNotFoundError:
            self._preserved = None
        self.path.write_text(self.content, encoding="utf-16")

    def __exit__(self, *exc_info):
        if self._preserved is None:
            self.path.unlink()
        else:
            self.path.write_bytes(self._preserved)


class RunPyMixin:
    py_exe = None

    @classmethod
    def find_py(cls):
        py_exe = None
        if sysconfig.is_python_build(True):
            py_exe = Path(sys.executable).parent / PY_EXE
        else:
            for p in os.getenv("PATH").split(";"):
                if p:
                    py_exe = Path(p) / PY_EXE
                    if py_exe.is_file():
                        break
            else:
                py_exe = None

        # Test launch and check version, to exclude installs of older
        # releases when running outside of a source tree
        if py_exe:
            try:
                with subprocess.Popen(
                    [py_exe, "-h"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="ascii",
                    errors="ignore",
                ) as p:
                    p.stdin.close()
                    version = next(p.stdout).splitlines()[0].rpartition(" ")[2]
                    p.stdout.read()
                    p.wait(10)
                if not sys.version.startswith(version):
                    py_exe = None
            except OSError:
                py_exe = None

        if not py_exe:
            raise unittest.SkipTest(
                "cannot locate '{}' for test".format(PY_EXE)
            )
        return py_exe

    def run_py(self, args, env=None, allow_fail=False, expect_returncode=0):
        if not self.py_exe:
            self.py_exe = self.find_py()

        env = {**os.environ, **(env or {}), "PYLAUNCHER_DEBUG": "1", "PYLAUNCHER_DRYRUN": "1"}
        env.pop("VIRTUAL_ENV", None)
        with subprocess.Popen(
            [self.py_exe, *args],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as p:
            p.stdin.close()
            p.wait(10)
            out = p.stdout.read().decode("utf-8", "replace")
            err = p.stderr.read().decode("ascii", "replace")
        if p.returncode != expect_returncode and support.verbose and not allow_fail:
            print("++ COMMAND ++")
            print([self.py_exe, *args])
            print("++ STDOUT ++")
            print(out)
            print("++ STDERR ++")
            print(err)
        if allow_fail and p.returncode != expect_returncode:
            raise subprocess.CalledProcessError(p.returncode, [self.py_exe, *args], out, err)
        else:
            self.assertEqual(expect_returncode, p.returncode)
        data = {
            s.partition(":")[0]: s.partition(":")[2].lstrip()
            for s in err.splitlines()
            if not s.startswith("#") and ":" in s
        }
        data["stdout"] = out
        data["stderr"] = err
        return data

    def py_ini(self, content):
        if not self.py_exe:
            self.py_exe = self.find_py()
        return PreservePyIni(self.py_exe.with_name("py.ini"), content)

    @contextlib.contextmanager
    def script(self, content, encoding="utf-8"):
        file = Path(tempfile.mktemp(dir=os.getcwd()) + ".py")
        file.write_text(content, encoding=encoding)
        try:
            yield file
        finally:
            file.unlink()


class TestLauncher(unittest.TestCase, RunPyMixin):
    @classmethod
    def setUpClass(cls):
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Python") as key:
            create_registry_data(key, TEST_DATA)

        if support.verbose:
            p = subprocess.check_output("reg query HKCU\\Software\\Python /s")
            #print(p.decode('mbcs'))


    @classmethod
    def tearDownClass(cls):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"Software\Python", access=winreg.KEY_WRITE | winreg.KEY_ENUMERATE_SUB_KEYS) as key:
            delete_registry_data(key, TEST_DATA)


    def test_version(self):
        data = self.run_py(["-0"])
        self.assertEqual(self.py_exe, Path(data["argv0"]))
        self.assertEqual(sys.version.partition(" ")[0], data["version"])

    def test_help_option(self):
        data = self.run_py(["-h"])
        self.assertEqual("True", data["SearchInfo.help"])

    def test_list_option(self):
        for opt, v1, v2 in [
            ("-0", "True", "False"),
            ("-0p", "False", "True"),
            ("--list", "True", "False"),
            ("--list-paths", "False", "True"),
        ]:
            with self.subTest(opt):
                data = self.run_py([opt])
                self.assertEqual(v1, data["SearchInfo.list"])
                self.assertEqual(v2, data["SearchInfo.listPaths"])

    def test_list(self):
        data = self.run_py(["--list"])
        found = {}
        expect = {}
        for line in data["stdout"].splitlines():
            m = re.match(r"\s*(.+?)\s+?(\*\s+)?(.+)$", line)
            if m:
                found[m.group(1)] = m.group(3)
        for company in TEST_DATA:
            company_data = TEST_DATA[company]
            tags = [t for t in company_data if isinstance(company_data[t], dict)]
            for tag in tags:
                arg = f"-V:{company}/{tag}"
                expect[arg] = company_data[tag]["DisplayName"]
            expect.pop(f"-V:{company}/ignored", None)

        actual = {k: v for k, v in found.items() if k in expect}
        try:
            self.assertDictEqual(expect, actual)
        except:
            if support.verbose:
                print("*** STDOUT ***")
                print(data["stdout"])
            raise

    def test_list_paths(self):
        data = self.run_py(["--list-paths"])
        found = {}
        expect = {}
        for line in data["stdout"].splitlines():
            m = re.match(r"\s*(.+?)\s+?(\*\s+)?(.+)$", line)
            if m:
                found[m.group(1)] = m.group(3)
        for company in TEST_DATA:
            company_data = TEST_DATA[company]
            tags = [t for t in company_data if isinstance(company_data[t], dict)]
            for tag in tags:
                arg = f"-V:{company}/{tag}"
                install = company_data[tag]["InstallPath"]
                try:
                    expect[arg] = install["ExecutablePath"]
                    try:
                        expect[arg] += " " + install["ExecutableArguments"]
                    except KeyError:
                        pass
                except KeyError:
                    expect[arg] = str(Path(install[None]) / Path(sys.executable).name)

            expect.pop(f"-V:{company}/ignored", None)

        actual = {k: v for k, v in found.items() if k in expect}
        try:
            self.assertDictEqual(expect, actual)
        except:
            if support.verbose:
                print("*** STDOUT ***")
                print(data["stdout"])
            raise

    def test_filter_to_company(self):
        company = "PythonTestSuite"
        data = self.run_py([f"-V:{company}/"])
        self.assertEqual("X.Y.exe", data["LaunchCommand"])
        self.assertEqual(company, data["env.company"])
        self.assertEqual("3.100", data["env.tag"])

    def test_filter_to_tag(self):
        company = "PythonTestSuite"
        data = self.run_py([f"-V:3.100"])
        self.assertEqual("X.Y.exe", data["LaunchCommand"])
        self.assertEqual(company, data["env.company"])
        self.assertEqual("3.100", data["env.tag"])

        data = self.run_py([f"-V:3.100-3"])
        self.assertEqual("X.Y-32.exe", data["LaunchCommand"])
        self.assertEqual(company, data["env.company"])
        self.assertEqual("3.100-32", data["env.tag"])

        data = self.run_py([f"-V:3.100-a"])
        self.assertEqual("X.Y-arm64.exe -X fake_arg_for_test", data["LaunchCommand"])
        self.assertEqual(company, data["env.company"])
        self.assertEqual("3.100-arm64", data["env.tag"])

    def test_filter_to_company_and_tag(self):
        company = "PythonTestSuite"
        data = self.run_py([f"-V:{company}/3.1"])
        self.assertEqual("X.Y.exe", data["LaunchCommand"])
        self.assertEqual(company, data["env.company"])
        self.assertEqual("3.100", data["env.tag"])

    def test_search_major_3(self):
        try:
            data = self.run_py(["-3"], allow_fail=True)
        except subprocess.CalledProcessError:
            raise unittest.SkipTest("requires at least one Python 3.x install")
        self.assertEqual("PythonCore", data["env.company"])
        self.assertTrue(data["env.tag"].startswith("3."), data["env.tag"])

    def test_search_major_3_32(self):
        try:
            data = self.run_py(["-3-32"], allow_fail=True)
        except subprocess.CalledProcessError:
            if not any(is_installed(f"3.{i}-32") for i in range(5, 11)):
                raise unittest.SkipTest("requires at least one 32-bit Python 3.x install")
            raise
        self.assertEqual("PythonCore", data["env.company"])
        self.assertTrue(data["env.tag"].startswith("3."), data["env.tag"])
        self.assertTrue(data["env.tag"].endswith("-32"), data["env.tag"])

    def test_search_major_2(self):
        try:
            data = self.run_py(["-2"], allow_fail=True)
        except subprocess.CalledProcessError:
            if not is_installed("2.7"):
                raise unittest.SkipTest("requires at least one Python 2.x install")
        self.assertEqual("PythonCore", data["env.company"])
        self.assertTrue(data["env.tag"].startswith("2."), data["env.tag"])

    def test_py_default(self):
        with self.py_ini(TEST_PY_COMMANDS):
            data = self.run_py(["-arg"])
        self.assertEqual("PythonTestSuite", data["SearchInfo.company"])
        self.assertEqual("3.100", data["SearchInfo.tag"])
        self.assertEqual("X.Y.exe -arg", data["stdout"].strip())

    def test_py2_default(self):
        with self.py_ini(TEST_PY_COMMANDS):
            data = self.run_py(["-2", "-arg"])
        self.assertEqual("PythonTestSuite", data["SearchInfo.company"])
        self.assertEqual("3.100-32", data["SearchInfo.tag"])
        self.assertEqual("X.Y-32.exe -arg", data["stdout"].strip())

    def test_py3_default(self):
        with self.py_ini(TEST_PY_COMMANDS):
            data = self.run_py(["-3", "-arg"])
        self.assertEqual("PythonTestSuite", data["SearchInfo.company"])
        self.assertEqual("3.100-arm64", data["SearchInfo.tag"])
        self.assertEqual("X.Y-arm64.exe -X fake_arg_for_test -arg", data["stdout"].strip())

    def test_py_shebang(self):
        with self.py_ini(TEST_PY_COMMANDS):
            with self.script("#! /usr/bin/env python -prearg") as script:
                data = self.run_py([script, "-postarg"])
        self.assertEqual("PythonTestSuite", data["SearchInfo.company"])
        self.assertEqual("3.100", data["SearchInfo.tag"])
        self.assertEqual(f"X.Y.exe -prearg {script} -postarg", data["stdout"].strip())

    def test_py2_shebang(self):
        with self.py_ini(TEST_PY_COMMANDS):
            with self.script("#! /usr/bin/env python2 -prearg") as script:
                data = self.run_py([script, "-postarg"])
        self.assertEqual("PythonTestSuite", data["SearchInfo.company"])
        self.assertEqual("3.100-32", data["SearchInfo.tag"])
        self.assertEqual(f"X.Y-32.exe -prearg {script} -postarg", data["stdout"].strip())

    def test_py3_shebang(self):
        with self.py_ini(TEST_PY_COMMANDS):
            with self.script("#! /usr/bin/env python3 -prearg") as script:
                data = self.run_py([script, "-postarg"])
        self.assertEqual("PythonTestSuite", data["SearchInfo.company"])
        self.assertEqual("3.100-arm64", data["SearchInfo.tag"])
        self.assertEqual(f"X.Y-arm64.exe -X fake_arg_for_test -prearg {script} -postarg", data["stdout"].strip())

    def test_install(self):
        data = self.run_py(["-V:3.10"], env={"PYLAUNCHER_ALWAYS_INSTALL": "1"}, expect_returncode=111)
        cmd = data["stdout"].strip()
        # If winget is runnable, we should find it. Otherwise, we'll be trying
        # to open the Store.
        try:
            subprocess.check_call(["winget.exe", "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            self.assertIn("ms-windows-store://", cmd)
        else:
            self.assertIn("winget.exe", cmd)
        # Both command lines include the store ID
        self.assertIn("9PJPW5LDXLZ5", cmd)
