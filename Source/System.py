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

Null = None

class Variables:
    class Convert:
        def String(ToVariable):
            return str(ToVariable)
    
        def Integer(ToVariable):
            return int(ToVariable)

        def Float(ToVariable):
            return float(ToVariable)
        
        def Boolean(ToVariable):
            return bool(ToVariable)
        
    class String(object):
        def __init__(self, String: str):
            self.String = String

        def __str__(self):
            return self.String
        
        def Convert(ToVariable):
            return str(ToVariable)
        
    def Search(Index, Key):
        return (" " + str(Key) + " ") in (" " + str(Index) + " ")

class Console():
    """System.Console

    Foundation class for the purpose of displaying plain text on the console, particularly for debugging or logging.
    Also comes with an advanced logger to format logs neatly in the console.
    Not recommended for actual text display as part of a GUI application, use only for logging purposes.
    """

    def WriteLine(Text):
        return print(Text)

    def Write(Text):
        return print(Text, end="")

    def Execute(ExecuteThis: str, IncludeFoundation | Null):
        """System.Execute()
    
        Foundation method for the purpose of executing Python code from a string."""
#        try:
        return exec(ExecuteThis, IncludeFoundation)
#        except NameError:
#            if Variables.Search(ExecuteThis, "System") == True:
#                return exec(ExecuteThis, {"System.Console":Console})

class Branding:
    """System.Branding
    
    Get computer details, interpreter details and other variables."""
    class Computer:
        """System.Branding.Computer"""
        Name = Legacy._socket.gethostname()
        Interpreter = Legacy._sys.platform
        SystemVar = Legacy._os.name
    Model = Computer
    class User:
        """System.Branding.User"""
        Login = Legacy._os.getlogin()
        UserName = f"{Login}@{Legacy._socket.gethostname()}"

class Explore:
    """System.Explore

    Foundation class for the purpose of allowing the developer to read, write and make new files on the end-user's computer.
    """

    def Read(FileName: str, Auto | Null, FileEncoding | Null):
        """System.Explore.Read()

        Foundation method for the purpose of a allowing the developer to read files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "r", encoding = FileEncoding)
        else:
            return open(FileName, "r", encoding = FileEncoding).read()
    # type: ignore   
    def Write(FileName: str, Auto: bool | Null, AutoValue: str | Null, FileEncoding | Null):     
        """System.Explore.Write()

        Foundation method for the purpose of a allowing the developer to write files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "w", encoding = FileEncoding)
        else:
            return open(FileName, "w", encoding = FileEncoding).write(Variables.String.Convert(AutoValue))

    def Append(FileName: str, Auto | Null, AutoValue | Null, FileEncoding | Null):
        """System.Explore.Append()

        Foundation method for the purpose of a allowing the developer to append to files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "a", encoding = FileEncoding)
        else:
            return open(FileName, "a", encoding = FileEncoding).write(AutoValue)

    def Create(FileName: str, FileEncoding | Null):
        """System.Explore.Create()

        Foundation method for the purpose of a allowing the developer to create files on the end-user's computer.
        """
        return open(FileName, "x", encoding = FileEncoding)

    def Access(FileName: str, FileEncoding | Null):
        """System.Explore.Access()

        Foundation method for the purpose of a allowing the developer to access files completely on the end-user's computer.
        """
        return open(FileName, "r+", encoding = FileEncoding)

class Packaging:
    """System.Packaging
    
    An advanced Foundation class enabling the developer to properly package their application.
    """
    class App(object):
        """System.Packaging.Package"""
