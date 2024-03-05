from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    close_annoying_modal()
    download_csv_file()
    orders = get_orders()
    for order in orders:
        fill_and_submit_form(order)
        pdf_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        embed_screenshot_to_pdf(pdf_path,screenshot_path)
        go_to_order_another()
        close_annoying_modal()   
    archive_orders()

def open_robot_order_website():
    """ 
    Open the robot order webstie to place the order
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def close_annoying_modal():
    """
    Close the annoying modal that pops up when you click the OK button on the robot order website.
    """
    page = browser.page()
    page.click("button:text('Ok')")

def download_csv_file():
    """
    Download the CSV file with the robot specifications
    """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite=True)

def get_orders():
    """
    Get orders from the CSV file and place the order
    """
    orders = read_csv_file_as_table()
    return orders

def read_csv_file_as_table():
    """
    Read the CSV file as a table
    """
    table = Tables()
    return table.read_table_from_csv("orders.csv",header=True,columns=["Order number","Head","Body","Legs","Address"],delimiters=',')

def fill_and_submit_form(orders):
    """
    fill an submit the form with the given order data.
    """
    page = browser.page()
    page.select_option("#head", str(orders["Head"]))
    page.click("#id-body-"+str(orders["Body"]))
    page.fill(" //input[@placeholder='Enter the part number for the legs']",str(orders["Legs"]))
    page.fill("#address", str(orders["Address"]))
    while not page.locator("#receipt").is_visible():
        page.click("button:text('Order')")

def go_to_order_another():
    """
    click the order another to order another bot
    """
    page = browser.page()
    page.click("#order-another")  

def store_receipt_as_pdf(receipt_number):
    """
    Store the receipt as a PDF file
    """
    page = browser.page()
    sales_receipt_html = page.locator("#receipt").inner_html()
    pdf_path = f"output/receipt/{receipt_number}.pdf"
    pdf = PDF()
    pdf.html_to_pdf(sales_receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(receipt_number):
    """
    Take a screenshot of the ordered robot and embed in pdf file
    """
    page = browser.page()
    robot = page.locator("#robot-preview-image")
    screenshot = f"output/receipt/{receipt_number}.png"
    robot.screenshot(path=screenshot)
    return screenshot

def embed_screenshot_to_pdf(pdf_path,png_path):
    """
    Embed the screenshot of the robot in the pdf file, delete png file after it has been added to pdf
    """
    pdf = PDF()
    pdf.add_files_to_pdf(files=[png_path],target_document=pdf_path,append=True)

def archive_orders():
    """
    Archive the receipts as a zip folder
    """
    archive = Archive()
    archive.archive_folder_with_zip("output/receipt", "output/receipts.zip",recursive=True)
