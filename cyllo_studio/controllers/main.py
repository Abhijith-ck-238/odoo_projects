# -*- coding: utf-8 -*-
import inspect
import uuid
from html import unescape, escape
import xml.etree.ElementTree as ET
from odoo import http, api, _
import json
import re

from odoo.exceptions import ValidationError, AccessError
from odoo.osv.expression import TERM_OPERATORS_NEGATION
from odoo.http import Controller, route, request
from odoo import Command
from lxml import etree
import re
from odoo.tools import ustr

random_uuid = uuid.uuid4()


class StudioMode(Controller):

    def create_invisible(self,args):
        active_fields_keys = args[0].get('active_fields',False).keys()

        all_fields = request.env['ir.model.fields'].search(
            [('model', '=', args[0]['model'])]).mapped('name')

        conditions = {
            'invisible': args[0].get('invisible',False),
            'readonly': args[0].get('readonly',False),
            'required': args[0].get('required',False)
        }
        pattern1 = r'\b(\w+)\b(?=\s*(?:in|not in|=))'
        pattern2 = r'set\((.*?)\)\.intersection'

        left_hand_names = []
        for condition in conditions.values():
            if isinstance(condition, str):
                matches1 = re.findall(pattern1, condition)
                matches2 = re.findall(pattern2, condition)
                left_hand_names.extend([*matches1,*matches2])
        left_hand_names = list(set(left_hand_names))
        keys_not_present = [key for key in left_hand_names if
                            key not in active_fields_keys and key in all_fields]
        fields_to_include = ''
        if keys_not_present:
            if args[0].get('viewType',False) == 'tree' or args[0].get('view_type',False) == 'tree':
                fields_to_include += f'''<xpath expr="/{args[0]["path"]}" position="{args[0].get("position")}">'''
                fields_to_include += ''.join(
                    f'''<field name="{field}" invisible="True" column_invisible="True"/>''' for field in
                    keys_not_present)
                fields_to_include +='</xpath>'
            else:
                fields_to_include = fields_to_include.join(
                    f'<field name="{field}" invisible="True"/>' for field in
                    keys_not_present)
        return fields_to_include

    def create_header(self, header_path):
        if not header_path:
            return ''
        path = header_path
        position = 'before'

        if path == "/form/":
            path = "/form"
            position = "inside"
        header_arch = f'<xpath expr="/{path}" position="{position}"><header/></xpath> '
        return header_arch

    @http.route('/web/webclient/cyllo_load_menus/<string:unique>', type='http', auth='user', methods=['GET'])
    def web_cyllo_load_menus(self, unique, lang=None):
        """
        //Removed the reload and odoo.loadparams for not taking cached menu and getting newly created menu from studio

        Loads the menus for the webclient
        :param unique: this parameters is not used, but mandatory: it is used by the HTTP stack to make a unique request
        :param lang: language in which the menus should be loaded (only works if language is installed)
        :return: the menus (including the images in Base64)
        """
        if lang:
            request.update_context(lang=lang)
        menus = request.env["ir.ui.menu"].load_web_menus(request.session.debug)
        body = json.dumps(menus, default=ustr)
        response = request.make_response(body, [
            # this method must specify a content-type application/json instead of using the default text/html set because
            # the type of the route is set to HTTP, but the rpc is made with a get and expects JSON
            ('Content-Type', 'application/json'),
            # ('Cache-Control', 'public, max-age=' + str(http.STATIC_CACHE_LONG)), #Removed this to get the newly created menus via calling load_menus from the load_web_menus
        ])
        return response

    def is_studio_user(self):
        is_studio_debug = 'studio' in request.session.debug.split(',')
        is_erp_manager = request.env.user.has_group('base.group_erp_manager')

        if is_erp_manager and not is_studio_debug:
            '''multi tab case may be in session deosn't have debug = studio
            so we need to manualy  debug session in to studio to not get an error'''
            request.session.debug = 'studio'

        if not is_erp_manager:
            raise AccessError(_("You don't have the access to this request."))

    def get_studio_view(self, view_id, model, view_type):
        self.is_studio_user()
        view_rec = request.env['ir.ui.view'].search([('inherit_id', '=', view_id)], order='priority desc, id desc',
                                                    limit='1')
        if not view_rec.is_studio:
            priority = view_rec.priority + 1 if len(view_rec) == 1 else 16
            view_rec = view_rec.sudo().create(
                {'name': f"Cyllo Studio {model} {view_type} view",
                 'type': view_type,
                 'model': model,
                 'mode': 'extension',
                 'inherit_id': view_id,
                 'arch_base': '<data></data>',
                 'active': True,
                 'priority': priority,
                 'is_studio': True})

            request.env['ir.model.data']._update_xmlids([{
                'xml_id': f"cy_studio.{model.replace('.', '_')}_{view_type}_view_{str(uuid.uuid4())[:8]}",
                'record': view_rec,
            }])
        return view_rec


    def create_view(self, data, ttype, arch):
        view_data = request.env['ir.ui.view'].create({
            'name': f"view_{data['name']}_{ttype}_{str(uuid.uuid4())[:8]}",
            'type': ttype,
            'model': data['resModel'],
            'model_id': request.env['ir.model']._get_id(data['resModel']),
            'arch': arch
        })
        return view_data


    def get_default_view_arch(self, view_type, data):
        """
        Generates the default architecture for a specified view type.

        This method returns a template XML structure based on the specified view type,
        which can be used as a default for creating new views.

        Args:
            view_type (str): The type of view to generate (e.g., 'calendar', 'kanban', 'form').
            data (dict): A dictionary containing data relevant to the view, such as field names.

        Returns:
            str: An XML string representing the default architecture for the specified view type.
        """

        arch = ""
        if view_type == "calendar":
            arch = f"""<calendar date_start="{data['startDateField']}" date_stop="{data['stopDateField']}">
                           <field name="{data['startDateField']}"/>
                       </calendar>"""
        elif view_type == "kanban":
            arch = """<kanban>
                        <field name="display_name" />
                        <templates>
                            <t t-name="kanban-box">
                                <div class="oe_kanban_global_click">
                                    <div class="oe_kanban_details">
                                        <field name="display_name" />
                                    </div>
                                </div>
                            </t>
                        </templates>
                    </kanban>"""
        elif view_type == "form":
            arch = """<form>
                        <header />
                        <sheet>
                            <div class="oe_title">
                                <h1>
                                    <field name="x_name" required="1" placeholder="Name..." />
                                </h1>
                            </div>
                            <group />
                        </sheet>
                    </form>"""
        elif view_type == "pivot":
            arch = """<pivot>
                        <field name="display_name"/>
                    </pivot>"""

        elif view_type == "graph":
            arch = """<graph>
                        <field name="display_name"/>
                    </graph>"""
        elif view_type == "activity":
            arch = f"""<activity string='{data['resModel']} Activity View'>
                        <field name="display_name" />
                        <templates>
                             <div t-name="activity-box">
                                <field name="display_name"/>
                             </div>
                        </templates>
                    </activity>"""
        elif view_type == "tree":
            arch = """<tree>
                       <field name="x_name"/>
                   </tree>"""
        return arch


    def ensure_unique_relation_table(self, field):
        """
        Ensures that the relation_table for a many2many field is unique.
        If the relation_table already exists, appends an integer to make it unique.

        :param field: The field object to check and update.
        :return: None (updates the field.relation_table in place).
        """
        if field.ttype == 'many2many':
            base_relation_table = field.relation_table
            relation_tables = request.env['ir.model.fields'].search([
                ('ttype', '=', 'many2many'),
                ('relation_table', '=', base_relation_table)
            ])

            if len(relation_tables) > 1:
                counter = 1
                new_relation_table = f"{base_relation_table}_{counter}"

                # Check if the new_relation_table already exists
                while request.env['ir.model.fields'].search_count([
                    ('ttype', '=', 'many2many'),
                    ('relation_table', '=', new_relation_table)
                ]) > 0:
                    counter += 1
                    new_relation_table = f"{base_relation_table}_{counter}"

                # Update the relation_table with the new unique name
                field.relation_table = new_relation_table

    def get_currency_field(self, model_id, field_name):
        ir_model = request.env["ir.model"].browse(model_id)
        res_model = request.env[ir_model.model]
        if field_name not in res_model._fields:
            return None
        currency_field_name = res_model._fields[field_name].get_currency_field(res_model)
        return currency_field_name

    def set_app_sequence(self, module_id, position):
        sequence = 10
        if module_id:
            apps = request.env['ir.ui.menu'].search([('parent_id', '=', False)])
            update_sequence = False

            for i, app in enumerate(apps):
                if update_sequence:
                    app.sequence += 2
                    continue

                if app.id == module_id:
                    if position == 'After':
                        next_app_sequence = apps[i + 1].sequence if i + 1 < len(apps) else None
                        if next_app_sequence is None or (app.sequence + 1) < next_app_sequence:
                            sequence = app.sequence + 1
                            break
                        update_sequence = True
                    else:
                        prev_app_sequence = apps[i - 1].sequence if i - 1 >= 0 else None
                        if prev_app_sequence is None or (app.sequence - 1) > prev_app_sequence:
                            sequence = app.sequence - 1
                            break
                        app.sequence += 2
                        update_sequence = True
        return sequence

    def get_last_element_from_path(self, xpath_string):
        return re.sub(r'\[\d+\]', '', xpath_string.strip('/').split('/')[-1])

    def get_default_view_template(self, view_type, editable=False):
        if view_type == 'kanban':
            return """<kanban>
                                <field name="x_name"/>
                               <templates>
                                   <t t-name="kanban-box">
                                       <div class="oe_kanban_global_click">
                                           <div class="oe_kanban_details">
                                               <field name="x_name"/>
                                           </div>
                                       </div>
                                   </t>
                               </templates>
                       </kanban>"""
        elif view_type == 'form':
            return """ <form>
                            <header/>
                            <sheet> 
                                <div class="oe_title">
                                    <h1><field name="x_name" required="1" placeholder="Name..."/></h1> 
                                </div> 
                                <group/> 
                            </sheet> 
                        </form>"""
        elif view_type == 'tree':
            tree = "<tree"
            if editable:
                tree += ' editable="top"'
            tree += """>
                        <field name="x_name"/>
                    </tree>"""
            return tree

    @route('/cyllo_studio/find/functions', type="json", auth="user",
           csrf=False)
    def find_functions(self, model_name, check_unusual_days=False):
        model = request.env[model_name]
        model_class = type(model)

        is_custom_extended = lambda cls: not cls.__module__.startswith("odoo.api")
        custom_extended_classes = [cls for cls in getattr(model_class, '_BaseModel__base_classes', []) if
                                   is_custom_extended(cls)]

        classes = [cls.__name__ for cls in custom_extended_classes]

        active_include = request.env['ir.model.fields'].search(
            [('model', '=', model_name), '|', ('name', '=', 'active'), ('name', '=', 'x_active')])

        methods = []

        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)

            if (inspect.isfunction(attr) or inspect.ismethod(attr)) and not getattr(attr, '__self__', None):

                if any(name in str(attr.__qualname__) for name in classes) or 'BaseModel' in str(attr.__qualname__):
                    if check_unusual_days and attr_name == 'get_unusual_days':
                        return True  # Return True immediately if we are checking for 'get_unusual_days'

                    signature = inspect.signature(attr)
                    parameters = signature.parameters

                    if len(parameters) == 1 and (attr_name.startswith("action") or attr_name.startswith("button")):
                        methods.append(attr_name)

        if not active_include:
            methods = [method for method in methods if method not in {'action_archive', 'action_unarchive'}]

        return False if check_unusual_days else methods

    @route('/cyllo_studio/view/active_views', type="json", auth="user",
           csrf=False)
    def active_views(self, args):
        """
        Handles the activation and deactivation of views based on the input arguments.

        This method processes a request to activate or deactivate views within an action window.
        It checks the current state of the specified view type and modifies the view accordingly.

        Args:
            args (list): A list containing a single dictionary with the following keys:
                - 'viewType' (str): The type of the view (e.g., 'list', 'form').
                - 'actionId' (int): The ID of the action window.
                - 'activeView' (bool): Whether to activate or deactivate the view.
                - 'resModel' (str, optional): The model name.

        Returns:
            None
        """
        data, = args
        view_type = 'tree' if data['viewType'] == 'list' else data['viewType']
        act_window_id = request.env['ir.actions.act_window'].browse(data['actionId'])
        active_view_id = act_window_id.view_ids.search(
            [('act_window_id', '=', act_window_id.id), ('view_mode', '=', view_type),
             ('active', 'in', [True, False])],
            limit=1)
        res_model = data.get("resModel", "")
        if data.get("activeView"):
            if active_view_id:
                active_view_id.active = True
            else:
                view_id = False
                if res_model.startswith("x_") or view_type in ['calendar']:
                    arch = self.get_default_view_arch(view_type, data)
                    view_id = self.create_view(data, view_type, arch).id
                act_window_id.view_ids = [Command.create({
                    'view_mode': view_type,
                    'sequence': len(act_window_id.view_ids),
                    'view_id': view_id,
                    'active': True
                })]
        else:
            if active_view_id:
                active_view_id.write({
                    'active': False,
                    'sequence': len(act_window_id.view_ids) + 1
                })
            view_mode = act_window_id.view_mode.split(",")
            if view_type in view_mode:
                view_mode.remove(view_type)
            elif view_type == 'tree' and 'list' in view_mode:
                view_mode.remove("list")
            if not view_mode and act_window_id.view_ids:
                view = act_window_id.view_ids[0]
                view_mode.append(view.view_mode)

            act_window_id.view_mode = ",".join(view_mode)

    @route('/cyllo_studio/view/active_views/set_default_view', type="json", auth="user",
           csrf=False)
    def set_default_view(self, args):
        """
        Sets the specified view type as the default for an action window.

        This method updates the view sequence in an action window, placing the specified view type as the first view,
        and activates it if necessary. It also adjusts the sequence of other views to maintain order.

        Args:
            args (list): A list containing a single dictionary with the following keys:
                - 'siblingType' (str): The type of the view to set as default (e.g., 'list', 'form').
                - 'actionId' (int): The ID of the action window.

        Returns:
            None
        """
        data, = args
        view_type = 'tree' if data['siblingType'] == 'list' else data['siblingType']
        act_window_id = request.env['ir.actions.act_window'].browse(data['actionId'])
        if act_window_id:
            view_mode = act_window_id.view_mode.split(",")
            if view_type in view_mode:
                view_mode.remove(view_type)
            active_view_ids = act_window_id.view_ids.search(
                [('act_window_id', '=', act_window_id.id), ('view_mode', '=', view_type),
                 ('active', 'in', [True, False])],
                limit=1)
            if active_view_ids:
                active_view_ids.write({
                    'active': True,
                    'sequence': 0
                })
            else:
                act_window_id.view_ids = [Command.create({
                    'view_mode': view_type,
                    'sequence': 0,
                })]
            seq = 1
            for rec in act_window_id.view_ids.filtered(lambda record: record.view_mode != view_type):
                rec.sequence = seq
                seq += 1
            if not view_mode and act_window_id.view_ids:
                view_mode.append(act_window_id.view_ids[0].view_mode)
            act_window_id.view_mode = ",".join(view_mode)

    @route('/cyllo_studio/edit/overall_view', type="json", auth="user", csrf=False)
    def edit_overallView(self, args, kwargs):
        model = args[0].get('model')
        view_type = args[0].get('view_type')
        view_id = args[0].get('view_id')

        form_arch_base = ' '
        if kwargs['attr']:
            if kwargs['attr'] == 'default_order':
                form_arch_base = f'''<xpath expr="/{kwargs['path']}" position="attributes">
                                              <attribute name="{kwargs['attr']}">{kwargs['value']} {kwargs['order']}</attribute>
                                            </xpath>    '''
            elif kwargs['attr'] == 'quick_create_view_id':
                form_arch_base = f'''
                    <xpath expr="/{kwargs['path']}" position="attributes">
                            <attribute name='quick_create'>true</attribute>
                            <attribute name="{kwargs['attr']}">{kwargs['value']}</attribute>
                    </xpath>
                '''
            else:
                form_arch_base = f'''<xpath expr="/{kwargs['path']}" position="attributes">
                                      <attribute name="{kwargs['attr']}">{kwargs['value']}</attribute>
                                    </xpath>    '''
        print("form_arch",form_arch_base)
        if form_arch_base:
            view_rec = self.get_studio_view(view_id, model, view_type)
            view_node = etree.fromstring(view_rec.arch_base)
            view_node.append(etree.fromstring(form_arch_base))
            view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
            return form_arch_base

    @route('/cyllo_studio/pivot/edit_element', type="json", auth="user",
           csrf=False)
    def edit_pivot_element(self, kwargs):
        pivot_arch_base = f'''<xpath expr="//pivot" position="{kwargs['position']}">'''
        if kwargs['position'] == 'inside':
            pivot_arch_base += f'''<field name="{kwargs['name']}" type="{kwargs['item_type']}"  '''
            if kwargs['interval']:
                pivot_arch_base += f'''interval="{kwargs['interval']}"'''
            pivot_arch_base += '/></xpath>'
        else:
            pivot_arch_base += f'''<attribute name="{kwargs['name']}">{kwargs['item_type']}</attribute></xpath>'''
        view_rec = self.get_studio_view(kwargs['viewId'], kwargs['model'], kwargs['view_type'])
        pivot_node = etree.fromstring(view_rec.arch_base)
        pivot_node.append(etree.fromstring(pivot_arch_base))
        view_rec.arch_base = etree.tostring(pivot_node, pretty_print=True,
                                            encoding='unicode')
        return pivot_arch_base

    @route('/cyllo_studio/add/existing_field', type="json", auth="user",
           csrf=False)
    def add_existing_field(self, args, kwargs):
        model = args[0].get('model')
        view_type = args[0].get('view_type')
        view_id = args[0].get('view_id')

        arch_base = f'''<xpath expr="{args[0].get('path')}" position="{args[0].get('position')}">'''
        if kwargs.get('value'):
            for value in kwargs.get('value'):
                arch_base += f'''<field name="{value}"/>'''
        arch_base += '</xpath>'
        print('asdasdasd', arch_base)
        if arch_base:
            view_rec = self.get_studio_view(view_id, model, view_type)
            view_node = etree.fromstring(view_rec.arch_base)
            view_node.append(etree.fromstring(arch_base))
            view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
            return arch_base



    @http.route('/cyllo_studio/get_non_abstract_non_transient_models', type='json', auth='user')
    def get_non_abstract_non_transient_models(self):
        Model = request.env['ir.model']
        non_abstract_non_transient_models = []

        for model in Model.search([('transient', '=', False)]):
            try:
                # Check if the model exists in the environment and get its class safely
                model_env = http.request.env.get(model.model)
                # is_abstract = model_env._abstract
                is_abstract = model_env._abstract or not model_env._auto
                # Ensure the model class exists and isn't abstract or transient
                if not is_abstract:
                    non_abstract_non_transient_models.append({
                        'id': model.id,
                        'model': model.model,
                        'name': model.name
                    })
            except Exception as e:
                request.env.cr.rollback()  # Avoid transaction issues
                continue
        return non_abstract_non_transient_models

    def is_studio_user(self):
        studio = request.session.get('studio')
        is_studio_debug = bool(studio) and '1' in studio
        is_erp_manager = request.env.user.has_group('base.group_erp_manager')

        if is_erp_manager and not is_studio_debug:
            '''multi tab case may be in session deosn't have debug = studio
            so we need to manualy  debug session in to studio to not get an error'''
            request.session.studio = '1'

        if not is_erp_manager:
            raise AccessError(_("You don't have the access to this request."))

# --------------------------Kanban View functionality ----------------------------------------------------

    @route('/cyllo_studio/kanban/add/field', type="json", auth="user",
           csrf=False)
    def add_kanban_field(self, view_id, view_type, model, path, position, field, x2many):
        view_rec = self.get_studio_view(view_id, model, view_type)
        view_arch_1 = f'''
                             <xpath expr="{x2many}" position="inside">
                                  <field name="{field}"/>
                             </xpath>'''
        view_arch_2 = f'''
                             <xpath expr="/{path}" position="{position}">
                                 <field name="{field}"/>
                             </xpath>'''
        view_node = etree.fromstring(view_rec.arch_base)
        view_node.append(etree.fromstring(view_arch_1))
        view_node.append(etree.fromstring(view_arch_2))
        combined_arch = view_arch_1 + view_arch_2
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        return combined_arch

    @route('/cyllo_studio/kanban/add/text', type="json", auth="user",
           csrf=False)
    def add_kanban_text(self, viewId, viewType, model, path, position, properties):
        print(self, "asdsa")
        view_rec = self.get_studio_view(viewId, model, viewType)
        view_arch = f'''
                              <xpath expr="/{path}" position="{position}">
                                      <span class="{properties['class_names']}">{escape(properties['string'])}</span>
                              </xpath>
                          '''
        view_node = etree.fromstring(view_rec.arch_base)
        view_node.append(etree.fromstring(view_arch))
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        return view_arch

    @route('/cyllo_studio/kanban/add/ribbon', type="json", auth="user",
           csrf=False)
    def add_kanban_ribbon(self, viewId, viewType, model, path, position, properties):
        print("okkkkkk", properties)
        view_rec = self.get_studio_view(viewId, model, viewType)

        view_arch = f'''
                           <xpath expr="/{path}" position="{position}">
                               <div class="ribbon ribbon-top-right" invisible='{properties['invisible']}'>
                                   <span class="{properties['color']}">{escape(properties['string']) if properties['string'] else ''}</span>
                               </div>
                           </xpath>
                       '''
        view_node = etree.fromstring(view_rec.arch_base)
        view_node.append(etree.fromstring(view_arch))
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        print("ssss", view_arch)
        return view_arch

    @route("/cyllo_studio/kanban/update/field", type="json", auth="user", csrf=False)
    def update_kanban_field(self, args):
        view_rec = self.get_studio_view(args.get("view_id"), args.get("model"), args.get("view_type"))
        view_node = etree.fromstring(view_rec.arch_base)
        view_arch = ''''''
        print('UPDATE KANBAN ABD : ',args.get("invisible"))
        not_present_field = self.create_invisible([args])
        print('UPDATE KANBAN ABD not present : ', not_present_field)

        if args.get("invisible") or args.get("invisible") == "False":
            view_arch = f'''
                            <xpath expr="/{args.get("path")}" position="attributes">
                                <attribute name='invisible'>{args.get("invisible")}</attribute>
                            </xpath>
                        '''
            if not_present_field:
                not_present_field1 = f"""<xpath expr="//templates" position="before">
                                      {not_present_field}
                                 </xpath>"""
                not_present_field2 = f""" <xpath expr="{args.get("path")}" position="after">{not_present_field}</xpath>"""
                view_node.append(etree.fromstring(not_present_field1))
                view_node.append(etree.fromstring(not_present_field2))
            view_node.append(etree.fromstring(view_arch))
            view_rec.arch_base = etree.tostring(view_node, pretty_print=True,
                                                encoding='unicode')


    @route('/cyllo_studio/delete/kanban/field', type="json", auth="user",
           csrf=False)
    def delete_kanban_field(self, view_id, view_type, model, path, field_name=None, child_field_name=None):
        view_rec = self.get_studio_view(view_id, model, view_type)
        view_node = etree.fromstring(view_rec.arch_base)

        view_arch = f'''
                                <xpath expr="/{path}" position="replace"/>
                           '''
        view_node.append(etree.fromstring(view_arch))
        arch = view_arch

        if field_name:
            view_arch_2 = f'''
                                     <xpath expr="//templates" position="before">
                                          <field name="{field_name}"/>
                                     </xpath>
                                 '''
            view_node.append(etree.fromstring(view_arch_2))
            arch += view_arch_2

        if child_field_name:
            for field_name in child_field_name:
                view_arch_3 = f'''
                                             <xpath expr="//templates" position="before">
                                                  <field name="{field_name}"/>
                                             </xpath>
                                         '''
                view_node.append(etree.fromstring(view_arch_3))
                arch += view_arch_3

        view_rec.arch_base = etree.tostring(view_node, pretty_print=True,
                                            encoding='unicode')
        return arch

    @route('/cyllo_studio/kanban/add/div', type="json", auth="user",
           csrf=False)
    def add_kanban_div(self, view_id, view_type, model, path, position):
        view_rec = self.get_studio_view(view_id, model, view_type)
        view_arch = f'''
                             <xpath expr="/{path}" position="{position}">
                                 <div class="d-flex"/>
                             </xpath>'''
        view_node = etree.fromstring(view_rec.arch_base)
        view_node.append(etree.fromstring(view_arch))
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        return view_arch

    @route('/cyllo_studio/kanban/remove', type="json", auth="user",
           csrf=False)
    def remove_kanban_element(self, view_id, view_type, model, path,
                              field_name):
        view_rec = self.get_studio_view(view_id, model, view_type)
        view_node = etree.fromstring(view_rec.arch_base)

        view_arch = f'''
                          <xpath expr="/{path}" position="replace"/>
                        '''
        view_node.append(etree.fromstring(view_arch))

        view_arch_2 = ""

        if field_name:
            view_arch_2 = f'''
                                  <xpath expr="//templates" position="before">
                                       <field name="{field_name}"/>
                                  </xpath>
                              '''
            view_node.append(etree.fromstring(view_arch_2))

        arch = view_arch + view_arch_2
        view_rec.arch_base = etree.tostring(view_node, pretty_print=True,
                                            encoding='unicode')
        return arch

    @route('/cyllo_studio/kanban/move', type="json", auth="user",
           csrf=False)
    def move_kanban_element(self, view_id, view_type, model, path, position, sibling_path):
        view_rec = self.get_studio_view(view_id, model, view_type)
        view_arch = f'''
                          <xpath expr="/{sibling_path}" position="{position}">
                              <xpath expr="/{path}" position="move"/>
                          </xpath>'''
        view_node = etree.fromstring(view_rec.arch_base)
        view_node.append(etree.fromstring(view_arch))
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        return view_arch

    ##-------------------------------------------------------------------------------------------


    # list functionalities

    @route('/cyllo_studio/move/tree', auth="user", csrf=False, type='json')
    def move_tree(self, args, kwargs, model, view_id, view_type):
        if not kwargs['path']:
            kwargs['path'] = '/tree'
        tree_arch_base = f'<xpath expr="/{kwargs["path"]}" position="{kwargs["position"]}">' \
                         f'<xpath expr="/{kwargs["fieldPath"]}" position="move"/>' \
                         '</xpath>'
        View = request.env['ir.ui.view'].sudo()

        if not kwargs['view_id']:
            kwargs['view_id'] = View.default_view(kwargs['model'],
                                                  kwargs['viewType'])
        view_rec = self.get_studio_view(view_id, model, view_type)
        form_node = etree.fromstring(view_rec.arch_base)
        print("tree_arch_base",tree_arch_base)
        form_node.append(etree.fromstring(tree_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')

        return tree_arch_base

    # New Field Create
    @route('/cyllo_studio/create/new_fields', type="json", auth="user",
           csrf=False)
    def create_new_fields(self, args, view_id, model, view_type):
        print('create_new_fields', args, view_id, model, view_type)
        form_arch_base = ''
        if args[0]['edit']:
            print('edit')
            for key, value in args[0]['value'].items():
                form_arch_base = f'''
                               <xpath expr="/{args[0]["field_path"]}" position="attributes">
                               <attribute name="{key}">{value}</attribute>
                               </xpath>'''
        if not args[0]['edit'] and args[0]['technical_name']:
            print('create')
            related_model = args[0].get('related_model')
            if args[0]['field_type'] in ['many2one', 'many2many', 'one2many']:
                if not args[0].get('related_model'):
                    raise ValidationError(_(
                        "The operation cannot be completed: The relational field is mandatory for a  '%s' field."
                    ) % args[0]['field_type'])
            values = {
                'name': args[0]['technical_name'],
                'field_description': args[0]['label'],
                'ttype': args[0]['field_type'],
                'is_studio': True,
                'model_id': request.env['ir.model'].search(
                    [('model', '=', model)]).id,
            }
            if args[0]['field_type'] in ['many2one', 'many2many']:
                values['relation'] = related_model

            new_field = request.env['ir.model.fields'].create(values)

            form_arch_base = f"""
                <xpath expr='/{args[0]['field_path']}' position='inside'>
                    <field name='{args[0]['technical_name']}'
            """
            print('form_arch_base', new_field)
            for (key, value) in args[0]['attrs'].items():
                print('dssf', key, value)
                if key and value:
                    if args[0]['field_type'] in ['many2one', 'many2many', 'one2many'] and key in ['context', 'domain']:
                        form_arch_base += f'''{key}="{value}"'''
                    else:
                        form_arch_base += f'''{key}="{value}"'''

            form_arch_base += f'''options="{args[0]['optional_fields']}"'''
            form_arch_base += "/>"
            args[0] = {'path': args[0]['field_path'], **args[0]}
            form_arch_base += "</xpath>"
        print('123ewqdsas',form_arch_base)
        view_rec = self.get_studio_view(view_id, model, view_type)

        # form_node = etree.fromstring(view_rec.arch_base)
        # form_node.append(etree.fromstring(form_arch_base))
        # view_rec.arch_base = etree.tostring(form_node, pretty_print=True,
        #                                     encoding='unicode')
        # return form_arch_base
        return  None


    # form functionality

    @route('/cyllo_studio/add/component', type="json", auth="user",
           csrf=False)
    def add_component(self, args):
        form_arch_base = f'<xpath expr="/{args[0]["path"]}" position="{args[0]["position"]}">' \
                         f'{args[0]["item"]}' \
                         '</xpath>'
        view_rec = self.get_studio_view(args[0]["view_id"], args[0]["model"], args[0]["view_type"])
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    @route('/cyllo_studio/add/form_tree', type="json", auth="user",
           csrf=False)
    def add_form_tree(self, kwargs):
        print("AddedFormTree", kwargs)
        values = {
            'name': kwargs['technical_name'],
            'field_description': kwargs['label'],
            'ttype': kwargs['selected_value'],
            'is_studio': True,
            'model_id': request.env['ir.model'].search(
                [('model', '=', kwargs['resModel'])]).id
        }
        if values['ttype'] == 'many2many':
            values.update({
                'relation': request.env['ir.model'].browse(int(kwargs['related_model_id'])).model
            })
        else:
            values.update({
                'relation': request.env['ir.model'].browse(
                    kwargs['related_model_field']['model_id'][0]).model,
                'relation_field': kwargs['related_model_field']['name']
            })

        new_field = request.env['ir.model.fields'].create(values)

        self.ensure_unique_relation_table(new_field)

        form_arch_base = f'<xpath expr="/{kwargs["path"]}" position="{kwargs["position"]}">' \
                         f'<field name="{kwargs["technical_name"]}"><tree>'

        field_ids = list(map(int, kwargs['field_ids']))

        tree_fields = request.env['ir.model.fields'].browse(field_ids)
        has_one_currency = False
        for field in tree_fields:
            if field.ttype == "monetary" and not has_one_currency:
                related_model_id = kwargs.get('related_model_id')
                currency_field_name = self.get_currency_field(related_model_id, field.name)
                if currency_field_name:
                    form_arch_base += f"<field name='{currency_field_name}' column_invisible='1'/>"
                has_one_currency = True
            form_arch_base += f'<field name="{field.name}"/>'
        form_arch_base += '</tree></field></xpath>'

        print("AArchBase", form_arch_base)
        view_rec = self.get_studio_view(kwargs['view_id'], kwargs['model'], kwargs['view_type'])
        print("lkhj")
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    @route('/cyllo_studio/form/create/new_fields', type="json", auth="user",
               csrf=False)
    def form_create_new_fields(self, args, view_id, model, view_type):
            print("args",args)
            if args[0]['edit']:
                form_arch_combined = f"""
                   <xpath expr='/{args[0]["cy_path"]}' position='attributes'>
                       <attribute name='string'>{escape(args[0]["label"])}</attribute>
                       <attribute name='widget'>{escape(args[0]["widget"])}</attribute>
                       <attribute name='help'>{escape(args[0]["help"])}</attribute>
                       <attribute name='placeholder'>{escape(args[0]["placeholder"])}</attribute>
                       <attribute name='invisible'>{args[0]["invisible"]}</attribute>
                       <attribute name='readonly'>{args[0]["readonly"]}</attribute>
                       <attribute name='required'>{args[0]["required"]}</attribute>

                       """
                form_arch_combined += f"""</xpath>
                                                 """
                view_rec = self.get_studio_view(view_id, model, view_type)
                form_node = etree.fromstring(view_rec.arch_base)
                form_node.append(etree.fromstring(form_arch_combined))
                view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
                print("form_arch_combined", form_arch_combined)
                return form_arch_combined

    @route('/cyllo_studio/add/page', type="json", auth="user",
           csrf=False)
    def add_page(self, args, kwargs, model, view_id, view_type):
        print("addddddd page",kwargs)

        View = request.env['ir.ui.view'].sudo()
        if not kwargs['view_id']:
            kwargs['view_id'] = View.default_view(kwargs['model'],
                                                  kwargs['viewType'])

        form_arch_base = f'<xpath expr="/{kwargs["path"]}" position="inside">' \
                         f'<page string="New Page"></page>' \
                         '</xpath>'

        view_rec = self.get_studio_view(view_id, model, view_type)
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    @route('/cyllo_studio/update/page', type="json", auth="user",
           csrf=False)
    def update_page(self, args, kwargs, model, view_id, view_type):
        View = request.env['ir.ui.view'].sudo()
        # if not kwargs['view_id']:
        #     kwargs['view_id'] = View.default_view(kwargs['model'],
        #                                           kwargs['viewType'])
        # group_ids = list(map(int, kwargs['groups']))
        # groups = ','.join(request.env['res.groups'].browse(
        #     group_ids).get_external_id().values())
        form_arch_base = f'<xpath expr="/{kwargs["path"]}" position="attributes">' \
                         f'<attribute name="string">{kwargs["string"]}</attribute>' \
                         f'<attribute name="autofocus">{"autofocus" if kwargs["autofocus"] else ""}</attribute>' \
                         f'<attribute name="invisible">{unescape(escape(kwargs["invisible"]))}</attribute>' \
                         '</xpath>'

        view_rec = self.get_studio_view(view_id, model, view_type)
        form_node = etree.fromstring(view_rec.arch_base)
        form_arch_base = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', form_arch_base)
        form_arch_base = re.sub(r'>([^<]*?)\s+</', lambda match: f'>{match.group(1).strip()}<', form_arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        print("fghj",form_arch_base)
        return form_arch_base

    @route('/cyllo_studio/move/page', type="json", auth="user",
           csrf=False)
    def move_page(self, args, kwargs, model, view_id, view_type="form"):
        print(self, args, kwargs, model, view_id)

        View = request.env['ir.ui.view'].sudo()
        if not kwargs['view_id']:
            kwargs['view_id'] = View.default_view(kwargs['model'],
                                                  "form")
        form_arch_base = f'<xpath expr="/{kwargs["path"]}" position="{kwargs["position"]}">' \
                         f'<xpath expr="/{kwargs["pagePath"]}" position="move"/>' \
                         '</xpath>'

        view_rec = self.get_studio_view(view_id, model, view_type)
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        print("form_arch_base",form_arch_base)
        return form_arch_base

    @route('/cyllo_studio/delete/existing_page', auth="user", csrf=False,
           type='json')
    def delete_existing_page(self, args, kwargs, model, view_id, view_type):

        View = request.env['ir.ui.view'].sudo()

        form_arch_base = f'''<xpath expr="{args[0]['path']}" position="replace"/>'''
        view_rec = self.get_studio_view(view_id, model, view_type)
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True,
                                            encoding='unicode')
        return form_arch_base

    # --------------------------Smart Button functionality ----------------------------------------------------

    @route('/cyllo_studio/add/smart_button', type="json", auth="user",
           csrf=False)
    def add_smart_button(self, kwargs):
        view_rec = self.get_studio_view(kwargs['view_id'], kwargs['model'], 'form')
        model_id = request.env['ir.model'].search(
            [('model', '=', kwargs['model'])])
        vals = {
            'name': f'x_cy_{kwargs["label"].replace(" ", "_").lower()}_count{str(uuid.uuid4())[:4]}',
            'field_description': f'{kwargs["label"].title()} Count',
            'model_id': model_id.id,
            'ttype': 'char',
            'store': False,
            'depends': kwargs['field'],
        }
        compute_field = request.env['ir.model.fields'].create(vals)
        if kwargs['domain'] != '[]':
            domain = kwargs['domain'][:-1] + f",('id', 'in', record.{kwargs['field'].strip()}.ids)]"
            compute = f"""for record in self:
        record['{compute_field.name}'] = len(record.{kwargs['field'].strip()}.search({domain}))
                    """
            kwargs['domain'] = kwargs['domain'][:-1] + ',]'
        else:
            compute = f"""for record in self:
        record['{compute_field.name}'] = len(record.{kwargs['field'].strip()})
                                """
        compute_field.compute = compute
        action_id = request.env['ir.actions.act_window'].create({
            'name': kwargs["label"].title(),
            'res_model': kwargs['field_model'],
            'view_mode': 'tree,form',
            'domain': kwargs['domain']
        })
        form_arch_base = ''
        if kwargs['addButtonBox']:
            form_arch_base += f'''<xpath expr="//form/sheet/*[1]" position="before">
                                              <div class="oe_button_box" name="button_box" cy-xpath="//form/sheet/div[@class='oe_button_box']">
                                             <button type="action" name="{action_id.id}" invisible='{kwargs["invisible"]}' class="oe_stat_button" icon="{kwargs["icon"]}" '''
            if kwargs['groups']:
                group_ids = list(map(int, kwargs['groups']))
                groups = ','.join(request.env['res.groups'].browse(
                    group_ids).get_external_id().values())
                form_arch_base += f'groups="{groups}"'

            form_arch_base += f'><field name="{compute_field.name}" widget="statinfo" '
            if kwargs['label']:
                form_arch_base += f'string="{kwargs["label"].title()}"'
            form_arch_base += '/></button></div>'
        else:
            form_arch_base += f'''<xpath expr="{kwargs['path']}" position="inside">
                                <button type="action" name="{action_id.id}" invisible='{kwargs["invisible"]}' class="oe_stat_button" icon="{kwargs["icon"]}" '''
            if kwargs['groups']:
                group_ids = list(map(int, kwargs['groups']))
                groups = ','.join(request.env['res.groups'].browse(
                    group_ids).get_external_id().values())
                form_arch_base += f'groups="{groups}"'

            form_arch_base += f'><field name="{compute_field.name}" widget="statinfo" '
            if kwargs['label']:
                form_arch_base += f'string="{kwargs["label"].title()}"'
            form_arch_base += '/></button>'

        form_arch_base += '</xpath>'
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    @route('/cyllo_studio/update/smart_button', type="json", auth="user",
           csrf=False)
    def update_smart_button(self, kwargs):
        view_rec = self.get_studio_view(kwargs['view_id'], kwargs['model'], 'form')
        group_ids = list(map(int, kwargs['groups']))
        groups = ','.join(request.env['res.groups'].browse(group_ids).get_external_id().values())
        form_arch = f'''<xpath expr="/{kwargs['path']}" position="attributes">
                            <attribute name="string">{kwargs['label']}</attribute>
                            <attribute name="icon">{kwargs['icon']}</attribute>
                            <attribute name="groups">{groups}</attribute>
                            <attribute name="invisible">{kwargs['invisible']}</attribute>
                        </xpath>'''
        form_arch_2 = ''
        if 'span' in kwargs['string_path']:
            form_arch_2 = f'''<xpath expr="/{kwargs['string_path']}" position="replace">
                               <span class="o_stat_text">{kwargs['label']}</span>
                           </xpath>'''
        elif kwargs['status_label_path']:
            form_arch_2 = f'''<xpath expr="/{kwargs['status_label_path']}" position="attributes">
                           <attribute name="status_label">{kwargs['label']}</attribute>
                       </xpath>'''
        else:
            form_arch_2 = f'''<xpath expr="/{kwargs['string_path']}" position="attributes">
                       <attribute name="string">{kwargs['label']}</attribute>
                   </xpath>'''
        form_node = etree.fromstring(view_rec.arch_base)

        form_node.append(etree.fromstring(form_arch))
        # form_node.append(etree.fromstring(form_arch_1)) if form_arch_1 else None
        form_node.append(etree.fromstring(form_arch_2))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        combined_arch = form_arch + form_arch_2
        return combined_arch

    @route('/cyllo_studio/remove/smart_button', type="json", auth="user",
           csrf=False)
    def remove_smart_button(self, kwargs):
        form_arch = f'''<xpath expr="{kwargs['path']}" position="replace"/>'''
        view_rec = self.get_studio_view(kwargs['view_id'], kwargs['model'], 'form')
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch

    @route('/cyllo_studio/move/smart_button', type="json", auth="user",
           csrf=False)
    def move_smart_button(self, kwargs):
        view = request.env['ir.ui.view'].sudo()
        if not kwargs['view_id']:
            kwargs['view_id'] = view.default_view(kwargs['model'],
                                                  kwargs['viewType'])
        form_arch_base = f'<xpath expr="/{kwargs["sourcePath"]}" position="{kwargs["position"]}">' \
                         f'<xpath expr="/{kwargs["smartButtonPath"]}" position="move"/>' \
                         '</xpath>'

        view_rec = self.get_studio_view(kwargs["view_id"], kwargs["model"], kwargs['viewType'])
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    ##-------------------------------------------------------------------------------------------

    # --------------------------Button functionality ----------------------------------------------------

    @route('/cyllo_studio/add/button_item', type='json', auth="user", csrf=False)
    def add_button_item(self, kwargs, button_properties):
        view_rec = self.get_studio_view(kwargs['viewId'], kwargs['model'], kwargs['viewType'])
        group_ids = list(map(int, kwargs.pop('groupIds')))
        if group_ids:
            button_properties['groups'] = ','.join(request.env['res.groups'].browse(
                group_ids).get_external_id().values())
        form_arch = f'<xpath expr="/{kwargs["path"]}" position="{kwargs["position"]}"><button'
        for key, value in button_properties.items():
            if value:
                form_arch += f" {key}='{value}'"
        form_arch += " colspan='2'/> </xpath>"
        form_node = etree.fromstring(view_rec.arch_base)
        new_button = kwargs.get('newHeader')
        if new_button:
            if new_button == "/form/":
                new_button = "/form"
                position = "inside"
            else:
                position = "before"
            header_arch = f'<xpath expr="/{new_button}" position="{position}"><header/></xpath> '
            form_node.append(etree.fromstring(header_arch))
        form_node.append(etree.fromstring(form_arch))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch

    @route('/cyllo_studio/update/button_item', type='json', auth="user", csrf=False)
    def update_button_item(self, kwargs, button_properties):
        if kwargs['viewType'] == 'list':
            kwargs['viewType'] = 'tree'
        group_ids = list(map(int, kwargs.pop('groupIds')))
        if group_ids:
            button_properties['groups'] = ','.join(request.env['res.groups'].browse(
                group_ids).get_external_id().values())
        form_arch_button = f'''
                            <xpath expr="/{kwargs["path"]}" position="attributes">'''

        for key, value in button_properties.items():
            if key in {'invisible', 'string'} and key not in {'name', 'type'}:
                form_arch_button += f" <attribute name='{key}'>{escape(value)}</attribute>"
            elif key not in {'name', 'type'}:
                form_arch_button += f" <attribute name='{key}'>{value}</attribute>"
        form_arch_button += """</xpath>"""
        view_rec = self.get_studio_view(kwargs['viewId'], kwargs['model'], kwargs['viewType'])
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_button))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_button

    @route('/cyllo_studio/delete/button', auth="user", csrf=False, type='json')
    def delete_button(self, kwargs):
        view_arch = f'''<xpath expr="/{kwargs['path']}" position="replace"/>'''
        view_rec = self.get_studio_view(kwargs['view_id'], kwargs['model'], kwargs['viewType'])
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(view_arch))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return view_arch

    @route('/cyllo_studio/move/button', type="json", auth="user",
           csrf=False)
    def move_button(self, kwargs):
        form_arch_base = f'<xpath expr="/{kwargs["path"]}" position="{kwargs["position"]}">' \
                         f'<xpath expr="/{kwargs["buttonPath"]}" position="move"/>' \
                         '</xpath>'
        view_rec = self.get_studio_view(kwargs["view_id"], kwargs["model"], kwargs["view_type"])
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    ##-------------------------------------------------------------------------------------------

    # --------------------------StatusBar functionality ----------------------------------------------------

    @route('/cyllo_studio/add/statusbar', type="json", auth="user",
           csrf=False)
    def add_statusbar(self, args, kwargs):
        if args['is_new']:
            model_id = request.env['ir.model']._get_id(args['model'])

            request.env['ir.model.fields'].create({
                'name': args['field'],
                'field_description': args['label'],
                'ttype': 'selection',
                'selection_ids': [
                    Command.create(
                        {'value': element.lower(), 'name': element,
                         'sequence': idx})
                    for idx, element in
                    enumerate(kwargs['values'])
                ],
                'model_id': model_id,
            })
        form_arch_base = f'''<xpath expr="/{args['path']}" position="inside">
                               <field name="{args['field']}" widget="statusbar" '''
        options = {}
        if kwargs['clickable']:
            options['clickable'] = kwargs['clickable']
        if kwargs['foldField']:
            options['fold_field'] = kwargs['foldField']
        if options:
            form_arch_base += f'options="{options}" '

        if kwargs['statusbarVisible']:
            form_arch_base += 'statusbar_visible="{}" '.format(re.sub(r",\s+", ",", kwargs["statusbarVisible"]))

        if kwargs['invisible']:
            form_arch_base += f"invisible='{kwargs['invisible']}' "

        if kwargs['group_ids']:
            group_ids = list(map(int, kwargs['group_ids']))
            groups = ','.join(request.env['res.groups'].browse(group_ids).get_external_id().values())
            form_arch_base += f'groups="{groups}" '

        if kwargs['defaultValue']:
            field_id = request.env['ir.model.fields'].search(
                [('name', '=', args['field']), ('model', '=', args['model'])], limit=1)
            print("IdddddL", field_id.id, field_id.name)
            request.env['ir.default'].create({'field_id': field_id.id, 'json_value': f'"{kwargs["defaultValue"]}"'})

        form_arch_base += '/></xpath>'
        print("FormARc", form_arch_base)
        view_rec = self.get_studio_view(args['view_id'], args['model'], args['view_type'])
        form_node = etree.fromstring(view_rec.arch_base)
        header_arch = self.create_header(args.get('header', None))
        if header_arch:
            form_node.append(etree.fromstring(header_arch))
        form_node.append(etree.fromstring(form_arch_base))

        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')

        return form_arch_base

    ##-------------------------------------------------------------------------------------------

    @route('/cyllo_studio/add/avatar', type="json", auth="user",
           csrf=False)
    def add_avatar(self, path, is_new, field, model, view_id, view_type):
        if is_new:
            model_id = request.env['ir.model']._get_id(model)

            field = request.env['ir.model.fields'].create({
                'name': field['name'],
                'field_description': field['label'],
                'ttype': 'binary',
                'model_id': model_id,
            })
            form_arch_base = f'''<xpath expr="{path}" position="before">
                                             <field name="{field['name']}" widget="image" class="oe_avatar"/>
                                             </xpath>'''
        else:
            form_arch_base = f'''<xpath expr="{path}" position="before">
                                 <field name="{field['name']}" widget="image" class="oe_avatar"/>
                                 </xpath>'''

        view_rec = self.get_studio_view(view_id, model, view_type)

        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base

    @route('/cyllo_studio/FieldPositionMove', auth="user", csrf=False,
           type='json')
    def field_position_move(self, args):
        view_rec = self.get_studio_view(args['view_id'], args['model'], 'form')
        form_arch_base = f'<xpath expr="/{args["path"]}" position="{args["position"]}">'
        if args['has_multipath']:
            first_path = args['item_path']["first_path"]
            second_path = args['item_path']["second_path"]

            if (args["direction"] == "down" or not args["inSource"]) and self.get_last_element_from_path(
                    first_path) == self.get_last_element_from_path(second_path):
                form_arch_base += f'<xpath expr="/{first_path}" position="move"/>' * 2
            else:
                form_arch_base += f'<xpath expr="/{first_path}" position="move"/>'
                form_arch_base += f'<xpath expr="/{second_path}" position="move"/>'
        else:
            form_arch_base += f'<xpath expr="/{args["item_path"]}" position="move"/>'

        form_arch_base += '</xpath>'
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        root = ET.fromstring(view_rec.arch_base)
        item_count = len(root.findall('.//xpath'))
        return {
            'ItemCount': item_count,
            'viewId': view_rec.id,
            'FormArch': form_arch_base,
            'ViewArch': view_rec.arch_base,
        }

    @route('/cyllo_studio/find/groups', type="json", auth="user",
           csrf=False)
    def find_group_ids(self, groups):
        groups = groups.split(',')
        groups = [item.strip() for item in groups]
        return [request.env.ref(i).id for i in groups]

    #-------------------------Filter functionality---------------------------------------------------

    @route('/cyllo_studio/search/add/filter', type="json", auth="user",
           csrf=False)
    def add_filter(self, sibling_path, properties, view_id, model):
        view_rec = self.get_studio_view(view_id, model, 'search')
        properties['name'] = properties['string'].lower().replace(' ', '_') + str(uuid.uuid4())[:4]

        if properties['groupIds']:
            group_ids = list(map(int, properties.pop('groupIds')))
            groups = ','.join(request.env['res.groups'].browse(
                group_ids).get_external_id().values())
            properties['groups'] = groups
        if 'groupIds' in properties:
            properties.pop('groupIds')

        position = "inside" if sibling_path == "/search" else "after"
        search_arch = f'''
            <xpath expr="/{sibling_path}" position="{position}">
                <filter '''
        for key, value in properties.items():
            if key in ['domain', 'name', 'string']:
                value = escape(value)
            search_arch += f"{key}='{value}' "
        search_arch += '''/> 
            </xpath>'''
        search_node = etree.fromstring(view_rec.arch_base)
        search_node.append(etree.fromstring(search_arch))

        view_rec.arch_base = etree.tostring(search_node, pretty_print=True, encoding='unicode')
        return search_arch

    #--------------------------search functionality--------------------------------------------------

    @route('/cyllo_studio/add/search_field', type="json", auth="user",
           csrf=False)
    def add_search_field(self, path, view_id, model, properties):
        view_rec = self.get_studio_view(view_id, model, 'search')
        position = "inside" if path == "/search" else "after"

        search_arch = f'''
            <xpath expr="/{path}" position="{position}">
                <field name="{properties["field"]}" 
                invisible="{properties['invisible']}"'''
        if properties['string']:
            search_arch += f' string="{escape(properties["string"])}" '
        if properties['groupIds']:
            group_ids = list(map(int, properties['groupIds']))
            groups = ','.join(request.env['res.groups'].browse(
                group_ids).get_external_id().values())
            search_arch += f' groups="{groups}" '
        else:
            search_arch += ' groups=""'
        search_arch += ' /> </xpath>'
        search_node = etree.fromstring(view_rec.arch_base)
        search_node.append(etree.fromstring(search_arch))
        view_rec.arch_base = etree.tostring(search_node, pretty_print=True, encoding='unicode')
        return search_arch

    #-----------------------Add separator--------------------------------------------------------

    @route('/cyllo_studio/search/add/separator', type="json", auth="user",
           csrf=False)
    def add_separator(self, sibling_path, view_id, model):
        view_rec = self.get_studio_view(view_id, model, 'search')
        search_arch = f'''<xpath expr="{sibling_path}" position="after">
                <separator/>
            </xpath>'''
        search_node = etree.fromstring(view_rec.arch_base)
        search_node.append(etree.fromstring(search_arch))
        view_rec.arch_base = etree.tostring(search_node, pretty_print=True, encoding='unicode')
        return search_arch

    #-------------------------Groupby functionality--------------------------------------------------

    @route('/cyllo_studio/add/group_by', type="json", auth="user",
           csrf=False)
    def add_group_by(self, path, view_id, model, properties):
        view_rec = self.get_studio_view(view_id, model, 'search')
        name = properties['field'].lower().replace(' ', '_') + str(uuid.uuid4())[:4]
        context = {
            'group_by': properties['field'], }
        position = "inside" if path == "/search" else "after"
        search_arch = f'''
            <xpath expr="/{path}" position="{position}">
                <filter name="{name}" context="{context}" 
                invisible="{properties['invisible']}"'''
        if properties['string']:
            search_arch += f' string="{escape(properties["string"])}" '
        if properties['groupIds']:
            group_ids = list(map(int, properties['groupIds']))
            groups = ','.join(request.env['res.groups'].browse(
                group_ids).get_external_id().values())
            search_arch += f' groups="{groups}" '
        else:
            search_arch += ' groups=""'
        search_arch += ' /> </xpath>'
        search_node = etree.fromstring(view_rec.arch_base)
        search_node.append(etree.fromstring(search_arch))
        view_rec.arch_base = etree.tostring(search_node, pretty_print=True, encoding='unicode')
        return search_arch




    #--------------------------pivot functionality ----------------------------------------------------

    @route('/cyllo_studio/pivot/remove_element', type="json", auth="user",
           csrf=False)
    def remove_pivot_element(self, view_id, view_type, model, path):
        pivot_arch_base = f'<xpath expr="/{path}" position="replace"/>'
        view_rec = self.get_studio_view(view_id, model, view_type)
        pivot_node = etree.fromstring(view_rec.arch_base)
        pivot_node.append(etree.fromstring(pivot_arch_base))
        view_rec.arch_base = etree.tostring(pivot_node, pretty_print=True, encoding='unicode')
        return pivot_arch_base


     ##-------------------------------------------------------------------------------------------

    @route('/cyllo_studio/graph/edit_element', type="json", auth="user", csrf=False)
    def edit_graph_element(self, view_id, view_type, model, position, name, item_type, interval, **kw):
        graph_arch_base = f'''<xpath expr="//graph" position="{position}">'''
        if position == 'inside':
            graph_arch_base += f'''<field name="{name}" '''
            # graph_arch_base += f'''<field name="{name}" type="{item_type}"'''
            if item_type:
                graph_arch_base += f'''type="{item_type}"'''
            if interval:
                graph_arch_base += f'''interval="{interval}"'''
            graph_arch_base += '/></xpath>'
        else:
            graph_arch_base += f'''<attribute name="{name}">{item_type}</attribute></xpath>'''

        view_rec = self.get_studio_view(view_id, model, view_type)
        graph_node = etree.fromstring(view_rec.arch_base)

        existing_element = graph_node.xpath(
            f"//field[@type='{item_type}']" if position == 'inside' else f"//attribute[@name='{name}']"
        )

        if existing_element:

            parent_node = existing_element[0].getparent()

            parent_node.remove(existing_element[0])

            # Remove the parent xpath node if it becomes empty
            if len(parent_node) == 0:
                grandparent_node = parent_node.getparent()
                if grandparent_node is not None:
                    grandparent_node.remove(parent_node)

        graph_node.append(etree.fromstring(graph_arch_base))
        view_rec.arch_base = etree.tostring(graph_node, pretty_print=True, encoding='unicode')
        return graph_arch_base

    @route('/cyllo_studio/graph/remove_element', type="json", auth="user",
           csrf=False)
    def remove_graph_element(self, view_id, view_type, model, field, **kwargs):
        # graph_arch_base = f'<xpath expr="/{field}" position="replace"/>'
        view_rec = self.get_studio_view(view_id, model, view_type)
        graph_node = etree.fromstring(view_rec.arch_base)

        if ':' in field:
            key, value = field.split(':', 1)
            # Use the key for further processing
            field_to_use = key
        else:
            field_to_use = field

        existing_element = f'''<xpath expr="field[@name='{field_to_use}']" position="replace"/>'''
        graph_node = etree.fromstring(view_rec.arch_base)
        graph_node.append(etree.fromstring(existing_element))
        view_rec.arch_base = etree.tostring(graph_node, pretty_print=True, encoding='unicode')
        return existing_element




    # --------------------------------calendar view------------------------------------------------------

    @route('/cyllo_studio/calendar/remove/item', type="json", auth="user",
           csrf=False)
    def remove_calendar_item(self, view_id, model, path):
        view_rec = self.get_studio_view(view_id, model, 'calendar')
        calendar_arch = f'''
                   <xpath expr="/{path}" position="replace"/>
                   '''
        calendar_node = etree.fromstring(view_rec.arch_base)
        calendar_node.append(etree.fromstring(calendar_arch))
        view_rec.arch_base = (etree.tostring(calendar_node, pretty_print=True, encoding='unicode'))
        return calendar_arch

    @route('/cyllo_studio/calendar/save/item', type="json", auth="user",
           csrf=False)
    def save_calendar_item(self, view_id, model, path, position, properties,
                           extra_data):
        view_rec = self.get_studio_view(view_id, model, 'calendar')
        not_present_fields = self.create_invisible(
            [{**properties, **extra_data}])
        calendar_arch = f'''
          <xpath expr="/{path}" position="{position}">
                <field '''
        for name, value in properties.items():
            if name == 'invisible':
                calendar_arch += f"{name}='{escape(value)}' "
            else:
                calendar_arch += f"{name}='{value}' "
        calendar_arch += f'''/>{not_present_fields}</xpath>'''
        calendar_node = etree.fromstring(view_rec.arch_base)
        calendar_node.append(etree.fromstring(calendar_arch))
        view_rec.arch_base = (etree.tostring(calendar_node, pretty_print=True,
                                             encoding='unicode'))
        return calendar_arch

    @route('/cyllo_studio/calendar/remove/item', type="json", auth="user",
           csrf=False)
    def remove_calendar_item(self, view_id, model, path):
        view_rec = self.get_studio_view(view_id, model, 'calendar')
        calendar_arch = f'''
                   <xpath expr="/{path}" position="replace"/>
                   '''
        calendar_node = etree.fromstring(view_rec.arch_base)
        calendar_node.append(etree.fromstring(calendar_arch))
        view_rec.arch_base = (etree.tostring(calendar_node, pretty_print=True,
                                             encoding='unicode'))
        return calendar_arch

    @route('/cyllo_studio/calendar/move/item', type="json", auth="user",
           csrf=False)
    def move_calendar_item(self, view_id, model, path, position, sibling_path):
        view_rec = self.get_studio_view(view_id, model, 'calendar')
        calendar_arch = f'''
               <xpath expr="/{sibling_path}" position="{position}">
                   <xpath expr="/{path}" position="move"/>
               </xpath>'''
        calendar_node = etree.fromstring(view_rec.arch_base)
        calendar_node.append(etree.fromstring(calendar_arch))
        view_rec.arch_base = (etree.tostring(calendar_node, pretty_print=True,
                                             encoding='unicode'))
        return calendar_arch

    @route('/cyllo_studio/calendar/update/attributes', type='json', auth="user", csrf=False)
    def update_calendar_attributes(self, name, value, view_id, model):
        if name == 'quick_create_view_id':
            calendar_arch = f'''
                        <xpath expr="//calendar" position="attributes">
                            <attribute name='quick_create'>true</attribute>
                            <attribute name='{name}'>{value}</attribute>
                        </xpath>
                        '''
        else:
            calendar_arch = f'''
                <xpath expr="//calendar" position="attributes">
                    <attribute name='{name}'>{value}</attribute>
                </xpath>
                '''
        view_rec = self.get_studio_view(view_id, model, 'calendar')
        calendar_node = etree.fromstring(view_rec.arch_base)
        calendar_node.append(etree.fromstring(calendar_arch))
        view_rec.arch_base = etree.tostring(calendar_node, pretty_print=True, encoding='unicode')
        return calendar_arch

    # -----------------------------------------Activity View----------------------------------------------------

    @route('/cyllo_studio/add/activity/field', type="json", auth="user",
           csrf=False)
    def add_activity_field(self, view_id, view_type, model, path, name):
        view_rec = self.get_studio_view(view_id, model, view_type)
        activity_node = etree.fromstring(view_rec.arch_base)
        activity_arch = f'''
            <xpath expr="{path}" position="inside">
                <field name="{name}" display="full"/>
            </xpath>'''
        activity_node.append(etree.fromstring(activity_arch))
        activity_arch_class = f'''
             <xpath expr="//div[@t-name='activity-box']" position="attributes">
                <attribute name="class">d-block</attribute>
            </xpath>'''
        activity_node.append(etree.fromstring(activity_arch_class))
        view_rec.arch_base = etree.tostring(activity_node, pretty_print=True, encoding='unicode')
        activity_arch += activity_arch_class
        return activity_arch

    @route('/cyllo_studio/form/add/activity_view', type="json", auth="user", csrf=False)
    def add_activity_view(self, arch, model):
        model_id = request.env['ir.model']._get_id(model)
        activity = etree.fromstring(arch)

        def remove_custom_attributes(element):
            # List of attributes to remove
            attributes_to_remove = ['cy-xpath']

            # Iterate through the attributes and remove if present
            for attr in attributes_to_remove:
                if attr in element.attrib:
                    del element.attrib[attr]

            # Recursively call the function for each child element
            for child in element:
                remove_custom_attributes(child)

        remove_custom_attributes(activity)

        arch = etree.tostring(activity, pretty_print=True).decode('utf-8')
        activity_view = request.env['ir.ui.view'].create({
            'name': f"Cy_Studio_activity_{model.replace('.', '_')}_{str(uuid.uuid4())[:8]}",
            'type': 'activity',
            'model': model,
            'model_id': model_id,
            'arch': arch,
        })

        request.env['ir.model.data']._update_xmlids([{
            'xml_id': f"cy_studio.{model.replace('.', '_')}_activity_view_{str(uuid.uuid4())[:8]}",
            'record': activity_view,
        }])

    @route('/cyllo_studio/activity/move/field', type="json", auth="user",
           csrf=False)
    def move_activity_field(self, view_id, model, path, position, sibling_path, parent):

        view_rec = self.get_studio_view(view_id, model, 'activity')
        activity_arch = ''
        if sibling_path:
            activity_arch += f'''
                   <xpath expr="/{sibling_path}" position="{position}">
                           <xpath expr="/{path}" position="move"/>
                       </xpath>'''
        else:
            activity_arch += f'''
                                   <xpath expr="/{parent}" position="inside">
                       <xpath expr="/{path}" position="move"/>
                   </xpath>'''
        activity_node = etree.fromstring(view_rec.arch_base)
        activity_node.append(etree.fromstring(activity_arch))
        view_rec.arch_base = (etree.tostring(activity_node, pretty_print=True, encoding='unicode'))
        return activity_arch

    @route('/cyllo_studio/activity/save/field', type="json", auth="user",
           csrf=False)
    def save_activity_field(self, view_id, model, path, fieldDisplay, fieldBold, fieldMuted):
        view_rec = self.get_studio_view(view_id, model, 'activity')
        view_arch = f'''
                           <xpath expr="/{path}" position="attributes">
                                   <attribute name='display'>{fieldDisplay}</attribute>
                                   <attribute name='bold'>{fieldBold}</attribute>
                                   <attribute name='muted'>{fieldMuted}</attribute>
                           </xpath>
                       '''
        view_node = etree.fromstring(view_rec.arch_base)
        view_node.append(etree.fromstring(view_arch))
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        return view_arch

    @route('/cyllo_studio/add_remove/chatter', type="json", auth="user",
           csrf=False)
    def add_remove_chatter(self, model, view_id, path, view_type, position):
        # FIXME: issue on adding new chatter in base model that does not have one
        form_arch_base = f'<xpath expr="/{path}" position="{position}">'

        if position == 'inside':
            model_id = request.env['ir.model']._get_id(model)
            model_rec = request.env['ir.model'].browse(model_id)

            if model_rec.is_mail_thread:
                form_arch_base += '''<div class="oe_chatter">
                                           <field name="message_follower_ids"/>
                                           <field name="message_ids"/>'''
            if model_rec.is_mail_activity:
                form_arch_base += '<field name="activity_ids"/>'
            form_arch_base += "</div>"
        form_arch_base += '</xpath>'

        view_rec = self.get_studio_view(view_id, model, view_type)
        form_node = etree.fromstring(view_rec.arch_base)
        form_node.append(etree.fromstring(form_arch_base))
        view_rec.arch_base = etree.tostring(form_node, pretty_print=True, encoding='unicode')
        return form_arch_base


    @route('/cyllo_studio/activity/remove/field', type="json", auth="user",
           csrf=False)
    def remove_activity_field(self, view_id, model, path, field_name):
        view_rec = self.get_studio_view(view_id, model, 'activity')
        activity_node = etree.fromstring(view_rec.arch_base)

        activity_arch = f'''
                       <xpath expr="/{path}" position="replace"/>
                       '''
        activity_node.append(etree.fromstring(activity_arch))
        activity_arch_2 = ''
        if field_name:
            activity_arch_2 = f'''
                                      <xpath expr="//templates" position="before">
                                           <field name="{field_name}"/>
                                      </xpath>
                                      '''
            activity_node.append(etree.fromstring(activity_arch_2))
        combined_arch = activity_arch + activity_arch_2
        view_rec.arch_base = (etree.tostring(activity_node, pretty_print=True, encoding='unicode'))

    #-----------------------------------------Undo Redo----------------------------------------------------

    @route('/cyllo_studio/redo_action', type="json", auth="user", csrf=False)
    def redo_action(self, model, view_id, view_type, arch):
        view_rec = self.get_studio_view(view_id, model, view_type)
        xpath_count = arch.count("<xpath")
        xpath_close_count = arch.count('</xpath>') or arch.count("/>")
        view_node = etree.fromstring(view_rec.arch_base)
        if arch.count('</xpath>') == 2 or arch.count('/>') == 2:
            split_string = arch.split("<xpath")
            xpath1 = "<xpath " + split_string[1].strip()
            xpath2 = "<xpath " + split_string[2].strip()
            view_node.append(etree.fromstring(xpath1))
            view_node.append(etree.fromstring(xpath2))
        else:
            view_node.append(etree.fromstring(arch))
        view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))

    @route('/cyllo_studio/undo_action', type="json", auth="user", csrf=False)
    def undo_action(self, model, view_id, view_type, xPaths):
        view_rec = self.get_studio_view(view_id, model, view_type)
        root = etree.fromstring(view_rec.arch)
        xpath_elements = root.findall(".//xpath")
        if xpath_elements:
            element_to_remove = xpath_elements[-1]
            if xPaths:
                element_to_remove_second = xpath_elements[-2]
                parent = element_to_remove_second.getparent()
                if parent is not None:
                    if element_to_remove in parent:
                        parent.remove(element_to_remove)
                    if element_to_remove_second in parent:
                        parent.remove(element_to_remove_second)
                    element = etree.tostring(parent, pretty_print=True).decode("utf-8")
                    if not element.startswith("<data>"):
                        grandparent = parent.getparent()
                        if grandparent is not None:
                            grandparent.remove(parent)
            else:
                parent = element_to_remove.getparent()
                if parent is not None:
                    parent.remove(element_to_remove)
                    element = etree.tostring(parent, pretty_print=True).decode("utf-8")
                    if not element.startswith("<data>"):
                        grandparent = parent.getparent()
                        if grandparent is not None:
                            grandparent.remove(parent)
            view_rec.arch_base = (etree.tostring(root, pretty_print=True, encoding='unicode'))
        #     ------------------------ menu bar --------------------------

    @route('/cyllo_studio/move/menuitem', auth="user", csrf=False, type='json')
    def move_menu(self, args, kwargs):
        """qwerty"""
        print("demo")
        print("demoo", kwargs['MenuPosition'])
        for key, value in kwargs['MenuPosition'].items():
            menu_value = request.env['ir.ui.menu'].browse(int(value))
            menu_value.sequence = int(key)
            print("demooooo", menu_value)
            print("demooooooo", menu_value.sequence)
            menu_item_data = request.env['ir.model.data'].sudo().search([
                ('res_id', 'in', menu_value.ids),
                ('model', '=', 'ir.ui.menu')
            ])
            menu_item_data.noupdate = True
            print("demoooooooo", menu_item_data)

    @route('/cyllo_studio/move/childmenuitem', auth="user", csrf=False, type='json')
    def move_child_menu(self, args, kwargs):
        """qwerty"""
        print("childmenu-menu", kwargs)
        menu = request.env['ir.ui.menu'].browse(int(kwargs['Menu']['id']))
        menu.name = kwargs['MenuName']
        print("qweasdfcdw",menu)
        print("qweasdfcdw",menu.name)
        # if kwargs['ParentChange'] == False:
        #     menu = request.env['ir.ui.menu'].browse(int(kwargs['Menu']['id']))
        if kwargs['ParentMenu']['id'] and kwargs.get('isCreate'):
            menu.parent_id = int(kwargs['ParentMenu']['id'])
        if kwargs['groups'] or kwargs['groups'] == []:
            menu = request.env['ir.ui.menu'].browse(int(kwargs['Menu']['id']))
            if kwargs['groups'] == []:
                menu.groups_id = [Command.clear()]
            else:
                menu.groups_id = kwargs['groups']
        if kwargs['ActionType']:
            menu = request.env['ir.ui.menu'].browse(int(kwargs['Menu']['id']))
            menu.action = f'{kwargs["ActionType"]},%d' % kwargs['ActionModel']
        menu = request.env['ir.ui.menu'].browse(int(kwargs['Menu']['id']))
        menu.active = kwargs['ActiveMenu']

        for key, value in kwargs['MenuPosition'].items():
            menu_value = request.env['ir.ui.menu'].browse(int(value))
            menu_value.sequence = int(key)
            menu_item_data = request.env['ir.model.data'].sudo().search([
                ('res_id', 'in', menu_value.ids),
                ('model', '=', 'ir.ui.menu')
            ])
            menu_item_data.noupdate = True

    @route('/cyllo_studio/menuitem/confirm', auth="user", csrf=False, type='json')
    def menu_confirm(self, args, kwargs):
        print("1234rqasxxfe",kwargs)
        if kwargs['resId']:
            print('if case')
            model = request.env['ir.model'].browse(kwargs['resId'])
            model_action = request.env['ir.actions.act_window'].create({
                'name': kwargs['menuName'],
                'res_model': model.model,
                'view_mode': 'kanban,tree,form',
                'target': 'current'
            })
            menu_item = request.env['ir.ui.menu'].create({
                'name': kwargs['menuName'],
                'action': f"{model_action.type}, {model_action.id}",
                'parent_id': kwargs['ParentMenu'],
                'groups_id': kwargs['groups'] if kwargs['groups'] else None,
                'sequence': 110,
            })
        elif kwargs['model_name'] or kwargs['description']:
            ir_model = request.env['ir.model'].create({
                'name': kwargs['model_name'],
                'model': 'x_cyllo_' + '_'.join(kwargs['model_name'].lower().split(' ')),
                'field_id': [
                    Command.create({'name': 'x_cyllo_name', 'ttype': 'char',
                                    'field_description': kwargs['description']}),
                ]
            })
            model_action = request.env['ir.actions.act_window'].create({
                'name': kwargs['menuName'],
                'res_model': ir_model.model,
                'view_mode': 'kanban,tree,form',
                'target': 'current'
            })
            ir_model_access_user = request.env['ir.model.access'].create({
                'name': "user_access_" + '_'.join(kwargs['menuName'].lower().split(' ')),
                'model_id': ir_model.id,
                'group_id': request.env.ref('base.group_user').id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': False,
            })
            ir_model_access_administrator = request.env['ir.model.access'].create({
                'name': "admin_access_" + '_'.join(kwargs['menuName'].lower().split(' ')),
                'model_id': ir_model.id,
                'group_id': request.env.ref('base.group_system').id,
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            })
            form_view = request.env['ir.ui.view'].create({
                'name': 'Default_Form_' + '_'.join(kwargs['menuName'].lower().split(' ')),
                'type': 'form',
                'model': ir_model.model,
                'model_id': ir_model.id,
                'arch': f"""
                                <form>
                                    <header/>
                                    <sheet string="{ir_model.name}"> <div class="oe_title">
                                    <h1> <field name="x_cyllo_name" required="1"
                                    placeholder="Name..."/> </h1> </div> <group></group> </sheet> </form>"""
            })
            list_view = request.env['ir.ui.view'].create({
                'name': 'Default_List_' + '_'.join(kwargs['menuName'].lower().split(' ')),
                'type': 'tree',
                'model': ir_model.model,
                'model_id': ir_model.id,
                'arch': """
                                <tree>
                                    <field name="x_cyllo_name"/>
                                </tree>
                            """
            })
            search_view = request.env['ir.ui.view'].create({
                'name': 'Default_Search_' + '_'.join(kwargs['menuName'].lower().split(' ')),
                'type': 'search',
                'model': ir_model.model,
                'model_id': ir_model.id,
                'arch': """
                                <search>
                                    <field name="x_cyllo_name"/>
                                </search>
                            """
            })
            menu_item = request.env['ir.ui.menu'].create({
                'name': kwargs['menuName'],
                'action': f"{model_action.type}, {model_action.id}",
                'parent_id': kwargs['ParentMenu'],
                'groups_id': kwargs['groups'] if kwargs['groups'] else None,
                'sequence': 110,
                'web_icon': "",
                'web_icon_data': "",
            })
            if kwargs['IconImage'].startswith('ri'):
                menu_item.web_icon = kwargs['IconImage']
            elif kwargs['IconImage']:
                menu_item.web_icon_data = kwargs['IconImage'].split(',')[1]
        elif kwargs['isParent']:
            menu_item = request.env['ir.ui.menu'].create({
                'name': kwargs['menuName'],
                'action': 'ir.actions.client,%d' % 148,
                'parent_id': kwargs['ParentMenu'],
                'groups_id': kwargs['groups'] if kwargs['groups'] else None,
                'sequence': 110,
                'is_studio': True,
                'web_icon': "",
                'web_icon_data': "",
            })
            if kwargs['IconImage'].startswith('ri'):
                menu_item.web_icon = kwargs['IconImage']
            elif kwargs['IconImage']:
                menu_item.web_icon_data = kwargs['IconImage'].split(',')[1]
        else:
            print("iselsecase", kwargs['ParentMenu'])
            menu_item = request.env['ir.ui.menu'].create({
                'name': kwargs['menuName'] if kwargs['menuName'] else None,
                'active': kwargs['ActiveMenu'],
                'action': f'{kwargs["ActionType"]},%d' % kwargs['ActionModel'] if kwargs['ActionType'] else None,
                'parent_id': kwargs['ParentMenu'] if kwargs['ParentMenu'] else None,
                'groups_id': kwargs['groups'] if kwargs['groups'] else None,
                'sequence': 999,
                'is_studio': True,
                'web_icon': "",
                'web_icon_data': "",
            })
            print("sfvcswdc",menu_item, menu_item.parent_id, menu_item.parent_id.name)
            if kwargs['IconImage'].startswith('ri'):
                menu_item.web_icon = kwargs['IconImage']
            elif kwargs['IconImage']:
                menu_item.web_icon_data = kwargs['IconImage'].split(',')[1]
        request.env['ir.model.data'].create({
            'name': f"menus_{kwargs['menuName'].replace(' ', '_')}_{str(uuid.uuid4())[:8]}",
            'model': 'ir.ui.menu',
            'module': 'base',
            'noupdate': 'True',
            'res_id': menu_item.id,
        })
    #-----------------------------------------New App----------------------------------------------------
    @route('/cyllo_studio/create_app/existing_model', type="json", auth="user",
           csrf=False)
    def create_app_existing_model(self, args, kwargs):

        module_id = kwargs['state'].get('module_id')
        position = kwargs['state'].get('position')

        sequence = self.set_app_sequence(module_id, position)

        model = request.env['ir.model'].browse(kwargs['model_id'])
        View = request.env['ir.ui.view'].sudo()
        views = []
        view_types = [kwargs['set_default_view']]
        editable = False
        for view_type in kwargs['default_views'].values():
            if view_type not in view_types:
                view_types.append(view_type)

        if 'kanban' in view_types and len(view_types) == 1:
            view_types.append('form')

        if (len(view_types) == 1 and view_types[0] == 'tree') \
                or (len(view_types) == 2 and 'tree' in view_types and 'kanban' in view_types):
            editable = True

        for view_mode in view_types:
            view_arch = View.search([('model', '=', model.model), ('type', '=', view_mode), ('inherit_id', '=', False)],
                                    order="id", limit=1)['arch']
            if view_arch:
                if view_mode == 'tree':
                    view_node = etree.fromstring(view_arch)
                    view_editable = view_node.get('editable')
                    if editable and view_editable not in ['top', 'bottom']:
                        view_node.set('editable', 'top')
                    elif view_editable in ['top', 'bottom']:
                        del view_node.attrib['editable']
                    view_arch = etree.tostring(view_node, pretty_print=True, encoding='unicode')

                new_view = request.env['ir.ui.view'].create({
                    'name': f'{view_mode}_' + '_'.join(model.name.lower().split(' ')),
                    'type': view_mode,
                    'model': model.model,
                    'model_id': model.id,
                    'arch': view_arch,
                    'priority': 999
                })
                views.append({'id': new_view.id, 'view_mode': new_view.type})

        menu_action = request.env['ir.actions.act_window'].create({
            'name': model.name,
            'res_model': model.model,
            'view_mode': ','.join(view_types),
            'view_ids': [Command.create({'view_id': view['id'], 'view_mode': view['view_mode']})
                         for view in views]
        })

        menu_item = request.env['ir.ui.menu'].create({
            'name': kwargs['appname'],
            'action': 'ir.actions.act_window,%d' % menu_action.id,
            'web_icon_data': "",
            'web_icon': "",
            'sequence': sequence,
            'is_studio': True,
        })
        if kwargs['state']['group_ids']:
            menu_item.groups_id = kwargs['state']['group_ids']
        if kwargs['IconImage'].startswith('ri'):
            menu_item.web_icon = kwargs['IconImage']
        elif kwargs['IconImage']:
            menu_item.web_icon_data = kwargs['IconImage'].split(',')[1]

        return menu_action.id, menu_item.id, model.model, views, model.id, model.name

    @route('/cyllo_studio/create_app/new_model', auth="user", csrf=False, type='json')
    def create_app_new_model(self, args, kwargs):
        module_id = kwargs['state'].get('module_id')
        position = kwargs['state'].get('position')

        sequence = self.set_app_sequence(module_id, position)

        model_id = request.env['ir.model'].create({
            'name': kwargs['description'],
            'model': 'x_cyllo_' + '_'.join(kwargs['model'].lower().split(' ')),
        })
        View = request.env['ir.ui.view'].sudo()
        views = []
        view_types = [kwargs['set_default_view']]
        editable = False
        for view_type in kwargs['default_view'].values():
            if view_type not in view_types:
                view_types.append(view_type)

        if 'kanban' in view_types and len(view_types) == 1:
            view_types.append('form')

        if (len(view_types) == 1 and view_types[0] == 'tree') \
                or (len(view_types) == 2 and 'tree' in view_types and 'kanban' in view_types):
            editable = True

        for view_mode in view_types:
            view_arch = self.get_default_view_template(view_mode, editable)
            new_view = request.env['ir.ui.view'].create({
                'name': f'{view_mode}_' + '_'.join(model_id.name.lower().split(' ')),
                'type': view_mode,
                'model': model_id.model,
                'model_id': model_id.id,
                'arch': view_arch,
                'priority': 999
            })
            views.append({'id': new_view.id, 'view_mode': new_view.type})

        menu_action = request.env['ir.actions.act_window'].create({
            'name': model_id.name,
            'res_model': model_id.model,
            'view_mode': ','.join(view_types),
            'view_ids': [Command.create({'view_id': view['id'], 'view_mode': view['view_mode']})
                         for view in views]
        })

        menu_item = request.env['ir.ui.menu'].create({
            'name': kwargs['appname'],
            'web_icon_data': "",
            'web_icon': "",
            'sequence': sequence,
            'is_studio': True,
        })

        child_menu_item = request.env['ir.ui.menu'].create({
            'name': kwargs['appname'],
            'parent_id': menu_item.id,
            'action': 'ir.actions.act_window,%d' % menu_action.id,
            'web_icon_data': "",
            'web_icon': "",
            'sequence': sequence,
            'is_studio': True,
        })

        if kwargs['GroupId']:
            menu_item.groups_id = kwargs['GroupId']
        if kwargs['IconImage'].startswith('ri'):
            menu_item.web_icon = kwargs['IconImage']
        elif kwargs['IconImage']:
            menu_item.web_icon_data = kwargs['IconImage'].split(',')[1]

        request.env['ir.model.access'].create({
            'name': "user_access_" + '_'.join(model_id.model.lower().split(' ')),
            'model_id': model_id.id,
            'group_id': request.env.ref('base.group_user').id,
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': True,
        })

        request.env['ir.model.access'].create({
            'name': "admin_access_" + '_'.join(model_id.model.lower().split(' ')),
            'model_id': model_id.id,
            'group_id': request.env.ref('base.group_system').id,
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': True,
        })

        active_field = request.env['ir.model.fields'].create({
            'name': "x_active",
            'field_description': "Active Field",
            'ttype': 'boolean',
            'model_id': model_id.id,
        })

        request.env['ir.default'].create({
            'field_id': active_field.id,
            'json_value': json.dumps(True)
        })
        return (
            menu_action.id, model_id.model, model_id.id, menu_action, menu_item.read(['id', 'name', 'action']),
            menu_item.id, model_id.name, menu_action.id)

    @route('/cyllo_studio/parentmenuitem', auth="user", csrf=False, type='json')
    def parent_menu(self, args, kwargs):
        print("entered the function")
        # parentmenu = request.env['ir.ui.menu'].browse(int(kwargs['ParentMenu']['id']))
        # parentmenu.is_studio = True
        # parentmenu.name = kwargs['MenuName']
        # if kwargs['groups'] or kwargs['groups'] == []:
        #     if kwargs['groups'] == []:
        #         parentmenu.groups_id = [Command.clear()]
        #     else:
        #         parentmenu.groups_id = kwargs['groups']
        # if kwargs.get('IconImage') and kwargs['IconImage'].startswith('ri'):
        #     parentmenu.web_icon = kwargs['IconImage']
        #     parentmenu.web_icon_data = ''
        # elif kwargs.get('IconImage'):
        #     parentmenu.web_icon = ''
        #     parentmenu.web_icon_data = kwargs['IconImage'].split(',')[1] if ',' in kwargs['IconImage'] else kwargs[
        #         'IconImage']
        # parentmenu.active = kwargs['ActiveMenu']

        # # ----------------------------------------search view -------------------------------------------------------4
        #
        # @route('/cyllo_studio/search/add/search_view', type="json", auth="user",
        #        csrf=False)
        # def add_search_view(self, arch, model):
        #     arch_element = etree.fromstring(arch)
        #     model_id = request.env['ir.model']._get_id(model)
        #
        #     def remove_element(element):
        #         if 'cy-xpath' in element.attrib:
        #             del element.attrib['cy-xpath']
        #             for child in element:
        #                 if child.tag == 'studio':
        #                     element.remove(child)
        #                 else:
        #                     remove_element(child)
        #         else:
        #             print("no")
        #
        #     remove_element(arch_element)
        #     main_arch = etree.tostring(arch_element, pretty_print=True).decode('utf-8')
        #     search_rec = request.env['ir.ui.view'].create({
        #         'name': f"Cy_Studio_Search_{model.replace('.', '_')}_{str(uuid.uuid4())[:8]}",
        #         'type': 'search',
        #         'model': model,
        #         'model_id': model_id,
        #         'arch': main_arch,
        #     })
        #     return search_rec
        #
        # @route('/cyllo_studio/add/search_field', type="json", auth="user",
        #        csrf=False)
        # def test_search(self, path, view_id, model, properties):
        #     print(1234567890)
        #     print("kwargs")
        #     print(path)
        #     print(view_id)
        #     print(model)
        #     print(properties)
        #     position = 'inside' if path == '/search' else 'after'
        #     arch = f"""<xpath expr = '{path}' position='{position}'>
        #         <field name = '{properties.get('field')}' string='{properties.get('string')}' """
        #
        #     view_rec = self.get_studio_view(view_id, model, 'search')
        #     print("view_rec")
        #     print(view_rec)
        #     view_node = etree.fromstring(view_rec.arch_base)
        #     view_node.append(etree.fromstring(arch))
        #     view_rec.arch_base = (etree.tostring(view_node, pretty_print=True, encoding='unicode'))
        #     print("ssss", view_arch)
        #     return view_arch
        #
        # # ----------------------------------------------------------------------------------------------------
