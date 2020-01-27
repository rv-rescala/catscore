import os
from catscore.lib.time import get_today_date, get_current_time
from catscore.lib.logger import CatsLogging as logging
import pathlib
import shutil

def daily_worker_out(output_folder_path: str, s: str, function_name: str, extension: str, do_zip:bool=True):
    # output init
    function_folder_path = f"{output_folder_path}/{function_name}"
    daily_folder_path = f"{function_folder_path}/{get_today_date()}"
    #zip_daily_folder_path = daily_folder_path + ".zip"
    worker_out_path = daily_folder_path + f"/{function_name}_{get_current_time()}.{extension}"
    logging.info(f"daily_folder_path: {daily_folder_path}")
    logging.info(f"worker_out_path: {worker_out_path}")
    
    # check daily_folder
    daily_folder = pathlib.Path(daily_folder_path)
    if not daily_folder.exists():
        logging.info(f"daily_folder_path: mkdir {daily_folder_path}")
        daily_folder.mkdir(parents=True)
        
    # output str
    with open(worker_out_path, 'w') as f:
        f.write(s)
        
    # zip daily_folder check&create
    if do_zip:
        files = sorted(os.listdir(function_folder_path))
        latest_timestamp = files[-1]
        #zip_files = sorted(filter(lambda f: "zip" in f, os.listdir(function_folder_path)))
        if get_today_date() > latest_timestamp:
            logging.info("daily_worker_out: zipping")
            shutil.make_archive(daily_folder_path, 'zip', root_dir=daily_folder_path)