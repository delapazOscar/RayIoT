from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

class Rayiot(models.Model):
    _name = "ray.rayiot"
    _inherit = ['mail.thread']
    _description = "RayIoT's"

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

    @api.model
    def add_rayiot(self, vals):
        device = self.sudo().search([
            ('active', '=', True)
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
            self.voltage = voltage

        if current:
            self.current = current

        if battery_percentage:
            self.battery_percentage = battery_percentage

        self.last_update = fields.Datetime.now()
        if self.device_state == 'off':
            self.device_state = 'on'

        return {
            'success': True,
            'message': 'Datos actualizados correctamente!'
        }

    def get_data(self):
        data = {
            'id': self.id,
            'name': self.name,
            'battery_percentage': self.battery_percentage,
            'voltage': self.voltage,
            'current': self.current
        }

        return data

    def cron_define_device_state(self):
        one_minute_ago = fields.Datetime.now() - timedelta(minutes=1)
        devices = self.sudo().search([
            ('active', '=', True)
            ('last_update', '<', one_minute_ago)
        ])

        devices.write({'device_state': 'off'})
        return True

