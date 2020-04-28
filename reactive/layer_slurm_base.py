from charms.reactive import when, when_not
from charms.reactive import set_flag

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import application_version_set

from charms.slurm.helpers import get_slurm_version


@when('snap.installed.slurm')
@when_not('slurm.base.available')
def set_slurm_version():
    # Set Slurm version
    slurm_version = get_slurm_version()
    if slurm_version is not None:
        application_version_set(slurm_version)
    else:
        status_set('blocked', 'cannot get slurm version')
        return
    status_set('active', '')
    set_flag('slurm.base.available')
