import psycopg2

if __name__ == '__main__':

    # VARIABLES FOR THAT OPERATION
    opentera_id_site = 1    # OpenTera ID Site target
    teraplus_id_group = 19  # TeraPlus participant group to export as project in the selected site in OpenTera

    # Open connections to TeraPlus databases
    tera_conn = None
    tera_cursor = None
    try:
        tera_conn = psycopg2.connect(host="localhost", database="tera", user="postgres", password="admin")
        tera_cursor = tera_conn.cursor()
    except psycopg2.DatabaseError as e:
        print("Unable to connect to Tera database:" + e.args[0])
        exit(1)

    exas_conn = None
    exas_cursor = None
    try:
        exas_conn = psycopg2.connect(host="localhost", database="ExAS", user="postgres", password="admin")
        exas_cursor = exas_conn.cursor()
    except psycopg2.DatabaseError as e:
        print("Unable to connect to ExAS database:" + e.args[0])
        exit(1)

    # Create project in the site based on the selected participant group
    query = "SELECT * FROM t_groups WHERE id_group=%s"
    try:
        tera_cursor.execute(query, [teraplus_id_group])
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    teraplus_group = tera_cursor.fetchone()
    print("--> Creating project '" + teraplus_group[1] + "'...")
    # TODO Call project API to create project and store returned id
    # TODO Create "admin" access for that project and store usergroup id

    # Query for users for the specified participant group
    teraplus_usergroups = []

    print("** CREATING USERS **")
    query = "SELECT t_users.id_user, firstname, lastname, id_userid, t_users.id_usergroup FROM t_users " \
            "INNER JOIN t_users_groups ON t_users.id_usergroup = " \
            "t_users_groups.id_usergroup INNER JOIN t_user_group_access ON t_user_group_access.id_usergroup = " \
            "t_users_groups.id_usergroup WHERE id_group=%s and t_users.id_usergroup >1"
    try:
        tera_cursor.execute(query, [teraplus_id_group])
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    users = tera_cursor.fetchall()
    for user in users:
        user_id = user[0]
        user_firstname = user[1]
        user_lastname = user[2]
        user_uuid = user[3]
        user_usergroup = user[4]
        if user_usergroup not in teraplus_usergroups:
            teraplus_usergroups.append(user_usergroup)

        # Query username (pseudo) from exas database
        query = "SELECT user_pseudo, user_email FROM t_account WHERE user_uuid=%s"
        try:
            exas_cursor.execute(query, [user_uuid])
        except(Exception, psycopg2.Error) as error:
            print("SQL error: " + error.args[0])
            exit(1)
        account = exas_cursor.fetchone()
        if not account:
            print("No valid account for user " + user_firstname + " " + user_lastname)
            exit(1)
        user_name = account[0]
        user_email = account[1]

        print("--> Creating user '" + user_firstname + " " + user_lastname + " (" + user_name + ")'...")
        # TODO: Create user in OpenTera, if not already there (check username)
        # TODO: Assign user to project admin user group

    # Query for sessions types
    print("** CREATING SESSION TYPES **")
    query = "SELECT * FROM t_sessions_types INNER JOIN t_session_type_access ON " \
            "t_sessions_types.id_ses_type = t_session_type_access.id_session_type WHERE " \
            "id_usergroup IN(%s)"
    try:
        tera_cursor.execute(query, teraplus_usergroups)
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    sessions_types = tera_cursor.fetchall()
    tera_open_session_type_map = {}
    for session_type in sessions_types:
        session_type_id = session_type[0]
        if session_type_id not in tera_open_session_type_map:
            session_type_name = session_type[1]
            session_type_online = session_type[5]
            session_type_color = session_type[6]
            print("--> Creating session type '" + session_type_name + "' (online: " + str(session_type_online) + ")...")
            # TODO Create session type and associate it with the project
            # tera_open_session_type_map[session_type_id] =

    # Query for participants in the specified participant group
    print("** CREATING PARTICIPANTS **")
    query = "SELECT * FROM t_patients WHERE id_group=%s"
    try:
        tera_cursor.execute(query, [teraplus_id_group])
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    participants = tera_cursor.fetchall()
    for participant in participants:
        part_id = participant[0]
        part_name = participant[1]
        part_create_date = participant[2]
        part_active = (participant[3] is not None)

        print("--> Creating participant '" + part_name + "' (active: " + str(part_active) + ")...")
        # TODO: Create participant in project

        # Query for sessions for current participant
        query = "SELECT * FROM t_sessions INNER JOIN t_sessions_dates ON t_sessions.id_session_date = " \
                "t_sessions_dates.id_session_date INNER JOIN v_sessions_duration ON t_sessions.id_session = " \
                "v_sessions_duration.id_session WHERE id_patient = %s"
        try:
            tera_cursor.execute(query, [part_id])
        except(Exception, psycopg2.Error) as error:
            print("SQL error: " + error.args[0])
            exit(1)

        sessions = tera_cursor.fetchall()
        for session in sessions:
            session_id = session[0]
            session_name = session[1]
            session_datetime = session[2]
            session_status = session[3]     # Status code are the same between TeraPlus and OpenTera!
            session_type = session[4]
            session_id_user = session[5]
            session_comments = session[6]
            session_duration = session[10]
            print("---> Creating session '" + session_name + "' (" + session_datetime.isoformat() + ")...")
            # TODO: Create session

            # Query sessions logs for that session
            query = "SELECT * FROM t_sessions_logs WHERE id_session = %s"
            try:
                tera_cursor.execute(query, [session_id])
            except(Exception, psycopg2.Error) as error:
                print("SQL error: " + error.args[0])
                exit(1)

            sessions_logs = tera_cursor.fetchall()
            for log in sessions_logs:
                session_log_date = log[3]
                session_log_text = log[4]
                session_log_type = log[2]
                # Convert logtype to SessionEventType
                # SESSIONLOG_NONE=0 --> GENERAL_ERROR=0
                # SESSIONLOG_START=1 --> SESSION_START = 3
                # SESSIONLOG_STOP=2 --> SESSION_STOP = 4
                # SESSIONLOG_DISCONNECT=3 --> SESSION_STOP = 4
                # SESSIONLOG_PAUSE=4 --> SESSION_STOP = 4
                # SESSIONLOG_NEWTEST=5 --> GENERAL_INFO = 1
                # SESSIONLOG_DELETETEST=6 --> GENERAL_INFO = 1
                # SESSIONLOG_EDITTEST=7 --> GENERAL_INFO = 1
                # SESSIONLOG_LOCKTEST=8 --> GENERAL_INFO = 1
                # SESSIONLOG_UNLOCKTEST=9 --> GENERAL_INFO = 1
                # SESSIONLOG_DELETEDATA=10 --> GENERAL_INFO = 1
                if session_log_type == 1:
                    session_log_type = 3
                elif session_log_type == 2 or session_log_type == 3 or session_log_type == 4:
                    session_log_type = 4
                else:
                    session_log_type = 1

                # TODO: Create session event
                print("----> Creating session event '" + session_log_text + "' (" + session_log_date.isoformat() +
                      ")...")

    tera_cursor.close()
    exas_cursor.close()
    tera_conn.close()
    exas_conn.close()
    exit(0)
