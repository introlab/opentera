from libtera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from libtera.db.models.TeraSession import TeraSessionStatus


class TeraSessionForm:

    @staticmethod
    def get_session_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("session")

        # Building lists
        # Session types
        ses_types = user_access.get_accessible_session_types()
        st_list = []
        for st in ses_types:
            st_list.append(TeraFormValue(value_id=st.id_session_type, value=st.session_type_name))

        # Users
        users = user_access.get_accessible_users()
        users_list = []
        for user in users:
            users_list.append(TeraFormValue(value_id=user.id_user, value=user.get_fullname()))

        # Devices
        devices = user_access.get_accessible_devices()
        devices_list = list()
        for device in devices:
            devices_list.append(TeraFormValue(value_id=device.id_device, value=device.device_name))

        # Participants
        participants = user_access.get_accessible_participants()
        parts_list = list()
        for part in participants:
            parts_list.append(TeraFormValue(value_id=part.id_participant, value=part.participant_name))

        # Services
        services = user_access.get_accessible_services()
        services_list = list()
        for service in services:
            services_list.append(TeraFormValue(value_id=service.id_service, value=service.service_name))

        # Session status
        status_list = []
        for status in TeraSessionStatus:
            # Translation is done here, since we have to proper language context
            status_name = gettext('Unknown')
            if status.value == TeraSessionStatus.STATUS_CANCELLED.value:
                status_name = gettext('Cancelled')
            if status.value == TeraSessionStatus.STATUS_COMPLETED.value:
                status_name = gettext('Completed')
            if status.value == TeraSessionStatus.STATUS_INPROGRESS.value:
                status_name = gettext('In progess')
            if status.value == TeraSessionStatus.STATUS_NOTSTARTED.value:
                status_name = gettext('Planned')
            if status.value == TeraSessionStatus.STATUS_TERMINATED.value:
                status_name = gettext('Interrupted')

            status_list.append(TeraFormValue(value_id=status.value, value=status_name))

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_session", gettext("Session ID"), "hidden", True))
        section.add_item(TeraFormItem("session_uuid", gettext("Session UUID"), "hidden", True))
        section.add_item(TeraFormItem("session_name", gettext("Session Name"), "text", True))
        section.add_item(TeraFormItem("id_session_type", gettext("Session Type"), "array", True, item_values=st_list))
        section.add_item(TeraFormItem('session_creator_user', gettext('Session User Creator'), 'hidden', False))
        section.add_item(TeraFormItem("id_creator_user", gettext("Session User Creator"), "array", True,
                                      item_values=users_list, item_options={"readonly": True},
                                      item_condition=TeraFormItemCondition(condition_item='session_creator_user',
                                                                           condition_operator='NOT NULL',
                                                                           condition_condition=None)))
        section.add_item(TeraFormItem('session_creator_device', gettext('Session Creator Device'), 'hidden', False))
        section.add_item(TeraFormItem("id_creator_device", gettext("Session Creator Device ID"), "array", True,
                                      item_values=devices_list, item_options={"readonly": True},
                                      item_condition=TeraFormItemCondition(condition_item='session_creator_device',
                                                                           condition_operator='NOT NULL',
                                                                           condition_condition=None)
                                      ))
        section.add_item(TeraFormItem('session_creator_participant', gettext('Session Creator Participant'), 'hidden',
                                      False))
        section.add_item(TeraFormItem("id_creator_participant", gettext("Session Creator Participant"), "array", True,
                                      item_values=parts_list, item_options={"readonly": True},
                                      item_condition=TeraFormItemCondition(condition_item='session_creator_participant',
                                                                           condition_operator='NOT NULL',
                                                                           condition_condition=None)))
        section.add_item(TeraFormItem('session_creator_service', gettext('Session Creator Service'), 'hidden',
                                      False))
        section.add_item(TeraFormItem("id_creator_service", gettext("Session Creator Service"), "array", True,
                                      item_values=services_list, item_options={"readonly": True},
                                      item_condition=TeraFormItemCondition(condition_item='session_creator_service',
                                                                           condition_operator='NOT NULL',
                                                                           condition_condition=None)))
        section.add_item(TeraFormItem("session_start_datetime", gettext("Start Date"), "datetime", True))
        section.add_item(TeraFormItem("session_duration", gettext("Duration"), "duration", True,
                                      item_options={"default": 0, "readonly": True}))
        # Session status is hidden as it needs to be handled elsewhere for now
        section.add_item(TeraFormItem("session_status", gettext("State"), "array", True, item_values=status_list))
        section.add_item(TeraFormItem("session_comments", gettext("Comments"), "longtext", False))

        # Hidden as handled elsewhere
        # section.add_item(TeraFormItem("session_participants", gettext("Participants"), "hidden", False))
        # section.add_item(TeraFormItem("session_users", gettext("Users"), "hidden", False))
        # section.add_item(TeraFormItem("session_devices", gettext("Devices"), "hidden", False))
        section.add_item(TeraFormItem("session_has_device_data", gettext("Session Has Device Data"), "hidden", False))

        return form.to_dict()
