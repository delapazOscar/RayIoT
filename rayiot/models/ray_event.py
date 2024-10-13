from odoo import api, fields, models
import logging

class Event(models.Model):
    _name = "ray.event"
    _inherit = ['mail.thread']
    _description = "Eventos RayIoT"

    name = fields.Char(
        string='Nombre del evento',
        tracking=True,
        required=True
    )

    description = fields.Char(
        string='Descripción del evento',
        tracking=True
    )

    date = fields.Datetime(
        string='Fecha',
        tracking=True
    )

    def get_data(self):
        return {
            'name': self.name,
            'description': self.description,
            'date': self.date
        }

    def createEvent(self, **vals):

        event = self.create({
            'name': vals.get('name'),
            'description': vals.get('description'),
            'date': vals.get('date'),
        })

        return event.get_data()