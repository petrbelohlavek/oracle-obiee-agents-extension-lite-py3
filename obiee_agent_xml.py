from datetime import datetime
import os
import obiee_fields_transformation
import configparser


class ObieeAgentXml(object):
    def __init__(self, file_path=None, xml_tree_obiee_agent=None, xml_namespace_saw=None, xml_namespace_cond=None,
                 job_id=None):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read('obiee_settings.cfg')
        self.file_path = file_path
        self.xml_tree_obiee_agent = xml_tree_obiee_agent
        self.xml_namespace_saw = xml_namespace_saw
        self.xml_namespace_cond = xml_namespace_cond
        self.job_id = job_id
        self.report_ref = None
        self.email_recipients = []
        self.delivery_destinations = []
        self.action_j2ee_apps = []
        self.schedule_start_immediately = None
        self.schedule_start__file_insert = None
        self.schedule_start__sqlplus_insert = None
        self.file_created = datetime.fromtimestamp(os.path.getctime(self.file_path)).strftime('%Y-%m-%d %H:%M:%S')
        self.file_modified = datetime.fromtimestamp(os.path.getmtime(self.file_path)).strftime('%Y-%m-%d %H:%M:%S')

    def extract_data_from_xml_tree_to_object(self, obiee_ag_xml, storing_method):
        ns_mapping = {'saw': self.xml_namespace_saw, 'cond': self.xml_namespace_cond}

        elem_saw_deliverycontent__report_ref = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:choose/saw:when/saw:deliveryContent/saw:reportRef/@path',
            namespaces=ns_mapping)
        elem_saw_headline__report_ref = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:choose/saw:when/saw:deliveryContent/saw:headline/saw:reportRef/@path',
            namespaces=ns_mapping)
        elem_saw_deliverycontent__dashboardpage_ref = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:choose/saw:when/saw:deliveryContent/saw:dashboardPageRef/@dashboard',
            namespaces=ns_mapping)
        elem_cond_report_ref = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/cond:condition/cond:comparison/cond:rowcount/saw:reportRef/@path',
            namespaces=ns_mapping)
        elem_saw_deliverycontent_dispotion = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:choose/saw:when/saw:deliveryContent/@disposition',
            namespaces=ns_mapping)

        if len(elem_saw_deliverycontent__report_ref) != 0:
            self.report_ref = str(elem_saw_deliverycontent__report_ref[0])
        elif len(elem_saw_headline__report_ref) != 0:
            self.report_ref = str(elem_saw_headline__report_ref[0])
        elif len(elem_saw_deliverycontent__dashboardpage_ref) != 0:
            self.report_ref = str(elem_saw_deliverycontent__dashboardpage_ref[0])
        elif len(elem_saw_deliverycontent_dispotion) != 0:
            self.report_ref = str(elem_saw_deliverycontent_dispotion[0])
        else:
            self.report_ref = elem_cond_report_ref[0]

        elem_email_recipients = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:emailRecipients/saw:emailRecipient/@address',
            namespaces=ns_mapping)
        for elem_email_recipient in elem_email_recipients:
            self.email_recipients.append(str(elem_email_recipient))

        elem_delivery_destinations = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:deliveryDestinations/saw:destination/@category',
            namespaces=ns_mapping)
        for elem_delivery_destination in elem_delivery_destinations:
            self.delivery_destinations.append(str(elem_delivery_destination))

        elem_action_j2ee_apps = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:choose/saw:when/saw:postActions/saw:action/saw:implementation/saw:j2ee-app/text()',
            namespaces=ns_mapping)
        for elem_action_j2ee_app in elem_action_j2ee_apps:
            self.action_j2ee_apps.append(elem_action_j2ee_app)

        elem_schedule_start_date = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:schedule/saw:start/@date',
            namespaces=ns_mapping)
        elem_schedule_start_time = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:schedule/saw:start/@time',
            namespaces=ns_mapping)

        if (len(elem_schedule_start_date) != 0) and (len(elem_schedule_start_time) != 0):
            self.schedule_start__file_insert = str(elem_schedule_start_date[0]) + ' ' + str(elem_schedule_start_time[0])
            self.schedule_start__sqlplus_insert = "TO_TIMESTAMP('" + str(elem_schedule_start_date[0]) + ' ' + str(
                elem_schedule_start_time[0]) + "', 'YYYY-mm-dd HH24:MI:SS')"
        else:
            if storing_method == 'to_db_sqlldr':
                self.schedule_start__file_insert = '1900-01-01 12:00:00'
            else:
                self.schedule_start__file_insert = 'NULL'
            self.schedule_start__sqlplus_insert = 'NULL'

        elem_schedule_start_immediately = obiee_ag_xml.xml_tree_obiee_agent.xpath(
            '//saw:ibot/saw:schedule/saw:start/@startImmediately',
            namespaces=ns_mapping)

        if len(elem_schedule_start_immediately) != 0:
            if elem_schedule_start_immediately[0] == 'false':
                self.schedule_start_immediately = 'N'
            else:
                self.schedule_start_immediately = 'Y'
        else:
            self.schedule_start_immediately = 'N'

    def write_obiee_agent_from_object_to_report(self, report_file, obiee_ag_xml, fields_enclosed, fields_terminated):
        field_trans = obiee_fields_transformation.FieldsTransformation(fields_enclosed, fields_terminated)

        # reportRef
        report_file.write(field_trans.get_field_encl_term(obiee_ag_xml.job_id) + field_trans.get_field_encl_term(
            'reportRef') + field_trans.get_field_encl_term(obiee_ag_xml.report_ref) + field_trans.get_field_encl_term(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + field_trans.get_field_encl_term(
            obiee_ag_xml.file_modified) + field_trans.get_field_encl_term(
            self.schedule_start__file_insert) + field_trans.get_field_encl_newln(self.schedule_start_immediately))

        # emailRecipient
        for email_recipient in self.email_recipients:
            report_file.write(field_trans.get_field_encl_term(obiee_ag_xml.job_id) + field_trans.get_field_encl_term(
                'emailRecipient') + field_trans.get_field_encl_term(email_recipient) + field_trans.get_field_encl_term(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + field_trans.get_field_encl_term(
                obiee_ag_xml.file_modified) + field_trans.get_field_encl_term(
                self.schedule_start__file_insert) + field_trans.get_field_encl_newln(self.schedule_start_immediately))

        # filePath
        report_file.write(field_trans.get_field_encl_term(obiee_ag_xml.job_id) + field_trans.get_field_encl_term(
            'filePath') + field_trans.get_field_encl_term(obiee_ag_xml.file_path) + field_trans.get_field_encl_term(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + field_trans.get_field_encl_term(
            obiee_ag_xml.file_modified) + field_trans.get_field_encl_term(
            self.schedule_start__file_insert) + field_trans.get_field_encl_newln(self.schedule_start_immediately))

        # deliveryDestination
        for delivery_destination in self.delivery_destinations:
            report_file.write(field_trans.get_field_encl_term(obiee_ag_xml.job_id) + field_trans.get_field_encl_term(
                'deliveryDestination') + field_trans.get_field_encl_term(
                delivery_destination) + field_trans.get_field_encl_term(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + field_trans.get_field_encl_term(
                obiee_ag_xml.file_modified) + field_trans.get_field_encl_term(
                self.schedule_start__file_insert) + field_trans.get_field_encl_newln(self.schedule_start_immediately))

        # j2eeApp
        for action_j2ee_app in self.action_j2ee_apps:
            report_file.write(field_trans.get_field_encl_term(obiee_ag_xml.job_id) + field_trans.get_field_encl_term(
                'actionJ2eeApp') + field_trans.get_field_encl_term(action_j2ee_app) + field_trans.get_field_encl_term(
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + field_trans.get_field_encl_term(
                obiee_ag_xml.file_modified) + field_trans.get_field_encl_term(
                self.schedule_start__file_insert) + field_trans.get_field_encl_newln(self.schedule_start_immediately))
