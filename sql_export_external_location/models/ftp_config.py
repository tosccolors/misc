# -*- coding: utf-8 -*-

import datetime, ftputil, logging
from lxml import etree
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class FTPConfig(models.Model):
    _name = 'ftp.config'
    _description = 'Connection info of FTP Transfers'



    server = fields.Char(string='Server', help="Servername, including protocol, e.g. https://prod.barneveldsekrant.nl")
    directory = fields.Char(string='Server subdir', help="Directory starting with slash, e.g. /api/v1, or empty")
    tempdir = fields.Char(string='Local temp dir', help="Local temporary directory. e.g. /home/odoo")
    user = fields.Char(string='User')
    password = fields.Char(string='Password')
    # days = fields.Integer(string='History in days')
    # pretty_print = fields.Boolean(string='Pretty print XML')
    # use_sql = fields.Boolean(string='Use SQL')

    latest_run = fields.Char(string='Latest run', help="Date of latest run of Announcement connector")
    latest_status = fields.Char(string='Latest status', help="Log of latest run")

    # end = fields.Date(string='End', help="End date of date range in format yyyy-mm-dd")



    # show only first record to configure, no options to create an additional one
    @api.multi
    def default_view(self):
        configurations = self.search([])
        if not configurations:
            server = "bdu.nl"
            self.write({'server': server})
            configuration = self.id
            _logger.info("configuration created")
        else:
            configuration = configurations[0].id
        action = {
            "type": "ir.actions.act_window",
            "res_model": "ftp.config",
            "view_type": "form",
            "view_mode": "form",
            "res_id": configuration,
            "target": "inline",
        }
        return action


    @api.multi
    def save_config(self):
        self.write({})
        return True


    def log_exception(self, msg, final_msg):
        config = self[0]
        _logger.exception(final_msg)
        config.latest_run = datetime.datetime.utcnow().strftime('UTC %Y-%m-%d %H:%M:%S ')
        config.latest_status = msg + final_msg
        config.write({})
        return

    def ship_xml_file(self, msg, xml, filename):
        config = self[0]

        f = open(config.tempdir + "/" + filename, "w")
        f.write(xml)
        # if self.use_sql:
        #     f.write(xml)
        # else:
        #     data = etree.tostring(xml, pretty_print=self.pretty_print)
        #     f.write(data)
        f.close
        f = None  # to force releasing the file handle

        # Initiate File Transfer Connection
        try:
            port_session_factory = ftputil.session.session_factory(port=21, use_passive_mode=True)
            ftp = ftputil.FTPHost(config.server, config.user, config.password, session_factory=port_session_factory)
        except Exception, e:
            self.log_exception(msg, "Invalid FTP configuration")
            return False

        try:
            _logger.info("Transfering " + filename)
            if config.directory:
                target = str(config.directory) + '/' + filename
            else:
                target = '/' + filename
            source = config.tempdir + '/' + filename
            ftp.upload(source, target)
        except Exception, e:
            self.log_exception(msg, "Transfer failed, quiting....")
            return False

        ftp.close()

        return True



    @api.multi
    def automated_run(self):
        configurations = self.search([])
        if not configurations:
            # cannot use local method because there is no record
            _logger.exception(msg, "Cannot start automated_run. Need a valid configuration")
            return False
        else:
            # start with previous end
            self = configurations[0]
            # self.end = datetime.date.today()
            self.write({})
            return self.do_send()



    @api.multi
    def do_send(self):
        cursor = self._cr
        msg = ""
        config = self[0]
        if not config:
            self.log_exception(msg, "No configuration found. <br>Please configure Schuiteman Peacock connector.")
            return False

        # if not config.end:
        #     self.log_exception(msg, "Program not started. <br>Please provide a valid date")
        #     return False

        # if not config.days:
        #     self.log_exception(msg, "Program not started. <br>Please provide a valid period (i.e. history in days)")
        #     return False

        if not config.server or not config.user or not config.password or not config.tempdir:
            self.log_exception(msg,
                               "Program not started. <br>Please provide a valid server/user/password/tempdir configuration")
            return False

        # # calc begin and end date
        # end = datetime.datetime.strptime(config.end, DEFAULT_SERVER_DATE_FORMAT).date()
        # begin = end - datetime.timedelta(days=config.days)

        # # for sql queries
        # period_end = end.strftime('%Y-%m-%d')
        # period_begin = begin.strftime('%Y-%m-%d')
        # # for ORM search_reads
        # end = end.strftime('UTC %Y-%m-%d T23:59:59')
        # begin = begin.strftime('UTC %Y-%m-%d T00:00:00')

        # # --------------- MANUAL QUERY -------------------------
        # query = 'SELECT  query_to_xml(\'SELECT  id, name, create_date, create_uid, write_date, write_uid, \
        #                                                 company_id, code \
        #                                         FROM account_account WHERE deprecated>=$$False$$\',true,false,\'\')'
        # cursor.execute(query)
        # aa = cursor.fetchall()
        # aa_root = aa[0][0]
        #
        # print ("aa query", query)
        # # Transfer files
        # self.ship_xml_file(msg, aa_root, 'account_account.xml')
        # ----- [ENDS]


        sqlExports = self.env['sql.export'].search([('state','=', 'sql_valid')], order='id')

        if not len(sqlExports.ids):
            self.log_exception(msg,
                               "Program not started. <br>Please create a valid record in SQL Export, & ensure it is in 'SQL Valid' state ")
            return False

        for se in sqlExports:
            query = 'SELECT query_to_xml(\'' + str(se.query) + '\',\
                                          true,false,\'\')'

            cursor.execute(query)
            res = cursor.fetchall()
            res = res[0][0]
            filename = str(se.name) + '.xml'
            self.ship_xml_file(msg, res, filename)

        # TODO: ftputil.session



        # report and exit positively
        final_msg = "File transfer Successfull ..."
        _logger.info(final_msg)
        config.latest_run = datetime.datetime.utcnow().strftime('UTC %Y-%m-%d %H:%M:%S ')
        config.latest_status = msg + final_msg
        config.write({})
        return True

    # def add_element(self, node, dict, tag):
    #
    #     new_node = etree.Element(tag)
    #     node.append(new_node)
    #     for key, value in dict.iteritems():
    #         element = etree.Element(key)
    #         new_node.append(element)
    #         if type(value) in [str, int, float]:
    #             element.text = str(value)
    #         elif type(value) == unicode:
    #             element.text = value.encode("ascii", "replace")
    #         elif type(value) == bool:
    #             element.text = str(value)
    #         elif key.endswith('ids'):
    #             n = 0
    #             for v in value:
    #                 sub_node = etree.Element('_' + str(n))
    #                 element.append(sub_node)
    #                 sub_node.text = str(v)
    #                 n += 1
    #         elif type(value) == tuple and type(value[0]) == int and type(value[1]) == unicode:
    #             sub_node = etree.Element('id')
    #             element.append(sub_node)
    #             sub_node.text = str(value[0])
    #             sub_node = etree.Element('name')
    #             element.append(sub_node)
    #             sub_node.text = value[1].encode("ascii", "replace")
    #         elif type(value) == tuple:
    #             n = 0
    #             for v in value:
    #                 sub_node = etree.Element('_' + str(n))
    #                 element.append(sub_node)
    #                 if type(v) == unicode:
    #                     sub_node.text = v.encode("ascii", "replace")
    #                 else:
    #                     sub_node.text = str(v)
    #                 n += 1
    #         else:  # object
    #             self.add_element(element, value, key)
    #     return True