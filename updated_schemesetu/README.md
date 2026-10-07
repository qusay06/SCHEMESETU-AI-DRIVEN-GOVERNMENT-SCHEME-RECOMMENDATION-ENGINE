# SchemeSetu Enhanced - Console Version

This version adds:

- Login
- Register
- Exit
- Email OTP verification during registration
- Password validation
- PBKDF2 password hashing
- SQLite database storage
- User eligibility profiles
- Conditional student / farmer / business questions
- TF-IDF scheme recommendations using the full scheme text
- Benefits, eligibility, documents and application details in results

## 1. Project files

Place your `updated_data.csv` in the same directory:

```
SchemeSetu/
├── app.py
├── auth.py
├── database.py
├── profile_manager.py
├── preprocess.py
├── recommender.py
├── updated_data.csv
├── requirements.txt
├── .env
└── .gitignore
```

`schemes.csv` and `schemesetu.db` will be created automatically.

## 2. Install requirements

```powershell
python -m pip install -r requirements.txt
```

If your `python` command is still not mapped correctly, use the full Python executable path that works on your PC.

## 3. Configure OTP email

Copy `.env.example` to `.env`.

Then enter the Gmail account that will send SchemeSetu verification emails and its Google App Password.

Never upload `.env` to GitHub.

## 4. Preprocess all schemes

```powershell
python preprocess.py
```

The supplied dataset has about 3,400 scheme rows. The final number can be slightly lower if duplicate or empty scheme records are removed.

## 5. Run

```powershell
python app.py
```

## Console flow

```
SCHEMESETU

1. Login
2. Register
3. Exit
```

Registration:

```
Name
Email
Password
Confirm password
        ↓
OTP emailed
        ↓
Enter OTP in console
        ↓
Account stored in SQLite
```

After login:

```
1. Find schemes
2. Create / Update eligibility profile
3. View my profile
4. Logout
```

## Important eligibility note

The dataset's `eligibility` field is primarily free-form text. The recommendation engine uses profile details and textual similarity to rank schemes, but this is not a legal guarantee that a person is eligible. A later version can parse each scheme's eligibility statements into structured machine-readable rules for strict eligibility checking.
