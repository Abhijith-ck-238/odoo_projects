# -*- coding: utf-8 -*-
from odoo import models, fields


class CustomCrossoveredBudgetLines(models.Model):
    _inherit = 'budget.line'


    amount_to_extend = fields.Float(string="Amount to Extend")
    paid_date = fields.Date("Paid Date")
    # achieved_amount = fields.Monetary(
    #     compute='_compute_all',
    #     string='Achieved',
    #     help="Amount Billed/Invoiced.",
    #     store=True)
    # achieved_percentage = fields.Float(
    #     compute='_compute_all',
    #     string='Achieved (%)',
    #     store=True)
    # committed_amount = fields.Monetary(
    #     compute='_compute_all',
    #     string='Committed',
    #     help="Already Billed amount + Confirmed purchase orders.",
    #     store=True)
    # committed_percentage = fields.Float(
    #     compute='_compute_all',
    #     string='Committed (%)',
    #     store=True)

    # def _compute_all(self):
    #     """Compute with simple batch processing"""
    #     if not self:
    #         return
    #
    #     BATCH_SIZE = 1000
    #
    #     if len(self.ids) > BATCH_SIZE:
    #         print("ABD BEFORE COMPUTE  START:",fields.Datetime.now())
    #         for i in range(0, len(self.ids), BATCH_SIZE):
    #             batch = self.browse(self.ids[i:i + BATCH_SIZE])
    #             batch._compute_all_batch()
    #         print("ABD BEFORE COMPUTE  END:", fields.Datetime.now())
    #     else:
    #         print("ABD BEFORE COMPUTE  END:", fields.Datetime.now())
    #         print("ABD BEFORE COMPUTE  END:", self.env["budget.report"].search_count([]))
    #         print("ABD BEFORE COMPUTE  END:")
    #         self._compute_all_batch()

    # def _compute_budget_report(self):
    #     budget_count = self.env["budget.report"].search_count([])
    #     BATCH_SIZE = 1000
    #     return

    def _compute_all(self):
        """Process a single batch"""
        if not self:
            return
#         self.env.cr.execute("""SELECT CONCAT('bl', bl.id::TEXT) AS id,
#        bl.budget_analytic_id AS budget_analytic_id,
#        bl.id AS budget_line_id,
#        'budget.analytic' AS res_model,
#        bl.budget_analytic_id AS res_id,
#        bl.date_from AS date,
#        ba.name AS description,
#        bl.company_id AS company_id,
#        NULL AS user_id,
#        'budget' AS line_type,
#        bl.budget_amount AS budget,
#        0 AS committed,
#        0 AS achieved,
#        "bl"."account_id", "bl"."x_plan6085_id", "bl"."x_plan6087_id", "bl"."x_plan6089_id",
#        "bl"."x_plan6091_id", "bl"."x_plan6093_id", "bl"."x_plan6095_id", "bl"."x_plan6097_id",
#        "bl"."x_plan6099_id", "bl"."x_plan6101_id", "bl"."x_plan6154_id", "bl"."x_plan6155_id",
#        "bl"."x_plan6156_id", "bl"."x_plan6157_id"
#   FROM budget_line bl
#   JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
#
# UNION ALL
#
# SELECT CONCAT('aal', aal.id::TEXT) AS id,
#        bl.budget_analytic_id AS budget_analytic_id,
#        bl.id AS budget_line_id,
#        'account.analytic.line' AS res_model,
#        aal.id AS res_id,
#        aal.date AS date,
#        aal.name AS description,
#        aal.company_id AS company_id,
#        aal.user_id AS user_id,
#        'achieved' AS line_type,
#        0 AS budget,
#        aal.amount * CASE WHEN ba.budget_type = 'expense' THEN -1 ELSE 1 END AS committed,
#        aal.amount * CASE WHEN ba.budget_type = 'expense' THEN -1 ELSE 1 END AS achieved,
#        "aal"."account_id", "aal"."x_plan6085_id", "aal"."x_plan6087_id", "aal"."x_plan6089_id",
#        "aal"."x_plan6091_id", "aal"."x_plan6093_id", "aal"."x_plan6095_id", "aal"."x_plan6097_id",
#        "aal"."x_plan6099_id", "aal"."x_plan6101_id", "aal"."x_plan6154_id", "aal"."x_plan6155_id",
#        "aal"."x_plan6156_id", "aal"."x_plan6157_id"
#   FROM account_analytic_line aal
#   LEFT JOIN budget_line bl ON aal.company_id = bl.company_id
#                           AND aal.date >= bl.date_from
#                           AND aal.date <= bl.date_to
#                           AND ("bl"."account_id" IS NULL OR "aal"."account_id" = "bl"."account_id")
#                           AND ("bl"."x_plan6085_id" IS NULL OR "aal"."x_plan6085_id" = "bl"."x_plan6085_id")
#                           AND ("bl"."x_plan6087_id" IS NULL OR "aal"."x_plan6087_id" = "bl"."x_plan6087_id")
#                           AND ("bl"."x_plan6089_id" IS NULL OR "aal"."x_plan6089_id" = "bl"."x_plan6089_id")
#                           AND ("bl"."x_plan6091_id" IS NULL OR "aal"."x_plan6091_id" = "bl"."x_plan6091_id")
#                           AND ("bl"."x_plan6093_id" IS NULL OR "aal"."x_plan6093_id" = "bl"."x_plan6093_id")
#                           AND ("bl"."x_plan6095_id" IS NULL OR "aal"."x_plan6095_id" = "bl"."x_plan6095_id")
#                           AND ("bl"."x_plan6097_id" IS NULL OR "aal"."x_plan6097_id" = "bl"."x_plan6097_id")
#                           AND ("bl"."x_plan6099_id" IS NULL OR "aal"."x_plan6099_id" = "bl"."x_plan6099_id")
#                           AND ("bl"."x_plan6101_id" IS NULL OR "aal"."x_plan6101_id" = "bl"."x_plan6101_id")
#                           AND ("bl"."x_plan6154_id" IS NULL OR "aal"."x_plan6154_id" = "bl"."x_plan6154_id")
#                           AND ("bl"."x_plan6155_id" IS NULL OR "aal"."x_plan6155_id" = "bl"."x_plan6155_id")
#                           AND ("bl"."x_plan6156_id" IS NULL OR "aal"."x_plan6156_id" = "bl"."x_plan6156_id")
#                           AND ("bl"."x_plan6157_id" IS NULL OR "aal"."x_plan6157_id" = "bl"."x_plan6157_id")
#   LEFT JOIN account_account aa ON aa.id = aal.general_account_id
#   LEFT JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
#  WHERE CASE
#            WHEN ba.budget_type = 'expense' THEN (
#                SPLIT_PART(aa.account_type, '_', 1) = 'expense'
#                OR (aa.account_type IS NULL AND aal.category NOT IN ('invoice', 'other'))
#                OR (aa.account_type IS NULL AND aal.category = 'other' AND aal.amount < 0)
#            )
#            WHEN ba.budget_type = 'revenue' THEN (
#                SPLIT_PART(aa.account_type, '_', 1) = 'income'
#                OR (aa.account_type IS NULL AND aal.category = 'other' AND aal.amount > 0)
#            )
#            ELSE TRUE
#        END
#    AND (SPLIT_PART(aa.account_type, '_', 1) IN ('income', 'expense') OR aa.account_type IS NULL)
#
# UNION ALL
#
# SELECT (pol.id::TEXT || '-' || ROW_NUMBER() OVER (PARTITION BY pol.id ORDER BY pol.id)) AS id,
#        bl.budget_analytic_id AS budget_analytic_id,
#        bl.id AS budget_line_id,
#        'purchase.order' AS res_model,
#        po.id AS res_id,
#        po.date_order AS date,
#        pol.name AS description,
#        pol.company_id AS company_id,
#        po.user_id AS user_id,
#        'committed' AS line_type,
#        0 AS budget,
#        COALESCE(pol.price_subtotal::FLOAT, pol.price_unit::FLOAT * pol.product_qty)
#             / pol.product_qty
#             * (pol.product_qty - COALESCE(qty_invoiced_table.qty_invoiced, 0))
#             / po.currency_rate
#             * (a.rate) AS committed,
#        0 AS achieved,
#        "a"."account_id", "a"."x_plan6085_id", "a"."x_plan6087_id", "a"."x_plan6089_id",
#        "a"."x_plan6091_id", "a"."x_plan6093_id", "a"."x_plan6095_id", "a"."x_plan6097_id",
#        "a"."x_plan6099_id", "a"."x_plan6101_id", "a"."x_plan6154_id", "a"."x_plan6155_id",
#        "a"."x_plan6156_id", "a"."x_plan6157_id"
#   FROM purchase_order_line pol
#   LEFT JOIN (
#         SELECT SUM(
#                    CASE WHEN COALESCE(uom_aml.id != uom_pol.id, FALSE)
#                         THEN ROUND((aml.quantity / uom_aml.factor) * uom_pol.factor, -LOG(uom_pol.rounding)::integer)
#                         ELSE COALESCE(aml.quantity, 0)
#                    END
#                    * CASE WHEN aml.balance < 0 THEN -1 ELSE 1 END
#                ) AS qty_invoiced,
#                pol.id AS pol_id
#           FROM purchase_order po
#      LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
#      LEFT JOIN account_move_line aml ON aml.purchase_line_id = pol.id
#      LEFT JOIN uom_uom uom_aml ON uom_aml.id = aml.product_uom_id
#      LEFT JOIN uom_uom uom_pol ON uom_pol.id = pol.product_uom
#      LEFT JOIN uom_category uom_category_aml ON uom_category_aml.id = uom_pol.category_id
#      LEFT JOIN uom_category uom_category_pol ON uom_category_pol.id = uom_pol.category_id
#          WHERE aml.parent_state = 'posted'
#       GROUP BY pol.id
#   ) qty_invoiced_table ON qty_invoiced_table.pol_id = pol.id
#        JOIN purchase_order po ON pol.order_id = po.id AND po.state in ('purchase', 'done')
#  CROSS JOIN JSONB_TO_RECORDSET(pol.analytic_json) AS a(
#        rate FLOAT, "account_id" FLOAT, "x_plan6085_id" FLOAT, "x_plan6087_id" FLOAT, "x_plan6089_id" FLOAT,
#        "x_plan6091_id" FLOAT, "x_plan6093_id" FLOAT, "x_plan6095_id" FLOAT, "x_plan6097_id" FLOAT,
#        "x_plan6099_id" FLOAT, "x_plan6101_id" FLOAT, "x_plan6154_id" FLOAT, "x_plan6155_id" FLOAT,
#        "x_plan6156_id" FLOAT, "x_plan6157_id" FLOAT
#  )
#   LEFT JOIN budget_line bl ON po.company_id = bl.company_id
#                           AND po.date_order >= bl.date_from
#                           AND po.date_order <= bl.date_to
#                           AND ("bl"."account_id" IS NULL OR "a"."account_id" = "bl"."account_id")
#                           AND ("bl"."x_plan6085_id" IS NULL OR "a"."x_plan6085_id" = "bl"."x_plan6085_id")
#                           AND ("bl"."x_plan6087_id" IS NULL OR "a"."x_plan6087_id" = "bl"."x_plan6087_id")
#                           AND ("bl"."x_plan6089_id" IS NULL OR "a"."x_plan6089_id" = "bl"."x_plan6089_id")
#                           AND ("bl"."x_plan6091_id" IS NULL OR "a"."x_plan6091_id" = "bl"."x_plan6091_id")
#                           AND ("bl"."x_plan6093_id" IS NULL OR "a"."x_plan6093_id" = "bl"."x_plan6093_id")
#                           AND ("bl"."x_plan6095_id" IS NULL OR "a"."x_plan6095_id" = "bl"."x_plan6095_id")
#                           AND ("bl"."x_plan6097_id" IS NULL OR "a"."x_plan6097_id" = "bl"."x_plan6097_id")
#                           AND ("bl"."x_plan6099_id" IS NULL OR "a"."x_plan6099_id" = "bl"."x_plan6099_id")
#                           AND ("bl"."x_plan6101_id" IS NULL OR "a"."x_plan6101_id" = "bl"."x_plan6101_id")
#                           AND ("bl"."x_plan6154_id" IS NULL OR "a"."x_plan6154_id" = "bl"."x_plan6154_id")
#                           AND ("bl"."x_plan6155_id" IS NULL OR "a"."x_plan6155_id" = "bl"."x_plan6155_id")
#                           AND ("bl"."x_plan6156_id" IS NULL OR "a"."x_plan6156_id" = "bl"."x_plan6156_id")
#                           AND ("bl"."x_plan6157_id" IS NULL OR "a"."x_plan6157_id" = "bl"."x_plan6157_id")
#   LEFT JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
#  WHERE pol.product_qty > COALESCE(qty_invoiced_table.qty_invoiced, 0)
#    AND ba.budget_type != 'revenue';
# """)
#
#         res = self.env.cr.fetchall()
#         print("ABD compute all BQ after : ", fields.Datetime.now())
#         print("ABD compute all B :",len(res))
        budget_querry = self.env['budget.report']._table_query
        self.env.cr.execute(budget_querry)
        budget_report = self.env.cr.dictfetchall()
        budget_data = []
        for row in budget_report:
            bl_id = row['budget_line_id']
            if bl_id in self.ids:
                # if bl_id not in budget_data:
                #     budget_data[bl_id] = {'committed': 0.0, 'achieved': 0.0}
                budget_data += [(bl_id,row['committed'],row['achieved'])]
                # budget_data[bl_id]['committed'] += row['committed']
                # budget_data[bl_id]['achieved'] += row['achieved']
        grouped = {
            line: (committed, achieved)
            for line, committed, achieved in budget_data
        }


        for line in self:
            committed, achieved = grouped.get(line, (0, 0))
            line.committed_amount = committed
            line.achieved_amount = achieved
            line.committed_percentage = line.budget_amount and (line.committed_amount / line.budget_amount) or 0
            line.achieved_percentage = line.budget_amount and (line.achieved_amount / line.budget_amount) or 0