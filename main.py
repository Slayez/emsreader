# pip install easyocr
# pip install Pillow

import re
from datetime import datetime, timedelta
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
print("torch.cuda.is_available "+str(torch.cuda.is_available()));
print("---");

# распознавание с помощью easyocr, параметры: отключена детализация вывода,
# включены параграфы и установлена точность текста
def easyocr_recognition_action(path_img, reader):
    im = Image.open(path_img)
    # настройки обрезки скрина для распознания в % от размера экрана
    im_crop = im.crop((im.size[0]*0.16, im.size[1]*0.83, im.size[0]*0.65, im.size[1]));
    # для дебага раскоментить строки ниже
    #im_crop.show();
    #sys.exit();
    return reader.readtext(asarray(im_crop), detail=0, paragraph=True, text_threshold=0.8)

def check_bodycam(path_img, reader):
    im = Image.open(path_img);
    im_crop = im.crop((im.size[0]*0.02, im.size[1]*0.73, im.size[0]*0.159, im.size[1]*0.8));
    #im_crop.show();

    im_crop = im.crop((im.size[0]*0.148, im.size[1]*0.743, im.size[0]*0.15, im.size[1]*0.745));
    pix = im_crop.load();
    print (im_crop.size);  # Get the width and hight of the image for iterating over
    print (pix[0,0]);  # Get the RGBA Value of the a pixel of an imageim_crop.show();
    sys.exit();
    ###
    #bd = reader.readtext(asarray(im_crop), detail=0, paragraph=True, text_threshold=0.8);
    #bd = bd[0];
    #bd = bd[44:len(bd)];
    #bd = bd[0:bd.find(" ")]; 
    #bd = bd.replace(".","");
    #print(float(bd));
    #sys.exit();
    #return float(bd)>0;
    return;


# в 20% случаев не распознаёт дату со скрина, сейчас не используется
def easyocr_recognition_date(path_img, reader):
    im = Image.open(path_img)
    im_crop = im.crop((im.size[0]*0.16, im.size[1]*0.83, im.size[0]*0.25, im.size[1]*0.94));
    #im_crop.show();
    return reader.readtext(asarray(im_crop), detail=0, paragraph=True, text_threshold=0.8)    

def check_dir(path):
    if (os.path.isdir(path)==False):
        os.mkdir(path);

def move_file(destination_file, source_file, file_name):
    check_dir(destination_file[:-len(file_name)]);
    if (True!=os.path.exists(destination_file)):
        shutil.copy2(source_file, destination_file);
        if (delete_new):
            os.remove(source_file);

def build_file_name(dir, destination, file_name, date, old = False):
    d_dir = "";
    # по неделям
    if (date_dir_week):
        d = str(date.date().year)+"-W"+str(date.date().isocalendar()[1]);
        monday = datetime.strptime(d + '-1', "%Y-W%W-%w");
        sunday = monday + timedelta(days=6);       
        d_dir = str(monday.date()) +" - "+ str(sunday.date())+"/";
    # по дням
    if (date_dir):
        d_dir = d_dir+str(date.date())+"/";

    if (old == False):
        check_dir(dir+"После повышения/");
        check_dir(dir+"После повышения/"+d_dir);
        return dir+"После повышения/"+d_dir+destination+file_name;
    else:
        check_dir(dir+"До повышения/");
        check_dir(dir+"До повышения/"+d_dir);
        return dir+"До повышения/"+d_dir+destination+file_name;

def get_night(date : datetime):
    # дневное и ночное время если в вашем отделе иначе поправьте
    night_time = datetime.strptime("22-00-00", '%H-%M-%S').time();
    day_time = datetime.strptime("10-00-00", '%H-%M-%S').time();
    # правка для выходных
    if (date.weekday() >= 5):
        day_time = datetime.strptime("12-00-00", '%H-%M-%S').time();
    time = date.time();
    return (time >= night_time or time <day_time);          

extra_path_tag = " пригород";
extra_night_tag = " ночь";  


class ems_work:

    name :str
    find_tag :str
    folder_name :str

    point :float = 0
    point_extra :float = 0
    point_night :float = 0
    point_extra_night :float = 0
    count :float = 0
    point_count :float = 0

    def __init__(self, name : str, find_tag: str, folder_name: str, point : float, point_extra : float, point_night : float, point_extra_night : float):
        self.name = name;
        self.find_tag = find_tag;
        self.folder_name = folder_name;
        self.point = point;
        self.point_extra = point_extra;
        self.point_night = point_night;
        self.point_extra_night = point_extra_night;
        self.count = 0;
        self.point_count = 0;

    def get_folder_name(self, date : datetime, extra_flag : bool):
        night = get_night(date);
        if ((extra_flag) and (self.point_extra > 0) and (night == False)):            
                return self.folder_name + extra_path_tag;
        if ((extra_flag == False) and (self.point_night > 0) and (night == True)):            
                return self.folder_name + extra_night_tag;      
        if ((extra_flag) and (self.point_extra_night > 0) and (night == True)):            
                return self.folder_name + extra_path_tag + extra_night_tag;
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

# главная директория в которой будет создана сортировка, в ней должна быть папка со скринами
MAIN_DIR = "D:/рп/EMS/";
# папка со скринами
path_img = MAIN_DIR+"NEW/";
ems_works = [];
# название, тэг_для_поиска, название_папки, название_папки_пригород, название_папки_ночь, название_папки_ночь_пригород,    
ems_works.append(ems_work("Таблетки", "вылечил", "Выдача таблеток",
# баллы, баллы_пригород, баллы_ночью, баллы_ночью_пригород   
 1, 0, 0, 0));
# если нет дополнительных баллов писать 0 при этом доп папка не будет создана
ems_works.append(ems_work("Вакцины", "вакцинировал", "Вакцинация", 2, 0, 0, 0));
ems_works.append(ems_work("ПМП", "реанимировал", "ПМП", 3, 0, 4, 0));
ems_works.append(ems_work("Медсправки", "справку", "Медсправки", 4, 0, 0, 0));    
ems_works.append(ems_work("Пожары", "задачу", "Пожар", 4, 5, 5, 6)); 
# тэги для пригорода, будут обновлятся
extra_flags = ['Сэнди', 'Палето', 'Сенора', 'Чилиад', 'Хармони', 'Джошуа'];   
# дата повышения для отбора только действующих баллов
up_date = datetime.strptime("20-05-2024-21-00-00", '%d-%m-%Y-%H-%M-%S');
# разделять по дням
date_dir = False;
# разделять по неделям - для еженедельного отчёта
date_dir_week = False;
# удалять обработанные скрины, после копирования в сортированные папки
delete_new = False;

def main():
    reader = easyocr.Reader(["ru","en"], gpu = True); 

    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path_img) for f in filenames if os.path.splitext(f)[1] in '.png.jpg'];
    i = 0;    

    print("Найдено скринов "+str(len(result)));
    td = datetime.today();
    
    for val in result:
        #bodycam = check_bodycam(val, reader);
        rec = easyocr_recognition_action(val, reader);      
        i = i+1;  
        name = os.path.basename(val);

        # формат времени в вашем скрине сейчас поиск по 2024-05-20-23-36-37
        match_str = re.search(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}', name);
        if (match_str!=None):
            date = datetime.strptime(match_str.group(), '%Y-%m-%d-%H-%M-%S');
        else:
            # формат времени в вашем скрине поиск по 15.05.2024 - 14.09.37
            match_str = re.search(r'\d{2}.\d{2}.\d{4} - \d{2}.\d{2}.\d{2}', name);
            if (match_str!=None):            
                date = datetime.strptime(match_str.group(), '%d.%m.%Y - %H.%M.%S');

        if (match_str==None):
            print(name);
            print("Не содержит читаемой даты в названии! Исправьте формат скрина или формат чтения его даты в коде.");
            sys.exit();      

        flags = 0;
        extra_flag = False;
        time = date.time();

        for line in rec:
            for flag in extra_flags:
                if (line.find(flag)!= -1):
                    extra_flag = True;       

        for line in rec:
            for work in ems_works:
                if (line.find(work.find_tag)!= -1):
                    work.add_work(up_date, date, extra_flag);
                    destination_file = build_file_name(MAIN_DIR, work.get_folder_name(date, extra_flag)+"/", name, date, (date<up_date));
                    flags = flags+1;
        source_file=val; 
        move_file(destination_file, source_file, name);

    print ("Обработано за "+str(datetime.today() - td));    
    print("---"); 
    all = 0;
    for work in ems_works:
        print(work.name+" "+str(work.count)+ " баллов: "+str(work.point_count));
        all = all + work.point_count;
    print("---");    
    print("Всего баллов: "+str(all));
    return;    

if __name__ == "__main__":
    main()
print("---");    