"""C:System.Explore

Foundation class for the purpose of allowing the developer to read, write and make new files on the end-user's computer.
"""

def Read(FileToReadName: str, FileToReadEncoding=None):
    """M:System.Explore.Read()

    Foundation method for the purpose of a allowing the developer to read files on the end-user's computer.
    """
    return open(FileToReadName, "r", encoding = FileToReadEncoding)

def Write(FileToWriteName: str, FileToWriteEncoding=None):
    """M:System.Explore.Write()

    Foundation method for the purpose of a allowing the developer to write files on the end-user's computer.
    """
    return open(FileToWriteName, "w", encoding = FileToWriteEncoding)

def Append(FileToAppendName: str, FileToAppendEncoding=None):
    """M:System.Explore.Append()

    Foundation method for the purpose of a allowing the developer to append to files on the end-user's computer.
    """
    return open(FileToAppendName, "a", encoding = FileToAppendEncoding)

def Create(FileToCreateName: str, FileToCreateEncoding=None):
    """M:System.Explore.Create()

    Foundation method for the purpose of a allowing the developer to create files on the end-user's computer.
    """
    return open(FileToCreateName, "x", encoding = FileToCreateEncoding)

def Access(FileToAccessName: str, FileToAccessEncoding=None):
    """M:System.Explore.Access()

    Foundation method for the purpose of a allowing the developer to access files completely on the end-user's computer.
    """
    return open(FileToAccessName, "r+", encoding = FileToAccessEncoding)

# TODO: Find a way to automatically close the explorer upon completion
# TODO
