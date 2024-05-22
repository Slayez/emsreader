# pip install easyocr
# pip install Pillow

import re
from datetime import datetime
import os.path
import sys
import time 


import easyocr
from PIL import Image
from numpy import asarray
from glob import glob
import shutil
import torch


print("---");
print("torch.cuda.is_available");
print(torch.cuda.is_available());
print("---");

# распознавание с помощью easyocr, параметры: отключена детализация вывода,
# включены параграфы и установлена точность текста
def easyocr_recognition_action(path_img, reader):
    im = Image.open(path_img)
    im_crop = im.crop((im.size[0]*0.16, im.size[1]*0.83, im.size[0]*0.65, im.size[1]));
    #im_crop.show();
    #sys.exit()
    return reader.readtext(asarray(im_crop), detail=0, paragraph=True, text_threshold=0.8)

def easyocr_recognition_date(path_img, reader):
    im = Image.open(path_img)
    im_crop = im.crop((im.size[0]*0.16, im.size[1]*0.83, im.size[0]*0.30, im.size[1]*0.94));
    #im_crop.show();
    return reader.readtext(asarray(im_crop), detail=0, paragraph=True, text_threshold=0.8)    

def check_dir(path):
    if (os.path.isdir(path)==False):
        os.mkdir(path);

def move_file(destination_file, source_file, file_name):
    check_dir(destination_file[:-len(file_name)]);
    if (True!=os.path.exists(destination_file)):
        shutil.copy2(source_file, destination_file);
        #os.remove(source_file);

def build_file_name(dir, destination, file_name, date, old = False, date_dir = True):
    d_dir = "";
    if (date_dir):
        d_dir = str(date.date())+"/";

    if (old == False):
        check_dir(dir+"После повышения/");
        check_dir(dir+"После повышения/"+d_dir);
        return dir+"После повышения/"+d_dir+destination+file_name;
    else:
        check_dir(dir+"До повышения/");
        check_dir(dir+"До повышения/"+d_dir);
        return dir+"До повышения/"+d_dir+destination+file_name;

def get_night(date : datetime):
    night_time = datetime.strptime("22-00-00", '%H-%M-%S').time();
    day_time = datetime.strptime("10-00-00", '%H-%M-%S').time();
    if (date.weekday() >= 5):
        day_time = datetime.strptime("12-00-00", '%H-%M-%S').time();
    time = date.time();
    return (time >= night_time or time <day_time);          

class ems_work:

    name :str
    find_tag :str
    folder_name :str
    folder_name_extra :str
    folder_name_night :str
    folder_name_extra_night :str
    
    point :float = 0
    point_extra :float = 0
    point_night :float = 0
    point_extra_night :float = 0
    count :float = 0
    point_count :float = 0

    def __init__(self, name : str, find_tag: str, folder_name: str, folder_name_extra: str, folder_name_night: str, folder_name_extra_night: str, point : float, point_extra : float, point_night : float, point_extra_night : float):
        self.name = name;
        self.find_tag = find_tag;
        self.folder_name = folder_name;
        self.folder_name_extra = folder_name_extra;
        self.folder_name_night = folder_name_night;
        self.folder_name_extra_night = folder_name_extra_night;
        self.point = point;
        self.point_extra = point_extra;
        self.point_night = point_night;
        self.point_extra_night = point_extra_night;
        self.count = 0;
        self.point_count = 0;




    def get_folder_name(self, date : datetime, extra_flag : bool):
        night = get_night(date);
        if ((extra_flag) and (self.point_extra > 0) and (night == False)):            
                return self.folder_name_extra;
        if ((extra_flag == False) and (self.point_night > 0) and (night == True)):            
                return self.folder_name_night;         
        if ((extra_flag) and (self.point_extra_night > 0) and (night == True)):            
                return self.folder_name_extra_night;
        return self.folder_name;   


    def add_work(self, up_date : datetime, date : datetime, extra_flag : bool):
        night = get_night(date);   

        self.count = self.count+1;
        
        if (up_date>date):
            return;

        val = self.point;  

        if ((extra_flag) and (self.point_extra > 0) and (night == False)):            
                val = self.point_extra;
        if ((extra_flag == False) and (self.point_night > 0) and (night == True)):            
                val = self.point_night;         
        if ((extra_flag) and (self.point_extra_night > 0) and (night == True)):            
                val = self.point_extra_night;
        self.point_count = self.point_count+val;

def main():

    MAIN_DIR = "D:/рп/EMS/";

    path_img = MAIN_DIR+"NEW/";

    ems_works = [];
    ems_works.append(ems_work("Таблетки", "вылечил", "Выдача таблеток Пиллбокс", "Выдача таблеток Сенди-Шорс и Палето-Бэй", "","", 1, 0, 0, 0));
    ems_works.append(ems_work("Вакцины", "вакцинировал", "Вакцинация Пиллбокс", "Вакцинация Сенди-Шорс и Палето-Бэй", "","", 2, 0, 0, 0));
    ems_works.append(ems_work("ПМП", "реанимировал", "ПМП день", "", "ПМП ночь","", 3, 0, 4, 0));
    ems_works.append(ems_work("Медсправки", "справку", "Медсправки", "", "","", 4, 0, 0, 0));    
    ems_works.append(ems_work("Пожары", "задачу", "Пожар город", "Пожар пригород", "Пожар город ночь","Пожар пригород ночь", 4, 5, 5, 6)); 

    extra_flags = ['Сэнди', 'Палето', 'Сенора', 'Чилиад', 'Хармони', 'Джошуа'];   

    up_date = datetime.strptime("18-05-2024-04-47-00", '%d-%m-%Y-%H-%M-%S');

    date_dir = False;

    reader = easyocr.Reader(["ru","en"], gpu = True); 

    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path_img) for f in filenames if os.path.splitext(f)[1] in '.png.jpg'];
    i = 0;    

    for val in result:  

        rec = easyocr_recognition_action(val, reader);      
        i = i+1;
  
        name = val
        name = name[len(path_img):len(name)];
        match_str = re.search(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}', name);
        date = datetime.strptime(match_str.group(), '%Y-%m-%d-%H-%M-%S');

        flags = 0;
        extra_flag = False;
        time = date.time();
        #if (line.find('Сэнди')!= -1):

        for line in rec:
            for flag in extra_flags:
                if (line.find(flag)!= -1):
                    extra_flag = True;       

        for line in rec:
            for work in ems_works:
                if (line.find(work.find_tag)!= -1):
                    work.add_work(up_date, date, extra_flag);
                    destination_file = build_file_name(MAIN_DIR, work.get_folder_name(date, extra_flag)+"/", name, date, (date<up_date), date_dir);
                    flags = flags+1;
        
        source_file=val;        


        #if (flags>1):
        #    destination_file = build_file_name(MAIN_DIR, "Более 1 типа на скрине/", name, date, (date<up_date), date_dir);
        move_file(destination_file, source_file, name);

    all = 0;
    for work in ems_works:
        print(work.name+" "+str(work.count)+ " баллов: "+str(work.point_count));
        all = all + work.point_count;
    print("---");    
    print ("Всего баллов: "+str(all));
    return;    




if __name__ == "__main__":
    main()
print("---");    