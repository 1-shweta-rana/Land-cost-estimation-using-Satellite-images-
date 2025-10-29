from take_ss import sel_setup
import pandas as pd
from take_ss import sel_setup, extract_and_save_with_id
from utils import extract_ids

data = pd.read_csv("./dataset1.csv")
land_ids_list = extract_ids()

if __name__ == "__main__":
    web_Driver = sel_setup()
    try:
        print("\nStarting process..")

        for land_id in land_ids_list:
            extract_and_save_with_id(web_Driver, land_id, data)
    finally:
        if web_Driver:
            web_Driver.quit()
            print("Process is complete or an error occured")