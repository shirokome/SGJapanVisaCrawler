This tool helps you more easily secure your desired Japan visa appointment slot.
## How It Works

1. The script checks the reservation system status every 50–70 seconds.
2. If any of your specified dates match available slots, an email notification is sent.

## Setup Instructions

1. Enter your Gmail account and app password to enable email notifications. (You may use other email providers with additional configuration.)
2. Modify the target date(s) and month in the script. You can specify multiple dates.

## Running the Script

```bash
pip install selenium
```

```bash
python visa.py
```

## Notes

- To keep the script running continuously, do not shut down your computer. Consider using a server or cloud host for reliability.
- You may adjust the frequency of checks, but excessive requests could result in your IP being blocked by the website.
- Star the repo if it helps, thank you.