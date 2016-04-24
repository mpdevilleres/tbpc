import csv, os

dir = os.path.abspath(os.path.dirname(__file__))
basedir = '/web'
def model_to_csv(model=None, columns=list(), output_file=None):
    if model is None:
        raise Exception('Model is None')

    elif len(columns) == 0 or columns is None:
        raise Exception('Columns list is Empty')

    elif output_file is None:
        raise Exception('Output file not specified')

    output = os.path.join(basedir, 'csv_backup', output_file)
    with open(output, 'w', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        # Headers
        headers = []
        for column in columns:
            headers.append(column.replace('.', '__'))
        writer.writerow(headers)

        # Content
        for record in model.objects.all():
            row_values = []
            for column in columns:
                obj = record
                try:
                    # gets value without nested attribute
                    # obj.attr
                    text = getattr(obj, column)

                except AttributeError:
                    # gets value with nested attribute
                    # obj.attr1.attr2
                    for part in column.split('.'):
                        if obj is None:
                            break
                        obj = getattr(obj, part)
                    text = obj
                # if isinstance(text, int):
                #     text = '%s' % text

                row_values.append(r'%s' % text)

            writer.writerow(row_values)

# def csv_to_model(model=None, csvpath=None):
#     if model is None:
#         raise Exception('Model is None')
#     elif csvpath is None:
#         raise Exception('CSV File is None')
#
#     with open(csvpath, encoding='mac_roman') as csvfile:
#         reader = csv.DictReader(csvfile)
#         print(reader.fieldnames)
#         row = next(reader)
#         for i in row:
#             print(type(i))
#         failed_list = []
#         for row in reader:
#             record = model.objects.filter(invoice_no=row['invoice_no']).first()
#
#             if record is not None:
#                 print('Invoice ID# %sExist' % record.pk)
#                 continue
#
#             task = Task.objects.filter(task_no=row['task_no']).first()
#             if task is None:
#                 task = Task(task_no=row['task_no'])
#                 task.save()
#
#             contract = Contract.objects.filter(pk=row['contract_id']).first()
#             contractor = Contractor.objects.filter(pk=row['contractor_id']).first()
#
#             record = model(task=task, contract=contract, contractor=contractor)
#
#             record.region = row['region']
#             record.invoice_no = row['invoice_no']
#             record.invoice_type = row['invoice_type']
#             #record.revenue_amount = Decimal(['revenue_amount'])
#             record.opex_amount = Decimal(row['opex_amount'])
#             record.capex_amount = Decimal(row['capex_amount'])
#             record.invoice_amount = Decimal(row['invoice_amount'])
#             record.penalty = Decimal(row['penalty'])
#             record.invoice_date = date_format(row['invoice_date'])
#             record.invoice_cert_date = date_format(row['invoice_cert_date'])
#             record.received_date = date_format(row['received_date'])
#             record.signed_date = date_format(row['signed_date'])
#             record.start_date = date_format(row['start_date'])
#             record.end_date = date_format(row['end_date'])
#             record.rfs_date = date_format(row['rfs_date'])
#             record.sent_finance_date = date_format(row['sent_finance_date'])
#             record.cost_center = row['cost_center']
#             record.expense_code = row['expense_code']
#             record.remarks = row['remarks']
#             record.description = row['description']
#             record.proj_no = row['proj_no']
#             record.status = row['status']
#             record.invoice_ref = row['invoice_ref']
#             record.state_id = row['state_id']
#             record.save()
