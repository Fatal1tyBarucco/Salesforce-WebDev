# Security Policy

## Supported Versions

We actively support and provide security patches for the following versions:

| Version / Branch | Supported          | Python Version |
| :--------------- | :----------------- | :------------- |
| `main`           | :white_check_mark: | `>= 3.12`      |
| `< 1.0.0`        | :x:                | —              |

---

## Reporting a Vulnerability

We take the security of `Salesforce-WebDev` seriously. If you discover a security vulnerability, we appreciate your help in disclosing it to us responsibly.

### 1. Preferred Method: Private Vulnerability Reporting

Please report security issues using **GitHub Private Vulnerability Reporting**:

1. Navigate to the repository's [Security Tab](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/security).
2. Click on **Advisories** &rarr; **Report a vulnerability** (or open [New Advisory Report](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/security/advisories/new)).
3. Provide details about the vulnerability, including:
   - Type of issue (e.g., path traversal, SSRF, secret leakage, injection).
   - Step-by-step instructions to reproduce or a Proof of Concept (PoC).
   - Potential impact and affected components.
   - Suggested mitigations (if any).

> [!IMPORTANT]
> **Please do not open public GitHub Issues or Pull Requests for suspected security vulnerabilities** until they have been reviewed and addressed.

---

## Response Timeline & Disclosure Process

When a vulnerability report is received:

1. **Acknowledgment**: We aim to acknowledge receipt within **48 hours**.
2. **Assessment & Triage**: We will investigate and confirm the severity and impact within **5 business days**.
3. **Remediation**: A fix will be developed in a private security fork/advisory branch.
4. **Coordinated Disclosure**: Once patched and released to `main`, a security advisory will be published crediting the reporter (unless anonymity is requested).

---

## Security Practices in this Repository

- **Static Application Security Testing (SAST)**: CodeQL scans are automatically executed on all pull requests and pushes to `main`.
- **Dependency Management**: Dependabot scans dependencies continuously for known CVEs.
- **Secret Scanning**: Active protection against accidental credential exposure.
- **Strict Quality Gates**: All contributions must pass `mypy --strict`, `ruff`, `black`, and full test suites with high test coverage (`pytest`).

---

## Deployment & Operational Security

When deploying this service:

- **API Keys & Secrets**: Always configure `API_SECRET_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, and webhooks via secure environment variables or secret managers—never hardcode credentials.
- **Least Privilege**: Run the ETL container with non-root privileges.
- **Network Boundaries**: Restrict access to internal metrics and admin endpoints behind authenticated reverse proxies or VPC boundaries.
