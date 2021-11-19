from src.db import DB

class CC_DB(DB):
    """
    CreepyCrawler SQLite3 database implementation class
    """

    def db_init(self, db_name):
        """
        Initialise the database, by creating/connecting to it and creating the needed tables 
        if not already existing.
        """
        self._init(db_name=db_name)
        self.tables=self.get_tables()
        self.create_cc_tables()

    def set_target(self, domain, protocol, description='None'):
        cursor=self.select(table_name='targets',
                           column_names=['target_id', 'domain'],
                           where="domain='"+domain +"' AND protocol='"\
                           +protocol+"'")
        update=False
        target_id=0
        for row in cursor:
            if domain in row:
                update=True
                target_id=row[0]

        if update:
            self.update_target(target_id=target_id, domain=domain,
                               protocol=protocol,
                               description=description)
        else:
            self.insert_target(domain=domain,
                               protocol=protocol,
                               description=description)
            

    def insert_target(self, domain, protocol, description='None'):
        self.insert(table_name='targets',
                    column_names=['domain', 'protocol',
                                  'description'],
                    values=["'"+domain+"'", "'"+protocol+"'",
                            "'"+description+"'"])

    def insert_internal_link(self, target:str, protocol:str, url:str, evidence:str,
                             status:int, regex:str, origin:str):
        cursor=self.select(table_name='targets', column_names=['target_id'],
                           where="domain='"+target+"' AND protocol='"+protocol+"'")

        for row in cursor:
            target_id=row[0]
            break

        cursor=self.select(table_name='links_internal',
                           column_names=['link_id', 'status'],
                           where="url='"+url+"' AND target_id="+str(target_id))
        counter=0
        for row in cursor:
            link_id=row[0]
            counter+=1
        if counter:
            self.update(table_name='links_internal',column_name='evidence',value="'"+evidence+"'",
                        where="link_id="+str(link_id))
            self.update(table_name='links_internal',column_name='status',value="'"+str(status)+"'",
                        where="link_id="+str(link_id))
            self.update(table_name='links_internal',column_name='regex',value="'"+regex+"'",
                        where="link_id="+str(link_id))
            self.update(table_name='links_internal',column_name='origin',value="'"+origin+"'",
                        where="link_id="+str(link_id))
        else:
            self.insert(table_name='links_internal',
                        column_names=['url', 'evidence',
                                      'status', 'regex', 'origin',
                                      'target_id'],
                        values=["'"+url+"'", "'"+evidence+"'", str(status), "'"+regex+"'",
                                "'"+origin+"'", str(target_id)])
        
    def insert_external_link(self, target:str, protocol:str, url:str, evidence:str,
                             status:int, regex:str, origin:str):
        cursor=self.select(table_name='targets', column_names=['target_id'],
                           where="domain='"+target+"' AND protocol='"+protocol+"'")

        for row in cursor:
            target_id=row[0]
            break

        cursor=self.select(table_name='links_external',
                           column_names=['link_id', 'status'],
                           where="url='"+url+"' AND target_id="+str(target_id))
        counter=0
        for row in cursor:
            link_id=row[0]
            counter+=1
        if counter:
            self.update(table_name='links_external',column_name='evidence',value="'"+evidence+"'",
                        where="link_id="+str(link_id))
            self.update(table_name='links_external',column_name='status',value="'"+str(status)+"'",
                        where="link_id="+str(link_id))
            self.update(table_name='links_external',column_name='regex',value="'"+regex+"'",
                        where="link_id="+str(link_id))
            self.update(table_name='links_external',column_name='origin',value="'"+origin+"'",
                        where="link_id="+str(link_id))
        else:
            self.insert(table_name='links_external',
                        column_names=['url', 'evidence',
                                      'status', 'regex', 'origin',
                                      'target_id'],
                        values=["'"+url+"'", "'"+evidence+"'", str(status), "'"+regex+"'",
                                "'"+origin+"'", str(target_id)])

    def update_target(self, target_id, domain, protocol, description):
        self.update(table_name='targets',column_name='domain',value="'"+domain+"'",
                    where="target_id="+str(target_id))
        self.update(table_name='targets',column_name='protocol',value="'"+protocol+"'",
                    where="target_id="+str(target_id))
        self.update(table_name='targets',column_name='description',value="'"+description+"'",
                    where="target_id="+str(target_id))

    def create_cc_tables(self):
        self.create_target_table()
        self.create_link_int_table()
        self.create_ext_int_table()
        self.create_subdomains_table()
        self.create_emails_table()
        self.create_ip_table()
        self.create_version_table()

    def create_target_table(self):
        """
        """
        if not('targets' in self.tables):
            self.create_table(table_name='targets',
                              column_names=['target_id', 'domain',
                                            'protocol', 'description'],
                              column_types=['INTEGER', 'char(50)',
                                            'char(50)', 'char(100)'],
                              pk_index=0, notnull=[0])

    def create_link_int_table(self):
        """
        """
        if not('links_internal' in self.tables):
            self.create_table(table_name='links_internal',
                              column_names=['link_id', 'url', 'evidence',
                                            'status', 'regex', 'origin', 'target_id'],
                              column_types=['INTEGER', 'char(400)', 'char(400)',
                                            'INTEGER', 'char(400)', 'char(400)', 'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_ext_int_table(self):
        """
        """
        if not('links_external' in self.tables):
            self.create_table(table_name='links_external',
                              column_names=['link_id', 'url', 'evidence',
                                            'status', 'regex', 'origin', 'target_id'],
                              column_types=['INTEGER', 'char(400)', 'char(400)',
                                            'INTEGER', 'char(400)', 'char(400)', 'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_subdomains_table(self):
        """
        """
        if not('subdomains' in self.tables):
            self.create_table(table_name='subdomains',
                              column_names=['domain_id', 'domain', 'target_id',
                                            'IP', 'evidence','regex'],
                              column_types=['INTEGER', 'char(400)','INTEGER',
                                            'char(30)', 'char(400)', 'char(400)'],
                              pk_index=0, notnull=[0])

    def create_emails_table(self):
        """
        """
        if not('emails' in self.tables):
            self.create_table(table_name='emails',
                              column_names=['email_id', 'email', 'evidence',
                                            'regex', 'target_id'],
                              column_types=['INTEGER', 'char(400)', 'char(400)',
                                            'char(400)', 'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_ip_table(self):
        """
        """
        if not('ip_address' in self.tables):
            self.create_table(table_name='ip_address',
                              column_names=['ip_id', 'ip_address',
                                            'evidence', 'regex', 'target_id'],
                              column_types=['INTEGER', 'char(400)',
                                            'char(400)', 'char(400)', 'INTEGER'],
                              pk_index=0, notnull=[0])

    def create_version_table(self):
        """
        """
        if not('versions' in self.tables):
            self.create_table(table_name='versions',
                              column_names=['version_id', 'version',
                                            'evidence', 'regex', 'target_id'],
                              column_types=['INTEGER', 'char(400)',
                                            'char(400)', 'char(400)', 'INTEGER'],
                              pk_index=0, notnull=[0])

db=CC_DB()
