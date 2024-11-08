from opentera.db.Base import BaseModel
from sqlalchemy import Column, Integer, String, Sequence

class EmailTemplate(BaseModel):
    __tablename__ = "t_email_templates"
    id_email_template = Column(Integer, Sequence('id_email_template_sequence'), primary_key=True, autoincrement=True)
    id_site = Column(Integer, nullable=True)
    id_project = Column(Integer, nullable=True)
    email_template_key = Column(String, nullable=False)
    email_template = Column(String, nullable=False)
    email_template_language = Column(String, nullable=False, default='en')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_template_by_id(id_template: int):
        return EmailTemplate.query.filter_by(id_email_template=id_template).first()

    @staticmethod
    def get_template_by_key(key: str, site_id: None | int = None, project_id: None | int = None, lang: str = 'en'):
        # Try to get with filters
        query = EmailTemplate.query.filter_by(email_template_key=key)
        if site_id:
            query = query.filter_by(id_site=site_id)
        if project_id:
            query = query.filter_by(id_project = project_id)

        query = query.filter_by(email_template_language = lang)
        template = query.first()

        if not template and (site_id or project_id):
            # Try to fall back to global template, if available
            template = EmailTemplate.query.filter_by(email_template_key=key, email_template_language=lang,
                                                     id_site=None, id_project=None).first()

        return template

    @staticmethod
    def get_templates_for_site(site_id: int, lang: str = 'en'):
        query = EmailTemplate.query.filter_by(id_site=site_id, email_template_language=lang)
        return query.all()

    @staticmethod
    def get_templates_for_project(project_id: int, lang: str = 'en'):
        query = EmailTemplate.query.filter_by(id_site=project_id, email_template_language=lang)
        return query.all()