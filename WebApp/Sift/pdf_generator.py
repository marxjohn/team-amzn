__author__ = 'cse498'

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key


def create_pdf(pdf_lines, cluster_run_id):
    style = getSampleStyleSheet()
    story = []
    filename = cluster_run_id.__str__() + ".pdf"
    cluster_pdf = SimpleDocTemplate(filename)
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
    k.set_contents_from_filename(filename)