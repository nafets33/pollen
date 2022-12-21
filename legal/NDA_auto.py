import datetime
import pandas as pd
import os
import argparse
# import _locale
import pytz
# est = _locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])
est = pytz.timezone("US/Eastern")

def createParser_NDA():

    parser = argparse.ArgumentParser()
    parser.add_argument ('-dp', default="Divergent Thinkers")
    parser.add_argument ('-rp', default="Jedidiah Oladele")
    parser.add_argument ('-date', default=datetime.datetime.strftime(datetime.datetime.now(est), '%B %d, %Y'))
    # parser.add_argument ('-prod', default='true')

    return parser


legal_root = os.getcwd()
# db_root = os.path.join(main_root, 'db')
# legal_root = os.path.join(main_root, 'legal')

parser = createParser_NDA()
namespace = parser.parse_args()
date= namespace.date
disclosing_party= namespace.dp
receiving_party= namespace.rp
governinglaw = "United States"

# Optional Clauses

# # Structured Headers
# level-1:
# no-indent:
# no-reset:

content = {'content':
f'{"THIS AGREEMENT is made and entered into as of "}{date}{" Effective Date, by and between "}{disclosing_party}{", :the Disclosing Party and "}{receiving_party}{", the Recipient" "(collectively, the Parties)."}" Purpose for Disclosure ("Business Purpose"): "{disclosing_party}'
"The Parties hereby agree as follows:"
"\n"
"\n"
"""
l. For purposes of this Agreement, the term 'Confidential Information' means any financial, business, legal and technical information disclosed to Recipient by or for Discloser or any of its affiliates, suppliers, customers and employees. Information includes research, development, operations, marketing, transactions, regulatory affairs, discoveries, inventions, methods, processes, articles, materials, algorithms, software, specifications, designs, drawings, data, strategies, plans, prospects, know-how and ideas, whether tangible or intangible, and including any copies, abstracts, summaries, analyses and other derivatives thereof. Disclosure includes any act of transmitting the information whether previously, presently, or subsequently disclosed to recipient. For convenience, the Disclosing Party may, but is not required to, mark written Confidential Information with the legend "Confidential" or an equivalent designation, Confidential Information also includes information that by its nature would be understood by a reasonable person to be confidential.
l. All Confidential Information disclosed to the Recipient will be used solely for the Business Purpose and for no other purpose whatsoever. The Recipient agrees to keep the Disclosing Party's Confidential Information confidential and to protect the confidentiality of such Confidential Information with the same degree of care with which it protects the confidentiality of its own confidential information, and in no event with less than a reasonable degree of care. Recipient may disclose Confidential Information only to its employees, agents, consultants and contractors on a need-to-know basis, and only if such employees, agents, consultants and contractors have executed appropriate written agreements with Recipient sufficient to enable Recipient to enforce all the provisions of this Agreement. Recipient shall not make any copies of Disclosing Party's Confidential Information except as needed for the Business Purpose. At the request of Disclosing Party, Recipient shall return to Disclosing Party all Confidential Information of Disclosing Party (including any copies thereof) or certify the destruction thereof.
l. All right title and interest in and to the Confidential Information shall remain with Disclosing Party or its licensors. Nothing in this Agreement is intended to grant any rights to Recipient under any patents, copyrights, trademarks, or trade secrets of Disclosing Party. ALL CONFIDENTIAL INFORMATION IS PROVIDED "AS IS". THE DISCLOSING PARTY MAKES NO WARRANTIES, EXPRESS, IMPLIED OR OTHERWISE, REGARDING NON-INFRINGEMENT OF THIRD PARTY RIGHTS OR ITS ACCURACY, COMPLETENESS OR PERFORMANCE.
l. The obligations and limitations set forth herein regarding Confidential Information shall not apply to information which is: (a) at any time in the public domain, other than by a breach on the part of the Recipient; or (b) at any time rightfully received from a third party which had the right to and transmits it to the Recipient without any obligation of confidentiality.
l. In the event that the Recipient shall breach this Agreement, or in the event that a breach appears to be imminent, the Disclosing Party shall be entitled to all legal and equitable remedies afforded it by law, and in addition may recover all reasonable costs and attorneys' fees incurred in seeking such remedies.  If the Confidential Information is sought by any third party, including by way of subpoena or other court process, the Recipient shall inform the Disclosing Party of the request in sufficient time to permit the Disclosing Party to object to and, if necessary, seek court intervention to prevent the disclosure.  
"""
f'l. The validity, construction and enforceability of this Agreement shall be governed in all respects by the law of {governinglaw}. This Agreement may not be amended except in writing signed by a duly authorized representative of the respective Parties. This Agreement shall control in the event of a conflict with any other agreement between the Parties with respect to the subject matter hereof.'
"l. This Agreement will terminate as to the further exchange of Confidential Information immediately upon the earlier of receipt by one party of written notice from the other or one year after the date of this Agreement."
"\n"
"\n"
"IN WITNESS HEREOF, the parties have executed this Agreement as of the date set forth above."
"\n"
f'"For the "{disclosing_party}" - Signature: ______________________________"'
"\n"
"Date:________________________ Print: _________________________"
"\n"
f'"For the "{receiving_party}" - Signature: ______________________________"'
"\n"
"Date: _______________________ Print: _________________________"


}

doc_w = os.path.join(legal_root, f'{receiving_party}{"___"}{"NDA.txt"}')

from fpdf import FPDF


with open( doc_w, 'w') as f:
    f.write(content['content'])

title = 'Terms of Contract'

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        # self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        # Read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        # self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, title, name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name)


# save the pdf with name .pdf
# pdf = FPDF()
# pdf.add_page()
# pdf.set_font("Arial", size = 15)
# pdf.set_left_margin(32)
# pdf.set_right_margin(32)
pdf = PDF()
pdf.set_title(title)
pdf.print_chapter(1, '----', doc_w)

doc_w = os.path.join(legal_root, f'{receiving_party}{"___"}{"NDA.pdf"}')
pdf.output(doc_w) 