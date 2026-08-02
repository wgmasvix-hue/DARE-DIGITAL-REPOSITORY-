# DSpace 9 Gutenberg Quick Start

**Quick reference for ingesting Gutenberg into DSpace 9 at repo.dare.co.zw**

---

## 🚀 5-Minute Setup

### 1. Get Admin Token

```bash
curl -X POST https://repo.dare.co.zw/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin@example.com","password":"password"}' | jq .token

# Save token
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Get Collection Handle

```bash
# List collections
curl -s https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {name, handle}'

# Save handle
export COLLECTION="123456789/10"
```

### 3. Run Ingest

```bash
chmod +x deploy/dspace_gutenberg_ingest.py

python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token $TOKEN \
  --collection $COLLECTION \
  --json gutenberg_data/gutenberg_books_latest.json
```

### 4. Verify

Go to: **https://repo.dare.co.zw/** → Search for "Gutenberg"

---

## 📊 What Gets Ingested

**18 Sample Books**:
- Shakespeare (complete works)
- Pride and Prejudice (Jane Austen)
- Alice in Wonderland (Lewis Carroll)
- Frankenstein (Mary Shelley)
- War and Peace (Leo Tolstoy)
- Crime and Punishment (Dostoevsky)
- Sherlock Holmes series
- A Tale of Two Cities (Dickens)
- And more classics...

**Metadata Captured**:
- ✅ Title, authors, language
- ✅ Publication date, subjects
- ✅ Download counts from Gutenberg
- ✅ Links to Gutenberg website
- ✅ Rights (Public Domain)

---

## 🔧 DSpace 9 Specifics

### API Endpoint
```
https://repo.dare.co.zw/server/api
```

### Authentication
- **Type**: JWT Bearer Token
- **Endpoint**: `/server/api/authn/login`
- **Method**: POST JSON
- **Returns**: `{token, name}`

### Item Creation
- **Endpoint**: `/server/api/core/items`
- **Method**: POST JSON
- **Headers**:
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`

### Collection Query
- **Endpoint**: `/server/api/core/collections`
- **Method**: GET
- **Returns**: Array of collections with handles

---

## 📁 Files Provided

| File | Purpose |
|------|---------|
| `deploy/dspace_gutenberg_ingest.py` | Main ingest tool |
| `deploy/deploy_dspace9_gutenberg.sh` | Setup verification script |
| `DSPACE_INGEST_GUIDE.md` | Detailed guide (700+ lines) |
| `gutenberg_data/gutenberg_books_latest.json` | 18 books ready to ingest |
| `gutenberg_data/gutenberg_books_latest.csv` | Alternative CSV format |

---

## ⚡ Common Commands

### Test Connection
```bash
curl -I https://repo.dare.co.zw/server/api
```

### Authenticate
```bash
curl -X POST https://repo.dare.co.zw/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin@example.com","password":"password"}'
```

### List Collections
```bash
curl -s https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Check Collection Size
```bash
curl -s https://repo.dare.co.zw/server/api/core/collections/123456789/10 \
  -H "Authorization: Bearer $TOKEN" | jq '{name, itemsCount}'
```

### Search Ingested Books
```bash
curl -s 'https://repo.dare.co.zw/server/api/discover/search?query=gutenberg' \
  -H "Authorization: Bearer $TOKEN" | jq '.results | length'
```

---

## 🔍 Verify Ingest

### Check Items
```bash
# List recently added items
curl -s 'https://repo.dare.co.zw/server/api/core/items?sort=dc.date.accessioned,desc' \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:3] | .[] | {handle, title: .metadata."dc.title"[0]}'
```

### Browse Web UI
1. Go to: https://repo.dare.co.zw/
2. Search: "Alice" or "Shakespeare"
3. Should see ingested items with metadata

### View Item Details
```bash
# Get specific item
curl -s https://repo.dare.co.zw/server/api/core/items/123456789/1 \
  -H "Authorization: Bearer $TOKEN" | jq '.metadata'
```

---

## 🐛 Troubleshooting

### "Invalid Token"
```bash
# Get fresh token
curl -X POST https://repo.dare.co.zw/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin@example.com","password":"password"}'
```

### "Collection Not Found"
```bash
# Verify collection handle
curl -s https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | select(.name | contains("Gutenberg")) | .handle'
```

### "Connection Refused"
```bash
# Check DSpace is running
curl -I https://repo.dare.co.zw/
# Check API is accessible
curl -I https://repo.dare.co.zw/server/api
```

### "Slow Ingest"
- Normal speed: ~0.5-1 item/second
- 18 books: ~30 seconds
- Full dataset (70k): ~15-20 hours
- Script rate-limits to be respectful to DSpace

---

## 📖 Full Documentation

For complete details, see: **DSPACE_INGEST_GUIDE.md**

Topics covered:
- Detailed authentication
- Collection management
- Testing procedures
- Error handling
- Post-ingest indexing
- Automated scheduling
- DSpace REST API reference

---

## ✅ Checklist

- [ ] DSpace 9 running at repo.dare.co.zw
- [ ] Admin credentials available
- [ ] Python 3.7+ installed
- [ ] `requests` module installed (`pip install requests`)
- [ ] Gutenberg data files present
- [ ] Ingest script is executable
- [ ] Got authentication token
- [ ] Verified collection handle
- [ ] Ran ingest script
- [ ] Verified items in DSpace UI

---

## 🎯 Next Steps

1. **Prepare**: Gather admin credentials for repo.dare.co.zw
2. **Authenticate**: Get API token using Step 1 above
3. **Verify**: Check collections exist using Step 2
4. **Ingest**: Run script from Step 3
5. **Test**: Search for "Gutenberg" in web UI
6. **Monitor**: Check `/server/api/discover/search` endpoint

---

**Ready to ingest!** Questions? See DSPACE_INGEST_GUIDE.md for detailed help.
