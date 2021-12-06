from opentera.db.Base import db, BaseModel


class TeraUserUserGroup(db.Model, BaseModel):
    __tablename__ = 't_users_users_groups'
    id_user_user_group = db.Column(db.Integer, db.Sequence('id_user_user_group_sequence'), primary_key=True,
                                   autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey("t_users.id_user", ondelete='cascade'), nullable=False)
    id_user_group = db.Column(db.Integer, db.ForeignKey("t_users_groups.id_user_group"),
                              nullable=False)

    user_user_group_user = db.relationship("TeraUser", viewonly=True)
    user_user_group_user_group = db.relationship("TeraUserGroup", viewonly=True)  # Fun variable name!

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['user_user_group_user', 'user_user_group_user_group'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraUser import TeraUser
            from opentera.db.models.TeraUserGroup import TeraUserGroup
            user1 = TeraUser.get_user_by_username('siteadmin')
            user2 = TeraUser.get_user_by_username('user')
            user3 = TeraUser.get_user_by_username('user2')
            user4 = TeraUser.get_user_by_username('user3')
            group1 = TeraUserGroup.get_user_group_by_group_name("Users - Projects 1 & 2")
            group2 = TeraUserGroup.get_user_group_by_group_name("Admins - Project 1")
            group3 = TeraUserGroup.get_user_group_by_group_name("Admins - Default Site")
            group4 = TeraUserGroup.get_user_group_by_group_name("Users - Project 1")

            user_ug = TeraUserUserGroup()
            user_ug.id_user = user1.id_user
            user_ug.id_user_group = group3.id_user_group
            db.session.add(user_ug)

            user_ug = TeraUserUserGroup()
            user_ug.id_user = user2.id_user
            user_ug.id_user_group = group1.id_user_group
            db.session.add(user_ug)

            user_ug = TeraUserUserGroup()
            user_ug.id_user = user3.id_user
            user_ug.id_user_group = group4.id_user_group
            db.session.add(user_ug)

            user_ug = TeraUserUserGroup()
            user_ug.id_user = user3.id_user
            user_ug.id_user_group = group3.id_user_group
            db.session.add(user_ug)

            user_ug = TeraUserUserGroup()
            user_ug.id_user = user4.id_user
            user_ug.id_user_group = group2.id_user_group
            db.session.add(user_ug)

            db.session.commit()

    @staticmethod
    def get_user_user_group_by_id(user_user_group_id: int):
        return TeraUserUserGroup.query.filter_by(id_user_user_group=user_user_group_id).first()

    @staticmethod
    def query_users_for_user_group(user_group_id: int):
        return TeraUserUserGroup.query.filter_by(id_user_group=user_group_id).all()

    @staticmethod
    def query_users_groups_for_user(user_id: int):
        return TeraUserUserGroup.query.filter_by(id_user=user_id).all()

    @staticmethod
    def query_user_user_group_for_user_user_group(user_id: int, user_group_id: int):
        return TeraUserUserGroup.query.filter_by(id_user=user_id, id_user_group=user_group_id).first()

    @staticmethod
    def insert_user_user_group(id_user_group: int, id_user: int):
        new_uug = TeraUserUserGroup()
        new_uug.id_user_group = id_user_group
        new_uug.id_user = id_user

        db.session.add(new_uug)
        db.session.commit()

        return new_uug
