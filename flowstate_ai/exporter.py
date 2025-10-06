import csv
import json
import io
from fpdf import FPDF

class DataExporter:
    def __init__(self, data):
        """Initialize with data to export. Data should be a list of dictionaries."""
        self.data = data

    def to_csv(self):
        """Export data as CSV format string."""
        if not self.data:
            return ""

        output = io.StringIO()
        fieldnames = self.data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(self.data)
        return output.getvalue()

    def to_json(self):
        """Export data as JSON format string."""
        return json.dumps(self.data, indent=2)

    def to_pdf(self):
        """Export data as PDF byte string."""
        if not self.data:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, "No Data Available", ln=True)
            return pdf.output(dest='S').encode('latin1')

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Calculate column widths
        col_widths = {}
        headers = list(self.data[0].keys())
        for header in headers:
            max_len = len(header)
            for row in self.data:
                max_len = max(max_len, len(str(row.get(header, ''))))
            # Approximate width in points (1 char ~ 3 points)
            col_widths[header] = max_len * 3 + 4

        # Print headers
        for header in headers:
            pdf.cell(col_widths[header], 10, header, border=1)
        pdf.ln()

        # Print rows
        for row in self.data:
            for header in headers:
                text = str(row.get(header, ''))
                pdf.cell(col_widths[header], 10, text, border=1)
            pdf.ln()

        return pdf.output(dest='S').encode('latin1')


if __name__ == "__main__":
    sample_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]

    exporter = DataExporter(sample_data)
    print("CSV Export:\n", exporter.to_csv())
    print("JSON Export:\n", exporter.to_json())

    # Save PDF to file
    with open("sample_export.pdf", "wb") as f:
        f.write(exporter.to_pdf())
    print("PDF exported to sample_export.pdf")
