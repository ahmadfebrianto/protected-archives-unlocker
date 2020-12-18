import subprocess
import os
import sys


def parse_args(args):
    path = ''
    passwords = ''
    if len(args) > 1:
        if len(args) == 2:
            if args[1] == '-h':
                print('\n\t[!] Under construction.\n')
                sys.exit()
            else:
                print('\n\t[!] Invalid option.\n')
                sys.exit()

        path = args[1]
        passwords = args[2]
        return path, passwords
    else:
        print(f'\n\t[!] Run with -h option to view the manual guide.\n')
        sys.exit()


def list_files(path):
    os.chdir(path)
    files = []
    for file in os.listdir():
        if os.path.isfile(file):
            ext = os.path.splitext(file)[1]
            if ext.lower() in ['.zip', '.rar']:
                files.append(file)
    return files


def read_password(password_file):
    output = subprocess.run(
        ['cat', password_file], capture_output=True, text=True)
    if output.returncode != 0:
        print(f'\n\t{output.stderr.strip()}\n')
        sys.exit()
    passwords = output.stdout.split('\n')
    return passwords


def extract_file(file, password):
    output = subprocess.run(
        ['7z', 'x', '-p'+password, file], capture_output=True, text=True)
    return output


def check_and_delete(dir):
    if os.path.exists(dir):
        subprocess.run(
            ['rm', '-rf', dir], capture_output=True, text=True)
    return None


def main():
    args = sys.argv
    path, passwords = parse_args(args)
    passwords = read_password(passwords)

    if os.path.isfile(path):
        current_dir = os.getcwd()
        if os.path.abspath(os.path.join(os.path.abspath(path), os.path.pardir)) == current_dir:
            file = path
        else:
            print()
            dir, file = os.path.split(path)
            os.chdir(dir)
        check_and_delete(os.path.splitext(file)[0])
        for password in passwords:
            output = extract_file(file, password)
            if output.returncode == 0:
                print(f'\n[*] DONE.\n')
                sys.exit()
            else:
                check_and_delete(os.path.splitext(file)[0])

    elif os.path.isdir(path):
        failed = 0
        success = 0
        files = list_files(path)
        spaces = 0
        if files:
            spaces = len(max(files, key=len)) + 22
        print()
        for file in files:
            check_and_delete(os.path.splitext(file)[0])
            print(f'\t[*] Extracting {file}......'.ljust(spaces), end='')
            for password in passwords:
                output = extract_file(file, password)
                if output.returncode == 0:
                    success += 1
                    print(f'DONE')
                    break
                else:
                    check_and_delete(os.path.splitext(file)[0])
                    if password == passwords[-1]:
                        failed += 1
                        print(f'FAILED')
                        print(f'\t{output.returncode}')

        print(f'\n[*] Success = {success}')
        print(f'[!] Failed = {failed}\n')


if __name__ == "__main__":
    main()
