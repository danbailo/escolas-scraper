import xlsxwriter

data = {}

data[0] = "school", "school_name", "telephone", "streetAddress", "neighborhood", "addressLocality", None, "public"
data[1] = "school", "school_name", "telephone", "streetAddress", "neighborhood", "addressLocality", None, "public"
data[2] = "school", "school_name", "telephone", "streetAddress", "neighborhood", "addressLocality", "addressRegion", "public"
data[3] = "school", "school_name", "telephone", "streetAddress", "neighborhood", "addressLocality", None, "public"


def write_sheet():
        workbook = xlsxwriter.Workbook("test.xlsx")
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        values = list(data.values())
        worksheet.write(0, 0, "Estado",bold)
        worksheet.write(0, 1, "Cidade",bold)
        worksheet.write(0, 2, "Bairro",bold)
        worksheet.write(0, 3, "Nome da Instituição",bold)
        worksheet.write(0, 4, "Tipo",bold)
        worksheet.write(0, 5, "Telefone",bold)
        worksheet.write(0, 6, "Email",bold)
        worksheet.write(0, 7, "Endereço",bold)

        for row_number, info in enumerate(values):
            worksheet.write(row_number+1, 0, info[0])
            worksheet.write(row_number+1, 1, info[1])
            worksheet.write(row_number+1, 2, info[2])
            worksheet.write(row_number+1, 3, info[3])
            worksheet.write(row_number+1, 4, info[4])
            worksheet.write(row_number+1, 5, info[5])
            worksheet.write(row_number+1, 6, info[6])
            worksheet.write(row_number+1, 7, info[7])
        workbook.close()

write_sheet()