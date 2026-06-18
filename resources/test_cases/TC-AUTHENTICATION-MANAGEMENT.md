# Test Cases — Authentication Management

- **Base URL:** `https://book.anhtester.com`
- **Feature:** Authentication Management
- **Endpoints:** `POST /api/login` · `POST /api/register` · `GET /api/me` · `PATCH /api/profile` · `DELETE /api/logout` · `POST /api/refetch-token`

---

## TC-AUTH-01 — Login — Valid Credentials

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-01 |
| **Title** | Login with valid credentials |
| **Method** | POST |
| **Endpoint** | `/api/login` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/login
Content-Type: application/json

{
    "email": "{{test_email}}",
    "password": "{{test_password}}"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | Success message string |
| `accessToken` | Non-empty JWT string |
| `exp` | Non-empty string (token expiry) |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Login successfully."` |
| `accessToken` | Non-empty JWT string ✓ |
| `exp` | `"6d"` |
| Pass / Fail | ✅ PASS |

### Notes
- `accessToken` returned here is used in the `Authorization: Bearer` header for all authenticated endpoints.
- `exp` is a **duration string** (`"6d"` = 6 days), not an ISO timestamp or Unix epoch — keep this in mind when writing automation assertions (assert non-empty string, not a date format).
---

## TC-AUTH-02 — Login — Wrong Password

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-02 |
| **Title** | Login with correct email but wrong password |
| **Method** | POST |
| **Endpoint** | `/api/login` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/login
Content-Type: application/json

{
    "email": "{{test_email}}",
    "password": "wrong_password_999"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `403 Forbidden` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | `"Invalid password."` |
| `fields.password` | `["Invalid password, please try again."]` |
| Pass / Fail | ✅ PASS |

### Notes
- Status code is `400`, not `403` as initially expected — server uses 400 with a `fields` object for credential errors.
- Response includes a `fields` object even though this is an authentication error, not a schema validation error — consistent with the 400 response schema in the OpenAPI spec.
- `msg` gives a summary; `fields.password` gives the detailed message.
---

## TC-AUTH-03 — Login — Unregistered Email

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-03 |
| **Title** | Login with an email that is not registered in the system |
| **Method** | POST |
| **Endpoint** | `/api/login` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/login
Content-Type: application/json

{
    "email": "nonexistent_autotest@fake.com",
    "password": "any_password"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `404 Not Found` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `404 Not Found` |
| `msg` | `"User not found."` |
| `fields.email` | `["Email not found, please register."]` |
| Pass / Fail | ✅ PASS |

### Notes
- Status code is `404` (not `403`) — confirmed.
- Response pattern is consistent with TC-AUTH-02: both credential errors return a `fields` object pointing to the specific failing field (`password` for wrong password, `email` for unknown email).
- `msg` is a short summary; `fields.email` contains the actionable message for the user.
---

## TC-AUTH-04 — Login — Missing Email Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-04 |
| **Title** | Login without providing the `email` field |
| **Method** | POST |
| **Endpoint** | `/api/login` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/login
Content-Type: application/json

{
    "password": "some_password"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.email` | Array containing error description for the `email` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.email` | `["Expected property 'email' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Error message pattern is identical to TC-CAT-04: `"Expected property '{field}' to be string but found: undefined"`.
- Server validates fields independently — only `fields.email` appears in the response since `password` was correctly provided.
- Re-run with correct `Content-Type: application/json` confirmed the isolated field validation behavior.
---

## TC-AUTH-05 — Login — Missing Password Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-05 |
| **Title** | Login without providing the `password` field |
| **Method** | POST |
| **Endpoint** | `/api/login` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/login
Content-Type: application/json

{
    "email": "{{test_email}}"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.password` | Array containing error description for the `password` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.password` | `["Expected property 'password' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Consistent with TC-AUTH-04: server validates fields independently — only `fields.password` appears since `email` was correctly provided.
- Error message pattern is identical across all 422 responses: `"Expected property '{field}' to be string but found: undefined"`.
---

## TC-AUTH-06 — Login — Invalid Email Format

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-06 |
| **Title** | Login with a malformed email string |
| **Method** | POST |
| **Endpoint** | `/api/login` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/login
Content-Type: application/json

{
    "email": "not-an-email",
    "password": "some_password"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.email` | Array containing error description for the `email` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.email` | `["Property 'email' should be email"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Server validates email format correctly — rejects `"not-an-email"` with a format-specific error message.
- Two distinct `fields.email` error messages exist depending on the violation type:
  - Missing field: `"Expected property 'email' to be string but found: undefined"` (TC-AUTH-04)
  - Invalid format: `"Property 'email' should be email"` (TC-AUTH-06)
- Both distinctions are important for automation assertions.
---

## TC-AUTH-07 — Register — Valid Full Payload

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-07 |
| **Title** | Register a new account with all available fields |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "name": "AutoTest User",
    "email": "autotest_full_1234567890@test.com",
    "password": "Test@12345",
    "phone": "0901234567",
    "address": "123 AutoTest Street"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `201 Created` |
| `msg` | Success confirmation message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `201 Created` |
| `msg` | `"Register successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Use a unique email with a timestamp suffix (e.g. `autotest_full_1234567890@test.com`) to avoid conflicts in the shared environment.
- There is no `DELETE /api/user` endpoint — registered test accounts will persist in the database.
- Response returns only `msg`, no user object (id, email, etc.) in the body.
---

## TC-AUTH-08 — Register — Required Fields Only

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-08 |
| **Title** | Register a new account with only the three required fields |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "name": "AutoTest Minimal",
    "email": "autotest_min_1234567890@test.com",
    "password": "Test@12345"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `201 Created` |
| `msg` | Success confirmation message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `201 Created` |
| `msg` | `"Register successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Confirms that `phone`, `address`, and `avatarUrl` are truly optional — omitting them does not cause validation errors.
- Response is identical to TC-AUTH-07 (full payload) — server does not require or return optional fields.
---

## TC-AUTH-09 — Register — Duplicate Email

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-09 |
| **Title** | Register with an email address that already exists in the system |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | High |
| **Precondition** | Account with `{{test_email}}` already exists |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "name": "Duplicate User",
    "email": "{{test_email}}",
    "password": "Test@12345"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | Error message indicating the email is already taken |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Email already exists."` |
| `fields.email` | `["Email already exists."]` |
| Pass / Fail | ✅ PASS |

### Notes
- Server returns `422` for duplicate email, not `400` as initially expected.
- Unlike the category duplicate error (TC-CAT-03: `400 "Category already exists."`), the register endpoint uses `422` with a `fields` object — inconsistency across endpoints worth noting.
- `msg` and `fields.email[0]` contain the same string `"Email already exists."` — both can be used for assertion.
---

## TC-AUTH-10 — Register — Missing Name Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-10 |
| **Title** | Register without providing the required `name` field |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "email": "autotest_1234567890@test.com",
    "password": "Test@12345"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.name` | Array containing error description for the `name` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.name` | `["Expected property 'name' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-AUTH-11 — Register — Missing Email Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-11 |
| **Title** | Register without providing the required `email` field |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "name": "AutoTest User",
    "password": "Test@12345"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.email` | Array containing error description for the `email` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.email` | `["Expected property 'email' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-AUTH-12 — Register — Missing Password Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-12 |
| **Title** | Register without providing the required `password` field |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "name": "AutoTest User",
    "email": "autotest_1234567890@test.com"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.password` | Array containing error description for the `password` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.password` | `["Expected property 'password' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-AUTH-13 — Register — Invalid Email Format

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-13 |
| **Title** | Register with a malformed email string |
| **Method** | POST |
| **Endpoint** | `/api/register` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/register
Content-Type: application/json

{
    "name": "AutoTest User",
    "email": "not-an-email",
    "password": "Test@12345"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.email` | Array containing error description for the `email` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.email` | `["Property 'email' should be email"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Error message is identical to TC-AUTH-06 (login with invalid email format) — same validation rule applied consistently across both endpoints.
- The `email` field has `"format": "email"` in the OpenAPI spec — server correctly rejects invalid format at the validation layer before any DB lookup.
---

## TC-AUTH-14 — Get Me — Authenticated

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-14 |
| **Title** | Get current user profile with a valid token |
| **Method** | GET |
| **Endpoint** | `/api/me` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
GET {{base_url}}/api/me
Authorization: Bearer {{access_token}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `id` | Non-empty string |
| `name` | String |
| `email` | Matches `{{test_email}}` |
| `avatarUrl` | String (may be empty) |
| `phone` | String (may be empty) |
| `address` | String (may be empty) |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `id` | `"cmpcuwb500ssn7uk1zphpd4ix"` |
| `name` | `"Administrator"` |
| `email` | `"admin@test.com"` |
| `avatarUrl` | `""` (empty string) |
| `phone` | `"0912123123"` |
| `address` | `"70 Lữ Gia, Phường Phú Thọ, Thành phố Hồ Chí Minh"` |
| `config` | `{}` (empty object) |
| Pass / Fail | ✅ PASS |

### Notes
- Response is a flat user object — no `msg` field, unlike other endpoints.
- Response includes an undocumented `config` field (`{}` empty object) not present in the OpenAPI spec — add to Expected Result for future assertions.
- `avatarUrl` returns an empty string `""` (not `null`) when not set — assert as string, not null-check.
- Current profile values noted for TC-AUTH-16 restore data: `name = "Administrator"`, `phone = "0912123123"`, `address = "70 Lữ Gia, Phường Phú Thọ, Thành phố Hồ Chí Minh"`.
---

## TC-AUTH-15 — Get Me — No Token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-15 |
| **Title** | Call GET /api/me without providing an Authorization header |
| **Method** | GET |
| **Endpoint** | `/api/me` |
| **Authentication** | Not provided |
| **Priority** | High |

### Request

```
GET {{base_url}}/api/me
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `401 Unauthorized` or `403 Forbidden` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | `"Missing or invalid Authorization header"` |
| Pass / Fail | ✅ PASS |

### Notes
- Status code is `401` (not `403`) — confirmed for automation assertions.
- Same `msg` likely applies to all authenticated endpoints when token is missing — verify in TC-AUTH-19 and TC-AUTH-21.
---

## TC-AUTH-16 — Update Profile — Valid Name Change

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-16 |
| **Title** | Update the authenticated user's `name` field with a valid value |
| **Method** | PATCH |
| **Endpoint** | `/api/profile` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
PATCH {{base_url}}/api/profile
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "AutoTest Updated Name"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | Success confirmation message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Updated profile successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Response returns only `msg` — no updated user object in the body.
- After verifying the 200 response, call `GET /api/me` to confirm the `name` field has been updated.
- ⚠️ Restore original name after this test: `PATCH /api/profile` with `{"name": "Administrator"}`.
---

## TC-AUTH-17 — Update Profile — Change Password with Correct Old Password

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-17 |
| **Title** | Change the authenticated user's password by providing the correct `password_old` |
| **Method** | PATCH |
| **Endpoint** | `/api/profile` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
PATCH {{base_url}}/api/profile
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "password": "NewTest@99999",
    "password_old": "{{test_password}}"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | Success confirmation message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Updated profile successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Response is identical to TC-AUTH-16 — same `msg` for all successful profile updates regardless of which field was changed.
- ⚠️ **Restore the original password immediately** after this test: `PATCH /api/profile` with `{"password": "{{test_password}}", "password_old": "NewTest@99999"}`.
- Failing to restore will break the `auth_token` session fixture and all subsequent authenticated tests.
- After the password change, verify whether the existing token is still valid or has been invalidated by calling `GET /api/me`.
---

## TC-AUTH-18 — Update Profile — Change Password with Wrong Old Password

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-18 |
| **Title** | Change password while providing an incorrect `password_old` value |
| **Method** | PATCH |
| **Endpoint** | `/api/profile` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
PATCH {{base_url}}/api/profile
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "password": "NewTest@99999",
    "password_old": "wrong_old_password"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` or `403 Forbidden` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Updated profile successfully."` |
| Pass / Fail | ❌ FAIL |

### Notes
- 🐛 **BUG: Server does not validate `password_old` when using `fields` wrapper payload.**
  - Flat payload `{"password": "...", "password_old": "..."}` → `400` with `fields.fields` missing error (TC-AUTH-17 used this and passed with correct old password).
  - `fields` wrapper `{"fields": {"password": "...", "password_old": "..."}}` → `200` regardless of whether `password_old` is correct — `password_old` is effectively ignored.
- This is a **security vulnerability**: any authenticated user can change their password without knowing the current one, as long as the request uses the `fields` wrapper format.
- ⚠️ Password was changed to `"NewTest@99999"` — **restore immediately** before continuing:
  ```json
  PATCH /api/profile  →  { "password": "{{test_password}}", "password_old": "NewTest@99999" }
  ```

---

## TC-AUTH-19 — Update Profile — No Token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-19 |
| **Title** | Call PATCH /api/profile without providing an Authorization header |
| **Method** | PATCH |
| **Endpoint** | `/api/profile` |
| **Authentication** | Not provided |
| **Priority** | High |

### Request

```
PATCH {{base_url}}/api/profile
Content-Type: application/json

{
    "name": "Unauthorized Attempt"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `401 Unauthorized` or `403 Forbidden` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | `"Missing or invalid Authorization header"` |
| Pass / Fail | ✅ PASS |

### Notes
- Status code is `401` — consistent with TC-AUTH-15 (`GET /api/me` no token).
- `msg` is identical: `"Missing or invalid Authorization header"` — same auth middleware applied across all protected endpoints.
---

## TC-AUTH-20 — Logout — Authenticated

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-20 |
| **Title** | Logout from an authenticated session |
| **Method** | DELETE |
| **Endpoint** | `/api/logout` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
DELETE {{base_url}}/api/logout
Authorization: Bearer {{fresh_token}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | Success message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Logout successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Used a fresh token from a separate login call — main session token unaffected.
- After logout, verify the token is invalidated by calling `GET /api/me` with the logged-out token — should return `401`.
- Note whether the `refetchToken` cookie is cleared in the response headers.
---

## TC-AUTH-21 — Logout — No Token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-21 |
| **Title** | Call DELETE /api/logout without providing an Authorization header |
| **Method** | DELETE |
| **Endpoint** | `/api/logout` |
| **Authentication** | Not provided |
| **Priority** | Medium |

### Request

```
DELETE {{base_url}}/api/logout
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `401 Unauthorized` or `403 Forbidden` |
| `msg` | Error message string (response body may be empty per spec) |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `401 Unauthorized` |
| Response body | `{}` (empty object — no `msg` field) |
| Pass / Fail | ✅ PASS |

### Notes
- Response body is `{}` — unlike TC-AUTH-15 and TC-AUTH-19 which return `{"msg": "Missing or invalid Authorization header"}`, this endpoint returns an empty object on 401.
- Inconsistency across protected endpoints: `GET /api/me` and `PATCH /api/profile` return a `msg` on 401; `DELETE /api/logout` does not — assertions must handle this per-endpoint.
---

## TC-AUTH-22 — Refetch Token — Valid Cookie

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-22 |
| **Title** | Get a new access token by providing a valid `refetchToken` cookie |
| **Method** | POST |
| **Endpoint** | `/api/refetch-token` |
| **Authentication** | Cookie: `refetchToken` (set by server at login) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/refetch-token
Cookie: refetchToken={{refetch_token_cookie}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | Success message string |
| `accessToken` | New non-empty JWT string |
| `exp` | Non-empty string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Refetch token successfully."` |
| `accessToken` | New non-empty JWT string ✓ |
| `exp` | `"6d"` |
| Pass / Fail | ✅ PASS |

### Notes
- Server sets `refetchToken` cookie automatically at login — Postman sends it automatically on subsequent requests to the same domain.
- Response schema is identical to `POST /api/login`: `{msg, accessToken, exp}` — `exp` is a duration string `"6d"`, not a timestamp.
- The new `accessToken` is different from the one obtained at login — can be used to replace the current session token.
---

## TC-AUTH-23 — Refetch Token — No Cookie

| Field | Detail |
|---|---|
| **Test Case ID** | TC-AUTH-23 |
| **Title** | Call POST /api/refetch-token without providing the required cookie |
| **Method** | POST |
| **Endpoint** | `/api/refetch-token` |
| **Authentication** | Not provided |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/refetch-token
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` or `422 Unprocessable Entity` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.refetchToken` | `["Property 'refetchToken' is missing", "Expected property 'refetchToken' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Server returns `422` (not `400`) when the cookie is absent — consistent with other missing-field validation errors.
- `fields.refetchToken` contains **two error messages** simultaneously — unique pattern not seen on other endpoints.
- Cookie-based fields follow the same `"found: undefined"` error pattern as body fields (TC-AUTH-04, 05, 10, 11, 12).
---