# Microsoft 365 Troubleshooting Runbook

Purpose: isolate identity, service-health, client, browser, network, synchronization, file, and device issues across Outlook, Teams, OneDrive, Word, and Excel.

## Rapid triage

- Record application, platform, version, exact error, timestamp/time zone, and business impact.
- Determine scope: one item/file, one application, one employee, or multiple employees.
- Confirm general internet access and check the approved Microsoft 365 service-health channel.
- Compare the approved web application with the desktop/mobile client. Web success often isolates a local client issue.
- Confirm the organizational account is selected; do not enter credentials into an unfamiliar prompt.

## Identity and access

- Repeated sign-in, conditional-access, license, or account-disabled messages may require IT even when the password is correct.
- Correct device date/time and complete only MFA prompts initiated by the employee.
- Do not clear all credentials, delete a profile, or remove device registration as an initial step.

---PAGE---
# Outlook Mail and Calendar

## Outlook disconnected or not receiving mail

- Check the status bar for Working Offline, Disconnected, Trying to connect, or a password prompt.
- Open the approved web mail client. If web mail also fails, investigate identity, service health, license, or mailbox state.
- If web mail works, restart Outlook and verify Work Offline is not enabled.
- Send a small test message to the employee's own mailbox and note send/receive behavior.
- Do not delete local mail data files or recreate the profile before IT confirms synchronization and retention status.

## Repeated password prompts

- Confirm identity-portal sign-in and whether the password changed recently.
- Fully close Outlook and other Office applications, then reopen Outlook.
- Record the account/domain displayed in the prompt; dismiss prompts for unknown accounts.
- Persistent modern-authentication or conditional-access loops require IT review rather than repeated password entry.

## Search, calendar, attachment, or mailbox problems

- Determine whether one folder/item or the whole mailbox is affected.
- Compare search and calendar behavior in web mail.
- For attachment failure, record file type and size; do not bypass blocked-file policy.
- "Mailbox full" requires approved cleanup/archive or quota review. Do not permanently delete business records outside retention policy.

---PAGE---
# Teams Meetings, Calls, and Messaging

## Camera, microphone, or speaker does not work

- Open Teams device settings and select the intended approved camera, microphone, and speaker.
- Run a test call, confirm operating-system privacy permission, and close other apps using the device.
- Reconnect the headset and test without the dock or Bluetooth connection when practical.
- If the device works in another approved application, capture that distinction.

## Cannot join or poor call quality

- Confirm meeting time/link and sign in with the intended organizational account.
- Check network stability; pause large downloads and move to stronger Wi-Fi or wired connectivity.
- Record whether audio, video, screen sharing, or the entire meeting fails.
- Never install a plug-in or executable offered by an unexpected meeting page.

## Messages, presence, or Teams will not load

- Compare the Teams web client. Restart the desktop client and verify service health.
- Determine whether one chat/team or all content is affected.
- Record sync banners, timestamps, and whether other employees see the same problem.
- Avoid deleting application caches unless IT supplies a version-appropriate approved procedure; cache locations and effects change.

---PAGE---
# OneDrive, SharePoint, Word, and Excel

## OneDrive or SharePoint sync

- Check the sync icon for paused, signing in, conflict, storage full, invalid filename, or access-denied state.
- Confirm the file appears in the approved web location before deleting or moving local copies.
- Resume sync, verify organizational sign-in, and test one small file.
- Preserve both copies of a conflict until the content owner decides which changes to keep.
- Do not unlink/reset the sync client before confirming all local work is backed up.

## Word or Excel file will not open

- Copy the exact error and determine whether one file or all files are affected.
- Test the file in the approved web app and test another known-good document in the desktop app.
- Verify file extension, storage location, permissions, and whether another user has it locked.
- Use Open and Repair only on a copy when approved. Never overwrite the only copy of a damaged file.

## Application hangs or crashes

- Save recoverable work, restart the application, and test a blank document.
- Record add-ins involved and whether the issue follows one file.
- Apply company-approved Office updates. Do not disable security add-ins or macros to work around policy.
- Repeated crashes across Office applications may require repair/reinstall by IT.

---PAGE---
# Microsoft 365 Verification and Escalation

## Resolution checks

- Organizational sign-in completes without repeated prompts.
- The web and/or desktop client completes the original mail, meeting, sync, or document task.
- A test message/file synchronizes and remains correct after restart.
- No unsynchronized or conflicted data was discarded.

## Contact IT immediately

- Unexpected MFA prompts, suspicious sharing requests, malicious attachment warnings, or suspected account compromise.
- Missing business data, widespread outage, license/conditional-access denial, or mailbox/storage policy issue.
- Repeated crashes, corrupted files, or sync conflicts involving irreplaceable data.

## Standard ticket evidence

- Employee/device, application/platform/version, timestamp/time zone, business impact, and exact error.
- Web-versus-desktop result, service-health status, network/VPN state, and scope of affected users/items.
- File or site path only through an approved secure channel; do not expose confidential filenames publicly.
- Safe troubleshooting completed and sanitized screenshots. Never include passwords, MFA codes, access tokens, or confidential message/file content.
