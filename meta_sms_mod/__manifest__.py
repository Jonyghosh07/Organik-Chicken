# -*- coding: utf-8 -*-

{
  "name"                 :  "Notification Via SMS",
  
  "summary"              :  """Notification via SMS.""",
  
  "category"             :  "Tools/Tools",
  "version"              :  "16.0.0.0",
  "sequence"             :  1,
  
  "author"               :  "Metamorphosis Limited, Rifat Anwar",
  "co-author"            :  "Rifat Anwar",
  "license"              :  "AGPL-3",
  "website"              :  "Metamorphosis.com.bd",
  "description"          :  """
  Description will be here
  """,
  "depends"              :  ['base', 'sale','stock'],
  "data"                 :  [
                              'security/ir.model.access.csv',
                              #  'data/so_sms_cron.xml',
                              'data/server_action_gear.xml',
                              'views/res_config_views.xml',
                              'views/sale_order_views.xml',
                              'views/manual_sms_view.xml',
                              'views/res_contact_view.xml'
                            ],
  
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
}