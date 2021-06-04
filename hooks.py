

def pre_init_hook(cr):
    cr.execute(""" 
        ALTER TABLE resource_resource ADD COLUMN IF NOT EXISTS employee_number VARCHAR, ADD COLUMN IF NOT EXISTS sequence_number VARCHAR;
    """)
    cr.execute(
        """
        UPDATE resource_resource SET employee_number= LPAD(CAST (id AS text), 4, '0') , sequence_number=LPAD(CAST (id AS text), 4, '0') WHERE employee_number IS null OR employee_number='/';
    """)
