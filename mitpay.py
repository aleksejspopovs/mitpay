#!/usr/bin/env python3

import sys
import traceback
from xml.etree import ElementTree as ET

import pdfrw

OUTPUT_WIDTH = 72
REDACTED_MODE = False

def format_term(term_code):
    # converted from code wrapped in "//TERMCODE" and "// END TERMCODE" inside
    # the PDF
    year = term_code[:4]
    term_kind = term_code[4]
    term_kind_readable = {'1': 'Fall', '2': 'Spring', '3': 'Spring'}.get(
        term_kind, '???')

    return '{} {}'.format(term_kind_readable, year)

def format_id(id_):
    if REDACTED_MODE:
        return '[redacted]'

    return id_

def format_date(date):
    # I think the ISO dates in the XML are pretty awesome
    return date

def format_amount(amount, explicit_plus, invert_sign=False):
    if REDACTED_MODE:
        return '[redacted]'

    sign = ''
    if amount.startswith('+'):
        amount = amount[1:]
    if amount.startswith('-'):
        sign = '-'
        amount = amount[1:]

    if invert_sign:
        sign = '-' if sign == '' else ''

    if explicit_plus and (sign == ''):
        sign = '+'

    whole, cents = amount.split('.')
    # terrible hack to split the whole part into groups of three
    whole_rev = whole[::-1]
    whole_grouped = [whole_rev[3*i:3*(i+1)][::-1]
                     for i in range((len(whole) + 2) // 3)][::-1]

    return '{}${}.{}'.format(sign, ' '.join(whole_grouped), cents)

def print_line():
    print('-'*72)

def print_center(*s):
    s = ' '.join(s)
    padding = (OUTPUT_WIDTH - len(s)) // 2
    print(' '*padding, s, sep='')

def print_left(*s):
    print(*s)

def print_right(*s):
    s = ' '.join(s)
    padding = OUTPUT_WIDTH - len(s)
    print(' '*padding, s, sep='')

def print_pair(left, right):
    padding = OUTPUT_WIDTH - len(left) - len(right)
    if padding < 2:
        print_left(left)
        print_right(right)
    else:
        print(left, ' '*padding, right, sep='')

def main(filename):
    try:
        pdf = pdfrw.PdfFileReader(filename)
    except Exception as e:
        print('Error: couldn\'t open statement.')
        print('Are you sure the file "{}" exists? Is it a PDF?'.format(filename))
        print()
        print('Technical information:')
        traceback.print_exc()
        return

    try:
        xfa = pdf.Root.AcroForm.XFA.stream

        # if you want to explore the format yourself, I suggest printing
        # the contents of the xfa variable --- it's just a string containing
        # XML, some of which contains statement information and some of which
        # contains JavaScript describing how the data is to be displayed

        tree = ET.fromstring(xfa)
        datasets = tree.find('{http://www.xfa.org/schema/xfa-data/1.0/}datasets')
        statement = datasets.find('*/TouchNet/BillingStmt')
    except Exception as e:
        print('Error: couldn\'t find statement data in PDF.')
        print('Are you sure this PDF is a statement from the new MITPAY?')
        print()
        print('Technical information:')
        traceback.print_exc()
        return


    student_id = statement.find('Student/StuID').text
    student_name = statement.find('Student/FullName').text
    statement_term = format_term(statement.find('TermCode').text)

    statement_date = statement.find('StmtDt').text
    statement_due = statement.find('DueDt').text

    amount_due = statement.find('AmtDue').text

    print_line()
    print_center('MIT BILLING STATEMENT')
    print_center('UNOFFICIAL. Contact SFS in case of discrepancies.')
    print_center('This report should hopefully include all personalized information')
    print_center('from the PDF except the student\'s address. No guarantees.')
    print_center('When paying by mailing a check, you MUST use the original PDF.')
    print_center('If amount due is negative, you are due a refund.')

    print_line()
    print_center('{} (ID: {})'.format(student_name, format_id(student_id)))
    print_pair('Statement generated on {}'.format(format_date(statement_date)),
        'Due on {}'.format(format_date(statement_due)))
    print_pair('Term: {}'.format(statement_term),
        'Amount due: {}'.format(format_amount(amount_due, False)))

    print_line()

    for line in statement.findall('LineItem'):
        kind = line.find('Type').text
        description = line.find('Desc').text
        amount = line.find('Amt').text # might be None

        date = None
        if line.find('TransDt') is not None:
            date = line.find('TransDt').text
        term = None
        if line.find('TermCode') is not None:
            term = line.find('TermCode').text

        formatted_date = ''
        if (date is not None) and (term is not None):
            formatted_date = ' ({}, {})'.format(format_term(term),
                format_date(date))
        elif date is not None:
            formatted_date = ' ({})'.format(format_date(date))
        elif term is not None:
            formatted_date = ' ({})'.format(format_term(term))

        complete_description = '{desc}{date}'.format(
            desc=description,
            date=formatted_date)

        if amount is None:
            print_center(complete_description)
        else:
            # NB: sometimes Charges have negative amounts
            # e.g. "Initial Housing Average Fee Cr" (freshmen getting their
            # estimated housing fee back) is a charge for some reason.
            invert_sign = (kind == 'Charge') or (kind == 'FutureChgs') \
               or kind.endswith('Chg')

            print_pair(complete_description,
                format_amount(amount, True, invert_sign))

    print_line()
    print_pair('Amount due', format_amount(amount_due, False))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE:')
        print('{} statement.pdf'.format(sys.argv[0]))
    else:
        main(sys.argv[1])
