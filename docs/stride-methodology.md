# STRIDE Threat Modeling Methodology

## What is STRIDE?

STRIDE is a threat classification model developed by Microsoft for identifying security threats in system architectures. Each letter represents a category of threat:

| Category | Description | Security Property Violated |
|----------|-------------|---------------------------|
| **S**poofing | Pretending to be someone/something else | Authentication |
| **T**ampering | Modifying data or code without authorization | Integrity |
| **R**epudiation | Denying having performed an action | Non-repudiation |
| **I**nformation Disclosure | Exposing data to unauthorized parties | Confidentiality |
| **D**enial of Service | Making a system unavailable | Availability |
| **E**levation of Privilege | Gaining unauthorized access levels | Authorization |

## How AITM Applies STRIDE

### Per-Asset Analysis

Each identified asset is analyzed against all 6 STRIDE categories:

- **Web Application** → Spoofing (session hijacking), XSS (Tampering), CSRF
- **API Endpoint** → Injection (Tampering), broken auth (Spoofing), rate limiting (DoS)
- **Database** → SQL injection (Tampering), data leakage (Info Disclosure)
- **Message Queue** → Message tampering, unauthorized publish (EoP)

### Per-Flow Analysis

Data flows crossing trust boundaries get additional scrutiny:

- **Unencrypted flows** → Information Disclosure
- **Unauthenticated flows** → Spoofing
- **Flows without integrity checks** → Tampering

## Risk Scoring

Each threat is scored using a simplified risk matrix:

```
Risk = Impact × Likelihood

Impact:    High | Medium | Low
Likelihood: High | Medium | Low
```

| | High Impact | Medium Impact | Low Impact |
|---|---|---|---|
| **High Likelihood** | Critical | High | Medium |
| **Medium Likelihood** | High | Medium | Low |
| **Low Likelihood** | Medium | Low | Minimal |

## References

- [Microsoft STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
