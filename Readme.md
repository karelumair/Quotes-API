# Quotes API
sample REST API for Quotes!!

---
#### Technologies used:
- Flask
- MongoDB
---

## API Endpoints

### Quotes
```
http://localhost:5000/quotes/
```
##### Methods:
- GET: List all quotes
- POST: Create quote

```
http://localhost:5000/quotes/<quote_id>/
```
##### Methods:
- GET: Get single quote
- PUT: Update quote
- DELETE: Delete quote


### Authors
```
http://localhost:5000/authors/
```
##### Methods:
- GET: List all authors
- POST: Create author

```
http://localhost:5000/authors/<author_id>/
```
##### Methods:
- GET: Get single author
- PUT: Update author
- DELETE: Delete author


### Scrape
This API scrapes data and add it to the database.

**Scrape Quotes**
```
http://localhost:5000/scrape/quotes/
```
##### Methods:
- GET
- POST

**Scrape Authors**
```
http://localhost:5000/scrape/authors/
```
##### Methods:
- GET
- PUT
- DELETE
