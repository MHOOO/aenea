#!/usr/bin/python

import comsat, sys, os, random

# to help see when the server has started while in a bash loop
for i in range(random.randint(1, 10)):
  print

XPROP_PROPERTIES = {
    "_NET_WM_DESKTOP(CARDINAL)":"desktop",
    "WM_WINDOW_ROLE(STRING)":"role",
    "_NET_WM_WINDOW_TYPE(ATOM)":"type",
    "_NET_WM_PID(CARDINAL)":"pid",
    "WM_LOCALE_NAME(STRING)":"locale",
    "WM_CLIENT_MACHINE(STRING)":"client_machine",
    "WM_NAME(STRING)":"name"
    }

XDOTOOL_COMMAND_BREAK = set(("type",))

class Handler(object):
  def __init__(self):
    self.state = {}

  @classmethod
  def runCommand(cls, command, executable="xdotool"):
    command_string = "%s %s" % (executable, command)
    sys.stderr.write(command_string + "\n")
    os.system(command_string)
  
  @classmethod
  def readCommand(cls, command, executable="xdotool"):
    with os.popen("%s %s" % (executable, command), "r") as fd:
      rval = fd.read()
    return rval
  
  @classmethod
  def writeCommand(cls, message, executable="xdotool"):
    with os.popen("%s type --file -" % executable, "w") as fd:
      fd.write(message)

  @classmethod
  def getActiveWindow(cls):
    """Returns the window id and title of the active window."""
    window_id = cls.readCommand("getactivewindow")
    if window_id:
      window_id = int(window_id)
      window_title = cls.readCommand("getwindowname %i" % window_id).strip()
      return window_id, window_title
    else:
      return None, None

  @classmethod
  def getGeometry(cls, window_id=None):
    if window_id is None:
      window_id, _ = cls.getActiveWindow()
    geo = dict([val.lower() for val in line.split("=")]
               for line in cls.readCommand(("getwindowgeometry --shell %i"
                                             % window_id)).strip().split("\n"))
    geo = dict((key, int(value)) for (key, value) in geo.iteritems())
    return dict((key, geo[key]) for key in ("x", "y", "width", "height", "screen"))

  @classmethod
  def _transform_relative_mouse_event(cls, event):
    geo = cls.getGeometry()
    dx, dy = map(int, map(float, event.split()))
    return [("mousemove", "%i %i" % (geo["x"] + dx, geo["y"] + dy))]

  def callGetCurrentWindow(self):
    """return a dictionary of window properties for the currently active window.
       it is fine to include platform specific information, but at least include
       title and executable."""
    window_id, window_title = self.getActiveWindow()
    if window_id is None:
      return {}

    properties = {
        "id":window_id,
        "title":window_title,
      }
    for line in self.readCommand("-id %s" % window_id, "xprop").split("\n"):
      split = line.split(" = ", 1)
      if len(split) == 2:
        rawkey, value = split
        if split[0] in XPROP_PROPERTIES:
          properties[XPROP_PROPERTIES[rawkey]] = value[1:-1] if "(STRING)" in rawkey else value
        elif rawkey == "WM_CLASS(STRING)":
          window_class_name, window_class = value.split('", "')
          properties["cls_name"] = window_class_name[1:]
          properties["cls"] = window_class[:-1]

    # Sigh...
    properties["executable"] = None
    try:
      properties["executable"] = os.readlink("/proc/%s/exe" % properties["pid"])
    except OSError:
      ps = self.readCommand("%s" % properties["pid"], executable="ps").split("\n")[1:]
      if ps:
        try:
          properties["executable"] = ps[0].split()[4]
        except Exception:
          raise
          pass

    return properties

  def callReloadConfiguration(self):
    pass

  def callExecute(self, events):
    """Execute a sequence of xdotool-style events using xdotool."""
    transformed_events = [[]]
    for (command, arguments) in events:
      if command == "mousemove_active":
        transformed_events[-1].extend(self._transform_relative_mouse_event(arguments))
      elif command in XDOTOOL_COMMAND_BREAK:
        transformed_events.append([(command, arguments)])
        transformed_events.append([])
      else:
        transformed_events[-1].append((command, arguments))

    for events in filter(None, transformed_events):
      if events[0][0] == "type":
        self.writeCommand(events[0][1])
      else:
        self.readCommand(' '.join("%s %s" % event for event in events))

cs = comsat.ComSat()
cs.handlers.append(Handler())

loop = cs.serverMainLoop()
while 1:
  loop.next()