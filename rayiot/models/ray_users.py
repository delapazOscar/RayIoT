from odoo import api, fields, models
import logging
from odoo.exceptions import ValidationError, UserError, MissingError
import requests

class RayAdmin(models.Model):
    _name = "ray.user"
    _inherit = ['mail.thread']
    _description = "Usuarios"

    active = fields.Boolean(
        string="Activo",
        tracking=True,
        default=True
    )
    name = fields.Char(
        string="Nombre",
        required=True,
        tracking=True
    )
    last_name = fields.Char(
        string="Apellido",
        tracking=True
    )
    email = fields.Char(
        string="Email",
        tracking=True
    )
    institution_id = fields.Many2one(
        string="Institución",
        comodel_name="ray.institution",
        tracking=True
    )
    phone_number = fields.Char(
        string="Número telefónico",
        tracking=True
    )
    student_id = fields.Char(
        string="Identificador de usuario",
        tracking=True
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ('pending_nfc_id', 'Pendiente de vincular nfc'),
            ('active', 'Activo')
        ],
        default='pending_nfc_id',
        tracking=True
    )

    nfc_id = fields.Char(
        string="Identificador de NFC",
        tracking=True
    )

    def get_data(self):
        data = {
            'active': self.active if self.active else False,
            'id': self.id,
            'name': self.name if self.name else '',
            'last_name': self.last_name if self.last_name else '',
            'email': self.email if self.email else '',
            'institution_id': self.institution_id.get_data() if self.institution_id else {},
            'phone_number': self.phone_number if self.phone_number else '',
            'student_id': self.student_id if self.student_id else '',
            'state': self.state if self.state else '',
            'nfc_id': self.nfc_id if self.nfc_id else ''
        }
        return data

    @api.model
    def create_user(self, **vals):
        name = vals['name']
        last_name = vals['last_name']
        email = vals['email']
        student_id = vals['student_id']
        mobile = vals['phone_number']
        rayiot_id = vals['rayiot_id']

        if not name or not last_name or not email or not student_id or not mobile or not rayiot_id:
            return {
                'success': False,
                'message': 'Todos los campos son obligatorios'
            }

        device = self.env['ray.rayiot'].sudo().browse(rayiot_id)

        if not device:
            return {
                'success': False,
                'message': 'Dispositivo RayIoT no encontrado'
            }

        ray_user = self.env['ray.user'].create({
            'name': name,
            'last_name': last_name,
            'email': email,
            'student_id': student_id,
            'phone_number': mobile,
            'state': 'pending_nfc_id',
            'institution_id': device.institution_id.id
        })

        # Mandar petición a RayIoT
        # register_mode = self.send_register_mode_rayiot(ray_user, rayiot_id)

        return {
            'success': True,
            'data': ray_user.get_data()
        }

    def send_register_mode_rayiot(self, user, rayiot):
        if not user:
            return False

        url = rayiot.ip_address + '/register_mode'

        data = {
            'user_id': user.id
        }
        response = requests.post(url, json=data, timeout=60)

        return response

    def set_nfc(self, nfc_id):
        if not nfc_id:
            return {
                'success': False,
                'message': 'El id del nfc es necesario'
            }

        self.write({
            'nfc_id': nfc_id,
            'state': 'active'
        })

        return {
            'success': True,
            'message': 'NFC Establecido con éxito'
        }

    def delete_user(self):
        self.ensure_one()
        if not self.exists():
            return {
                'success': False,
                'message': 'El usuario proporcionado no existe'
            }

        self.write({
            'active': False
        })

        return {
            'success': True,
            'message': 'Haz eliminado el usuario correctamente'
        }

