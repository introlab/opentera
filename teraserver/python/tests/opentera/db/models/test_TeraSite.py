import os
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.Base import db

from opentera.db.models.TeraSite import TeraSite


class TeraSiteTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraSiteTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_nullable_args(self):
        new_site = TeraSite()
        new_site.site_name = None
        db.session.add(new_site)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_unique_args(self):
        new_site1 = TeraSite()
        same_site1 = TeraSite()
        new_site1.site_name = None
        same_site1.site_name = None
        db.session.add(new_site1)
        db.session.add(same_site1)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_to_json(self):
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        db.session.add(new_site)
        db.session.commit()
        new_site_json = new_site.to_json()
        new_site_json_minimal = new_site.to_json(minimal=True)
        self.assertEqual(new_site_json['site_name'], 'Site Name')
        self.assertGreaterEqual(new_site_json['id_site'], 1)
        self.assertEqual(new_site_json_minimal['site_name'], 'Site Name')
        self.assertGreaterEqual(new_site_json_minimal['id_site'], 1)
        # Minimal doesnt change ignore fields

    def test_to_json_create_event(self):
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        db.session.add(new_site)
        db.session.commit()
        db.session.rollback()
        new_site_json = new_site.to_json_create_event()
        self.assertEqual(new_site_json['site_name'], 'Site Name')
        self.assertGreaterEqual(new_site_json['id_site'], 1)

    def test_to_json_update_event(self):
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        db.session.add(new_site)
        db.session.commit()
        db.session.rollback()
        new_site_json = new_site.to_json_update_event()
        self.assertEqual(new_site_json['site_name'], 'Site Name')
        self.assertGreaterEqual(new_site_json['id_site'], 1)

    def test_to_json_delete_event(self):
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        db.session.add(new_site)
        db.session.commit()
        new_site_json_delete = new_site.to_json_delete_event()
        self.assertGreaterEqual(new_site_json_delete['id_site'], 1)

    def test_get_site_by_sitename(self):
        db.session.rollback()
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        db.session.add(new_site)
        same_site = TeraSite.get_site_by_sitename(sitename='Site Name')
        self.assertEqual(new_site, same_site)

    def test_get_site_by_id(self):
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        db.session.add(new_site)
        db.session.commit()
        same_site = TeraSite.get_site_by_id(site_id=new_site.id_site)
        self.assertEqual(new_site, same_site)

    def test_insert_and_delete(self):
        new_site = TeraSite()
        new_site.site_name = 'Site Name'
        TeraSite.insert(site=new_site)
        self.assertGreaterEqual(new_site.id_site, 1)
        id_to_del = TeraSite.get_site_by_id(new_site.id_site).id_site
        TeraSite.delete(id_todel=id_to_del)
        Same_site = TeraSite()
        Same_site.site_name = 'Site Name'
        db.session.add(Same_site)
        db.session.commit()
