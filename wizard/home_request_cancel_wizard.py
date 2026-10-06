from odoo import models, fields
class HomeRequestCancelWizard(models.TransientModel):
    _name = 'home.request.cancel.wizard'
    _description = 'Cancel Request Wizard'
    request_id = fields.Many2one('home.request', string='Request',required=True)
    reason = fields.Text(string='Reason',required=True)

    def action_confirm(self):
        self.ensure_one()
        self.request_id.write({'state' : 'cancelled','cancel_reason': self.reason,})
        self.request_id.message_post(body=f"Request cancelled. Reason: {self.reason}")
        return {'type': 'ir.actions.act_window_close'}