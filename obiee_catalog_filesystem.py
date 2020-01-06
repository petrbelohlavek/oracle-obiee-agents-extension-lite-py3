import sys

print(sys.stdout.encoding)
if sys.version[0] == '2':
    from importlib import reload

    reload(sys)
    sys.setdefaultencoding('utf8')
import os
from datetime import datetime
from lxml import etree
import obiee_agent_xml
import obiee_fields_transformation
import configparser


class ObiCatalogFS(object):
    def __init__(self, storing_method, obiee_catalog_path):
        super(ObiCatalogFS, self).__init__()
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read('obiee_settings.cfg')
        self.obiee_catalog_path = obiee_catalog_path
        self.storing_method = storing_method
        self.xml_namespace_saw = 'com.siebel.analytics.web/report/v1.1'
        self.pattern_ignored_path = '/_delivers/_deliveries/'
        self.parsing_start_dt = datetime.now()
        self.parsing_end_dt = None
        self.time_duration_str = None
        self.report_abs_path = None
        self.report_datetime_str = self.parsing_start_dt.strftime('%Y-%m-%d_%H-%M-%S_')
        self.report_name = None
        self.report_file = None
        self.fields_enclosed = '~*~'
        self.fields_terminated = '\t\t'
        self.count_fs_objects = 0
        self.count_files_all = 0
        self.count_files_agent = 0
        self.count_files_others = 0
        self.count_files_ignored = 0
        # print('\nObject reference:\t\t\t\t{}'.format(str(self)))
        print('\nOBIEE catalog path:\t{}\n'.format(self.obiee_catalog_path))

    def set_parsing_end(self):
        self.parsing_end_dt = datetime.now()
        self.set_time_duration_str()

    def set_time_duration_str(self):
        self.time_duration_str = self.parsing_end_dt - self.parsing_start_dt
        self.time_duration_str = '{} sec'.format(str(self.time_duration_str.seconds))

    def print_stats(self, obiee_catalog_fs):
        print('Parsing start:\t\t\t\t\t{}'.format(str(self.parsing_start_dt.strftime('%Y-%m-%d %H:%M:%S'))))
        print('Parsing end:\t\t\t\t\t{}'.format(str(self.parsing_end_dt.strftime('%Y-%m-%d %H:%M:%S'))))
        print('Time duration:\t\t\t\t\t{}'.format(self.time_duration_str))
        print('Storing method:\t\t\t\t\t{}'.format(self.storing_method))
        print('Count of all filesystem objects:\t\t{}'.format(str(self.count_fs_objects)))
        print('Count of all directories:\t\t\t{}'.format(str(self.count_fs_objects - self.count_files_all)))
        print('Count of all files:\t\t\t\t{}'.format(str(self.count_files_all)))
        print('Count of files with an agent:\t\t\t{}'.format(str(self.count_files_agent)))
        print('Count of others files:\t\t\t\t{}'.format(str(self.count_files_others)))
        print('Count of ignored files (private folder):\t{}'.format(str(self.count_files_ignored)))

    def write_stats_to_file(self):
        stats_name_base = 'obiee_agents'
        stats_suffix = '.stats'
        stats_abs_path = self.report_abs_path
        stats_datetime = self.report_datetime_str
        stats_name = stats_datetime + stats_name_base + stats_suffix
        stats_file = open('{}/log/{}'.format(stats_abs_path, stats_name), "w")
        stats_file.write(
            'Parsing start:\t\t\t\t\t\t\t\t{}\n'.format(str(self.parsing_start_dt.strftime('%Y-%m-%d %H:%M:%S'))))
        stats_file.write(
            'Parsing end:\t\t\t\t\t\t\t\t{}\n'.format(str(self.parsing_end_dt.strftime('%Y-%m-%d %H:%M:%S'))))
        stats_file.write('Time duration:\t\t\t\t\t\t\t\t{}\n'.format(self.time_duration_str))
        stats_file.write('Loading method:\t\t\t\t\t\t\t\t{}\n'.format(self.storing_method))
        stats_file.write('Count of all filesystem objects:\t\t\t{}\n'.format(str(self.count_fs_objects)))
        stats_file.write(
            'Count of all directories:\t\t\t\t\t{}\n'.format(str(self.count_fs_objects - self.count_files_all)))
        stats_file.write('Count of all files:\t\t\t\t\t\t\t{}\n'.format(str(self.count_files_all)))
        stats_file.write('Count of files with an agent:\t\t\t\t{}\n'.format(str(self.count_files_agent)))
        stats_file.write('Count of others files:\t\t\t\t\t\t{}\n'.format(str(self.count_files_others)))
        stats_file.write('Count of ignored files (private folder):\t{}'.format(str(self.count_files_ignored)))

    def iter_obiee_catalog_fs(self, top_down=True):
        for root, dirs, files in os.walk(self.obiee_catalog_path, topdown=top_down):
            for file in os.listdir(root):
                if (self.obiee_catalog_path + '/shared' == root[0:len(self.obiee_catalog_path + '/shared')]) or (
                        self.obiee_catalog_path + '/users' == root[0:len(self.obiee_catalog_path + '/users')]):
                    yield os.path.join(root, file)

    def is_xml_file_obiee_agent(self, fs_object_path):
        if os.path.isdir(fs_object_path):
            return None
        else:
            self.count_files_all += 1
            if fs_object_path.find(self.pattern_ignored_path) == -1:
                if os.path.basename(fs_object_path).find('.') == -1:
                    try:
                        xml_tree = etree.parse(fs_object_path)
                        xml_root = xml_tree.getroot()
                        job_id = xml_root.attrib.get('jobID')
                        if job_id is None:
                            job_id = -1
                        """
                        # in py2:
                        if (xml_tree.getroot().iter().next().nsmap.get('saw') == self.xml_namespace_saw) and (
                                xml_root.tag[(len(xml_root.tag) - 4):] == 'ibot') and (int(job_id) >= 0):
                        """
                        if (xml_root.nsmap['saw'] == self.xml_namespace_saw) and (
                                xml_root.tag[(len(xml_root.tag) - 4):] == 'ibot') and (int(job_id) >= 0):
                            self.count_files_agent += 1

                            """
                            # in py2:
                            obiee_ag_xml = \
                                obiee_agent_xml.ObieeAgentXml(fs_object_path, xml_tree, self.xml_namespace_saw,
                                                              xml_tree.getroot().iter().next().nsmap.get('cond'),
                                                              job_id)
                            """

                            obiee_ag_xml = \
                                obiee_agent_xml.ObieeAgentXml(fs_object_path, xml_tree, self.xml_namespace_saw,
                                                              xml_root.nsmap['cond'], job_id)
                            print('FILE (AGENT):\t\t{}\n'.format(fs_object_path))
                            return obiee_ag_xml
                        else:
                            self.count_files_others += 1
                            print('FILE (not conditions):\t{}\n'.format(fs_object_path))
                            return None
                    except etree.XMLSyntaxError:
                        self.count_files_others += 1
                        print('FILE (not XML):\t\t{}\n'.format(fs_object_path))
                        return None
                else:
                    self.count_files_others += 1
                    print('FILE (has a dot):\t{}\n'.format(fs_object_path))
                    return None
            else:
                self.count_files_ignored += 1
                print('FILE (private):\t\t{}\n'.format(fs_object_path))
                return None

    def create_obiee_agents_report(self):
        report_name_base = 'obiee_agents'
        report_suffix = '.report'
        self.report_abs_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.report_name = self.report_datetime_str + report_name_base + report_suffix
        self.report_file = open('{}/log/{}'.format(self.report_abs_path, self.report_name), "w")
        field_trans = obiee_fields_transformation.FieldsTransformation(self.fields_enclosed, self.fields_terminated)
        first_line = field_trans.get_field_encl_term('JOB_ID') + \
                     field_trans.get_field_encl_term('PARAM') + \
                     field_trans.get_field_encl_term('VALUE') + \
                     field_trans.get_field_encl_term('INSERTED') + \
                     field_trans.get_field_encl_term('FILE_MODIFIED') + \
                     field_trans.get_field_encl_term('SCHEDULE_START') + \
                     field_trans.get_field_encl_term('START_IMMEDIATELY') + \
                     field_trans.get_field_encl_newln('VALID')
        self.report_file.write(first_line)

    def load_agents_from_xml_to_file(self):
        self.create_obiee_agents_report()
        for fs_object_path in self.iter_obiee_catalog_fs():
            self.count_fs_objects += 1
            obiee_ag_xml = self.is_xml_file_obiee_agent(fs_object_path)
            if obiee_ag_xml is not None:
                obiee_ag_xml.extract_data_from_xml_tree_to_object(obiee_ag_xml, self.storing_method)
                obiee_ag_xml.write_obiee_agent_from_object_to_report(self.report_file, obiee_ag_xml,
                                                                     self.fields_enclosed, self.fields_terminated)
