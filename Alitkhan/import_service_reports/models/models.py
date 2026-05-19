# -*- coding: utf-8 -*-

from odoo import models, fields, api
import os, csv, json
from datetime import datetime

class ResPartner(models.Model):
    _inherit = "res.partner"

    

    def do_it(self):
        files = os.listdir("/usr/lib/python3/dist-packages/odoo/c-addons/import_service_reports/data")
        for temp_file in files:
            with open('/usr/lib/python3/dist-packages/odoo/c-addons/import_service_reports/data/' + temp_file , 'r', encoding="utf8", errors='ignore') as infile:
                data = csv.DictReader(infile, delimiter=";")
                table=[]

                for line in data:
                    vals={}
                    vals.update(
                        {
                            "task_number":line["Task No "],
                            "t_type":line["Task Type"],
                            "modality":self.search_for_script("name",line["Modality"],module="contract.modality"),
                            # "travel_from":self.search_for_script("name",line["Traviling from "],module="contract.province"),
                            # "travel_to":self.search_for_script("name",line["Traviling from "],module="contract.province"),
                            # "travel_distance":line["KM"],
                            "in_out":line["internal / out"],
                            "date":datetime.strptime(line["Date of Task"], "%d\\%m\\%Y").strftime("%Y-%m-%d") if line["Date of Task"] !="" else False,
                            "engineer":self.search_for_script("name",line["Eng. Name"],module="res.partner"),
                            "car":line["Car"],
                            "site":self.search_for_script("site_name",line["Site"],module="contract.site"),
                            "province":self.search_for_script("name",line["Province"],module="contract.province"),
                            "unit":line["Unit"],
                            "type_unit":line["Type Unit"],
                            "sn":line["SN"],
                            "contract":self.search_for_script("number",line["Contract #"],module="contract.contract"),
                            "desc":line["Task Description "],
                            "done_desc":line["Work Done"],
                            "spare":line["Spear used"],
                            "task_complete":self.sort_task_complete(line["Task Complete"]),
                            "state":line["State"],
                            # "hours_from":line["Working hours from"],
                            # "hours_to":line["Working hours to"],
                            "resource":line["Resoures list"],
                            "service_report_time_lines":[(0, 0, {"date":datetime.strptime(line["Date of Task"], "%d\\%m\\%Y").strftime("%Y-%m-%d") if line["Date of Task"] !="" else False,
                            "time_from":line["Working hours from"],
                            "time_to":line["Working hours to"],
                            "distance":line["KM"]})]

                        }
                    )
                    if line["Traviling from "] != "":
                        if "-" in line["Traviling from "]:
                            vals.update({
                                "travel_from":self.search_for_script("name",line["Traviling from "].split("-")[0].strip(),module="contract.province"),
                                "travel_to":self.search_for_script("name",line["Traviling from "].split("-")[1].strip(),module="contract.province")
                            })
                        else:
                            vals.update({
                                "travel_from":self.search_for_script("name",line["Traviling from "],module="contract.province"),
                                "travel_to":False
                            })
                    else:
                        vals.update({
                                "travel_from":False,
                                "travel_to":False
                            })


                
                    table.append(vals)
        for item in table: 
            self.env["service.report"].create(item)
                            
    def sort_task_complete(self,value):
        yes = ["Yes","yes","YES"]
        no=["No","NO","no"]
        if value == "":
            return False
        if value in yes:
            return "Yes"
        if value in no:
            return "No"


    def search_for_script(self,field,value,module=""):
        if value !="":
            res = self.env[module].search([(field,"=",value)])
            if res:
                if len(res) > 1 :
                    return res[0].id
                else:
                    return res.id
            else:
                if module == "contract.contract":
                    res=self.env[module].create({field:value,"iq":"NO IQ","partner_id":1,"contract_signed_by":1,"signed_date":datetime.today()})
                    return res.id
                else:
                    res = self.env[module].create({field:value})
                    return res.id

        else:
            return False



