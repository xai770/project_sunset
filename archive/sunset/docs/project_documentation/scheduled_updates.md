# Setting Up Scheduled Model Ranking Updates

This guide explains how to set up automated scheduled updates for the LLM model rankings using cron.

## Overview

The system includes a scheduled task script (`scripts/bin/scheduled_ranking_update.sh`) that:
1. Updates model rankings based on accumulated performance data
2. Runs benchmark tests on a sample of tasks to refresh performance metrics
3. Logs all activities for monitoring and debugging

## Installation Steps

### 1. Verify the script is executable

```bash
chmod +x /home/xai/Documents/sunset/scripts/bin/scheduled_ranking_update.sh
```

### 2. Test the script manually

Run the script once to make sure it works correctly:

```bash
/home/xai/Documents/sunset/scripts/bin/scheduled_ranking_update.sh
```

Check the logs folder for the output.

### 3. Set up a cron job

Open your crontab file:

```bash
crontab -e
```

Add a line to run the script daily at midnight:

```
0 0 * * * /home/xai/Documents/sunset/scripts/bin/scheduled_ranking_update.sh
```

Or weekly on Sunday at 3 AM:

```
0 3 * * 0 /home/xai/Documents/sunset/scripts/bin/scheduled_ranking_update.sh
```

### 4. Verify the cron job

List your current cron jobs to make sure it was added:

```bash
crontab -l
```

## Checking Results

- Check the logs directory for update logs
- Review the model rankings in `config/model_rankings.json` to see changes
- Monitor the performance feedback data in `config/model_performance_feedback.json`

## Troubleshooting

If the scheduled updates aren't working:

1. Check the log files in the logs directory
2. Make sure the script has executable permissions
3. Verify the cron job is properly configured
4. Check that the Python environment is correctly activated in the script
5. Ensure file paths in the script are correct
