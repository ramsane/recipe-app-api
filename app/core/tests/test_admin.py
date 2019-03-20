from django.test import TestCase
# importing get_user_model instead of just User is recommended because if
# we change the User model, then we don't have to change it everywhere
# because we are using this function and it returns the same.
from django.contrib.auth import get_user_model
# It is used to generate urls from the django admin page
from django.urls import reverse
# import test client that will that will allows test requests to our
# application in our unit tests
from django.test import Client


class AdminSiteTests(TestCase):

    def setUp(self):
        """ It will run before every test that we run. Some times we need to
        run somethings before running some tests. We can keep all such codes
        here.
        """
        # add a new user that we can use to test. Make sure the user
        # logged into our Client
        self.client = Client()
        # create a super user
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@ramana.com',
            password='test123'
        )
        # make the user log in automatically with django authentication by
        # using some helper function in Client
        self.client.force_login(self.admin_user)
        # create a normal user
        self.user = get_user_model().objects.create_user(
            email='ram@123.com',
            password='1234',
            name='Raman'
        )

    def test_users_listed(self):
        """Test that users are listed on user page in django-admin
        """
        url = reverse('admin:core_user_changelist')
        # response
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit works"""
        # make the url as 'admin/core/user'.
        url = reverse('admin:core_user_change', args=[self.user.id])
        # response from http get request
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)  # Is it Okay?

    def test_create_user_page(self):
        """Test that the create user page works"""
        # create the url from the app schema
        url = reverse('admin:core_user_add')
        # get the response from this url
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)