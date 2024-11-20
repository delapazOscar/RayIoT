import datetime
from .utils.ray_timezone import convert_utc_in_tz
from odoo import api, fields, models
import logging
import pytz

class UserEvent(models.Model):
    _name = "ray.user.event"
    _inherit = ['mail.thread']
    _description = "Eventos de Usuarios RayIoT"

    event_id = fields.Many2one(
        string="Evento relacionado",
        comodel_name="ray.event",
        tracking=True
    )

    user_id = fields.Many2one(
        string="Usuario",
        comodel_name="ray.user",
        tracking=True
    )

    access_date = fields.Datetime(
        string="Fecha de registro",
        tracking=True
    )

    def get_data(self):
        data = {
            'event': self.event_id.get_data() if self.event_id else {},
            'user': self.user_id.get_data() if self.user_id else {},
            'access_date': str(self.access_date) if self.access_date else ''
        }

    @api.model
    def register_assistence(self, nfc_id):
        if not nfc_id:
            return {
                'success': False,
                'message': 'Es necesario proporcionar un nfc para registrar asistencia'
            }

        user = self.env['ray.user'].sudo().search([
            ('nfc_id', '=', nfc_id)
        ], limit=1)

        if not user:
            return {
                'success': False,
                'message': 'No hemos encontrado el identificador de nfc'
            }

        today_date = fields.Datetime.now()

        now, _ = convert_utc_in_tz(today_date)

        event = self.env['ray.event'].sudo().search([
            ('state', '=', 'active')
        ])

        if not event:
            return {
                'success': False,
                'message': 'No hay eventos en esta hora'
            }

        user_event = self.sudo().create({
            'user_id': user.id,
            'event_id': event.id,
            'access_date': now
        })

        return {
            'success': True,
            'data': user_event.get_data()
        }

