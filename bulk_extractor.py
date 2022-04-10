import subprocess
import os
import sys
import argparse


def list_files(path):
    files = []
    for file in os.listdir(path):
        if os.path.isfile(file):
            ext = os.path.splitext(file)[1]
            if ext.lower() in ['.zip', '.rar']:
                file_path = os.path.join(path, file)
                files.append(file_path)
    return files


def read_password(password_file):
    output = subprocess.run(
        ['cat', password_file], capture_output=True, text=True)
    if output.returncode != 0:
        print(f'\n\t{output.stderr.strip()}\n')
        sys.exit()
    passwords = output.stdout.split('\n')
    return passwords


def extract_file(file, password, destination):
    output = subprocess.run(
        ['7z', 'x', '-p'+password, file, '-o'+destination], capture_output=True, text=True)
    return output


def check_and_delete(dir):
    if os.path.exists(dir):
        subprocess.run(
            ['rm', '-rf', dir], capture_output=True, text=True)
    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract files from a zip or rar archive protected with a password.')

    parser.add_argument(
        '-p', '--password',
        required=True,
        help='Password string or a file containing a list of passwords.')

    parser.add_argument(
        '-f', '--file',
        required=True,
        help='File to extract. It can be a single file or a list of files in a directory.')

    parser.add_argument(
        '-d', '--destination',
        default='.',
        help='Destination to store extracted files.')

    args = parser.parse_args()
    return args


def get_passwords(arg):
    if os.path.isfile(arg):
        passwords = read_password(arg)
    else:
        passwords = arg.password.split(',')
    return passwords


def get_files(arg):
    path = os.path.join(os.getcwd(), arg)
    if os.path.isfile(arg):
        files = [path]
    else:
        files = list_files(path)
    return files


def main():

    args = parse_args()

    passwords = get_passwords(args.password)
    files = get_files(args.file)
    destination = args.destination

    failed = 0
    success = 0
    spaces = 0
    if files:
        spaces = len(max(files, key=len)) + 22
    print()
    for file in files:
        check_and_delete(os.path.join(os.getcwd(), destination))
        print(f'[*] Extracting {file}......'.ljust(spaces), end='')
        for password in passwords:
            output = extract_file(file, password, destination)
            if output.returncode == 0:
                success += 1
                print(f'DONE')
                break
            else:
                check_and_delete(os.path.join(os.getcwd(), destination))
                if password == passwords[-1]:
                    failed += 1
                    print(f'FAILED')
                    print(f'\t{output.returncode}')

    print(f'\n[+] Success = {success}')
    print(f'[!] Failed = {failed}\n')


if __name__ == "__main__":
    main()
