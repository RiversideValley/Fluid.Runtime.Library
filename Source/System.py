"""System

A professional yet usable programming framework.
"""

class Legacy:
    """System.Legacy
    
    Foundation class for the purpose of providing legacy Python modules for more.. refined use."""
    from Legacy import os as _os;
    import sys as _sys;
    from Legacy import pathlib as _path;
    from Legacy import zipimport as _zip;
    from Legacy import csv as _csv;
    from Legacy import turtle as _turtle;
    from Legacy import socket as _socket;
    from Legacy import random as _random;
    from Legacy import subprocess as _process;
    import time as _time;

Null = type[None]
Object = object

class Branding:
    """System.Branding
    
    Get computer details, interpreter details and other variables."""

    # Windows, Microsoft
    Windows = "win32"
    Win = Windows
    Microsoft = Windows
    MSDOS = Windows
    # Cygwin
    Cygwin = "cygwin"
    # macOS, Apple
    macOS = "darwin"
    MacOS = macOS
    Apple = macOS
    Darwin = macOS
    OSX = macOS
    macOSX = macOS
    # Unix
    Unix = macOS or "linux"
    # Linux, Unix
    Linux = "linux"
    # AIX, IBM
    Aix = "aix"
    # Emscripten, WebAssembly
    Emscripten = "emscripten"
    # WebAssembly
    WebAssembly = "wasi"
    WebAssembleySystemInterface = WebAssembly
    Web = WebAssembly
    class Computer:
        """System.Branding.Computer"""
        Name = Legacy._socket.gethostname()
        Interpreter = Legacy._sys.platform
        Register = Legacy._os.name

    Model = Computer
    class User:
        """System.Branding.User"""
        Login = Legacy._os.getlogin()
        UserName = f"{Login}@{Legacy._socket.gethostname()}"

class Variables:
    def Environment(EnvironmentVariable: str):
        return Legacy._os.environ[EnvironmentVariable] 
    class Convert:
        def String(ToVariable):
            return str(ToVariable)
    
        def Integer(ToVariable):
            return int(ToVariable)

        def Float(ToVariable):
            return float(ToVariable)
        
        def Boolean(ToVariable):
            return bool(ToVariable)
        
    class String(Object):
        def __init__(This, String: str):
            This.String = String

        def __str__(This):
            return This.String
        
        def Convert(ToVariable):
            return str(ToVariable)
        
    def Search(Index, Key, MatchFullWord: bool = True):
        if MatchFullWord == False:
            return (" " + str(Key) + " ") in (" " + str(Index) + " ")
        else:
            return str(Key) in str(Index)
        
class Processing:
    """System.Processing
    
    Foundation class for the purpose of spawning, viewing and managing processes on the user's computer."""

    def Execute(ExecuteScript, ScriptTimeOut = Null, Language: str = "fl", IncludeFoundation = Null):
        """System.Execute()
    
        Foundation method for the purpose of executing Python code from a string."""
        if Language == "fl" or "py":
            if IncludeFoundation is not Null:
#               try:
                return exec(Variables.Convert.String(ExecuteScript), IncludeFoundation)
#               except NameError: # NameError is for when the person includes a Foundation module such as 'System' without using the 'IncludeFoundation' parameter.
#                   if Variables.Search(ExecuteScript, "System") is True:
#                       return exec(ExecuteScript, {"System.Console":Console})
            else:
                return exec(Variables.Convert.String(ExecuteScript))
        elif Language == "bash" or "cmd" or "command" or "cmd.exe" or "/bin/bash" or "pwsh" or "pwsh-core" or "powershell" or "shell" or "prompt" or "os.system()" or "system":
            return Legacy._process.call(ExecuteScript, timeout = ScriptTimeOut)
        else:
            raise NotImplementedError

    #class Task(Object):
        #if Branding.Computer.Interpreter is 
        #def __init__(This, Task: str, Task):



class Console:
    """System.Console

    Foundation class for the purpose of displaying plain text on the console, particularly for debugging or logging.
    Also comes with an advanced logger to format logs neatly in the console.
    Not recommended for actual text display as part of a GUI application; use only for logging purposes.
    """

    def WriteLine(Text: Null): # type: ignore
        return print(Variables.Convert.String(Text))

    def Write(Text: Null): # type: ignore
        return print(Variables.Convert.String(Text), end="")

class Chronology:
    def Time(TimeZone: str, WithSeconds=None):
        if TimeZone == "UCT":
            if WithSeconds == True:
                return Null # TODO: implement time with seconds
                return f"{Legacy._time.gmtime().tm_hour}:{Legacy._time.gmtime().tm_min}:{Legacy._time.gmtime().tm_sec}"
            else:
                return f"{Legacy._time.gmtime().tm_hour}:{Legacy._time.gmtime().tm_min}"

class Explore:
    """System.Explore

    Foundation class for the purpose of allowing the developer to read, write and make new files on the end-user's computer.
    """

    def Read(FileName: str, Auto: bool | Null, FileEncoding: str | Null):
        """System.Explore.Read()

        Foundation method for the purpose of a allowing the developer to read files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "r", encoding = FileEncoding)
        else:
            return open(FileName, "r", encoding = FileEncoding).read()
    # type: ignore   
    def Write(FileName: str, Auto: bool | Null, AutoValue: str | Null, FileEncoding: Null):     
        """System.Explore.Write()

        Foundation method for the purpose of a allowing the developer to write files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "w", encoding = FileEncoding)
        else:
            return open(FileName, "w", encoding = FileEncoding).write(Variables.String.Convert(AutoValue))

    def Append(FileName: str, Auto: bool | Null, AutoValue: Null, FileEncoding: Null):
        """System.Explore.Append()

        Foundation method for the purpose of a allowing the developer to append to files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "a", encoding = FileEncoding)
        else:
            return open(FileName, "a", encoding = FileEncoding).write(AutoValue)

    def Create(FileName: str, FileEncoding: str | Null):
        """System.Explore.Create()

        Foundation method for the purpose of a allowing the developer to create files on the end-user's computer.
        """
        return open(FileName, "x", encoding = FileEncoding)

    def Access(FileName: str, FileEncoding: str | Null):
        """System.Explore.Access()

        Foundation method for the purpose of a allowing the developer to access files completely on the end-user's computer.
        """
        return open(FileName, "r+", encoding = FileEncoding)

class Packaging:
    """System.Packaging
    
    An advanced Foundation class enabling the developer to properly package their application.
    """
    class App(Object):
        """System.Packaging.Package"""
