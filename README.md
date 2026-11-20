# ICE Website & Management System

Website, online giving and management system for the International Center of Evangelism (Jos).
Built with FastAPI + SQLAlchemy (SQLite or MySQL) and a plain HTML/CSS/JS frontend.

## Pages
- `/site/`   public website: Home, About, Ministries, Events (with registration), Gallery, Give, Contact
- `/admin/`  staff portal: Dashboard, Staff, Members, Donors, Donations, Online Gifts, Events, Registrations, Gallery, Messages, Reports
- `/docs`    API documentation

## Run
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then edit it
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. Tables are created automatically on startup.

First admin: go to `/admin/` and click "First time? Create the admin account" (works only once).

## Database
Default is SQLite. For MySQL set in `.env`:
`DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ice?charset=utf8mb4`
New tables are added automatically; existing tables are not altered.

## Online giving (Paystack)
1. Create a Paystack account and copy the secret key into `PAYSTACK_SECRET_KEY` (use `sk_test_...` while testing).
2. Set `SITE_URL` to the public address of the site (the payment return link uses it).
3. In the Paystack dashboard set the webhook URL to `SITE_URL/give/webhook`.
4. Successful gifts are saved under Online Gifts and also recorded as a Donation (the donor is matched by email or created).
Leave `PAYSTACK_SECRET_KEY` empty to switch online giving off; the Give page then shows a friendly message.

## Reports & backup
Admin > Reports shows donations by month, top donors, staff by department and members by type (printable),
and "Download backup" saves every table as one JSON file. Do this regularly and keep copies off the server.

## Before going live
- Use a strong `SECRET_KEY`, serve over HTTPS (domain + SSL) and keep `.env` out of git.
- Gallery uploads are stored in `app/static/uploads/`; back that folder up too.
