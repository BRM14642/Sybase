from scr.automation.bitbucket import Bitbucket
from scr.automation.sybase import Sybase
from scr.automation.automation import Automation
from scr.utils.utils import get_default_value_to_string

def main():
    bitbucket = Bitbucket()
    #bitbucket.download_file("cr-tablas", "CRTIPOS.sql", "develop")

    #sybase = Sybase()
    #sybase.modify_table("CRTMPREH")

    automation = Automation()
    automation.add_fields_table()
    #print(get_default_value_to_string("double"))


if __name__ == "__main__":
    main()