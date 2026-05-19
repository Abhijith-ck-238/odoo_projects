import datetime
import json

from odoo import http
from odoo.http import request

class OdooAPIController(http.Controller):
    @http.route('/api/rfid/<string:epc_id>', type='json', auth='api_key', methods=["POST"])
    def rfid_read_api(self, epc_id):
        result = request.env['rfid.tag.epc'].search_read([("epc_id", "=", epc_id)], ["product_id","epc_id","reference"])
        picking = request.env['rfid.out.transfer'].sudo().search([],limit=1, order="id desc").picking_id.id
        result[0].update({
            'picking_id': picking if picking else 0
        })
        return result

    @http.route('/api/rfid/transfer/allowed/<string:epc_id>', type='json', auth='api_key',
                methods=["POST"])
    def rfid_transfer_allowed_read_api(self, epc_id):
        record_out = request.env['rfid.transfer.line'].search_read(
            [("epc_id", "=", epc_id),
             ("rfid_transfer_id.transfer_type", 'ilike', 'out')])
        if record_out:
            result = {'is_available': True}
        else:
            result = {'is_available': False}

        return result

    @http.route('/api/rfid/transfer/completed', type='json',
                auth='api_key',
                methods=["POST"])
    def rfid_transfer_allowed_write_api(self, **data):
        try:
            for rec in data['data']:
                record = request.env['rfid.transfer.line'].search([('id', '=', rec['id'])])
                if record:
                    record.write({
                        'is_available': rec['is_available'],
                    })
            return {
                'status': 'success',
                'data_id': record.id
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    @http.route('/api/rfid/transfer', type='json', auth='api_key',methods=["POST"])
    def rfid_write_api(self):
        try:
            data = json.loads(request.httprequest.data)
            for rec in data['data']:
                date_obj = rec.get('date', False)
                if date_obj:
                    format = '%d-%m-%Y'
                    datetime_str = datetime.datetime.strptime(date_obj, format)
                    rec['date'] = datetime_str
                record = request.env['rfid.transfer'].search([('transfer', '=', rec['transfer'])])
                if record:
                    record.write({
                        'transfer_line_ids':[(0, 0,  {
                            'epc_id': rec['epc_id'],
                            'product_name': rec['product_name'],
                            'product_ref': rec['product_ref'],
                            'product_qty': rec['product_qty'],
                        })]
                    })
                else:
                    record = request.env['rfid.transfer'].create({
                        'transfer': rec['transfer'],
                        'transfer_type': rec['transfer_type'],
                        'date': rec['date'],
                        'picking_id': rec['picking_id'],
                        'transfer_line_ids': [(0, 0, {
                            'epc_id': rec['epc_id'],
                            'product_name': rec['product_name'],
                            'product_ref': rec['product_ref'],
                            'product_qty': rec['product_qty'],
                        })]
                    })
            return {
                'status': 'success',
                'data_id': record.id
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
