# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Portions Copyright Buildbot Team Members
#
# Portions Copyright (c) 2009, StatPro Italia srl

"""Fake implementation of the drmaa library for testing purposes."""

from collections import namedtuple
from functools import wraps


class errors:

    class DrmaaException(Exception):
        pass

    class AlreadyActiveSessionException(DrmaaException):
        pass

    class AuthorizationException(DrmaaException):
        pass

    class ConflictingAttributeValuesException(DrmaaException, AttributeError):
        pass

    class DefaultContactStringException(DrmaaException):
        pass

    class DeniedByDrmException(DrmaaException):
        pass

    class DrmCommunicationException(DrmaaException):
        pass

    class DrmsExitException(DrmaaException):
        pass

    class DrmsInitException(DrmaaException):
        pass

    class ExitTimeoutException(DrmaaException):
        pass

    class HoldInconsistentStateException(DrmaaException):
        pass

    class IllegalStateException(DrmaaException):
        pass

    class InternalException(DrmaaException):
        pass

    class InvalidAttributeFormatException(DrmaaException, AttributeError):
        pass

    class InvalidContactStringException(DrmaaException):
        pass

    class InvalidJobException(DrmaaException):
        pass

    class InvalidJobTemplateException(DrmaaException):
        pass

    class NoActiveSessionException(DrmaaException):
        pass

    class NoDefaultContactStringSelectedException(DrmaaException):
        pass

    class ReleaseInconsistentStateException(DrmaaException):
        pass

    class ResumeInconsistentStateException(DrmaaException):
        pass

    class SuspendInconsistentStateException(DrmaaException):
        pass

    class TryLaterException(DrmaaException):
        pass

    class UnsupportedAttributeException(DrmaaException, AttributeError):
        pass

    class InvalidArgumentException(DrmaaException, AttributeError):
        pass

    class InvalidAttributeValueException(DrmaaException, AttributeError):
        pass

    class OutOfMemoryException(DrmaaException, MemoryError):
        pass


def _test_initialized():
    if not Session._initialized:
        raise errors.NoActiveSessionException()


def _require_initialized(f):
    """Decorator to label functions which require an initialized DRMAA
    Session"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        _test_initialized()
        return f(*args, **kwargs)
    return wrapper


class JobControlAction(object):
    SUSPEND = 'suspend'
    RESUME = 'resume'
    HOLD = 'hold'
    RELEASE = 'release'
    TERMINATE = 'terminate'

    _all = [SUSPEND, RESUME, HOLD, RELEASE, TERMINATE]


class JobState(object):
    UNDETERMINED = 'undetermined'
    QUEUED_ACTIVE = 'queued_active'
    SYSTEM_ON_HOLD = 'system_on_hold'
    USER_ON_HOLD = 'user_on_hold'
    USER_SYSTEM_ON_HOLD = 'user_system_on_hold'
    RUNNING = 'running'
    SYSTEM_SUSPENDED = 'system_suspended'
    USER_SUSPENDED = 'user_suspended'
    USER_SYSTEM_SUSPENDED = 'user_system_suspended'
    DONE = 'done'
    FAILED = 'failed'


class JobTemplate(object):
    HOME_DIRECTORY = '$drmaa_hd_ph$'
    PARAMETRIC_INDEX = '$drmaa_incr_ph$'
    WORKING_DIRECTORY = '$drmaa_wd_ph$'
    _drmaa_c_fields = ['blockEmail', 'deadlineTime', 'errorPath', 'inputPath',
                       'jobCategory', 'jobName', 'jobSubmissionState',
                       'joinFiles', 'nativeSpecification', 'outputPath',
                       'remoteCommand', 'startTime', 'transferFiles',
                       'workingDirectory']

    @_require_initialized
    def __init__(self):
        pass

    def __getattribute__(self, name):
        if name in JobTemplate._drmaa_c_fields:
            _test_initialized()
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in JobTemplate._drmaa_c_fields:
            _test_initialized()
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in JobTemplate._drmaa_c_fields:
            raise AttributeError('Cannot delete builtin attr: %s' % name)
        object.__delattr__(self, name)

    @_require_initialized
    def delete(self):
        pass

Version = namedtuple("Version", "major minor")


class Session(object):
    JOB_IDS_SESSION_ALL = 'DRMAA_JOB_IDS_SESSION_ALL'
    JOB_IDS_SESSION_ANY = 'DRMAA_JOB_IDS_SESSION_ANY'
    TIMEOUT_NO_WAIT = 0
    TIMEOUT_WAIT_FOREVER = -1

    # weird static/instance variable depending upon whether initialized
    contact = ''
    drmaaImplementation = ''
    drmsInfo = ''
    version = Version(long(10), long(10))

    _initialized = False
    _test_return = None
    _default_contact = 'default contact'
    _default_build_id = 'build_id'

    @staticmethod
    @_require_initialized
    def control(jobId, operation):
        if operation not in JobControlAction._all:
            raise ValueError('%s not a JobControlAction' % operation)
        Session._test_return = (jobId, operation)

    @staticmethod
    def createJobTemplate():
        return JobTemplate()

    @staticmethod
    def deleteJobTemplate(jobTemplate):
        jobTemplate.delete()

    @staticmethod
    @_require_initialized
    def exit():
        Session._initialized = False

    @staticmethod
    def initialize(contactString=None):
        if Session._initialized:
            raise errors.SessionAlreadyActiveException()
        Session.contact = contactString or Session._default_contact
        Session._initialized = True

    @staticmethod
    @_require_initialized
    def jobStatus(jobId):
        return JobState.UNDETERMINED

    @staticmethod
    @_require_initialized
    def runBulkJobs(jobTemplate, beginIndex, endIndex, step):
        if not isinstance(jobTemplate, JobTemplate):
            raise TypeError("jobTemplate is not instance of JobTemplate")
        return []

    @staticmethod
    @_require_initialized
    def runJob(jobTemplate):
        if not isinstance(jobTemplate, JobTemplate):
            raise TypeError("jobTemplate is not instance of JobTemplate")
        Session._test_return = jobTemplate
        return Session._default_build_id

    @staticmethod
    @_require_initialized
    def synchronize(jobIds, timeout=-1, dispose=False):
        pass

    @staticmethod
    @_require_initialized
    def wait(jobId, timeout=-1):
        pass

    def __enter__(self):
        self.initialize(self.contactString)
        return self

    def __exit__(self, *args):
        self.exit()
        return False
