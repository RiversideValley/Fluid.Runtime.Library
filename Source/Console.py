"""System.Console

Foundation class for the purpose of displaying plain text on the console, particularly for debugging or logging.
Also comes with an advanced logger to format logs neatly in the console.
Not recommended for actual text display as part of a , use only for logging purposes.
"""

def WriteLine(LineText):
  print(LineText)

def Write(Text):
  print(Text, end="")

