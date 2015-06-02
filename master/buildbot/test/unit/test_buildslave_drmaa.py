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
# Copyright Buildbot Team Members

from twisted.trial import unittest

from buildbot import config
from buildbot.buildslave import drmaa as drmaabs
from buildbot.test.fake import drmaa


class TestDRMAALatentBuildSlave(unittest.TestCase):

    def setUp(self):
        # Oh dear, this library is all global state...
        self.patch(drmaa.Session, '_initialized', False)
        self.patch(drmaa.Session, '_test_return', None)
        self.patch(drmaa.Session, 'contact', None)
        self.patch(drmaabs.DRMAALatentBuildSlave, '_drmaa_session', None)
        self.patch(drmaabs, 'drmaa', drmaa)

    def test_constructor_nodrmaa(self):
        self.patch(drmaabs, 'drmaa', None)
        self.assertRaises(config.ConfigErrors, drmaabs.DRMAALatentBuildSlave,
                          'bot', 'pass', 'cmd')

    def test_constructor_minimal(self):
        build_cmd = 'build cmd'
        bs = drmaabs.DRMAALatentBuildSlave('bot', 'pass', build_cmd)
        self.assertEqual(bs.slavename, 'bot')
        self.assertEqual(bs.password, 'pass')
        self.assertEqual(bs.job_template.remoteCommand, build_cmd)

    def test_constructor_contact(self):
        build_cmd = 'build cmd'
        contact = 'some string'
        bs = drmaabs.DRMAALatentBuildSlave('bot', 'pass', build_cmd,
                                           drmaa_session_contact=contact)
        self.assertEqual(bs.slavename, 'bot')
        self.assertEqual(bs.password, 'pass')
        self.assertEqual(bs.job_template.remoteCommand, build_cmd)
        self.assertEqual(drmaa.Session.contact, contact)

    def test_start_instance(self):
        build_cmd = 'build cmd'
        bs = drmaabs.DRMAALatentBuildSlave('bot', 'pass', build_cmd)
        self.assertTrue(bs._start_instance())
        self.assertEqual(drmaa.Session._test_return.remoteCommand, build_cmd)
        self.assertEqual(bs.job_id, drmaa.Session._default_build_id)

    def test_stop_instance(self):
        build_cmd = 'build cmd'
        bs = drmaabs.DRMAALatentBuildSlave('bot', 'pass', build_cmd)
        bs._start_instance()
        bs._stop_instance()
        self.assertEqual(bs.job_id, None)
        self.assertEqual(drmaa.Session._test_return,
                         (drmaa.Session._default_build_id, drmaa.JobControlAction.TERMINATE))
