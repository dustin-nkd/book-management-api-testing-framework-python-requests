# Test Cases — Category Management

- **Base URL:** `https://book.anhtester.com`
- **Feature:** Category Management
- **Endpoints:** `GET | POST | PUT /api/category-book` · `DELETE /api/category-book/{name}`

---

## TC-CAT-01 — Get All Categories

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-01 |
| **Title** | Get all categories successfully |
| **Method** | GET |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Not required |
| **Priority** | High |

### Request

```
GET {{base_url}}/api/category-book
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `200 OK` |
| `list` | Array of category objects, each has `name` (string) and `bookCount` (number) |
| `pagination.total` | Number >= 0 |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `list` | Array of 90 items, each has `name` (string) and `bookCount` (number) |
| `pagination.total` | `90` |
| Pass / Fail | ✅ PASS |

### Notes
- Category with `name: ""` (empty string) exists with bookCount: 5 — possible bad data or server allows empty name creation.
- Some categories have leading whitespace (e.g. " Bình tĩnh sống") — server does not trim input.
- `pagination` only returns `total`, unlike Book API which returns `totalPage`, `currentPage`, `lengthData`.
- Shared environment: many categories created by other users — use unique names in automation tests.

---

## TC-CAT-02 — Create Category — Valid Name

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-02 |
| **Title** | Create a new category with a valid unique name |
| **Method** | POST |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
POST {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Science Fiction"
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
| `msg` | `"Category created successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Response only returns `msg`, no category object (id, name) in the body.
- To verify the category was actually created, call GET /api/category-book and search in the list.

---

## TC-CAT-03 — Create Category — Duplicate Name

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-03 |
| **Title** | Create a category with an already existing name |
| **Method** | POST |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |
| **Precondition** | Category `"Science Fiction"` already exists (created in TC-CAT-02) |

### Request

```
POST {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Science Fiction"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | Error message indicating the category already exists |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | `"Category already exists."` |
| Pass / Fail | ✅ PASS |

### Notes
- Server returns a clear, descriptive error message for duplicate names.
- No `fields` object in the response body, unlike 422 validation errors.

---

## TC-CAT-04 — Create Category — Missing Name Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-04 |
| **Title** | Create a category without providing the required `name` field |
| **Method** | POST |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{}
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
- `fields` is an object where each key is the invalid field name,
  and value is an array of error message strings.
- Error message explicitly states the expected type and actual value found.
- This pattern is consistent with OpenAPI spec's 422 response schema.

---

## TC-CAT-05 — Create Category — Empty String Name

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-05 |
| **Title** | Create a category with an empty string as the name value |
| **Method** | POST |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": ""
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` or `422 Unprocessable Entity` |
| `msg` | Error message indicating name cannot be empty |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | `"Category already exists."` |
| Pass / Fail | ⚠️ PASS (conditional — see notes) |

### Notes
- 🐛 BUG: Server does not validate empty string as an invalid name.
  Empty string is treated as a valid category name.
- The 400 response here is only because a category with name "" already
  exists in the database (observed in TC-CAT-01 with bookCount: 5).
- If no category with name "" existed, the server would return 201 Created —
  meaning an empty-string category would be successfully created.
- Expected behavior: server should reject empty string with 422 and a
  descriptive validation error, similar to TC-CAT-04.
- Recommendation: add server-side validation to reject blank or
  whitespace-only category names.

---

## TC-CAT-06 — Update Category — Valid Rename

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-06 |
| **Title** | Rename an existing category with a valid new name |
| **Method** | PUT |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |
| **Precondition** | Category `"Science Fiction"` exists |

### Request

```
PUT {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Science Fiction",
    "newName": "Sci-Fi & Fantasy"
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
| `msg` | `"Category updated successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Response only returns `msg`, no updated category object in the body.
- To verify the rename was applied, call GET /api/category-book and
  confirm old name is absent and new name is present in the list.

---

## TC-CAT-07 — Update Category — Name Does Not Exist

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-07 |
| **Title** | Rename a category that does not exist in the system |
| **Method** | PUT |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
PUT {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "NonExistentCategory_XYZ",
    "newName": "Whatever"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` or `404 Not Found` |
| `msg` | Error message indicating the category was not found |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | `"Invalid data."` |
| Pass / Fail | ✅ PASS |

### Notes
- Server returns 400 instead of 404 for a non-existent category name.
- Error message "Invalid data." is generic and does not explicitly state
  that the category was not found — less descriptive than expected.
- No `fields` object in response body, unlike 422 validation errors.
- When writing automation assertions, assert on both status code (400)
  and exact msg value ("Invalid data.") to distinguish from other 400 errors.

---

## TC-CAT-08 — Update Category — Missing newName Field

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-08 |
| **Title** | Send update request without the required `newName` field |
| **Method** | PUT |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
PUT {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Technology"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | Validation error message |
| `fields.newName` | Array containing error description for the `newName` field |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `422 Unprocessable Entity` |
| `msg` | `"Invalid data."` |
| `fields.newName` | `["Expected property 'newName' to be string but found: undefined"]` |
| Pass / Fail | ✅ PASS |

### Notes
- Consistent with TC-CAT-04: missing required fields always return 422
  with a `fields` object describing exactly which property failed and why.
- Error message pattern is identical: "Expected property '{field}' to be
  string but found: undefined" — useful for automation assertions.

---

## TC-CAT-09 — Delete Category — Exists

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-09 |
| **Title** | Delete an existing category by name |
| **Method** | DELETE |
| **Endpoint** | `/api/category-book/{name}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |
| **Precondition** | Category `"Sci-Fi & Fantasy"` exists (renamed in TC-CAT-06) |

### Request

```
DELETE {{base_url}}/api/category-book/Sci-Fi%20%26%20Fantasy
Authorization: Bearer {{access_token}}
```

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `200 OK` |
| `msg` | `"Category deleted successfully."` |
| Pass / Fail | ✅ PASS |

### Notes
- Response only returns `msg`, no deleted category object in the body.
- To verify deletion, call GET /api/category-book and confirm
  the name is no longer present in the list.

---

## TC-CAT-10 — Delete Category — Does Not Exist

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-10 |
| **Title** | Delete a category that does not exist in the system |
| **Method** | DELETE |
| **Endpoint** | `/api/category-book/{name}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |

### Request

```
DELETE {{base_url}}/api/category-book/NonExistentCategory_XYZ
Authorization: Bearer {{access_token}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `404 Not Found` |
| `msg` | Error message indicating the category was not found |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `404 Not Found` |
| `msg` | `"Category not found."` |
| Pass / Fail | ✅ PASS |

### Notes
- Unlike TC-CAT-07 (PUT with non-existent name returns 400 "Invalid data."),
  DELETE returns a proper 404 with a clear "Category not found." message.
- Inconsistency detected: PUT and DELETE handle non-existent category
  differently — worth noting for automation assertions.

---

## TC-CAT-11 — Create Category — Whitespace-Only Name

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-11 |
| **Title** | Create a category with a whitespace-only string as the name |
| **Method** | POST |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | Medium |

### Request

```
POST {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "   "
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` or `422 Unprocessable Entity` |
| `msg` | Error message indicating name cannot be blank or whitespace-only |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | `"Category already exists."` |
| Pass / Fail | ❌ FAIL |

### Notes
- 🐛 BUG CONFIRMED (same root cause as TC-CAT-05): server does not
  validate or trim whitespace-only names before processing.
- The 400 response is only because a category with name "   " already
  exists in the database — not due to any input validation.
- If no such category existed, the server would return 201 Created,
  allowing a whitespace-only string to become a valid category name.
- Consistent with TC-CAT-05 (empty string) — server treats any string,
  including blank and whitespace-only, as a valid category name.
- Expected behavior: server should trim input and reject blank/whitespace
  names with 422 before any DB lookup.

---

## TC-CAT-12 — Update Category — newName Already Exists

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-12 |
| **Title** | Rename a category to a name that already exists in the system |
| **Method** | PUT |
| **Endpoint** | `/api/category-book` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |
| **Precondition** | At least 2 categories exist — e.g. `"Technology"` and `"Fiction"` |

### Request

```
PUT {{base_url}}/api/category-book
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "name": "Technology",
    "newName": "Fiction"
}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` or `409 Conflict` |
| `msg` | Error message indicating the target name already exists |

### Actual Result

| Field | Actual |
|---|---|
| Status Code | `400 Bad Request` |
| `msg` | `"Invalid data."` |
| Pass / Fail | ✅ PASS |

### Notes
- Server correctly rejects renaming to an already existing name with 400.
- However, the error message "Invalid data." is identical to TC-CAT-07
  (updating a non-existent category) — two different error scenarios
  return the same generic message, making it impossible to distinguish
  the root cause from the response alone.
- Expected behavior: more specific messages such as
  "Category already exists." (for duplicate newName) would improve
  API usability and debuggability.

---

## TC-CAT-13 — Delete Category — Has Associated Books (bookCount > 0)

| Field | Detail |
|---|---|
| **Test Case ID** | TC-CAT-13 |
| **Title** | Delete a category that currently has books associated with it |
| **Method** | DELETE |
| **Endpoint** | `/api/category-book/{name}` |
| **Authentication** | Required (Bearer Token) |
| **Priority** | High |
| **Precondition** | A category with `bookCount > 0` exists — e.g. `"Fiction"` (bookCount: 83 from TC-CAT-01) |

### Request

```
DELETE {{base_url}}/api/category-book/Fiction
Authorization: Bearer {{access_token}}
```

### Expected Result

| Field | Expected |
|---|---|
| Status Code | `400 Bad Request` (blocked) **OR** `200 OK` (force deleted) |
| `msg` | Either an error preventing deletion, or a success confirmation |

> ⚠️ Behavior is undefined — this is an exploratory test to observe how the system handles this case.

### Actual Result

| Field | Actual |
|---|---|
| Status Code | |
| Response Body | |
| Pass / Fail | |

### Notes

---
