
DROP-IN: Logout Dialog (matches API Key style)
=============================================

Files in this folder:
- logout_dialog_custom.py  (black/orange compact dialog)

How to install (no risk):
1) Copy BOTH files into your folder:
   C:\Users\Steven\Documents\ARBITRAGE120925G\

2) Edit C:\Users\Steven\Documents\ARBITRAGE120925G\dashboard.py
   Find the method:  def _logout(self):
   Replace its ENTIRE body with this:

       from logout_dialog_custom import show_logout
       if show_logout(self):  # True if "Yes"
           from PyQt6.QtWidgets import QApplication
           QApplication.quit()

3) Save the file and run:
   python C:\Users\Steven\Documents\ARBITRAGE120925G\start_dashboard.py

That's it. Your Logout dialog now matches the API Key window style.
