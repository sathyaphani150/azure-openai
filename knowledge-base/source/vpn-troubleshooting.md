# VPN Troubleshooting Runbook

Purpose: diagnose remote-access VPN failures without weakening security controls. This runbook applies to a company-managed device using an approved VPN client. Names of gateways, profiles, and support contacts must come from the employee's approved company portal.

## Rapid triage

- Record the exact error, time, device name, operating system, VPN client version, and network type.
- Confirm ordinary internet access by opening two trusted public sites. If neither opens, troubleshoot the local network before the VPN.
- Confirm date, time, and time zone are correct. Large clock differences can invalidate certificates and tokens.
- Check the approved status page or service notice. Do not repeatedly reconnect during a known outage.
- Determine scope: one user, one device, one network, or multiple employees. Scope changes the likely cause.

## Security stop conditions

- Never share passwords, MFA codes, recovery codes, certificates, private keys, or session tokens.
- Deny and report an MFA prompt that the employee did not initiate.
- Stop and contact IT for certificate warnings, an unrecognized VPN profile, suspected account compromise, or instructions to disable firewall or endpoint protection.

---PAGE---
# VPN Connection and Authentication Failures

## Cannot reach the VPN gateway

Common messages: "VPN server unavailable," "Gateway not responding," "The network connection could not be established," or Windows error 809.

- Verify public internet access and then close and reopen the approved VPN client.
- Switch once between wired and trusted Wi-Fi, if available. Success on one network suggests local router, captive portal, or ISP filtering.
- Complete any hotel, airport, or guest-network captive portal in a browser before starting VPN. Avoid sensitive work on untrusted networks.
- Restart the laptop. Do not change router port-forwarding, registry, firewall, DNS, or VPN protocol settings unless IT provides an approved procedure.
- If several employees fail at the same time, treat it as a possible service incident and escalate rather than reinstalling clients.

## Credentials rejected or sign-in loops

Common messages: "Authentication failed," "Credentials rejected," "Account locked," error 691, or repeated sign-in prompts.

- Confirm the user can sign in to the approved company identity portal. Never test a password on an unfamiliar site.
- After a recent password change, fully exit the VPN client and sign in with the new password. Reboot if old credentials remain cached.
- Stop after a small number of careful attempts. Repeated failures can extend an account lockout.
- Approve only an MFA prompt initiated by the current VPN sign-in. Check that the authenticator device has internet access and correct time.
- If web sign-in succeeds but VPN authentication fails, capture the VPN error and contact IT; VPN access, group membership, device compliance, or profile assignment may require administrator review.

## Certificate or compliance failure

Messages may mention certificate expired, certificate not trusted, device not compliant, conditional access, or access denied by policy.

- Confirm system time and install pending approved operating-system updates if permitted.
- Connect the device to the internet long enough for management policy to synchronize, then retry once.
- Do not bypass certificate validation, install a certificate sent through chat, or remove device-management software.
- Escalate with the certificate subject/expiry date or compliance message, but never export a private key.

---PAGE---
# VPN Connected but Work Resources Fail

## Tunnel connects but internal sites do not open

- Verify the VPN client explicitly shows Connected and note the assigned connection time.
- Try two known internal resources. One failing resource suggests that service; all internal resources failing suggests routing, DNS, authorization, or tunnel policy.
- Use the full approved internal hostname rather than a saved shortcut. Do not guess internal server addresses.
- Disconnect once, wait 30 seconds, and reconnect. If failure persists, capture the internal hostname, browser message, and whether public sites still work.
- Do not run copied network-reset scripts or change DNS servers without IT approval.

## File share, remote desktop, or application unavailable

- Confirm the specific application is approved for remote access and that the target system is expected to be online.
- Record whether the message is timeout, name not found, access denied, or credentials rejected; each points to a different layer.
- An access-denied response after the VPN connects is normally an authorization issue, not proof that the tunnel failed.
- For remote desktop, confirm the destination name came from an approved source. Do not expose remote desktop directly to the internet.

## Slow VPN or frequent disconnection

- Compare internet stability without VPN. Packet loss, weak Wi-Fi, roaming between access points, or laptop sleep can drop the tunnel.
- Move closer to the access point, pause large downloads and cloud synchronization, and keep the laptop awake during one test.
- If permitted, test a wired connection. Record the approximate disconnect interval and whether calls, all traffic, or only one application is affected.
- Do not use consumer "VPN optimizer" software or an unapproved personal VPN at the same time.

---PAGE---
# VPN Verification and Escalation

## Resolution checks

- The client remains Connected for at least ten minutes on a stable network.
- The employee can open an approved internal resource and complete the original task.
- No certificate warning, unexpected MFA prompt, or repeated credential request appears.
- Disconnect and reconnect once to confirm the resolution persists.

## Contact IT immediately

- Unexpected MFA prompts, suspected credential theft, an unknown profile, or a certificate/private-key warning.
- Multiple employees are affected or a business-critical service is unavailable.
- The client reports account disabled, device blocked, compliance failure, or access denied by policy.
- The VPN causes a crash, blue screen, or loss of network connectivity after reboot.

## Standard ticket evidence

- Employee contact, device name/asset tag, operating system, VPN client version, and connection type.
- Exact error text/code and timestamp with time zone.
- Whether public internet works, whether identity-portal sign-in works, and whether other employees are affected.
- Internal resource names affected and safe steps already attempted.
- A sanitized screenshot with passwords, tokens, email content, and confidential data removed.

Do not attach VPN diagnostic bundles unless IT requests them through an approved secure channel; logs can contain internal addresses and identifiers.

