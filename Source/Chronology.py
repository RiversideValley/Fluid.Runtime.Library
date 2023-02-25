# System.Chronology

import time as Legacy

def Time(TimeZone: str, WithSeconds=None):
  if TimeZone == "UCT":
    if WithSeconds == True:
      return "# todo"
    else:
      CurrentStructuredTime = Legacy.gmtime()
      return f"{CurrentStructuredTime.tm_hour}:{CurrentStructuredTime.tm_min}"