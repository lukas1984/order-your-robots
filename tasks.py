from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    
    browser.configure(
        #slowmo=100,
    )

    open_rsb_website()
    download_order_csv()
    
    orders = Tables().read_table_from_csv('orders.csv')
    for order in orders:
        place_order_in_rsb(order)

    archive_receipts()

def open_rsb_website():
    """Open RSB website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_popup():
    """Accept the initial popup"""
    page = browser.page()
    page.click("button:text('Yep')")

def download_order_csv():
    """Download the CSV file that contains the orders to place"""
    http = HTTP()
    http.download(url='https://robotsparebinindustries.com/orders.csv', overwrite = True)

def place_order_in_rsb(order):
    """Places the order into the RSB website"""
    
    order_number = order['Order number']
    close_popup()
    fill_the_form(order)
    screenshot = take_preview_screenshot(order_number)
    submit_order()
    receipt = store_receipt_as_pdf(order_number)
    embed_screenshot_to_receipt(screenshot, receipt)
    back_to_order_page()

def fill_the_form(order):
    """Fill the order form with values"""
    page = browser.page()

    page.select_option('#head', order['Head'])
    page.click('#id-body-' + order['Body'])
    page.fill('[placeholder="Enter the part number for the legs"]', order['Legs'])
    page.fill('#address', order['Address'])

def take_preview_screenshot(order_number):
    """Take a screenshot and save it"""
    page = browser.page()
    page.click('#preview')
    screenshot_path = 'output/screenshots/order_' + order_number + '.png'
    page.screenshot(path = screenshot_path)
    return screenshot_path

def submit_order():
    """Submit the order (retrying it if RSB returns an error)"""
    page = browser.page()
    order_ok = False
    while not order_ok:
        page.click('#order')

        # repeat until no errors are present
        if page.query_selector('.alert-danger') == None:
            order_ok = True

def store_receipt_as_pdf(order_number):
    """Save the receipt as PDF"""
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()
    
    pdf = PDF()
    pdf_path = 'output/receipts/order_' + order_number + '.pdf'
    pdf.html_to_pdf(receipt, pdf_path)
    return pdf_path

def back_to_order_page():
    """Go back to order page"""
    page = browser.page()
    page.click('#order-another')

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Append the screenshot to the receipt file"""
    pdf = PDF()
    pdf.add_files_to_pdf(files = [ screenshot ], target_document = pdf_file, append = True)

def archive_receipts():
    """Gather all receipts into a single ZIP file"""
    archive = Archive()
    archive.archive_folder_with_zip(folder = 'output/receipts/', archive_name = 'output/orders.zip')