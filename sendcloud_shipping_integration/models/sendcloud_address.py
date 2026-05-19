# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Abhijith CK (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0(OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from odoo import fields, models


class SendcloudAddress(models.Model):
    """To store sendcloud Addresses."""
    _name = 'sendcloud.address'
    _description = 'Sendcloud Address'

    name = fields.Char(string="Company", help="Company Name of the sendcloud"
                                              " address")
    email = fields.Char(string="Email", help="E-mail of the sendcloud address")
    sender_address = fields.Char(string="Sender ID",
                                 help="ID of the sender address under "
                                      "sendcloud")
    country_id = fields.Many2one("res.country", string="Country",
                                 help="Country name of the sender")
    line_id = fields.Many2one('delivery.carrier', string='Line',
                              help="Delivery carrier ID")
