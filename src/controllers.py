import os

def get_active_application():
  # AppleScript to get the active application
  script = """
  tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
  end tell
  return frontApp
  """
  result = os.popen(f"osascript -e '{script}'").read().strip()
  return result

# Add a locker with two hands to avoid gestures while is locked

def zoom_in():
  # We obtain the active application
  active_app = get_active_application()
  
  if active_app in ["Google Chrome", "Brave Browser", "Safari"]:
    # If we are in a browser, we use AppleScript to change the tab.
    script = f"""
    tell application "System Events"
      tell application process "System Events"
        key down command
        keystroke "+"
        key up command
      end tell
    end tell
    """
    os.system(f"osascript -e '{script}'")
  else:
    print(f"You cannot scroll in {active_app}.")
    
def zoom_out():
  # We obtain the active application
  active_app = get_active_application()
  
  if active_app in ["Google Chrome", "Brave Browser", "Safari"]:
    # If we are in a browser, we use AppleScript to change the tab.
    script = f"""
    tell application "System Events"
      tell application process "System Events"
        key down command
        keystroke "-"
        key up command
      end tell
    end tell
    """
    os.system(f"osascript -e '{script}'")
  else:
    print(f"You cannot scroll in {active_app}.")
    
def scroll_up():
  # We obtain the active application
  active_app = get_active_application()
  
  if active_app in ["Google Chrome", "Brave Browser", "Safari"]:
    # If we are in a browser, we use AppleScript to change the tab.
    script = f"""
    tell application "System Events"
      repeat 10 times -- Adjust this number for faster scrolling
        key code 126 -- Simulates the "Arrow Up" key
        delay 0.01 -- Minimum delay for smoother performance
      end repeat
    end tell
    """
    os.system(f"osascript -e '{script}'")
  else:
    print(f"You cannot scroll in {active_app}.")

def scroll_down():
  # We obtain the active application
  active_app = get_active_application()
  
  if active_app in ["Google Chrome", "Brave Browser", "Safari"]:
    # If we are in a browser, we use AppleScript to change the tab.
    script = f"""
    tell application "System Events"
      repeat 10 times -- Adjust this number for faster scrolling
        key code 125 -- Simulates the "Arrow Down" key
        delay 0.01 -- Minimum delay for smoother performance
      end repeat
    end tell
    """
    os.system(f"osascript -e '{script}'")
  else:
    print(f"You cannot scroll in {active_app}.")

def previous_tab():
  # We obtain the active application
  active_app = get_active_application()
  
  if active_app in ["Google Chrome", "Brave Browser", "Safari"]:
    # If we are in a browser, we use AppleScript to change the tab.
    script = f"""
    tell application "{active_app}"
      tell window 1
        set activeTabIndex to (active tab index) - 1
        if activeTabIndex = 1 then
          set activeTabIndex to (count of tabs) - 1
        end if
        set active tab index to activeTabIndex
      end tell
    end tell
    """
    os.system(f"osascript -e '{script}'")
  else:
    print(f"You cannot change the tab in {active_app}.")
    
def next_tab():
  # We obtain the active application
  active_app = get_active_application()
  
  if active_app in ["Google Chrome", "Brave Browser", "Safari"]:
    # If we are in a browser, we use AppleScript to change the tab.
    script = f"""
    tell application "{active_app}"
      tell window 1
        set activeTabIndex to (active tab index) + 1
        if activeTabIndex > (count of tabs) then
          set activeTabIndex to 1
        end if
        set active tab index to activeTabIndex
      end tell
    end tell
    """
    os.system(f"osascript -e '{script}'")
  else:
    print(f"You cannot change the tab in {active_app}.")
