# Test Checklist (A24e)

1) **Launch**  
   - `python start_dashboard.py` starts without warnings (ignore known PNG warnings if still present).

2) **Exit dialog**  
   - Click **Exit** → dialog opens **224×133**; title is green; body text matches Table‑1.  
   - Click **No** → stays in app. Click **Yes** → app quits.

3) **Bet Card**  
   - Click **Bet Card** → dialog opens **≈110×80 mm** and is readable.  
   - Try on a second monitor / different Windows scaling → still readable.

4) **Spinboxes**  
   - All six show **+/-** arrows; clicks adjust values; wheel scroll changes value.

5) **Regression**  
   - Search for `QDialog {` in code; verify none in app‑wide styles.
