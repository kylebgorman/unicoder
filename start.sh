pip3 install -r requirements.txt
gunicorn app:app --workers 1 --log-file -
