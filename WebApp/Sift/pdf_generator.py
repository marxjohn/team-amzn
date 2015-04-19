__author__ = 'cse498'

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os


def create_pdf(pdf_lines, cluster_run_id):
    style = getSampleStyleSheet()
    story = []
    filename = str(cluster_run_id) + ".pdf"
    directory = '/pdf'
    cur_dir = os.curdir
    local_file_path = os.path.join(directory, filename)
    full_file_path = cur_dir + local_file_path
    cluster_pdf = SimpleDocTemplate(full_file_path)
    for line in pdf_lines:
        para = Paragraph(line, style["Normal"])
        story.append(para)
        story.append(Spacer(inch*.05, inch*.05))
    cluster_pdf.build(story)

    s3 = S3Connection("AKIAJTM2LBKXQIUVR5UQ", "F+IV5WbjQOyHdB6UtFRxGuK+eFlA79R5oSXD8AwI")
    bucket = s3.get_bucket("cluster-runs")
    k = Key(bucket)
    k.key = cluster_run_id
    k.set_metadata("Content-Type", "application/pdf")
    k.set_contents_from_filename(full_file_path)



def main():
    list = []
    list.append("Hello")
    create_pdf(list, 259)


# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == '__main__':
    main()