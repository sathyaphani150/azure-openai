# IT Support Policy - POC Control Document

Status: demonstration policy. Replace bracketed organization-specific fields and obtain policy-owner approval before production use. The assistant must never present unapproved demo values as real company policy.

## Supported scope

- Company-managed laptops and approved operating-system versions.
- Approved VPN, browsers, Microsoft 365, identity/MFA, wireless access, and applications in the managed software portal.
- Company-owned peripherals and docks where asset records exist.
- Personally owned devices receive only the limited assistance defined by the real organization policy; the POC does not invent BYOD authorization.
- Unlicensed, unapproved, end-of-life, or personally installed software is not supported and may require security review.

## Support channels and hours

- Standard hours: `[CONFIGURE APPROVED BUSINESS HOURS AND TIME ZONE]`.
- Approved ticket portal: `[CONFIGURE APPROVED PORTAL]`.
- Approved urgent/security channel: `[CONFIGURE APPROVED CHANNEL]`.
- Do not put a guessed phone number, email address, SLA, or office location in an AI response.
- Outside approved hours, follow the organization's documented on-call process. If none is configured, state that the channel is unknown rather than inventing one.

---PAGE---
# Priority, Impact, and Escalation Policy

## Suggested triage levels for POC demonstration

- Critical: active security compromise, widespread business-critical outage, safety hazard, or loss of access affecting essential operations. Escalate immediately through the configured urgent channel.
- High: multiple employees blocked, executive/critical-function impact, repeated device crashes, or important data at risk. Escalate promptly according to the approved SLA.
- Normal: one employee has a workaround or a non-critical application/device issue. Handle through the standard queue.
- Request: software access, installation, information, or a planned change. Route through the approved request/approval process.

These labels do not establish response-time commitments. Production priority definitions and SLAs must come from the organization.

## Immediate escalation triggers

- Unexpected MFA prompts, phishing, malware alert, exposed credentials/token, suspicious account change, or lost/stolen managed device.
- Smoke, burning smell, sparks, swollen battery, liquid damage, or electrical hazard.
- Multiple employees or a site are affected by network, VPN, identity, or Microsoft 365 failure.
- Data loss, encryption recovery, missing boot device, or corruption of irreplaceable business files.
- A request to bypass security, licensing, administrator, retention, or access controls.

## Escalation boundaries

- The AI assistant can propose safe user-level checks but cannot approve access, software, policy exceptions, data deletion, or security-control changes.
- Access denied, device non-compliance, license assignment, and account disablement require authorized staff.
- The employee should stop when instructions require privileged credentials, destructive recovery, disassembly, or disabling protection.

---PAGE---
# Identity, Software, Device, and Data Rules

## Password and MFA

- Never request or record passwords, MFA codes, recovery codes, authenticator QR codes, private keys, or access tokens.
- Employees approve only authentication prompts they initiate.
- Identity recovery must use approved verification and reset channels.
- Unexpected prompts or recovery-detail changes are security incidents, not routine password tickets.

## Approved software

- Install only licensed software from the managed portal or an explicitly approved publisher source.
- Administrator elevation follows the organization's approved process; employees must not share admin credentials or bypass controls.
- Security, encryption, VPN, device-management, and monitoring agents may not be disabled or removed without authorization.
- Software requests include business justification, owner, licensing need, data sensitivity, and compatibility information.

## Device support

- Employees protect company devices from loss, theft, liquid, extreme temperature, and unauthorized repair.
- Hardware safety symptoms require shutdown and escalation, not continued troubleshooting.
- Recovery keys and diagnostic packages use approved secure channels.

## Data protection

- Tickets and screenshots must contain only information necessary to diagnose the issue.
- Remove passwords, tokens, personal data, confidential messages, customer data, and unrelated screen content.
- Preserve unsynchronized files and conflicting copies before repair, reset, unlink, uninstall, or profile recreation.
- Follow the real retention and incident-response policy; the POC does not authorize deletion.

---PAGE---
# Ticket Quality and Resolution Standards

## Information required when raising a ticket

- Employee contact and preferred approved contact method.
- Device name, asset tag, operating system, application/version, and location/network type.
- Clear symptom, exact error text/code, start time with time zone, frequency, and business impact.
- Scope: one item, one application, one user/device, multiple employees, site-wide, or organization-wide.
- Last known working time and relevant recent changes such as password, update, network, device, or software change.
- Safe troubleshooting already performed and its result.
- Sanitized screenshots or logs only when necessary and transferred through an approved channel.

## Definition of resolved

- The employee can repeat the original business task successfully.
- The result persists after the relevant reconnect/restart when safe.
- No security control was weakened and no important data remains unsynchronized or at risk.
- Root cause or most likely cause, remediation, verification, and any follow-up are recorded.
- The employee knows how to reopen/escalate if symptoms return.

## Assistant response rules

- Cite the controlling knowledge-base pages.
- Separate observed facts from hypotheses.
- Prefer reversible, user-level steps before disruptive action.
- State when information is unavailable or organization-specific.
- Escalate rather than inventing policy, credentials, internal hostnames, contact details, or administrator procedures.
