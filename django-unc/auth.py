import ldap

from django.contrib.auth.models import User

"""
Thanks to the following sources of information for helping me figure this out:
http://www.carthage.edu/webdev/?p=12 -- django ldap auth backend
http://www.linuxjournal.com/article/6988 -- python ldap info
"""

# Constants
LDAP_SERVER = "ldap.unc.edu"
LDAP_USER = ""
LDAP_PASS = ""

class UNCLDAPBackend:
    """
Put 'django-unc.auth.UNCLDAPBackend', in your AUTHENTICATION_BACKENDS setting
in settings.py.
    """
    def authenticate(self, username=None, password=None):
        base = "dc=unc,dc=edu"
        scope = ldap.SCOPE_SUBTREE
        filter = "(&(objectClass=UNCPerson)(uid=%s))" % username
        ret = ['dn', 'givenName', 'mail', 'sn']

        # Authenticate base user to search
        try:
            l = ldap.open(LDAP_SERVER)
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(LDAP_USER,LDAP_PASS)
        except ldap.LDAPError:
            return None

        # Get info from ldap server
        try:
            result_id = l.search(base, scope, filter, ret)
            result_type, result_data = l.result(result_id, 0)

            # if user does not exist, fail
            if (len(result_data) != 1):
                return None
        
            # Bind to user's DN
            l.simple_bind_s(result_data[0][0], password)

            # Get further user info
            result_id = l.search(base, scope, filter, ret)
            result_type, result_data = l.result(result_id, 0)
            user_info = result_data[0][1]

            # If that didn't throw an exception, the user must have authed
            # and we can get or create a user object for the user.
            try:
                user = User.objects.get(username__exact=username)
            except:
                if 'mail' in user_info:
                    email = user_info['mail'][0]
                else:
                    email = "%s@email.unc.edu" % username
                if 'givenName' in user_info:
                    firstname = user_info['givenName'][0]
                else:
                    firstname = ''
                if 'sn' in user_info:
                    lastname = user_info['sn'][0]
                else:
                    lastname = ''
                temp_pass = User.objects.make_random_password(12)
                user = User.objects.create_user(username, email , temp_pass)
                user.first_name = firstname
                user.last_name = lastname
                user.is_staff = False
                user.save()
            # We've created a a user, now we return it to Django.
            return user
        except ldap.INVALID_CREDENTIALS:
            # We couldn't successfully auth against the LDAP server with the
            # supplied username and password, so we fail.
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
