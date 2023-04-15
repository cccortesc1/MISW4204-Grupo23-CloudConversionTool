from celery import Celery
import shutil, os

celery = Celery('convert', broker='redis://localhost:6379/0')

upload_folder = './upload'
download_folder = './download'

@celery.task
def convert_file(file_path, new_format):
    output_path = os.path.splitext(file_path)[0] + '.' + new_format
    shutil.unpack_archive(file_path, upload_folder)
    shutil.make_archive(output_path, new_format, download_folder)
    return output_path