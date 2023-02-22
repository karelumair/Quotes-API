"""Author Tests"""

import unittest
from app import create_app
from database.models import Author


class AuthorTest(unittest.TestCase):
    """Author Test Class"""

    def setUp(self):
        self.app = create_app("test")
        self.client = self.app.test_client()
        author = Author.objects().order_by("-createdOn").first()
        self.author_id = author.id if author else None

    def test_get_all_authors(self):
        "Test for get all Authors"

        response = self.client.get("/authors/")

        self.assertEqual(response.status_code, 200)

    def test_create_author(self):
        """Test for create Author"""

        data = {
            "name": "Test User",
            "dob": "2000-12-1",
            "country": "India",
            "description": "Testing....",
        }
        response = self.client.post("/authors/", json=data)
        self.assertEqual(response.status_code, 201)

    def test_create_invalid_author(self):
        """Test for Error in POST method"""

        data = {"name": "In Complete", "description": "This is an incomplete body"}
        response = self.client.post("/authors/", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.get_json())

    def test_get_author(self):
        """Test for get Author"""

        response = self.client.get(f"/authors/{self.author_id}/")
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_author_id(self):
        """Test for get invalid Author ID"""

        response = self.client.get("/authors/63bfb6768a1d693e61cd/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Error", response.get_json())

    def test_update_author(self):
        """Test for updating Author"""

        data = {"name": "User Test"}
        response = self.client.put(f"/authors/{self.author_id}/", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.get(id=self.author_id).name, data["name"])

    def test_update_author_request_validation(self):
        """Test for pydantic conversion"""

        data = {"name": 123}
        response = self.client.put(f"/authors/{self.author_id}/", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.get(id=self.author_id).name, str(data["name"]))

    def test_update_invalid_author_id(self):
        """Test for invalid Author ID"""

        response = self.client.put("/authors/63bfb6768a1d693e61cd/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.get_json())

    def test_delete_author(self):
        """Test for deleting Author ID"""

        response = self.client.delete(f"/authors/{self.author_id}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_invalid_author_id(self):
        """Test for deleting invalid Author ID"""

        response = self.client.delete("/authors/63bfb6768a1d693e61cd/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Error", response.get_json())


if __name__ == "__main__":
    unittest.main()
