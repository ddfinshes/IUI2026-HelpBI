q = """
%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"""

l = ['2025-02-10', '202545', '2', '202502', '2025', 'UAHONGKONGWFH', '', 'UAHKG02', 'UAHKG02', 'HONG KONG CAUSEWAY BAY SOGO DS', '', 'Hongkong', '', '', 'HONG KONG', 'BH', '', 'BH', 'Y', 'HKD', '305', '2', '22748.4500', '22748.4500000000', '2917.028847', '0.0000', '2917.0288470000', '0.000000', '0.000000', '0.000000', '-2917.028847', '0', '0.000000', '0.000000', '0.000000', '0', '491', '5', '31773.8400000000', '4074.3526650000', '4074.352665', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'FP', 'Y', 'Y', '0.0000', '', 'Y', '2010-01-01', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '0.0000', '0.0000', '0.0000', '0.0000']

p = """
ds_sid,date_sid,store_sid,date_code,store_master_code,store_code,store_name,short_name,channel,store_type,country,region,province,city,address1,address2,address3,latitude,longitude,zip_code,customer_code,customer_name,customer_sort,warehouse_code,warehouse_name,district_manager,pin_code,b1_code,fms_site_code,sit_code,sap_customer_code,area,cluster,open_date,close_date,open_flag,keep_comp,comp_flag,finance_comp,active_flag,source_interface,source_sys,hdetl_date,store_local_name,phone1,phone2,store_no,subchannel"""
print(len(l))
print(len(q.split(', ')))
print(q.split(','))
print(len(p.split(',')))