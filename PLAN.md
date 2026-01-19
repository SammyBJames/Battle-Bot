# Plan: Battle Bot CTF Web Server

This plan outlines the creation of a vulnerable Flask web application controlling a physical robot. The application will guide students through three levels of cybersecurity challenges (Reconnaissance, Cookie Manipulation, SQL Injection) to gain control of the robot.

### Steps
- [ ] **Project & Database Setup**: Initialize a SQLite database in `main.py` with a `Users` table containing a standard user and an admin account. Connect the existing `Robot` class to the Flask app.
- [ ] **Frontend Base (Shadcn-like)**: Create a base Jinja2 template with TailwindCSS (via CDN) to mimic the "shadcn/ui" modern dark mode aesthetic (zinc/slate colors, clean typography, rounded corners).
- [ ] **Level 1 (Recon)**: Implement the root route `index.html` with the hidden HTML comment. The `/robots.txt` route will reveal the secret login path (`/secret-login-page`). It will also dynamically generate (or retrieve) a unique username and 8-char random password tied to the user's IP address.
- [ ] **Level 2 (Auth & Cookies)**: Create the login route and a `dashboard.html`. Middleware will check for a `searchEnabled` cookie. If `False/Missing`, the search UI is disabled; if `True`, the search input is revealed.
- [ ] **Level 3 (SQL Injection)**: Implement a vulnerable search endpoint (using raw SQL string concatenation). Ensure the 'Search' results table and the 'Users' table have the exact same number of columns to facilitate easy UNION-based SQLi, allowing students to dump the `Users` table and retrieve the admin credentials.
- [ ] **Admin Control & Win**: Update `dashboard.html` to show directional control buttons only for the `admin` user. Create API endpoints to trigger `robot.py` movement methods.

### Further Considerations
1.  **Vulnerability Safety**: Since this is educational, should we sanitize inputs *everywhere else* to ensure only the intended SQLi vector works?
2.  **Robot Safety**: The current movement code is blocking. Should we add a small delay or non-blocking logic to prevent the server from hanging during moves?
3.  **Deployment**: Will this run on a Raspberry Pi? We should ensure the database file is writable in the deployment environment.
