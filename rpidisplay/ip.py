import subprocess


def get_ip():
    return subprocess.run('hostname -I', shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('UTF-8').rstrip()
