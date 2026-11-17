# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

Older versions are not supported. Upgrade to the latest 0.1.x release.

## Reporting a vulnerability

Report suspected vulnerabilities privately by email to
[nickejanssen@gmail.com](mailto:nickejanssen@gmail.com). Do not open a public
issue for a security report.

Please include enough detail to reproduce the issue. You will get an
acknowledgement, and we follow a 90-day coordinated disclosure window: the
report stays private until a fix ships or 90 days pass, whichever comes first.

## Attack surface

The framework runs no services and makes no model calls. Its attack surface is
limited to local file generation and the scripts it ships. There is no server,
no network listener, and no credential handling in the framework itself.
