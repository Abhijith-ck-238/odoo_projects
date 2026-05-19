import importlib
from odoo import api

odoo_module = importlib.import_module(
    "odoo.addons.al-itkan.models.applicant_form")
ItkApplForm = odoo_module.ItkApplForm

# Original create method
original_create = ItkApplForm.create


@api.model
def new_create(self, values):
    BINARY_FILES = [('photo', 'Photo'),
                    ('national_id', "National ID"),
                    ('accomodation_id', "Accomodation ID"),
                    ('uni_degree', "University Degree"),
                    ('cv', "CV")]
    record = original_create(self, values)

    for attach in BINARY_FILES:
        if values.get(attach[0]):
            record.message_post(body="%s Attachment" % (attach[1]),
                                attachments=[
                                    (attach[1] + '.pdf', values[attach[0]])])

    return record


# Assign the new method
ItkApplForm.create = new_create

















# import importlib
# from odoo import api
# odoo_module = importlib.import_module("odoo.addons.al-itkan.models.applicant_form")
# ItkApplForm = odoo_module.ItkApplForm
#
#
# class ItkApplFormMpatch(ItkApplForm):
#
#     @api.model
#     def create(self, values):
#         BINARY_FILES = [('photo', 'Photo'),
#                         ('national_id', "National ID"),
#                         ('accomodation_id', "Accomodation ID"),
#                         ('uni_degree', "University Degree"),
#                         ('cv', "CV")]
#         record = super(ItkApplForm, self).create(values)
#         # raise UserError(str(values))
#         for attach in BINARY_FILES:
#             if values[attach[0]]:
#                 record.message_post(body="%s Attachment" % (attach[1]),
#                                     attachments=[(attach[1] + '.pdf', values[attach[0]])])
#             else:
#                 pass
#         return record
#
#     ItkApplForm.create = create
