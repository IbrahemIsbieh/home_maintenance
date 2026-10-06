from odoo import models, fields,api


class HomeRequestScheduleWizard(models.TransientModel):
    _name = 'home.request.schedule.wizard'
    _description = 'Schedule Visit Wizard'

    request_id = fields.Many2one('home.request', string='Request', required=True)
    technician_id = fields.Many2one('res.users', string='Technician', required=True)
    visit_date = fields.Datetime(string='Visit Date', required=True,
                                 default=fields.Datetime.now)
    duration = fields.Float(string='Duration (hours)', default=1.0)
    notes = fields.Text(string='Notes')
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        request = self.env['home.request'].browse(res.get('request_id'))
        if request.exists() and request.slot_id:
            slot = request.slot_id
            res.update({
                'technician_id': slot.technician_id.id,
                'visit_date': slot.slot_start,
                'duration': slot.duration,
            })
        return res
    def action_confirm(self):
        self.ensure_one()
        self.env['home.visit'].create({
            'request_id': self.request_id.id,
            'technician_id': self.technician_id.id,
            'visit_date': self.visit_date,
            'duration': self.duration,
            'notes': self.notes,
        })
        self.request_id.write({
            'state': 'scheduled',
            'technician_id': self.technician_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}