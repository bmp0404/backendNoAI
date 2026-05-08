psql -U krish -d bookmark_db
TRUNCATE bookmarktag, tag, bookmark RESTART IDENTITY CASCADE;
\q

pytest pytest/test_api.py -v