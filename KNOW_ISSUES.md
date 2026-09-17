This document tracks known issues and planned improvements that should be addressed in future versions of the application.


**Multiple Instances Can Be Opened**

The application currently allows multiple instances to be launched simultaneously.

Current Behavior

User opens the application.
User launches the application again.
A second instance is created.
Additional launches continue creating new instances.

Expected Behavior

Only one instance of the application should be allowed to run at a time.

If the user attempts to launch the application while it is already running, the existing window should be restored and brought to the foreground instead of creating a new instance.

*Priority: High*

----------------------

**Snooze Reminder Feature**

Add a "Snooze" option when a medication reminder is triggered.

Expected Behavior

When a reminder appears, the user should be able to:

Confirm the medication was taken.
Snooze the reminder for a short period.

Suggested Option

Remind me again in 5 minutes.

Potential Future Enhancements

5 minutes

*Priority: Medium*