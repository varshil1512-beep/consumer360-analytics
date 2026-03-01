# Weekly Automation (Windows Task Scheduler)

Create a weekly Sunday 11:00 PM run:

```powershell
$python = "D:\Retail - Customer Behavior & RFM Analysis\.venv\Scripts\python.exe"
$script = "-m src.main"
$action = New-ScheduledTaskAction -Execute $python -Argument $script -WorkingDirectory "D:\Retail - Customer Behavior & RFM Analysis"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 11:00PM
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel LeastPrivilege
Register-ScheduledTask -TaskName "Consumer360 Weekly Refresh" -Action $action -Trigger $trigger -Principal $principal
```

Validate run history after the first scheduled date.
