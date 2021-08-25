from logging import getLogger, INFO, StreamHandler, Formatter
from os import walk, path, makedirs, listdir, system, getcwd, remove
from pathlib import PurePath
from shutil import rmtree, make_archive
from sys import version


class Zipper:
    def __init__(self):
        log_format = Formatter(
            fmt="%(asctime)s - [%(levelname)s] - %(name)s - %(funcName)s - Line: %(lineno)d - %(message)s",
            datefmt='%b-%d-%Y %H:%M:%S'
        )
        handler = StreamHandler()
        handler.setFormatter(fmt=log_format)

        self.base_file = PurePath(__file__)
        self.logger = getLogger(self.base_file.stem)
        self.logger.setLevel(level=INFO)
        self.logger.addHandler(hdlr=handler)

        self.zip_dir = 'MakeZip'
        self.archive = 'Archive'

        self.run()

    def prep_indices(self):
        if path.isdir(self.zip_dir):
            self.logger.info(f'Removing {self.zip_dir}')
            rmtree(self.zip_dir)
        makedirs(self.zip_dir)

        zipped = f'{self.archive}.zip'
        if path.isfile(zipped):
            self.logger.info(f'Removing {zipped}')
            remove(zipped)

    def pycache(self):
        if path.isdir('venv'):
            cached = ['venv', self.base_file.parent]
        else:
            cached = [f'..{path.sep}venv', self.base_file.parent]
        for directory in cached:
            for record in walk(directory):
                if record[0].split(path.sep)[-1] == '__pycache__':
                    self.logger.info(f'Removing {record[0]}')
                    rmtree(record[0])

    def copy_app_files(self):
        for record in listdir():
            ignore = record.split(path.sep)[-1]
            if ignore != self.zip_dir and ignore != '.DS_Store' and ignore != PurePath(__file__).name:
                self.logger.info(f'Copying {ignore} to {self.zip_dir}')
                system(f'cp -r {path.abspath(getcwd()) + path.sep + record} {getcwd() + path.sep}{self.zip_dir}')

    def copy_packages(self):
        if path.isdir('venv'):
            packages = f'venv{path.sep}lib{path.sep}python{version[0:3]}{path.sep}site-packages'
        else:
            packages = f'..{path.sep}venv{path.sep}lib{path.sep}python{version[0:3]}{path.sep}site-packages'
        ignore_packages = ['boto3', 'botocore', 's3transfer']  # packages that are not needed for resources within aws
        for record in listdir(packages):
            if not record.endswith('dist-info') and record not in ignore_packages:
                self.logger.info(f'Copying {record} to {self.zip_dir}')
                system(f'cp -r {path.abspath(packages + path.sep + record)} {getcwd() + path.sep}{self.zip_dir}')

    def zipped(self):
        self.logger.info(f'Archiving content in {self.zip_dir}')
        make_archive(self.archive, 'zip', self.zip_dir)
        rmtree(self.zip_dir)

    def run(self):
        self.prep_indices()
        self.pycache()
        self.copy_app_files()
        self.copy_packages()
        self.zipped()


if __name__ == '__main__':
    Zipper()
