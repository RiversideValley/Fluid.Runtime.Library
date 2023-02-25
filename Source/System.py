"""System

A professional yet usable programming framework.
"""

class Legacy:
    """System.Legacy
    
    Foundation class for the purpose of providing legacy Python modules for more.. refined use."""
    import os as _os;
    import sys as _sys;
    import pathlib as _path;
    import zipimport as _zip;
    import csv as _csv;
    import turtle as _turtle;
    import socket as _socket;
    import random as _random;

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

def Execute(ExecuteThis: str, IncludeFoundation=None):
    """System.Execute()
    
    Foundation method for the purpose of executing Python code from a string."""
    exec(ExecuteThis, IncludeFoundation)

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
        UserName = Login

class Explore:
    """System.Explore

    Foundation class for the purpose of allowing the developer to read, write and make new files on the end-user's computer.
    """

    def Read(FileName: str, Auto=None, FileEncoding=None):
        """System.Explore.Read()

        Foundation method for the purpose of a allowing the developer to read files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "r", encoding = FileEncoding)
        else:
            return open(FileName, "r", encoding = FileEncoding).read()

    def Write(FileName: str, Auto=None, AutoValue=None, FileEncoding=None):
        """System.Explore.Write()

        Foundation method for the purpose of a allowing the developer to write files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "w", encoding = FileEncoding)
        else:
            return open(FileName, "w", encoding = FileEncoding).write(Variables.Convert.String(AutoValue))

    def Append(FileName: str, Auto=None, AutoValue=None, FileEncoding=None):
        """System.Explore.Append()

        Foundation method for the purpose of a allowing the developer to append to files on the end-user's computer.
        """
        if Auto == False:
            return open(FileName, "a", encoding = FileEncoding)
        else:
            return open(FileName, "a", encoding = FileEncoding).write(AutoValue)

    def Create(FileName: str, FileEncoding=None):
        """System.Explore.Create()

        Foundation method for the purpose of a allowing the developer to create files on the end-user's computer.
        """
        return open(FileName, "x", encoding = FileEncoding)

    def Access(FileName: str, FileEncoding=None):
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
