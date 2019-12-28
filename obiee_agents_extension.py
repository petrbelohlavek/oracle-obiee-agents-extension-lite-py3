import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])))
import obiee_catalog_filesystem
import configparser
config_parser = configparser.ConfigParser()
config_parser.read('obiee_settings.cfg')


def main(argv=None):
    if len(sys.argv) == 2:
        if (sys.argv[1] == 'to_file') or (sys.argv[1] == 'to_db_sqlplus') or (sys.argv[1] == 'to_db_sqlldr'):
            storing_method = sys.argv[1]
            if config_parser.get('OBIEE_catalog', 'path') != '':
                obiee_cat_fs_path = config_parser.get('OBIEE_catalog', 'path')
            else:
                obiee_cat_fs_path = '{}/__obiee_test_catalog'.format(os.path.abspath(os.path.dirname(sys.argv[0])))
            obiee_cat_fs = obiee_catalog_filesystem.ObiCatalogFS(storing_method, obiee_cat_fs_path)
            if sys.argv[1] == 'to_file':
                obiee_cat_fs.load_agents_from_xml_to_file()
            elif sys.argv[1] == 'to_db_sqlplus':
                print('\nThis is lite version.')
            elif sys.argv[1] == 'to_db_sqlldr':
                print('\nThis is lite version.')
            obiee_cat_fs.set_parsing_end()
            obiee_cat_fs.write_stats_to_file()
            obiee_cat_fs.print_stats(obiee_cat_fs)
        else:
            print(
                '\nYou entered an unknown parameter: {}\nYou can enter the following parameters: to_file, '
                'to_db_sqlplus, to_db_sqlldr'.format(
                    sys.argv[1]))
    else:
        print(
            '\nYou did not enter a parameter.\nYou can enter the following parameters: to_file, to_db_sqlplus, '
            'to_db_sqlldr\nExample: python /home/obiee/obiee_agents_extension.py to_db_sqlldr')


if __name__ == "__main__":
    main(sys.argv)
    print('')
