#!/usr/bin/env python
"""
CGNX script to manage BW Monitoring Configuration at one or more sites
tkamath@paloaltonetworks.com
"""
import sys
import os
import argparse
import cloudgenix

SCRIPT_NAME = "Manage Bandwidth Monitoring"
SCRIPT_VERSION = "v1.0"


# Import CloudGenix Python SDK
try:
    import cloudgenix
except ImportError as e:
    cloudgenix = None
    sys.stderr.write("ERROR: 'cloudgenix' python module required. (try 'pip install cloudgenix').\n {0}\n".format(e))
    sys.exit(1)

# Check for cloudgenix_settings.py config file in cwd.
sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN

except ImportError:
    # if cloudgenix_settings.py file does not exist,
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

try:
    # Also, separately try and import USERNAME/PASSWORD from the config file.
    from cloudgenix_settings import CLOUDGENIX_USER, CLOUDGENIX_PASSWORD

except ImportError:
    # will get caught below
    CLOUDGENIX_USER = None
    CLOUDGENIX_PASSWORD = None


# Handle differences between python 2 and 3. Code can use text_type and binary_type instead of str/bytes/unicode etc.
if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes



def cleanexit(cgx_session):
    print("INFO: Logging Out")
    cgx_session.get.logout()
    sys.exit()



site_id_name = {}
site_name_id = {}
nw_id_name = {}
label_id_name = {}
siteid_swilist = {}

def create_dicts(cgx_session, sitename):
    print("Creating Translation Dicts")
    #
    # Get Sites
    #
    print("\tSites")
    resp = cgx_session.get.sites()
    if resp.cgx_status:
        sitelist = resp.cgx_content.get("items", None)
        for site in sitelist:
            site_id_name[site["id"]] = site["name"]
            site_name_id[site["name"]] = site["id"]
    else:
        print("ERR: Could not retrieve Sites")
        cloudgenix.jd_detailed(resp)

    #
    # Validate Site Name Passed
    #
    sitelist = []
    if sitename == "ALL_SITES":
        sitelist = site_id_name.keys()

    elif sitename in site_name_id.keys():
        sitelist = [site_name_id[sitename]]

    else:
        print("ERR: Invalid Site Name: {}. Please re-enter sitename".format(sitename))
        cleanexit(cgx_session)

    #
    # Get WAN Interface Labels
    #
    print("\tWAN Interface Labels")
    resp = cgx_session.get.waninterfacelabels()
    if resp.cgx_status:
        labels = resp.cgx_content.get("items", None)
        for label in labels:
            label_id_name[label["id"]] = label["name"]
    else:
        print("ERR: Could not retrieve WAN Interface Labels")
        cloudgenix.jd_detailed(resp)
    #
    # Get WAN Networks
    #
    print("\tWAN Networks")
    resp = cgx_session.get.wannetworks()
    if resp.cgx_status:
        nws = resp.cgx_content.get("items", None)
        for nw in nws:
            nw_id_name[nw["id"]] = nw["name"]
    else:
        print("ERR: Could not retrieve WAN Networks")
        cloudgenix.jd_detailed(resp)

    return sitelist


def go():
    """
    Stub script entry point. Authenticates CloudGenix SDK, and gathers options from command line to run do_site()
    :return: No return
    """

    # Parse arguments
    parser = argparse.ArgumentParser(description="{0} ({1})".format(SCRIPT_NAME, SCRIPT_VERSION))

    ####
    #
    # Add custom cmdline argparse arguments here
    #
    ####

    custom_group = parser.add_argument_group('custom_args', 'My Custom Args')
    custom_group.add_argument("--print-lower", help="Print all in lower case",
                              default=False, action="store_true")

    ####
    #
    # End custom cmdline arguments
    #
    ####

    # Standard CloudGenix script switches.
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. https://api.elcapitan.cloudgenix.com",
                                  default=None)

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of cloudgenix_settings.py "
                                                   "or prompting",
                             default=None)
    login_group.add_argument("--password", "-PW", help="Use this Password instead of cloudgenix_settings.py "
                                                       "or prompting",
                             default=None)
    login_group.add_argument("--insecure", "-I", help="Do not verify SSL certificate",
                             action='store_true',
                             default=False)
    login_group.add_argument("--noregion", "-NR", help="Ignore Region-based redirection.",
                             dest='ignore_region', action='store_true', default=False)

    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--sdkdebug", "-D", help="Enable SDK Debug output, levels 0-2", type=int,
                             default=0)
    config_group = parser.add_argument_group('Config', 'These options are to provide site and BW monitoring details')
    config_group.add_argument("--sitename", "-S", help="Name of the Site. Or use keyword ALL_SITES", default="ALL_SITES")
    config_group.add_argument("--bwmon", "-B",
                              help="Enable or Disable BW Monitoring. Allowed values: True or False",
                              default=None)

    ############################################################################
    # Parse arguments provided via CLI
    ############################################################################
    args = vars(parser.parse_args())
    sdk_debuglevel = args["sdkdebug"]
    sitename = args["sitename"]
    bwmon = args["bwmon"]

    if bwmon not in ["True", "False"]:
        print("ERR: Invalid bwmon values. Please choose: True or False")
        sys.exit()

    if sitename is None:
        print("ERR: No site name provided. Please provide a site name or use the keyword: ALL_SITES")
        sys.exit()

    ############################################################################
    # Instantiate API & Login
    ############################################################################
    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=False)
    cgx_session.set_debug(sdk_debuglevel)
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, cgx_session.version, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # figure out user
    if args["email"]:
        user_email = args["email"]
    elif CLOUDGENIX_USER:
        user_email = CLOUDGENIX_USER
    else:
        user_email = None

    # figure out password
    if args["pass"]:
        user_password = args["pass"]
    elif CLOUDGENIX_PASSWORD:
        user_password = CLOUDGENIX_PASSWORD
    else:
        user_password = None

    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None
    ############################################################################
    # Create Translation Dicts
    ############################################################################
    sitelist = create_dicts(cgx_session, sitename)

    ############################################################################
    # Disable Bandwidth Monitoring
    ############################################################################
    for sid in sitelist:
        sname = site_id_name[sid]
        print("Retrieving circuits for site {}".format(sname))

        resp = cgx_session.get.waninterfaces(site_id=sid)
        if resp.cgx_status:
            swilist = resp.cgx_content.get("items", None)
            for swi in swilist:
                cname = swi["name"]
                if swi["name"] is None:
                    cname = "{}_{}".format(nw_id_name[swi["network_id"]], label_id_name[swi["label_id"]])

                if swi["bwc_enabled"]:
                    swi["bwc_enabled"] = False
                    resp = cgx_session.put.waninterfaces(site_id=sid, waninterface_id=swi["id"], data=swi)
                    if resp.cgx_status:
                        print("INFO: BW Monitoring Disabled on WAN Interface {} on site {}".format(cname, sname))

                    else:
                        print("ERR: Could not update WAN Interface {} on site {}".format(cname,sname))
                        cloudgenix.jd_detailed(resp)
                else:
                    print("INFO: BW Monitoring already Disabled on WAN Interface {} on site {}".format(cname, sname))
        else:
            print("ERR: Could not retrieve WAN Interfaces for site {}".format(sname))
            cloudgenix.jd_detailed(resp)

    ############################################################################
    # Logout to clear session.
    ############################################################################
    cleanexit(cgx_session)


if __name__ == "__main__":
    go()
