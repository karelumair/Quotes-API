"""Quote Tests"""

import unittest
from app import create_app
from database.models import Quote, Author


class QuoteTest(unittest.TestCase):
    """Quote Test Class"""

    def setUp(self):
        self.app = create_app("test")
        self.client = self.app.test_client()
        quote = Quote.objects().order_by("-createdOn").first()
        self.quote_id = quote.id if quote else None

    def test_get_all_quotes(self):
        "Test for get all Quotes"

        response = self.client.get("/quotes/")

        self.assertEqual(response.status_code, 200)

    def test_create_quote(self):
        """Test for create Quote"""

        author_id = Author.objects().first().id

        data = {
            "quote": "All code is guilty, until proven innocent.",
            "tags": ["code", "testing"],
            "author": str(author_id),
        }
        response = self.client.post("/quotes/", json=data)
        self.assertEqual(response.status_code, 201)

    def test_create_quote_invalid_author(self):
        """Test for creating quote with invalid author id"""

        data = {
            "quote": "All code is guilty, until proven innocent.",
            "tags": ["code", "testing"],
            "author": "63bfc7d1ee2902be104ed524",
        }
        response = self.client.post("/quotes/", json=data)
        self.assertEqual(response.status_code, 404)

    def test_create_invalid_quote(self):
        """Test for Error in POST method"""

        data = {"quote": "This must fail", "tags": "123"}
        response = self.client.post("/quotes/", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.get_json())

    def test_get_quote(self):
        """Test for get Quote"""

        response = self.client.get(f"/quotes/{self.quote_id}/")
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_quote_id(self):
        """Test for get invalid Quote ID"""

        response = self.client.get("/quotes/63bfb6768a1d693e61cd/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Error", response.get_json())

    def test_update_quote(self):
        """Test for updating Quote"""

        data = {"quote": "The Quote is Updated..."}
        response = self.client.put(f"/quotes/{self.quote_id}/", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quote.objects.get(id=self.quote_id).quote, data["quote"])

    def test_pydantic_update_quote(self):
        """Test for pydantic conversion"""

        data = {"quote": 123}
        response = self.client.put(f"/quotes/{self.quote_id}/", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quote.objects.get(id=self.quote_id).quote, str(data["quote"]))

    def test_update_invalid_quote_id(self):
        """Test for invalid Quote ID"""

        response = self.client.put("/quotes/63bfb6768a1d693e61cd/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.get_json())

    def test_delete_quote(self):
        """Test for deleting Quote ID"""

        response = self.client.delete(f"/quotes/{self.quote_id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_invalid_quote_id(self):
        """Test for deleting invalid Quote ID"""

        response = self.client.delete("/quotes/63bfb6768a1d693e61cd/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Error", response.get_json())


if __name__ == "__main__":
    unittest.main()
