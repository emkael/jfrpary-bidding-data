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

    __icon_data = """iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/
AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3woaDDQU8kJ17gAAABl0RVh0Q29tbWVu
dABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAP/SURBVFjD7ZdfTFNXGMB/bS+3LRUqf8xmFjPmQsAphuxh
kajhZWYkm/oCCSYo4wFeXIIz3ZbBdFGXsQWy+CBZnC8GQxqjWWIFs7hEp2MxCBpklbSQsbBRig6CbWnp
9XJ79kCphQAtrrg97CRfcnPOd+73y3e+P+cgy/LrmZmZHkAkEkmSRE5OzjekcmRmZo4mYzxe8vMLDqXK
vuT3+18BKCp6h7KyjzEaLUsq+nzj2O0fMjHxO0ND7s2pAtDPf5SVfYQQEVQ1iKoGCYcDMVGUAEajhV27
3ifVIwYgyxYkSU9n50Nu3BhcoDQ6+gQAiyVr7QB0Oujr8/DoUQCDYW7aYNBz7doADocTTYsgBGsHMDkZ
pLf3D/bu3RYzfvWqk4EBL8HgU86e/QWdbg0Brlz5lbQ0Ax0dD+nvH8Pnm2FgwANAerpMKDSD1+ufV59t
bm5OCYAumlqcPHkXVQ0xOvqEwcHH7Ny5mcnJIJom8HimWL/egsn0mAsXPqCwsNDtcrkKW1pasNls/ywN
5z8URUNRVPR6HVarmUhEIAT09IwwM6NSVGTEZJrTdblcBcXFxfdtNtsxQH4ewwUFBRNut/vnmAcaG++g
KNMrbjIaLZw+/S7B4FRK3J+dnf15DKC9fYhQKJBwk8Eg4XCcIhwOPJdRRVHo6upCVVVkec55AhAvcnR3
d8fKeswDYi2SfKXoj+a0nn95SKn8mdcbwO9XyM42s2GDJel9S8bA7KwmWlvvCJutU4yN+ZM62wMH7AI+
EWATPT1/rqgb196fAdy8+ZuYmgoJIYSorLQL+DQqR8WtW8MJAaqqLoqNG78Ux4//KOCouHSpPyGAfnFg
3Ls3BkBvrye+AlBa2srISOL8V1WNEyfe5syZcioq2mhq+im5XgBgMkkcOdIBwMGDxUAkblUmL+8rXK6/
kjrXw4dLuH69joaGH6iuvpwcAIDT6SEt7TO2b3+Z2tq35o9pvgyxZUsz+/a1MT2tJITYsycft9uG3d7H
7t3fLZnq+qVi8vbtWkpLN3Pu3N1ov3q2tmPHazgch1i3zkgkIlBVDVXVEEIQiYgFR6GqGnl5WYyPN/Dg
gZdNm74mHJ5dPg0jEUFT03uUlLxKScm3i/gE1dVvcv58RWymre0+NTXtgCHqKQnQo9PZFoHPeS8QUKip
uYzdXrk0QCikUl6+LdYd443v3//GAuMAZnMaGRlWJGkONBh8iqpGyMqyLnt7ysgwJlcHnM5xIUmNwmQ6
Jurqvk+qDlRVXRS5uaeS0o29NZYLoK1bX0JVv1hVJZRlA+npq7se/N+M/jsA9fX1AGiatqYSbytafk3D
q32cpkpMJtOwTpblHLPZPOHz+V6o661WK0ajMfdv7mF1hk5b7XQAAAAASUVORK5CYII="""

def main():
    app = BiddingGUI()
    app.mainloop()

if __name__ == '__main__':
    main()
