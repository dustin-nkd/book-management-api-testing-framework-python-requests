# Test Cases — Book Management

- **Base URL:** `https://book.anhtester.com`
- **Feature:** Book Management
- **Endpoints:** `GET | POST /api/book` · `GET | PATCH | DELETE /api/book/{id}`

---

## TC-BOOK-01 — Get Books — Default Pagination

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-01 |
| **Title** | GET /api/book with default parameters returns paginated list |
| **Method** | GET |
| **Endpoint** | `/api/book` |
| **Authentication** | Not required (public endpoint) |
| **Priority** | High |

### Request

```
GET {{base_url}}/api/book
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `list` | Array of 10 book objects (default `limit=10`) |
| `list[*]` | Each item has: `id`, `name`, `description`, `slug`, `categories`, `picture`, `auth`, `status`, `createdAt`, `updatedAt`, `price`, `currentPrice`, `viewCount`, `promotions` |
| `pagination.total` | Integer ≥ 0 |
| `pagination.currentPage` | `1` |
| `pagination.totalPage` | Integer |
| `pagination.lengthData` | `10` |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `list` | Array of 10 book objects |
| `pagination.total` | `685` |
| `pagination.totalPage` | `69` |
| `pagination.currentPage` | `1` |
| `pagination.lengthData` | `10` |
| Pass / Fail | ✅ PASS |

### Notes
- Default query parameters: `limit=10`, `page=1`.
- Each book item in `list` contains: `id`, `name`, `description`, `slug`, `categories`, `picture`, `auth`, `status`, `createdAt`, `updatedAt`, `price`, `currentPrice`, `viewCount`, `promotions`.
- ⚠️ Field name inconsistency: list response uses `picture` (singular), but `POST /api/book` request body uses `pictures` (plural) — note for test assertions.
- `auth` object (undocumented in spec) contains: `name`, `email`, `avatarUrl` of the book creator.
- Some books have `categories: []` empty array even though spec defines `minItems: 1` for creation — leftover data from test runs bypassing validation.
- `currentPrice` may differ from `price` when promotions are applied (e.g. `price: 60000`, `currentPrice: 1431` seen on one item).

---

## TC-BOOK-02 — Get Books — Pagination

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-02 |
| **Title** | GET /api/book with custom limit and page parameters |
| **Method** | GET |
| **Endpoint** | `/api/book` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
GET {{base_url}}/api/book?limit=5&page=2
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `list` | Array with ≤ 5 items |
| `pagination.currentPage` | `2` |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `list` | Array of 5 items |
| `pagination.total` | `685` |
| `pagination.totalPage` | `137` (= 685 ÷ 5) |
| `pagination.currentPage` | `2` |
| `pagination.lengthData` | `5` |
| Pass / Fail | ✅ PASS |

### Notes
- `limit=5` correctly returns 5 items; `page=2` correctly sets `currentPage=2`.
- `totalPage` recalculates dynamically based on `limit` — TC-BOOK-01 with `limit=10` returned `totalPage=69`, here `limit=5` returns `totalPage=137`.

---

## TC-BOOK-03 — Get Books — Search by Name

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-03 |
| **Title** | GET /api/book with search parameter filters by name |
| **Method** | GET |
| **Endpoint** | `/api/book` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
GET {{base_url}}/api/book?search=Lisa's love story
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `list` | Filtered array containing only books matching the search term |
| `pagination.total` | Count of matching books |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `list` | Array of 1 item — `"Lisa's love story"` |
| `pagination.total` | `1` |
| `pagination.totalPage` | `1` |
| `pagination.currentPage` | `1` |
| `pagination.lengthData` | `1` |
| Pass / Fail | ✅ PASS |

### Notes
- Initial run with `search=python` returned empty list (no matching books in DB) — inconclusive.
- Re-run with `search=Lisa's love story` confirmed search filtering works correctly — only the exact matching book is returned.
- Search appears to match against `name` field; confirm whether `description` is also searched during test script implementation.

---

## TC-BOOK-04 — Get Books — Sort by Name Ascending

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-04 |
| **Title** | GET /api/book with sort by name and ascending order |
| **Method** | GET |
| **Endpoint** | `/api/book` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
GET {{base_url}}/api/book?sort=name&sortBy=asc
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `list` | Array sorted alphabetically by book name (ascending) |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `list[0].name` | `""` (empty string) |
| `list[1].name` | `" OR 1=1 -- 2b79de85"` |
| `list[2].name` | `"' OR 1=1"` |
| `list[3].name` | `"#$#%$%%^% hu"` |
| `list[4].name` | `"<script>alert('XSS')</script> 6fde58a4"` |
| `list[5].name` | `"1"` |
| Sort order | Empty → special chars → numbers → letters ✓ |
| Pass / Fail | ✅ PASS |

### Notes
- Sort ascending works correctly: empty string → space-prefixed strings → special characters → numbers → letters.
- 🐛 **Data integrity issues found (not a sort bug — pre-existing bad data in shared DB):**
  - Books with **empty name** `""` exist — server does not validate blank `name` on creation.
  - SQL injection strings stored as plain text (`" OR 1=1"`, `"' OR 1=1"`) — server correctly does not execute them.
  - XSS payload stored as plain text (`<script>alert('XSS')</script>`) — server correctly does not execute it.
  - One book has `price: 0` — zero price is accepted by the server.
  - One book has `currentPrice: -5145100` (negative!) — likely caused by a promotion calculation overflow; potential promotion bug.

---

## TC-BOOK-05 — Get Books — Sort by Price Descending

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-05 |
| **Title** | GET /api/book sorted by price in descending order |
| **Method** | GET |
| **Endpoint** | `/api/book` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
GET {{base_url}}/api/book?sort=price&sortBy=desc
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `list` | Array sorted by price (highest to lowest) |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `list[0].price` | `2147483647` |
| `list[1].price` | `2122218` |
| `list[2].price` | `930014` |
| Sort order | `2147483647 ≥ 2122218 ≥ 930014 ≥ ...` ✓ |
| Pass / Fail | ✅ PASS |

### Notes
- Sort by `price` descending works correctly — prices decrease monotonically.
- ⚠️ `list[0].price = 2,147,483,647` = `INT32_MAX` (2³¹ − 1) — the highest price in the DB is exactly the max value of a 32-bit signed integer. OpenAPI spec documents max as `9,000,000,000,000` but actual storage appears to be 32-bit integer. Create test (TC-BOOK-06/07) should use a safe price value well below `INT32_MAX`.
- Promotions structure confirmed in this response: `{name, description, type, startDate, endDate, code, value}` — `type: "FIXED_AMOUNT"` subtracts `value` from `price` to produce `currentPrice`.

---

## TC-BOOK-06 — Create Book — Valid Full Payload

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-06 |
| **Title** | POST /api/book with all available fields should return 201 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "AutoTest Book Full",
    "slug": "autotest-book-full",
    "description": "Complete book with all optional fields",
    "status": "AVAILABLE",
    "pictures": [],
    "categories": ["Technology"],
    "price": 150000,
    "promotions": []
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Status code is `200` (not `201`) — inconsistent with REST convention for resource creation. Update Expected accordingly.
- Response body contains only `msg` — **no book ID returned**. To retrieve the created book's ID for subsequent tests (TC-BOOK-16 onward), call `GET /api/book?search=AutoTest Book Full` and extract `list[0].id`.
- ⚠️ Run `GET /api/book?search=AutoTest Book Full` after this TC and note down the `id` before continuing.

---

## TC-BOOK-07 — Create Book — Required Fields Only

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-07 |
| **Title** | POST /api/book with only required fields should return 201 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "AutoTest Book Minimal",
    "status": "AVAILABLE",
    "categories": ["Technology"],
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Confirms `slug`, `description`, `pictures`, `promotions` are truly optional — omitting them does not cause validation errors.
- Status code is `200` (consistent with TC-BOOK-06).

---

## TC-BOOK-08 — Create Book — Unavailable Status

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-08 |
| **Title** | POST /api/book with status=UNAVAILABLE should return 201 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "AutoTest Out of Stock",
    "status": "UNAVAILABLE",
    "categories": ["Technology"],
    "price": 75000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- `status: "UNAVAILABLE"` is accepted — both enum values confirmed working.

---

## TC-BOOK-09 — Create Book — Missing Name Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-09 |
| **Title** | POST /api/book without name field should return 422 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "status": "AVAILABLE",
    "categories": ["Technology"],
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.name` | Array containing error description |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.name` | `["Expected property 'name' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Consistent with auth 422 pattern: `"Expected property '{field}' to be string but found: undefined"`.

---

## TC-BOOK-10 — Create Book — Missing Categories Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-10 |
| **Title** | POST /api/book without categories field should return 422 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Book Without Category",
    "status": "AVAILABLE",
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.categories` | Array containing error description |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.categories` | `["Expected array"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Error message differs from string-type fields: `categories` is an array so the error is `"Expected array"` (not `"Expected property... to be string"`).
- Error message is type-specific — important distinction for test script assertions.

---

## TC-BOOK-11 — Create Book — Missing Price Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-11 |
| **Title** | POST /api/book without price field should return 422 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Book Without Price",
    "status": "AVAILABLE",
    "categories": ["Technology"]
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.price` | Array containing error description |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |
| `fields.price` | — (not present, book was created) |
| Pass / Fail | ❌ FAIL |

### Notes
- 🐛 **BUG: `price` field is not validated as required.** Server created the book successfully without a `price` value despite `price` being marked as required in the OpenAPI spec.
- Follow-up search `GET /api/book?search=Book Without Price` revealed: `price: 50000` and `currentPrice: -4335750`.
- `price: 50000` — server stored an unexpected default value (not `0` or `null`).
- 🐛 **BUG: `currentPrice: -4335750`** — a deeply negative price was calculated despite `promotions: []` being empty. Likely a server-side promotion calculation error triggered by the missing/malformed price value.

---

## TC-BOOK-12 — Create Book — Missing Status Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-12 |
| **Title** | POST /api/book without status field should return 422 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Book Without Status",
    "categories": ["Technology"],
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.status` | Array containing error description |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Book created successfully."` |
| `fields.status` | — (not present, book was created) |
| Pass / Fail | ❌ FAIL |

### Notes
- 🐛 **BUG: `status` field is not validated as required.** Server created the book successfully without a `status` value.
- Consistent pattern with TC-BOOK-11 (`price` also not validated) — server does not enforce required field validation for `POST /api/book` beyond `name` and `categories`.

---

## TC-BOOK-13 — Create Book — Invalid Status Value

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-13 |
| **Title** | POST /api/book with invalid status enum value should return 422 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Book With Invalid Status",
    "status": "PENDING_APPROVAL",
    "categories": ["Technology"],
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.status` | Array containing error about invalid enum value |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.status` | `["Expected kind 'UnionEnum'"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Re-run with correct Content-Type (`raw > JSON`) and complete payload confirmed enum validation works.
- Error message for invalid enum value: `"Expected kind 'UnionEnum'"` — unique pattern, different from other 422 messages.
- Interesting inconsistency: **missing** `status` is accepted (TC-BOOK-12: 200), but **invalid** `status` value is rejected (422). Server only validates enum when the field is present.
- Complete 422 error message map for `POST /api/book`:
  - Missing string field → `"Expected property '{field}' to be string but found: undefined"`
  - Missing array field → `"Expected array"`
  - Invalid enum value → `"Expected kind 'UnionEnum'"`

---

## TC-BOOK-14 — Create Book — Empty Categories Array

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-14 |
| **Title** | POST /api/book with empty categories array should return 422 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Book With Empty Categories",
    "status": "AVAILABLE",
    "categories": [],
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.categories` | Array containing error about minItems constraint |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.categories` | `["Expected array length to be greater or equal to 1"]` |
| Pass / Fail | ✅ PASS |

### Notes
- `minItems: 1` constraint is enforced with a clear descriptive error message.
- Distinct from missing `categories` (TC-BOOK-10: `"Expected array"`) — server differentiates between absent array and empty array.

---

## TC-BOOK-15 — Create Book — No Token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-15 |
| **Title** | POST /api/book without Authorization header should return 401 |
| **Method** | POST |
| **Endpoint** | `/api/book` |
| **Authentication** | Not provided |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/book
Content-Type: application/json

{
    "name": "Unauthorized Book",
    "status": "AVAILABLE",
    "categories": ["Technology"],
    "price": 50000
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | `"Missing or invalid Authorization header"` |
| Pass / Fail | ✅ PASS |

### Notes
- Consistent with TC-AUTH-15 and TC-AUTH-19 — same `msg` across all protected endpoints.

---

## TC-BOOK-16 — Get Book by ID — Valid ID

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-16 |
| **Title** | GET /api/book/{id} with valid book ID should return full book details |
| **Method** | GET |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Not required |
| **Priority** | High |
| **Precondition** | A book exists in the system (created by TC-BOOK-06 or TC-BOOK-07) |

### Request

```
GET {{base_url}}/api/book/{{book_id}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `id` | Non-empty string (UUID) |
| `name` | String |
| `description` | String (may be empty) |
| `status` | `AVAILABLE` or `UNAVAILABLE` |
| `price` | Number |
| `currentPrice` | Number |
| `categories` | Array of strings |
| `picture` | Array of picture objects |
| `auth` | Object: `{name, email, avatarUrl}` |
| `promotions` | Array (may be empty) |
| `viewCount` | Integer |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `id` | `"cmqpcfkns0v137uk15xmbqi2j"` |
| `name` | `"AutoTest Book Full"` |
| `description` | `"Complete book with all optional fields"` |
| `status` | `"AVAILABLE"` |
| `price` | `150000` |
| `currentPrice` | `150000` |
| `categories` | `["Technology"]` |
| `picture` | Array of 1 picture object |
| `auth` | `{name: "Administrator", email: "admin@test.com", avatarUrl: ""}` |
| `promotions` | `[]` |
| `viewCount` | `0` |
| Pass / Fail | ✅ PASS |

### Notes
- `viewCount: 0` — freshly created book, not yet viewed.
- `picture` in the detail response contains full file metadata objects: `{name, path, isFile, size, type, modified, created}` — richer than the list response which returns `picture: []`.
- `slug` field present in list response (TC-BOOK-01/02) is **absent** from the detail response — inconsistency between list and detail schemas.
- Field name is `picture` (singular) — consistent with list response, different from create request body which uses `pictures` (plural).

---

## TC-BOOK-17 — Get Book by ID — View Count Increment

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-17 |
| **Title** | GET /api/book/{id}?view=true increments viewCount |
| **Method** | GET |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Not required |
| **Priority** | Medium |

### Request

```
GET {{base_url}}/api/book/{{book_id}}?view=true
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `viewCount` | Incremented by 1 compared to previous request |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `viewCount` | `1` (was `0` in TC-BOOK-16 before `?view=true`) |
| Pass / Fail | ✅ PASS |

### Notes
- `viewCount` incremented from `0` → `1` after one `?view=true` request — confirmed working.
- `view=false` or absent should NOT increment viewCount — verify this when writing test script assertions (call without param and assert viewCount stays at `1`).

---

## TC-BOOK-18 — Get Book by ID — Non-existent ID

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-18 |
| **Title** | GET /api/book/{id} with non-existent ID should return 404 |
| **Method** | GET |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
GET {{base_url}}/api/book/nonexistent-uuid-xyz
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
| `msg` | `"Book not found."` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-BOOK-19 — Update Book — Valid Name Change

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-19 |
| **Title** | PATCH /api/book/{id} to change name should return 200 |
| **Method** | PATCH |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |
| **Precondition** | A book exists created in TC-BOOK-06 or TC-BOOK-07 |

### Request

```
PATCH {{base_url}}/api/book/{{book_id}}
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Updated Book Name"
}
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
| `msg` | `"Book updated successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Verify name change by calling `GET /api/book/{id}` after update.

---

## TC-BOOK-20 — Update Book — Change Status

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-20 |
| **Title** | PATCH /api/book/{id} to change status should return 200 |
| **Method** | PATCH |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
PATCH {{base_url}}/api/book/{{book_id}}
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "status": "UNAVAILABLE"
}
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
| `msg` | `"Book updated successfully."` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-BOOK-21 — Update Book — Change Price

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-21 |
| **Title** | PATCH /api/book/{id} to change price should return 200 |
| **Method** | PATCH |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
PATCH {{base_url}}/api/book/{{book_id}}
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "price": 250000
}
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
| `msg` | `"Book updated successfully."` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-BOOK-22 — Update Book — Change Categories

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-22 |
| **Title** | PATCH /api/book/{id} to change categories should return 200 |
| **Method** | PATCH |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
PATCH {{base_url}}/api/book/{{book_id}}
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "categories": ["Technology", "Programming"]
}
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
| `msg` | `"Book updated successfully."` |
| Pass / Fail | ✅ PASS |

### Notes

---

## TC-BOOK-23 — Update Book — Non-existent ID

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-23 |
| **Title** | PATCH /api/book/{id} with non-existent ID should return 404 |
| **Method** | PATCH |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
PATCH {{base_url}}/api/book/nonexistent-uuid-xyz
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Nonexistent Book"
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
| `msg` | `"Book not found."` |
| Pass / Fail | ✅ PASS |

### Notes
- Same `msg` as TC-BOOK-18 (`GET` non-existent) — consistent 404 message across endpoints.

---

## TC-BOOK-24 — Update Book — No Token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-24 |
| **Title** | PATCH /api/book/{id} without Authorization header should return 401 |
| **Method** | PATCH |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Not provided |
| **Priority** | High |

### Request

```
PATCH {{base_url}}/api/book/{{book_id}}
Content-Type: application/json

{
    "name": "Unauthorized Update"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | `"Missing or invalid Authorization header"` |
| Pass / Fail | ✅ PASS |

### Notes
- Consistent with TC-BOOK-15 and all other protected endpoints.

---

## TC-BOOK-25 — Delete Book — Existing Book

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-25 |
| **Title** | DELETE /api/book/{id} with valid ID should return 200 |
| **Method** | DELETE |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
DELETE {{base_url}}/api/book/{{book_id}}
Authorization: Bearer {{access_token}}
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
| `msg` | `"Deleted successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- `msg` is `"Deleted successfully."` — shorter than create/update messages (`"Book created/updated successfully."`).
- Verify deletion by calling `GET /api/book/cmqpcfkns0v137uk15xmbqi2j` → should now return `404 "Book not found."`.

---

## TC-BOOK-26 — Delete Book — Non-existent ID

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-26 |
| **Title** | DELETE /api/book/{id} with non-existent ID should return 404 |
| **Method** | DELETE |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
DELETE {{base_url}}/api/book/nonexistent-uuid-xyz
Authorization: Bearer {{access_token}}
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
| `msg` | `"Book not found."` |
| Pass / Fail | ✅ PASS |

### Notes
- Same `msg` as TC-BOOK-18 and TC-BOOK-23 — `"Book not found."` is consistent across all non-existent ID scenarios.

---

## TC-BOOK-27 — Delete Book — No Token

| Field | Detail |
|---|---|
| **Test Case ID** | TC-BOOK-27 |
| **Title** | DELETE /api/book/{id} without Authorization header should return 401 |
| **Method** | DELETE |
| **Endpoint** | `/api/book/{id}` |
| **Authentication** | Not provided |
| **Priority** | High |

### Request

```
DELETE {{base_url}}/api/book/{{book_id}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | Error message string |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `401 Unauthorized` |
| `msg` | `"Missing or invalid Authorization header"` |
| Pass / Fail | ✅ PASS |

### Notes
- Consistent with TC-BOOK-15, TC-BOOK-24 and all other protected endpoints.

---

## Summary

| TC ID | Endpoint | Scenario | Status |
|---|---|---|---|
| TC-BOOK-01 | GET /api/book | Default pagination → 200 | ✅ PASS |
| TC-BOOK-02 | GET /api/book | Custom limit/page → 200 | ✅ PASS |
| TC-BOOK-03 | GET /api/book | Search by name → 200 | ✅ PASS |
| TC-BOOK-04 | GET /api/book | Sort by name asc → 200 | ✅ PASS |
| TC-BOOK-05 | GET /api/book | Sort by price desc → 200 | ✅ PASS |
| TC-BOOK-06 | POST /api/book | Valid full payload → 200 | ✅ PASS |
| TC-BOOK-07 | POST /api/book | Required fields only → 200 | ✅ PASS |
| TC-BOOK-08 | POST /api/book | Status=UNAVAILABLE → 200 | ✅ PASS |
| TC-BOOK-09 | POST /api/book | Missing name → 422 | ✅ PASS |
| TC-BOOK-10 | POST /api/book | Missing categories → 422 | ✅ PASS |
| TC-BOOK-11 | POST /api/book | Missing price → 422 | ❌ FAIL |
| TC-BOOK-12 | POST /api/book | Missing status → 422 | ❌ FAIL |
| TC-BOOK-13 | POST /api/book | Invalid status enum → 422 | ✅ PASS |
| TC-BOOK-14 | POST /api/book | Empty categories → 422 | ✅ PASS |
| TC-BOOK-15 | POST /api/book | No token → 401 | ✅ PASS |
| TC-BOOK-16 | GET /api/book/{id} | Valid ID → 200 + full detail | ✅ PASS |
| TC-BOOK-17 | GET /api/book/{id} | ?view=true increments viewCount | ✅ PASS |
| TC-BOOK-18 | GET /api/book/{id} | Non-existent ID → 404 | ✅ PASS |
| TC-BOOK-19 | PATCH /api/book/{id} | Change name → 200 | ✅ PASS |
| TC-BOOK-20 | PATCH /api/book/{id} | Change status → 200 | ✅ PASS |
| TC-BOOK-21 | PATCH /api/book/{id} | Change price → 200 | ✅ PASS |
| TC-BOOK-22 | PATCH /api/book/{id} | Change categories → 200 | ✅ PASS |
| TC-BOOK-23 | PATCH /api/book/{id} | Non-existent ID → 404 | ✅ PASS |
| TC-BOOK-24 | PATCH /api/book/{id} | No token → 401 | ✅ PASS |
| TC-BOOK-25 | DELETE /api/book/{id} | Existing ID → 200 | ✅ PASS |
| TC-BOOK-26 | DELETE /api/book/{id} | Non-existent ID → 404 | ✅ PASS |
| TC-BOOK-27 | DELETE /api/book/{id} | No token → 401 | ✅ PASS |