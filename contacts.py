from tkinter import Tk, Button, PhotoImage, Label, LabelFrame, W, E, N, S, Entry, END, StringVar, Scrollbar, Toplevel
from tkinter import ttk
import sqlite3

###Create by Thuong Nguyen 21/8/2021

class Contacts:
    db_filename = "contacts.db"

    def __init__(self, root):
        self.root = root
        self.create_gui()

        ttk.style = ttk.Style()
        ttk.style.configure("Treeview", font=('helvetica', 10))
        ttk.style.configure("Treeview.Heading", font=('helvetica', 12, 'bold'))


    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.db_filename) as conn:
            print("You have successfully connected to the database")
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

    def create_gui(self):
        self.create_left_icon()
        self.create_label_frame()
        self.create_message_area()
        self.create_tree_view()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.view_contacts()


    ### Tạo icon
    def create_left_icon(self):
        photo = PhotoImage(file='icons/logo.gif')
        label = Label(image=photo)
        label.image = photo
        label.grid(row=0, column=0)

    ### Tạo bảng nhập thông tin
    def create_label_frame(self):
        labelFrame = LabelFrame(self.root, text="Create New Contact", bg="sky blue", font="helvetica 10")
        labelFrame.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        Label(labelFrame, text="Name:", bg="green", fg="white").grid(row=1, column=1, sticky=W, pady=2, padx=15)
        self.namefield = Entry(labelFrame)
        self.namefield.grid(row=1, column=2, sticky=W, padx=5, pady=2)
        Label(labelFrame, text="Email:", bg="brown", fg="white").grid(row=2, column=1, sticky=W, pady=2, padx=15)
        self.emailfield= Entry(labelFrame)
        self.emailfield.grid(row=2, column=2, sticky=W, padx=5, pady=2)
        Label(labelFrame, text="Number:", bg="Black", fg="white").grid(row=3, column=1, sticky=W, pady=2, padx=15)
        self.numfield= Entry(labelFrame)
        self.numfield.grid(row=3, column=2, sticky=W, padx=5, pady=2)

        Button(labelFrame, text="Add Contact", command=self.on_add_contact_button_clicked, bg="blue", fg="white").grid(row=4, column=2, sticky=E, padx=5, pady=5)

    ### Tạo message
    def create_message_area(self):
        self.message = Label(text="", fg="red")
        self.message.grid(row=3, column=1, sticky=W)

    ### tạo tree table view
    def create_tree_view(self):
        self.tree = ttk.Treeview(height=10, columns=("email", "number"))
        self.tree.grid(row=6, column=0, columnspan=3)
        self.tree.heading("#0", text="Name", anchor=W)
        self.tree.heading("email", text="Email Address", anchor=W)
        self.tree.heading("number", text="Contact Number", anchor=W)

    ### tạo crollbar cho tree table
    def create_scrollbar(self):
        self.scrollbar= Scrollbar(orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=6, column=3, rowspan=10, sticky='sn')

    def create_bottom_buttons(self):
        Button(text='Delete Selected', command=self.on_delete_contact_button_clicker, bg="red", fg="white").grid(row=8, column=0, sticky=W, pady=10, padx= 20)
        Button(text='Modify Selected', command=self.on_modify_selected_button_clicker, bg="purple", fg="white").grid(row=8, column=1, sticky=W)

    def on_add_contact_button_clicked(self):
        self.add_new_contact()
    def on_delete_contact_button_clicker(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected to delete'
            return
        self.delete_contact()

    def on_modify_selected_button_clicker(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected to modify'
            return
        self.open_modify_window()

    def open_modify_window(self):
        name = self.tree.item(self.tree.selection())['text']
        old_number = self.tree.item(self.tree.selection())['values'][1]
        self.transient = Toplevel()
        self.transient.title("Update Contact")
        Label(self.transient, text="Name").grid(row=0, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=name), state='readonly').grid(row=0, column=2)
        Label(self.transient, text="Old contact number").grid(row=1, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=old_number), state='readonly').grid(row=1, column=2)
        Label(self.transient, text="New Phone Number:").grid(row=2, column=1)
        new_phone_number = Entry(self.transient)
        new_phone_number.grid(row=2, column=2)

        Button(self.transient, text='Update Contact', command=lambda: self.update_contact(
            new_phone_number.get(), old_number, name)).grid(row=3, column=2, sticky=E)

        self.transient.mainloop()

    def update_contact(self, new_phone, old_phone,name):
        query = 'UPDATE contacts_list SET number=? WHERE number =? AND name =?'
        parameters = (new_phone, old_phone, name)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = 'Phone number of {} modified'.format(name)
        self.view_contacts()





    def add_new_contact(self):
        if self.new_contact_validate():
            query = "INSERT INTO contacts_list VALUES(NULL, ?, ?, ?)"
            parameters = (self.namefield.get(), self.emailfield.get(), self.numfield.get())
            self.execute_db_query(query, parameters)
            self.message['text'] = 'New contact {} added'.format(self.namefield.get())
            self.namefield.delete(0, END)
            self.emailfield.delete(0, END)
            self.numfield.delete(0, END)
            self.view_contacts()

        else:
            self.message['text'] = 'name, email, and number cannot be blank'
            self.view_records()

    def new_contact_validate(self):
        return len(self.namefield.get()) != 0 and len(self.emailfield.get()) != 0 and len(self.numfield.get()) != 0

    def view_contacts(self):
        items = self.tree.get_children()
        for items in items:
            self.tree.delete(items)
        query = 'SELECT * FROM contacts_list ORDER BY name desc'
        contact_entries = self.execute_db_query(query)
        for row in contact_entries:
            self.tree.insert('', 0, text=row[1], values=(row[2], row[3]))

    def delete_contact(self):
        self.message['text'] = ''
        name = self.tree.item(self.tree.selection())['text']
        query = "DELETE FROM contacts_list WHERE name =? "
        self.execute_db_query(query, (name, ))
        self.message['text']="Contacts for {} deleted".format(name)
        self.view_contacts()

if __name__ =='__main__':
    root = Tk()
    root.title("My Contact List")
    root.geometry("650x450")
    root.resizable(width=False,height=False)
    application = Contacts(root)
    root.mainloop()

