import datetime
from .utils.ray_timezone import convert_utc_in_tz
from odoo import api, fields, models
import logging
import pytz
from pytz import timezone

class UserEvent(models.Model):
    _name = "ray.user.event"
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

    def name_get(self):
        res = []
        for record in self:
            name = f"Asistencia usuario {record.user_id.name}, Evento {record.event_id.name}"
            res.append((record.id, name))
        return res

    def get_data(self):
        data = {
            'event': self.event_id.get_data() if self.event_id else {},
            'user': self.user_id.get_data() if self.user_id else {},
            'access_date': str(self.access_date) if self.access_date else ''
        }
        return data

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
        user_tz = timezone('America/Mexico_City')
        local_date = today_date.astimezone(user_tz)
        local_naive_date = local_date.replace(tzinfo=None)

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
            'access_date': local_naive_date
        })

        return {
            'success': True,
            'data': user_event.get_data()
        }

