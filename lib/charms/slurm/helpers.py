import os
import textwrap
import subprocess

from charmhelpers.core.host import mkdir
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import log


SNAP_COMMON = "/var/snap/slurm/common"
SLURMD_SERVICE = 'slurm.slurmd'
SLURMCTLD_SERVICE = 'slurm.slurmctld'
SLURM_CONFIG_TEMPLATE = 'slurm.conf'
SLURM_CONFIG_DIR = f"{SNAP_COMMON}/etc/slurm"
SLURM_CONFIG_PATH = f'{SLURM_CONFIG_DIR}/slurm.conf'

MUNGE_SERVICE = 'munge'
MUNGE_KEY_TEMPLATE = 'munge.key'
MUNGE_KEY_PATH = f"{SNAP_COMMON}/etc/munge/munge.key"

DEFAULT_INCLUDE_CONFIG = textwrap.dedent("""\
            # This file is automatically distributed to the Slurm cluster by Juju.
            # To add configuration to this file, edit the file on the active
            # slurm controller and wait some minutes for the next update-status
            # hook.
            #
            # To find your active controller, look for ControlMachine and
            # ControlAddr in %s.
            #
            # To find the unit name of the active controller, run this command:
            # juju run -a slurm-controller 'leader-get active_controller'
        """ % SLURM_CONFIG_PATH)

GRES_CONFIG_TEMPLATE = 'gres.conf'
GRES_CONFIG_PATH = f'{SLURM_CONFIG_DIR}/gres.conf'


def render_slurm_config(context, active_controller=False):
    render(source=SLURM_CONFIG_TEMPLATE,
           target=SLURM_CONFIG_PATH,
           context=context,
           owner="root",
           group="root",
           perms=0o644)

    # Extract clustername from context, create empty config file
    clustername = context['clustername']
    slurmconf_include = '%s/slurm-%s.conf' % (SLURM_CONFIG_DIR, clustername)

    # If we're a node or backup controller, write the received include config
    # to disk (or create a dummy file)
    includecfg = context.get('include', DEFAULT_INCLUDE_CONFIG)

    if active_controller and os.path.exists(slurmconf_include):
        log('Active controller and include %s exists, not rendering'
                % slurmconf_include)
    else:
        with open(slurmconf_include, 'w') as f:
            f.write(includecfg)


def render_munge_key(context):
    render(source=MUNGE_KEY_TEMPLATE,
           target=MUNGE_KEY_PATH,
           context=context,
           owner="root",
           group="root",
           perms=0o400)

def render_gres_config(context):
    render(source=GRES_CONFIG_TEMPLATE,
        target=GRES_CONFIG_PATH,
        context=context,
        owner="root",
        group="root",
        perms=0o644)

def create_spool_dir(context):
    if not os.path.isdir(context.get('slurmd_spool_dir')):
        mkdir(path=context.get('slurmd_spool_dir'),
              owner="root",
              group="root",
              perms=0o750)


def create_state_save_location(context):
    if not os.path.isdir(context.get('state_save_location')):
        mkdir(path=context.get('state_save_location'),
              owner="root",
              group="root",
              perms=0o750)


def get_slurm_version():
    slurm_version = subprocess.check_output([
        "slurm.version",
    ]).decode().rstrip()
    return slurm_version
