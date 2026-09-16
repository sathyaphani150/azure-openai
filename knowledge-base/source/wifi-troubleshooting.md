# Wi-Fi Troubleshooting Runbook

Purpose: distinguish device, wireless, internet, DNS, captive-portal, and corporate-authentication failures. This guide does not authorize changes to corporate access points, routers, certificates, or security controls.

## Rapid triage

- Record location, network name, device name, operating system, exact message, and start time.
- Determine scope: one device, all devices, one room, one access point area, or the whole site.
- Confirm Wi-Fi is enabled and airplane mode is disabled. Check any approved hardware wireless switch or function key.
- Compare a second approved device only if doing so does not expose credentials.
- Never join a look-alike network. Verify the expected SSID through an approved company source.

## Choose the symptom

- No networks listed: focus on radio, airplane mode, adapter, or driver state.
- Network listed but connection fails: focus on credentials, profile, signal, or enterprise authentication.
- Connected with no internet: focus on captive portal, address assignment, gateway, DNS, or outage.
- Internet works but is slow or unstable: focus on signal, congestion, interference, roaming, or bandwidth use.

---PAGE---
# Wi-Fi Discovery and Connection Failures

## No wireless networks appear

- Toggle Wi-Fi off, wait ten seconds, and turn it back on.
- Move to an area where the approved network is normally available.
- Restart the laptop. If the wireless adapter is missing or has a warning in operating-system settings, capture the status and contact IT.
- Do not install drivers from search results or third-party update utilities. Use company management or manufacturer packages approved by IT.
- If every device sees no network in one location, report the site/room and do not restart corporate access points.

## Cannot connect to a listed network

Common messages: "Can't connect to this network," "Unable to join," "Authentication failed," or repeated credential prompts.

- Verify signal is adequate and the SSID is exact.
- For a saved profile that recently changed, use the operating system's Forget action and reconnect only if the employee knows the approved connection process.
- For corporate 802.1X Wi-Fi, do not accept a new or unexpected certificate issuer. Capture the certificate prompt and contact IT.
- Stop repeated password attempts to avoid lockout. Never ask another employee for their credentials.
- Success on a personal hotspot but not corporate Wi-Fi suggests profile, certificate, access-point, or account policy—not necessarily a damaged adapter.

## Guest or public captive portal

- Open a browser to a normal HTTP test page or the network's documented sign-in page.
- Read the network terms and verify the portal branding/domain before submitting permitted details.
- Disconnect from VPN temporarily only if corporate policy allows completing the portal first; reconnect VPN before corporate work.
- Never install a certificate, profile, or executable offered by an unknown public hotspot.

---PAGE---
# Connected Without Internet, Slow, or Unstable

## Connected but no internet

- Check whether the Wi-Fi icon reports No internet, Self-assigned address, or Limited connectivity.
- Disconnect and reconnect once. Restart the device if address assignment does not recover.
- Test an approved site by hostname. If one site fails, the site may be unavailable; if all names fail, DNS or upstream connectivity may be involved.
- On Windows, `ipconfig /all` is a read-only command that can help IT inspect address, gateway, and DNS configuration. Do not post its full output publicly because it contains network identifiers.
- Do not manually assign an IP address, gateway, proxy, or DNS server unless IT supplies approved values.

## Slow Wi-Fi

- Check signal strength and move closer to the approved access point.
- Pause large downloads, backups, updates, and streaming, then retest the affected business application.
- Compare performance at another location and time. Record whether slowness affects one application or all internet traffic.
- Bluetooth devices, microwaves, dense meeting rooms, and neighboring networks can contribute to interference; do not change corporate radio channels yourself.

## Frequent disconnection

- Prevent sleep during one controlled test and note the exact disconnect times.
- Disable neither endpoint security nor corporate network profiles.
- If disconnections occur only while moving, record the route/rooms; roaming configuration may require network-team investigation.
- If only a dock or USB wireless adapter is affected, reconnect it and test without the dock when practical.

---PAGE---
# Wi-Fi Verification and Escalation

## Resolution checks

- The device reconnects after Wi-Fi is toggled off and on.
- It receives network connectivity without a warning and opens two approved sites.
- The original business application works for at least ten minutes without disconnecting.
- Corporate Wi-Fi shows the expected identity/certificate behavior.

## Contact IT immediately

- An unexpected enterprise certificate, credential-harvesting page, or suspicious look-alike SSID appears.
- Multiple devices or an entire office area are affected.
- The adapter is missing, disabled by policy, or repeatedly fails after reboot.
- A company-managed device is asked to weaken encryption or install unknown software.

## Standard ticket evidence

- Device name/asset tag, operating system, location/room, network name, time, and exact error.
- Signal level, whether other devices work, and whether wired or another approved network works.
- Whether the failure is discovery, authentication, no internet, DNS/site-specific, slow, or intermittent.
- Safe steps attempted and a sanitized screenshot.

Never include wireless passwords, certificate private keys, full network dumps, or personal hotspot credentials in a ticket.
