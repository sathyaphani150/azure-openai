# Software Installation and Update Runbook

Purpose: install and maintain approved business software without bypassing licensing, administrator, endpoint-security, or data-protection controls.

## Before installation

- Confirm the software is listed in the managed company portal or explicitly approved by IT/security.
- Verify publisher, package name, requested version, business owner, license entitlement, and operating-system compatibility.
- Save work, connect to stable power/network, and confirm adequate free storage.
- Obtain installers only from the managed portal or an IT-approved publisher location.
- Do not disable antivirus, application control, firewall, browser protection, or device management to make an installer run.

## Choose the condition

- Not listed or blocked: approval, security, or licensing decision is required.
- Download fails: portal, proxy, storage, or network issue.
- Installation fails: package, permissions, prerequisites, conflict, or disk space.
- Application installs but will not launch: compatibility, dependency, profile, or license activation.
- Update fails: running processes, damaged install, storage, policy, or service issue.

---PAGE---
# Download, Permission, and Installation Failures

## Package does not download

- Confirm internet/VPN state required by the managed portal and verify other portal items load.
- Check free disk space and retry once after restarting the portal/client.
- Record package/version, timestamp, progress percentage, and exact message.
- Do not use a public mirror, file-sharing site, personal cloud storage, or another employee's installer.

## Administrator permission or access denied

Common errors: "Administrator privileges required," "Access denied," or `0x80070005`.

- Standard employees must not use another person's administrator credential or bypass elevation.
- Request installation through the approved portal or IT elevation process with business justification.
- If an approved managed installation reports access denied, capture the error; policy assignment or endpoint-management health may require IT.

## Generic installer failure

Common examples include Windows Installer error 1603, package failed, prerequisite missing, another installation in progress, or insufficient disk space.

- Restart the device to clear a pending installer and retry once from the approved source.
- Close the affected application and save work before retrying an update.
- Confirm supported operating-system version, architecture, storage, and required reboot status.
- Do not manually delete installer caches, edit the registry, or download random runtime libraries.
- For error 1603, record the package and installation stage; the code is generic and does not identify one cause by itself.

---PAGE---
# Launch, License, Update, and Reinstall

## Installed application will not launch

- Restart the device and launch from the official installed shortcut.
- Record whether nothing happens, the application crashes, or an error appears.
- Check whether the issue affects all users or only one profile when IT can safely test that distinction.
- Verify the application is supported on the current OS and not blocked by endpoint security.
- Do not add exclusions or run unknown compatibility scripts.

## License or activation failure

- Confirm the employee is signed in with the approved organizational account and has a documented license assignment.
- Record the product, edition, tenant/account shown without exposing identifiers unnecessarily, and exact activation error.
- A license error requires the software owner or IT; reinstalling repeatedly rarely creates entitlement.

## Update failure

- Save work, close the application, restart, and retry through the managed updater.
- Confirm power, network, VPN if required, and free storage.
- If an update is known to affect multiple devices, pause repeated attempts and report a potential deployment incident.
- Never downgrade security software or apply an unofficial patch.

## Safe uninstall and reinstall

- Confirm local projects, templates, plug-ins, settings, and unsynchronized files are backed up or documented.
- Use the managed portal or operating system's approved uninstall path.
- Restart if requested, reinstall from the approved source, then restore only trusted compatible settings.
- Do not uninstall security, management, encryption, VPN, or business-critical agents without explicit IT authorization.

---PAGE---
# Software Verification and Escalation

## Resolution checks

- The installed publisher/version matches the approved request.
- The application launches under the employee account and performs the original business task.
- Licensing is active, updates report current, and no security control was disabled.
- A reboot does not reintroduce the failure.

## Contact IT immediately

- Security software flags the installer, the signature/publisher is unexpected, or the source appears compromised.
- The request involves privileged, security, encryption, VPN, device-management, or unsupported software.
- Business data may have been lost, the installer causes crashes, or multiple devices fail after the same deployment.

## Standard ticket evidence

- Device/OS, application name, publisher, version, source, business justification, and license status.
- Exact error/code, timestamp, installation stage, available storage, and whether restart was completed.
- Whether the application previously worked and recent updates or configuration changes.
- Sanitized screenshot and approved installer/log reference. Logs should be uploaded only through an approved channel.

