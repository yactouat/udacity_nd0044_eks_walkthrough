import unittest

from flaskr import create_app

class AppTestCase(unittest.TestCase):
    """This class represents the app's test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app("test")
        self.client = self.app.test_client

    def tearDown(self):
        """Hook executed after each test"""
        pass

    def test_get_base_url_200(self):
        """Given a web user,
        when he hits / with a get request,
        then the response should have a status code of 200
        and it should show that the API is up"""
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.json["data"])
        self.assertEqual(res.json["msg"], "API is up")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
