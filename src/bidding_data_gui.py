# encoding=utf-8

"""
Bidding data for JFR Pary result pages - GUI.

Graphical user interface to insert HTML tables with bidding data into traveller
files generated by JFR Pary.
"""

import json
import logging as log
import os
import Queue
import socket
import threading
import tkFileDialog
import tkMessageBox

import Tkinter as tk

from bidding_data import __version__ as bidding_data_version
import bidding_data_resources as res

# config file path
CONFIG_FILE = 'config.json'


class BiddingGUI(tk.Frame):
    """GUI frame class."""

    # Tk variables to bind widget values
    __variables = {}
    # widgets which are toggled in Goniec settings panel
    __goniec_widgets = []

    def run_bidding_data(self):
        """
        Run the parser and do all the actual work.

        "On-click" event for analysis start button.
        Sanitizes input parameters, handles warning/error messages,
        imports main module (from CLI script) and runs it.
        """
        self.queue(self.run_btn.__setitem__, 'state', tk.DISABLED)
        try:
            # reset error/warning count and log output field
            self.__gui_logger.reset_counts()

            # check for input parameter paths
            if not os.path.exists(self.__variables['bws_filename'].get()):
                raise Exception('BWS file not found')
            if not os.path.exists(self.__variables['tour_filename'].get()):
                raise Exception('Tournament results file not found')

            # Goniec parameters/switches
            goniec_params = '%s:%d' % (
                self.__variables['goniec_host'].get(),
                self.__variables['goniec_port'].get()
            ) if self.__variables['goniec_enabled'].get() == 1 else None

            # do the magic
            from bidding_data import JFRBidding
            parser = JFRBidding(
                bws_file=self.__variables['bws_filename'].get(),
                file_prefix=self.__variables['tour_filename'].get())
            parser.setup_goniec(
                goniec_setup=goniec_params,
                goniec_force=self.__variables['goniec_forced'].get())
            changed_files = []
            changed_files += parser.write_bidding_tables()
            changed_files += parser.write_bidding_scripts()
            changed_files += parser.write_bidding_links()
            if self.__variables['goniec_enabled'].get() == 1:
                parser.send_changed_files(changed_files)

            # inform of any warnings/errors that might have occuerd
            if self.__gui_logger.errors():
                self.queue(res.play, 'error')
                self.queue(self.log_field.insert, tk.END,
                           ('Podczas wykonywania programu wystąpiły błędy ' +
                            'w liczbie: %d\n' +
                            'Sprawdź dziennik logów\n')
                           % self.__gui_logger.errors())
                self.queue(self.log_field.yview, tk.END)
            elif self.__gui_logger.warnings():
                self.queue(res.play, 'warning')
                self.queue(self.log_field.insert, tk.END,
                           ('Podczas wykonywania programu wystąpiły ' +
                            'ostrzeżenia w liczbie: %d\n' +
                            'Sprawdź dziennik logów\n')
                           % self.__gui_logger.warnings())
                self.queue(self.log_field.yview, tk.END)
            else:
                self.queue(res.play, 'success')
                self.queue(self.log_field.insert, tk.END,
                           'Wszystko wporzo.\n')
                self.queue(self.log_field.yview, tk.END)
        except Exception as ex:
            # JFRBidding errors are logged
            # (and notified of after entire execution),
            # other exceptions should halt execution and display error message
            log.getLogger('root').error(ex)
            self.queue(tkMessageBox.showerror, 'Błąd!', ex)
            raise
        finally:
            self.queue(self.run_btn.__setitem__, 'state', tk.NORMAL)

    def tour_select(self):
        """
        Allow for tournament file selection.

        "On-click" event for tournament select button.
        Displays file selection dialog for tournament file and stores user's
        choice in Tk variable.
        """
        self.__variables['tour_filename'].set(tkFileDialog.askopenfilename(
            title='Wybierz główny plik wyników turnieju',
            filetypes=[('HTML files', '.htm*'), ('all files', '.*')]))

    def bws_select(self):
        """
        Allow for BWS file selection.

        "On-click" event for BWS select button.
        Displays file selection dialog for tournament file and stores user's
        choice in Tk variable.
        """
        self.__variables['bws_filename'].set(tkFileDialog.askopenfilename(
            title='Wybierz plik z danymi licytacji',
            filetypes=[('BWS files', '.bws'), ('all files', '.*')]))

    def display_info(self):
        """Show application "About" box."""
        self.queue(
            tkMessageBox.showinfo, 'O co cho?',
            'Narzędzie dodaje do strony wyników z JFR Pary dane licytacji, ' +
            'zbierane w pliku BWS "pierniczkami" nowego typu.\n' +
            'Żeby użyć - wybierz główny plik turnieju (PREFIX.html) ' +
            'oraz plik BWS.\n\n' +
            'Wersja: ' + bidding_data_version + '\n' +
            'Autor: M. Klichowicz')

    def toggle_goniec(self):
        """Toggle state for Goniec-related controls on Goniec switch toggle."""
        for control in self.__goniec_widgets:
            self.queue(
                control.__setitem__, 'state',
                tk.NORMAL if self.__variables['goniec_enabled'].get() == 1
                else tk.DISABLED
            )

    def test_goniec(self):
        """Test connectivity with Goniec and display a message accordingly."""
        goniec_socket = socket.socket()
        try:
            goniec_socket.connect((self.__variables['goniec_host'].get(),
                                   self.__variables['goniec_port'].get()))
            goniec_socket.close()
            self.queue(
                tkMessageBox.showinfo, 'Hurra!',
                'Goniec - albo coś, co go udaje - działa!')
        except socket.error:
            self.queue(
                tkMessageBox.showerror, 'Buuu...',
                'Pod podanym adresem Goniec nie działa :(')
        except (ValueError, OverflowError):
            self.queue(
                tkMessageBox.showerror, 'Buuu...',
                'Parametry Gońca mają niewłaściwy format, ' +
                'czemu mi to robisz :(')

    def on_close(self):
        """Handle root window WM_DELETE_WINDOW message."""
        try:
            self.__store_config()
        except (ValueError, TypeError, OverflowError) as ex:
            log.getLogger('config').error('Could not save config file: %s', ex)
        self.master.destroy()

    def on_quit(self):
        """Handle manual "quit" button click."""
        self.on_close()
        self.quit()

    # GUI message queue (for background thread interaction)
    __queue = None

    def queue(self, callback, *args, **kwargs):
        """Add message (function call) to GUI interaction queue."""
        if self.__queue is None:
            self.__queue = Queue.Queue()
        self.__queue.put((callback, args, kwargs))

    def process_queue(self):
        """Process GUI interaction queue from other threads."""
        if self.__queue is None:
            self.__queue = Queue.Queue()
        try:
            callback, args, kwargs = self.__queue.get_nowait()
        except Queue.Empty:
            self.master.after(100, self.process_queue)
        else:
            callback(*args, **kwargs)
            self.master.after(1, self.process_queue)

    def __init__(self, master=None):
        """
        Construct the frame.

        Initializes window appearence, controls, layout and logging facility.
        """
        tk.Frame.__init__(self, master)

        self.__variables = {
            # bind Tk variables to input parameter paths
            'tour_filename': tk.StringVar(master=self),
            'bws_filename': tk.StringVar(master=self),
            # and to Goniec parameters
            'goniec_host': tk.StringVar(master=self),
            'goniec_port': tk.IntVar(master=self),
            # "boolean" variables to hold checkbox states
            'goniec_enabled': tk.IntVar(master=self),
            'goniec_forced': tk.IntVar(master=self)
        }

        # set window title and icon
        self.master.title('JBBD - JFR/BWS bidding data')
        self.__set_icon(res.ICON)

        # create controls
        self.__create_widgets()
        # and align them within a layout
        # second column and sixth row should expand
        self.__configure_grid_cells([1], [5])
        # main frame should fill entire application window
        self.pack(expand=1, fill=tk.BOTH)

        # finally, set logging up
        self.__configure_logging()

        # default config values
        self.__default_config = {
            'paths': {
                'html': '',
                'bws': ''
            },
            'goniec': {
                'enabled': 0,
                'host': 'localhost',
                'port': 8090
            }
        }

        # restore config from file
        self.__restore_config()

        # register on-close hook
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # fire up interthread queue
        self.after(100, self.process_queue)

    def __configure_grid_cells(self, columns, rows):
        """Set expand with window resize for cells of layout grid."""
        for column in columns:
            self.columnconfigure(column, weight=1)
        for row in rows:
            self.rowconfigure(row, weight=1)

    def __set_icon(self, data):
        """Set app icon from base64-encoded data."""
        # pylint: disable=protected-access
        img = tk.PhotoImage(data=data, master=self.master)
        # protected access is necessary since Tkinter does not expose
        # the wm.iconphoto call
        self.master.tk.call('wm', 'iconphoto', self.master._w, img)

    def __dispatch_run_button_action(self):
        """Dispatch main button action asynchronously."""
        run_thread = threading.Thread(target=self.run_bidding_data)
        run_thread.start()

    def __create_widgets(self):
        """
        Create main application window controls and align them on grid.

        Grid has 6 columns (so that 1/2, 1/3 or 1-4-1 layouts are configurable.
        """
        # label for tournament file selection
        tour_label = tk.Label(
            self, text='Plik turnieju:')
        # text field for tournament file path
        tour_entry = tk.Entry(
            self, textvariable=self.__variables['tour_filename'])
        # tournament selection button
        tour_select_btn = tk.Button(
            self, text='Szukaj', command=self.tour_select)
        # first row, label aligned to the right, text field expands
        tour_label.grid(row=0, column=0, sticky=tk.E)
        tour_entry.grid(row=0, column=1, columnspan=4, sticky=tk.E+tk.W)
        tour_select_btn.grid(row=0, column=5)

        # label for BWS file selection
        bws_label = tk.Label(
            self, text='BWS:')
        # text field for BWS file path
        bws_entry = tk.Entry(
            self, textvariable=self.__variables['bws_filename'])
        # BWS selection button
        bws_select_btn = tk.Button(
            self, text='Szukaj', command=self.bws_select)
        # second row, label aligned to the right, text field expands
        bws_label.grid(row=1, column=0, sticky=tk.E)
        bws_entry.grid(row=1, column=1, columnspan=4, sticky=tk.E+tk.W)
        bws_select_btn.grid(row=1, column=5)

        # main command button
        self.run_btn = tk.Button(
            self, text='No to sru!', height=3,
            command=self.__dispatch_run_button_action)
        info_btn = tk.Button(
            self, text='OCB?!', command=self.display_info)
        # application exit button
        quit_btn = tk.Button(
            self, text='Koniec tego dobrego', command=self.on_quit)
        # third and fourth row, leftmost 2/3 of window width, entire cell
        self.run_btn.grid(
            row=2, column=0, rowspan=2, columnspan=4,
            sticky=tk.N+tk.S+tk.E+tk.W)
        # third row, rightmost 1/3 of window width
        info_btn.grid(row=2, column=4, columnspan=3, sticky=tk.E+tk.W)
        # fourth row, rightmost 1/3 of window width
        quit_btn.grid(row=3, column=4, columnspan=3, sticky=tk.E+tk.W)

        self.__create_goniec_widgets()

        # vertical scrollbar for log output field
        log_scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL)
        # horizontal scrollbar for log output field
        log_scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        # log field, bound (both ways) to scrollbars
        self.log_field = tk.Text(
            self, height=5, width=80, wrap=tk.NONE,
            xscrollcommand=log_scroll_x.set,
            yscrollcommand=log_scroll_y.set)
        log_scroll_x['command'] = self.log_field.xview
        log_scroll_y['command'] = self.log_field.yview
        # fifth row, entries window width, expands with window
        self.log_field.grid(
            row=5, column=0, columnspan=6, sticky=tk.N+tk.S+tk.E+tk.W)
        # scrollbars to the right and to the bottom of the field
        log_scroll_y.grid(row=5, column=6, sticky=tk.N+tk.S)
        log_scroll_x.grid(row=6, column=0, columnspan=6, sticky=tk.E+tk.W)

    def __create_goniec_widgets(self):
        # Goniec toggle checkbox
        goniec_checkbox = tk.Checkbutton(
            self, text='Ślij Gońcem',
            command=self.toggle_goniec,
            variable=self.__variables['goniec_enabled'])
        # fifth row, leftmost column
        goniec_checkbox.grid(
            row=4, column=0)
        # aggregate for Goniec controls
        frame = tk.Frame(self)
        # fifth row, second leftmost column, 1-4-1 layout
        frame.grid(row=4, column=1, columnspan=4, sticky=tk.E+tk.W)
        # Goniec force toggle checkbox
        goniec_force_checkbox = tk.Checkbutton(
            frame, text='Wymuś przesłanie',
            variable=self.__variables['goniec_forced'])
        # first column of frame, aligned to the left
        goniec_force_checkbox.grid(
            row=0, column=0, sticky=tk.W)
        # label for Goniec host entry field
        goniec_host_label = tk.Label(
            frame, text='Host:')
        # second column of frame, aligned to the right
        goniec_host_label.grid(
            row=0, column=1, sticky=tk.E)
        # Goniec host entry field
        goniec_host_field = tk.Entry(
            frame, textvariable=self.__variables['goniec_host'])
        # fifth row, third column, aligned to the left
        goniec_host_field.grid(
            row=0, column=2, sticky=tk.W+tk.E)
        # label for Goniec port entry field
        goniec_port_label = tk.Label(
            frame, text='Port:')
        # fifth row, fourth column, aligned to the right
        goniec_port_label.grid(
            row=0, column=3, sticky=tk.E)
        # Goniec port entry field
        goniec_port_field = tk.Entry(
            frame, textvariable=self.__variables['goniec_port'])
        # fifth row, fifth column, aligned to the left
        goniec_port_field.grid(
            row=0, column=4, sticky=tk.W+tk.E)
        # Goniec test button
        goniec_test_btn = tk.Button(
            self, text='Test Gońca',
            command=self.test_goniec)
        # fifth row, rightmost column
        goniec_test_btn.grid(
            row=4, column=5)

        # aggregate all widgets for which goniec_checkbox toggles status
        self.__goniec_widgets = [
            goniec_force_checkbox,
            goniec_host_label, goniec_host_field,
            goniec_port_label, goniec_port_field,
            goniec_test_btn]

    def __configure_logging(self):
        """Set up logging facility, bound to log output field."""
        class GUILogHandler(log.Handler):
            """Log handler which allows output to Tk Text widget."""

            def __init__(self, text):
                """Construct the handler, provided Text widget to bind to."""
                log.Handler.__init__(self)
                self.text = text

            def emit(self, record):
                """Output the message."""
                msg = self.format(record)
                # Append message to the Text widget, at the end."""
                self.text.master.queue(self.text.insert, tk.END, msg + '\n')
                # scroll to the bottom, afterwards
                self.text.master.queue(self.text.yview, tk.END)

            def handle(self, record):
                """Handle log message record (count errors/warnings)."""
                log.Handler.handle(self, record)
                if record.levelname == 'WARNING':
                    self.__warning_count += 1
                if record.levelname == 'ERROR':
                    self.__error_count += 1

            # message stats, for summary purposes
            __warning_count = 0
            __error_count = 0

            def warnings(self):
                """Return number of accumulated warnings."""
                return self.__warning_count

            def errors(self):
                """Return number of accumulated errors."""
                return self.__error_count

            def reset_counts(self):
                """Reset stats and log output."""
                self.__warning_count = 0
                self.__error_count = 0
                self.text.master.queue(self.text.delete, 1.0, tk.END)

        # disable default logging limits/thresholds
        log.basicConfig(
            level=log.NOTSET,
            streamhandler=log.NullHandler)
        # set up GUI logging
        self.__gui_logger = GUILogHandler(self.log_field)
        self.__gui_logger.setLevel(log.INFO)
        self.__gui_logger.setFormatter(log.Formatter(
            '%(levelname)-8s %(name)-8s %(message)s'))
        # register GUI handler
        log.getLogger().addHandler(self.__gui_logger)
        # remove default (console) handler
        log.getLogger().removeHandler(log.getLogger().handlers[0])

    def __restore_config(self):
        """Read config from JSON file."""
        try:
            if os.path.exists(CONFIG_FILE):
                self.__default_config = json.load(file(CONFIG_FILE))
            else:
                log.getLogger('config').info(
                    'Config does not exist, using defaults')
        except ValueError as ex:
            log.getLogger('config').warning(
                'Could not load complete config from file: %s', ex)
        finally:
            self.__variables['tour_filename'].set(
                self.__default_config['paths']['html'])
            self.__variables['bws_filename'].set(
                self.__default_config['paths']['bws'])
            self.__variables['goniec_host'].set(
                self.__default_config['goniec']['host'])
            self.__variables['goniec_port'].set(
                self.__default_config['goniec']['port'])
            self.__variables['goniec_enabled'].set(
                self.__default_config['goniec']['enabled'])
            self.toggle_goniec()

    def __store_config(self):
        """Write config to JSON file."""
        self.__default_config = {
            'paths': {
                'html': self.__variables['tour_filename'].get(),
                'bws': self.__variables['bws_filename'].get()
            },
            'goniec': {
                'host': self.__variables['goniec_host'].get(),
                'port': self.__variables['goniec_port'].get(),
                'enabled': self.__variables['goniec_enabled'].get()
            }
        }
        json.dump(self.__default_config, file(CONFIG_FILE, 'w'),
                  sort_keys=True, indent=4)


def main():
    """Entry point for application - spawn main window."""
    root = tk.Tk()
    app = BiddingGUI(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
