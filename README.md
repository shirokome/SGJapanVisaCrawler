How it works:
  1. The program fetch the status of the reservation system every 50-70 seconds.
  2. Every time a match is detected between your desired date and an available slot, an email will be sent to notify you.

Customize the file to make it work:
  1. Add your Gmail account and password, to enable email notification. (Other emails are possible to use if you change more.)
  2. Edit the date to be your desired date(and corresponding month). You can choose multiple dates.

How to run:  <br />
```
pip install selenium
```
```
python visa.py
```
Notes:
  1. To keep it running, avoid shutting down your computer, or you can use a server instead.
  2. While the fetching frequency can be changed, avoid too high frequency, or your IP might be banned by the website.