from opentera.db.Base import db, BaseModel


class TeraUserPreference(db.Model, BaseModel):
    __tablename__ = 't_users_preferences'
    id_user_preference = db.Column(db.Integer, db.Sequence('id_userpreference_sequence'), primary_key=True,
                                   autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user', ondelete='cascade'), nullable=False)
    user_preference_app_tag = db.Column(db.String, nullable=False)
    user_preference_preference = db.Column(db.String, nullable=False)

    user_preference_user = db.relationship("TeraUser")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['user_preference_user'])
        if minimal:
            ignore_fields.extend([])
        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def get_user_preferences_for_app(app_tag: str):
        return TeraUserPreference.query.filter_by(user_preference_app_tag=app_tag).first()

    @staticmethod
    def get_user_preference_by_id(user_pref_id: int):
        return TeraUserPreference.query.filter_by(id_user_prefrence=user_pref_id).first()

    @staticmethod
    def get_user_preferences_for_user(user_id: int):
        return TeraUserPreference.query.filter_by(id_user=user_id).all()

    @staticmethod
    def get_user_preferences_for_user_and_app(user_id: int, app_tag: str):
        return TeraUserPreference.query.filter_by(id_user=user_id, user_preference_app_tag=app_tag).first()

    @staticmethod
    def create_defaults(test=False):

        if test:
            from opentera.db.models.TeraUser import TeraUser
            super_admin = TeraUser.get_user_by_username('admin')
            site_admin = TeraUser.get_user_by_username('siteadmin')

            new_pref = TeraUserPreference()
            new_pref.id_user = super_admin.id_user
            new_pref.user_preference_app_tag = 'openteraplus'
            new_pref.user_preference_preference = '{"language": "fr", "notification_sounds": true}'
            db.session.add(new_pref)

            new_pref = TeraUserPreference()
            new_pref.id_user = site_admin.id_user
            new_pref.user_preference_app_tag = 'openteraplus'
            new_pref.user_preference_preference = '{"language": "en", "notification_sounds": false}'
            db.session.add(new_pref)

            new_pref = TeraUserPreference()
            new_pref.id_user = super_admin.id_user
            new_pref.user_preference_app_tag = 'anotherapp'
            new_pref.user_preference_preference = '{"gui_style": 1, "auto_save": false}'
            db.session.add(new_pref)

    @staticmethod
    def insert_or_update_or_delete_user_preference(user_id: int, app_tag: str, prefs: str):
        if prefs:
            # Check if prefs is a valid json structure
            import json
            if not isinstance(prefs, dict):
                try:
                    json.loads(prefs)
                except ValueError as err:
                    raise err
            else:
                try:
                    prefs = json.dumps(prefs)
                except ValueError as err:
                    raise err

        # Check if we have an existing preference for that user
        existing_pref = TeraUserPreference.get_user_preferences_for_user_and_app(user_id=user_id, app_tag=app_tag)

        if existing_pref:
            # Update or delete
            if prefs is None or prefs == '':
                db.session.delete(existing_pref)
            else:
                # Updage pref
                existing_pref.user_preference_preference = prefs
        else:
            # Insert
            new_user_pref = TeraUserPreference()
            new_user_pref.id_user = user_id
            new_user_pref.user_preference_app_tag = app_tag
            new_user_pref.user_preference_preference = prefs
            db.session.add(new_user_pref)
        db.session.commit()
