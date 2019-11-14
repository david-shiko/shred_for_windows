import sys
import os
import argparse
import winreg
import argparse
import tkinter as tk
from tkinter import filedialog

key = winreg.HKEY_CURRENT_USER
subkey = r"Software\Classes\*\shell\shred_for_non_admin\command"

# dialog = {
# 'rus' : {
# 'common' : ['Нажмите "Enter" для подтверждения.\n', 'Что-то пошло не так :(', 'Повторить попытку', ],
# 'help' : ['Change language to English', 'Установить рограмму', 'Удалить программу', 'Уничтожить файлы', 'Помощь']},
# 'eng' : {
# 'short' : ['The program already installed', 'The program successfully removed', 'This file WILL NOT be shreded: ',],
# 'common' : ['Press "Enter" to confirm.\n', 'Something went wrong :(', 'Try again?', 'Choose add files to shred?'],
# 'installing' : ['installing the program ...', 'The program installed correctly!', ],
# 'get_files' : ['Please, choose files to shred: \n', '\nNo any file is selected!', ],
# 'check_files' : ['I am knowing to shred only files. Can not to shred file: '],
# 'confirm_shred' : ['\nTotal files to shred: ', '\nAre you sure you want to shred the file', ],
# 'shredding' : ['\nThe next file was successfully shredded: ', 'This file WAS NOT shredded:', '\nTotal shredded files: ',],
# 'help' : ['Change for language to russian', 'Install program', 'Remove program', 'Shred files', 'Help']}
# }

dialog = {
'rus' : {
'common' : ['Нажмите "Enter" для подтверждения.', 'Что-то пошло не так :(',
'Повторить попытку', ],
'maintree' : iter(['\nВсего файлов для уничтожения:', '\nВы уверены, что\
 хотите безвозвратно уничтожить файл', '\nВсего файлов для уничтожения: ', # backslash to prevent line break
'Следующий файл был успешно уничтожен: ', '\nВсего уничтожено файлов: ',
'\Уничтожить еще файлы? ']),
'info' : ['\nпрограмма уже установлена.\n', 'Устанавливаю программу ...  \n',
'\nПрограмма успешно установленна! \n', '\nПрограмма успешно удалена\n',
'Пожалуйста, выберите файлы для уничтожения \n', ],
'file_warning' : ['\nНет файлов дял уничтожения. Завершаю работу.\n',
'\nЯ умею стирать только файлы. Не могу уничтожить файл: ',
'Этот файл НЕ БУДЕТ уничтожен:', 'Этот файл НЕ БЫЛ уничтожен:'],
'help' : ['Change language to English', 'Установить рограмму',
'Удалить программу', 'Уничтожить файлы', 'Помощь']},
}


dialog = dialog['rus'] # Default


def get_args():

    parser = argparse.ArgumentParser(description =
    'Secure deleting (shred) for windows', epilog = 'Enjoy the program! :)')

    exclude_group_1 = parser.add_mutually_exclusive_group()

    exclude_group_1.add_argument('-if', '--input-file', nargs = '+',
    metavar = 'if', default = argparse.SUPPRESS, help = ( # metavar
    r'''Input file with filenames for shredding. Example: -if C:\Users\
    User\Desktop\files1_to_shred, C:\Users\User\Desktop\files2_to_shred'''))
    exclude_group_1.add_argument('-f','--file', nargs = '+',
    default = argparse.SUPPRESS, help = (r'''Specify file or files to shredding.
    Example: -f file1, file2, C:\Users\User\Desktop\file_N'''))
    exclude_group_1.add_argument('-g', '--gui', action = 'store_true',
    default = argparse.SUPPRESS, help = ('GUI interface to choose files'))

    exclude_group_2 = parser.add_mutually_exclusive_group()
    exclude_group_2.add_argument('-i', '--install', action = 'store_true',
    default = argparse.SUPPRESS, help = '''Install program for using throught
    right-click-menu (will be created a subkey in regedit)''')
    exclude_group_2.add_argument('-r', '--remove', action = 'store_true',
    default = argparse.SUPPRESS, help =
    'Remove program from regedit and right-click-menu.')

    parser.add_argument('-l', '--lang', help = 'Change language to English.',
                        default = argparse.SUPPRESS, choices = ['eng', 'rus'])
    parser.add_argument('-c', '--cycles', type = int, default = 5,
    help = 'count of cycles (overwrites), default = 5. Example: -c 20')
    parser.add_argument('-of', '--output-file', default = argparse.SUPPRESS,
                                    help = 'Save output to specifed file.')
    parser.add_argument('-q', '--quiet', action = 'store_true',
    default = argparse.SUPPRESS, help = 'Quiet mode (no progress_bar).')
    parser.add_argument('-y', '--yes', action = 'store_true',
    default = argparse.SUPPRESS, help = 'Answer "yes" to every question.')
    parser.add_argument('-vh', '--verbose-help', action = 'store_true',
                    default = argparse.SUPPRESS, help = 'Verbose help.')
    parser.add_argument('-v', '--version', action = 'version', help =
                                            'Show version and exit.')
    parser.version = '\nversion: 0.25\n'

    if len(sys.argv) == 1: # If no args
        parser.print_help()
        args, args.file_from_right_click = parser.parse_known_args(input(
                                            '\nType arguments: ').split())
    else:
        args, args.file_from_right_click = parser.parse_known_args()
    return args


def process_flags(args):
    if hasattr(args, 'lang'):
        get_lang(args.lang)
    if hasattr(args, 'verbose_help'):
        print(help) # Help!
    if hasattr(args, 'install'):
        install_program()
    elif hasattr(args, 'remove'):
        remove_program()
    return args


def create_funcs_from_args(args):

    if hasattr(args, 'yes'):
        global input
        input = empty_func
    if hasattr(args, 'output_file'):
        save_output(args)
    if hasattr(args, 'quiet'):
        global progress_bar
        progress_bar = empty_func

    return args


def empty_func(*args):
    return args


def save_output(args):
    global progress_bar
    global print
    progress_bar = empty_func
    original_print = print
    def modified_print(*txt):
        with open(args.output_file, 'a') as f:
            original_print(*txt, file = f)
    print = modified_print


def get_lang(lang = 'eng'):
    global dialog
    if lang == 'eng':
        dialog = dialog['eng']
    elif lang == 'rus':
        dialog = dialog['rus']


def install_program(): # Running always

    '''
    This function running every time and checking if the program added
    to right-ckick-menu. If not, trying to edit the regedit for adding itself
    '''

    path_to_program = sys.argv[0]
    # sys.executable returns str(path to interpreter) like path + 'pythonw.exe',
    # (w in the end - without stdin/ stdout), but needs just 'python.exe'
    path_to_python = ( sys.executable.replace('pythonw.exe', 'python.exe')
                if ('pythonw.exe' in sys.executable) else sys.executable )
    reg_value = '\"{0}\" \"{1}\" \"{2}\"'.format(path_to_python,
                    path_to_program, "%1") # Only double quotes!

    try: # Try to read reg value
        winreg.QueryValue(key, subkey)
        print(dialog['info'][0]) # The program already installed
    except:
        try: # Create reg branch+value to get file path via context menu
            winreg.CreateKey(key, subkey)
            winreg.SetValue(key, subkey, winreg.REG_SZ, reg_value)
            print(dialog['info'][1])
            print(dialog['info'][2])
        except Exception as error:
            print(dialog['common'][1]) # Something went wrong :(
            input(f'Error: {error}')
    sys.exit()


def remove_program():
    try:
        winreg.DeleteKey(key, subkey)
        print(dialog['info'][3])
    except Exception as error:
        print(dialog['common'][1]) # Something went wrong :(
        input(f'Error: {error}')
    sys.exit()


def get_files_from_gui():
    root = tk.Tk() # Legacy
    root.withdraw() # Legacy
    files = filedialog.askopenfilename(initialdir = '~', multiple = True,
    title = dialog['info'][4], parent = root) # Use GUI for choose
    return list(files) # Was tuple


def get_files_from_file(file):
    files = []
    with open(file, r) as file:
        lines = file.readlines()
        for line in lines:
            if os.path.isfile(line.strip()):
                files.append(line.strip())
    return files


def get_files(args):
    if args.file_from_right_click:
        files = args.file_from_right_click
    elif hasattr(args, 'gui'):
        files = get_files_from_gui()
    elif hasattr(args, 'file'):
        files = args.file
    elif hasattr(args, 'input_file'):
        files = get_files_from_file()
    else:
        print(dialog['file_warning'][0])
        sys.exit()
    print(args)
    args.files = files
    return args


def check_files(file_args):

    '''
        This function getting path to files and do next:
        1) Get list files in arg.
        2) Removes spaces from list item.
        3) Checking if list item is file
        4) Del if not file.
        5) Return list files.
    '''

    try:

        for index, file in enumerate(file_args.files[:]):
            file_args.files[index] = file.strip() # To save changes
            if not os.path.isfile(file):
                file_args.files.remove(file)
                if not file: # Printing empty filename will confuse.
                    print(dialog['file_warning'][1] + file)
        return file_args

    except Exception as error:
        input(f"dialog['common'][1] Error: {error}" )
        sys.exit()


def confirm_shred(file_args):

    '''
        This function getting path to files and do next:
        1) Get list files in arg.
        2) Asking for shred confirmation file
        3) If not - go ro next file
        4) If repeating - calling itself (recursion)
    '''

    print(next(dialog['maintree']) + str(len(file_args.files)))
    _ = next(dialog['maintree']) # Save phrase for loop
    for file in file_args.files[:]:
        confirm = input(f'{_} {file} ? {dialog["common"][0]}') # 'Are you sure you want to permanently delete the file? Press "Enter" to confirm'
        if confirm:
            print(dialog['file_warning'][2], file)
            file_args.files.remove(file)

    if not file_args.files:
        print(dialog['file_warning'][0])
        sys.exit()
    else:
        input(next(dialog['maintree']) + str(len(file_args.files)))

    return file_args


def shredding(file_args):

    '''
    This func do next:
    1) Get list of files in arg.
    2) Get size of every files.
    3) Writes 0 instead every symbol throughout file.
    4) Repeat the action by the number of cycles.
    '''

    try:
        _ = next(dialog['maintree']) # Save for loop
        for file in file_args.files:
            print() # linebreak outside of loop
            with open(file, 'r+') as f:
                size = os.path.getsize(file)
                null_str = '0' * size
                for i in range(1, file_args.cycles + 1): # For progress_bar
                    f.write(null_str)
                    f.seek(0)
                    progress_bar(i, file_args.cycles)
            print()
            print(f'\n{_} {file}')
        input(f'{next(dialog["maintree"])} {len(file_args.files)}\n')
    except Exception as error:
        print(dialog['file_warning'][4])
        input(f'{dialog["common"][1]} Error: {error}')
        sys.exit()


def progress_bar(current_cycle, cycles):

    '''
    display progress bar
    '''

    gone = '#' # Create every time, put in global namespace or make closure :)
    left = '-'
    fraction = current_cycle / cycles
    percents = round(fraction * 100)
    end_str = str(percents) + '% done]'
    # Maybe sometimes console consider control characters and flood the output;
    # Terminal width may change during use.
    terminal_width = os.get_terminal_size()[0] -1
    terminal_width -= len('[0%') + len(end_str)
    current_progress = round(fraction * terminal_width)
    print('[0%' + gone * current_progress + (terminal_width -
                current_progress) * left, end = end_str + '\r')

if __name__ == '__main__':
    shredding(confirm_shred(check_files(get_files(create_funcs_from_args(process_flags(get_args()))))))
