# Cron scheduling

Add the following entries to the user's crontab to trigger the agency at the desired times (server time should match the configured timezone):

```
# 09:00 morning slot
0 9 * * 1-5 cd /path/to/sod-emuna-agency && /usr/bin/python -m src.agency morning

# 15:00 noon slot
0 15 * * 1-5 cd /path/to/sod-emuna-agency && /usr/bin/python -m src.agency noon

# 22:00 night slot
0 22 * * 1-5 cd /path/to/sod-emuna-agency && /usr/bin/python -m src.agency night
```
