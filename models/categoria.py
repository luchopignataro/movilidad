# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)


class Categoria(models.Model):
    _name = 'movilidad.categoria'

    nombre = fields.Char('Categoría')

    valor = fields.Float('Valor asignado')

