# JWT Bearer Auth Pattern (REST Connector)

## Overview

Some APIs require JWT bearer token authentication (e.g., Google service accounts, Azure AD service principals). Workato's REST connector auth types (None, Basic, Header, OAuth2) don't include JWT bearer / service account flows natively. This pattern handles JWT auth entirely within the recipe using the REST connector with auth type set to **None**.

---

## When to Use

- Google APIs with service account credentials
- Azure AD with service principal / client credentials (certificate-based)
- Any API requiring a signed JWT exchanged for an access token

---

## Pattern Steps

### 1. Build and Sign the JWT

Use `workato.jwt_encode` to construct a signed JWT:

```json
{
  "number": 1,
  "provider": "workato",
  "name": "jwt_encode_rs256",
  "as": "build_jwt",
  "keyword": "action",
  "input": {
    "payload": "={'iss' => 'service-account@project.iam.gserviceaccount.com', 'scope' => 'https://www.googleapis.com/auth/analytics.readonly', 'aud' => 'https://oauth2.googleapis.com/token', 'iat' => now.to_i, 'exp' => (now + 1.hour).to_i}.to_json",
    "algorithm": "RS256",
    "key": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"private_key_pem\"]}')}",
    "header_fields": "={'typ' => 'JWT'}.to_json"
  },
  "uuid": "build-jwt-001"
}
```

**Key points:**
- `iat` uses `now.to_i` (Unix epoch seconds)
- `exp` uses `(now + 1.hour).to_i` — do NOT use `now.utc` (`.utc` is not available on Workato's `now` object)
- The private key PEM should come from a recipe parameter or Workato account property, never hardcoded
- `algorithm` supports `RS256`, `RS384`, `RS512`, `ES256`, `ES384`, `ES512`

### 2. Exchange JWT for Access Token

POST the signed JWT to the token endpoint using `make_request_v2`. Use `content_type: "application/json"` with a manual `Content-Type` header to avoid Workato's automatic double-encoding of form bodies:

```json
{
  "number": 2,
  "provider": "rest",
  "name": "make_request_v2",
  "as": "token_request",
  "keyword": "action",
  "toggleCfg": {
    "response.ignore_http_errors": true,
    "disable_retries": true
  },
  "input": {
    "request_name": "Exchange JWT for access token",
    "request": {
      "method": "POST",
      "content_type": "application/json",
      "url": "https://oauth2.googleapis.com/token",
      "headers": [{"header": "Content-Type", "value": "application/x-www-form-urlencoded"}],
      "body": "=('grant_type=' + 'urn:ietf:params:oauth:grant-type:jwt-bearer'.encode_url + '&assertion=' + _dp('{\"pill_type\":\"output\",\"provider\":\"workato\",\"line\":\"build_jwt\",\"path\":[\"jwt\"]}'))"
    },
    "response": {
      "output_type": "json",
      "expected_encoding": "UTF-8",
      "ignore_http_errors": "false"
    },
    "wait_for_response": "true",
    "disable_retries": "false"
  },
  "extended_output_schema": [
    {
      "label": "Response",
      "name": "response",
      "optional": true,
      "type": "object",
      "properties": [
        {
          "control_type": "text",
          "label": "Access Token",
          "name": "access_token",
          "optional": true,
          "type": "string"
        },
        {
          "control_type": "text",
          "label": "Token Type",
          "name": "token_type",
          "optional": true,
          "type": "string"
        },
        {
          "control_type": "number",
          "label": "Expires In",
          "name": "expires_in",
          "optional": true,
          "type": "integer"
        }
      ]
    }
  ],
  "extended_input_schema": ["... (see adhoc-http-actions.md EIS template)"],
  "uuid": "token-request-002",
  "wizardFinished": true
}
```

**Key points:**
- Use an **absolute URL** for the token endpoint (not relative) since the REST connection's base URL will be the target API, not the OAuth server
- Do NOT use `content_type: "application/x-www-form-urlencoded"` — Workato auto-encodes the body when this content type is set, causing double-encoding of pre-encoded values. Instead use `content_type: "application/json"` with a manual `Content-Type: application/x-www-form-urlencoded` header to pass the body through raw
- Use `.encode_url` on values that need URL-encoding (e.g., the `grant_type` URN) — this gives you explicit control over encoding
- Define `extended_output_schema` to extract `access_token` via datapill path — do NOT use `.parse_json['access_token']` (bracket notation fails in formulas)

### 3. Use the Token in Subsequent API Calls

Pass the access token as a `Bearer` header on API calls:

```json
{
  "number": 3,
  "provider": "rest",
  "name": "make_request_v2",
  "as": "api_call",
  "keyword": "action",
  "toggleCfg": {
    "response.ignore_http_errors": true,
    "disable_retries": true
  },
  "input": {
    "request_name": "Call target API",
    "request": {
      "method": "GET",
      "url": "/v1/your-endpoint",
      "headers": [
        {
          "header": "Authorization",
          "value": "='Bearer ' + _dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"token_request\",\"path\":[\"response\",\"access_token\"]}')"
        }
      ]
    },
    "response": {
      "output_type": "json",
      "expected_encoding": "UTF-8",
      "ignore_http_errors": "false"
    },
    "wait_for_response": "true",
    "disable_retries": "false"
  },
  "extended_output_schema": ["... (define fields for your API response)"],
  "extended_input_schema": ["... (see adhoc-http-actions.md EIS template)"],
  "uuid": "api-call-003",
  "wizardFinished": true
}
```

**Key points:**
- The `Authorization` header uses formula mode (`=`) to concatenate `'Bearer '` with the token datapill
- The REST connection auth type should be **None** — the recipe handles auth itself
- Subsequent calls use the connection's base URL (relative path), while the token exchange used an absolute URL

---

## Connection Configuration

The REST connection should be configured with:
- **Auth type:** None (recipe manages auth via JWT)
- **Base URL:** The target API base URL (e.g., `https://analyticsdata.googleapis.com`)

```json
{
  "keyword": "application",
  "provider": "rest",
  "skip_validation": false,
  "account_id": {
    "zip_name": "my_rest_connection.connection.json",
    "name": "My REST Connection",
    "folder": ""
  }
}
```

---

## Google Service Account Example (GA4)

Full flow for querying Google Analytics 4 Data API:

1. **Trigger** receives report parameters (property ID, date range, metrics, dimensions)
2. **Build JWT** with scope `https://www.googleapis.com/auth/analytics.readonly`
3. **Exchange JWT** at `https://oauth2.googleapis.com/token`
4. **Call GA4 API** at `/v1beta/properties/{propertyId}:runReport` with `Bearer` token header

The JWT claims for Google service accounts:
- `iss`: Service account email
- `scope`: Space-delimited OAuth scopes
- `aud`: Always `https://oauth2.googleapis.com/token`
- `iat`: Current time as Unix epoch
- `exp`: Expiry time (max 1 hour from `iat`)

---

## Validation Checklist

- [ ] REST connection auth type is **None**
- [ ] JWT `exp` uses `(now + 1.hour).to_i` — NOT `now.utc`
- [ ] Token exchange uses absolute URL (not relative to connection base URL)
- [ ] Token exchange uses `content_type: "application/json"` with manual `Content-Type` header (avoids double-encoding)
- [ ] `extended_output_schema` defines `access_token` field on the token request step
- [ ] Token is referenced via datapill path (`["response", "access_token"]`) — NOT `.parse_json['access_token']`
- [ ] Subsequent API calls use `='Bearer ' + token_datapill` in Authorization header
- [ ] Action name is `make_request_v2` (NOT `__adhoc_http_action`) for `rest` provider
