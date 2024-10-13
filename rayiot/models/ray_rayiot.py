from odoo import api, fields, models
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

    battery_percentage = fields.Float(
        string="Porcentaje de bateria"
    )

    voltage = fields.Float(
        string="Voltaje del dispositivo"
    )

    current = fields.Float(
        string="Corriente del dispositivo"
    )

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

        return {
            'success': True,
            'message': 'Datos actualizados correctamente!'
        }

    def get_data(self):
        data = {
            'name': self.name,
            'battery_percentage': self.battery_percentage,
            'voltage': self.voltage,
            'current': self.current
        }

        return data

