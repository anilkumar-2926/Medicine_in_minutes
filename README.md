# Medicine in Minutes — Patient Description & Shop Response Platform

## Correct workflow
- Patients register on the separate patient portal and describe their health concern.
- Submitted descriptions appear in the medical shop portal.
- Each medical shop has its own login and can send one response per request.
- Patients see responses from shops in their patient dashboard.
- Shop accounts see their own sent responses and requests not yet answered by that shop.
- Both portals use the same SQLite database, with separate Flask applications and session cookies.

## Run on Windows
1. Extract the ZIP.
2. Open this folder in VS Code.
3. Open a terminal in this folder.
4. Run: `python -m pip install -r requirements.txt`
5. Run `run_both.bat`, or open two terminals and run `python patient_app.py` and `python shop_app.py`.

## Local URLs
- Patient portal: http://127.0.0.1:5000
- Medical shop portal: http://127.0.0.1:5001

## Test
1. Register a shop at port 5001.
2. Register a patient at port 5000.
3. Patient submits a problem description from their dashboard.
4. Shop opens its dashboard, reviews the request and submits a response.
5. Patient refreshes their dashboard to view the shop response.

## Important
This starter is for development and demonstration, not for real clinical use. It does not diagnose, triage, or prescribe. A qualified healthcare professional must assess symptoms and treatment. Do not use it to recommend prescription-only medicines without a valid prescription and legally required professional review. Add production security, CSRF protection, privacy controls, HTTPS, backups and compliance review before deployment.
"# Medicine_in_minutes" 
