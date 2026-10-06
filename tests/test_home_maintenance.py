from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHomeMaintenance(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Owner'})
        cls.prop = cls.env['home.property'].create({
            'name': 'Test Flat',
            'partner_id': cls.partner.id,
        })
        cls.manager = cls._create_user('mgr_test', 'group_home_manager')
        cls.technician = cls._create_user('tech_test', 'group_home_technician')
        cls.user_a = cls._create_user('user_a_test', 'group_home_user')
        cls.user_b = cls._create_user('user_b_test', 'group_home_user')

    @classmethod
    def _create_user(cls, login, group_xmlid):
        user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': login,
            'login': login,
            'email': f'{login}@example.com',
        })
        cls.env.ref(f'home_maintenance.{group_xmlid}').write({
            'user_ids': [(4, user.id)],
        })
        return user

    def _new_request(self, **kwargs):
        vals = {'title': 'Leak', 'property_id': self.prop.id}
        vals.update(kwargs)
        return self.env['home.request'].create(vals)

    # ---------- منطق الطلب ----------

    def test_01_sequence_and_default_state(self):
        req = self._new_request()
        self.assertTrue(req.name.startswith('REQ'))
        self.assertEqual(req.state, 'new')
        self.assertEqual(req.partner_id, self.partner)

    def test_02_state_flow(self):
        req = self._new_request()
        req.action_schedule()
        self.assertEqual(req.state, 'scheduled')
        req.action_start()
        self.assertEqual(req.state, 'in_progress')
        req.action_done()
        self.assertEqual(req.state, 'done')

    def test_03_cancel_wizard(self):
        req = self._new_request()
        wizard = self.env['home.request.cancel.wizard'].create({
            'request_id': req.id,
            'reason': 'Customer changed his mind',
        })
        wizard.action_confirm()
        self.assertEqual(req.state, 'cancelled')
        self.assertEqual(req.cancel_reason, 'Customer changed his mind')
        req.action_reset()
        self.assertEqual(req.state, 'new')
        self.assertFalse(req.cancel_reason)

    def test_04_schedule_wizard(self):
        req = self._new_request()
        wizard = self.env['home.request.schedule.wizard'].create({
            'request_id': req.id,
            'technician_id': self.technician.id,
            'visit_date': fields.Datetime.now(),
            'duration': 2.0,
        })
        wizard.action_confirm()
        self.assertEqual(req.state, 'scheduled')
        self.assertEqual(req.technician_id, self.technician)
        self.assertEqual(len(req.visit_ids), 1)

    # ---------- الخانات ----------

    def _new_slot(self):
        return self.env['home.slot'].create({
            'technician_id': self.technician.id,
            'slot_start': fields.Datetime.now(),
        })

    def test_05_slot_booked_and_freed(self):
        slot = self._new_slot()
        self.assertEqual(slot.state, 'free')
        req = self._new_request(slot_id=slot.id)
        self.assertEqual(slot.state, 'booked')
        self.env['home.request.cancel.wizard'].create({
            'request_id': req.id,
            'reason': 'test',
        }).action_confirm()
        self.assertEqual(slot.state, 'free')

    def test_06_no_double_booking(self):
        slot = self._new_slot()
        self._new_request(slot_id=slot.id)
        with self.assertRaises(ValidationError):
            self._new_request(slot_id=slot.id)

    def test_07_schedule_wizard_defaults_from_slot(self):
        slot = self._new_slot()
        req = self._new_request(slot_id=slot.id)
        wizard = self.env['home.request.schedule.wizard'].with_context(
            default_request_id=req.id).create({})
        self.assertEqual(wizard.technician_id, self.technician)
        self.assertEqual(wizard.visit_date, slot.slot_start)

    # ---------- الصلاحيات ----------

    def test_08_technician_sees_only_assigned(self):
        mine = self._new_request(technician_id=self.technician.id)
        other = self._new_request()
        visible = self.env['home.request'].with_user(self.technician).search([])
        self.assertIn(mine, visible)
        self.assertNotIn(other, visible)

    def test_09_technician_cannot_create(self):
        with self.assertRaises(AccessError):
            self.env['home.request'].with_user(self.technician).create({
                'title': 'x',
                'property_id': self.prop.id,
            })

    def test_10_user_sees_only_own_and_cannot_edit(self):
        req_a = self.env['home.request'].with_user(self.user_a).create({
            'title': 'A request',
            'property_id': self.prop.id,
        })
        req_b = self.env['home.request'].with_user(self.user_b).create({
            'title': 'B request',
            'property_id': self.prop.id,
        })
        visible = self.env['home.request'].with_user(self.user_a).search([])
        self.assertIn(req_a, visible)
        self.assertNotIn(req_b, visible)
        with self.assertRaises(AccessError):
            req_a.with_user(self.user_a).write({'title': 'changed'})

    def test_11_manager_sees_all(self):
        r1 = self._new_request()
        r2 = self._new_request(technician_id=self.technician.id)
        visible = self.env['home.request'].with_user(self.manager).search([])
        self.assertIn(r1, visible)
        self.assertIn(r2, visible)