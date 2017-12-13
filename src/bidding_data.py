"""
Bidding data for JFR Pary result pages.

Utility to insert HTML tables with bidding data into traveller files generated
by JFR Pary.
"""

import glob
import logging as log
import hashlib
import json
import re
import socket
import sys
from os import mkdir, path, remove, sep

import pypyodbc

from bs4 import BeautifulSoup as bs4

__version__ = '1.2rc1'


def isfile(file_path):
    """Check if a path describes a file.

    Accepts symlinks to files, and does not fail for network drivers.
    """
    return path.exists(file_path) and not path.isdir(file_path)


def hash_file(file_path, block=65536):
    """Return MD5 hash of a specified file."""
    if path.exists(file_path):
        with file(file_path) as file_obj:
            file_hash = hashlib.md5()
            file_buffer = file_obj.read(block)
            while len(file_buffer) > 0:
                file_hash.update(file_buffer)
                file_buffer = file_obj.read(block)
            return file_hash.hexdigest()
    return None


def parse_lineup_data(sitting_data):
    """
    Convert BWS lineup to dictionary structure.

    Structure: {round}.{sector}_{table}.{pair numbers}
    """
    round_lineups = {}
    for sitting in sitting_data:
        log.getLogger('lineup').debug(sitting)
        round_no = sitting[2] if sitting[2] is not None else 0
        table_no = str(sitting[0]) + '_' + str(sitting[1])
        lineup = sorted([sitting[3], sitting[4]])
        if round_no not in round_lineups:
            round_lineups[round_no] = {}
        round_lineups[round_no][table_no] = lineup
        log.getLogger('lineup').debug('round %d, table %s: %s',
                                      round_no, table_no, lineup)
    return round_lineups


def merge_timestamps(date_stamp, time_stamp):
    """
    Merge two timestamps into a single one.

    First timestamp contains date, second - time.
    """
    return ''.join([date_stamp.strftime('%Y%m%d'),
                    time_stamp.replace(year=1900).strftime('%H%M%S')])


def get_board_number(entry):
    """
    Compile board_number from BWS entry.

    Value: {board}_{round}_{sector}_{table}
    """
    return '_'.join([
        str(s) for s in [entry[4], entry[3], entry[1], entry[2]]])


def erase_bid(bidding, bid):
    """Erase bid from bidding."""
    bid_counter = bid[5]
    board_no = get_board_number(bid)
    if bidding[bid_counter]['direction'] == bid[6]:
        bidding.pop(bid_counter, None)
        log.getLogger('bidding').debug(
            'erased bid %d from board %s, ' +
            'round %s, table %s-%s',
            bid_counter, *board_no.split('_'))
    else:
        log.getLogger('bidding').debug(
            'bid does not match, not removing')
    return bidding


def parse_bidding_data(bidding_data, erased_boards=None):
    """
    Convert BWS bidding to dictionary structure.

    Keys: {board}_{round}_{sector}_{table}.{sector}_{table}.{round}
    Values: {bidding}[]
    Applies call erasures and entries result erasures.
    """
    bids = {}
    erased = {}
    if erased_boards is None:
        erased_boards = []
    for entry in erased_boards:
        board_no = get_board_number(entry)
        timestamp = merge_timestamps(entry[13], entry[14])
        if board_no not in erased or erased[board_no] < timestamp:
            erased[board_no] = timestamp
    for bid in bidding_data:
        log.getLogger('bidding').debug(bid)
        round_no = bid[3]
        table_no = str(bid[1]) + '_' + str(bid[2])
        board_no = str(bid[4]) + '_' + str(round_no) + '_' + table_no
        bid_counter = bid[5]
        if (board_no not in erased or
                erased[board_no] < merge_timestamps(bid[8], bid[9])):
            bid_erased = bid[10]
            if board_no not in bids:
                bids[board_no] = {}
            if table_no not in bids[board_no]:
                bids[board_no][table_no] = {}
            if round_no not in bids[board_no][table_no]:
                bids[board_no][table_no][round_no] = {}
            if (bid_erased == 1 and
                    bid_counter in bids[board_no][table_no][round_no]):
                bids[board_no][table_no][round_no] = erase_bid(
                    bids[board_no][table_no][round_no], bid)
                if len(bids[board_no][table_no][round_no]) == 0:
                    bids[board_no][table_no].pop(round_no, None)
                    log.getLogger('bidding').debug(
                        'bidding on board %s, round %s, ' +
                        'table %s-%s empty, removing',
                        *board_no.split('_'))
            else:
                bids[board_no][table_no][round_no][bid_counter] = {
                    'direction': bid[6], 'bid': bid[7]}
                log.getLogger('bidding').debug(
                    'board %s, round %s, table %s-%s, bid %d: %s by %s',
                    *(board_no.split('_') + [bid_counter, bid[7], bid[6]]))
        else:
            log.getLogger('bidding').info(
                'bid from erased board skipped: ' +
                'board %s, round %s, table %s-%s, bid %d: %s by %s',
                *(board_no.split('_') + [bid_counter, bid[7], bid[6]]))
    return bids


def get_dealer(bidding):
    """Return first player to call in a bidding."""
    return bidding[min(bidding.keys())]['direction']


def get_last_bidder(bidding):
    """Return last player to call in a bidding."""
    return bidding[max(bidding.keys())]['direction']


def filter_scripts(header_scripts, name):
    """Return specific scripts from among script tag list."""
    return [script for script in header_scripts
            if script['src'] == name]


class JFRBidding(object):
    """Bidding data converter (from BWS data to JFR HTML pages)."""

    # alignment of the bidding table
    __directions = ['W', 'N', 'E', 'S']

    def __store_file_hash(self, file_path):
        if self.__goniec['host'] is not None:
            self.__goniec['file_hashes'][file_path] = hash_file(file_path)

    def __detect_changed_files(self):
        changed_paths = []
        for file_path, file_hash in self.__goniec['file_hashes'].iteritems():
            if file_hash != hash_file(file_path):
                changed_paths.append(file_path)
            else:
                log.getLogger('hash').debug('file not changed: %s', file_path)
        return changed_paths

    def __format_bidding(self, bidding):
        """Convert bidding data to properly formatted HTML table."""
        log.getLogger('b_format').debug('formatting bidding: %s', bidding)
        bid_match = re.compile(r'(\d)([SHDCN])')
        html_output = bs4('<table>', 'lxml')
        header_row = html_output.new_tag('tr')
        html_output.table.append(header_row)
        for direction in self.__directions:
            header_cell = html_output.new_tag('th')
            header_cell.string = direction
            header_row.append(header_cell)
        for bid_round in bidding:
            bidding_row = html_output.new_tag('tr')
            html_output.table.append(bidding_row)
            for bid in bid_round:
                bid_cell = html_output.new_tag('td')
                call_match = re.match(bid_match, bid)
                if call_match:
                    bid_cell.append(call_match.group(1))
                    bid_icon = html_output.new_tag(
                        'img', src='images/' + call_match.group(2) + '.gif')
                    bid_cell.append(bid_icon)
                else:
                    if bid == 'SkipBid':
                        bid = '( - )'
                    bid_cell.append(bid)
                bidding_row.append(bid_cell)
            log.getLogger('b_format').debug('%5s' * 4, *bid_round)
        return unicode(html_output.table)

    def __get_bidding_file_output_path(self,
                                       board_no,
                                       pair_numbers=None,
                                       position_info=(None, None),
                                       compressed=False):
        """
        Compile file path for bidding data (HTML file with bidding).

        Path format: {prefix}_bidding_{jfr_board_number}_{pair_numbers}.txt
        Compressed path format: {prefix}_bidding_{jfr_board_number}.json
        """
        if compressed:
            return path.join(
                path.dirname(self.__tournament_prefix),
                'bidding-data',
                u'{0}_bidding_{1:03}.json'.format(
                    path.basename(self.__tournament_prefix), board_no))
        else:
            if pair_numbers is None:
                # read numbers from lineup
                (round_no, table_no) = position_info
                pair_numbers = self.__round_lineups[round_no][table_no]
            return u'{0}_bidding_{1:03}_{2}.txt'.format(
                self.__tournament_prefix, board_no,
                '_'.join([str(num) for num in pair_numbers]))

    def __map_board_numbers(self):
        """
        Map BWS board numbers to JFR board numbers.

        Filters boards to these present in both sets of data.
        """
        self.__tournament_files = [
            f for f
            in glob.glob(self.__tournament_prefix + '*.html')
            if re.search(self.__tournament_files_match, f)]
        log.getLogger('b_map').debug('found %d possible board files to map',
                                     len(self.__tournament_files))
        self.__board_number_mapping.clear()
        for round_data in self.__lineup_data:
            log.getLogger('b_map').debug('round data: %s', round_data)
            # 13th column has JFR number for the first board
            if len(round_data) > 12:
                jfr_number = round_data[12]
                round_no = round_data[2]
                sector_no = round_data[0]
                table_no = round_data[1]
                if jfr_number and round_no:
                    # 5th and 6th - actual board number
                    for board_number in range(int(round_data[5]),
                                              int(round_data[6])+1):
                        board_string = '_'.join([
                            str(board_number),
                            str(round_no),
                            str(sector_no),
                            str(table_no)])
                        board_no = jfr_number + board_number - round_data[5]
                        self.__board_number_mapping[
                            board_string
                        ] = board_no
                        log.getLogger('b_map').debug('mapping %s -> %d',
                                                     board_string,
                                                     board_no)
        # only include these board numbers from mapping
        # which actually exist in JFR output
        custom_files = []
        for b_number, jfr_number in self.__board_number_mapping.iteritems():
            board_files = [
                f for f
                in self.__tournament_files
                if f.endswith('{0:03}.html'.format(jfr_number))]
            if len(board_files):
                custom_files = custom_files + board_files
            else:
                self.__board_number_mapping[b_number] = None
                log.getLogger('b_map').debug(
                    'board %s -> %d not in board files, ignoring',
                    b_number, jfr_number)
        self.__tournament_files = list(set(custom_files))

    def __compile_bidding(self, bidding):
        """Compile two-dimensional bidding table from a list of calls."""
        bidding_table = [[], [], [], []]
        # compile bidding player-by-player
        for bid_index in sorted(bidding):
            bid = bidding[bid_index]
            bidding_table[
                self.__directions.index(
                    bid['direction'])
            ].append(bid['bid'])
        return bidding_table

    def __form_bidding(self, bidding_table, dealer, last_bidder):
        """Format bidding table in equally sized, full rows."""
        # fill skipped calls for players before dealer
        # in the first round of bidding
        for pos in range(
                0, self.__directions.index(dealer)):
            bidding_table[pos].insert(0, '')
        # fill skipped calls for players after pass out
        # (so that bidding table is a proper matrix)
        for pos in range(
                self.__directions.index(last_bidder),
                len(self.__directions)):
            bidding_table[pos].append('')
        # transpose the bidding table
        # aligning it row-by-row (bid round-by-round)
        return [list(row) for row in zip(*bidding_table)]

    def __write_bidding_file(self, board_text_path, file_number):
        """Alter traveller file to include links to bidding tables."""
        self.__store_file_hash(board_text_path)
        with file(board_text_path, 'r+') as board_text:
            board_text_content = bs4(
                board_text, 'lxml')
            used_files = []
            for row in board_text_content.select('tr'):
                cells = row.select('td')
                log.getLogger('links').debug(
                    'row: %s',
                    ' '.join([
                        ''.join([
                            cc for cc
                            in c.contents if isinstance(cc, basestring)
                        ]).strip()
                        for c in cells]))
                # traveller table rows for specific score entries
                # should have 11 cells
                if len(cells) == 11:
                    try:
                        pair_numbers = sorted([
                            int(cells[1].contents[0]),
                            int(cells[2].contents[0])])
                        log.getLogger('links').debug(
                            'pairs: %s', pair_numbers)
                    except ValueError:
                        log.getLogger('links').debug(
                            'invalid pair numbers, skipping')
                        continue
                    bidding_link = board_text_content.new_tag(
                        'a', href='#', **{'class': 'biddingLink'})
                    bidding_link.string = ' '
                    bidding_path = self.__get_bidding_file_output_path(
                        int(file_number, 10),
                        pair_numbers=pair_numbers)
                    bidding_link['data-bidding-link'] = '_'.join(
                        [str(pair) for pair in pair_numbers])
                    # only append link if we've got bidding data
                    if isfile(bidding_path):
                        if bidding_path in self.__bidding_files:
                            used_files.append(bidding_path)
                        log.getLogger('links').info(
                            'linking: %s',
                            bidding_link['data-bidding-link'])
                        # fourth cell is the contract
                        for link in cells[3].select('a.biddingLink'):
                            log.getLogger('links').debug(
                                'removing existing link')
                            link.extract()
                        cells[3].append(bidding_link)
                    else:
                        log.getLogger('links').warning(
                            'bidding for file path %s not found',
                            bidding_link['data-bidding-link'])
                else:
                    log.getLogger('links').debug('skipping row')
            board_text.seek(0)
            board_text.write(board_text_content.table.prettify(
                'utf-8', formatter='html'))
            board_text.truncate()
            return used_files

    def __link_compressed_bidding_file(self, traveller_file, bidding_file):
        """Put <link> markup for compressed bidding file in a traveller."""
        if traveller_file in self.__tournament_files:
            with file(traveller_file, 'r+') as traveller_html:
                traveller = bs4(traveller_html, 'lxml')
                for link in traveller.findAll('link', rel='bidding-file'):
                    link.extract()
                bidding_scripts = filter_scripts(
                    traveller.select('head script'), 'javas/bidding.js')
                if len(bidding_scripts) < 0:
                    log.getLogger('compress').warning(
                        'traveller file %s lacks bidding JavaScript, skipping',
                        traveller_file)
                else:
                    bidding_data_tag = traveller.new_tag('link')
                    bidding_data_tag['rel'] = 'bidding-file'
                    bidding_data_tag['src'] = path.relpath(
                        bidding_file, path.dirname(traveller_file)
                    ).replace(sep, '/')
                    bidding_scripts[0].insert_after(bidding_data_tag)
                    traveller_html.seek(0)
                    traveller_html.write(traveller.prettify(
                        'utf-8', formatter='html'))
        else:
            log.getLogger('compress').warning(
                'traveller file %s not registered, skipping', traveller_file)

    # sitting read from BWS
    __round_lineups = {}
    # bidding read from BWS
    __bids = {}

    # full path + JFR prefix
    __tournament_prefix = ''
    # RegEx matching board HTML files
    __tournament_files_match = None
    # matched files, including board number mapping boundaries
    __tournament_files = []

    # BWS number -> JFR number mapping
    __board_number_mapping = {}

    # all generated bidding table files, for cleanup purposes
    __bidding_files = []

    # configuration for Goniec
    __goniec = {'host': None, 'port': None,
                'file_hashes': {}, 'force_resend': False}

    def __init__(self, bws_file, file_prefix,
                 section_number=0, max_round=0):
        """Construct parser object."""
        log.getLogger('init').debug('reading BWS file: %s', bws_file)
        with pypyodbc.win_connect_mdb(bws_file) as connection:
            cursor = connection.cursor()
            if max_round == 0:
                max_round = sys.maxint
            criteria_string = ' WHERE '
            criteria_string += 'Section = %d' % section_number \
                               if section_number > 0 else '1 = 1'
            criteria_string += ' AND Round <= %d' % max_round
            self.__lineup_data = cursor.execute(
                'SELECT * FROM RoundData' + criteria_string
            ).fetchall()
            bid_data = cursor.execute(
                'SELECT * FROM BiddingData' + criteria_string
            ).fetchall()
            erased_boards = cursor.execute(
                'SELECT * FROM ReceivedData ' + criteria_string + ' AND Erased'
            ).fetchall()
        log.getLogger('init').debug('parsing lineup data (%d entries)',
                                    len(self.__lineup_data))
        self.__round_lineups = parse_lineup_data(self.__lineup_data)
        log.getLogger('init').debug('parsing bidding data (%d entries)',
                                    len(bid_data))
        self.__bids = parse_bidding_data(bid_data, erased_boards)
        log.getLogger('init').debug('parsing prefix, filename = %s',
                                    file_prefix)
        self.__tournament_prefix = path.splitext(
            path.realpath(file_prefix))[0]
        log.getLogger('init').debug('prefix = %s', self.__tournament_prefix)
        self.__tournament_files_match = re.compile(
            re.escape(self.__tournament_prefix) + r'([0-9]{3})\.html')
        log.getLogger('init').debug('tournament files pattern: %s',
                                    self.__tournament_files_match.pattern)
        self.__map_board_numbers()

    def setup_goniec(self, goniec_setup=None, goniec_force=False):
        """Configure Goniec for sending files."""
        if goniec_setup is not None:
            setup_parts = goniec_setup.split(':')
            self.__goniec['host'] = setup_parts[0] if len(setup_parts) > 0 \
                else 'localhost'
            self.__goniec['port'] = int(setup_parts[1]) \
                if len(setup_parts) > 1 else 8090
            self.__goniec['force_resend'] = goniec_force

    def write_bidding_tables(self):
        """Iterate over bidding and writes tables to HTML files."""
        self.__bidding_files = []
        for board_no, board_data in self.__bids.items():
            if board_no in self.__board_number_mapping:
                for table_no, table_data in board_data.items():
                    for round_no, round_data in table_data.items():
                        if round_no in self.__round_lineups:
                            if table_no in self.__round_lineups[round_no]:
                                dealer = get_dealer(round_data)
                                log.getLogger('tables').debug(
                                    'board %s: %d bids, dealer %s',
                                    board_no, len(round_data), dealer)
                                last_bidder = get_last_bidder(round_data)
                                bidding_table = self.__compile_bidding(
                                    round_data)
                                bidding_table = self.__form_bidding(
                                    bidding_table, dealer, last_bidder)
                                log.getLogger('tables').debug(
                                    'compiled into %d rounds of bidding',
                                    len(bidding_table))
                                bidding_fpath = \
                                    self.__get_bidding_file_output_path(
                                        self.__board_number_mapping[board_no],
                                        position_info=(round_no, table_no))
                                self.__bidding_files.append(bidding_fpath)
                                self.__store_file_hash(bidding_fpath)
                                with file(bidding_fpath, 'w') as bidding_file:
                                    bidding_file.write(
                                        self.__format_bidding(bidding_table))
                                log.getLogger('tables').info(
                                    'written bidding table to %s',
                                    bidding_fpath)
                            else:
                                log.getLogger('tables').info(
                                    'lineup for table %s, round %s not found',
                                    table_no, round_no)
                        else:
                            log.getLogger('tables').info(
                                'lineup for round %s not found',
                                round_no)
            else:
                log.getLogger('tables').info('mapping for board %s not found',
                                             board_no)
        return self.__bidding_files

    def write_bidding_scripts(self):
        """Alter traveller files to include necessary JavaScript."""
        for tournament_file in self.__tournament_files:
            log.getLogger('scripts').info('writing scripts into: %s',
                                          tournament_file)
            self.__store_file_hash(tournament_file)
            with file(tournament_file, 'r+') as board_html:
                board_content = bs4(board_html, 'lxml', from_encoding='utf-8')
                header_scripts = board_content.select('head script')
                # check for jQuery, append if necessary
                jquery_scripts = filter_scripts(
                    header_scripts, 'javas/jquery.js')
                if not len(jquery_scripts):
                    jquery = board_content.new_tag(
                        'script', src='javas/jquery.js',
                        type='text/javascript')
                    jquery_scripts.append(jquery)
                    board_content.head.append(jquery)
                    log.getLogger('scripts').debug('jQuery not found, adding')
                # check for bidding.js
                bidding_scripts = filter_scripts(
                    header_scripts, 'javas/bidding.js')
                log.getLogger('scripts').debug('found %d bidding.js scripts',
                                               len(bidding_scripts))
                # and make sure bidding.js is appended after jQuery
                for script in bidding_scripts:
                    script.extract()
                bidding_script = board_content.new_tag(
                    'script', src='javas/bidding.js',
                    type='text/javascript')
                jquery_scripts[0].insert_after(bidding_script)
                # check for bidding.css
                bidding_styles = [css for css in
                                  board_content.find_all(
                                      'link',
                                      rel='stylesheet',
                                      href='css/bidding.css')]
                log.getLogger('scripts').debug('found %d bidding.css sheets',
                                               len(bidding_styles))
                # add if none exist
                if len(bidding_styles) == 0:
                    bidding_style = board_content.new_tag(
                        'link', rel='stylesheet',
                        href='css/bidding.css')
                    board_content.head.append(bidding_style)
                board_html.seek(0)
                board_html.write(board_content.prettify(
                    'utf-8', formatter='html'))
                board_html.truncate()
        return self.__tournament_files

    def write_bidding_links(self):
        """
        Iterate over traveller files to include links to bidding tables.

        Cleans up bidding table files, which are not used.
        """
        used_bidding_tables = []
        used_board_files = []
        for tournament_file in self.__tournament_files:
            file_number = re.match(
                self.__tournament_files_match,
                tournament_file).group(1)
            board_text_path = path.splitext(tournament_file)[0] + '.txt'
            if path.exists(board_text_path):
                log.getLogger('links').info(
                    'writing traveller for board %s: %s',
                    file_number, board_text_path)
                used_bidding_tables = self.__write_bidding_file(
                    board_text_path, file_number) + used_bidding_tables
                used_board_files.append(board_text_path)
                log.getLogger('links').info('used board files: %s',
                                            ', '.join(used_bidding_tables))
        for unused_file in [unused for unused
                            in self.__bidding_files
                            if unused not in used_bidding_tables]:
            log.getLogger('links').warning(
                'bidding file %s not used, deleting', unused_file)
            if path.exists(unused_file):
                remove(unused_file)
            else:
                log.getLogger('links').warning(
                    'bidding file %s does not exist', unused_file)
        return used_board_files

    def compress_bidding_files(self):
        """Compile all *.txt for a traveller into a single *.json file."""
        output_directory = path.join(
            path.dirname(self.__tournament_prefix),
            'bidding-data'
        )
        if not path.exists(output_directory):
            try:
                mkdir(output_directory)
            except OSError:
                log.getLogger('compress').error(
                    'unable to create directory for bidding-data: %s',
                    output_directory)
                return []
        compressed_files = []
        for traveller in self.__tournament_files:
            traveller_match = re.match(
                self.__tournament_files_match, traveller)
            if traveller_match:
                board_number = int(traveller_match.group(1), 10)
                compressed_file_path = self.__get_bidding_file_output_path(
                    board_number, compressed=True)
                board_file_prefix = path.basename(
                    compressed_file_path).split('.')[0]
                board_files = [filename for
                               filename in self.__bidding_files
                               if path.exists(filename) and
                               path.basename(filename).startswith(
                                   board_file_prefix)]
                compressed_board = {}
                for board_file in board_files:
                    compressed_board[
                        '_'.join(board_file.split('.')[-2].split('_')[-2:])
                    ] = file(board_file).read()
                json.dump(compressed_board, file(compressed_file_path, 'w'))
                for board_file in board_files:
                    remove(board_file)
                compressed_files.append(compressed_file_path)
                self.__link_compressed_bidding_file(
                    traveller, compressed_file_path)
        return compressed_files

    def send_changed_files(self, files_to_send):
        """Send specified files from working directory via Goniec."""
        if self.__goniec['host'] is not None:
            working_directory = path.dirname(self.__tournament_prefix) \
                                + path.sep
            changed_files = self.__detect_changed_files()
            files_to_send = [file_to_send.replace(working_directory, '', 1)
                             for file_to_send in files_to_send
                             if file_to_send.startswith(working_directory) and
                             path.exists(file_to_send) and
                             (file_to_send in changed_files or
                              self.__goniec['force_resend'])]
            if len(files_to_send) > 0:
                try:
                    goniec_socket = socket.socket()
                    goniec_socket.connect((
                        self.__goniec['host'],
                        self.__goniec['port']))
                    log.getLogger('goniec').info(
                        'connected to Goniec at %s:%d',
                        self.__goniec['host'], self.__goniec['port'])
                    content_lines = [working_directory] + files_to_send + \
                                    ['bye', '']
                    goniec_socket.sendall('\n'.join(
                        [line.encode(sys.getfilesystemencoding())
                         for line in content_lines]))
                    log.getLogger('goniec').info(
                        'working directory is: %s', working_directory)
                    goniec_socket.close()
                    for file_sent in files_to_send:
                        log.getLogger('goniec').info(
                            'sent file to Goniec: %s', file_sent)
                except socket.error as err:
                    log.getLogger('goniec').error(
                        'unable to connect to Goniec: %s', err)
            else:
                log.getLogger('goniec').info('nothing to send')


def main():
    """Program entry point, invoked when __name__ is __main__."""
    import argparse

    argument_parser = argparse.ArgumentParser(
        description='Display bidding data from BWS files on JFR Pary pages')

    def file_path(filepath):
        """Sanitize and validate file paths from input parameters."""
        filepath = unicode(filepath, sys.getfilesystemencoding())
        if isfile(filepath):
            return filepath
        else:
            argument_parser.error('File %s does not exist' % filepath)

    argument_parser.add_argument('-V', '--version', action='version',
                                 version='%(prog)s {version}'.format(
                                     version=__version__))

    argument_parser.add_argument('bws_file', metavar='BWS_FILE',
                                 help='path to BWS file',
                                 type=file_path)
    argument_parser.add_argument('path', metavar='PATH',
                                 help='tournament path (to PREFIX.html)',
                                 type=file_path)

    console_output_args = argument_parser.add_mutually_exclusive_group()
    console_output_args.add_argument('-q', '--quiet', action='store_true',
                                     help='suppress warning on STDERR')
    console_output_args.add_argument('-v', '--verbose', action='store_true',
                                     help='be verbose on STDERR')

    argument_parser.add_argument('-l', '--log-level', metavar='LEVEL',
                                 help='file logging verbosity level',
                                 default='INFO', choices=['DEBUG',
                                                          'INFO',
                                                          'WARNING',
                                                          'ERROR',
                                                          'CRITICAL'])
    argument_parser.add_argument('-f', '--log-file', metavar='LOGFILE',
                                 help='log file path',
                                 default='bidding_data.log')
    argument_parser.add_argument('-s', '--send-files', metavar='GONIEC_HOST',
                                 help='use Goniec to send modified files',
                                 nargs='?',
                                 default=None, const='localhost:8090')
    argument_parser.add_argument('-fs', '--force-resend', action='store_true',
                                 help='force resending all files with Goniec')
    argument_parser.add_argument('-sn', '--section-number', metavar='SECTION',
                                 help='section number to read from',
                                 type=int, nargs='?', default=0)
    argument_parser.add_argument('-mr', '--max-round', metavar='MAX_ROUND',
                                 help='max round number to read from',
                                 type=int, nargs='?', default=sys.maxint)
    arguments = argument_parser.parse_args()

    # primary logging facility - virtual_table.log file
    log.basicConfig(
        level=getattr(log, arguments.log_level),
        format='%(asctime)s %(levelname)-8s %(name)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=arguments.log_file)

    # secondary logging facility - standard error output
    console_log = log.StreamHandler()
    console_log.setLevel(log.INFO if arguments.verbose else (
        log.ERROR if arguments.quiet else log.WARNING))
    console_log.setFormatter(log.Formatter(
        '%(levelname)-8s %(name)-8s: %(message)s'))
    log.getLogger().addHandler(console_log)

    log.info('-------- program started --------')
    log.debug('parsed arguments: %s', arguments)

    try:
        bidding_parser = JFRBidding(
            bws_file=arguments.bws_file,
            file_prefix=arguments.path,
            section_number=arguments.section_number,
            max_round=arguments.max_round
        )
        bidding_parser.setup_goniec(
            goniec_setup=arguments.send_files,
            goniec_force=arguments.force_resend
        )
        bidding_parser.write_bidding_tables()
        all_files = []
        all_files += bidding_parser.write_bidding_scripts()
        all_files += bidding_parser.write_bidding_links()
        all_files += bidding_parser.compress_bidding_files()
        bidding_parser.send_changed_files(all_files)
    except Exception as ex:
        log.getLogger('root').error(ex)
        raise

    log.info('--------- program ended ---------')

if __name__ == '__main__':
    main()
