from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraUserPreference import TeraUserPreference
from opentera.db.models.TeraUser import TeraUser
import json
from sqlalchemy import exc
from modules.FlaskModule.FlaskModule import flask_app


class TeraUserPreferenceTest(BaseModelsTest):

    def test_default_user_preference_for_openteraplus(self):
        with flask_app.app_context():
            preference: TeraUserPreference = TeraUserPreference.get_user_preferences_for_app('openteraplus')
            self.assertIsNotNone(preference)
            self.assertEqual(preference.user_preference_app_tag,'openteraplus')
            json_user_preferences = json.loads(preference.user_preference_preference)
            self.assertIsInstance(json_user_preferences, dict)
            self.assertTrue('language' in json_user_preferences)
            self.assertTrue('notification_sounds' in json_user_preferences)

    def test_default_user_preference_for_anotherapp(self):
        with flask_app.app_context():
            preference: TeraUserPreference = TeraUserPreference.get_user_preferences_for_app('anotherapp')
            self.assertIsNotNone(preference)
            self.assertEqual(preference.user_preference_app_tag,'anotherapp')
            json_user_preferences = json.loads(preference.user_preference_preference)
            self.assertIsInstance(json_user_preferences, dict)
            self.assertTrue('gui_style' in json_user_preferences)
            self.assertTrue('auto_save' in json_user_preferences)

    def test_default_user_preference_for_openteraplus_multiple(self):
        with flask_app.app_context():
            preferences: list[TeraUserPreference] = TeraUserPreference.query.filter_by(user_preference_app_tag='openteraplus').all()
            self.assertEqual(2, len(preferences))
            self.assertNotEqual(preferences[0].id_user, preferences[1].id_user)
            for preference in preferences:
                self.assertIsNotNone(preference)
                self.assertEqual(preference.user_preference_app_tag, 'openteraplus')
                json_user_preferences = json.loads(preference.user_preference_preference)
                self.assertIsInstance(json_user_preferences, dict)
                self.assertTrue('language' in json_user_preferences)
                self.assertTrue('notification_sounds' in json_user_preferences)

            super_admin: TeraUser = TeraUser.get_user_by_username('admin')
            site_admin: TeraUser = TeraUser.get_user_by_username('siteadmin')
            self.assertIsNotNone(super_admin)
            self.assertIsNotNone(site_admin)

            self.assertEqual(
                TeraUserPreference.get_user_preferences_for_user_and_app(super_admin.id_user, 'openteraplus'),
                preferences[0])

            self.assertEqual(
                TeraUserPreference.get_user_preferences_for_user_and_app(site_admin.id_user, 'openteraplus'),
                preferences[1])

    def test_user_preference_null_id_user(self):
        with flask_app.app_context():
            preference: TeraUserPreference = TeraUserPreference()
            preference.user_preference_app_tag = 'myapp'
            preference.user_preference_preference = json.dumps({'my_super_key': 'my_super_value'})
            self.db.session.add(preference)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_user_preference_null_app_tag(self):
        with flask_app.app_context():
            preference: TeraUserPreference = TeraUserPreference()
            preference.id_user = 1  # admin
            preference.user_preference_preference = json.dumps({'my_super_key': 'my_super_value'})
            self.db.session.add(preference)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_user_preference_null_preference(self):
        with flask_app.app_context():
            preference: TeraUserPreference = TeraUserPreference()
            preference.id_user = 1  # admin
            preference.user_preference_app_tag = 'myapp'
            self.db.session.add(preference)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_to_json(self):
        with flask_app.app_context():
            preference: TeraUserPreference = TeraUserPreference()
            preference.id_user_preference = 0
            preference.id_user = 1  # admin
            preference.user_preference_app_tag = 'myapp'
            preference.user_preference_preference = json.dumps({'my_super_key': 'my_super_value'})
            json_output = preference.to_json()
            self._check_json(preference, json_output, minimal=False)
            new_preference = TeraUserPreference()
            new_preference.from_json(json_output)
            self.assertEqual(preference.id_user_preference, new_preference.id_user_preference)
            self.assertEqual(preference.id_user, new_preference.id_user)
            self.assertEqual(preference.user_preference_app_tag, new_preference.user_preference_app_tag)
            self.assertEqual(preference.user_preference_preference, new_preference.user_preference_preference)

    def _check_json(self, preference: TeraUserPreference, preference_dict: dict, minimal=False):
        self.assertGreaterEqual(preference_dict['id_user_preference'], preference.id_user_preference)
        self.assertEqual(preference_dict['id_user'], preference.id_user)
        self.assertEqual(preference_dict['user_preference_app_tag'], preference.user_preference_app_tag)
        self.assertEqual(preference_dict['user_preference_preference'], preference.user_preference_preference)
        self.assertFalse('user_preference_user' in preference_dict)

        if minimal:
            pass

    def test_insert_or_update_or_delete_user_preference(self):
        with flask_app.app_context():
            # Insert
            TeraUserPreference.insert_or_update_or_delete_user_preference(user_id=1, app_tag='newapp',
                                                                          prefs={'key': 'value'})

            self.assertIsNotNone(TeraUserPreference.get_user_preferences_for_user_and_app(1,'newapp'))

            # Update
            TeraUserPreference.insert_or_update_or_delete_user_preference(user_id=1, app_tag='newapp',
                                                                          prefs={'key': 'newvalue'})
            self.assertIsNotNone(TeraUserPreference.get_user_preferences_for_user_and_app(user_id=1, app_tag='newapp'))

            preference: TeraUserPreference = TeraUserPreference.get_user_preferences_for_user_and_app(user_id=1,
                                                                                                      app_tag='newapp')
            self.assertIsNotNone(preference)
            self.assertEqual(json.loads(preference.user_preference_preference), {'key': 'newvalue'})

            # Delete
            TeraUserPreference.insert_or_update_or_delete_user_preference(user_id=1, app_tag='newapp', prefs=None)

            preference: TeraUserPreference = TeraUserPreference.get_user_preferences_for_user_and_app(user_id=1,
                                                                                                      app_tag='newapp')
            self.assertEqual(None, preference)
