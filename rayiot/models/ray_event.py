import datetime
from .utils.ray_timezone import convert_utc_in_tz
from odoo import api, fields, models
import logging
import pytz
from datetime import datetime
import requests

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

    start_date = fields.Datetime(
        string='Fecha de inicio',
        tracking=True
    )

    end_date = fields.Datetime(
        string='Fecha de fin',
        tracking=True
    )

    rayiot_id = fields.Many2one(
        string="Dispositivo vinculado al evento",
        comodel_name="ray.rayiot",
        tracking=True
    )

    state = fields.Selection(
        string="Estado del evento",
        tracking=True,
        selection=[
            ('pending', 'Pendiente'),
            ('active', 'Activo'),
            ('done', 'Finalizado')
        ],
        default='pending'
    )

    def get_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': str(self.start_date) if self.start_date else '',
            'end_date': str(self.end_date) if self.end_date else '',
            'state': self.state if self.state else '',
            'rayiot': self.rayiot_id.get_data() if self.rayiot_id else {}
        }

    def cron_define_event_state(self):
        """Cron para actualizar el estado de los eventos basado en las fechas y la zona horaria del dispositivo."""
        now_utc = pytz.utc.localize(fields.Datetime.now())  # Fecha y hora actual en UTC
        logging.info("Iniciando la revisión del estado de los eventos.")

        events = self.search([])  # Buscar todos los eventos
        for event in events:
            if event.start_date and event.end_date and event.rayiot_id:
                # Obtener la zona horaria del dispositivo o usar una predeterminada
                tz = event.rayiot_id.tz if event.rayiot_id.tz else 'America/Mexico_City'
                timezone = pytz.timezone(tz)

                # Asegurar que `start_date` y `end_date` sean offset-aware en la zona horaria del dispositivo
                start_date_tz = pytz.utc.localize(event.start_date).astimezone(timezone)
                end_date_tz = pytz.utc.localize(event.end_date).astimezone(timezone)

                # Convertir `now_utc` a la zona horaria del dispositivo
                tz_now_in_device_tz = now_utc.astimezone(timezone)

                logging.info(f'start_date_tz: {start_date_tz}, end_date_tz = {end_date_tz}, tz_now_in_device_tz: {tz_now_in_device_tz}')

                # Comparar las fechas
                if tz_now_in_device_tz > end_date_tz:
                    event.state = 'done'
                    logging.info(f"Evento '{event.name}' marcado como 'Finalizado'.")
                elif start_date_tz <= tz_now_in_device_tz <= end_date_tz:
                    event.state = 'active'
                    logging.info(f"Evento '{event.name}' marcado como 'Activo'.")
                    # try:
                    #     url = f'https://{event.rayiot_id.ip_address}/attendance_mode'
                    #     logging.info(f'URL RASP: {url}')
                    #     data = {}
                    #     response = requests.post(url, json=data, timeout=2)
                    # except Exception as e:
                    #     logging.info(f'Raspberry no respondió : {e}')
                elif tz_now_in_device_tz < start_date_tz:
                    event.state = 'pending'
                    logging.info(f"Evento '{event.name}' marcado como 'Pendiente'.")
            else:
                logging.warning(f"El evento '{event.name}' no tiene fechas completas o dispositivo asignado.")

        logging.info("Revisión del estado de los eventos completada.")

    @api.model
    def create_event(self, **vals):
        name = vals.get('name')
        description = vals.get('description')
        start_date = vals.get('start_date')
        rayiot_id = vals.get('rayiot_id')
        end_date = vals.get('end_date')

        # Validar que los campos obligatorios no sean vacíos
        if not name or not description or not start_date or not rayiot_id or not end_date:
            return {
                'success': False,
                'message': 'Todos los campos son obligatorios'
            }

        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return {
                'success': False,
                'message': 'El formato de las fechas debe ser YYYY-MM-DD HH:mm:ss'
            }

        if start_date_obj >= end_date_obj:
            return {
                'success': False,
                'message': 'La fecha de inicio debe ser anterior a la fecha de fin'
            }

        exist_event = self.env['ray.event'].sudo().search([
            ('start_date', '=', start_date),
            ('rayiot_id', '=', rayiot_id)
        ])

        if exist_event:
            return {
                'success': False,
                'message': 'Ya hay un evento asignado para esa fecha'
            }

        event = self.create({
            'name': name,
            'description': description,
            'start_date': start_date,
            'rayiot_id': rayiot_id,
            'end_date': end_date
        })

        return {
            'success': True,
            'data': event.get_data()
        }