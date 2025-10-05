# Mail Client Service

Thin FastAPI wrapper over the email client via dependency injection.

**Exposes endpoints:**
- `GET /messages`
- `GET /messages/{id}`
- `POST /messages/{id}/mark-as-read`
- `DELETE /messages/{id}`