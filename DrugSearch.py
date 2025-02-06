import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import re


def fetch_data(search_keyword):
    """
    Fetch data from the specified URL using the search keyword and update the tree view.

    Args:
        search_keyword (str): The keyword to search for drug prices.
    """
    url = f"https://www.yaopinnet.com/tools/load/jiage_Load.asp?keyword={search_keyword}"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'jiagetable'})
        rows = table.find_all('tr')[1:-1]  # Skip header and footer rows

        data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            # note translation
            if len(cols) > 4:
                if cols[4] == '*' or cols[4] == '★' or cols[4] == '﹡':
                    cols[4] = '代表品'
                elif cols[4] == '△' or cols[4] == '#' or cols[4] == '＃':
                    cols[4] = '临时价格'

            # price format fix
            if len(cols) > 2:  # 确保价格列存在
                cols[2] = fix_price_format(cols[2])  # 修正价格格式
                if not is_valid_price(cols[2]):  # 删除不合理的价格条目
                    continue

            if len(cols) > 3 and cols[3]:  # 判断生产厂家是否存在
                cols[4] += "[优质优价药品最高零售价 单独定价]"

            data.append(cols)

        for item in tree.get_children():
            tree.delete(item)

        for row in data:
            tree.insert("", "end", values=row)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except IndexError as e:
        print(f"Error processing data: {e}")


def fix_price_format(price):
    if re.match(r'^\.\d+$', price):
        return '0' + price
    return price


def is_valid_price(price):
    try:
        price_value = float(price.replace(',', ''))
        return price_value > 0
    except ValueError:
        return False


def on_fetch_data():
    search_keyword = entry.get()
    fetch_data(search_keyword)


def sort_tree(column, reverse):
    """
    Sort the treeview by the given column.

    Args:
        column (str): The column to sort by.
        reverse (bool): Whether to sort in reverse order.
    """
    # Extract data from the treeview for sorting
    data = [(tree.set(child, column), child) for child in tree.get_children('')]

    # Try to sort by converting to numbers if possible, otherwise sort as strings
    def try_convert(value):
        try:
            return float(value.replace(',', ''))  # Convert numeric strings (e.g., prices)
        except ValueError:
            return value  # Return as-is for non-numeric strings

    data.sort(key=lambda item: try_convert(item[0]), reverse=reverse)

    # Rearrange items in sorted order
    for index, (_, child) in enumerate(data):
        tree.move(child, '', index)

    # Toggle the sorting order for the next click
    tree.heading(column, command=lambda: sort_tree(column, not reverse))

# main window

root = tk.Tk()
root.title("药品价格查询")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (1200 // 2)
y = (screen_height // 2) - (800 // 2)
root.geometry("1200x800+{}+{}".format(x, y))
root.resizable(True, True)
root.iconbitmap('E:\DrugSearch\drug.ico')

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

entry = ttk.Entry(frame, width=50)
entry.grid(row=0, column=0, pady=10, padx=5, sticky=(tk.W, tk.E))

root.bind('<Return>', lambda event: on_fetch_data())
button = ttk.Button(frame, text="搜索（Enter）", command=on_fetch_data)
button.grid(row=0, column=1, pady=10, padx=5, sticky=(tk.W, tk.E))

columns = ("name", "form", "price", "manufacturer", "note", "source")
tree = ttk.Treeview(frame, columns=columns, show='headings')

# treeview column headings
tree.heading("name", text="药品名称", command=lambda: sort_tree("name", False))
tree.heading("form", text="剂型/规格/单位", command=lambda: sort_tree("form", False))
tree.heading("price", text="价格", command=lambda: sort_tree("price", False))
tree.heading("manufacturer", text="生产厂家", command=lambda: sort_tree("manufacturer", False))
tree.heading("note", text="备注", command=lambda: sort_tree("note", False))
tree.heading("source", text="来源", command=lambda: sort_tree("source", False))

# column width and alignment
for col in columns:
    tree.column(col, width=200, minwidth=150, stretch=True)
    if col == "price":
        tree.column(col, width=50, minwidth=20, anchor=tk.CENTER)

tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))

# resizable
for child in frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)

# focus on the entry field
entry.focus()

root.mainloop()