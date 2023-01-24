"""C:System

A professional yet usable Python framework.
"""

from src import Branding;
from src import Chronology;
from src import Console;
from src import Explore;
from src import Packaging;
from src import Random;

import sys as Legacy;
import os as Legacy;

def Execute(ExecuteThis: str, IncludeFoundation=None):
    """M:System.Execute()
    
    Foundation method for the purpose of executing Python code from a string."""
    exec(ExecuteThis, IncludeFoundation)

Type = Branding.Name
