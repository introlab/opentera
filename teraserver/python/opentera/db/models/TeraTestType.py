from opentera.db.Base import db, BaseModel


tests_types_projects_table = db.Table('t_tests_types_projects', db.Column('id_tests_types', db.Integer, db.ForeignKey(
                                                                                  't_tests_types.id_test_type',
                                                                                  ondelete='cascade')),
                                      db.Column('id_project', db.Integer, db.ForeignKey('t_projects.id_project',
                                                                                        ondelete='cascade')))


class TeraTestType(db.Model, BaseModel):
    __tablename__ = 't_tests_types'
    id_test_type = db.Column(db.Integer, db.Sequence('id_test_type_sequence'), primary_key=True, autoincrement=True)
    test_type_name = db.Column(db.String, nullable=False, unique=False)
    test_type_prefix = db.Column(db.String(10), nullable=False, unique=False)
    test_type_definition = db.Column(db.String, nullable=False)

    test_type_projects = db.relationship("TeraProject", secondary=tests_types_projects_table)
