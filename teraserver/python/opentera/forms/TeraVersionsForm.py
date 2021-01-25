from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from opentera.utils.TeraVersions import TeraVersions


class TeraVersionsForm:

    @staticmethod
    def get_versions_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("versions")

        # Building lists
        #################
        # None to build!

        # Sections
        section = TeraFormSection("infos", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("version_string", gettext("OpenTeraServer version string"), "hidden",
                                      item_required=True, item_options={"readonly": True}))

        section.add_item(TeraFormItem("version_major", gettext("OpenTeraServer major version number"), "text",
                                      item_required=True, item_options={"readonly": True}))

        section.add_item(TeraFormItem("version_minor", gettext("OpenTeraServer minor version number"), "text",
                                      item_required=True, item_options={"readonly": True}))

        section.add_item(TeraFormItem("version_patch", gettext("OpenTeraServer patch version number"), "text",
                                      item_required=True, item_options={"readonly": True}))

        # Load versions from DB
        versions = TeraVersions()
        versions.load_from_db()
        versions_dict = versions.to_dict()

        # One section per client.
        # TODO - Right way?
        for client_string in versions_dict['clients']:
            # Create a section for each client
            client = versions_dict['clients'][client_string]
            section_clients = TeraFormSection(client['client_name'], client['client_name'] + ' ' + gettext("Versions"))

            section_clients.add_item(TeraFormItem("client_name", gettext("Client name"), "text", item_required=True,
                                                  item_options={"readonly": True}))

            section_clients.add_item(TeraFormItem("client_description", gettext("Client description"), "longtext",
                                                  item_required=True, item_options={"readonly": True}))

            section_clients.add_item(TeraFormItem("client_version", gettext("Client version"), "text",
                                                  item_required=True, item_options={"readonly": True}))

            section_clients.add_item(TeraFormItem("client_documentation_url", gettext("Client documentation url"),
                                                  "text", item_required=True, item_options={"readonly": True}))

            section_clients.add_item(TeraFormItem("client_windows_download_url", gettext("Client windows version"),
                                                  "text", item_required=True, item_options={"readonly": True}))

            section_clients.add_item(TeraFormItem("client_mac_download_url", gettext("Client mac version"), "text",
                                                  item_required=True, item_options={"readonly": True}))

            section_clients.add_item(TeraFormItem("client_linux_download_url", gettext("Client linux version"), "text",
                                                  item_required=True, item_options={"readonly": True}))

            form.add_section(section_clients)

        return form.to_dict()
