# Threat Model Report

**Generated:** 2026-05-29T14:32:18.442Z
**Model:** us.anthropic.claude-sonnet-4-20250514-v1:0
**Provider:** bedrock

## Summary

Threat model for system with 11 assets, 14 data flows, and 18 identified threats.

## Assets

| # | Asset | Type | Trust Boundary | Description |
|---|-------|------|----------------|-------------|
| 1 | React SPA | web_app | Public Internet | Single page application serving the e-commerce storefront to end users |
| 2 | CloudFront CDN | cdn | Public Internet | Content delivery network caching static assets and routing requests |
| 3 | API Gateway | api | DMZ | REST API gateway handling request routing, rate limiting, and API key validation |
| 4 | Keycloak | identity_provider | DMZ | OpenID Connect identity provider managing user authentication and JWT issuance |
| 5 | Order Service | container | Internal Network | Node.js microservice handling order creation, updates, and fulfillment |
| 6 | Payment Service | container | Internal Network | Java microservice processing payments via Stripe, PCI DSS compliant |
| 7 | Product Catalog Service | serverless_function | Internal Network | Python FastAPI Lambda serving product data and search |
| 8 | PostgreSQL (RDS) | database | Data Layer | Relational database storing orders, users, and transaction data |
| 9 | Redis Cache | cache | Internal Network | ElastiCache cluster for session management and product catalog caching |
| 10 | S3 Bucket | storage | Internal Network | Object storage for product images and static assets |
| 11 | SQS Queue | message_queue | Internal Network | Async message queue for order processing pipeline |

## Data Flows

| Source | Target | Description | Protocol | Encrypted |
|--------|--------|-------------|----------|-----------|
| React SPA | CloudFront CDN | Static asset requests and API calls | HTTPS | ✓ |
| CloudFront CDN | API Gateway | Proxied API requests with origin authentication | HTTPS | ✓ |
| React SPA | Keycloak | OAuth2 authorization code flow for user login | HTTPS | ✓ |
| API Gateway | Order Service | Order CRUD operations with JWT validation | HTTPS | ✓ |
| API Gateway | Product Catalog Service | Product queries and search requests | HTTPS | ✓ |
| Order Service | PostgreSQL (RDS) | Order data persistence and retrieval | TLS/TCP | ✓ |
| Order Service | SQS Queue | Async order events for downstream processing | HTTPS | ✓ |
| Order Service | Payment Service | Payment initiation requests | gRPC/mTLS | ✓ |
| Payment Service | PostgreSQL (RDS) | Transaction records and payment status | TLS/TCP | ✓ |
| Payment Service | Stripe API | Payment processing via external gateway | HTTPS | ✓ |
| Product Catalog Service | Redis Cache | Cached product data reads/writes | TLS/TCP | ✓ |
| Product Catalog Service | S3 Bucket | Product image URL generation | HTTPS | ✓ |
| Keycloak | PostgreSQL (RDS) | User credentials and session storage | TLS/TCP | ✓ |
| Redis Cache | Order Service | Session validation tokens | TLS/TCP | ✓ |

## Threat Catalog

**Total threats identified:** 18

### 🔴 Critical Risk (2)

#### [1] SQL Injection in Order Service Database Queries

- **STRIDE:** Tampering
- **Target:** Order Service
- **Impact:** High | **Likelihood:** High
- **Attack Vector:** Attacker crafts malicious input in order fields (product IDs, quantities, addresses) that gets interpolated into SQL queries without parameterization
- **CWE:** CWE-89

If the Order Service constructs SQL queries using string concatenation with user-supplied input, an attacker could extract all customer data, modify orders, or drop tables. Given the service handles financial transactions, this could lead to massive data breach and financial fraud.

**Mitigations:**
- Use parameterized queries (prepared statements) for all database operations in the Order Service
- Implement input validation with strict type checking and length limits on all order fields
- Deploy a Web Application Firewall (WAF) rule to detect and block SQL injection patterns
- Enable PostgreSQL audit logging to detect anomalous query patterns

#### [2] Credential Stuffing Against Keycloak Authentication

- **STRIDE:** Spoofing
- **Target:** Keycloak
- **Impact:** High | **Likelihood:** High
- **Attack Vector:** Attacker uses leaked credential databases from other breaches to attempt automated login against the Keycloak authentication endpoint
- **CWE:** CWE-307

With billions of leaked credentials available, automated attacks against the login endpoint could compromise customer accounts. Successful account takeover enables fraudulent orders, payment theft, and access to personal data.

**Mitigations:**
- Implement progressive rate limiting (exponential backoff) on failed login attempts per IP and per account
- Enable multi-factor authentication (MFA) for all user accounts
- Integrate a breached password detection service (e.g., HaveIBeenPwned API) during registration and login
- Deploy CAPTCHA after 3 consecutive failed login attempts

### 🟠 High Risk (5)

#### [3] JWT Token Manipulation for Privilege Escalation

- **STRIDE:** Elevation of Privilege
- **Target:** API Gateway
- **Impact:** High | **Likelihood:** Medium
- **Attack Vector:** Attacker modifies JWT claims (role, user_id) or exploits weak signature validation to escalate from regular user to admin
- **CWE:** CWE-287

If the API Gateway or downstream services don't properly validate JWT signatures or rely on client-supplied claims without verification, an attacker could forge tokens granting admin access to order management, user data, or system configuration.

**Mitigations:**
- Validate JWT signatures using RS256 with key rotation on every request at the API Gateway level
- Implement claim validation (issuer, audience, expiration) in each microservice independently
- Never trust client-supplied role claims — always resolve permissions from the identity provider
- Implement short-lived tokens (5-15 minutes) with refresh token rotation

#### [4] Payment Data Interception via Man-in-the-Middle

- **STRIDE:** Information Disclosure
- **Target:** Payment Service
- **Impact:** High | **Likelihood:** Medium
- **Attack Vector:** Attacker intercepts communication between Payment Service and Stripe API by compromising network infrastructure or DNS
- **CWE:** CWE-319

If TLS certificate validation is improperly configured or certificate pinning is not implemented, an attacker positioned on the network could intercept payment card data in transit, violating PCI DSS requirements.

**Mitigations:**
- Implement certificate pinning for the Stripe API endpoint in the Payment Service
- Use Stripe's tokenization (Stripe.js) so card numbers never reach your backend
- Enable TLS 1.3 with strong cipher suites for all external API calls
- Monitor for certificate transparency log anomalies

#### [5] Server-Side Request Forgery (SSRF) in Product Catalog

- **STRIDE:** Tampering
- **Target:** Product Catalog Service
- **Impact:** High | **Likelihood:** Medium
- **Attack Vector:** Attacker manipulates product image URLs or search parameters to make the Lambda function issue requests to internal AWS metadata endpoints or other services
- **CWE:** CWE-918

If the Product Catalog Service fetches resources based on user-supplied URLs (e.g., product image validation), an attacker could access the Lambda execution role credentials via the metadata service (169.254.169.254) or probe internal services.

**Mitigations:**
- Implement URL allowlisting — only permit requests to known S3 bucket domains
- Block access to AWS metadata endpoint (169.254.169.254) via Lambda security group or IMDSv2
- Validate and sanitize all URL inputs with strict schema and domain checks
- Use IMDSv2 (token-required) to prevent SSRF-based credential theft

#### [6] Denial of Service via API Gateway Rate Limit Bypass

- **STRIDE:** Denial of Service
- **Target:** API Gateway
- **Impact:** High | **Likelihood:** Medium
- **Attack Vector:** Attacker distributes requests across many IPs to bypass per-IP rate limits, overwhelming backend services
- **CWE:** CWE-770

Distributed attacks from botnets can exhaust API Gateway throttling limits and overwhelm downstream microservices, causing service unavailability during peak shopping periods.

**Mitigations:**
- Implement multi-layer rate limiting: per-IP, per-user, and per-endpoint with different thresholds
- Deploy AWS WAF with rate-based rules and geographic restrictions
- Configure auto-scaling for backend services with circuit breakers
- Implement request queuing with SQS to absorb traffic spikes

#### [7] Session Hijacking via Redis Cache Compromise

- **STRIDE:** Spoofing
- **Target:** Redis Cache
- **Impact:** High | **Likelihood:** Medium
- **Attack Vector:** Attacker exploits Redis misconfiguration or network access to read session tokens stored in cache
- **CWE:** CWE-384

If Redis is accessible without authentication or with weak passwords, an attacker on the internal network could dump all active session tokens and impersonate any logged-in user.

**Mitigations:**
- Enable Redis AUTH with strong passwords rotated via AWS Secrets Manager
- Restrict Redis security group to only allow connections from authorized services
- Enable encryption in-transit (TLS) for ElastiCache Redis
- Implement session token binding to client fingerprint (IP + User-Agent hash)

### 🟡 Medium Risk (7)

#### [8] Cross-Site Scripting (XSS) in React SPA

- **STRIDE:** Tampering
- **Target:** React SPA
- **Impact:** Medium | **Likelihood:** Medium
- **Attack Vector:** Attacker injects malicious JavaScript via product reviews, search queries, or user profile fields that gets rendered without sanitization
- **CWE:** CWE-79

Stored or reflected XSS could steal session tokens, redirect users to phishing pages, or modify displayed prices and product information.

**Mitigations:**
- Use React's built-in JSX escaping and avoid dangerouslySetInnerHTML
- Implement Content Security Policy (CSP) headers blocking inline scripts
- Sanitize all user-generated content server-side before storage
- Deploy DOMPurify for any HTML rendering requirements

#### [9] Insecure Direct Object Reference in Order API

- **STRIDE:** Information Disclosure
- **Target:** Order Service
- **Impact:** Medium | **Likelihood:** Medium
- **Attack Vector:** Attacker modifies order IDs in API requests to access other customers' order details
- **CWE:** CWE-639

If the Order Service only checks authentication but not authorization per resource, any authenticated user could enumerate and view other users' orders, addresses, and payment history.

**Mitigations:**
- Implement resource-level authorization checking order ownership against the authenticated user
- Use UUIDs instead of sequential IDs to prevent enumeration
- Add row-level security policies in PostgreSQL
- Log and alert on access patterns indicating IDOR attempts

#### [10] Message Tampering in SQS Order Queue

- **STRIDE:** Tampering
- **Target:** SQS Queue
- **Impact:** Medium | **Likelihood:** Low
- **Attack Vector:** Attacker with compromised IAM credentials publishes fraudulent order messages to the SQS queue
- **CWE:** CWE-345

If SQS queue policies are overly permissive, a compromised service could inject fake order completion messages, triggering fulfillment without payment.

**Mitigations:**
- Restrict SQS SendMessage permissions to only the Order Service IAM role
- Implement message signing/verification using HMAC before processing
- Add message schema validation in the consumer before acting on messages
- Enable SQS dead-letter queue for rejected/malformed messages

#### [11] CloudFront Cache Poisoning

- **STRIDE:** Tampering
- **Target:** CloudFront CDN
- **Impact:** Medium | **Likelihood:** Low
- **Attack Vector:** Attacker manipulates cache keys via Host header injection or query parameter pollution to serve malicious content to other users
- **CWE:** CWE-444

If CloudFront caches responses based on manipulable headers, an attacker could poison the cache with modified JavaScript or HTML, affecting all users served from that edge location.

**Mitigations:**
- Configure CloudFront to use a strict cache key policy (only approved headers/query params)
- Implement origin request signing to prevent unauthorized cache population
- Enable CloudFront access logs and monitor for anomalous cache hit patterns
- Use Subresource Integrity (SRI) hashes for all JavaScript assets

#### [12] Insufficient Logging in Payment Service

- **STRIDE:** Repudiation
- **Target:** Payment Service
- **Impact:** Medium | **Likelihood:** Medium
- **Attack Vector:** Attacker performs fraudulent transactions and disputes them, with insufficient audit trail to prove the transaction was legitimate
- **CWE:** CWE-778

Without comprehensive logging of payment operations, the organization cannot prove transaction legitimacy during chargebacks or fraud investigations, leading to financial losses.

**Mitigations:**
- Log all payment operations with immutable audit trail (timestamp, user, amount, Stripe ID, IP)
- Store logs in append-only storage (S3 with Object Lock) to prevent tampering
- Implement log integrity verification using hash chains
- Retain payment logs for minimum 7 years per PCI DSS requirements

#### [13] S3 Bucket Misconfiguration Exposing Product Data

- **STRIDE:** Information Disclosure
- **Target:** S3 Bucket
- **Impact:** Medium | **Likelihood:** Low
- **Attack Vector:** Misconfigured bucket policy or ACL allows public access to internal product data, pricing strategies, or unreleased product images
- **CWE:** CWE-732

If S3 bucket policies are overly permissive or public access block is disabled, sensitive business data could be exposed to competitors or the public.

**Mitigations:**
- Enable S3 Block Public Access at the account level
- Use pre-signed URLs with short expiration for all object access
- Implement S3 bucket policies with explicit deny for public access
- Enable AWS Config rules to detect and auto-remediate public bucket configurations

#### [14] Unvalidated Redirect in OAuth2 Flow

- **STRIDE:** Spoofing
- **Target:** Keycloak
- **Impact:** Medium | **Likelihood:** Low
- **Attack Vector:** Attacker manipulates the redirect_uri parameter in the OAuth2 authorization request to redirect tokens to an attacker-controlled domain
- **CWE:** CWE-601

If Keycloak doesn't strictly validate redirect URIs against a whitelist, an attacker could steal authorization codes or tokens by redirecting the OAuth2 callback to their server.

**Mitigations:**
- Configure exact redirect URI matching in Keycloak (no wildcards)
- Validate redirect_uri on both authorization and token endpoints
- Implement PKCE (Proof Key for Code Exchange) for all OAuth2 flows
- Monitor for redirect_uri parameter tampering in access logs

### 🟢 Low Risk (3)

#### [15] DNS Rebinding Against Internal Services

- **STRIDE:** Elevation of Privilege
- **Target:** Product Catalog Service
- **Impact:** Low | **Likelihood:** Low
- **Attack Vector:** Attacker uses DNS rebinding to make the user's browser send requests to internal service endpoints
- **CWE:** CWE-350

If internal services don't validate the Host header, a DNS rebinding attack could allow an attacker to access internal APIs through the victim's browser.

**Mitigations:**
- Validate Host headers in all internal services
- Implement network segmentation preventing browser-accessible services from reaching internal APIs
- Use private DNS zones for internal service discovery

#### [16] Information Leakage via Error Messages

- **STRIDE:** Information Disclosure
- **Target:** API Gateway
- **Impact:** Low | **Likelihood:** Medium
- **Attack Vector:** Attacker triggers errors to extract stack traces, database schema details, or internal service topology from verbose error responses
- **CWE:** CWE-209

Detailed error messages in production can reveal internal architecture, library versions, and database structure that aids further attacks.

**Mitigations:**
- Return generic error messages to clients (e.g., "Internal Server Error") without stack traces
- Log detailed errors server-side only with correlation IDs for debugging
- Implement custom error handlers in each microservice that sanitize responses

#### [17] Timing Attack on Authentication Endpoint

- **STRIDE:** Information Disclosure
- **Target:** Keycloak
- **Impact:** Low | **Likelihood:** Low
- **Attack Vector:** Attacker measures response time differences between valid and invalid usernames to enumerate existing accounts
- **CWE:** CWE-208

If the authentication endpoint responds faster for non-existent users than for users with wrong passwords, an attacker can enumerate valid accounts for targeted attacks.

**Mitigations:**
- Implement constant-time comparison for credential validation
- Return identical response times and messages for both valid and invalid usernames
- Add random delay jitter to authentication responses

### ⚪ Minimal Risk (1)

#### [18] Clickjacking on React SPA

- **STRIDE:** Tampering
- **Target:** React SPA
- **Impact:** Low | **Likelihood:** Low
- **Attack Vector:** Attacker embeds the application in a hidden iframe on a malicious site to trick users into performing unintended actions
- **CWE:** CWE-1021

While modern browsers provide some protection, clickjacking could trick users into confirming orders or changing account settings.

**Mitigations:**
- Set X-Frame-Options: DENY header on all responses
- Implement Content-Security-Policy frame-ancestors 'none' directive
- Use JavaScript frame-busting as a defense-in-depth measure

## STRIDE Distribution

| Category | Count |
|----------|-------|
| Spoofing | 4 |
| Tampering | 5 |
| Repudiation | 1 |
| Information Disclosure | 4 |
| Denial of Service | 1 |
| Elevation of Privilege | 3 |
