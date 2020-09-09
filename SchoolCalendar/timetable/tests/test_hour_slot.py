from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class HourSlotTestCase(BaseTestCase):
    def setUp(self):
        super(HourSlotTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()

        # Create 2 hour slots groups.
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Dafault school 1')
        self.hsg2 = HourSlotsGroup(school=self.s2, school_year=self.school_year_2020, name='Dafault school 2')
        self.hsg1.save()
        self.hsg2.save()

    def test_hour_slot_correct_creation(self):
        """
        Test the creation of an HourSlot, using the correct admin and school.
        :return:
        """
        data = {'hour_number': '4',
                'starts_at': '11:05',
                'ends_at': '12:00',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '0',
                'legal_duration_0': '1',   # Hour
                'legal_duration_1': '0'}   # Minutes
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_hour_slot_wrong_admin_for_school_creation(self):
        """
        Test the creation of a hour_slot, using the wrong school for the admin.
        :return:
        """
        data = {'hour_number': '4',
                'starts_at': '11:05',
                'ends_at': '12:00',
                'hour_slots_group': self.hsg1.id,  # Wrong school for admin a2
                'day_of_week': '0',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        # But admin of school 2
        f = HourSlotForm(user=self.a2, data=data)   # Admin is for different school
        f.full_clean()
        self.assertTrue(f.has_error('hour_slots_group'))   # The form should have an error on the school field.

    def test_hour_slot_wrong_start_end_hour(self):
        """
        Test the creation of a wrong hour_slot, with starts_at > ends_at
        :return:
        """
        data = {'hour_number': '4',
                'starts_at': '13:05',    # Starts_at > ends_at
                'ends_at': '12:00',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '0',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        # But admin of school 1
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        self.assertFalse(f.is_valid())

    def test_hour_slot_multiple_hour_number(self):
        """
        Test the creation of a wrong hour_slot, with multiple hour_number in the same day, school_year, school etc.
        :return:
        """
        hs1 = HourSlot(hour_number=4,
                       starts_at=time(hour=9, minute=0),
                       ends_at=time(hour=10, minute=5),
                       hour_slots_group=self.hsg1,
                       day_of_week=0,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '4',      # Same hour_number as above!
                'starts_at': '11:05',
                'ends_at': '12:00',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '0',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        # But admin of school 1
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        hs1.delete()
        self.assertFalse(f.is_valid())

    def test_hour_slot_multiple_hour_number_but_different_days(self):
        """
        Test the creation of a hour_slot, with multiple hour_number in a different day, school_year, school etc.
        :return:
        """
        hs1 = HourSlot(hour_number=4,
                       starts_at=time(hour=9, minute=0),
                       ends_at=time(hour=10, minute=5),
                       hour_slots_group=self.hsg1,
                       day_of_week=1,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '4',      # Same hour_number as above!
                'starts_at': '11:05',
                'ends_at': '12:00',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '0',        # But different day
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        # But admin of school 1
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        hs1.delete()
        self.assertTrue(f.is_valid(), msg=f.errors)

    def test_hour_slot_on_conflicting_hours(self):
        """
        Test the creation of multiple hour slots for the same school and in concurrent time interval.
        An error should be returned.
        """
        hs1 = HourSlot(hour_number=1,
                       starts_at=time(hour=8, minute=45),
                       ends_at=time(hour=9, minute=35),
                       hour_slots_group=self.hsg1,
                       day_of_week=1,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '2',
                'starts_at': '9:05',   # Conflicting time interval.
                'ends_at': '10:00',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '1',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        self.assertFalse(f.is_valid())

    def test_hour_slot_on_conflicting_hours_2(self):
        """
        Test the creation of multiple hour slots for the same school and in concurrent time interval.
        An error should be returned.
        """
        hs1 = HourSlot(hour_number=2,
                       starts_at=time(hour=8, minute=45),
                       ends_at=time(hour=9, minute=35),
                       hour_slots_group=self.hsg1,
                       day_of_week=1,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '1',
                'starts_at': '7:55',   # Conflicting time interval.
                'ends_at': '8:55',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '1',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        self.assertFalse(f.is_valid())

    def test_hour_slot_on_conflicting_hours_3(self):
        """
        Test the creation of multiple hour slots for the same school and in concurrent time interval.
        An error should be returned.
        """
        hs1 = HourSlot(hour_number=1,
                       starts_at=time(hour=8, minute=45),
                       ends_at=time(hour=9, minute=35),
                       hour_slots_group=self.hsg1,
                       day_of_week=1,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '2',
                'starts_at': '9:00',   # Conflicting time interval.
                'ends_at': '9:30',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '1',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        self.assertFalse(f.is_valid())

    def test_hour_slot_on_conflicting_hours_but_different_days(self):
        """
        Test the creation of multiple hour slots for the same school and in concurrent time interval, but on
        different days.
        No error should be returned.
        """
        hs1 = HourSlot(hour_number=1,
                       starts_at=time(hour=8, minute=45),
                       ends_at=time(hour=9, minute=35),
                       hour_slots_group=self.hsg1,
                       day_of_week=1,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '2',
                'starts_at': '9:05',   # Conflicting time interval.
                'ends_at': '10:00',
                'hour_slots_group': self.hsg1.id,
                'day_of_week': '2',      # But different day
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        f = HourSlotForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_hour_slot_on_conflicting_hours_but_different_schools(self):
        """
        Test the creation of multiple hour slots for the same school and in concurrent time interval, but in
        different schools.
        No error should be returned.
        """
        hs1 = HourSlot(hour_number=1,
                       starts_at=time(hour=8, minute=45),
                       ends_at=time(hour=9, minute=35),
                       hour_slots_group=self.hsg1,
                       day_of_week=1,
                       legal_duration=timedelta(seconds=3600))
        hs1.save()
        data = {'hour_number': '2',
                'starts_at': '9:05',   # Conflicting time interval.
                'ends_at': '10:00',
                'hour_slots_group': self.hsg2.id,   # Different school
                'day_of_week': '1',
                'legal_duration_0': '1',
                'legal_duration_1': '0'}
        f = HourSlotForm(user=self.a2, data=data)
        f.full_clean()
        self.assertTrue(f.is_valid())
