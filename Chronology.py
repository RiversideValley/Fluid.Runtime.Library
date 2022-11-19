# System.Chronology

import time as Legacy

def Time(TimeZone, WithSeconds=None):
  if TimeZone == "UCT":
    if WithSeconds == False:
      CurrentStructuredTime = Legacy.gmtime()
      # to-do
    
