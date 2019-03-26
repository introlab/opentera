import unittest
from libtera.db.DBManager import DBManager
from libtera.db.models.TeraUser import TeraUser, TeraUserTypes
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.Base import db
import uuid
import os
from passlib.hash import bcrypt


class TeraUserTest(unittest.TestCase):

    filename = 'TeraUserTest.db'

    SQLITE = {
        'filename': filename
    }

    man = DBManager()

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.man.open_local(self.SQLITE)
        self.man.create_defaults()

    def tearDown(self):
        pass

    def test_groups(self):
        pass
        # usergroup_name
        # usergroup_users
        # usergroup_access
        # group1 = TeraUserGroup()
        # group1.usergroup_name = 'TestGroup1'
        # access1 = TeraAccess('TestGroup1:admin', True, True, True, True)
        # group1.usergroup_access.append(access1)
        # db.session.add(group1)
        #
        # group2 = TeraUserGroup()
        # group2.usergroup_name = 'TestGroup2'
        # access2 = TeraAccess('TestGroup2:admin', True, True, True, True)
        # group2.usergroup_access.append(access2)
        # db.session.add(group2)
        #
        # user1 = TeraUser()
        # user1.user_enabled = True
        # user1.user_firstname = "User1_FirstName"
        # user1.user_lastname = "User1_LastName"
        # user1.user_profile = ""
        # user1.user_password = bcrypt.hash("admin")
        # user1.user_superadmin = True
        # user1.user_type = TeraUserTypes.USER.value
        # user1.user_username = "user1"
        # user1.user_uuid = str(uuid.uuid4())
        #
        # user1.user_usergroups.append(group1)
        # user1.user_usergroups.append(group2)
        # db.session.add(user1)
        #
        # user2 = TeraUser()
        # user2.user_enabled = True
        # user2.user_firstname = "User2_FirstName"
        # user2.user_lastname = "User2_LastName"
        # user2.user_profile = ""
        # user2.user_password = bcrypt.hash("admin")
        # user2.user_superadmin = True
        # user2.user_type = TeraUserTypes.USER.value
        # user2.user_username = "user2"
        # user2.user_uuid = str(uuid.uuid4())
        #
        # user2.user_usergroups.append(group1)
        #
        # db.session.add(user2)
        #
        # db.session.commit()
        #
        # filter_args = dict()
        #
        # print(TeraUser.get_all_user_access(user1.user_uuid))
        # print(TeraUser.get_all_user_access(user2.user_uuid))

