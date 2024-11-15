from odoo import api, fields, models
from datetime import datetime, timedelta
import logging
from odoo.addons.base.models.res_partner import _tz_get
from .utils.ray_timezone import convert_utc_in_tz

class Rayiot(models.Model):
    _name = "ray.rayiot"
    _inherit = ['mail.thread']
    _description = "RayIoT's"

    active = fields.Boolean(
        string="Activo",
        tracking=True,
        default=True
    )

    name = fields.Char(
        string='Nombre del dispositivo',
        tracking=True,
        required=True
    )

    institution_id = fields.Many2one(
        string="Institución",
        comodel_name="ray.institution",
        tracking=True,
        required=True
    )

    institution_location_id = fields.Many2one(
        string="Ubicación",
        comodel_name="ray.institution.location",
        required=False,
        tracking=True
    )

    battery_percentage = fields.Float(
        string="Porcentaje de bateria",
        readonly=True
    )

    voltage = fields.Float(
        string="Voltaje del dispositivo",
        readonly=True
    )

    current = fields.Float(
        string="Corriente del dispositivo",
        readonly=True
    )

    state = fields.Selection(
        string="Estado",
        selection=[
            ('pending', 'Pendiente'),
            ('confirmed', 'Confirmado'),
            ('active', 'Activo')
        ],
        tracking=True,
        default='pending',
        readonly=True
    )

    identifier = fields.Char(
        string="Identificador único de dispositivo",
        tracking=True
    )

    device_state = fields.Selection(
        string="Estado del dispositivo",
        selection=[
            ('off', 'Apagado'),
            ('on', 'Encendido')
        ],
        tracking=True,
        readonly=True
    )

    last_update = fields.Datetime(
        string="Última actualización",
        readonly=True
    )

    tz = fields.Selection(_tz_get, string='Zona horaria del dispositivo', default=lambda self: self._context.get('tz'),
                          help="Zona horaria utilizada en la APP", tracking=True)

    @api.model
    def add_rayiot(self, vals):
        device = self.sudo().search([
            ('active', '=', True),
            ('identifier', '=', vals['identifier'])
        ], limit=1)

        if not device:
            self.sudo().create(vals)
            return {
                'success': True,
                'message': 'Dispositivo añadido correctamente'
            }

        data_uploaded = device.update_battery_data({
            'voltage': vals['voltage'],
            'current': vals['current'],
            'battery_percentage': vals['battery_percentage']
        })

        return data_uploaded

    def update_battery_data(self, **kwargs):
        voltage = kwargs.get("voltage", False)
        current = kwargs.get("current", False)
        battery_percentage = kwargs.get("battery_percentage", False)

        if voltage:
            if not self.voltage or abs(self.voltage - voltage) >= 1:
                self.voltage = voltage

        if current:
            if not self.current or abs(self.current - current) >= 1:
                self.current = current

        if battery_percentage:
            if not self.battery_percentage or abs(self.battery_percentage - battery_percentage) >= 1:
                self.battery_percentage = battery_percentage

        self.last_update = fields.Datetime.now()
        if not self.device_state or self.device_state == 'off':
            self.device_state = 'on'

        return {
            'success': True,
            'message': 'Datos actualizados correctamente!'
        }

    def get_data(self):
        last_update_tz, _ = convert_utc_in_tz(self.last_update, self.tz)
        data = {
            'id': self.id,
            'name': self.name if self.name else '',
            'battery_percentage': self.battery_percentage if self.battery_percentage else 0,
            'voltage': self.voltage if self.voltage else 0,
            'current': self.current if self.voltage else 0,
            'device_state': self.device_state if self.device_state else '',
            'last_update': str(last_update_tz) if last_update_tz else ''
        }

        return data

    def cron_define_device_state(self):
        one_minute_ago = fields.Datetime.now() - timedelta(minutes=1)
        devices = self.sudo().search([
            ('active', '=', True),
            ('last_update', '<', one_minute_ago)
        ])

        devices.write({'device_state': 'off'})
        return True

