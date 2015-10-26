# encoding=utf-8

import Tkinter as tk
import tkFileDialog
import tkMessageBox

import logging as log

import os


class BiddingGUI(tk.Frame):
    __tour_filename = None
    __bws_filename = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.__tour_filename = tk.StringVar(master=self)
        self.__bws_filename = tk.StringVar(master=self)
        self.grid()
        self.create_widgets()
        self.master.title('JBBD - JFR/BWS bidding data')
        self.set_icon(self.master)

    def set_icon(self, master):
        img = tk.PhotoImage(data=self.__icon_data, master=master)
        master.tk.call('wm', 'iconphoto', master._w, img)

    def tour_select(self):
        self.__tour_filename.set(tkFileDialog.askopenfilename(
            title='Wybierz główny plik wyników turnieju',
            filetypes=[('HTML files', '.htm*'), ('all files', '.*')]))

    def bws_select(self):
        self.__bws_filename.set(tkFileDialog.askopenfilename(
            title='Wybierz plik z danymi licytacji',
            filetypes=[('BWS files', '.bws'), ('all files', '.*')]))

    class GUILogHandler(log.Handler):
        def __init__(self, text):
            log.Handler.__init__(self)
            self.text = text

        def emit(self, record):
            msg = self.format(record)

            def append():
                self.text.insert(tk.END, msg + '\n')
                self.text.yview(tk.END)

            self.text.after(0, append)

    def run_bidding_data(self):
        try:
            self.log_field.delete(1.0, tk.END)
            if not os.path.exists(self.__bws_filename.get()):
                raise Exception('BWS file not found')
            if not os.path.exists(self.__tour_filename.get()):
                raise Exception('Tournament results file not found')
            from bidding_data import JFRBidding
            parser = JFRBidding(
                bws_file=self.__bws_filename.get(),
                file_prefix=self.__tour_filename.get())
            parser.write_bidding_tables()
            parser.write_bidding_scripts()
            parser.write_bidding_links()
        except Exception as ex:
            log.getLogger('root').error(ex)
            tkMessageBox.showerror('Błąd!', ex)
            raise

    def create_widgets(self):
        tour_label = tk.Label(
            self, text='Plik turnieju:')
        tour_entry = tk.Entry(
            self, state=tk.DISABLED, textvariable=self.__tour_filename)
        tour_select_btn = tk.Button(
            self, text='Szukaj', command=self.tour_select)
        tour_label.grid(row=0, column=0)
        tour_entry.grid(row=0, column=1, columnspan=4, sticky=tk.E+tk.W)
        tour_select_btn.grid(row=0, column=5)

        bws_label = tk.Label(
            self, text='BWS:')
        bws_entry = tk.Entry(
            self, state=tk.DISABLED, textvariable=self.__bws_filename)
        bws_select_btn = tk.Button(
            self, text='Szukaj', command=self.bws_select)
        bws_label.grid(row=1, column=0)
        bws_entry.grid(row=1, column=1, columnspan=4, sticky=tk.E+tk.W)
        bws_select_btn.grid(row=1, column=5)

        run_btn = tk.Button(
            self, text='No to sru!', height=3, command=self.run_bidding_data)
        quit_btn = tk.Button(
            self, text='Koniec tego dobrego', command=self.quit)
        run_btn.grid(
            row=2, column=0, columnspan=4, sticky=tk.N+tk.S+tk.E+tk.W)
        quit_btn.grid(row=2, column=4, columnspan=2)

        log_scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL)
        log_scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.log_field = tk.Text(
            self, height=5, width=80, wrap=tk.NONE,
            xscrollcommand=log_scroll_x.set,
            yscrollcommand=log_scroll_y.set)
        log_scroll_x['command'] = self.log_field.xview
        log_scroll_y['command'] = self.log_field.yview
        self.log_field.grid(row=3, column=0, columnspan=6, sticky=tk.E+tk.W)
        log_scroll_y.grid(row=3, column=6, sticky=tk.N+tk.S)
        log_scroll_x.grid(row=4, column=0, columnspan=6, sticky=tk.E+tk.W)

        log.basicConfig(
            level=log.NOTSET,
            streamhandler=log.NullHandler)
        self.__gui_logger = self.GUILogHandler(self.log_field)
        self.__gui_logger.setLevel(log.INFO)
        self.__gui_logger.setFormatter(log.Formatter(
            '%(levelname)-8s %(name)-8s %(message)s'))
        log.getLogger().addHandler(self.__gui_logger)
        log.getLogger().removeHandler(log.getLogger().handlers[0])

    __icon_data = """R0lGODlhIAAgAOeRAAAAAAQEBAUFBQYGBggICAAAcQAAcgAAcwAAdAAAdQA
AdgAAdwAAeAAAeQEBegsLEQQEewUFew4ODgYGfA8PDwgIfQoKfgoKfxMTEwsLfxQUIQ0NgBERghISghQ
UgxQUhBUVhRYWhhkZhhkZhxoajxsbhx4eiSgoKCIijCQkjC0tRzAwMCoqkSsrkSwskCwskjExkzU1lzg
4ljg4mUFBQTs7mjw8mUJChEhISEVFn0hIolBQVUpKo01NoVBQgU9Pok9PplVVqlhYp1pakllZp1lZq1t
bklpaqF1dlFxcqV5eq19fqmBgsGFhsGJirGJisWNjsWVlrWVlrmZmrmhotG5ubmlpvG1tsHFxuXR0tXR
0u3V1u3V1vHV1vXZ2vHd3vXh4vXt7xnt7x3x8x3x8yH19wH5+u4GBvIKCyoaGv4eHwJSUxpWVx5ubzp6
e0p+fzKWl26io0aur0q+v1Lq62ry83L+/3cDA3sHB3sbG4MbG4cnJycjI4svL49TU6NfX6tjY69nZ69v
b7ODg7ubm8urq9O3t9e7u9u/v9vPz+Pf3+/n5/Pr6/Pz8/Pz8/f39/v7+/v/////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
//////////////////////yH5BAEKAP8ALAAAAAAgACAAQAj+AP9JAECwYMEAGP4pXMiwIUOCaMo0qeE
FCpMcQZAAOOGwY0OCkUJGcsQmCyGRKEMSWYCgT8qQBlH6gVBhykuRSTzchFlQDJgXMbQILaLFCEGPSP+
B3MmU6Z6YfBJAmBOFQYOrCXokQplTZKAINiDxXNq0bEqDKrqQWcv2ioajSTsStPLhyYwvLKxaMAogrlw
AYoQKFhzmgcHDiAsqBWC2sciYd+pESnG1wYFBN7uuQZDmbMFIetREklGZwRKRbwogOLDAMoLXCFoLiRT
TcWOCBBLr3o2YwEDeff06JMhFy5cvgrdo8QFX+EKCY3SAmGGcRQYsQ5o7X0xiRIgLVBS1MLiQ4Ebw7Qo
JBobCQ8uTFiiAaASwAv1iOG3y69fvZgeO/wAGGCANAgAwAFm2NVWbbYQAUshOMdmBSCRCXGUAHjslIYI
ZBsjxElQuRHJGa1cp8MdLXUVCxwJKoAQVAnkcQmIDDMgQ0iOMMALJETrluIghG5SgCG2f1SFIJDBcxcA
PKMWxAQccTOBAB1BWyYEURCLYmBMmMLVggl4WVEUkjZRp5plopmlmJFUcRQFwcB5GwT8BAQA7"""

def main():
    app = BiddingGUI()
    app.mainloop()

if __name__ == '__main__':
    main()
