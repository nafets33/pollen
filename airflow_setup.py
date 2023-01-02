

# airflow users create -r Admin -u pollenq -p PollenQueen33! -f stefan -l stapinski -e pollenq.queen@gmail.com
# airflow users create -r Admin -u pollenq -p PollenQueen33! -f stefan -l stapinski -e pollenq.queen@gmail.com
import shutil
import os

## main ##
def copy_to_airflow_dags():

    main_root = os.getcwd()
    db_root = os.path.join(main_root, 'dags')
    dst_path = '/home/stapinski89/airflow/dags'

    for fn in os.listdir(db_root):
        db_file = os.path.join(db_root, fn)
        shutil.copy(db_file, dst_path)


    # if __name__ == '__main__':
copy_to_airflow_dags()





